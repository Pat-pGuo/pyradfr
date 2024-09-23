class BaseParser:
    def __init__(self, whitespace_tokens=None):
        self.buffer = None
        self.cursor = None
        self.whitespace_tokens = whitespace_tokens
        if not whitespace_tokens:
            self.whitespace_tokens = [' ', '\n', '\r']

    def get_next_token(self):
        cursor_start = self.cursor
        while not self.no_buffer_left:
            if self.buffer[self.cursor] in self.whitespace_tokens:
                return self.buffer[cursor_start:self.cursor]
            self.cursor += 1
        return self.buffer[cursor_start:]

    def move_past_whitespace(self):
        while not self.no_buffer_left:
            if self.buffer[self.cursor] not in self.whitespace_tokens:
                return
            self.cursor += 1

    @property
    def at_whitespace(self):
        return self.buffer[self.cursor] in self.whitespace_tokens

    @property
    def no_buffer_left(self):
        return self.cursor >= len(self.buffer)