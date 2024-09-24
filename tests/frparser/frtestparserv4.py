from tests.frparser.baseparser import BaseParser
from tests.frparser.testcasecontext import TestCaseContext

import enum

token_prev_result = '-'

class TestCommands(str, enum.Enum):
    encode_pair = 'encode-pair'
    decode_pair = 'decode-pair'
    match = 'match'

class ParseError(Exception):
    pass

class Pair:
    def __init__(self, name, operator, value):
        self._name = name
        self._operator = operator
        self._value = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def operator(self):
        return self._operator

class V4FrTestParser(BaseParser):
    def __init__(self, operator_tokens=None, delimiter=','):
        super().__init__()
        self.operator_tokens = operator_tokens
        if not operator_tokens:
            self.operator_tokens = ['=', ':=']
        self.delimiter = delimiter

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
            return None, None

        return command, command_funcs[command]()

    def cmd_encode_pair(self) -> list[Pair] | str:
        self.move_past_whitespace()
        if self.buffer[self.cursor] == token_prev_result:
            self.cursor = len(self.buffer) - 1
            return '-'

        attributes = []
        while True:
            attr_name = self.token_attribute_name()
            operator = self.token_operators()
            attr_value = self.token_attribute_value()

            attributes.append(Pair(attr_name, operator, attr_value))

            # for dealing with whitespace as last char (e.g., '\n')
            self.move_past_whitespace()
            if self.no_buffer_left:
                break

            if self.buffer[self.cursor] == ',':
                self.cursor += 1

        return attributes

    def cmd_decode_pair(self) -> bytes | str:
        self.move_past_whitespace()

        if self.buffer[self.cursor] == token_prev_result:
            self.cursor = len(self.buffer) - 1
            return '-'

        return bytes.fromhex(self.buffer[self.cursor:])

    def cmd_match(self) -> bytes | list[Pair] | str:
        self.move_past_whitespace()
        if self.no_buffer_left:
            return ''

        cursor_start = self.cursor
        try:
            return self.cmd_decode_pair()
        except ValueError:
            self.cursor = cursor_start
            try:
                return self.cmd_encode_pair()
            except ParseError:
                self.cursor = cursor_start
                return self.buffer[self.cursor:]

    def token_attribute_name(self) -> tuple[str,...]:
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

    def token_operators(self) -> str:
        self.move_past_whitespace()

        cursor_start = self.cursor
        while not self.no_buffer_left:
            if self.at_whitespace:
                break
            self.cursor += 1

        if self.buffer[cursor_start:self.cursor] in self.operator_tokens:
            return self.buffer[cursor_start:self.cursor]

        raise ParseError

    def token_attribute_value(self) -> str | list[Pair]:
        self.move_past_whitespace()

        if self.buffer[self.cursor] == '{':
            self.cursor += 1
            return self.token_dictionary_attribute()

        if self.buffer[self.cursor] == '"':
            self.cursor += 1
            return self.token_double_quoted_string()

        if self.buffer[self.cursor] == "'":
            self.cursor += 1
            return self.token_single_quoted_string()

        cursor_start = self.cursor
        while not self.no_buffer_left:
            if self.at_whitespace or self.buffer[self.cursor] == ',':
                return self.buffer[cursor_start:self.cursor]
            self.cursor += 1
        return self.buffer[cursor_start:self.cursor]

    def token_dictionary_attribute(self) -> list[Pair]:
        self.move_past_whitespace()

        values = []

        while True:
            attr_name = self.token_attribute_name()
            operator = self.token_operators()
            attr_value = self.token_attribute_value()

            values.append(Pair(attr_name, operator, attr_value))

            self.move_past_whitespace()

            if self.buffer[self.cursor] == '}':
                self.cursor += 1
                break

            if self.buffer[self.cursor] == ',':
                self.cursor += 1

        return values

    def token_double_quoted_string(self) -> str:
        cursor_start = self.cursor
        while not self.no_buffer_left:
            if self.buffer[self.cursor] == '"':
                self.cursor += 1
                return self.buffer[cursor_start:self.cursor - 1]
            self.cursor += 1

    def token_single_quoted_string(self) -> str:
        cursor_start = self.cursor
        while not self.no_buffer_left:
            if self.buffer[self.cursor] == "'":
                self.cursor += 1
                return self.buffer[cursor_start:self.cursor - 1]
            self.cursor += 1
