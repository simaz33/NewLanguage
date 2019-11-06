class A():
    def __init__(self):
        print('this is class A')

class B(A):
    def __init__(self):
        print('this is class B')

b = B()

if isinstance(b, A):
    print('b is instance of A')