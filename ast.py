from scope import *
from checkTypes import *
from token import Token
import genCode as gc
import globalVars as gv

class Node():
    parent = None

    def __init__(self):
        pass
    
    def printNode(self, p):
        print('printNode() not implemented for', self.__name__)
        exit(1)

    def addChildren(self, *children):
        for child in children:
            if child is None:
                continue
            child.parent = self

    def findAncestor(self, ancestorClass):
        currNode = self.parent
        while currNode:
            if isinstance(currNode, ancestorClass):
                return currNode
            else:
                currNode = currNode.parent

    def resolveNames(self, scope):
        print(f'resolveNames() is not implemented for: {self}')

    def checkTypes(self):
        print(f'checkTypes() is not implemented for: {self}')
    
    def genCode(self):
        print(f'genCode() is not implemented for: {self}')
    
    def __str__(self):
        return self.__class__.__name__

class Param(Node):
    def __init__(self, type, name):
        self.addChildren(type)
        self.type = type
        self.name = name

    def printNode(self, p):
        p.print('name', self.name)
        p.print('type', self.type)

    def resolveNames(self, scope):
        self.stackSlot = gv.stackSlotIndex
        gv.stackSlotIndex += 1
        scope.add(self.name, self)

class Program(Node):
    def __init__(self, decls):
        self.addChildren(*decls)
        self.decls = decls
        self.mainLabel = None

    def printNode(self, p):
        p.print('decls', self.decls)

    def resolveNames(self, scope):
        [scope.add(decl.name, decl) for decl in self.decls]
        [decl.resolveNames(scope) for decl in self.decls]

        if not self.mainLabel:
            semanticError(None, 'Main function does not exist')

    def checkTypes(self):
        [decl.checkTypes() for decl in self.decls if decl]

    def genCode(self, w):
        w.write('I_CALL_BEGIN')
        w.write('I_CALL', self.mainLabel, 0)
        w.write('I_EXIT')
        [decl.genCode(w) for decl in self.decls]

class StmtBlock(Node):
    def __init__(self, stmts):
        self.addChildren(*stmts)
        self.stmts = stmts

    def printNode(self, p):
        p.print('stmts', self.stmts)

    def resolveNames(self, parentScope):
        scope = Scope(parentScope, gv.filename)
        for stmt in self.stmts:
            stmt.resolveNames(scope)

    def checkTypes(self):
        [stmt.checkTypes() for stmt in self.stmts if stmt]

    def genCode(self, w):
        [stmt.genCode(w) for stmt in self.stmts]

class Decl(Node):
    def __init__(self):
        super()

class DeclFn(Decl):
    def __init__(self, type, name, params, body):
        self.addChildren(*params, type, body)
        self.type = type
        self.name = name
        self.params = params
        self.body = body
        self.startLabel = gc.Label()

    def printNode(self, p):
        p.print('retType', self.type)
        p.print('name', self.name)
        p.print('params', self.params)
        p.print('body', self.body)

    def resolveNames(self, parentScope):
        if self.name.value == 'main':
            unifyTypes(TypePrim(Token('INT_KW', '', self.type.token.lineNr), 'int'), self.type)
            if len(self.params) == 0:
                program = self.findAncestor(Program)
                program.mainLabel = self.startLabel
            
        gv.stackSlotIndex = 0
        scope = Scope(parentScope, gv.filename)
        for param in self.params:
            param.resolveNames(scope)
        
        self.body.resolveNames(scope)
        self.numLocals = gv.stackSlotIndex

    def checkTypes(self):
        self.body.checkTypes()

    def genCode(self, w):
        w.placeLabel(self.startLabel)
        if self.numLocals > 0:
            w.write('I_ALLOC', self.numLocals)
        self.body.genCode(w)
        w.write('I_RET')

class Expr(Node): 
    pass

class ExprBinary(Expr):
    def __init__(self, op, left, right):
        self.addChildren(left, right)
        self.op = op
        self.left = left
        self.right = right

    def printNode(self, p):
        p.print('left', self.left)
        p.print('right', self.right)

    def resolveNames(self, scope):
        if None not in [self.left, self.right]:
            self.left.resolveNames(scope)
            self.right.resolveNames(scope)

    def genCode(self, w):
        self.left.genCode(w)
        self.right.genCode(w)
        op = self.op.type
        kind = self.left.checkTypes().kind.upper()

        if op == 'ADD_OP':
            w.write(f'I_{kind}_ADD')
        elif op == 'MINUS_OP':
            w.write(f'I_{kind}_SUB')
        elif op == 'MULT_OP':
            w.write(f'I_{kind}_MULT')
        elif op == 'DIV_OP':
            w.write(f'I_{kind}_DIV')
        elif op == 'COMP_L':
            w.write(f'I_{kind}_LESS')
        elif op == 'COMP_LE':
            w.write(f'I_{kind}_LESS_E')
        elif op == 'COMP_G':
            w.write(f'I_{kind}_GREATER')
        elif op == 'COMP_GE':
            w.write(f'I_{kind}_GREATER_E')
        elif op == 'EQ_OP':
            w.write('I_EQ')
        elif op == 'NOT_EQ_OP':
            w.write('I_NOT_EQ')
        elif op == 'OR_OP':
            w.write('I_OR')
        elif op == 'AND_OP':
            w.write('I_AND')    
        else:
            print(f'invalid binary operation: {op}')
            exit(1)

    def __str__(self):
        return f'{self.__class__.__name__}({self.op.type})' 

class ExprBinArith(ExprBinary):
    def checkTypes(self):
        leftType = None
        rightType = None
        if self.left and self.right:
            leftType = self.left.checkTypes()
            rightType = self.right.checkTypes()
            if leftType and rightType and leftType.isArithmetic() and rightType.isArithmetic():
                unifyTypes(leftType, rightType)
            else:
                semanticError(self.op, f'cannot perform arithmetic operations with types: {leftType.kind} and {rightType.kind}')
            return leftType
        else:
            semanticError(self.op, f'no value specified in operation: {self.op.type}')
        return
            

class ExprBinComparison(ExprBinary):
    def checkTypes(self):
        leftType = self.left.checkTypes()
        rightType = self.right.checkTypes()
        if leftType and leftType.isComparable():
            unifyTypes(leftType, rightType)
        else:
            semanticError(self.op, f'cannot perform comparison operations with this type: {leftType.kind}')
        return TypePrim(Token('BOOLEAN_KW', '', self.op.lineNr), 'boolean')

class ExprBinEquality(ExprBinary):
    def checkTypes(self):
        leftType = self.left.checkTypes()
        rightType = self.right.checkTypes()
        if leftType and leftType.hasValue():
            unifyTypes(leftType, rightType)
        else:
            semanticError(self.op, f'cannot perform comparison operations with this type: {leftType.kind}')
        return TypePrim(Token('BOOLEAN_KW', '', self.op.lineNr), 'boolean')

class ExprBinLogic(ExprBinary):
    def checkTypes(self):
        leftType = self.left.checkTypes()
        rightType = self.right.checkTypes()
        unifyTypes(leftType, TypePrim(Token('BOOLEAN_KW', '', self.op.lineNr), 'boolean'))
        unifyTypes(rightType, TypePrim(Token('BOOLEAN_KW', '', self.op.lineNr), 'boolean'))
        return TypePrim(Token('BOOLEAN_KW', '', self.op.lineNr), 'boolean')

class ExprUnary(Expr):
    def __init__(self, op, target):
        self.addChildren(target)
        self.op = op
        self.target = target

    def printNode(self, p):
        p.print('target', self.target)

    def resolveNames(self, scope):
        self.target.resolveNames(scope)
        self.targetNode = scope.resolveName(self.target.name)
        
    def genCode(self, w):
        self.target.genCode(w)
        op = self.op.type        

        if op in ['INC', 'DEC']:
            w.write(f'I_{op}')

            if hasattr(self.targetNode, 'stackSlot'):
                w.write('I_SET_L', self.targetNode.stackSlot)
                w.write('I_GET_L', self.targetNode.stackSlot)
            else:
                print('unknown assignment variable')
                exit(1)

        elif op == 'NOT_OP':
            w.write('I_NOT')
        else:
            print(f'invalid unary operation: {op}')
            exit(1)

    def __str__(self):
        return f'{self.__class__.__name__}({self.op.type})'

class ExprUnarArith(ExprUnary):
    def checkTypes(self):
        targetType = self.target.checkTypes()
        if targetType:
            if targetType.isArithmetic():
                pass 
            else:
                semanticError(self.op, f'cannot perform arithmetic operations with this type: {targetType}')
        return targetType

class ExprUnarLogic(ExprUnary):
    def checkTypes(self):
        targetType = self.target.checkTypes()
        unifyTypes(targetType, TypePrim(Token('BOOLEAN_KW', '', self.op.lineNr), 'boolean'))
        return TypePrim(Token('BOOLEAN_KW', '', self.op.lineNr), 'boolean')

class ExprLit(Expr):
    def __init__(self, type, lit):
        self.type = type
        self.lit = lit

    def printNode(self, p):
        p.print('type', self.type)
        p.print('lit', self.lit)

    def resolveNames(self, scope):
        pass

    def checkTypes(self):
        litType = self.lit.type

        if litType == 'INT':
            return TypePrim(Token('INT_KW', self.lit.value, self.lit.lineNr), 'int')

        elif litType == 'FLOAT':
            return TypePrim(Token('FLOAT_KW', self.lit.value, self.lit.lineNr), 'float')

        elif litType == 'STR':
            return TypePrim(Token('STRING_KW', self.lit.value, self.lit.lineNr), 'string')

        elif litType == 'TRUE_KW':
            return TypePrim(Token('BOOLEAN_KW', self.lit.value, self.lit.lineNr), 'boolean')

        elif litType == 'FALSE_KW':
            return TypePrim(Token('BOOLEAN_KW', self.lit.value, self.lit.lineNr), 'boolean')        

        else:
            semanticError(self.lit, 'this type does not exist')

    def genCode(self, w):
        litType = self.lit.type

        if litType == 'INT':
            w.write('I_INT_PUSH', self.lit.value)
        elif litType == 'FLOAT':
            value = gv.bytes2Int(self.lit.value)
            w.write('I_FLOAT_PUSH', value)
        elif litType == 'STR':
            value = gv.bytes2Int(self.lit.value)
            w.write('I_STRING_PUSH', value)
        elif litType == 'TRUE_KW':
            w.write('I_BOOLEAN_PUSH', 1)
        elif litType == 'FALSE_KW':
            w.write('I_BOOLEAN_PUSH', 0)
        else:
            print('unknown literal type')
            exit(1)

class ExprVar(Expr):
    def __init__(self, name):
        self.name = name

    def printNode(self, p):
        p.print('name', self.name)

    def resolveNames(self, scope):
        self.targetNode = scope.resolveName(self.name)

    def checkTypes(self):
        if self.targetNode:
            if isinstance(self.targetNode, DeclFn):
                semanticError(self.name, f'argument \'{self.targetNode.name.value}\' is not a variable')
            return self.targetNode.type

    def genCode(self, w):
        if hasattr(self.targetNode, 'stackSlot'):
            w.write('I_GET_L', self.targetNode.stackSlot)
        elif hasattr(self.targetNode, 'globalSlot'):
            w.write('I_GET_G', self.targetNode.globalSlot)
        else:
            print('unknown variable')
            exit(1)

class ExprFnCall(Expr):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def printNode(self, p):
        p.print('name', self.name)
        p.print('args', self.args)

    def resolveNames(self, scope):
        self.targetNode = scope.resolveName(self.name)
        [arg.resolveNames(scope) for arg in self.args if arg]
  
    def checkTypes(self):
        argTypes = []
        for arg in self.args:
            argTypes.append(arg.checkTypes())

        if not self.targetNode:
            return
        if not isinstance(self.targetNode, DeclFn):
            semanticError(self.name, 'the call target is not a function')
            return

        paramTypes = [param.type for param in self.targetNode.params]
        if len(paramTypes) != len(argTypes):
            semanticError(self.name, f'invalid argument count: expected {len(paramTypes)}, got {len(argTypes)}')

        paramCount = min(len(paramTypes), len(argTypes))
        for i in range(paramCount):
            unifyTypes(paramTypes[i], argTypes[i])

        return self.targetNode.type

    def genCode(self, w):
        w.write('I_CALL_BEGIN')
        [arg.genCode(w) for arg in self.args]
        w.write('I_CALL', self.targetNode.startLabel, len(self.args))

class Stmt(Node):
    pass

class StmtVarDecl(Stmt):
    def __init__(self, type, name, value):
        self.addChildren(type, value)
        self.type = type
        self.name = name
        self.value = value

    def printNode(self, p):
        p.print('type', self.type)
        p.print('name', self.name)
        p.print('value', self.value)

    def resolveNames(self, scope):
        self.stackSlot = gv.stackSlotIndex
        gv.stackSlotIndex += 1
        scope.add(self.name, self)
        if self.value:
            self.value.resolveNames(scope)

    def checkTypes(self):
        if self.value:
            valueType = self.value.checkTypes()
            unifyTypes(self.type, valueType)

    def genCode(self, w):
        if self.value:
            self.value.genCode(w)
            w.write('I_SET_L', self.stackSlot)

class StmtAssign(Stmt):
    def __init__(self, op, target, value):
        self.addChildren(value)
        self.op = op
        self.target = target
        self.value = value

    def printNode(self, p):
        p.print('target', self.target)
        p.print('value', self.value)

    def resolveNames(self, scope):
        self.targetNode = scope.resolveName(self.target)
        self.value.resolveNames(scope)

    def checkTypes(self):
        valueType = self.value.checkTypes()
        if valueType and self.targetNode:
            unifyTypes(self.targetNode.type, valueType)

    def genCode(self, w):
        self.value.genCode(w)
        if hasattr(self.targetNode, 'stackSlot'):
            w.write('I_SET_L', self.targetNode.stackSlot)
        else:
            print('unknown assignment variable')
            exit(1)

class StmtIf(Stmt):
    def __init__(self, branches, elseStmt):
        self.addChildren(*branches, elseStmt)
        self.branches = branches
        self.elseStmt = elseStmt

    def printNode(self, p):
        p.print('branch', self.branches)
        p.print('else', self.elseStmt)

    def resolveNames(self, scope):
        [branch.resolveNames(scope) for branch in self.branches]
        if self.elseStmt:
            self.elseStmt.resolveNames(scope) 

    def checkTypes(self):
        [branch.checkTypes() for branch in self.branches]
        if self.elseStmt:
            self.elseStmt.checkTypes() 

    def genCode(self, w):
        [branch.genCode(w) for branch in self.branches]
        if self.elseStmt:
            self.elseStmt.genCode(w)

class StmtBranch(Stmt):
    def __init__(self, cond, body):
        self.addChildren(cond, body)
        self.cond = cond
        self.body = body

    def printNode(self, p):
        p.print('cond', self.cond)
        p.print('body', self.body)

    def resolveNames(self, scope):
        self.cond.resolveNames(scope)
        self.body.resolveNames(scope)

    def checkTypes(self):
        condType = self.cond.checkTypes()
        unifyTypes(TypePrim(Token('BOOLEAN_KW', '', condType.token.lineNr), 'boolean'), condType)
        self.body.checkTypes()

    def genCode(self, w):
        endL = gc.Label()
        self.cond.genCode(w)
        w.write('I_BZ', endL)
        self.body.genCode(w)
        w.placeLabel(endL)

class StmtElse(Stmt):
    def __init__(self, body):
        self.body = body

    def printNode(self, p):
        p.print('body', self.body)

    def resolveNames(self, scope):
        self.body.resolveNames(scope)

    def checkTypes(self):
        self.body.checkTypes()

    def genCode(self, w):
        endL = gc.Label()
        self.body.genCode(w)
        w.placeLabel(endL)

class StmtLoop(Stmt):
    pass

class StmtFor(StmtLoop):
    def __init__(self, decl, cond, final, body):
        self.decl = decl
        self.cond = cond
        self.final = final
        self.body = body

    def printNode(self, p):
        p.print('decl', self.decl)
        p.print('cond', self.cond)
        p.print('final', self.final)
        p.print('body', self.body)

    def resolveNames(self, scope):
        self.decl.resolveNames(scope)
        self.cond.resolveNames(scope)
        self.final.resolveNames(scope)
        self.body.resolveNames(scope)

    def checkTypes(self):
        self.decl.checkTypes()
        condType = self.cond.checkTypes()
        unifyTypes(TypePrim(Token('BOOLEAN_KW', '', condType.token.lineNr), 'boolean'), condType)
        self.body.checkTypes()

class StmtWhile(StmtLoop):
    def __init__(self, cond, body):
        self.addChildren(cond, body)
        self.cond = cond
        self.body = body

    def printNode(self, p):
        p.print('cond', self.cond)
        p.print('body', self.body)

    def resolveNames(self, scope):
        self.cond.resolveNames(scope)
        self.body.resolveNames(scope)

    def checkTypes(self):
        condType = self.cond.checkTypes()
        unifyTypes(TypePrim(Token('BOOLEAN_KW', '', condType.token.lineNr), 'boolean'), condType)
        self.body.checkTypes()

    def genCode(self, w):
        self.startL = gc.Label()
        self.endL = gc.Label()
        w.placeLabel(self.startL)
        self.cond.genCode(w)
        w.write('I_BZ', self.endL)
        self.body.genCode(w)
        w.write('I_BR', self.startL)
        w.placeLabel(self.endL)

class StmtInput(Stmt):
    def __init__(self, inputKw, args):
        self.inputKw = inputKw
        self.args = args

    def printNode(self, p):
        p.print('input_kw', self.inputKw)
        p.print('args', self.args) 

    def resolveNames(self, scope):
        [arg.resolveNames(scope) for arg in self.args]

class StmtOutput(Stmt):
    def __init__(self, outputKw, results):
        self.outputKw = outputKw
        self.results = results

    def printNode(self, p):
        p.print('output_kw', self.outputKw)
        p.print('value', self.results)

    def resolveNames(self, scope):
        [result.resolveNames(scope) for result in self.results]
    
class StmtBreak(Stmt):
    def __init__(self, breakKw):
        self.breakKw = breakKw

    def printNode(self, p):
        p.print('break_kw', self.breakKw)

    def resolveNames(self, scope):
        currNode = self.parent
        self.targetNode = None
        while currNode:
            if isinstance(currNode, StmtLoop):
                self.targetNode = currNode
                break
            else:
                currNode = currNode.parent

        if not self.targetNode:
            print(f'Error:{gv.filename}:{self.breakKw.lineNr}: break is not in loop')
            gv.errors = True

    def checkTypes(self):
        pass
    
    def genCode(self, w):
        w.write('I_BR', self.targetNode.endL)

class StmtContinue(Stmt):
    def __init__(self, continueKw):
        self.continueKw = continueKw

    def printNode(self, p):
        p.print('continue_kw', self.continueKw)
    
    def resolveNames(self, scope):
        currNode = self.parent
        self.targetNode = None
        while currNode:
            if isinstance(currNode, StmtLoop):
                self.targetNode = currNode
                break
            else:
                currNode = currNode.parent

        if not self.targetNode:
            print(f'Error:{gv.filename}:{self.continueKw.lineNr}: continue is not in loop')
            gv.errors = True

    def checkTypes(self):
        pass

    def genCode(self, w):
        w.write('I_BR', self.targetNode.startL)

class StmtReturn(Stmt):
    def __init__(self, retKw, value):
        self.addChildren(value)
        self.retKw = retKw
        self.value = value

    def printNode(self, p):
        p.print('return_kw', self.retKw)
        p.print('value', self.value)

    def resolveNames(self, scope):
        if self.value:
            self.value.resolveNames(scope)

    def checkTypes(self):
        retType = self.findAncestor(DeclFn).type
        valueType = self.value.checkTypes() if self.value else TypePrim(Token('VOID_KW', '', self.retKw.lineNr), 'void')
        unifyTypes(retType, valueType)

    def genCode(self, w):
        if self.value:
            self.value.genCode(w)
            w.write('I_RET_V')
        else:
            w.write('I_RET')

class StmtExpr(Stmt):
    def __init__(self, expr):
        self.addChildren(expr)
        self.expr = expr

    def printNode(self, p):
        p.print('expr', self.expr)

    def resolveNames(self, scope):
        self.expr.resolveNames(scope)

    def checkTypes(self):
        self.expr.checkTypes()

    def genCode(self, w):
        self.expr.genCode(w)
        w.write('I_POP')

class Type(Node):
    def __init__(self):
        super()
    
    def isArithmetic(self):
        return False

    def isComparable(self):
        return False

    def hasValue(self):
        return False

class TypePrim(Type):
    def __init__(self, token, kind):
        self.token = token
        self.kind = kind

    def printNode(self, p):
        p.print('kind', self.kind)

    def isArithmetic(self):
        return self.kind == 'float' or self.kind == 'int'

    def isComparable(self):
        return self.kind == 'float' or self.kind == 'int'

    def hasValue(self):
        return self.kind != 'void'