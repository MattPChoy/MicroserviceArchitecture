import os
import json
import uuid

import pika
import time
import socket
import logging
import threading

import psycopg2


def get_local_ip():
    try:
        # Create a socket to get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))  # Connect to a known external server (e.g., Google's DNS)
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error getting local IP address: {str(e)}")
        return None


class Microservice:
    def __init__(self, amqp_url):
        self.DEFAULT_EXCHANGE = ''

        self.amqp_url = amqp_url
        self.connection = pika.BlockingConnection(
            pika.URLParameters(self.amqp_url)
        )
        self.channel = self.connection.channel()

        self._db = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")
        threading.Thread(target=self.send_heartbeat).start()

        # Tell Disco I'm alive!
        self.write("disco", json.dumps({
            # Retrieve name of class - this gets the implementing class' name
            "service_name": type(self).__name__,
            "timestamp": time.time(),
            "ip": get_local_ip()
        }))

        self.channel.queue_declare(queue='battery-out')
        self.channel.queue_declare(queue='battery-out')

    def send_heartbeat(self):
        self.connection.process_data_events()

    def set_db(self, db):
        self._db = db

    def get_db(self):
        return self._db

    def listen(self, queue_name, callback, durable=True):
        self.channel.queue_declare(queue=queue_name, durable=durable)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback)

    def add_write_queue(self, queue_name):
        self.channel.queue_declare(queue=queue_name, durable=True)

    def write(self, queue_name, message):
        # Queues are singleton so it is fine to re-declare a queue
        try:
            self.add_write_queue(queue_name)
            self.channel.basic_publish(
                exchange=self.DEFAULT_EXCHANGE,
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
        except pika.exceptions.StreamLostError as e:
            self.connection = self.connection = pika.BlockingConnection(
                pika.URLParameters(self.amqp_url)
            )
            self.channel = self.connection.channel()
            self.add_write_queue(queue_name)
            self.channel.basic_publish(
                exchange=self.DEFAULT_EXCHANGE,
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )


class BatteryManagementService(Microservice):
    def __init__(self):
        super().__init__(amqp_url=os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/%2f'))

    def bms_callback(self, channel, method, properties, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)
        _msg = body.decode('utf-8')
        try:
            msg = json.loads(_msg)
        except json.decoder.JSONDecodeError as e:
            logging.warning(f"JSONDecodeError raised {e} {body}")
            return

        cursor = self.get_db().cursor()

        if (req_type := msg.get("type", None)) is not None:
            if req_type == "ADD_BATTERY":
                capacity = str(msg.get("capacity", None))
                charge = str(msg.get("charge", None))
                name = msg.get("name", None)

                if capacity is None or charge is None or name is None:
                    self.logger.warning(
                        f"[AddBattery] One of the required fields is None: ({capacity},{charge},{name})")
                    return

                cursor.execute("INSERT INTO batteries (capacity, charge, name) VALUES (%s,%s,%s) RETURNING id",
                               (capacity, charge, name))
                self.get_db().commit()
                self.logger.info(f"[AddBattery] Adding battery id={cursor.fetchall()[0][0]}")
            elif req_type == "GET_BATTERY":
                if (battery_id := msg.get("battery_id", None)) is None:
                    self.logger.warning(f"[GetBattery] BatteryID provided is None {_msg}")
                    return

                if (dest := msg.get("destination", None)) is None:
                    self.logger.warning(f"[GetBattery] Result destination is None {_msg}")
                    return
                cursor.execute(f"SELECT * FROM batteries WHERE batteries.id={battery_id}")
                res = cursor.fetchall()
                if len(res) > 1:
                    # If there are more than 1 entry with the ID it is an error
                    self.logger.warning(
                        f"[GetBattery] Query to retrieve battery id {battery_id} returned {len(res)} values")
                data = {
                    "success": True,
                    "data": res
                }
                self.write(dest, bytes(str(data), 'utf-8'))
                self.logger.info(f"[GetBattery] Retrieved battery ID {battery_id} data={res}")

    def start(self):
        self.set_db(
            psycopg2.connect(
                database='exampledb',
                user='docker',
                password='docker',
                host='database',
            )
        )

        cursor = self.get_db().cursor()

        cursor.execute('CREATE TABLE IF NOT EXISTS "public".BATTERIES ( \
                        "id" SERIAL PRIMARY KEY, \
                        "capacity" integer NOT NULL, \
                        "charge" integer NOT NULL, \
                        "name" text NOT NULL \
                    ) \
                ')

        # Read from inputs
        self.listen("battery-management-service", self.bms_callback)
        self.channel.start_consuming()


def handle_gateway_requests():
    print("Starting listener thread")

    def callback(_channel, method, properties, body):
        _channel.basic_ack(delivery_tag=method.delivery_tag)
        _msg = body.decode('utf-8')

        try:
            msg = json.loads(_msg)
        except json.decoder.JSONDecodeError as e:
            logging.warning(f"JSONDecodeError raised {e} {body}")
            return

        logging.info(f"Retrieved message from battery-in queue {_msg}")

        if (req_type := msg.get("type", None)) is None:
            logging.warning(f"Request type is None {_msg}")
            return
        elif req_type == "GET_BATTERY":
            cursor = srv.get_db().cursor()
            cursor.execute('SELECT * FROM "public".BATTERIES WHERE "id"=%s', (msg["battery_id"],))
            data = cursor.fetchall()

            correlation_id = msg.get("correlation_id", None)
            if correlation_id is None:
                correlation_id = uuid.uuid4()
                logging.error("Correlation ID has not been generate yet.")

            response_body = {
                "correlation_id": correlation_id,
            }
            if len(data) > 1:
                logging.warning(f"Query to retrieve battery id {msg['battery_id']} returned {len(data)} values")
                response_body["success"] = False
                response_body["err_code"] = 500
                response_body["description"] = "Multiple entries found for the same ID"
            else:
                response_body["data"] = data
                response_body["success"] = True

            channel.basic_publish(
                exchange='',
                routing_key='battery-out',
                body=json.dumps(response_body).encode('utf-8')
            )

        elif req_type == "ADD_BATTERY":
            cursor = srv.get_db().cursor()

            cursor.execute("INSERT INTO batteries (capacity, charge, name) VALUES (%s,%s,%s) RETURNING id",
                           (msg["capacity"], msg["charge"], msg["name"]))
            srv.get_db().commit()

            reply_body = json.dumps({
                "correlation_id": msg["correlation_id"],
                # Determine if we can try-catch the insertion to not tear down the microservice if a SQL error
                # occurs.
                "success": True,
                "battery_id": cursor.fetchall()[0][0]
            }).encode('utf-8')

            channel.basic_publish(
                exchange='',
                routing_key='battery-out',
                body=reply_body
            )

    AMQP_URL = os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/%2f')
    connection = pika.BlockingConnection(
        pika.URLParameters(AMQP_URL)
    )
    channel = connection.channel()
    channel.basic_consume(queue='battery-in', on_message_callback=callback)
    channel.start_consuming()


if __name__ == "__main__":
    srv = BatteryManagementService()
    srv.channel.queue_declare(queue="battery-in")
    srv.channel.queue_declare(queue="battery-out")

    threading.Thread(target=handle_gateway_requests).start()

    srv.start()
