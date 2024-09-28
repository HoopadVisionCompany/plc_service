import os
from dotenv import load_dotenv
from pymongo import MongoClient
from src.utils.patterns.singletons import SingletonMeta

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
        use_test_db=os.getenv("USE_TEST_DB")
        if use_test_db:
            db_name = os.getenv("TEST_DB_NAME")
        else:
            db_name = os.getenv("DB_NAME")
        if self.db_client is None:
            raise Exception("No DB connection established.")
        print(f"Creating database: {db_name}")
        self.db = self.db_client[db_name]
        return self
