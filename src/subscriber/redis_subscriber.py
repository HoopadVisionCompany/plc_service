import os
import json
import sys
from typing import List, AnyStr
from dotenv import load_dotenv

sys.path.append("../..")
from src.database.db import RedisDbBuilder
from src.task.service import TaskCollectionCreator
from src.utils.controller_dict_creator import create_controller_event_dict, convert_action_to_event_dict
from src.controller.controller import Controller

task_collection = TaskCollectionCreator().create_collection()
task_collection_cursor = task_collection.task_collection
load_dotenv()

channel_name = os.getenv('REDIS_CHANNEL_NAME')


def message_handler(message: List[AnyStr]):
    message = json.loads(message)
    print(f"Received message: {message}, type : {type(message)}")
    if message["type"] == "action":
        print(f"Received action: {message}")
        controller_event_dict = convert_action_to_event_dict(message["data"])
    elif message["type"] == "event":
        print(f"Received event: {message}")
        controller_event_dict = create_controller_event_dict(message["data"]["task_id"])
    else:
        raise Exception("Invalid message type")

    print(controller_event_dict)
    controller = Controller({})
    print(controller)
    controller.controller_action(controller_event_dict)
    # tasks = list(task_collection_cursor.find({"_id": {"$in": message}}))
    # print(tasks)


def subscriber_handler():
    print(11)
    redis_client = RedisDbBuilder().connect()
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel_name)
    print(f"Subscribed to {channel_name}. Waiting for messages...")
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = message['data'].decode('utf-8')
            message_handler(data)
