import sys
import unittest

sys.path.append("..")
from src.utils.exceptions.custom_exceptions import CustomException404


class TestCustomException(unittest.TestCase):
    def test_custom_exception_message(self):
        message = "Resource not found"

        with self.assertRaises(CustomException404) as context:
            raise CustomException404(message)

        self.assertEqual(str(context.exception), message)
