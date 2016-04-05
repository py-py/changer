__author__ = 'py'


class A:
    s = 'Some'
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __call__(self, *args, **kwargs):
        return self.a + self.b

    def __bool__(self):
        return True if self.a+self.b != 0 else False

    @classmethod
    def method(cls):
        cls.s = 'New world!'

a = A(10, -1)

print(A.s)
A.method()
print(A.s)

