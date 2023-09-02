"""
A modification of the previous example, where we want to ensure that messages are preserved in the MQ after the consumer
   has been terminated for whatever reason.
"""
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='raw_post', durable=True)

# for i in range(5000):
i = 0
try:
    while 1:
        channel.basic_publish(exchange='',
                              routing_key='raw_post',
                              body=b"hi",
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # make message persistent
                              ))

        print(" [x] Sent 'Hello World!' {}".format(i := i + 1))

except KeyboardInterrupt:
    connection.close()
