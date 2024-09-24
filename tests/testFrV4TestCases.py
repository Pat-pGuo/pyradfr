import unittest
from pyrad.dictionary import Dictionary
from pyrad.datatypes import *
from tests.frparser.frtestparserv4 import V4FrTestParser, TestCommands, Pair
from tests.frparser.testcasecontext import TestCaseContext
import os
import configparser

config_file = './frparser/testconfig.ini'
config = configparser.ConfigParser()
config.read(config_file)

class V4TestCaseRetriever:
    def __init__(self):
        self.parser = V4FrTestParser()

        self.looking_for_match_command = False

    def load_file(self, filename) -> list[TestCaseContext]:
        testcases = []

        with open(filename, 'r') as fileopen:
            for line_num, line_content in enumerate(fileopen):
                command, values = self.parser.start(line_content)
                match command:
                    case TestCommands.encode_pair.value | TestCommands.decode_pair.value:
                        testcases.append(TestCaseContext(filename, line_num + 1,
                                                         command, values))
                        self.looking_for_match_command = True
                    case TestCommands.match.value:
                        if not self.looking_for_match_command:
                            continue
                        testcases.append(TestCaseContext(filename, line_num + 1,
                                                         command, values))
                        self.looking_for_match_command = False

        return testcases

class DataTypeConverter:
    def __init__(self, dictionary: Dictionary = None):
        self.dictionary = dictionary
        if dictionary is None:
            self.dictionary = Dictionary(config['FRTESTCASES']['dictionary'])

    def convert_fr_datatype(self, datatype: str, value: Pair):
        match datatype:
            case 'string' | 'String':
                return 1
            case 'ipaddr':
                return
            case 'integer':
                return
            case 'date':
                return
            case 'octets':
                return
            case 'abinary':
                return
            case 'ipv6addr':
                return
            case 'ipv6prefix':
                return
            case 'short':
                return
            case 'byte':
                return
            case 'signed':
                return
            case 'ifid':
                return
            case 'ether':
                return
            case 'tlv':
                return
            case 'integer64':
                return
            case 'combo-ip':
                return
            case 'ipv4prefix':
                return
            case 'uint32':
                return
            case 'vsa':
                return
            case 'extended':
                return
            case 'long-extended':
                return
            case 'evs':
                return
            case 'float32':
                return
            case 'int64':
                return
            case 'uint8':
                return
            case 'uint64':
                return
            case 'bool':
                return
            case 'uint16':
                return

    def convert_testcase_values(self, values, previous_result):
        if values == '-':
            return previous_result
        elif isinstance(values, list):
            converted_values = []
            for pair in values:
                converted_values.append(
                    self.convert_fr_datatype(
                        self.dictionary.attributes[''.join(pair.name)].type,
                        pair.value
                    )
                )
            return converted_values
        return values

class TestFrV4TestCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dictionary = Dictionary(config['FRTESTCASES']['dictionary'])

        cls.testcases: list[TestCaseContext] = []
        cls.tc_retriever = V4TestCaseRetriever()
        for root, dirs, files in os.walk(config['FRTESTCASES']['testFileDir']):
            for file in files:
                filepath = os.path.join(root, file)
                for testcase in cls.tc_retriever.load_file(filepath):
                    cls.testcases.append(testcase)

        cls.previous_result = None

    def run_encode_pair_test(self, testcase_context):
        testcase_context.values = self.convert_testcase_values(testcase_context.values)

    def run_decode_pair_test(self, testcase_context):
        testcase_context.values = self.convert_testcase_values(testcase_context.values)

    def run_match_test(self, testcase_context):
        testcase_context.values = self.convert_testcase_values(testcase_context.values)

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
