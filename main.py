#!/usr/bin/python3

import globalVars as gv
from parser import Parser
from lexer import Lexer
from astPrinter import ASTPrinter
from scope import Scope
from genCode import CodeWriter
from vm import VM

def main():
    content = ''
    with open(gv.filename, 'r') as f:
        content = f.read()

    lexer = Lexer(gv.filename, content)
    lexer.lexAll()
    #lexer.dumpTokens()
    lexer.displayError()

    parser = Parser(lexer.tokens, gv.filename)
    root = parser.parseProgram()

    rootScope = Scope(None, gv.filename)
    scopeErrors = root.resolveNames(rootScope)
    typeErrors = root.checkTypes()

    if gv.errors:
        exit(1)
        
    #printer = ASTPrinter()
    #printer.print('root', root)
    
    writer = CodeWriter()
    root.genCode(writer)
    writer.dumpCode()

    vm = VM(writer.code)
    vm.exec()

if __name__ == '__main__':
    main()
    