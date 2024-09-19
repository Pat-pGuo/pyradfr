import unittest
import os
from tests.frparser.frtestparser import ParseError, TestCaseParser

test_case_file_dir = ''

class ContextManager:
    def __init__(self):
        self.parser = TestCaseParser()
        self.previous_result = None

    def reset_previous_result(self):
        self.previous_result = None

    def get_previous_result(self):
        pass

    def parse_file(self, file):
        with open(file, 'r') as file_open:
            for line_num, line_content in enumerate(file_open):
                try:
                    self.parse_line(line_content)
                except ParseError as e:
                    print(f'Encountered Parse Error in file {file} on line'
                          f' {line_num + 1}. Error: {e}')

    def parse_line(self, line_content):
        test_case = self.parser.start(line_content, self.get_previous_result)
        if test_case:
            cmd, data = test_case['testcase']
            match cmd:
                case 'encode-pair':
                    self.test_encode_pair(data)
                case 'decode-pair':
                    self.test_decode_pair(data)
                case 'match':
                    self.test_match(data)

    def test_encode_pair(self, data):
        pass

    def test_decode_pair(self, data):
        pass

    def test_match(self, data):
        pass


class TestFrTestCases(unittest.TestCase):
    def setUp(self):
        self.context_manager = ContextManager()

    def tearDown(self):
        pass

    def test_all_fr_test_cases(self):
        for test_case_file in os.listdir(test_case_file_dir):
            self.context_manager.parse_file(test_case_file)
