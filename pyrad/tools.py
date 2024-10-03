# tools.py
#
# Utility functions
from ipaddress import IPv4Address, IPv6Address
from ipaddress import IPv4Network, IPv6Network
import struct
import binascii
from pyrad.datatypes import Tlv, Extended, LongExtended, Vsa, Evs


def EncodeString(origstr):
    if len(origstr) > 253:
        raise ValueError('Can only encode strings of <= 253 characters')
    if isinstance(origstr, str):
        return origstr.encode('utf-8')
    else:
        return origstr


def EncodeOctets(octetstring):
    # Check for max length of the hex encoded with 0x prefix, as a sanity check
    if len(octetstring) > 508:
        raise ValueError('Can only encode strings of <= 253 characters')

    if isinstance(octetstring, bytes) and octetstring.startswith(b'0x'):
        hexstring = octetstring.split(b'0x')[1]
        encoded_octets = binascii.unhexlify(hexstring)
    elif isinstance(octetstring, str) and octetstring.startswith('0x'):
        hexstring = octetstring.split('0x')[1]
        encoded_octets = binascii.unhexlify(hexstring)
    elif isinstance(octetstring, str) and octetstring.isdecimal():
        encoded_octets = struct.pack('>L',int(octetstring)).lstrip((b'\x00'))
    else:
        encoded_octets = octetstring

    # Check for the encoded value being longer than 253 chars
    if len(encoded_octets) > 253:
        raise ValueError('Can only encode strings of <= 253 characters')

    return encoded_octets

def EncodeIPv4Prefix(addr):
    if not isinstance(addr, str):
        raise TypeError('Address has to be a string')
    network = IPv4Network(addr)
    return struct.pack('2B', *[0, network.prefixlen]) + network.network_address.packed

def EncodeAddress(addr):
    if not isinstance(addr, str):
        raise TypeError('Address has to be a string')
    return IPv4Address(addr).packed


def EncodeIPv6Prefix(addr):
    if not isinstance(addr, str):
        raise TypeError('IPv6 Prefix has to be a string')
    ip = IPv6Network(addr)
    return struct.pack('2B', *[0, ip.prefixlen]) + ip.ip.packed


def EncodeIPv6Address(addr):
    if not isinstance(addr, str):
        raise TypeError('IPv6 Address has to be a string')
    return IPv6Address(addr).packed


def EncodeAscendBinary(orig_str):
    """
    Format: List of type=value pairs separated by spaces.

    Example: 'family=ipv4 action=discard direction=in dst=10.10.255.254/32'

    Note: redirect(0x20) action is added for http-redirect (walled garden) use case

    Type:
        family      ipv4(default) or ipv6
        action      discard(default) or accept or redirect
        direction   in(default) or out
        src         source prefix (default ignore)
        dst         destination prefix (default ignore)
        proto       protocol number / next-header number (default ignore)
        sport       source port (default ignore)
        dport       destination port (default ignore)
        sportq      source port qualifier (default 0)
        dportq      destination port qualifier (default 0)

    Source/Destination Port Qualifier:
        0   no compare
        1   less than
        2   equal to
        3   greater than
        4   not equal to
    """

    terms = {
        'family':       b'\x01',
        'action':       b'\x00',
        'direction':    b'\x01',
        'src':          b'\x00\x00\x00\x00',
        'dst':          b'\x00\x00\x00\x00',
        'srcl':         b'\x00',
        'dstl':         b'\x00',
        'proto':        b'\x00',
        'sport':        b'\x00\x00',
        'dport':        b'\x00\x00',
        'sportq':       b'\x00',
        'dportq':       b'\x00'
    }

    family = 'ipv4'
    for t in orig_str.split(' '):
        key, value = t.split('=')
        if key == 'family' and value == 'ipv6':
            family = 'ipv6'
            terms[key] = b'\x03'
            if terms['src'] == b'\x00\x00\x00\x00':
                terms['src'] = 16 * b'\x00'
            if terms['dst'] == b'\x00\x00\x00\x00':
                terms['dst'] = 16 * b'\x00'
        elif key == 'action' and value == 'accept':
            terms[key] = b'\x01'
        elif key == 'action' and value == 'redirect':
            terms[key] = b'\x20'
        elif key == 'direction' and value == 'out':
            terms[key] = b'\x00'
        elif key == 'src' or key == 'dst':
            if family == 'ipv4':
                ip = IPv4Network(value)
            else: 
                ip = IPv6Network(value)
            terms[key] = ip.network_address.packed
            terms[key+'l'] = struct.pack('B', ip.prefixlen)
        elif key == 'sport' or key == 'dport':
            terms[key] = struct.pack('!H', int(value))
        elif key == 'sportq' or key == 'dportq' or key == 'proto':
            terms[key] = struct.pack('B', int(value))

    trailer = 8 * b'\x00'

    result = b''.join((terms['family'], terms['action'], terms['direction'], b'\x00',
        terms['src'], terms['dst'], terms['srcl'], terms['dstl'], terms['proto'], b'\x00',
        terms['sport'], terms['dport'], terms['sportq'], terms['dportq'], b'\x00\x00', trailer))
    return result


def EncodeInteger16(num, format='!H'):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer16')
    return struct.pack(format, num)

def EncodeInteger(num, format='!I'):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer')
    return struct.pack(format, num)


def EncodeInteger64(num, format='!Q'):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer64')
    return struct.pack(format, num)


def EncodeDate(num):
    if not isinstance(num, int):
        raise TypeError('Can not encode non-integer as date')
    return struct.pack('!I', num)

def EncodeEther(addr):
    return struct.pack('6H', *map(lambda x: int(x, 16), (addr.split(':'))))

def EncodeIfid(addr):
    return struct.pack('8H', *map(lambda x: int(x, 16), (addr.split(':'))))

def EncodeVsa(data: Vsa, attrcodes):
    type_bstr = struct.pack('B', data.datatype)
    len_bstr = struct.pack('B', data.length)
    vendor_id_bstr = struct.pack('I', data.vendor_id)

    v_attr = b''
    for attribute in data.attributes:
        v_attr += EncodeAttr('tlv', attribute, attrcodes)

    return type_bstr + len_bstr + vendor_id_bstr + v_attr

def DecodeString(orig_str):
    return orig_str.decode('utf-8')


def DecodeOctets(orig_bytes):
    return orig_bytes

def DecodeComboIp(addr):
    if len(addr) == 4:
        return DecodeAddress(addr)
    return DecodeIPv6Address(addr)

def DecodeIPv4Prefix(addr):
    addr = addr + b'\x00' * (6-len(addr))
    _, length, prefix = '.'.join(map('{0:x}'.format, struct.unpack('!BB' + 'B'*4, addr))).split('.', 2)
    return str(IPv4Network("%s/%s" % (prefix, int(length, 16))))

def DecodeAddress(addr):
    return '.'.join(map(str, struct.unpack('BBBB', addr)))


def DecodeIPv6Prefix(addr):
    addr = addr + b'\x00' * (18-len(addr))
    _, length, prefix = ':'.join(map('{0:x}'.format, struct.unpack('!BB'+'H'*8, addr))).split(":", 2)
    return str(IPv6Network("%s/%s" % (prefix, int(length, 16))))


def DecodeIPv6Address(addr):
    addr = addr + b'\x00' * (16-len(addr))
    prefix = ':'.join(map('{0:x}'.format, struct.unpack('!'+'H'*8, addr)))
    return str(IPv6Address(prefix))


def DecodeAscendBinary(orig_bytes):
    return orig_bytes

def DecodeInteger16(num, format='!H'):
    return (struct.unpack(format, num))[0]

def DecodeInteger(num, format='!I'):
    return (struct.unpack(format, num))[0]

def DecodeInteger64(num, format='!Q'):
    return (struct.unpack(format, num))[0]

def DecodeDate(num):
    return (struct.unpack('!I', num))[0]

def DecodeEther(addr):
    return ':'.join(map('{0:02x}'.format, struct.unpack('H'*6, addr))).upper()

def DecodeIfid(addr):
    return ':'.join(map('{0:02x}'.format, struct.unpack('H'*8, addr))).upper()

def DecodeVsa(data, attrcodes):
    v_type = struct.unpack('B', data[0:1])
    v_len = struct.unpack('B', data[1:2])
    v_id = struct.unpack('I', data[2:6])

    curr_attribute_start = 6
    attributes = []
    while curr_attribute_start < len(data):
        datatype = struct.unpack('B', data[curr_attribute_start : curr_attribute_start + 1])[0]
        length = struct.unpack('B', data[curr_attribute_start + 1: curr_attribute_start + 2])[0]
        value = DecodeAttr(datatype, data[curr_attribute_start + 2 : curr_attribute_start + length], attrcodes)

        attributes.append(Tlv(datatype, length, value))

    return Vsa(v_type, v_len, v_id, attributes)

def EncodeFloat32(value):
    try:
        value = float(value)
    except:
        raise TypeError('Can not encode non-float as float32')
    return struct.pack('f', value)

def DecodeFloat32(value):
    return struct.unpack('f', value)[0]

def EncodeInt64(value):
    try:
        value = int(value)
    except:
        raise TypeError('Can not encode non-integer as int64')
    return struct.pack('q', value)

def DecodeInt64(value):
    return struct.unpack('q', value)[0]

def EncodeUint8(value):
    try:
        if value.startswith('0x'):
            value = int(value, 16)
        else:
            value = int(value)
    except:
        raise TypeError('Can not encode non-integer as uint8')
    return struct.pack('B', value)

def DecodeUint8(value):
    return struct.unpack('B', value)[0]

def EncodeUint64(value):
    try:
        value = int(value)
    except:
        raise TypeError('Can not encode non-integer as uint64')
    return struct.pack('Q', value)

def DecodeUint64(value):
    return struct.unpack('Q', value)[0]

def EncodeBool(value):
    try:
        value = int(value)
    except:
        raise TypeError('Can not encode non-integer as bool')
    return struct.pack('B', bool(value))

def DecodeBool(value):
    return struct.unpack('c', value)[0]

def EncodeTlv(tlv: Tlv, attrcodes):
    type_bstr = struct.pack('B', tlv.datatype)
    len_bstr = struct.pack('B', tlv.length)

    # Use nested calls to encoded nested TLVs
    val_bstr = EncodeAttr(attrcodes.GetForward(tlv.datatype),
                          tlv.value, attrcodes)

    return type_bstr + len_bstr + val_bstr

def DecodeTlv(value, attrcodes) -> Tlv:
    datatype = struct.unpack('B', value[0:1])[0]
    length = struct.unpack('B', value[1:2])[0]

    value = DecodeAttr(attrcodes.GetForward(datatype),
                       value[2:length], attrcodes)
    return Tlv(datatype, length, value)

def EncodeUint16(num):
    try:
        if num.startswith('0x'):
            num = int(num, 16)
        else:
            num = int(num)
    except:
        raise TypeError('Can not encode non-integer as uint16')
    return struct.pack('!H', num)

def DecodeUint16(value):
    return struct.unpack('H', value)[0]

def EncodeLongExtended(value: LongExtended):
    datatype_bstr = struct.pack('B', value.datatype)
    length_bstr = struct.pack('B', value.length)
    extended_datatype_bstr = struct.pack('B', value.extended_type)

    more_bstr = struct.pack('B', 255 if value.more else 0)

    full_datatype = f'{value.datatype}.{value.extended_type}'

    # Value field of packet should already be encoded
    return (datatype_bstr + length_bstr + extended_datatype_bstr + more_bstr +
            value.value)

def DecodeLongExtended(value):
    datatype = struct.unpack('B', value[0:1])[0]
    length = struct.unpack('B', value[1:2])[0]
    extended_datatype = struct.unpack('B', value[2:3])[0]

    more = struct.unpack('B', value[3:4])[0] == 255

    return LongExtended(datatype, length, extended_datatype, more,
                        value[4:length])

def EncodeExtended(value: Extended, attrcodes):
    datatype_bstr = struct.pack('B', value.datatype)
    length_bstr = struct.pack('B', value.length)
    extended_datatype_bstr = struct.pack('B', value.extended_type)

    full_datatype = f'{value.datatype}.{value.extended_type}'

    val_bstr = EncodeAttr(attrcodes.GetForward(full_datatype),
                          value.value, attrcodes)
    return datatype_bstr + length_bstr + extended_datatype_bstr + val_bstr

def DecodeExtended(value, attrcodes):
    datatype = struct.unpack('B', value[0:1])[0]
    length = struct.unpack('B', value[1:2])[0]
    extended_datatype = struct.unpack('B', value[2:3])[0]
    full_datatype = f'{datatype}.{extended_datatype}'

    value = DecodeAttr(attrcodes.GetForward(full_datatype),
                       value[3:length], attrcodes)

    return Extended(datatype, length, extended_datatype, value)

def EncodeEvs(value: Evs, attrcodes):
    vendor_id_bstr = struct.pack('I', value.vendor_id)
    evs_type_bstr = struct.pack('B', value.evs_type)
    evs_value_bstr = EncodeAttr(attrcodes.GetForward(value.evs_type), value.evs_value, attrcodes)

    return vendor_id_bstr + evs_type_bstr + evs_value_bstr

def DecodeEvs(value, attrcodes):
    vendor_id, evs_type = struct.unpack('!IB', value[0:5])
    evs_value = DecodeAttr(attrcodes.GetForward(evs_type), value[5:], attrcodes)

    return Evs(vendor_id, evs_type, evs_value)

def EncodeAttr(datatype, value, attrcodes=None):
    if datatype == 'string':
        return EncodeString(value)
    elif datatype == 'octets':
        return EncodeOctets(value)
    elif datatype == 'integer' or datatype == 'uint32':
        return EncodeInteger(value)
    elif datatype == 'ipaddr':
        return EncodeAddress(value)
    elif datatype == 'ipv6prefix':
        return EncodeIPv6Prefix(value)
    elif datatype == 'ipv6addr':
        return EncodeIPv6Address(value)
    elif datatype == 'abinary':
        return EncodeAscendBinary(value)
    elif datatype == 'signed':
        return EncodeInteger(value, '!i')
    elif datatype == 'short':
        return EncodeInteger(value, '!H')
    elif datatype == 'byte':
        return EncodeInteger(value, '!B')
    elif datatype == 'date':
        return EncodeDate(value)
    elif datatype == 'integer64':
        return EncodeInteger64(value)
    elif datatype == 'combo-ip':
        if len(value.split('.')) == 4:
            return EncodeAddress(value)
    elif datatype == 'ipv4prefix':
        return EncodeIPv4Prefix(value)
    elif datatype == 'ether':
        return EncodeEther(value)
    elif datatype == 'ifid':
        return EncodeIfid(value)
    elif datatype == 'vsa':
        return EncodeVsa(value, attrcodes)
    elif datatype == 'float32':
        return EncodeFloat32(value)
    elif datatype == 'int64':
        return EncodeInt64(value)
    elif datatype == 'uint8':
        return EncodeUint8(value)
    elif datatype == 'uint64':
        return EncodeUint64(value)
    elif datatype == 'bool':
        return EncodeBool(value)
    elif datatype == 'tlv':
        return EncodeTlv(value, attrcodes)
    elif datatype == 'uint16':
        return EncodeUint16(value)
    elif datatype == 'long-extended':
        return EncodeLongExtended(value)
    elif datatype == 'extended':
        return EncodeExtended(value, attrcodes)
    elif datatype == 'evs':
        return EncodeEvs(value, attrcodes)
    else:
        raise ValueError('Unknown attribute type %s' % datatype)


def DecodeAttr(datatype, value, attrcodes=None):
    if not isinstance(value, bytes):
        value = value.encode('utf-8')

    if datatype== 'string':
        return DecodeString(value)
    elif datatype == 'octets':
        return DecodeOctets(value)
    elif datatype == 'integer' or datatype == 'uint32':
        return DecodeInteger(value)
    elif datatype == 'ipaddr':
        return DecodeAddress(value)
    elif datatype == 'ipv6prefix':
        return DecodeIPv6Prefix(value)
    elif datatype == 'ipv6addr':
        return DecodeIPv6Address(value)
    elif datatype == 'abinary':
        return DecodeAscendBinary(value)
    elif datatype == 'signed':
        return DecodeInteger(value, '!i')
    elif datatype == 'short':
        return DecodeInteger(value, '!H')
    elif datatype == 'byte':
        return DecodeInteger(value, '!B')
    elif datatype == 'date':
        return DecodeDate(value)
    elif datatype == 'integer64':
        return DecodeInteger64(value)
    elif datatype == 'combo-ip':
        if len(value) == '4':
            return DecodeAddress(value)
        return DecodeIPv6Address(value)
    elif datatype == 'ipv4prefix':
        return DecodeIPv4Prefix(value)
    elif datatype == 'ether':
        return DecodeEther(value)
    elif datatype == 'ifid':
        return DecodeIfid(value)
    elif datatype == 'vsa':
        return DecodeVsa(value, attrcodes)
    elif datatype == 'float32':
        return DecodeFloat32(value)
    elif datatype == 'int64':
        return DecodeInt64(value)
    elif datatype == 'uint8':
        return DecodeUint8(value)
    elif datatype == 'uint64':
        return DecodeUint64(value)
    elif datatype == 'bool':
        return DecodeBool(value)
    elif datatype == 'tlv':
        return DecodeTlv(value, attrcodes)
    elif datatype == 'uint16':
        return DecodeUint16(value)
    elif datatype == 'long-extended':
        return DecodeLongExtended(value)
    elif datatype == 'extended':
        return DecodeExtended(value, attrcodes)
    elif datatype == 'evs':
        return DecodeEvs(value, attrcodes)
    else:
        raise ValueError('Unknown attribute type %s' % datatype)
