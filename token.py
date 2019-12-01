class Token():
    def __init__(self, type, value, lineNr):
        self.type       = type
        self.lineNr     = lineNr
        self.setValue(value)

    def setValue(self, _value):
        if self.type == 'INT':
            self.value = int(_value)

        elif self.type == 'INT_HEX': 
            self.value = int(_value, 16)
            self.type = 'INT'

        elif self.type == 'INT_BIN':
            self.value = int(_value, 2)
            self.type = 'INT'

        elif self.type == 'FLOAT':
            self.value = float(_value)

        else:
            self.value = _value
    