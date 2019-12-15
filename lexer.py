from token import Token


keywords = {
    'return'    :   'RET_KW',
    'true'      :   'TRUE_KW',
    'false'     :   'FALSE_KW',
    'if'        :   'IF_KW',
    'elseif'    :   'ELSEIF_KW',
    'else'      :   'ELSE_KW',
    'for'       :   'FOR_KW',
    'while'     :   'WHILE_KW',
    'int'       :   'INT_KW',
    'float'     :   'FLOAT_KW',
    'string'    :   'STRING_KW',
    'boolean'   :   'BOOLEAN_KW',
    'void'      :   'VOID_KW',
    'input'     :   'INPUT_KW',
    'output'    :   'OUTPUT_KW',
    'break'     :   'BREAK_KW',
    'continue'  :   'CONTINUE_KW'
}

class Lexer():
    def __init__(self, filename, input):
        self.filename           = filename
        self.input              = input
        self.buffer             = ''
        self.floatEBuffer       = ''
        self.offset             = 0
        self.currentChar        = ''
        self.lineNr             = 1
        self.columnNr           = 1
        self.state              = 'START'
        self.tokens             = list()
        self.tokenStart         = 0
        self.running            = True
        self.error              = ''
        self.switch             = {
            'START'             :   self.lexStart,
            'COMM_SL'           :   self.lexCommentSl,
            'COMM_MULT'         :   self.lexCommentMult,
            'COMM_MULT_END'     :   self.lexCommentMultEnd,
            'IDENT'             :   self.lexIdent,
            'PREFIX'            :   self.lexPrefix,
            'INT'               :   self.lexInt,
            'INT_HEX'           :   self.lexIntHex,
            'INT_BIN'           :   self.lexIntBin,
            'FLOAT'             :   self.lexFloat,
            'FLOAT_E'           :   self.lexFloatE,
            'STR'               :   self.lexStr,
            'STR_ESCAPE'        :   self.lexStrEscape,
            'COMP_L'            :   self.lexCompL,
            'COMP_G'            :   self.lexCompG,
            'ASSIGN_OP'         :   self.lexAssignOp,
            'ADD_OP'            :   self.lexAddOp,
            'MINUS_OP'          :   self.lexMinusOp,
            'MULT_OP'           :   self.lexMultOp,
            'DIV_OP'            :   self.lexDivOp,
            'OR_OP'             :   self.lexOrOp,
            'AND_OP'            :   self.lexAndOp,
            'NOT_OP'            :   self.lexNotOp,
            'PAREN_OPEN'        :   self.lexParenOpen,
            'PAREN_CLOSE'       :   self.lexParenClose,
            'CURL_PAREN_OPEN'   :   self.lexCurlParenOpen,
            'CURL_PAREN_CLOSE'  :   self.lexCurlParenClose,
            'COMMA'             :   self.lexComma,
            'SEMICOLON'         :   self.lexSemicolon
        }

    def lexAll(self):
        while self.running and self.offset < len(self.input):
            self.currentChar = self.input[self.offset]
            self.lexChar()
            self.offset += 1
            self.columnNr += 1
        
        self.currentChar = ' '
        self.lexChar()

        
        if self.state is 'START' or self.state is 'COMM_SL':
            self.completeToken('EOF')
        
        elif self.state is 'STR':
            self.setError('unterminated string')

        else:
            self.setError("unterminated token: {}".format(self.state))

    def lexChar(self):
        try:
            self.switch[self.state]()
        except KeyError as e:
            self.setError('unknown state "{}"'.format(self.state))
            
    def lexStart(self):
        if self.currentChar.islower():
            self.add()
            self.beginToken('IDENT')
            
        elif self.currentChar.isupper():
            self.add()
            self.beginToken('IDENT')

        elif self.currentChar == '0':
            self.add()
            self.beginToken('PREFIX')

        elif self.currentChar.isdigit():
            self.add()
            self.beginToken('INT')

        elif self.currentChar is '"':
            self.beginToken('STR')

        elif self.currentChar is '#':
            self.beginToken('COMM_SL')

        elif self.currentChar is ' ':
            pass

        elif self.currentChar is '\n':
            self.lineNr += 1
            self.columnNr = 1
        
        elif self.currentChar is '+':
            self.beginToken('ADD_OP')
        
        elif self.currentChar is '-':
            self.beginToken('MINUS_OP')

        elif self.currentChar is '*':
            self.beginToken('MULT_OP')

        elif self.currentChar is '/':
            self.beginToken('DIV_OP')

        elif self.currentChar is '<':
            self.beginToken('COMP_L')

        elif self.currentChar is '>':
            self.beginToken('COMP_G')

        elif self.currentChar is '=':
            self.beginToken('ASSIGN_OP')

        elif self.currentChar is '|':
            self.beginToken('OR_OP')

        elif self.currentChar is '&':
            self.beginToken('AND_OP')

        elif self.currentChar is '!':
            self.beginToken('NOT_OP')

        elif self.currentChar is '(':
            self.beginToken('PAREN_OPEN')
        
        elif self.currentChar is ')':
            self.beginToken('PAREN_CLOSE')

        elif self.currentChar is '{':
            self.beginToken('CURL_PAREN_OPEN')

        elif self.currentChar is '}':
            self.beginToken('CURL_PAREN_CLOSE')

        elif self.currentChar is ',':
            self.beginToken('COMMA')

        elif self.currentChar is ';':
            self.beginToken('SEMICOLON')

        elif self.currentChar is '.':
            self.add()
            self.beginToken('FLOAT')
        
        else:
            self.setError('invalid character found')
    
    def lexCommentSl(self):
        if self.currentChar is '\n':
            self.lineNr += 1
            self.columnNr = 1
            self.state = 'START'

    def lexCommentMult(self):
        if self.currentChar is '\n':
            self.lineNr += 1
            self.columnNr = 1

        elif self.currentChar is '#':
            self.state = 'COMM_MULT_END'

        else:
            pass

    def lexCommentMultEnd(self):
        if self.currentChar is '/':
            self.state = 'START'

        else:
            self.offset -= 1
            self.state = 'COMM_MULT'

    def lexIdent(self):
        if (self.currentChar.islower() or
           self.currentChar.isupper() or
           self.currentChar.isdigit() or
           self.currentChar == '_'):
            self.add()
        else:
            self.completeIdent()
    
    def lexPrefix(self):
        if self.currentChar == 'x':
            self.state = 'INT_HEX'
            self.add()

        elif self.currentChar == 'b':
            self.state = 'INT_BIN'
            self.add()

        elif (self.currentChar.islower() or
            self.currentChar.isupper()   or
            self.currentChar == '_'):
            self.setError('invalid character found in prefix')

        elif self.currentChar == '.':
            self.state = 'FLOAT'
            self.add()

        elif self.currentChar.isdigit():
            self.state = 'INT'
            self.add()

        else:
            self.completeToken('INT', False)
    
    def lexInt(self):
        if self.currentChar.isdigit():
            self.add()
        
        elif self.currentChar is '.':
            self.state = 'FLOAT'
            self.add()

        elif self.currentChar is 'e':
            self.state = 'FLOAT_E'
            self.add()

        elif (self.currentChar.islower() or
            self.currentChar.isupper()   or 
            self.currentChar is '_'):
            self.setError('invalid character found in integer')

        else:
            self.completeToken('INT', False)

    def lexIntHex(self):
        if self.currentChar.isdigit():
            self.add()

        elif ord(self.currentChar) in range(ord('A'), ord('G')):
            self.add()

        elif ord(self.currentChar) in range(ord('a'), ord('g')):
            self.add()

        elif (self.currentChar.islower() or 
            self.currentChar.isupper()   or
            self.currentChar is '_'):
            self.setError('invalid hexadecimal character found')

        else:
            self.completeToken('INT_HEX', False)

    def lexIntBin(self):
        if self.currentChar == '0' or self.currentChar == '1':
            self.add()

        elif (self.currentChar.isdigit() or
            self.currentChar.islower()   or
            self.currentChar.isupper()   or
            self.currentChar is '_'):
            self.setError('invalid binary character found')

        else:
            self.completeToken('INT_BIN', False)
    
    def lexFloat(self):
        if self.currentChar.isdigit():
            self.add()

        elif self.currentChar is 'e':
            self.state = 'FLOAT_E'
            self.add()
        
        elif (self.currentChar.islower() or
            self.currentChar.isupper()   or 
            self.currentChar is '_'):
            self.setError('invaid float suffix')

        else:
            self.completeToken('FLOAT', False)

    def lexFloatE(self):
        if self.floatEBuffer:
            if self.currentChar.isdigit():
                self.addFloatEBuffer()

            elif (self.currentChar.islower() or
                self.currentChar.isupper()   or 
                self.currentChar is '_'):
                self.setError('invalid float suffix')

            else:
                self.buffer += self.floatEBuffer
                self.floatEBuffer = ''
                self.completeToken('FLOAT', False)

        else:
            if (self.currentChar.isdigit() or
                self.currentChar is '-'):
                self.addFloatEBuffer()
            
            else:
                self.setError('invalid float suffix')

    def lexStr(self):
        if self.currentChar is '"':
            self.completeToken('STR')

        elif self.currentChar is "\n":
            self.setError('ctring contains newline')    

        elif self.currentChar is '\\':
            self.state = 'STR_ESCAPE'

        else:
            self.add()

    def lexStrEscape(self):
        if self.currentChar is '\"':
            self.buffer += "\""

        elif self.currentChar is 't':
            self.buffer += "\t"

        elif self.currentChar is 'n':
            self.buffer += "\n"

        elif self.currentChar is '0':
            self.buffer += "\0"

        else:
            self.setError("invalid escape sequence '\\'{}".format(self.currentChar))

        self.state = 'STR'

    def lexCompL(self):
        if self.currentChar is '=':
            self.completeToken('COMP_LE')
        else:
            self.completeToken('COMP_L', False)

    def lexCompG(self):
        if self.currentChar is '=':
            self.completeToken('COMP_GE')
        else:
            self.completeToken('COMP_G', False)
    
    def lexAssignOp(self):
        if self.currentChar is '=':
            self.completeToken('EQ_OP')
        else:
            self.completeToken('ASSIGN_OP', False)

    def lexAddOp(self):
        if self.currentChar is '+':
            self.completeToken('INC')
        else:
            self.completeToken('ADD_OP', False)

    def lexMinusOp(self):
        if self.currentChar is '-':
            self.completeToken('DEC')
        else:
            self.completeToken('MINUS_OP', False)

    def lexMultOp(self):
        self.completeToken('MULT_OP', False)

    def lexDivOp(self):
        if self.currentChar is '#':
            self.state = 'COMM_MULT'

        else:
            self.completeToken('DIV_OP', False)

    def lexOrOp(self):
        if self.currentChar is '|':
            self.add()
            self.completeToken('OR_OP')

        else:
            self.setError('unknown operator')

    def lexAndOp(self):
        if self.currentChar is '&':
            self.add()
            self.completeToken('AND_OP')

        else:
            self.setError('unknown operator')

    def lexNotOp(self):
        if self.currentChar is '=':
            self.completeToken('NOT_EQ_OP')
        else:
            self.completeToken('NOT_OP', False)

    def lexParenOpen(self):
        self.completeToken('PAREN_OPEN', False)

    def lexParenClose(self):
        self.completeToken('PAREN_CLOSE', False)

    def lexCurlParenOpen(self):
        self.completeToken('CURL_PAREN_OPEN', False)

    def lexCurlParenClose(self):
        self.completeToken('CURL_PAREN_CLOSE', False)

    def lexComma(self):
        self.completeToken('COMMA', False)

    def lexSemicolon(self):
        self.completeToken('SEMICOLON', False)

    def add(self):
        self.buffer += self.currentChar

    def addFloatEBuffer(self):
        self.floatEBuffer += self.currentChar

    def beginToken(self, newState):
        self.tokenStart = self.lineNr
        self.state = newState

    def completeToken(self, tokenType, advance = True):
        self.tokens.append(Token(tokenType, self.buffer, self.tokenStart))
        self.buffer = ''
        self.state = 'START'

        if not advance:
            self.offset -= 1
    
    def completeIdent(self):
        if self.buffer in keywords:
            keyword = self.buffer
            self.buffer = ''
            self.completeToken(keywords[keyword], False) 
        else:
            self.completeToken('IDENT', False) 

    def dumpTokens(self):
        print("{:<5} | {:<5} | {:<16} | {}".format('ID', 'LINE', 'TYPE', 'VALUE'))
        print('-' * 40)
        index = 0
        for token in self.tokens:
            print("{:<5} | {:<5} | {:<16} | {}".format(index, token.lineNr, token.type, token.value)) 
            index += 1

    def setError(self, msg):
        if (msg):
            self.error = 'Error{}:{}:{}'.format(self.filename, self.lineNr, msg)

        self.running = False      

    def displayError(self):
        if not self.running:
            print(self.error)
            exit(1)


