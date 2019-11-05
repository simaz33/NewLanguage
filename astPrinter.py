from ast import Node
from token import Token

class ASTPrinter():
    def __init__(self):
        self.indentLevel = 0
  
    def print(self, title, obj):
        if obj is None:
            self.printText(title, 'None')

        elif isinstance(obj, list):
            self.printList(title, obj)

        elif isinstance(obj, Node):
            self.printNode(title, obj)

        elif isinstance(obj, str):
            self.printText(title, obj)

        elif isinstance(obj, int):
            self.printText(title, obj)
        
        elif isinstance(obj, float):
            self.printText(title, obj)

        elif isinstance(obj, Token):
            self.printToken(title, obj)

        else:
            print('invalid print argument:', obj)

    def printList(self, title, list):
        if not list:
            self.printText(title, '[]')
            return

        for index, element in enumerate(list):
            elemTitle = '{}[{}]'.format(title, index)
            self.print(elemTitle, element)

    def printNode(self, title, node):
        self.printText(title, node.__class__.__name__)
        self.indentLevel += 1
        node.printNode(self)
        self.indentLevel -= 1

    def printText(self, title, text):
        prefix = ' ' * self.indentLevel
        print('{}{}: {}'.format(prefix, title, text))

    def printToken(self, title, token):
        self.printText(title, '{} ({})'.format(token.value, token.lineNr))
