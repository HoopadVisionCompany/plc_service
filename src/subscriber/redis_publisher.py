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


event_data_publish_alarm = {"type": "event", "data": {"task_id": "f4eab1c2-fbd4-49c5-adb1-e4c9182c316d"}}
event_data_publish_gate = {"type": "event", "data": {"task_id": "f4eab1c2-fbd4-49c5-adb1-e4c9182c316g"}}

action_data_publish_on = {"type": "action",
                       "data": {'type': 'in',
                                'controller_id': '5d86a0b8-d789-4637-9c61-86617afe6808',
                                'number': 0,
                                'button_dual_reset': None, 
                                'button_dual_set': None, 
                                'button_single': True,
                                'scenario_id': '5606fb01-fb9f-4dac-9d42-25ed9609666e',
                                'task_id': 'f4eab1c2-fbd4-49c5-adb1-e4c9182c316e', 
                                'delay': 1,
                                'timer': 2001,
                                'pin_id': '5e572805-a061-4ac9-8e32-2d6f43bcac8c'}
                       }

action_data_publish_off = {"type": "action",
                       "data": {'type': 'in',
                                'controller_id': '5d86a0b8-d789-4637-9c61-86617afe6808',
                                'number': 0,
                                'button_dual_reset': None, 
                                'button_dual_set': None, 
                                'button_single': False,
                                'scenario_id': '5606fb01-fb9f-4dac-9d42-25ed9609666x',
                                'task_id': 'f4eab1c2-fbd4-49c5-adb1-e4c9182c316x', 
                                'delay': 1,
                                'timer': 2001,
                                'pin_id': '5e572805-a061-4ac9-8e32-2d6f43bcac8c'}
                       }
publish(event_data_publish_alarm)
publish(event_data_publish_gate)

publish(action_data_publish_on)
import time
time.sleep(5)
publish(action_data_publish_off)
