#imports
from pynard import *
import unittest


from collections import deque

class Tst:
    def __init__(self, a_init, b_init):
        self.a = a_init
        self.b = b_init

    def __eq__(self, obj):
        if not isinstance(obj, Tst): return False
        return self.a == obj.a

    def __ne__(self, obj):
        return not self == obj

if __name__ == "__main__":
    boo = []

    boo.append(Tst(1, 2))

    print(Tst(1, 2) in boo)
    print(Tst(2, 4) in boo)


    #unittest.main()