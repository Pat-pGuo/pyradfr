import os
from tests.frparser.frtestparserv4 import V4FrTestParser, TestCommands
from jinja2 import Environment, FileSystemLoader

READ_TEST_DIR = '../tests/testcases'
WRITE_TEST_DIR = '../tests/testfrtestcases'

CLASS_TEMPLATE = './fr_testcase_class_template.txt'
FUNC_TEMPLATE = './fr_testcase_function_template.txt'

class FrTCConverter:
    def __init__(self, read_dir, write_dir):
        self.parser = V4FrTestParser()
        self.testcases = []

        self.read_dir = read_dir
        self.write_dir = write_dir

        class_template_env = Environment(loader=FileSystemLoader(''))
        function_template_env = Environment(loader=FileSystemLoader(''))

        self.class_template = class_template_env.get_template(CLASS_TEMPLATE)
        self.function_template = function_template_env.get_template(FUNC_TEMPLATE)

    def parse_file(self, filename):
        self.testcases = []

        looking_for_match = False
        with open(filename, 'r') as fileopen:
            for line_num, line_content in enumerate(fileopen):
                cmd, testcase = self.parser.start_cmd_only(line_content)
                match cmd:
                    case TestCommands.encode_pair.value | TestCommands.decode_pair.value:
                        if not looking_for_match:
                            self.testcases.append([line_num, cmd, testcase])
                            looking_for_match = True
                    case TestCommands.match.value:
                        if looking_for_match:
                            self.testcases.append([line_num, cmd, testcase])
                            looking_for_match = False

    def write_to_file(self, filedir, filename: str):
        # don't create an "empty" unittest file
        if not self.testcases:
            return

        fullpath = os.path.join(
            filedir,
            f"test{filename.replace('.txt', '.py')}"
        )
        classname = f'Test{filename.split('.')[0].title()}'

        with open(fullpath, 'w') as fileopen:
            fileopen.write(
                self.class_template.render(
                    class_name = classname,
                )
            )

            for testcase in self.testcases:
                testcase_value = ''
                testcase[2] = testcase[2].replace("'", '"')
                match testcase[1]:
                    case TestCommands.encode_pair.value:
                        testcase_value = f"self.encode_pair('{testcase[2]}')"
                    case TestCommands.decode_pair.value:
                        testcase_value = f"self.decode_pair('{testcase[2]}')"
                    case TestCommands.match.value:
                        testcase_value = f"self.match('{testcase[2]}')"
                fileopen.write(
                    self.function_template.render(
                        testcase_name = f'{testcase[0]}',
                        testcase = testcase_value
                    )
                )

    def mirror_file_structure(self, read_dir, write_dir):
        for filename in os.listdir(read_dir):
            if os.path.isdir(os.path.join(read_dir, filename)):
                if not os.path.isdir(os.path.join(write_dir, filename)):
                    os.mkdir(os.path.join(write_dir, filename))
                self.mirror_file_structure(os.path.join(read_dir, filename),
                                      os.path.join(write_dir, filename))
            elif os.path.isfile(os.path.join(read_dir, filename)):
                self.parse_file(os.path.join(read_dir, filename))
                self.write_to_file(write_dir, filename)

    def start(self):
        self.mirror_file_structure(self.read_dir, self.write_dir)

if __name__ == '__main__':
    converter = FrTCConverter(READ_TEST_DIR, WRITE_TEST_DIR)
    converter.start()
