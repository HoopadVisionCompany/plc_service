import unittest
from src.config import redis_server
from src.config import key_auth
from Grpc.package.package import get_packages, redis_data_str_to_list, save_packages_in_redis
from Grpc.package import package_pb2
from Grpc.package import package_pb2_grpc

import grpc
import os
from dotenv import load_dotenv

load_dotenv()


class TestGetPackagesGrpc(unittest.TestCase):
    '''
        this class test def getpackages data return when key is valid or is notvalid
        dose not difrent beetween data get from grpc and or redis
    '''

    def test_packages_auth_key_valid(self):
        '''
            this def for test field auth_key is valid and check data return len more than zero
        '''
        packages = get_packages(auth_key=key_auth)
        self.assertTrue(len(packages) > 0)

    def test_packages_auth_key_not_valid(self):
        '''
            this def for test field auth_key is not valid and check data return len equal  zero    
        '''
        packages = get_packages(auth_key='key_auth')
        self.assertTrue(len(packages) == 0)


class TestSavePackagesInRedis(unittest.TestCase):
    '''
        this class test def save_packages_in_redis data save when test input value and type of input value
    '''

    def test_save_data_if_type_data_not_list(self):
        '''
            this def for test input data is not dict
            auth_key:authenticate key 
            data_reply:data from grpc
            assert:data save is exist
        '''
        auth_key = '123'
        data_reply = 123
        save_packages_in_redis(auth_key=auth_key, data_reply=data_reply)
        self.assertEqual(redis_server.get('packages_' + str(auth_key)), None)


class Main:
    def get_packages_like_grpc(self):
        '''
            in this def we get package data from server with grpc
        '''
        with grpc.insecure_channel(os.getenv("GRPC_MOTHER_PORT")) as channel:
            stub = package_pb2_grpc.PackageStub(channel)
            data_request = package_pb2.packageRequest(client_key=key_auth)
            data_reply = stub.ListPackage(data_request)
            str_data_reply = ''
            for data_reply_item in data_reply.id:
                str_data_reply += str(data_reply_item) + ','
            return str_data_reply


class TestRedisDataStrToList(unittest.TestCase, Main):
    '''
        this class test def package_reply_dict data return 
    '''

    def test_check_return(self):
        '''
            this def for test len return data more than zero
            package_reply_dict:get data we want check it
            assert:data more than zero
        '''
        packages = redis_data_str_to_list(self.get_packages_like_grpc())
        self.assertTrue(type(packages) == list)
