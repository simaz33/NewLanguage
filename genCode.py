import instrs
import globalVars as gv
class CodeWriter():
    def __init__(self):
        self.code = []

    def completeLabel(self, label, value):
        label.value = value
        for offset in label.offsets:
            self.code[offset] = value
    
    def dumpCode(self):
        offset = 0
        while offset < len(self.code):
            opcode = self.code[offset]
            instr = gv.instrsByOpcode[opcode]
            tmpOffset = offset + 1
            ops = []
            for i in range(tmpOffset, tmpOffset+instr.numOps):
                ops.append(str(self.code[i]))
            print('{:<2} | {:<2} | {:<16} {:<2}'.format(offset, opcode, instr.name, ', '.join(ops)))
            offset += 1 + instr.numOps

        print('RAW CODE:')
        print(self.code)

    def placeLabel(self, label):
        self.completeLabel(label, len(self.code))

    def write(self, instrName, *ops):
        instr = gv.instrsByName[instrName]
        if len(ops) != instr.numOps:
            print('invalid instruction operand count')
            exit(1)

        self.code.append(instr.opcode)
        for op in ops:
            if not isinstance(op, Label):
                self.code.append(op)
            elif not op.value:
                op.offsets.append(len(self.code))
                self.code.append(666)
            else:
                self.code.append(op.value)
    
class Label():
    def __init__(self):
        self.offsets = []
        self.value = None