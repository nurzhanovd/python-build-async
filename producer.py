import heapq
import time
from collections import deque


class Result:
    def __init__(self, value=None, exc=None):
        self.value = value
        self.exc = exc

    def result(self):
        if self.exc:
            raise self.exc
        else:
            return self.value


class Scheduler:
    def __init__(self):
        self.ready = deque()  # Functions ready to execute
        self.sleeping = []
        self.sequence = 0

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay, func):
        self.sequence += 1
        deadline = time.time() + delay  # Expiration time
        heapq.heappush(self.sleeping, (deadline, self.sequence, func))

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                deadline, _, func = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(func)

            while self.ready:
                func = self.ready.popleft()
                func()


sched = Scheduler()


# ---------

class AsyncQueue:
    def __init__(self):
        self.items = deque()
        self.waiting = deque()  # All the "get(callback)" functions waiting for data
        self.closed = False  # Can queue be used ?

    def close(self):
        self.closed = True
        if self.waiting and not self.items:
            for func in self.waiting:
                sched.call_soon(func)


    def put(self, item):
        if (self.closed):
            raise QueueClosed()

        self.items.append(item)
        if self.waiting:
            func = self.waiting.popleft()
            sched.call_soon(func)

    def get(self, callback):
        # Wait until item is available. Then return it.
        if self.items:
            callback(Result(value=self.items.popleft()))
        else:
            if self.closed:
                callback(Result(exc=QueueClosed()))
            else:
                self.waiting.append(lambda: self.get(callback))


def producer(q, count):
    def _run(n):
        if n < count:
            print("Producing", n)
            q.put(n)
            sched.call_later(1, lambda: _run(n + 1))
        else:
            print("Producer done")
            q.close()  # Means no more items will be produced

    _run(0)


class QueueClosed(Exception):
    pass


def consumer(q):
    def _consume(result):
        try:
            item = result.result()
            print("Consuming", item)
            sched.call_soon(lambda: consumer(q))
        except QueueClosed:
            print("Consumer done")

    q.get(callback=_consume)


q = AsyncQueue()
sched.call_soon(lambda: producer(q, 10))
sched.call_soon(lambda: consumer(q))
sched.run()
