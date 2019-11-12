#!/usr/bin/python3

import sys
from lexer import Lexer
from parser import Parser
from astPrinter import ASTPrinter

if __name__ == '__main__':
    filename = sys.argv[1]
    input = open(filename, 'r').read()
    lexer = Lexer(filename, input)
    lexer.lexAll()
    lexer.dumpTokens()
    lexer.displayError()

    parser = Parser(lexer.tokens, filename)
    root = parser.parseProgram()

    printer = ASTPrinter()
    printer.print('root', root)