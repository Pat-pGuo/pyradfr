import unittest
import os
from tests.frparser.frtestparser import ParseError, FrTestCaseParser
import configparser

config_file = './frparser/testconfig.ini'
config = configparser.ConfigParser()
config.read(config_file)


class FrTestCaseRetriever:
    def __init__(self, encode_func, decode_func, match_func, prev_result_func):
        self.parser = FrTestCaseParser()

        self.encode_func = encode_func
        self.decode_func = decode_func
        self.match = match_func

        self.prev_result_func = prev_result_func

    def parse_file(self, file):
        file_test_cases = []

        with open(file, 'r') as file_open:
            for line_num, line_content in enumerate(file_open):
                try:
                    file_test_cases.append(self.parse_line(line_content))
                except ParseError as e:
                    print(f'Encountered Parse Error in file {file} on line'
                          f' {line_num + 1}. Error: {e}')

        return file_test_cases

    def parse_line(self, line_content):
        test_case_funcs = {
            'encode_pair': self.encode_func,
            'decode_pair': self.decode_func,
            'match': self.match
        }

        test_case = self.parser.start(line_content, self.prev_result_func)
        if test_case:
            cmd, data = test_case['testcase']
            return test_case_funcs[cmd](data)


class TestFrTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tc_retriever = FrTestCaseRetriever(
            cls.run_encode_pair, cls.run_decode_pair, cls.run_match,
            cls.get_prev_result
        )
        cls.previous_result = None

        cls.test_cases = []
        for root, dirs, files in os.walk(config['FRTESTCASES']['testFileDir']):
            for file in files:
                cls.test_cases.append(
                    cls.tc_retriever.parse_file(os.path.join(root, file))
                )

    def get_prev_result(self):
        return self.previous_result

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def run_encode_pair(self, data):
        pass

    def run_decode_pair(self, data):
        pass

    def run_match(self, data):
        self.assertEqual(data, self.previous_result)

    def test_all_fr_test_cases(self):
        pass
