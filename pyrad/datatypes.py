class Tlv:
    def __init__(self, datatype, length, value):
        self._type: int = datatype
        self._len: int = length
        self._val: any = value

    @property
    def datatype(self):
        return self._type

    @datatype.setter
    def datatype(self, datatype):
        self._type = datatype

    @property
    def length(self):
        return self._len

    @length.setter
    def length(self, length):
        self._len = length

    @property
    def value(self):
        return self._val

    @value.setter
    def value(self, value):
        self._val = value

class Extended:
    def __init__(self, datatype, length, extended_type, value):
        self._type: int = datatype
        self._len = length
        self._extended_type = extended_type
        self._val: any = value

    @property
    def datatype(self):
        return self._type

    @datatype.setter
    def datatype(self, datatype):
        self._type = datatype

    @property
    def length(self):
        return self._len

    @length.setter
    def length(self, length):
        self._len = length

    @property
    def extended_type(self):
        return self._extended_type

    @extended_type.setter
    def extended_type(self, extended_type):
        self._extended_type = extended_type

    @property
    def value(self):
        return self._val

    @value.setter
    def value(self, value):
        self._val = value

class LongExtended(Extended):
    def __init__(self, datatype, length, extended_type, more, value):
        Extended.__init__(self, datatype, length, extended_type, value)
        self._more = more

    @property
    def more(self):
        return self._more

    @more.setter
    def more(self, more):
        self._more = more
