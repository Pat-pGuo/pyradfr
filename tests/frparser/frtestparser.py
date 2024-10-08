whitespaces = [' ', '\n', '\r']

class ParseError(Exception):
    pass

class FrTestCaseParser:
    def __init__(self):
        self.buffer = None
        self.cursor = None

    def get_next_word(self):
        cursor_start = self.cursor
        while self.buffer[self.cursor] not in whitespaces:
            self.cursor += 1

        return self.buffer[cursor_start:self.cursor]

    def skip_whitespace(self):
        while self.cursor < len(self.buffer):
            if not self.buffer[self.cursor] in whitespaces:
                return
            self.cursor += 1

    def check_for_pipe(self):
        return self.buffer[self.cursor:-1] == '-'

    def start(self, buffer):
        self.buffer = buffer
        self.cursor = 0

        return self.parse_command()

    def match_chars(self, *chars):
        for char in chars:
            if self.buffer[self.cursor] == char:
                self.cursor += 1
                return True
        raise ParseError(f'Expected one of {chars}, got '
                         f'{self.buffer[self.cursor]}')

    def parse_command(self):
        command_functions = {
            'encode-pair': self.cmd_encode_pair,
            'decode-pair': self.cmd_decode_pair,
            'match': self.cmd_match
        }

        cmd = self.get_next_word()
        if cmd not in command_functions:
            return None

        return command_functions[cmd]()

    def cmd_encode_pair(self):
        self.skip_whitespace()

        if self.check_for_pipe():
            return 'encode-pair', '-'

        pairs = []
        while self.cursor < len(self.buffer):
            pairs.append(self.get_attribute_pair())
            if self.cursor < len(self.buffer):
                self.match_chars(',', '\n')
                self.skip_whitespace()

        return 'encode-pair', pairs

    def cmd_decode_pair(self):
        self.skip_whitespace()

        if self.check_for_pipe():
            return 'decode-pair', '-'

        cursor_start = self.cursor
        while self.buffer[self.cursor] != '\n':
            self.cursor += 1

        return 'decode-pair', bytes.fromhex(self.buffer[cursor_start:self.cursor])

    def cmd_match(self):
        if self.buffer[self.cursor] == '\n':
            return 'match', ''

        if self.check_for_pipe():
            return 'match', '-'

        cursor_start = self.cursor
        while self.buffer[self.cursor] != '\n':
            self.cursor += 1

        return 'match', self.buffer[cursor_start:self.cursor]

    def get_attribute_pair(self):
        attribute_name = self.find_attribute_name()
        operator = self.get_operator()
        attribute_value = self.find_attribute_value()

        return attribute_name, operator, attribute_value

    def find_attribute_name(self):
        cursor_start = self.cursor

        # return essentially the next-full word (up to the next whitespace)
        while self.cursor < len(self.buffer):
            if self.buffer[self.cursor] == ' ':
                return self.buffer[cursor_start:self.cursor]
            self.cursor += 1
        raise ParseError(f'Buffer ended on an Attribute Name')

    def get_operator(self):
        self.skip_whitespace()
        operators = ['=', ':=']

        cursor_start = self.cursor

        last_match_cursor = None
        last_match_operator = None

        while self.cursor < len(self.buffer):
            if self.buffer[cursor_start:self.cursor] in operators:
                last_match_cursor = self.cursor
                last_match_operator = self.buffer[cursor_start:self.cursor]
            self.cursor += 1

        if last_match_cursor is None:
            raise ParseError(f'No equal operator found at pos {self.cursor}')

        self.cursor = last_match_cursor
        self.skip_whitespace()
        return last_match_operator

    def find_attribute_value(self):
        cursor_start = self.cursor
        if self.buffer[self.cursor] == '"':
            return self.find_quoted_string()

        while self.cursor < len(self.buffer):
            if self.buffer[self.cursor] == ',':
                return self.buffer[cursor_start: self.cursor]
            self.cursor += 1
        return self.buffer[cursor_start:self.cursor]

    def find_quoted_string(self):
        start_quote = self.match_chars('"')

        cursor_start = self.cursor
        while self.cursor < len(self.buffer):
            if self.buffer[self.cursor] == '"':
                end_quote = self.match_chars('"')
                # Don't want to return the double quotes as part of our string
                return self.buffer[cursor_start:self.cursor - 1]
            self.cursor += 1
        raise ParseError(f'Quote string not closed off')
