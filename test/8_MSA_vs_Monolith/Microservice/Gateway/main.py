# from flask import Flask, request
# import pika
import json
#
#
# class Gateway:
#     def __init__(self):
#         self.AMQP_URL = 'amqp://rabbit_mq?connection_attempts=10&retry_delay=10'
#         self.url_params = pika.URLParameters(self.AMQP_URL)
#         self.connection = pika.BlockingConnection(self.url_params)
#
#
# app = Flask(__name__)
# gateway = Gateway()
# chan = gateway.connection.channel()
# chan.queue_declare(queue='battery')
#
#
# @app.route('/api/batteries', methods=['GET', 'POST'])
# def batteries():
#     if request.method == "POST":
#         data = {
#             'event_type': 'ADD_BATTERY',
#             'capacity': request.json['capacity'],
#             'charge': request.json['charge'],
#             'name': request.json['name']
#         }
#     else:
#         # TODO: Could implement the GET request here.
#         data = {}
#
#     chan.basic_publish(exchange='', routing_key='battery', body=bytes(
#         json.dumps(data), 'utf-8'
#     ))
#     return "OK", 200


from flask import Flask, request, jsonify
import pika

app = Flask(__name__)

# RabbitMQ configuration
RABBITMQ_URL = 'amqp://rabbit_mq?connection_attempts=10&retry_delay=10'
RABBITMQ_QUEUE = 'battery'
# connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
# channel = connection.channel()
# channel.queue_declare(queue=RABBITMQ_QUEUE)


def publish_to_queue(message):
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE)
        channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=message)
        return True
    except Exception as e:
        print(f"Error publishing to RabbitMQ: {e}")
        return False


@app.route('/api/batteries', methods=['POST'])
def publish_battery_message():
    try:
        data = {
            'event_type': 'ADD_BATTERY',
            'capacity': request.json['capacity'],
            'charge': request.json['charge'],
            'name': request.json['name']
        }
        if publish_to_queue(bytes(json.dumps(data), 'utf-8')):
            return jsonify({"status": "Message published to RabbitMQ"}), 200
        else:
            return jsonify({"status": "Failed to publish message to RabbitMQ"}), 500
    except Exception as e:
        return jsonify({"status": f"Error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
