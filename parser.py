from ast import (Node, Param, Program, StmtBlock, Decl,
    DeclFn, StmtVarDecl, Expr, ExprBinary, ExprNot, ExprFnCall,  
    ExprLit, ExprVar, ExprPostfix, Stmt, StmtIf, StmtElseIf, 
    StmtElse, StmtFor, StmtWhile, StmtInput, StmtOutput, StmtBreak, 
    StmtContinue, StmtReturn, Type, TypePrim)


class Parser():
    def __init__(self, tokens, filename):
        self.tokens = tokens
        self.filename = filename
        self.offset = 0
        self.types = {
            'INT_KW' : 'int',
            'FLOAT_KW' : 'float',
            'STRING_KW' : 'string',
            'BOOLEAN_KW' : 'boolean'
        }

    def accept(self, tokenType):
        currentToken = self.tokens[self.offset]

        if currentToken.type == tokenType:
            self.offset += 1
            return currentToken

    def expect(self, tokenType):
        currentToken = self.tokens[self.offset]

        if currentToken.type == tokenType:
            self.offset += 1
            return currentToken

        else:
            self.error('Expected {}, got {}'.format(tokenType, currentToken.type))

    def error(self, msg):
        print('Error:{}:{}:{}'.format(self.filename, self.tokens[self.offset].lineNr, msg))
        exit(1)
    
    def parseDecl(self):
        return self.parseDeclFn()

    def parseProgram(self):
        decls = []

        while not self.accept('EOF'):
            decls.append(self.parseDecl())

        return Program(decls)

    def parseDeclFn(self):
        declType = self.parseType()
        name = self.expect('IDENT')
        self.expect('PAREN_OPEN')
        params = self.parseParams() 
        self.expect('PAREN_CLOSE') 
        body = self.parseStmtBlock()  

        return DeclFn(declType, name, params, body)

    def parseExprs(self):
        exprs = []

        exprs.append(self.parseExpr())

        while self.accept('COMMA'):
            exprs.append(self.parseExpr())

        return exprs
    
    def parseExpr(self):
        return self.parseExprAssign()

    def parseExprAssign(self):
        result = self.parseExprOr()

        while True:
            if self.accept('ASSIGN_OP'):
                result = ExprBinary('ASSIGN', result, self.parseExprOr())

            else:
                break
        
        return result

    def parseExprOr(self):
        result = self.parseExprAnd()

        while True:
            if self.accept('OR_OP'):
                result = ExprBinary('OR', result, self.parseExprAnd())

            else:
                break

        return result

    def parseExprAnd(self):
        result = self.parseExprEqual()

        while True:
            if self.accept('AND_OP'):
                result = ExprBinary('AND', result, self.parseExprEqual())

            else:
                break

        return result

    def parseExprEqual(self):
        result = self.parseExprComp()

        while True:
            if self.accept('EQ_OP'):
                result = ExprBinary('EQUAL', result, self.parseExprComp())

            else:
                break

        return result

    def parseExprComp(self):
        result = self.parseExprAdd()

        while True:
            if self.accept('COMP_L'):
                result = ExprBinary('COMPARE_LESS', result, self.parseExprAdd())
            
            elif self.accept('COMP_LE'):
                result = ExprBinary('COMPARE_LESS_EQUAL', result, self.parseExprAdd())

            elif self.accept('COMP_G'):
                result = ExprBinary('COMPARE_GREATER', result, self.parseExprAdd())

            elif self.accept('COMP_GE'):
                result = ExprBinary('COMPARE_GREATER_EQUAL', result, self.parseExprAdd())
            
            else:
                break

        return result

    def parseExprAdd(self):
        result = self.parseExprMult()

        while True:
            if self.accept('ADD_OP'):
                result = ExprBinary('ADD', result, self.parseExprMult())

            elif self.accept('MINUS_OP'):
                result = ExprBinary('SUB', result, self.parseExprMult())

            else:
                break

        return result

    def parseExprMult(self):
        result = self.parseExprUnary()

        while True:
            if self.accept('MULT_OP'):
                result = ExprBinary('MULT', result, self.parseExprUnary())

            elif self.accept('DIV_OP'):
                result = ExprBinary('DIV', result, self.parseExprUnary())

            else:
                break

        return result

    def parseExprUnary(self):
        result = self.parseExprPrimary()

        while True:
            if self.accept('NOT_OP'):
                result = ExprNot('NOT', self.parseExprPrimary())

            else:
                break

        return result

    def parseExprPrimary(self):
        if self.tokenType() == 'IDENT':
            return self.parseExprVar()

        elif self.tokenType() == 'INT':
            return self.parseExprInt()
        
        elif self.tokenType() == 'FLOAT':
            return self.parseExprFloat()

        elif self.tokenType() == 'STR':
            return self.parseExprStr()

        elif self.tokenType() == 'TRUE_KW':
            return self.parseExprTrue()

        elif self.tokenType() == 'FALSE_KW':
            return self.parseExprFalse()

        elif self.tokenType() == 'PAREN_OPEN':
            return self.parseExprParen()

        else:
            return None
            #self.error('Invalid expression')

    def parseExprParen(self):
        self.expect('PAREN_OPEN')
        result = self.parseExpr()
        self.expect('PAREN_CLOSE')
        
        return result

    def parseExprFalse(self):
        lit = self.expect('FALSE_KW')

        return ExprLit(lit)

    def parseExprTrue(self):
        lit = self.expect('TRUE_KW')

        return ExprLit(lit)

    def parseExprStr(self):
        lit = self.expect('STR')

        return ExprLit('STR', lit)

    def parseExprFloat(self):
        lit = self.expect('FLOAT')
        
        return ExprLit('FLOAT', lit)

    def parseExprInt(self):
        lit = self.expect('INT')

        return ExprLit('INT', lit)

    def parseExprVar(self):
        name = self.expect('IDENT')

        if self.tokenType() == 'PAREN_OPEN':
            return self.parseExprFnCall(name)

        if self.tokenType() == 'INC':
            postfixType = self.expect('INC')
            return ExprPostfix(postfixType, name)

        if self.tokenType() == 'DEC':
            postfixType = self.expect('DEC')
            return ExprPostfix(postfixType, name)
        
        return ExprVar(name)

    def parseExprFnCall(self, name):
        args = []
        self.expect('PAREN_OPEN')
        args = self.parseExprs()
        self.expect('PAREN_CLOSE')

        return ExprFnCall(name, args)

    def parseParam(self):
        paramType = self.parseType()
        name = self.expect('IDENT')
        
        return Param(paramType, name)

    def parseParams(self):
        params = []
        
        if self.tokenType() == 'PAREN_CLOSE':
            return params
        
        params.append(self.parseParam())

        while self.accept('COMMA'):
            params.append(self.parseParam())

        return params

    def parseStmt(self):
        if self.tokenType() == 'RET_KW':
            return self.parseStmtReturn()

        elif self.tokenType() == 'IF_KW':
            return self.parseStmtIf()

        elif self.tokenType() == 'FOR_KW':
            return self.parseStmtFor()

        elif self.tokenType() == 'WHILE_KW':
            return self.parseStmtWhile()

        elif self.tokenType() == 'INPUT_KW':
            return self.parseStmtInput()

        elif self.tokenType() == 'OUTPUT_KW':
            return self.parseStmtOutput()

        elif self.tokenType() == 'BREAK_KW':
            return self.parseStmtBreak()

        elif self.tokenType() == 'CONTINUE_KW':
            return self.parseStmtContinue()

        elif self.tokenType() == 'INT_KW':
            return self.parseStmtVarDecl()

        elif self.tokenType() == 'FLOAT_KW':
            return self.parseStmtVarDecl()

        elif self.tokenType() == 'STRING_KW':
            return self.parseStmtVarDecl()

        elif self.tokenType() == 'BOOLEAN_KW':
            return self.parseStmtVarDecl()

        else:
            return self.parseExpr()

    def parseStmtBlock(self):
        stmts = []

        self.expect('CURL_PAREN_OPEN')

        while not self.tokenType() == 'CURL_PAREN_CLOSE':
            stmt = self.parseStmt()

            if stmt:
                stmts.append(stmt)

            else:
                break

        self.expect('CURL_PAREN_CLOSE')

        return StmtBlock(stmts)

    def parseStmtVarDecl(self):
        vars = []
        declType = self.parseType()
        name = self.expect('IDENT')
        value = None

        if self.accept('ASSIGN_OP'):
            value = self.parseExpr()

        vars.append(StmtVarDecl(declType, name, value))

        while self.accept('COMMA'):
            vars.append(self.parseVars(declType))

        return vars

    def parseVars(self, declType):
        name = self.expect('IDENT')

        if self.accept('ASSIGN_OP'):
            value = self.parseExpr()

        return StmtVarDecl(declType, name, value)

    def parseStmtBreak(self):
        breakKw = self.expect('BREAK_KW')

        return StmtBreak(breakKw)

    def parseStmtContinue(self):
        continueKw = self.expect('CONTINUE_KW')

        return StmtBreak(continueKw)

    def parseStmtOutput(self):
        outputKw = self.expect('OUTPUT_KW')
        self.expect('PAREN_OPEN')
        result = self.parseExprs()
        self.expect('PAREN_CLOSE')

        return StmtOutput(outputKw, result)

    def parseStmtInput(self):
        inputKw = self.expect('INPUT_KW')
        self.expect('PAREN_OPEN')
        args = self.parseArgs()
        self.expect('PAREN_CLOSE')

        return StmtInput(inputKw, args)

    def parseStmtWhile(self):
        self.expect('WHILE_KW')
        cond = self.parseExpr()
        body = self.parseStmtBlock()

        return StmtWhile(cond, body)

    def parseStmtFor(self):
        self.expect('FOR_KW')
        self.expect('PAREN_OPEN')
        decl = self.parseStmt()
        self.expect('SEMICOLON')
        cond = self.parseExpr()
        self.expect('SEMICOLON')
        final = self.parseExpr()
        self.expect('PAREN_CLOSE')
    
        body = self.parseStmtBlock()
    
        return StmtFor(decl, cond, final, body)

    def parseStmtIf(self):
        self.expect('IF_KW')
        cond = self.parseExpr()
        body = self.parseStmtBlock()
        elseIfStmts = None
        elseStmt = None

        while self.accept('ELSEIF_KW'):
            elseIfStmts = []
            elseIfStmts.append(self.parseStmtElseIf())

        if self.accept('ELSE_KW'):
            elseStmt = self.parseStmtElse()

        return StmtIf(cond, body, elseIfStmts, elseStmt)

    def parseStmtElseIf(self):
        self.expect('ELSEIF_KW')
        cond = self.parseExpr()
        body = self.parseStmtBlock()

        return StmtElseIf(cond, body)

    def parseStmtElse(self):
        self.expect('ELSE_KW')
        body = self.parseStmtBlock()
        
        return StmtElse(body)

    def parseStmtReturn(self):
        retKw = self.expect('RET_KW')
        value = self.parseExpr()
        
        return StmtReturn(retKw, value)

    def parseType(self):
        if self.tokenType() == 'INT_KW':
            self.expect('INT_KW')
            return TypePrim('INT')

        elif self.tokenType() == 'FLOAT_KW': 
            self.expect('FLOAT_KW')
            return TypePrim('FLOAT')

        elif self.tokenType() == 'STRING_KW':
            self.expect('STRING_KW')
            return TypePrim('STRING')
        
        elif self.tokenType() == 'BOOLEAN_KW': 
            self.expect('BOOLEAN_KW')
            return TypePrim('BOOLEAN')

        elif self.tokenType() == 'VOID_KW': 
            self.expect('VOID_KW')
            return TypePrim('VOID')

        else:
            self.error('Invalid type declaration type: {}'.format(self.tokenType()))

    def tokenType(self):
        return self.tokens[self.offset].type