import ast

class Parser():
    def __init__(self, tokens, filename):
        self.tokens = tokens
        self.filename = filename
        self.offset = 0

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

        return ast.Program(decls)

    def parseDeclFn(self):
        declType = self.parseType()
        name = self.expect('IDENT')
        self.expect('PAREN_OPEN')
        params = self.parseParams() 
        self.expect('PAREN_CLOSE') 
        body = self.parseStmtBlock()  

        return ast.DeclFn(declType, name, params, body)

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
                result = ast.ExprBinary('ASSIGN', result, self.parseExprOr())

            else:
                break
        
        return result

    def parseExprOr(self):
        result = self.parseExprAnd()

        while True:
            if self.accept('OR_OP'):
                result = ast.ExprBinLogic('OR', result, self.parseExprAnd())

            else:
                break

        return result

    def parseExprAnd(self):
        result = self.parseExprEqual()

        while True:
            if self.accept('AND_OP'):
                result = ast.ExprBinLogic('AND', result, self.parseExprEqual())

            else:
                break

        return result

    def parseExprEqual(self):
        result = self.parseExprComp()

        while True:
            if self.accept('EQ_OP'):
                result = ast.ExprBinEquality('EQUAL', result, self.parseExprComp())

            else:
                break

        return result

    def parseExprComp(self):
        result = self.parseExprAdd()

        while True:
            if self.accept('COMP_L'):
                result = ast.ExprBinComparison('CMP_L', result, self.parseExprAdd())
            
            elif self.accept('COMP_LE'):
                result = ast.ExprBinComparison('CMP_LE', result, self.parseExprAdd())

            elif self.accept('COMP_G'):
                result = ast.ExprBinComparison('CMP_G', result, self.parseExprAdd())

            elif self.accept('COMP_GE'):
                result = ast.ExprBinComparison('CMP_GE', result, self.parseExprAdd())
            
            else:
                break

        return result

    def parseExprAdd(self):
        result = self.parseExprMult()

        while True:
            if self.accept('ADD_OP'):
                result = ast.ExprBinArith('ADD', result, self.parseExprMult())

            elif self.accept('MINUS_OP'):
                result = ast.ExprBinArith('SUB', result, self.parseExprMult())

            else:
                break

        return result

    def parseExprMult(self):
        result = self.parseExprUnary()

        while True:
            if self.accept('MULT_OP'):
                result = ast.ExprBinArith('MULT', result, self.parseExprUnary())

            elif self.accept('DIV_OP'):
                result = ast.ExprBinArith('DIV', result, self.parseExprUnary())

            else:
                break

        return result

    def parseExprUnary(self):
        result = self.parseExprPrimary()

        while True:
            if self.accept('NOT_OP'):
                result = ast.ExprUnary('NOT', self.parseExprPrimary())

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

        return ast.ExprLit('BOOLEAN', lit)

    def parseExprTrue(self):
        lit = self.expect('TRUE_KW')

        return ast.ExprLit('BOOLEAN', lit)

    def parseExprStr(self):
        lit = self.expect('STR')

        return ast.ExprLit('STR', lit)

    def parseExprFloat(self):
        lit = self.expect('FLOAT')
        
        return ast.ExprLit('FLOAT', lit)

    def parseExprInt(self):
        lit = self.expect('INT')

        return ast.ExprLit('INT', lit)

    def parseExprVar(self):
        name = self.expect('IDENT')

        if self.tokenType() == 'PAREN_OPEN':
            return self.parseExprFnCall(name)

        if self.tokenType() == 'INC':
            self.expect('INC')
            return ast.ExprUnary('INC', ast.ExprVar(name))
            #return ast.ExprUnary('INC', ast.ExprVar(name))

        if self.tokenType() == 'DEC':
            self.expect('DEC')
            return ast.ExprUnary('DEC', ast.ExprVar(name))
            #return ast.ExprUnary('DEC', name)
        
        return ast.ExprVar(name)

    def parseExprFnCall(self, name):
        args = []
        self.expect('PAREN_OPEN')
        args = self.parseExprs()
        self.expect('PAREN_CLOSE')

        return ast.ExprFnCall(name, args)

    def parseParam(self):
        paramType = self.parseType()
        name = self.expect('IDENT')
        
        return ast.Param(paramType, name)

    def parseParams(self):
        params = []
        
        if self.tokenType() == 'PAREN_CLOSE':
            return params
        
        params.append(self.parseParam())

        while self.accept('COMMA'):
            params.append(self.parseParam())

        return params

    def parseStmt(self):
        if self.testTokens('IDENT', 'ASSIGN_OP'):
            return self.parseStmtAssign()

        elif self.tokenType() == 'RET_KW':
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
            return self.parseStmtExpr()
            

    def parseStmtBlock(self):
        stmts = []

        self.expect('CURL_PAREN_OPEN')

        while not self.tokenType() == 'CURL_PAREN_CLOSE':
            stmt = self.parseStmt()
            
            if stmt:
                if isinstance(stmt, list):
                    [stmts.append(s) for s in stmt]
                else:
                    stmts.append(stmt)

            else:
                break

        self.expect('CURL_PAREN_CLOSE')

        return ast.StmtBlock(stmts)

    def parseStmtExpr(self):
        expr = self.parseExpr()
        
        return ast.StmtExpr(expr)

    def parseStmtVarDecl(self):
        variables = []
        declType = self.parseType()
        name = self.expect('IDENT')
        value = None

        if self.accept('ASSIGN_OP'):
            value = self.parseExpr()

        variables.append(ast.StmtVarDecl(declType, name, value))

        while self.accept('COMMA'):
            variables.append(self.parseVars(declType))

        return variables

    def parseVars(self, declType):
        name = self.expect('IDENT')
        value = None

        if self.accept('ASSIGN_OP'):
            value = self.parseExpr()

        return ast.StmtVarDecl(declType, name, value)

    def parseStmtBreak(self):
        breakKw = self.expect('BREAK_KW')

        return ast.StmtBreak(breakKw)

    def parseStmtContinue(self):
        continueKw = self.expect('CONTINUE_KW')

        return ast.StmtContinue(continueKw)

    def parseStmtOutput(self):
        outputKw = self.expect('OUTPUT_KW')
        self.expect('PAREN_OPEN')
        results = self.parseExprs()
        self.expect('PAREN_CLOSE')

        return ast.StmtOutput(outputKw, results)

    def parseStmtInput(self):
        inputKw = self.expect('INPUT_KW')
        self.expect('PAREN_OPEN')
        args = self.parseArgs()
        self.expect('PAREN_CLOSE')

        return ast.StmtInput(inputKw, args)

    def parseStmtWhile(self):
        self.expect('WHILE_KW')
        cond = self.parseExpr()
        body = self.parseStmtBlock()

        return ast.StmtWhile(cond, body)

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
    
        return ast.StmtFor(decl, cond, final, body)

    def parseStmtIf(self):
        branches = []
        self.expect('IF_KW')
        cond = self.parseExpr()
        body = self.parseStmtBlock()
        branches.append(ast.StmtBranch(cond, body))
        elseStmt = None

        while self.accept('ELSEIF_KW'):
            branches.append(self.parseStmtElseIf())

        if self.accept('ELSE_KW'):
            elseStmt = self.parseStmtElse()

        return ast.StmtIf(branches, elseStmt)

    def parseStmtElseIf(self):
        cond = self.parseExpr()
        body = self.parseStmtBlock()

        return ast.StmtBranch(cond, body)

    def parseStmtElse(self):
       return self.parseStmtBlock()

    def parseStmtReturn(self):
        retKw = self.expect('RET_KW')
        value = self.parseExpr()
        
        return ast.StmtReturn(retKw, value)

    def parseStmtAssign(self):
        target = self.expect('IDENT')
        self.expect('ASSIGN_OP')
        value = self.parseExpr()
        
        return ast.StmtAssign(target, value)

    def parseType(self):
        if self.tokenType() == 'INT_KW':
            return ast.TypePrim(self.expect('INT_KW'), 'int')

        elif self.tokenType() == 'FLOAT_KW': 
            return ast.TypePrim(self.expect('FLOAT_KW'), 'float')

        elif self.tokenType() == 'STRING_KW':
            return ast.TypePrim(self.expect('STRING_KW'), 'string')
        
        elif self.tokenType() == 'BOOLEAN_KW': 
            return ast.TypePrim(self.expect('BOOLEAN_KW'), 'boolean')

        elif self.tokenType() == 'VOID_KW': 
            return ast.TypePrim(self.expect('VOID_KW'), 'void')

        else:
            self.error('Invalid type declaration type: {}'.format(self.tokenType()))

    def testTokens(self, tokenType1, tokenType2):
        ok1 = self.tokens[self.offset + 0].type == tokenType1
        ok2 = self.tokens[self.offset + 1].type == tokenType2

        return ok1 and ok2

    def tokenType(self):
        return self.tokens[self.offset].type