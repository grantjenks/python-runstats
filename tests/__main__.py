from __future__ import print_function

import sys

from runstats import ExponentialMovingCovariance as FastExponentialCoveriance
from runstats import ExponentialMovingStatistics as FastExponentialStatistics
from runstats import Regression as FastRegression
from runstats import Statistics as FastStatistics
from runstats.core import (
    ExponentialMovingCovariance as CoreExponentialCoveriance,
)
from runstats.core import (
    ExponentialMovingStatistics as CoreExponentialStatistics,
)
from runstats.core import Regression as CoreRegression
from runstats.core import Statistics as CoreStatistics
from tests.test_runstats import (
    exp_cov_cor,
    exp_mean_var,
    kurtosis,
    mean,
    skewness,
    stddev,
    variance,
)


def main():
    args = list(map(float, sys.argv[1:]))

    print('Statistics Functions')
    print('Count:', len(args))
    print('Mean:', mean(args))
    print('Variance:', variance(args))
    print('StdDev:', stddev(args))
    print('Skewness:', skewness(args))
    print('Kurtosis:', kurtosis(args))

    exp_mean, exp_var = exp_mean_var(0.9, args)
    exp_cov, exp_cor = exp_cov_cor(0.9, enumerate(args, 1))
    print('Exponential Moving Mean (decay=0.9):', exp_mean)
    print('Exponential Moving Variance (decay=0.9):', exp_var)
    print('Exponential Moving StdDev (decay=0.9):', exp_var ** 0.5)
    print('Exponential Moving Covariance (decay=0.9):', exp_cov)
    print('Exponential Moving Correlation (decay=0.9):', exp_cor)

    fast_stats = FastStatistics()

    for arg in args:
        fast_stats.push(arg)

    print()
    print('FastStatistics')
    print('Count:', len(fast_stats))
    print('Mean:', fast_stats.mean())
    print('Variance:', fast_stats.variance())
    print('StdDev:', fast_stats.stddev())
    print('Skewness:', fast_stats.skewness())
    print('Kurtosis:', fast_stats.kurtosis())

    core_stats = CoreStatistics()

    for arg in args:
        core_stats.push(arg)

    print()
    print('CoreStatistics')
    print('Count:', len(core_stats))
    print('Mean:', core_stats.mean())
    print('Variance:', core_stats.variance())
    print('StdDev:', core_stats.stddev())
    print('Skewness:', core_stats.skewness())
    print('Kurtosis:', core_stats.kurtosis())

    fast_exp_stats = FastExponentialStatistics()

    for arg in args:
        fast_exp_stats.push(arg)

    print()
    print('FastExponentialMovingStatistics')
    print('Decay Rate (default):', fast_exp_stats.decay)
    print('Exponential Mean:', fast_exp_stats.mean())
    print('Exponential Variance:', fast_exp_stats.variance())
    print('Exponential StdDev:', fast_exp_stats.stddev())

    core_exp_stats = CoreExponentialStatistics()

    for arg in args:
        core_exp_stats.push(arg)

    print()
    print('CoreExponentialMovingStatistics')
    print('Decay Rate (default):', core_exp_stats.decay)
    print('Exponential Mean:', core_exp_stats.mean())
    print('Exponential Variance:', core_exp_stats.variance())
    print('Exponential StdDev:', core_exp_stats.stddev())

    fast_regr = FastRegression()

    for index, arg in enumerate(args, 1):
        fast_regr.push(index, arg)

    print()
    print('FastRegression')
    print('Count:', len(fast_regr))
    print('Slope:', fast_regr.slope())
    print('Intercept:', fast_regr.intercept())
    print('Correlation:', fast_regr.correlation())

    core_regr = CoreRegression()

    for index, arg in enumerate(args, 1):
        core_regr.push(index, arg)

    print()
    print('CoreRegression')
    print('Count:', len(core_regr))
    print('Slope:', core_regr.slope())
    print('Intercept:', core_regr.intercept())
    print('Correlation:', core_regr.correlation())

    fast_exp_cov = FastExponentialCoveriance()

    for index, arg in enumerate(args, 1):
        fast_exp_cov.push(index, arg)

    print()
    print('FastExponentialCovariance')
    print('Decay Rate (default):', fast_exp_cov.decay)
    print('Exponential Moving Covariance:', fast_exp_cov.covariance())
    print('Exponential Moving Correlation:', fast_exp_cov.correlation())

    core_exp_cov = CoreExponentialCoveriance()

    for index, arg in enumerate(args, 1):
        core_exp_cov.push(index, arg)

    print()
    print('CoreExponentialCovariance')
    print('Decay Rate (default):', core_exp_cov.decay)
    print('Exponential Moving Covariance:', core_exp_cov.covariance())
    print('Exponential Moving Correlation:', core_exp_cov.correlation())


if __name__ == '__main__':
    main()
