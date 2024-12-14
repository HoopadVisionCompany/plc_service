from . import user_pb2
from . import user_pb2_grpc
import json
import grpc
from src.config import redis_server, expire_time
import os
from dotenv import load_dotenv

load_dotenv()

def get_user_list(version_id, auth_key):
    '''
       input value:
          auth_key: this filed is jwt auth key we get from client
       data reply : request data we want recive from  redis
       condition:
          if len data reply less than zero then
             return query data from redis
       set grpc server ip and port in this stage we use
       stub: set channel to  stub package
       data request : request data we want send to server
       data reply : request data we want recive from  server
       save_user_in_redis:save data in redis

    '''
    data_reply = redis_server.hgetall('user_' + auth_key + str(version_id))
    if data_reply != None:
        return json.loads(data_reply)
    with grpc.insecure_channel(os.getenv("GRPC_MOTHER_PORT")) as channel:
        stub = user_pb2_grpc.UserStub(channel)
        data_request = user_pb2.usersRequest(version_id=version_id)
        data_reply = stub.UserList(data_request)
        data_reply = users_reply_dict(data_reply)
        save_users_in_redis(data_reply=data_reply, auth_key=auth_key, version_id=version_id)
        return data_reply


def save_users_in_redis(data_reply, auth_key, version_id):
    '''
          in this def we check if data reply is not a empty dict
          save data in redis
          condition:
          if  data reply is not empty dict and not equal empty dict then
             mapping data to redis with format hash set
             expire data to redis data with format hash set and set expire time
    '''
    if type(data_reply) == dict and data_reply != {}:
        redis_server.set('user_' + auth_key + str(version_id), json.dumps(data_reply))
        redis_server.expire('user_' + auth_key + str(version_id), expire_time)


def users_reply_dict(data_reply):
    '''
       in this def we change format data(get from grpc) to dict
       data_reply:this data come from grpc server(this data is user data)
       user: in this dict we want convertion data and return
       condition:
          if data_reply is exist then:
             complete user data
    '''
    users = {}
    for item in range(len(data_reply.results)):
        user = {}
        user['id'] = data_reply.results[item].id
        user['username'] = data_reply.results[item].user_name
        user['version_id'] = data_reply.results[item].version_id
        users[str(item)] = user
    return users
