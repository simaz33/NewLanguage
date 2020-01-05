import sys
import binascii
errors = False
filename = sys.argv[1]
stackSlotIndex = 0
instrsByName = {}
instrsByOpcode = {}
strLits = []
