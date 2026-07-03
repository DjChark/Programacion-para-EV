class QueueError(Exception):
    # Excepción personalizada para cola vacía
    pass


class Queue:
    def __init__(self):
        self.__queue = []

    def put(self, elem):
        # Agrega al principio de la lista
        self.__queue.insert(0, elem)

    def get(self):
        # Elimina y devuelve el último elemento (el primero en llegar)
        if not self.__queue:
            raise QueueError("Queue error")
        return self.__queue.pop()


# Código de prueba (salida esperada: 1, perro, False, Queue error)
que = Queue()
que.put(1)
que.put("perro")
que.put(False)
try:
    for i in range(4):
        print(que.get())
except QueueError:
    print("Queue error")