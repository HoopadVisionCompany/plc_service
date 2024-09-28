import unittest
import sys

sys.path.append('..')
from src.database.db import DbBuilder


class DbTest(unittest.TestCase):
    def testdb_connection(self):
        db = DbBuilder()
        server_info = db.db_client.server_info()
        self.assertIsNotNone(server_info)
        self.assertIn("version", server_info)
