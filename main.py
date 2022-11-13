import time
import threading


def countdown(n):
    while n > 0:
        print("Down " + str(n))
        time.sleep(1)
        n -= 1


def countup(until):
    x = 0
    while x < until:
        print("Up " + str(x))
        time.sleep(1)
        x += 1


threading.Thread(target=countdown, args=(5,)).start()
threading.Thread(target=countup, args=(5,)).start()
