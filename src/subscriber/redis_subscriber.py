import os
import json
import sys
from dotenv import load_dotenv

sys.path.append("../..")
from src.database.db import RedisDbBuilder
from src.task.service import TaskCollectionCreator

task_collection = TaskCollectionCreator().create_collection()
task_collection_cursor = task_collection.task_collection
load_dotenv()

channel_name = os.getenv('REDIS_CHANNEL_NAME')


def message_handler(message):
    print(1)
    print(f"Received message: {message}, type : {type(message)}")
    tasks = list(task_collection_cursor.find({"_id": {"$in": message}}))
    print(tasks)


def subscriber_handler():
    redis_client = RedisDbBuilder().connect()
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel_name)
    print(f"Subscribed to {channel_name}. Waiting for messages...")
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            message_handler(data)
