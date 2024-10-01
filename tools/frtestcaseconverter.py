import os
from tests.frparser.frtestparserv4 import V4FrTestParser, TestCommands

READ_TEST_DIR = '../tests/testcases'
WRITE_TEST_DIR = '../tests/testfrtestcases'

class FrTCConverter:
    def __init__(self):
        self.parser = V4FrTestParser()
        self.testcases = []

    def parse_file(self, filename):
        self.testcases = []

        looking_for_match = False
        with open(filename, 'r') as fileopen:
            for line in fileopen:
                cmd, testcase = self.parser.start(line)
                match cmd:
                    case TestCommands.encode_pair.value | TestCommands.decode_pair.value:
                        if not looking_for_match:
                            self.testcases.append(testcase)
                            looking_for_match = True
                    case TestCommands.match.value:
                        if looking_for_match:
                            self.testcases.append(testcase)
                            looking_for_match = False

    def write_to_file(self, filename):
        # don't create an "empty" unittest file
        if not self.testcases:
            return

        with open(filename, 'w+') as fileopen:
            fileopen.write()

    def mirror_file_structure(self, read_dir, write_dir):
        for filename in os.listdir(read_dir):
            if os.path.isdir(os.path.join(read_dir, filename)):
                if not os.path.isdir(os.path.join(write_dir, filename)):
                    os.mkdir(os.path.join(write_dir, filename))
                self.mirror_file_structure(os.path.join(read_dir, filename),
                                      os.path.join(write_dir, filename))
            elif os.path.isfile(os.path.join(read_dir, filename)):
                self.parse_file(os.path.join(read_dir, filename))
                self.write_to_file(os.path.join(write_dir, filename))

if __name__ == '__main__':
    converter = FrTCConverter()
    converter.mirror_file_structure(READ_TEST_DIR, WRITE_TEST_DIR)
