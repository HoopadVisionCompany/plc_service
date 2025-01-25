import redis
import os
from dotenv import load_dotenv

load_dotenv()
redis_port = int(os.getenv('REDIS_PORT'))
channel_name = os.getenv('REDIS_CHANNEL_NAME')


def publish(value):
    r = redis.StrictRedis(host='localhost', port=redis_port, db=1)
    r.publish(channel_name, value)
    print(f"send data {value} to redis")


publish("d7be635c-994f-4db0-89f1-908906b8515a")