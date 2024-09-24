import unittest
from pyrad.dictionary import Dictionary
from tests.frparser.frtestparserv4 import V4FrTestParser, TestCommands
from tests.frparser.testcasecontext import TestCaseContext
import os
import configparser

config_file = './frparser/testconfig.ini'
config = configparser.ConfigParser()
config.read(config_file)

class V4TestCaseRetriever:
    def __init__(self, dictionary: Dictionary = None):
        self.parser = V4FrTestParser()

        self.dict = dictionary
        if dictionary is None:
            self.dictionary = Dictionary()

        self.looking_for_match_command = False

    def load_file(self, filename):
        testcases = []

        with open(filename, 'r') as fileopen:
            for line_num, line_content in enumerate(fileopen):
                command, values = self.parser.start(line_content)
                match command:
                    case TestCommands.encode_pair.value | TestCommands.decode_pair.value:
                        testcases.append(TestCaseContext(filename, line_num,
                                                         command, values))
                        self.looking_for_match_command = True
                    case TestCommands.match.value:
                        if not self.looking_for_match_command:
                            continue
                        testcases.append(TestCaseContext(filename, line_num,
                                                         command, values))
                        self.looking_for_match_command = False

        return testcases


class TestFrV4TestCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testcases: list[TestCaseContext] = []
        cls.tc_retriever = V4TestCaseRetriever()
        for root, dirs, files in os.walk(config['FRTESTCASES']['testFileDir']):
            for file in files:
                filepath = os.path.join(root, file)
                for testcase in cls.tc_retriever.load_file(filepath):
                    cls.testcases.append(testcase)

        cls.previous_result = None

    def run_encode_pair_test(self, testcase_context):
        pass

    def run_decode_pair_test(self, testcase_context):
        pass

    def run_match_test(self, testcase_context):
        self.assertEqual(True, False)

    def test_all_test_cases(self):
        for testcase in self.testcases:
            with self.subTest(testcase=testcase,
                              filename=testcase.filename,
                              line_num=testcase.line_num):
                match testcase.command:
                    case TestCommands.encode_pair.value:
                        self.run_encode_pair_test(testcase)
                    case TestCommands.decode_pair.value:
                        self.run_decode_pair_test(testcase)
                    case TestCommands.match.value:
                        self.run_match_test(testcase)
