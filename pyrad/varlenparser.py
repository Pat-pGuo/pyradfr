class VarLenParser:
    """
    Data type parser to support fixed length datatypes.

    I.e., octets[24] treated as octets

    """
    def __init__(self):
        self.buffer = None
        self.cursor = None

    def start(self, buffer):
        self.buffer = buffer
        self.cursor = 0

        return self.find_datatype()

    def find_datatype(self):
        cursor_start = self.cursor
        while self.cursor < len(self.buffer):
            if self.buffer[self.cursor] == '[':
                return (self.buffer[cursor_start:self.cursor],
                        self.find_length())
            self.cursor += 1
        return self.buffer[cursor_start:self.cursor], None

    def find_length(self):
        # skip [
        self.cursor += 1

        cursor_start = self.cursor
        while self.buffer[self.cursor] != ']':
            self.cursor += 1
        return int(self.buffer[cursor_start: self.cursor])
