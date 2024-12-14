import unittest
from src.config import redis_server
from src.config import key_auth
from Grpc.user.user import get_user, user_reply_dict, save_user_in_redis
from Grpc.user import user_pb2
from Grpc.user import user_pb2_grpc

import grpc
import os
from dotenv import load_dotenv

load_dotenv()

class TestGetUserGrpc(unittest.TestCase):
    '''
        this class test def getuser data return when key is valid or is not valid
        dose not difrent beetween data get from grpc and or redis
    '''

    def test_user_auth_key_valid(self):
        '''
            this def for test field auth_key is valid and check data return len more than zero
        '''
        user = get_user(auth_key=key_auth)

        self.assertTrue(len(user) > 0)

    def test_parts_auth_key_not_valid(self):
        '''
            this def for test field auth_key is not valid and check data return len equal  zero    
        '''
        user = get_user(auth_key='key_auth')
        self.assertTrue(len(user) == 0)


class TestSaveUserInRedis(unittest.TestCase):
    '''
        this class test def save_user_in_redis data save when test input value and type of input value
    '''

    def test_save_data_if_type_data_not_dict(self):
        '''
            this def for test input data is not dict
            auth_key:authenticate key 
            data_reply:data from grpc
            assert:data save is exist
        '''
        auth_key = '123'
        data_reply = '123'
        save_user_in_redis(auth_key=auth_key, data_reply=data_reply)
        self.assertEqual(redis_server.hgetall('user_' + str(auth_key)), {})

    def test_save_data_if_type_data_empty_dict(self):
        '''
            this def for test input data is empty dict
            auth_key:authenticate key 
            data_reply:data from grpc
            assert:data save is exist
        '''
        auth_key = '123'
        data_reply = {}
        save_user_in_redis(auth_key=auth_key, data_reply=data_reply)
        self.assertEqual(redis_server.hgetall('user_' + str(auth_key)), {})


class Main:
    '''
        in this class we get data from grpc for testing in other classes
    '''

    def get_user_like_grpc(self):
        '''
            in this def we get package data from server with grpc
        '''
        with grpc.insecure_channel(os.getenv("GRPC_MOTHER_PORT")) as channel:
            stub = user_pb2_grpc.UserStub(channel)
            data_request = user_pb2.userRequest(client_key=key_auth)
            data_reply = stub.UserAuth(data_request)
            return data_reply


class TestGetUserToDict(unittest.TestCase, Main):
    '''
        this class test def package_reply_dict data return 
    '''

    def test_check_return(self):
        '''
            this def for test len return data more than zero
            package_reply_dict:get data we want check it
            assert:data more than zero
        '''
        user = user_reply_dict(self.get_user_like_grpc())
        print(user)
        self.assertTrue(len(user) > 0)
