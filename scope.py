class Scope():
    def __init__(self, parentScope, filename = 'default'):
        self.filename = filename
        self.parentScope = parentScope
        self.members = {}

    def add(self, nameToken, node):
        name = nameToken.value
        if name not in self.memebers.keys():
            self.members[name] = node
            return

        print(f'{self.filename}:{nameToken.lineNr}:duplicate variable: {name}')

    def resolveName(self, nameToken):
        name = nameToken.value
        if self.members[name]:
            return self.members[name]

        if self.parentScope:
            return self.parentScope.resolveName(nameToken)

        print(f'{self.filename}:{nameToken.lineNr}:error: undeclared variable: {name}')