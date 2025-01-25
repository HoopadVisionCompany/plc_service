import os
import json
import sys
from typing import List,AnyStr
from dotenv import load_dotenv

sys.path.append("../..")
from src.database.db import RedisDbBuilder
from src.task.service import TaskCollectionCreator
from src.utils.controller_dict_creator import create_controller_event_dict
from src.controller.controller import Controller

task_collection = TaskCollectionCreator().create_collection()
task_collection_cursor = task_collection.task_collection
load_dotenv()

channel_name = os.getenv('REDIS_CHANNEL_NAME')


def message_handler(message:List[AnyStr]):
    print(f"Received message: {message}, type : {type(message)}")
    controller_event_dict = create_controller_event_dict(message[0])
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
            data = json.loads(message['data'])
            message_handler(data)
