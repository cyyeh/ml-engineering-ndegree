class MyClass:
    def method(self):
        return 'instance method called', self

    @classmethod
    def classmethod(cls):
        return 'class method called', cls

    @staticmethod
    def staticmethod():
        return 'static method called'


obj = MyClass()
print(obj.classmethod())
print(obj.staticmethod())
print(obj.method())

print(MyClass.classmethod())
print(MyClass.staticmethod())
print(MyClass.method())
