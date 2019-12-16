import sys
import binascii
errors = False
filename = sys.argv[1]
stackSlotIndex = 0
instrsByName = {}
instrsByOpcode = {}

def float2Int(f):
    return int(binascii.hexlify(bytes(str(f).encode('utf-8'))), 16)

def int2Float(i):
    return float(binascii.unhexlify(hex(i)[2:])) 