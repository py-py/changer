__author__ = 'py'


def w(f):
    def wrapper(*args):
        print('Before')
        print(f(*args))
        print('After')
    return wrapper

@w
def printer(name):
    return name

printer('YES')


def p(name):
    return name

p = w(p)
p('No')