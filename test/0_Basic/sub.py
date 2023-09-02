# example_consumer.py
import pika, os, time

def pdf_process_function(msg):
  print(msg)
  return

# Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
url = 'amqp://guest:guest@localhost:5672/%2f'

params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel() # start a channel
channel.queue_declare(queue='pdfprocess') # Declare a queue

# create a function which is called on incoming messages
def callback(ch, method, properties, body):
  pdf_process_function(body)

# set up subscription on the queue
channel.basic_consume('pdfprocess',
  callback,
  auto_ack=True)

# start consuming (blocks)
channel.start_consuming()
connection.close()
