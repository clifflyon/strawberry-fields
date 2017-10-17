"""
From github:

  https://gist.github.com/267733/8f5d2e3576b6a6f221f6fb7e2e10d395ad7303f9

@author: http://gist.github.com/jefftriplett
"""

import functools


class Memoize(object):
    """ provide a way to cache deterministic functions.
    simply decorate the function:

    @Memoize
    def fun(x):
        ...

    This came in handy for a few rectangle (greenhouse) -related functions -
    merging, counting strawberries in the rectangle, etc.

    Works for functions and class methods

    """

    def __init__(self, func):
        """ create a cache for a function """
        self.func = func
        self.memoized = {}
        self.method_cache = {}

    def __call__(self, *args):
        """ call the function through the wrapper """
        return self.cache_get(self.memoized, args, lambda: self.func(*args))

    def __get__(self, obj, objtype):
        """ retrieve a result from the cache """
        return self.cache_get(
            self.method_cache,
            obj,
            lambda: self.__class__(
                functools.partial(
                    self.func,
                    obj)))

    def cache_get(self, cache, key, func):
        """ lookup the key (args); if it doesn't exist, cache it """
        try:
            return cache[key]
        except KeyError:
            cache[key] = func()
            return cache[key]
