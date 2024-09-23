from tests.frparser.baseparser import BaseParser

import enum

class TestCommands(str, enum.Enum):
    encode_pair = 'encode-pair'
    decode_pair = 'decode-pair'
    match = 'match'

class ParseError(Exception):
    pass

class V4FrTestParser(BaseParser):
    def __init__(self, operator_tokens=None):
        super().__init__()
        self.operator_tokens = operator_tokens
        if not operator_tokens:
            self.operator_tokens = ['=', ':=']

    def start(self, buffer):
        self.buffer = buffer
        self.cursor = 0

        return self.token_command()

    def token_command(self):
        command_funcs = {
            TestCommands.encode_pair.value: self.cmd_encode_pair,
            TestCommands.decode_pair.value: self.cmd_decode_pair,
            TestCommands.match.value: self.cmd_match,
        }

        command = self.get_next_token()
        if command not in command_funcs.keys():
            return None

        return command_funcs[command]()

    def cmd_encode_pair(self):
        attr_name = self.token_attribute_name()
        operator = self.token_operators()
        attr_value = self.token_attribute_value()

        return attr_name, operator, attr_value

    def cmd_decode_pair(self):
        return 'B'

    def cmd_match(self):
        return 'C'

    def token_attribute_name(self):
        self.move_past_whitespace()

        cursor_start = self.cursor
        while not self.no_buffer_left:
            if self.at_whitespace:
                return (self.buffer[cursor_start:self.cursor],)

            self.cursor += 1
            if self.buffer[self.cursor] == '.':
                self.cursor += 1
                return (self.buffer[cursor_start:self.cursor-1],
                        *self.token_attribute_name())

    def token_operators(self):
        self.move_past_whitespace()

        cursor_start = self.cursor
        while not self.no_buffer_left:
            if self.at_whitespace:
                break
            self.cursor += 1

        if self.buffer[cursor_start:self.cursor] in self.operator_tokens:
            return self.buffer[cursor_start:self.cursor]

        raise ParseError

    def token_attribute_value(self):
        self.move_past_whitespace()

        if self.buffer[self.cursor] == '{':
            self.cursor += 1
            return self.token_dictionary_attribute()

        if self.buffer[self.cursor] == '"':
            self.cursor += 1
            return self.token_quoted_string()

        cursor_start = self.cursor
        while not self.no_buffer_left:
            if self.at_whitespace or self.buffer[self.cursor] == ',':
                return self.buffer[cursor_start:self.cursor]
            self.cursor += 1
        return self.buffer[cursor_start:self.cursor]

    def token_dictionary_attribute(self):
        self.move_past_whitespace()

        attr_name = self.token_attribute_name()
        operator = self.token_operators()
        attr_value = self.token_attribute_value()

        return {
            attr_name: attr_value,
        }

    def token_quoted_string(self):
        cursor_start = self.cursor
        while not self.no_buffer_left:
            if self.buffer[self.cursor] == '"':
                self.cursor += 1
                return self.buffer[cursor_start:self.cursor - 1]
            self.cursor += 1
