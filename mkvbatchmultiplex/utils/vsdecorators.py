#!/usr/bin/env python3

"""Decorators"""

def staticVars(**kwargs):
    """Add static variables to function"""
    def decorate(func):
        """Add attributes to func"""
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


def greeting(expr):
    def greeting_decorator(func):
        def function_wrapper(x):
            print(expr + ", " + func.__name__ + " returns:")
            func(x)
        return function_wrapper
    return greeting_decorator


def argument_test_natural_number(f):
    def helper(x):
        if type(x) == int and x > 0:
            return f(x)
        else:
            raise Exception("Argument is not an integer")
    return helper


def call_counter(func):
    def helper(*args, **kwargs):
        helper.calls += 1
        return func(*args, **kwargs)
    helper.calls = 0

    return helper
