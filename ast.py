from scope import Scope

class Node():
    self.parent = None
    
    def printNode(self, p):
        print('PrintNode not implemented for', self.__name__)
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
        print('resolveNames() is not implemented for: {self.__class__.__name__}')

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
        scope.add(self.name, self)

class Program(Node):
    def __init__(self, decls):
        self.addChildren(*decls)
        self.decls = decls

    def printNode(self, p):
        p.print('decls', self.decls)

    def resolveNames(self, scope):
        for decl in self.decls:
            scope.add(decl.name, decl)

        for decl in self.decls:
            decl.resolveNames(scope)

class StmtBlock(Node):
    def __init__(self, stmts):
        self.addChildren(*stmts)
        self.stmts = stmts

    def printNode(self, p):
        p.print('stmts', self.stmts)

    def resolveNames(self, parentScope):
        scope = Scope(parentScope)
        for stmt in self.stmts:
            stmt.resolveNames(scope)

class Decl(Node):
    def __init__(self):
        super()

class DeclFn(Decl):
    def __init__(self, type, name, params, body):
        self.addChildren(params, type, body)
        self.type = type
        self.name = name
        self.params = params
        self.body = body

    def printNode(self, p):
        p.print('retType', self.type)
        p.print('name', self.name)
        p.print('params', self.params)
        p.print('body', self.body)

    def resolveNames(self, parentScope):
        scope = Scope(parentScope)
        for param in self.params:
            param.resolveNames(scope)
        
        self.body.resolveNames(scope)

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
        self.left.resolveNames(scope)
        self.right.resolveNames(scope)

    def __str__(self):
        return f'{self.__class__.__name__}({self.op})' 


# ExprBinArith: TYPE + TYPE -> TYPE; is_arithmetic
class ExprBinArith(ExprBinary):
    pass

# ExprBinComparison: TYPE < TYPE -> BOOL; is_comparable
class ExprBinComparison(ExprBinary):
    pass

# ExprBinEquality: TYPE == TYPE -> BOOL; has_value
class ExprBinEquality(ExprBinary):
    pass

# ExprBinLogic: BOOL || BOOL -> BOOL
class ExprBinLogic(ExprBinary):
    pass

class ExprUnary(Expr):
    def __init__(self, op, right):
        self.addChildren(right)
        self.op = op
        self.right = right

    def printNode(self, p):
        p.print('right', self.right)

    def resolveNames(self, scope):
        self.right.resolveNames(scope)

    def __str__(self):
        return f'{self.__class__.__name__}({self.op})'

class ExprLit(Expr):
    def __init__(self, type, lit):
        self.type = type
        self.lit = lit

    def printNode(self, p):
        p.print('type', self.type)
        p.print('lit', self.lit)

    def resolveNames(self, scope):
        pass

class ExprVar(Expr):
    def __init__(self, name):
        self.name = name

    def printNode(self, p):
        p.print('name', self.name)

    def resolveNames(self, scope):
        self.targetNode = scope.resolveName(self.name)

class ExprFnCall(Expr):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def printNode(self, p):
        p.print('name', self.name)
        p.print('args', self.args)

    def resolveNames(self, scope):
        self.targetNode = scope.resolveName(self.target)
        for arg in args:
            arg.resolveNames(scope)
  
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
        scope.add(self.name, self)

class StmtIf(Stmt):
    def __init__(self, branches, elseStmt):
        self.branches = branches
        self.elseStmt = elseStmt

    def printNode(self, p):
        p.print('branch', self.branches)
        p.print('else', self.elseStmt)

class StmtBranch(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def printNode(self, p):
        p.print('cond', self.cond)
        p.print('body', self.body)

class StmtElse(Stmt):
    def __init__(self, body):
        self.body = body

    def printNode(self, p):
        p.print('body', self.body)

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

class StmtInput(Stmt):
    def __init__(self, inputKw, args):
        self.inputKw = inputKw
        self.args = args

    def printNode(self, p):
        p.print('input_kw', self.inputKw)
        p.print('args', self.args)    

class StmtOutput(Stmt):
    def __init__(self, outputKw, value):
        self.outputKw = outputKw
        self.value = value

    def printNode(self, p):
        p.print('output_kw', self.outputKw)
        p.print('value', self.value)   

class StmtBreak(Stmt):
    def __init__(self, breakKw):
        self.breakKw = breakKw

    def printNode(self, p):
        p.print('break_kw', self.breakKw)

    def resolveNames(self, scope):
        currNode = self.parent
        while currNode:
            if isinstance(currNode, StmtLoop):
                self.targetNode = currNode
                break
            else:
                currNode = currNode.parent

        if not self.targetNode:
            print(f'filename:{self.breakKw.lineNr}:error: break is not in loop')

class StmtContinue(Stmt):
    def __init__(self, continueKw):
        self.continueKw = continueKw

    def printNode(self, p):
        p.print('continue_kw', self.continueKw)
    
    def resolveNames(self, scope):
        currNode = self.parent
        while currNode:
            if isinstance(currNode, StmtLoop):
                self.targetNode = currNode
                break
            else:
                currNode = currNode.parent

        if not self.targetNode:
            print(f'filename:{self.breakKw.lineNr}:error: break is not in loop')

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

class StmtExpr(Stmt):
    def __init__(self, expr):
        self.addChildren(expr)
        self.expr = expr

    def printNode(self, p):
        p.print('expr', self.expr)

    def resolveNames(self, scope):
        self.expr.resolveNames(scope)

class Type(Node):
    def __init__(self):
        super()

class TypePrim(Type):
    def __init__(self, token, kind):
        self.token = token
        self.kind = kind

    def printNode(self, p):
        p.print('kind', self.kind)