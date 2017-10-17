"""
A rectangle class
@author: clifford.lyon@gmail.com
"""
from collections import namedtuple
from memoize import Memoize
T, L, B, R = 0, 1, 2, 3  # TOP, LEFT, BOTTOM, RIGHT indices


@Memoize
def make_rectangle(top, left, bottom, right):
    """ make a rectangle using layout members """
    a = (bottom - top + 1) * (right - left + 1)
    return Rectangle(top, left, bottom, right,
                     a + 10,  # cost
                     a,)  # area


class Rectangle(
        namedtuple("Rectangle", "top, left, bottom, right, cost, area")):
    """ Rectangle instances are read-only objects used to represent partitions
    of the strawberry field, or greenhouses, or anything rectangular.

    Note the cost function assumes the rectangle is placed as cheaply as
    possible; least cost may require a call to field#feasibleRegion
    """
    __slots__ = ()

    def __contains__(self, xxx_todo_changeme):
        """ return true if the provided point is contained in the rectangle """
        (r, c) = xxx_todo_changeme
        return self[T] <= r <= self[B] and self[L] <= c <= self[R]

    def merge(self, other):
        """ create a new rectangle from this one and another
        this function is memoized through a higher level class to consolidate
        the cache
        """
        top = self[T] if self[T] < other[T] else other[T]
        left = self[L] if self[L] < other[L] else other[L]
        bottom = self[B] if self[B] > other[B] else other[B]
        right = self[R] if self[R] > other[R] else other[R]
        a = (bottom - top + 1) * (right - left + 1)
        return self._make((top, left, bottom, right, a + 10, a, ))

if __name__ == "__main__":

    r1 = make_rectangle(0, 2, 3, 4)
    r2 = make_rectangle(1, 3, 4, 5)

    print r1.merge(r2)
