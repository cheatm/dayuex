from queue import deque


class Context():

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value


dq = deque()
dq.append(Context(1))
dq.remove(Context(1))