# tools.py
#
# Utility functions
from ipaddress import IPv4Address, IPv6Address
from ipaddress import IPv4Network, IPv6Network
import struct
import binascii
import sys
from tkinter.ttk import Label
from pyrad.datatypes import Evs

curr_module = sys.modules[__name__]


# Encoding functions

def encode_string(origstr, attributes = None):
    if len(origstr) > 253:
        raise ValueError('Can only encode strings of <= 253 characters')
    if isinstance(origstr, str):
        return origstr.encode('utf-8')
    else:
        return origstr


def encode_octets(octetstring, attributes = None):
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


def encode_ipaddr(addr, attributes = None):
    if not isinstance(addr, str):
        raise TypeError('Address has to be a string')
    return IPv4Address(addr).packed


def encode_ipv6prefix(addr, attributes = None):
    if not isinstance(addr, str):
        raise TypeError('IPv6 Prefix has to be a string')
    ip = IPv6Network(addr)
    return struct.pack('2B', *[0, ip.prefixlen]) + ip.ip.packed


def encode_ipv6addr(addr, attributes = None):
    if not isinstance(addr, str):
        raise TypeError('IPv6 Address has to be a string')
    return IPv6Address(addr).packed


def encode_abinary(orig_str, attributes = None):
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


def encode_signed(num, attributes = None):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer')
    return struct.pack('!i', num)


def encode_integer64(num, attributes = None):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer64')
    return struct.pack('!Q', num)


def encode_date(num, attributes = None):
    if not isinstance(num, int):
        raise TypeError('Can not encode non-integer as date')
    return struct.pack('!I', num)

def encode_integer(num, attributes = None):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer')
    return struct.pack('!I', num)

def encode_short(num, attributes = None):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer')
    return struct.pack('!H', num)

def encode_byte(num, attributes = None):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer')
    return struct.pack('!B', num)

def encode_enum(num, attributes = None):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer')
    return struct.pack('!I', num)

def encode_combo_ip(addr, attributes = None):
    if len(addr.split('.')) == 4:
        return encode_ipaddr(addr)
    return encode_ipv6addr(addr)

def encode_uint8(num, attributes = None):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer')
    return struct.pack('!B', num)

def encode_uint16(num, attributes = None):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer')
    return struct.pack('!H', num)

def encode_uint32(num, attributes = None):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer')
    return struct.pack('!I', num)

def encode_uint64(num, attributes = None):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer')
    return struct.pack('!Q', num)


def encode_int64(num, attributes = None):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as integer')
    return struct.pack('!q', num)

def encode_float32(num, attributes = None):
    try:
        num = float(num)
    except:
        raise TypeError('Can not encode non-float as float')
    return struct.pack('!f', num)

def encode_ipv4prefix(addr, attributes = None):
    if not isinstance(addr, str):
        raise TypeError('Address has to be a string')
    network = IPv4Network(addr)
    return (struct.pack('!2B', *[0, network.prefixlen]) +
            network.network_address.packed)

def encode_ifid(addr, attributes = None):
    if not isinstance(addr, str):
        raise TypeError('Address has to be a string')
    fields = addr.split(':')
    octets = []
    for field in fields:
        octets.append(int(field[:2], 16))
        octets.append(int(field[2:], 16))
    return struct.pack('!8B', *octets)

def encode_ether(addr, attributes = None):
    if not isinstance(addr, str):
        raise TypeError('Address has to be a string')
    return struct.pack('!6B', *map(lambda x: int(x, 16), addr.split(':')))

def encode_bool(num, attributes = None):
    try:
        num = int(num)
    except:
        raise TypeError('Can not encode non-integer as boolean')
    return struct.pack('!B', num)

def encode_evs(evs: Evs, attributes = None):
    vendor_id_encoding = struct.pack('!L', evs.vendor_id)
    attr_code_encoding = struct.pack('!B', evs.attr_code)
    data_encoding = EncodeAttr(convert_code_to_datatype(attributes,
                                                        evs.attr_code),
                               evs.data, attributes)
    return vendor_id_encoding + attr_code_encoding + data_encoding

# Decoding functions

def decode_string(orig_str, attributes = None):
    return orig_str.decode('utf-8')


def decode_octets(orig_bytes, attributes = None):
    return orig_bytes


def decode_ipaddr(addr, attributes = None):
    return '.'.join(map(str, struct.unpack('BBBB', addr)))


def decode_ipv6prefix(addr, attributes = None):
    addr = addr + b'\x00' * (18-len(addr))
    _, length, prefix = ':'.join(map('{0:x}'.format, struct.unpack('!BB'+'H'*8, addr))).split(":", 2)
    return str(IPv6Network("%s/%s" % (prefix, int(length, 16))))


def decode_ipv6addr(addr, attributes = None):
    addr = addr + b'\x00' * (16-len(addr))
    prefix = ':'.join(map('{0:x}'.format, struct.unpack('!'+'H'*8, addr)))
    return str(IPv6Address(prefix))


def decode_abinary(orig_bytes, attributes = None):
    return orig_bytes


def decode_signed(num, attributes = None):
    return (struct.unpack('!i', num))[0]

def decode_integer64(num, attributes = None):
    return (struct.unpack('!Q', num))[0]

def decode_date(num, attributes = None):
    return (struct.unpack('!I', num))[0]

def decode_integer(num, attributes = None):
    return (struct.unpack('!I', num))[0]

def decode_short(num, attributes = None):
    return (struct.unpack('!H', num))[0]

def decode_byte(num, attributes = None):
    return (struct.unpack('!B', num))[0]

def decode_enum(num, attributes = None):
    return (struct.unpack('!I', num))[0]

def decode_combo_ip(addr, attributes = None):
    if len(addr) == 4:
        return decode_ipaddr(addr)
    return decode_ipv6addr(addr)

def decode_uint8(num, attributes = None):
    return (struct.unpack('!B', num))[0]

def decode_uint16(num, attributes = None):
    return (struct.unpack('!H', num))[0]

def decode_uint32(num, attributes = None):
    return (struct.unpack('!I', num))[0]

def decode_uint64(num, attributes = None):
    return (struct.unpack('!Q', num))[0]

def decode_int64(num, attributes = None):
    return (struct.unpack('!q', num))[0]

def decode_float32(num, attributes = None):
    return (struct.unpack('!f', num))[0]

def decode_ipv4prefix(addr, attributes = None):
    addr = addr + b'\x00' * (6 - len(addr))
    _, length, prefix = '.'.join(map('{0:x}'.format,
                                     struct.unpack('!BB' + 'B' * 4,
                                                   addr))
                                 ).split('.', 2)
    return str(IPv4Network('%s/%s' % (prefix, int(length, 16))))

def decode_ifid(addr, attributes = None):
    fields = list(map('{0:02x}'.format, struct.unpack('!8B', addr)))
    octets = []
    for i in range(4):
        octets.append(''.join(fields[i * 2: (i + 1) * 2]))
    return ':'.join(octets)

def decode_ether(addr, attributes = None):
    return ':'.join(map('{0:02x}'.format, struct.unpack('!6B', addr)))

def decode_bool(num, attributes = None):
    return (struct.unpack('!B', num))[0]

def decode_evs(evs, attributes = None):
    vendor_id = struct.unpack('!L', evs[0:4])[0]
    attr_code = struct.unpack('!B', evs[4:5])[0]
    data = DecodeAttr(convert_code_to_datatype(attributes, attr_code),
                      evs[5:], attributes)

    return Evs(vendor_id, attr_code, data)

# We need to pass the list of attribute definitions to each encoding/decoding
# function because nested attributes (evs, tlv, etc.) need to know the
# convertion between code <-> datatype
def EncodeAttr(datatype, value, attributes = None):
    try:
        # We need to replace any '-' in the datatype with '_' since python
        # doesn't allow '-' in function names. This is used for datatypes
        # like 'combo-ip'
        encode_func = getattr(curr_module,
                              f'encode_{datatype.replace('-', '_')}')
        return encode_func(value, attributes)
    except AttributeError:
        raise ValueError('Unknown attribute type %s' % datatype)

def DecodeAttr(datatype, value, attributes = None):
    try:
        decode_func = getattr(curr_module,
                              f'decode_{datatype.replace('-', '_')}')
        return decode_func(value, attributes)
    except AttributeError:
        raise ValueError('Unknown attribute type %s' % datatype)

def convert_code_to_datatype(attributes, code):
    for attribute in attributes:
        if attribute.code == code:
            return attribute.type

def convert_datatype_to_code(attributes, datatype):
    for attribute in attributes:
        if attribute.type == datatype:
            return attribute.code
