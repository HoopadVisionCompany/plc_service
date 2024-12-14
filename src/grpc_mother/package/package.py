from . import package_pb2
from . import package_pb2_grpc
import grpc
from src.database.db import RedisDbBuilder
import json
import os
from dotenv import load_dotenv

load_dotenv()
expire_time=int(os.getenv("REDIS_EXPIRE_TIME"))
redis_server=RedisDbBuilder().connect()

def redis_data_str_to_list(data_reply):
    '''
      split data_reply and then convert to list
      type of any item of list must be int
    '''
    data_reply = data_reply.split(',')
    for item in range(len(data_reply)):
        if len(data_reply[item]) > 0:
            data_reply[item] = int(data_reply[item])
        else:
            data_reply.remove(data_reply[item])
    return data_reply


def get_packages(auth_key):
    '''
       input value:
          auth_key: this filed is jwt auth key we get from client
             data reply : request data we want recive from  redis
       condition:
          if data reply is not None then
             return query data from redis(convert to list)

       set grpc server ip and port in this stage we use
       stub: set channel to  stub package
       data request : request data we want send to server
       data reply : request data we want recive from  server
       save_packages_in_redis: def we use for save data in redis
    '''
    data_reply = redis_server.get('packages_' + auth_key)
    if data_reply != None:
        return redis_data_str_to_list(data_reply)
    with grpc.insecure_channel(f"{os.getenv('GRPC_HOST')}:{os.getenv('GRPC_MOTHER_PORT')}") as channel:
        stub = package_pb2_grpc.PackageStub(channel)
        data_request = package_pb2.packageRequest(client_key=auth_key, type_ai='plc')
        data_reply = stub.ListPackage(data_request)
        save_packages_in_redis(data_reply.id, auth_key)
        return data_reply.id


def save_packages_in_redis(data_reply, auth_key):
    '''
       in this def we check if data reply is not a empty list and type data is list
       save data in redis
       condition:
          if  data reply is not empty list and data type  equal list then
            convert data to str for save in redis
            insert data to redis with format set
            expire data to redis data with format hash set and set expire time
    '''
    if data_reply != [] and type(data_reply) == list:
        str_data_reply = ''
        for data_reply_item in data_reply:
            str_data_reply += str(data_reply_item) + ','
        redis_server.set('packages_' + auth_key, str_data_reply)
        redis_server.expire('packages_' + auth_key, expire_time)


def package_is_exist(auth_key, package_id, is_staff, is_superuser):
    with grpc.insecure_channel(f"{os.getenv('GRPC_HOST')}:{os.getenv('GRPC_MOTHER_PORT')}") as channel:
        stub = package_pb2_grpc.PackageStub(channel)
        data_request = package_pb2.PackageExistRequest(client_key=auth_key, id=package_id, is_staff=is_staff,
                                                       is_superuser=is_superuser, type_ai='plc')
        data_reply = stub.ExistPackage(data_request)
        return data_reply.is_exist
