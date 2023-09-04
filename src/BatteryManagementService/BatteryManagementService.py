import json
import logging
import os
import pika
import psycopg2


class Microservice:
    def __init__(self, amqp_url):
        self.DEFAULT_EXCHANGE = ''

        self.amqp_url = amqp_url
        self.connection = pika.BlockingConnection(
            pika.URLParameters(self.amqp_url)
        )
        self.channel = self.connection.channel()

        self._db = None
        self._read_queues = {}
        self._write_queues = {}
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")

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
            logging.warning(f"JSONDecodeError raised {e}")
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


if __name__ == "__main__":
    srv = BatteryManagementService()
    srv.start()
