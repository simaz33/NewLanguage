import struct

floatSize = 4

def float2Bytes(value):
    return list(struct.pack('<f', value))


def bytes2Float(valueArray):
    floatBytes = bytes(valueArray[0: floatSize])
    value = struct.unpack('<f', floatBytes)
    return value[0]


def int_to_bytes(value, size=4, order='big'):
    return list(value.to_bytes(size, order, signed=True))


def string2Bytes(value):
    bytes_ = int_to_bytes(len(value))
    bytes_.extend(bytes(value, 'UTF-8'))
    return bytes_


def bytes2String(code):
    strSize = len(code)
    strLit = str(bytes(code[4: strSize], encoding='utf8'))
    return strLit