class TestCaseContext:
    def __init__(self, filename, line_num, command, values):
        self._filename = filename
        self._line_num = line_num

        self._command = command
        self._values = values

    @property
    def filename(self):
        return self._filename

    @property
    def line_num(self):
        return self._line_num

    @property
    def command(self):
        return self._command

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, value):
        self._values = value
