import unittest
import os
from tests.frparser.frtestparser import ParseError, FrTestCaseParser
import configparser

config_file = './frparser/testconfig.ini'
config = configparser.ConfigParser()
config.read(config_file)


class FrTestCaseRetriever:
    def __init__(self, encode_func, decode_func, match_func):
        self.parser = FrTestCaseParser()

        self.encode_func = encode_func
        self.decode_func = decode_func
        self.match = match_func

        self.ready_for_match = None

    def parse_file(self, file):
        self.ready_for_match = False
        file_test_cases = {}

        with open(file, 'r') as file_open:
            for line_num, line_content in enumerate(file_open):
                try:
                    cmd, test_case = self.parse_line(line_content)
                    if cmd:
                        match cmd:
                            case 'encode-pair' | 'decode-pair':
                                file_test_cases[line_num + 1] = test_case
                                self.ready_for_match = True
                            case 'match':
                                if self.ready_for_match:
                                    file_test_cases[line_num + 1] = test_case
                                    self.ready_for_match = False
                except ParseError as e:
                    print(f'Encountered Parse Error in file {file} on line'
                          f' {line_num + 1}. Error: {e}')

        return file_test_cases

    def parse_line(self, line_content):
        test_case_funcs = {
            'encode-pair': self.encode_func,
            'decode-pair': self.decode_func,
            'match': self.match
        }

        test_case = self.parser.start(line_content)
        if test_case:
            return test_case[0], (test_case_funcs[test_case[0]], test_case[1])
        return None, None


class TestFrTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tc_retriever = FrTestCaseRetriever(
            cls.run_encode_pair, cls.run_decode_pair, cls.run_match
        )
        cls.previous_result = 'None'

        # contains 2D array, with each file being an inner array
        cls.test_cases = {}
        for root, dirs, files in os.walk(config['FRTESTCASES']['testFileDir']):
            for file in files:
                file_path = os.path.join(root, file)
                cls.test_cases[file_path] = (
                    cls.tc_retriever.parse_file(file_path)
                )

        for i in cls.test_cases.keys():
            for j in sorted(list(cls.test_cases[i].keys())):
                print(i, j, cls.test_cases[i][j])

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
