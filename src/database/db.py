import os
import redis
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
