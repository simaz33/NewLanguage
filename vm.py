STACK_LOCATION = 1024

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

        if opcode == 0x10:
            b = self.pop()
            a = self.pop()
            self.push(a + b)

        elif opcode == 0x11:
            b = self.pop()
            a = self.pop()
            self.push(a - b)

        elif opcode == 0x12:
            b = self.pop()
            a = self.pop()
            self.push(a * b)

        elif opcode == 0x13:
            b = self.pop()
            a = self.pop()
            self.push(a / b)
        
        elif opcode == 0x20:
            b = self.pop()
            a = self.pop()
            self.push(1 if a < b else 0)

        elif opcode == 0x21:
            b = self.pop()
            a = self.pop()
            self.push(1 if a <= b else 0)

        elif opcode == 0x22:
            b = self.pop()
            a = self.pop()
            self.push(1 if a > b else 0)

        elif opcode == 0x23:
            b = self.pop()
            a = self.pop()
            self.push(1 if a >= b else 0)

        elif opcode == 0x28:
            b = self.pop()
            a = self.pop()
            self.push(1 if a == b else 0)

        elif opcode == 0x29:
            b = self.pop()
            a = self.pop()
            self.push(1 if a != b else 0)

        elif opcode == 0x30:
            i = self.readImm()
            self.push(self.memory[self.fp + i])

        elif opcode == 0x31:
            i = self.readImm()
            self.memory[self.fp + i] = self.pop()

        elif opcode == 0x32:
            self.sp -= 1

        elif opcode == 0x33: #I_INT_PUSH
            self.push(self.readImm())

        elif opcode == 0x34: #I_FLOAT_PUSH
            self.push(self.readImm())

        elif opcode == 0x35: #I_BOOLEAN_PUSH
            self.push(self.readImm())

        elif opcode == 0x36: #I_ALLOC
            self.sp += self.readImm()

        elif opcode == 0x40: #I_BR
            i = self.readImm()
            self.ip = i

        elif opcode == 0x41: #I_BZ
            i = self.readImm()
            if self.pop() == 0:
                self.ip = i 
            
        elif opcode == 0x42:
            self.execRet(0)

        elif opcode == 0x43:
            self.execRet(self.pop())

        elif opcode == 0x44:
            self.push(0)
            self.push(0)
            self.push(0)
        
        elif opcode == 0x45:
            self.execCall(self.readImm(), self.readImm())

        elif opcode == 0x46:
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
