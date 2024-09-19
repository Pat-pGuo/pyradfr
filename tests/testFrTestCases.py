import unittest
import os
from tests.frparser.frtestparser import ParseError, TestCaseParser

test_case_file_dir = ''


class TestFrTestCases(unittest.TestCase):
    def setUp(self):
        self.previous_result = None
        self.parser = TestCaseParser()

    def tearDown(self):
        self.previous_result = None

    def get_previous_result(self):
        return self.previous_result

    def test_all_fr_test_cases(self):
        for test_case_file in os.listdir(test_case_file_dir):
            with open(test_case_file, 'r') as file_open:
                for line_num, line_content in enumerate(file_open):
                    try:
                        test_case = self.parser.start(line_content, self.get_previous_result)
                        if test_case is not None:
                            cmd, data = test_case['testcase']
                            match cmd:
                                case 'encode-pair':
                                    for pair in data:
                                        attr_name, attr_value = pair

                                        # test case with these data
                                        print(attr_name, attr_value)
                                case 'decode-pair':

                                    # test case with these data
                                    print(data)
                                case 'match':

                                    # test case with these data
                                    print(data)
                    except ParseError as e:
                        print(
                            f'Encountered Parse Error in file {test_case_file}'
                            f' on line {line_num + 1}. Error: {e}')
