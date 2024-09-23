class Vsa:
    def __init__(self, datatype, length, vendor_id, attributes):
        self._type = datatype
        self._len = length
        self._vendor_id = vendor_id
        self._attributes: tuple[Tlv] = attributes

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
    def vendor_id(self):
        return self._vendor_id

    @vendor_id.setter
    def vendor_id(self, vendor_id):
        self._vendor_id = vendor_id

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        self._attributes = attributes

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

class Evs:
    def __init__(self, vendor_id, evs_type, evs_value):
        self._vendor_id = vendor_id
        self._evs_type = evs_type
        self._evs_value = evs_value

    @property
    def vendor_id(self):
        return self._vendor_id

    @vendor_id.setter
    def vendor_id(self, vendor_id):
        self._vendor_id = vendor_id

    @property
    def evs_type(self):
        return self._evs_type

    @evs_type.setter
    def evs_type(self, evs_type):
        self._evs_type = evs_type

    @property
    def evs_value(self):
        return self._evs_value

    @evs_value.setter
    def evs_value(self, evs_value):
        self._evs_value = evs_value