"""
Decorators
"""


import functools
import time


def staticVars(**kwargs):
    """Add static variables to function"""
    def decorate(func):
        """Add attributes to func"""
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

def callCounter(func):
    """count the number of times a function is called"""

    @functools.wraps(func)
    def helper(*args, **kwargs):
        helper.calls += 1
        return func(*args, **kwargs)
    helper.calls = 0

    return helper

def functionTimer(func):
    """time execution time of function"""

    @functools.wraps(func)
    def fTimer(*args, **kwargs):
        startTime = time.perf_counter()
        value = func(*args, **kwargs)
        endTime = time.perf_counter()
        fTimer.elapseTime = endTime - startTime
        return value
    fTimer.elapseTime = 0

    return fTimer

"""
def _greeting(func):
    @functools.wraps(func)
    def functionWrapper(x):
        #function_wrapper of greeting
        print("Hi, " + func.__name__ + " returns:")
        return func(x)
    return functionWrapper

def decorator1(f):
    def helper():
        print("Decorating", f.__name__)
        f()
    return helper

class decorator2:

    def __init__(self, f):
        self.f = f

    def __call__(self):
        print("Decorating", self.f.__name__)
        self.f()
"""
