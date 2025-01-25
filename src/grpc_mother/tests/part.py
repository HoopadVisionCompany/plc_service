import unittest
from src.config import redis_server
from src.config import key_auth
from Grpc.part.part import get_parts, get_parts_id, get_parts_to_dict, save_parts_in_redis
from Grpc.part import part_pb2
from Grpc.part import part_pb2_grpc

import grpc
import os
from dotenv import load_dotenv

load_dotenv()

class TestGetPartsGrpc(unittest.TestCase):
    '''
        this class test def getparts data return when key is valid or is notvalid
        dose not difrent beetween data get from grpc and or redis
    '''

    def test_parts_auth_key_valid(self):
        '''
            this def for test field auth_key is valid and check data return len more than zero
        '''
        parts = get_parts(auth_key=key_auth)
        self.assertTrue(len(parts) > 0)

    def test_parts_auth_key_not_valid(self):
        '''
            this def for test field auth_key is not valid and check data return len equal  zero    
        '''
        parts = get_parts(auth_key='key_auth')
        self.assertTrue(len(parts) == 0)


class TestSavePartsInRedis(unittest.TestCase):
    '''
        this class test def save_parts_in_redis data save when test input value and type of input value
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
        save_parts_in_redis(auth_key=auth_key, data_reply=data_reply)
        self.assertEqual(redis_server.get('parts_' + str(auth_key)), None)

    def test_save_data_if_type_data_empty_dict(self):
        '''
            this def for test input data is empty dict
            auth_key:authenticate key 
            data_reply:data from grpc
            assert:data save is exist
        '''
        auth_key = '123'
        data_reply = {}
        save_parts_in_redis(auth_key=auth_key, data_reply=data_reply)
        self.assertEqual(redis_server.get('parts_' + str(auth_key)), None)


class Main:
    '''
        in this class we get data from grpc or redis  for testing in other classes
    '''

    def get_parts(self):
        '''
            in this def we get package data test like data redis
        '''
        parts = {'0': {'id': 1, 'name': '12345', 'user_id': 2, 'version_id': 0, 'type_id': 0},
                 '1': {'id': 2, 'name': '1234', 'user_id': 2, 'version_id': 0, 'type_id': 0}}
        return parts

    def get_parts_like_grpc(self):
        '''
            in this def we get package data from server with grpc
        '''
        with grpc.insecure_channel(os.getenv("GRPC_MOTHER_PORT")) as channel:
            stub = part_pb2_grpc.PartStub(channel)
            data_request = part_pb2.partRequest(client_key=key_auth)
            data_reply = stub.List(data_request)
            return data_reply


class TestGetPartsId(unittest.TestCase, Main):
    '''
        this class test def getparts_id data return 
    '''

    def test_parts_id_type_not_dict(self):
        '''
            in this def check data return from  get_parts_id is empty dict or not 
        '''
        parts_id = get_parts_id('kalim')
        self.assertEqual(parts_id, [])

    def test_check_return(self):
        '''
            in this def check data return from  get_parts_id is  dict eqaul [1,2] 
        '''
        parts_id = get_parts_id(self.get_parts())
        self.assertEqual(parts_id, [1, 2])


class TestGetPartsToDict(unittest.TestCase, Main):
    '''
        this class test def package_reply_dict data return 
    '''

    def test_check_return(self):
        '''
            this def for test len return data more than zero
            package_reply_dict:get data we want check it
            assert:data more than zero
        '''
        parts = get_parts_to_dict(self.get_parts_like_grpc())
        print(parts)
        self.assertTrue(len(parts) > 0)
