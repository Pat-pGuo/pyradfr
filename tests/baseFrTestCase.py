import unittest


class BaseFrTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_value = None

    def encode_pair(self, value):
        pass

    def decode_pair(self, value):
        pass

    def match(self, value):
        pass
