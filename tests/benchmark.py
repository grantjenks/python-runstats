"""Benchmark core versus fast implementations.

"""

from __future__ import print_function

import random
import timeit

random.seed(0)
values = [random.random() for _ in range(int(1e4))]
pairs = [(pos, pos + (val * 2 - 1)) for pos, val in enumerate(values)]

core_stats = timeit.repeat(
    setup="""
from __main__ import values
from runstats.core import Statistics
stats = Statistics()
    """,
    stmt="""
for value in values:
    stats.push(value)
stats.mean()
    """,
    number=1,
    repeat=7,
)[2]

fast_stats = timeit.repeat(
    setup="""
from __main__ import values
from runstats.fast import Statistics
stats = Statistics()
    """,
    stmt="""
for value in values:
    stats.push(value)
stats.mean()
    """,
    number=1,
    repeat=7,
)[2]

speedup_stats = core_stats / fast_stats - 1

core_regr = timeit.repeat(
    setup="""
from __main__ import pairs
from runstats.core import Regression
regr = Regression()
    """,
    stmt="""
for pos, val in pairs:
    regr.push(pos, val)
regr.slope()
    """,
    number=1,
    repeat=7,
)[2]

fast_regr = timeit.repeat(
    setup="""
from __main__ import pairs
from runstats.fast import Regression
regr = Regression()
    """,
    stmt="""
for pos, val in pairs:
    regr.push(pos, val)
regr.slope()
    """,
    number=1,
    repeat=7,
)[2]

speedup_regr = core_regr / fast_regr - 1

print('core.Statistics:', core_stats)
print('fast.Statistics:', fast_stats)
print('  Stats Speedup: %.2fx faster' % speedup_stats)

print('core.Regression:', core_regr)
print('fast.Regression:', fast_regr)
print('   Regr Speedup: %.2fx faster' % speedup_regr)
