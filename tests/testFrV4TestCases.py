import unittest
from pyrad.dictionary import Dictionary
from tests.frparser.frtestparserv4 import V4FrTestParser, Pair, TestCommands
from tests.frparser.testcasecontext import TestCaseContext


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
    def setUp(cls):
        pass
