import os
import pika
import json
import sqlite3
import psycopg2


class Microservice:
    def __init__(self, AMQP_URL=None):
        self.AMQP_URL = os.environ.get("AMQP_URL", "amqp://guest:guest@localhost/%2f") if AMQP_URL is None else AMQP_URL
        self.url_params = pika.URLParameters(self.AMQP_URL)
        self.connection = pika.BlockingConnection(self.url_params)
        self.db = sqlite3.connect("./database.db", check_same_thread=False)
        self.read_queues = {}
        self.write_queues = {}

    def register_receive_message(self, queue_name, callback, durable=True):
        if queue_name not in self.read_queues:
            ch = self.connection.channel()
            self.read_queues[queue_name] = ch
            ch.queue_declare(queue=queue_name, durable=durable)
            ch.basic_qos(prefetch_count=1)
        else:
            ch = self.read_queues[queue_name]
        ch.basic_consume(queue=queue_name, on_message_callback=callback)

    def run(self):
        conn = psycopg2.connect(
            database='exampledb',
            user='docker',
            password='docker',
            host='database'
        )

        # Open cursor to perform operations on db
        cursor = conn.cursor()

        def handle_bms_input(ch, method, properties, body):
            in_json = json.loads(body.decode('utf-8'))
            print(in_json)

            cursor.execute('CREATE TABLE IF NOT EXISTS "public".BATTERIES ( \
                    "id" SERIAL PRIMARY KEY, \
                    "capacity" integer NOT NULL, \
                    "charge" integer NOT NULL, \
                    "name" text NOT NULL \
                ) \
            ')

            if in_json["event_type"] == "ADD_BATTERY":
                cursor.execute("INSERT INTO batteries (capacity, charge, name) VALUES (%s,%s,%s)",
                               (str(in_json["capacity"]), str(in_json["charge"]), in_json["name"]))
                conn.commit()
            if in_json["event_type"] == "DUMP":
                cursor.execute("SELECT * FROM batteries")
                print(
                    cursor.fetchall()
                )
                conn.commit()
            if in_json["event_type"] == "CLOSE":
                cursor.close()
                conn.commit()
                conn.close()
                ch.basic_ack(delivery_tag=method.delivery_tag)
                exit(0)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.register_receive_message("battery-management-service", handle_bms_input)

        try:
            for queue_name in self.read_queues:
                self.read_queues[queue_name].start_consuming()
        except KeyboardInterrupt:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    mi = Microservice()
    mi.run()
