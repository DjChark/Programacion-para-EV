class Stack:
    def __init__(self):
        self.__stk = []

    def push(self, val):
        self.__stk.append(val)

    def pop(self):
        val = self.__stk[-1]
        del self.__stk[-1]
        return val


class CountingStack(Stack):
    def __init__(self):
        super().__init__()
        self.__counter = 0

    def pop(self):
        val = super().pop()
        self.__counter += 1   # solo contamos las operaciones pop
        return val

    def get_counter(self):
        return self.__counter


# Código de prueba (esperado: 100)
stk = CountingStack()
for i in range(100):
    stk.push(i)
    stk.pop()
print(stk.get_counter())