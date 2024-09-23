# tools.py
#
# Utility functions
from ipaddress import IPv4Address, IPv6Address
from ipaddress import IPv4Network, IPv6Network
import struct
import binascii


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

def EncodeVsa(data):
    v_type = struct.pack('B', data['type'])
    v_len = struct.pack('B', data['length'])
    v_id = struct.pack('I', data['id'])

    v_attr = b''
    for attribute in data['attributes']:
        attr_type = struct.pack('B', attribute['type'])
        attr_len = struct.pack('B', attribute['length'])
        attr_value = struct.pack('H', attribute['value'])

        v_attr += attr_type + attr_len + attr_value

    return v_type + v_len + v_id + v_attr

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

def DecodeVsa(data):
    v_type = struct.unpack('B', data[0:1])
    v_len = struct.unpack('B', data[1:2])
    v_id = struct.unpack('I', data[2:6])

    attributes = []
    for attr_num in range((len(data) - 6) // 4):
        attribute = data[6 + attr_num * 4: 6 + (attr_num + 1) * 4]

        attr_type = struct.unpack('B', attribute[0:1])
        attr_len = struct.unpack('B', attribute[1:2])
        attr_value = struct.unpack('H', attribute[2:])
        attributes.append({
            'type': attr_type,
            'length': attr_len,
            'value': attr_value
        })

    return {
        'type': v_type,
        'length': v_len,
        'id': v_id,
        'attributes': attributes
    }

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

def EncodeTlv(value):
    return # TODO

def DecodeTlv(value):
    return # TODO

def EncodeUint16(num):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as uint16')
    return struct.pack('!H', num)

def DecodeUint16(value):
    return struct.unpack('H', value)[0]

def EncodeAttr(datatype, value):
    if datatype.lower() == 'string':
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
        return EncodeVsa(value)
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
        return EncodeTlv(value)
    elif datatype == 'uint16':
        return EncodeUint16(value)
    else:
        raise ValueError('Unknown attribute type %s' % datatype)


def DecodeAttr(datatype, value):
    if not isinstance(value, bytes):
        value = value.encode('utf-8')

    if datatype.lower() == 'string':
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
        return DecodeVsa(value)
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
        return DecodeTlv(value)
    elif datatype == 'uint16':
        return DecodeUint16(value)
    else:
        raise ValueError('Unknown attribute type %s' % datatype)
