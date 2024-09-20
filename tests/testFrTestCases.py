import unittest
import os
from tests.frparser.frtestparser import ParseError, FrTestCaseParser
import configparser

config_file = './frparser/testconfig.ini'
config = configparser.ConfigParser()
config.read(config_file)


class FrTestCaseRetriever:
    def __init__(self):
        self.parser = FrTestCaseParser()

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
                                file_test_cases[line_num + 1] = (cmd, test_case)
                                self.ready_for_match = True
                            case 'match':
                                if self.ready_for_match:
                                    file_test_cases[line_num + 1] = (cmd, test_case)
                                    self.ready_for_match = False
                except ParseError as e:
                    print(f'Encountered Parse Error in file {file} on line'
                          f' {line_num + 1}. Error: {e}')

        return file_test_cases

    def parse_line(self, line_content):
        test_case = self.parser.start(line_content)
        if test_case:
            return test_case[0],  test_case[1]
        return None, None


class TestFrTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tc_retriever = FrTestCaseRetriever()
        cls.previous_result = None

        # contains 2D array, with each file being an inner array
        cls.test_cases = {}
        for root, dirs, files in os.walk(config['FRTESTCASES']['testFileDir']):
            for file in files:
                file_path = os.path.join(root, file)
                cls.test_cases[file_path] = (
                    cls.tc_retriever.parse_file(file_path)
                )

    def run_encode_pair(self, data):
        pass # TODO :: run encoding

    def run_decode_pair(self, data):
        pass # TODO :: run decoding

    def run_match(self, data):
        self.assertEqual(self.previous_result, data)

    def test_all_fr_test_cases(self):
        for file in self.test_cases.keys():
            for line_num in self.test_cases[file]:
                cmd, data = self.test_cases[file][line_num]
                with self.subTest(cmd=cmd, data=data):
                    match cmd:
                        case 'encode-pair':
                            self.run_encode_pair(data)
                        case 'decode-pair':
                            self.run_decode_pair(data)
                        case 'match':
                            self.run_match(data)
