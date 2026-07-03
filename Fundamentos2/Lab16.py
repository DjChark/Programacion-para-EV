class QueueError(Exception):
    pass


class Queue:
    def __init__(self):
        self.__queue = []

    def put(self, elem):
        self.__queue.insert(0, elem)

    def get(self):
        if not self.__queue:
            raise QueueError("Queue error")
        return self.__queue.pop()

    def is_empty(self):
        return len(self.__queue) == 0


# Código de prueba (salida esperada: 1, perro, False, Cola vacía)
que = Queue()
que.put(1)
que.put("perro")
que.put(False)

for i in range(3):
    print(que.get())

print(que.is_empty())

try:
    print(que.get())
except QueueError:
    print("Cola vacía")