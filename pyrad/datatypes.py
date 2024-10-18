from typing import List


class Evs:
    def __init__(self, vendor_id, attr_code, data):
        self.vendor_id = vendor_id
        self.attr_code = attr_code
        self.data = data

class Tlv:
    def __init__(self, type_code, length, value):
        self.type_code = type_code
        self.length = length
        self.value = value

class Vsa:
    def __init__(self, vendor_id, tlv_list: List[Tlv]):
        self.vendor_id = vendor_id
        self.tlv_list = tlv_list
