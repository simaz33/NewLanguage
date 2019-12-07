import globalVars as gv
class Instruction():
    def __init__(self, opcode, name, numOps):
        self.opcode = opcode
        self.name = name
        self.numOps = numOps

def addInstr(opcode, name, numOps):
    instr = Instruction(opcode, name, numOps)
    gv.instrsByName[name] = instr
    gv.instrsByOpcode[opcode] = instr

# Arithmetic instructions
addInstr(0x10, 'I_INT_ADD', 0)
addInstr(0x11, 'I_INT_SUB', 0)
addInstr(0x12, 'I_INT_MUL', 0)
addInstr(0x13, 'I_INT_DIV', 0)
addInstr(0x14, 'I_INT_INC', 0)
addInstr(0x15, 'I_INT_DEC', 0)
addInstr(0x16, 'I_FLOAT_ADD', 0)
addInstr(0x17, 'I_FLOAT_SUB', 0)
addInstr(0x18, 'I_FLOAT_MUL', 0)
addInstr(0x19, 'I_FLOAT_DIV', 0)

# Comparison instructions
addInstr(0x20, 'I_INT_LESS', 0)
addInstr(0x21, 'I_INT_LESS_E', 0)
addInstr(0x22, 'I_INT_GREATER', 0)
addInstr(0x23, 'I_INT_GREATER_E', 0)
addInstr(0x24, 'I_FLOAT_LESS', 0)
addInstr(0x25, 'I_FLOAT_LESS_E', 0)
addInstr(0x26, 'I_FLOAT_GREATER', 0)
addInstr(0x27, 'I_FLOAT_GREATER_E', 0)
addInstr(0x28, 'I_EQ', 0)
addInstr(0x29, 'I_NOT_EQ', 0)

# Stack instructions
addInstr(0x30, 'I_GET_L', 1)
addInstr(0x31, 'I_SET_L', 1)
addInstr(0x32, 'I_POP', 0)
addInstr(0x33, 'I_INT_PUSH', 1)

# Control instructions
addInstr(0x40, 'I_BR', 1)
addInstr(0x41, 'I_BZ', 1)
addInstr(0x42, 'I_RET', 0)
addInstr(0x43, 'I_RET_V', 0)
addInstr(0x44, 'I_CALL_BEGIN', 0)
addInstr(0x45, 'I_CALL', 2)
