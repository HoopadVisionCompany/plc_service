import pika
import os
import json
import datetime
from dotenv import load_dotenv

load_dotenv()

import datetime
import json

routing_key = os.getenv("RABBITMQ_QUEUE_NAME")


def on_message3(channel, method, properties, body):
    # print(f'message recieved from publisher 3 : {json.loads(body).encode().decode("unicode_escape")} at --------{datetime.datetime.now()}')
    print(f'message recieved from publisher 3 : {json.loads(body)} at --------{datetime.datetime.now()}')
    channel.basic_ack(delivery_tag=method.delivery_tag)


connection_parameters = pika.ConnectionParameters(host='localhost',
                                                  heartbeat=600,  # Send a heartbeat every 10 minutes
                                                  blocked_connection_timeout=300  # Avoid blocking indefinitely
                                                  )

connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()

channel.queue_declare(routing_key)

channel.basic_consume(queue=routing_key, auto_ack=False, on_message_callback=on_message3)

print("start consuming")
channel.start_consuming()

"""
this file is a python example of how frontend should implement rabbitmq subscriber to get the connection info of 
each controller 

the message we send to frontend contains : 
a dictionary contains : 
{
    'controller_id': mongo _id, 
    'connection': False means it is disconnected and True means it is connected, '
    description':if it is disconnected then shows the reason of 
    disconnection , and if it is connected there is a message indicate that the controller is connected
}
"""
