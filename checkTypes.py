import ast
import sys
import globalVars as gv

def semanticError(token, msg):
    lineNr = token.lineNr if token else ''
    print(f'Error:{gv.filename}:{lineNr}: {msg}')
    gv.errors = True
    
def unifyTypes(type0, type1):
    if not type0 or not type1:
        pass
    elif type0.__class__.__name__ != type1.__class__.__name__:
        semanticError(type0.token, f'type mismatch: expected {type0.kind}, got {type1.kind}')
    elif isinstance(type0, ast.TypePrim):
        if type0.kind != type1.kind:
            semanticError(type0.token, f'type kind mismatch: expected {type0.kind}, got {type1.kind}')
    else:
        pass