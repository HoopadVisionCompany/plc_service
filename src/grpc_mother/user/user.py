from . import user_pb2
from . import user_pb2_grpc
import grpc
import os
from dotenv import load_dotenv

load_dotenv()

def get_user(auth_key):
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

    # data_reply = redis_server.hgetall('user_' + auth_key)
    # if data_reply != {}:
    #     print(1)
    #     return data_reply
    with grpc.insecure_channel(f"{os.getenv('GRPC_HOST')}:{os.getenv('GRPC_MOTHER_PORT')}") as channel:
        stub = user_pb2_grpc.UserStub(channel)
        data_request = user_pb2.userRequest(client_key=auth_key)
        data_reply = stub.UserAuth(data_request)
      #   print("((((((((((((((((((((((((")
      #   print("Reply",list(data_reply.permission_list), type(list(data_reply.permission_list)))
        
        data_reply = user_reply_dict(data_reply)
        save_user_in_redis(data_reply=data_reply, auth_key=auth_key)
        return data_reply


def save_user_in_redis(data_reply, auth_key):
    '''
          in this def we check if data reply is not a empty dict
          save data in redis
          condition:
          if  data reply is not empty dict and not equal empty dict then
             mapping data to redis with format hash set
             expire data to redis data with format hash set and set expire time
    '''
   #  if type(data_reply) == dict and data_reply != {}:
      #   redis_server.hset('user_' + auth_key, mapping=data_reply)
      #   redis_server.expire('user_' + auth_key, expire_time)


def user_reply_dict(data_reply):
    '''
       in this def we change format data(get from grpc) to dict
       data_reply:this data come from grpc server(this data is user data)
       user: in this dict we want convertion data and return
       condition:
          if data_reply is exist then:
             complete user data
    '''
    user = {}
    # print(list(data_reply.permission_list))
    if data_reply.user_name:
        user['id'] = data_reply.id
        user['username'] = data_reply.user_name
        user['is_superuser'] = data_reply.is_superuser
        user['is_staff'] = data_reply.is_staff
        user['permission_list'] = list(data_reply.permission_list)
    return user
