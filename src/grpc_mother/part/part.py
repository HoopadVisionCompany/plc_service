from . import part_pb2
from . import part_pb2_grpc
import grpc
from src.database.db import RedisDbBuilder
import json
import os
from dotenv import load_dotenv

load_dotenv()
expire_time=int(os.getenv("REDIS_EXPIRE_TIME"))
redis_server=RedisDbBuilder().connect()
def get_parts(auth_key):
    '''
       input value:
          auth_key: this filed is jwt auth key we get from client
             data reply : request data we want recive from  redis
       condition:
          if data reply is not None then
             return query data from redis

       set grpc server ip and port in this stage we use
       stub: set channel to  stub package
       data request : request data we want send to server
       data reply : request data we want recive from  server
       save_parts_in_redis: def we use for save data in redis
    '''
    data_reply = redis_server.get('parts_' + auth_key)
    if data_reply != None:
        return json.loads(data_reply)
    with grpc.insecure_channel(f"{os.getenv('GRPC_HOST')}:{os.getenv('GRPC_MOTHER_PORT')}") as channel:
        stub = part_pb2_grpc.PartStub(channel)
        data_request = part_pb2.partRequest(client_key=auth_key)
        data_reply = stub.List(data_request)
        data_reply = get_parts_to_dict(data_reply)
        save_parts_in_redis(data_reply, auth_key)
        return data_reply


def save_parts_in_redis(data_reply, auth_key):
    '''
       in this def we check if data reply is not a empty dict
       save data in redis
       condition:
          if  data reply is not empty dict and not equal empty dict then
             mapping data(use json.dumps() for convert data to string for saving in redis) to redis with format set
             expire data to redis data with format hash set and set expire time
    '''
    if type(data_reply) == dict and data_reply != {}:
        redis_server.set('parts_' + auth_key, json.dumps(data_reply))
        redis_server.expire('parts_' + auth_key, expire_time)


def get_parts_id(parts):
    '''
       in this def we extract id from parts data (from redis or grpc)
       parts:type of parts is dict
       parts_id: a short for in list of parts and the result is a list of ids
    '''
    if type(parts) == dict:
        parts_id = [parts[str(part)]['id'] for part in range(len(parts))]
        return parts_id
    else:
        return []


def get_parts_to_dict(data_reply):
    '''
       in this def we change format data(get from grpc) to dict
       data_reply:this data come from grpc server(this data is partitions data)
       parts: in this dict we want convertion data and return
    '''
    parts = {}
    for item in range(len(data_reply.results)):
        part = {}
        part['id'] = data_reply.results[item].id
        part['name'] = data_reply.results[item].name
        part['user_id'] = data_reply.results[item].user_id
        parts[str(item)] = part
    return parts


def part_is_exist(auth_key, part_id, version_id, title):
    with grpc.insecure_channel(f"{os.getenv('GRPC_HOST')}:{os.getenv('GRPC_MOTHER_PORT')}") as channel:
        stub = part_pb2_grpc.PartStub(channel)
        data_request = part_pb2.PartExistRequest(client_key=auth_key, id=part_id, version_id=version_id, title=title)
        data_reply = stub.PartExist(data_request)
        return data_reply.is_exist
