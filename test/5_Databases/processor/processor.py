import os
import pika
import json
import sqlite3

class Microservice():
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
        ch.basic_consume(queue=queue_name, on_message_callback=callback)
    def run(self):
        def handle_bms_input(ch, method, properties, body):
            in_json = json.loads(body.decode('utf-8'))
            print(in_json)
            if in_json["event_type"] == "ADD_BATTERY":
            	query=f"""INSERT INTO batteries VALUES({in_json['battery_id']}, {in_json['capacity']},
                         {in_json['owner_id']}, {in_json['name']}"""
                print(f"Query={query}")
                self.db.execute()
                cursor.commit()



        self.register_receive_message("battery-management-service", handle_bms_input)
        
        for queue_name in self.read_queues:
            self.read_queues[queue_name].start_consuming()

if __name__ == "__main__":
    mi = Microservice()
    mi.run()
