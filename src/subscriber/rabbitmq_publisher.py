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
    message_json = json.dumps(value)
    channel.basic_publish(exchange='', routing_key=routing_key, body=message_json)
    print(f'message sends from publisher face on queue {routing_key}')

#
# rabbitmq_publisher({"hello": 11111})
# rabbitmq_publisher({"222222": 11111})
# rabbitmq_publisher({"3333333": 11111})
# rabbitmq_publisher({"4444444": 11111})
