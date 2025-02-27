import os
import redis
import pika
from dotenv import load_dotenv
from pymongo import MongoClient
from src.utils.patterns.singletons import SingletonMeta, singleton

load_dotenv()


class DbBuilder(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.db_client = None
        self.db = None
        self.connect().create_database()

    def connect(self) -> "DbBuilder":
        uri = os.getenv("MONGODB_URI")
        print("Connecting to MongoDB...")
        self.db_client = MongoClient(uri, maxPoolSize=2, minPoolSize=2)
        return self

    def create_database(self) -> "DbBuilder":
        use_test_db = os.getenv("IS_DB_TEST")
        if use_test_db == "True":
            db_name = os.getenv("TEST_DB_NAME")
        elif use_test_db == "False":
            db_name = os.getenv("DB_NAME")
        if self.db_client is None:
            raise Exception("No DB connection established.")
        print(f"Creating database: {db_name}")
        self.db = self.db_client[db_name]
        return self


@singleton
class RedisDbBuilder:
    def __init__(self) -> None:
        self.redis_port = int(os.getenv('REDIS_PORT'))
        self.redis_host = os.getenv('REDIS_HOST')

    def connect(self):
        self.redis_client = redis.StrictRedis(host=self.redis_host, port=self.redis_port, db=1)
        return self.redis_client


class RabbitmqBuilder(metaclass=SingletonMeta):
    def __init__(self):
        self.rmq_user_name = os.getenv("RABBITMQ_USERNAME")
        self.rmq_password = os.getenv("RABBITMQ_PASSWORD")
        self.rmq_host = os.getenv("RABBITMQ_HOST")
        self.rmq_port = int(os.getenv("RABBITMQ_PORT"))
        self.rmq_queue_name = os.getenv("RABBITMQ_QUEUE_NAME")

        self.connection = None
        self.credentials = None
        self.channel = None

    def connect(self):
        if self.connection is None or self.connection.is_closed:
            self.credentials = pika.PlainCredentials(username=self.rmq_user_name, password=self.rmq_password)
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rmq_host, port=self.rmq_port, credentials=self.credentials, heartbeat=600, blocked_connection_timeout=300))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.rmq_queue_name)
            print(
                f"Connected to RabbitMQ at {self.rmq_host} on port {self.rmq_port} and declared queue '{self.rmq_queue_name}'.")
        return self

    def get_channel(self):
        if not self.channel:
            raise Exception("Not connected to RabbitMQ. Call 'connect()' first.")
        return self.channel

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("Connection closed.")