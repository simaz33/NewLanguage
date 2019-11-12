class Node():
    def printNode(self, p):
        print('PrintNode not implemented for', self.__name__)
        exit(1)

    def __str__(self):
        return self.__class__.__name__

class Param(Node):
    def __init__(self, type, name):
        self.name = name
        self.type = type

    def printNode(self, p):
        p.print('name', self.name)
        p.print('type', self.type)

class Program(Node):
    def __init__(self, decls):
        self.decls = decls

    def printNode(self, p):
        p.print('decls', self.decls)

class StmtBlock(Node):
    def __init__(self, stmts):
        self.stmts = stmts

    def printNode(self, p):
        p.print('stmts', self.stmts)

class Decl(Node):
    def __init__(self):
        super()

class DeclFn(Decl):
    def __init__(self, type, name, params, body):
        self.type = type
        self.name = name
        self.params = params
        self.body = body

    def printNode(self, p):
        p.print('retType', self.type)
        p.print('name', self.name)
        p.print('params', self.params)
        p.print('body', self.body)

class StmtVarDecl(Decl):
    def __init__(self, type, name, value):
        self.type = type
        self.name = name
        self.value = value

    def printNode(self, p):
        p.print('type', self.type)
        p.print('name', self.name)
        p.print('value', self.value)

class Expr(Node): 
    pass

class ExprStmt(Expr):
    pass

class ExprBinary(ExprStmt):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def printNode(self, p):
        p.print('left', self.left)
        p.print('right', self.right)

    def __str__(self):
        return f'{self.__class__.__name__}({self.op})' 

class ExprUnary(ExprStmt):
    def __init__(self, op, right):
        self.op = op
        self.right = right

    def printNode(self, p):
        p.print('right', self.right)

    def __str__(self):
        return f'{self.__class__.__name__}({self.op})'

class ExprLit(Expr):
    def __init__(self, type, lit):
        self.type = type
        self.lit = lit

    def printNode(self, p):
        p.print('type', self.type)
        p.print('lit', self.lit)

class ExprVar(Expr):
    def __init__(self, name):
        self.name = name

    def printNode(self, p):
        p.print('name', self.name)

class ExprFnCall(Expr):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def printNode(self, p):
        p.print('name', self.name)
        p.print('args', self.args)
  
class Stmt(Node):
    def __init__(self):
        super()

class StmtIf(Stmt):
    def __init__(self, branches, elseStmt):
        self.branches = branches
        self.elseStmt = elseStmt

    def printNode(self, p):
        p.print('cond', self.branches)
        p.print('else', self.elseStmt)

class StmtBranch(Stmt):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def printNode(self, p):
        p.print('cond', self.cond)
        p.print('body', self.body)

class StmtFor(Stmt):
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


class StmtElse(Stmt):
    def __init__(self, body):
        self.body = body

    def printNode(self, p):
        p.print('body', self.body)

class StmtWhile(Stmt):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def printNode(self, p):
        p.print('cond', self.cond)
        p.print('body', self.body)

class StmtInput(Stmt):
    def __init__(self, inputKw, args):
        self.inputKw = inputKw
        self.args = args

    def printNode(self, p):
        p.print('input_kw', 'input')
        p.print('args', self.args)    

class StmtOutput(Stmt):
    def __init__(self, outputKw, value):
        self.outputKw = outputKw
        self.value = value

    def printNode(self, p):
        p.print('output_kw', 'output')
        p.print('value', self.value)   

class StmtBreak(Stmt):
    def __init__(self, breakKw):
        self.breakKw = breakKw

    def printNode(self, p):
        p.print('break_kw', 'break')

class StmtContinue(Stmt):
    def __init__(self, continueKw):
        self.continueKw = continueKw

    def printNode(self, p):
        p.print('continue_kw', 'continue')

class StmtReturn(Stmt):
    def __init__(self, retKw, value):
        self.retKw = retKw
        self.value = value

    def printNode(self, p):
        p.print('return_kw', 'return')
        p.print('value', self.value)

class Type(Node):
    def __init__(self):
        super()

class TypePrim(Type):
    def __init__(self, kind):
        self.kind = kind

    def printNode(self, p):
        p.print('kind', self.kind)