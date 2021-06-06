"""Benchmark core versus fast implementations.

"""

from __future__ import print_function

import random
import timeit

random.seed(0)
VALUES = [random.random() for _ in range(int(1e4))]
PAIRS = [
    (pos, pos + (val * 2 - 1)) for pos, val in enumerate(VALUES)
]


def main():
    core_stats = timeit.repeat(
        setup='''
from __main__ import VALUES
from runstats.core import Statistics
        ''',
        stmt='''
stats = Statistics(VALUES)
stats.mean()
        ''',
        number=1,
        repeat=7,
    )[2]

    fast_stats = timeit.repeat(
        setup='''
from __main__ import VALUES
from runstats._core import Statistics
        ''',
        stmt='''
stats = Statistics(VALUES)
stats.mean()
        ''',
        number=1,
        repeat=7,
    )[2]

    speedup_stats = core_stats / fast_stats - 1

    core_exp_stats = timeit.repeat(
        setup='''
from __main__ import VALUES
from runstats.core import ExponentialStatistics
exp_stats = ExponentialStatistics()
        ''',
        stmt='''
for value in VALUES:
    exp_stats.push(value)
exp_stats.mean()
        ''',
        number=1,
        repeat=7,
    )[2]

    fast_exp_stats = timeit.repeat(
        setup='''
from __main__ import VALUES
from runstats._core import ExponentialStatistics
exp_stats = ExponentialStatistics()
        ''',
        stmt='''
for value in VALUES:
    exp_stats.push(value)
exp_stats.mean()
        ''',
        number=1,
        repeat=7,
    )[2]

    speedup_exp_stats = core_exp_stats / fast_exp_stats - 1

    core_regr = timeit.repeat(
        setup='''
from __main__ import PAIRS
from runstats.core import Regression
regr = Regression()
        ''',
        stmt='''
for pos, val in PAIRS:
    regr.push(pos, val)
regr.slope()
        ''',
        number=1,
        repeat=7,
    )[2]

    fast_regr = timeit.repeat(
        setup='''
from __main__ import PAIRS
from runstats._core import Regression
regr = Regression()
        ''',
        stmt='''
for pos, val in PAIRS:
    regr.push(pos, val)
regr.slope()
        ''',
        number=1,
        repeat=7,
    )[2]

    speedup_regr = core_regr / fast_regr - 1

    print('core.Statistics:', core_stats)
    print('_core.Statistics:', fast_stats)
    print('  Stats Speedup: %.2fx faster' % speedup_stats)

    print('core.ExponentialStatistics:', core_exp_stats)
    print('_core.ExponentialStatistics:', fast_exp_stats)
    print('  ExpStats Speedup: %.2fx faster' % speedup_exp_stats)

    print('core.Regression:', core_regr)
    print('_core.Regression:', fast_regr)
    print('   Regr Speedup: %.2fx faster' % speedup_regr)


if __name__ == '__main__':
    main()
