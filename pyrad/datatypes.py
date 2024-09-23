class Tlv:
    def __init__(self, datatype, length, value):
        self.type: int = datatype
        self.len: int = length
        self.val: any = value

    @property
    def datatype(self):
        return self.type

    @property
    def length(self):
        return self.len

    @property
    def value(self):
        return self.val
