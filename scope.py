class Scope():
    def __init__(self, parentScope, filename):
        self.filename = filename
        self.parentScope = parentScope
        self.members = {}

    def add(self, nameToken, node):
        name = nameToken.value
        if name not in self.members:
            self.members[name] = node
            return

        print(f'{self.filename}:{nameToken.lineNr}:duplicate variable: {name}')

    def resolveName(self, nameToken):
        name = nameToken.value
        if name in self.members:
            return self.members[name]

        if self.parentScope:
            return self.parentScope.resolveName(nameToken)

        print(f'Error:{self.filename}:{nameToken.lineNr}: undeclared variable: {name}')
        return None