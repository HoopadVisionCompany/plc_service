"""
How to install rabbitmq with docker
latest RabbitMQ 4.0.x

docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  -v rabbitmq_data:/var/lib/rabbitmq \
  rabbitmq:4.0-management

    when the container is running , open a tab on browser go this address : localhost:15672
    login with username:guest , password : guest
    go to Admin tab create a new user with username:admin passwrod :admin
    then click on admin(in the table in the Admin tab) go to set permission
    Virtual Host : /
    Configure regexp: *
    Write regexp: *
    Read regexp: *
    then click on set permission

How to run the python project

    first create a virtual environment and activate it
        virtualenv venv
        source venv/bin/activate
    install pika
        pip install pika
    run the consumer.py
        python comsumer.py

    or
    - python3 consumer.py
    now you can run each of the publishers
        python publisher.py

"""
import pika
import os
import json
import sys
from dotenv import load_dotenv
from typing import Dict, Any

sys.path.insert(1, os.path.abspath(os.path.join(__file__, "../../..")))
from src.database.db import RabbitmqBuilder

load_dotenv()
rmq_instance = RabbitmqBuilder().connect()
channel = rmq_instance.get_channel()
routing_key = os.getenv("RABBITMQ_QUEUE_NAME")


def rabbitmq_publisher(value: Dict[Any, Any]) -> None:
    message_json = json.dumps(value, ensure_ascii=False)
    channel.basic_publish(exchange='', routing_key=routing_key, body=message_json)
    print(f'message sends from publisher face on queue {routing_key}')

#
rabbitmq_publisher({"bye": 20})
# rabbitmq_publisher({"222222": 11111})
# rabbitmq_publisher({"3333333": 11111})
# rabbitmq_publisher({"4444444": 11111})
