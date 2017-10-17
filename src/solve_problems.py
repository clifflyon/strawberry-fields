"""
Strawberries are growing in a rectangular field of length and width at most 50.
You want to build greenhouses to enclose the strawberries. Greenhouses are
rectangular, axis-aligned with the field (i.e., not diagonal), and may not
overlap. The cost of each greenhouse is $10 plus $1 per unit of area covered.

This program chooses the best number of greenhouses to build, and their
locations, so as to enclose all the strawberries as cheaply as possible. The
solution is heuristic: it may not always produce the lowest possible cost; the
program seeks a reasonable tradeoff of efficiency and optimality.

The program reads a small integer 1 <= N <= 10 representing the maximum number
of greenhouses to consider, and a matrix representation of the field, in which
the '@' symbol represents a strawberry. Output is a copy of the original matrix
with letters used to represent greenhouses, preceded by the covering's cost.
Here is an example input-output pair:

Input
4
..@@@@@...............
..@@@@@@........@@@...
.....@@@@@......@@@...
.......@@@@@@@@@@@@...
.........@@@@@........
.........@@@@@........

Output
90
..AAAAAAAA............
..AAAAAAAA....CCCCC...
..AAAAAAAA....CCCCC...
.......BBBBBBBCCCCC...
.......BBBBBBB........
.......BBBBBBB........

In this example, the solution cost of $90 is computed as

    (10+8*3) + (10+7*3) + (10+5*3).

This program reads the 9 sample inputs found at

    http://itasoftware.com/careers/puzzles/rectangles.txt

and reports the total cost of the 9 solutions found, as well as each individual
solution.

On a fast, modern laptop, the program runs in about 5 seconds, most often
producing a total score of 1465.

@author: clifford.lyon@gmail.com

"""
import random
import sys
from itertools import combinations
from optparse import OptionParser

from field import StrawberryField
from memoize import Memoize
from rectangle import make_rectangle

T, L, B, R, COST, AREA = 0, 1, 2, 3, 4, 5
MAX_SUCCESSORS = 100


class BestSolution(object):
    """ holder for the best solution so far """

    def __init__(self):
        """ create a new instance to hold the best solution """
        self._solution = None
        self._score = sys.maxsize

    def store(self, candidate, score, goal):
        """ store a new candidate if better than current """
        if score < self._score and len(candidate) <= goal:
            self._score = score
            self._solution = candidate

    def solution(self):
        """ return the best solution """
        return self._solution


def pairs(seq):
    """ generate pairs of items in a list.  list order is randomized. """
    random.shuffle(seq)
    for pair in combinations(seq, 2):
        yield pair


def get_problems(infile="../data/rectangles.txt"):
    """ return array of data for the specific problem
    the first element is the maximum number of greenhouses.  the rest
    of the elements are the input data for the strawberry field
    """
    fh = open(infile, "r")
    buf = []
    for line in fh:
        line = line.strip()
        if line == "":
            if buf:
                yield buf
            buf = []
        elif line.strip():
            buf.append(line)
    if buf:
        yield buf


def agglomerate(field, partition, goal):
    """ combine greenhouses until we're done """
    greenhouse_list = partition[:]
    num_greenhouses = len(greenhouse_list)
    successors = [partition]
    best_solution = BestSolution()
    best_solution.store(partition,
                        get_score(partition),
                        field.maximum_greenhouses)

    while True:
        if num_greenhouses <= goal:
            break
        score, _successors = successors_by_agglomeration(successors)
        if not _successors:
            break
        successors = _successors
        num_greenhouses = len(successors[0])
        best_solution.store(successors[0],
                            score,
                            field.maximum_greenhouses)
    return [best_solution.solution()]


@Memoize
def merge_rectangles(rect1, rect2):
    """ memoizable version at program scope """
    return rect1.merge(rect2)


def successors_by_agglomeration(partitions):
    """ main action is here """

    # start out with max best score
    best_score = sys.maxsize
    # this is a set to eliminate duplicates
    successors = set()

    # for each possible solution
    for greenhouse_list in partitions:

        # check and see if we've generated enough successors
        if len(successors) >= MAX_SUCCESSORS:
            break

        # baseline our progress
        base_score = get_score(greenhouse_list)

        # check each pair in the list
        for house1, house2 in pairs(greenhouse_list):

            # make a copy
            successor = greenhouse_list[:]

            # merge the two
            new_house = merge_rectangles(house1, house2)

            # check and see if we included any other greenhouses
            # if we did, we'll try another route - we want local, incremental
            # aggregation
            count_overlaps = 0
            for greenhouse in greenhouse_list:
                if (greenhouse[B] < new_house[T] or
                        greenhouse[T] > new_house[B] or
                        greenhouse[R] < new_house[L] or
                        greenhouse[L] > new_house[R]):
                    continue
                count_overlaps += 1
                if count_overlaps > 2:
                    break

            if count_overlaps == 2:
                # successor is valid
                successor.remove(house1)
                successor.remove(house2)
                successor.append(new_house)
                score = (base_score - house1[COST] -
                         house2[COST] + new_house[COST])
                # if we've improved, store it
                if score < best_score:
                    frozen_successor = frozenset(successor)
                    successors = set()
                    successors.add(frozen_successor)
                    best_score = score
                elif score == best_score:
                    frozen_successor = frozenset(successor)
                    successors.add(frozen_successor)
                    # break if we're done
                    if len(successors) >= MAX_SUCCESSORS:
                        break

    # convert our set to a mutable type
    result = [[r for r in s] for s in successors]
    # if we have too many, sample
    if len(result) > MAX_SUCCESSORS:
        return best_score, random.sample(result, MAX_SUCCESSORS)
    # return the best score and the successors
    return best_score, result


def get_horizontal_runs(field):
    """ return natural horizontal clusters """
    berries = field.get_berries_in_rectangle(field.root_region)
    for row in range(field.num_rows):
        buf = []
        for col in range(field.num_cols):
            point = (row, col)
            if point in berries:
                buf.append(point)
            else:
                if buf:
                    if len(buf) > 1:
                        yield buf
                    buf = []
        if len(buf) > 1:
            yield buf


def get_vertical_runs(field):
    """ return natural vertical clusters """
    berries = field.get_berries_in_rectangle(field.root_region)
    for col in range(field.num_cols):
        buf = []
        for row in range(field.num_rows):
            point = (row, col)
            if point in berries:
                buf.append(point)
            else:
                if buf:
                    if len(buf) > 1:
                        yield buf
                    buf = []
        if len(buf) > 1:
            yield buf


def assign_open_greenhouses(field, partition):
    """ assign any open greenhouses sequentially """
    # greenhouse_list = field.greenhouses(partition)
    berries = field.get_berries_in_rectangle(field.root_region)
    sp = sorted(partition, key=lambda x: x[AREA])
    for berry in berries:
        is_assigned = False
        for r in sp:
            if berry in r:
                is_assigned = True
                break
        if not is_assigned:
            # if any([berry in r for r in partition]): # greenhouse_list]):
            #     continue
            partition.append(
                make_rectangle(berry[0], berry[1], berry[0], berry[1]))
    return partition


def pointlist2rectangle(point_list):
    """ convert a list of points into an enclosing rectangle """
    row_elems = [p[0] for p in point_list]
    col_elems = [p[1] for p in point_list]
    return make_rectangle(min(row_elems), min(col_elems),
                          max(row_elems), max(col_elems))


def combine_and_maintain_density(field, partition):
    """ for the start state, find natural greenhouses """
    pcopy = partition[:]
    fns = field.num_strawberries
    while True:
        num_merged = 0
        for first, second in pairs(pcopy):
            if first not in partition:
                continue
            if second not in partition:
                continue
            merged = merge_rectangles(first, second)
            if fns(merged) == merged[AREA]:
                count_overlaps = 0
                for t in partition:
                    if (t[B] < merged[T] or t[T] > merged[B] or
                            t[R] < merged[L] or t[L] > merged[R]):
                        continue
                    count_overlaps += 1
                    if count_overlaps > 2:
                        break
                if count_overlaps == 2:
                    partition.remove(first)
                    partition.remove(second)
                    partition.append(merged)
                    num_merged += 1
        if num_merged == 0:
            break
        pcopy = partition[:]
    return partition


def get_score(partition):
    """ score a partition based on cost and aggregate function """
    return sum([r[COST] for r in partition])


def get_start_state(field):
    """ get the starting state of the problem - a heuristic to reduce
    the state space """
    mix = {}
    mirror = {}
    state = []

    vertical_runs = [pointlist2rectangle(v) for v in get_vertical_runs(field)]
    vertical_runs = assign_open_greenhouses(field, vertical_runs)
    vertical_runs = combine_and_maintain_density(field, vertical_runs)

    horiz_runs = [pointlist2rectangle(h) for h in get_horizontal_runs(field)]
    horiz_runs = assign_open_greenhouses(field, horiz_runs)
    horiz_runs = combine_and_maintain_density(field, horiz_runs)

    for berry, idx in field.list_berries(horiz_runs):
        mix[berry] = [idx]
    for berry, idx in field.list_berries(vertical_runs):
        mix[berry].append(idx)
    for berry in mix:
        mirror.setdefault(tuple(mix[berry]), [])
        mirror[tuple(mix[berry])].append(berry)
    for key in mirror:
        state.append(pointlist2rectangle(mirror[key]))

    return state


def main():
    """ entry point """

    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-i", "--input", dest="infile",
                      default="../data/rectangles.txt",
                      help="read data from FILENAME")
    (options, _) = parser.parse_args()

    total_cost = 0
    for problem in get_problems(options.infile):
        problem = StrawberryField(problem)

        if problem.num_rows > 50:
            print "number of rows exceeds maximum of 50, skipping..."

        if problem.num_cols > 50:
            print "number of columns exceeds maximum of 50, skipping..."

        if problem.maximum_greenhouses > 10:
            print "number of greenhouses too large, need an integer N such"
            print "that 1 <= N <= 10..."

        if problem.maximum_greenhouses < 1:
            print "number of greenhouses too small, need an integer N such"
            print "that 1 <= N <= 10..."

        start_state = get_start_state(problem)
        solutions = agglomerate(problem, start_state, 2)
        cost = get_score(solutions[0])
        print cost
        print problem.display(solutions[0])
        # print problem.maximum_greenhouses
        # print problem
        total_cost += cost
    print
    print "Total cost for all greenhouses:", total_cost
    return 0

if __name__ == "__main__":
    if sys.version_info < (2, 6,):
        print "please use python 2.6 or greater"
        sys.exit(1)
    sys.exit(main())
