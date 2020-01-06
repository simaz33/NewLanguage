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
addInstr(0x12, 'I_INT_MULT', 0)
addInstr(0x13, 'I_INT_DIV', 0)
addInstr(0x14, 'I_INT_MOD', 0)
addInstr(0x15, 'I_INC', 0)
addInstr(0x16, 'I_DEC', 0)
addInstr(0x17, 'I_FLOAT_ADD', 0)
addInstr(0x18, 'I_FLOAT_SUB', 0)
addInstr(0x19, 'I_FLOAT_MUL', 0)
addInstr(0x1A, 'I_FLOAT_DIV', 0)

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

# Logical instructions
addInstr(0x50, 'I_OR', 0)
addInstr(0x51, 'I_AND', 0)

# Stack instructions
addInstr(0x30, 'I_GET_L', 1)
addInstr(0x31, 'I_SET_L', 1)
addInstr(0x32, 'I_POP', 0)
addInstr(0x33, 'I_INT_PUSH', 1)
addInstr(0x34, 'I_FLOAT_PUSH', 1)
addInstr(0x35, 'I_STRING_PUSH', 1)
addInstr(0x36, 'I_BOOLEAN_PUSH', 1)
addInstr(0x37, 'I_ALLOC', 1)

# Control instructions
addInstr(0x40, 'I_BR', 1)
addInstr(0x41, 'I_BZ', 1)
addInstr(0x42, 'I_RET', 0)
addInstr(0x43, 'I_RET_V', 0)
addInstr(0x44, 'I_CALL_BEGIN', 0)
addInstr(0x45, 'I_CALL', 2)
addInstr(0x46, 'I_EXIT', 0)

#Standard input/output
addInstr(0x50, 'I_STDOUT', 0)
addInstr(0x51, 'I_STDIN_STRING', 1)
addInstr(0x52, 'I_STDIN_INT', 1)
addInstr(0x53, 'I_STDIN_FLOAT', 1)
addInstr(0x54, 'I_STDIN_BOOLEAN', 1)