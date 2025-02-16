import redis
import os
import json
from dotenv import load_dotenv

load_dotenv()
redis_port = int(os.getenv('REDIS_PORT'))
channel_name = os.getenv('REDIS_CHANNEL_NAME')


def publish(value):
    r = redis.StrictRedis(host='localhost', port=redis_port, db=1)
    if not isinstance(value,str):
        value=json.dumps(value)
    r.publish(channel_name, value)
    print(f"send data {value} to redis")


event_data_publish = {"type": "event", "data": {"task_id": "f4eab1c2-fbd4-49c5-adb1-e4c9182c316d"}}
action_data_publish = {"type": "action",
                       "data": {'type': 'in', 'controller_id': 'cddefdda-7579-43e4-8624-413624589076', 'number': 1,
                                'button_dual_reset': False, 'button_dual_set': True, 'button_single': True,
                                'scenario_id': '449e3873-d4ed-487a-82d5-abc778392d6e',
                                'task_id': 'd7be635c-994f-4db0-89f1-908906b8515a', 'delay': 1,
                                'pin_id': '45cf00c0-b5cf-425a-8805-60e15e9d0807'}
                       }
publish(event_data_publish)
# publish(action_data_publish)
