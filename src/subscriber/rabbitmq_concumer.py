import pika
import os
from dotenv import load_dotenv
load_dotenv()
import datetime

routing_key = os.getenv("RABBITMQ_QUEUE_NAME")

def on_message3(channel,method,properties,body):
    print(f'message recieved from publisher 3 : {body} at --------{datetime.datetime.now()}')

connection_parameters=pika.ConnectionParameters(host='localhost')
connection=pika.BlockingConnection(connection_parameters)
channel=connection.channel()


channel.queue_declare(routing_key)
channel.basic_consume(queue=routing_key,auto_ack=True,on_message_callback=on_message3)
print("start consuming")
channel.start_consuming()