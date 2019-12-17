STACK_LOCATION = 1024
import globalVars as gv

class VM():
    def __init__(self, code):
        self.memory = [0 for i in range(0, 4096)]
        self.memory[0:len(code)] = code
        self.running = True
        self.ip = 0
        self.fp = STACK_LOCATION
        self.sp = STACK_LOCATION
    
    def exec(self):
        while self.running:
            self.execOne()

        result = self.pop()
        print(f'Result: {result}')


    def execCall(self, target, numArgs):
        newIp = target
        newFp = self.sp - numArgs
        newSp = newFp
        self.memory[newFp - 3] = self.ip
        self.memory[newFp - 2] = self.fp
        self.memory[newFp - 1] = newFp - 3
        self.ip = newIp
        self.fp = newFp
        self.sp = newSp

    def execRet(self, value):
        oldIp = self.memory[self.fp - 3]
        oldFp = self.memory[self.fp - 2]
        oldSp = self.memory[self.fp - 1]
        self.ip = oldIp
        self.fp = oldFp
        self.sp = oldSp
        self.push(value)

    def execOne(self):
        opcode = self.readImm()
        instr = gv.instrsByOpcode[opcode].name

        if instr in ['I_INT_ADD', 'I_FLOAT_ADD']:
            b = self.pop()
            a = self.pop()
            self.push(a + b)

        elif instr in ['I_INT_SUB', 'I_FLOAT_SUB']:
            b = self.pop()
            a = self.pop()
            self.push(a - b)

        elif instr in ['I_INT_MULT', 'I_FLOAT_MULT']:
            b = self.pop()
            a = self.pop()
            self.push(a * b)

        elif instr in ['I_INT_DIV', 'I_FLOAT_DIV']:
            b = self.pop()
            a = self.pop()
            self.push(a / b)

        elif instr in ['I_INC']:
            a = self.pop()
            self.push(a + 1)

        elif instr in ['I_DEC']:
            a = self.pop()
            self.push(a - 1)
        
        elif instr in ['I_INT_LESS', 'I_FLOAT_LESS']:
            b = self.pop()
            a = self.pop()
            self.push(1 if a < b else 0)

        elif instr in ['I_INT_LESS_E', 'I_FLOAT_LESS_E']:
            b = self.pop()
            a = self.pop()
            self.push(1 if a <= b else 0)

        elif instr in ['I_INT_GREATER', 'I_FLOAT_GREATER']:
            b = self.pop()
            a = self.pop()
            self.push(1 if a > b else 0)

        elif instr in ['I_INT_GREATER_E', 'I_FLOAT_GREATER_E']:
            b = self.pop()
            a = self.pop()
            self.push(1 if a >= b else 0)

        elif instr == 'I_EQ':
            b = self.pop()
            a = self.pop()
            self.push(1 if a == b else 0)

        elif instr == 'I_NOT_EQ':
            b = self.pop()
            a = self.pop()
            self.push(1 if a != b else 0)

        elif instr == 'I_OR':
            a = self.pop()
            b = self.pop()
            self.push(1 if a or b else 0)

        elif instr == 'I_AND':
            a = self.pop()
            b = self.pop()
            self.push(1 if a and b else 0)

        elif instr == 'I_GET_L':
            i = self.readImm()
            self.push(self.memory[self.fp + i])

        elif instr == 'I_SET_L':
            i = self.readImm()
            self.memory[self.fp + i] = self.pop()

        elif instr == 'I_POP':
            self.sp -= 1

        elif instr == 'I_INT_PUSH': 
            self.push(self.readImm())

        elif instr == 'I_FLOAT_PUSH': 
            self.push(gv.int2Float(self.readImm()))

        elif instr == 'I_STRING_PUSH': 
            self.push(gv.int2Str(self.readImm()))

        elif instr == 'I_BOOLEAN_PUSH': 
            self.push(self.readImm())

        elif instr == 'I_ALLOC': 
            self.sp += self.readImm()

        elif instr == 'I_BR': 
            i = self.readImm()
            self.ip = i

        elif instr == 'I_BZ':
            i = self.readImm()
            if self.pop() == 0:
                self.ip = i 
            
        elif instr == 'I_RET':
            self.execRet(0)

        elif instr == 'I_RET_V':
            self.execRet(self.pop())

        elif instr == 'I_CALL_BEGIN':
            self.push(0)
            self.push(0)
            self.push(0)
        
        elif instr == 'I_CALL':
            self.execCall(self.readImm(), self.readImm())

        elif instr == 'I_EXIT':
            self.running = False

        else:
            print(f'invalid instruction opcode {opcode}')
            exit(1)

    def pop(self):
        self.sp -= 1
        return self.memory[self.sp]

    def push(self, value):
        self.memory[self.sp] = value
        self.sp += 1

    def readImm(self):
        value = self.memory[self.ip]
        self.ip += 1
        return value
