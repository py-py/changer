__author__ = 'py'


class Dog:

    c = 'Something'

    def __init__(self, name):
        self.name = name

    def add_trick(self):
        print(self.c)

d = Dog('Fido')
d.c = 'Newworld!'

e = Dog('Buddy')


Dog.c = 'absolute'
print(d.c)
print(e.c)
