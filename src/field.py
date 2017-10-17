"""

@author: clifford.lyon@gmail.com

The field package provides the locations of all the strawberries and functions
to display a solution, to evaluate a covering, etc.

"""

import sys

from memoize import Memoize
from rectangle import make_rectangle

LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz"
T, L, B, R = 0, 1, 2, 3


class StrawberryField(object):
    """ data structure representing the field
    use a sparse matrix representation, storing stawberries by row

    partition - is a list of rectangles that break up the field.  sometimes the
    partition will exhuastively enumerate an area; sometime is represents only
    the area required to account for greenhouses.
    """

    def __init__(self, data):
        """ create a field object from the provided problem data """
        self.rows = []
        self.num_rows = 0
        self.num_cols = 0
        self.top = sys.maxsize
        self.left = sys.maxsize
        self.right = -1
        self.bottom = -1
        self.maximum_greenhouses = int(data[0])
        for row in data[1:]:
            self.add_row(row)
        self.root_region = \
            make_rectangle(self.top, self.left, self.bottom, self.right)

    @Memoize
    def num_strawberries(self, rectangle):
        """ return the count of strawberries in the rectangle """
        # return len(self.get_berries_in_rectangle(rectangle))
        num = 0
        for i in range(rectangle[T], rectangle[B] + 1):
            # num += sum([1 for berry in self.rows[i] if berry in rectangle])
            num += sum([1 for berry in self.rows[i]
                        if rectangle[L] <= berry[1] <= rectangle[R]])
        return num

    def greenhouses(self, partition):
        """ return a list of the greenhouses in a partition """
        ghs = []
        for rect in partition:
            f_rect = self.feasible_region(rect)
            if f_rect:
                ghs.append(f_rect)
        return ghs

    def list_berries(self, partition):
        """ helper to set up the start state) """
        result = []
        for berry in self.get_berries_in_rectangle(self.root_region):
            result.append((berry, self._get_rect_id(berry, partition)))
        return result

    def _get_rect_id(self, berry, partition):
        """ return the id of the rectangle containing the berry, or None """
        for idx, rect in enumerate(partition):
            if berry in rect:
                return idx
        return None

    def display(self, partition):
        """ return a string representation of a field """
        berries = []
        for row in self.rows:
            for berry in row:
                berries.append(berry)
        buf = ""
        for row in range(0, self.num_rows):
            for col in range(0, self.num_cols):
                point = (row, col)
                # check first
                dot = True
                num_assigned = 0
                chr_assign = "."
                for rect_id, rect in enumerate(partition):
                    feasible_rect = self.feasible_region(rect)
                    if feasible_rect and point in feasible_rect:
                        if num_assigned == 0:
                            chr_assign = LABELS[rect_id % len(LABELS)]
                            dot = False
                        else:
                            chr_assign = "*"
                        num_assigned += 1
                if dot:
                    if point in berries:
                        buf += "@"
                    else:
                        buf += "."
                else:
                    buf += chr_assign
            buf += "\n"
        return buf

    def display_full(self, partition):
        """ display full paritions, not just feasible regions """
        buf = ""
        for row in range(0, self.num_rows):
            for col in range(0, self.num_cols):
                point = (row, col)
                dot = True
                for rect_id, rect in enumerate(partition):
                    if point in rect:
                        buf += LABELS[rect_id % len(LABELS)]
                        dot = False
                        break
                if dot:
                    buf += "."
            buf += "\n"
        return buf

    @Memoize
    def feasible_region(self, rectangle=None):
        """ return the rectangle inside a rectangle that encloses
        strawberries.  if no rectangle is provided, return the root region
        """
        if not rectangle:
            return self.root_region

        berries = self.get_berries_in_rectangle(rectangle)
        b_zero = [b[0] for b in berries]
        b_one = [b[1] for b in berries]
        if berries:
            origin = (min(b_zero), min(b_one))
            extent = (max(b_zero), max(b_one))
            return make_rectangle(origin[0], origin[1], extent[0], extent[1])
        return None

    @Memoize
    def get_berries_in_rectangle(self, rectangle):
        """ get a list of strawberries in the rectangle """
        berries = []
        for i in xrange(rectangle[T], rectangle[B] + 1):
            berries += [berry for berry in self.rows[i] if berry in rectangle]
        return berries

    def add_row(self, row):
        """ add a row to the grid """
        elements = list(row)
        rbuf = []
        for idx, elem in enumerate(elements):
            if elem == "@":
                rbuf.append((self.num_rows, idx))
                self.top = min(self.top, self.num_rows)
                self.left = min(self.left, idx)
                self.bottom = max(self.bottom, self.num_rows)
                self.right = max(self.right, idx)
        self.rows.append(rbuf)
        if self.num_cols < len(elements):
            self.num_cols = len(elements)
        self.num_rows += 1

    def __str__(self):
        """ display the original field """
        buf = ""
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if (row, col) in self.rows[row]:
                    buf += "@"
                else:
                    buf += "."
            buf += "\n"
        return buf
