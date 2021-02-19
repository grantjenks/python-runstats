"""Test runstats module.

"""

import copy
import itertools
import math
import pickle
import random

import pytest

from runstats import ExponentialCovariance as FastExponentialCovariance
from runstats import ExponentialMovingStatistics as FastExponentialStatistics
from runstats import Regression as FastRegression
from runstats import Statistics as FastStatistics
from runstats.core import ExponentialCovariance as CoreExponentialCovariance
from runstats.core import (
    ExponentialMovingStatistics as CoreExponentialStatistics,
)
from runstats.core import Regression as CoreRegression
from runstats.core import Statistics as CoreStatistics

limit = 1e-2
count = 1000


def mean(values):
    return sum(values) / len(values)


def variance(values, ddof=1.0):
    temp = mean(values)
    return sum((value - temp) ** 2 for value in values) / (len(values) - ddof)


def stddev(values, ddof=1.0):
    return variance(values, ddof) ** 0.5


def skewness(values):
    temp = mean(values)
    numerator = sum((value - temp) ** 3 for value in values) / len(values)
    denominator = (
        sum((value - temp) ** 2 for value in values) / len(values)
    ) ** 1.5
    return numerator / denominator


def kurtosis(values):
    temp = mean(values)
    numerator = sum((value - temp) ** 4 for value in values) / len(values)
    sum_diff_2 = sum((value - temp) ** 2 for value in values)
    denominator = (sum_diff_2 / len(values)) ** 2
    return (numerator / denominator) - 3


def covariance(values):
    values = list(values)
    x_vals = [x for x, y in values]
    y_vals = [y for x, y in values]
    mean_x = mean(x_vals)
    mean_y = mean(y_vals)
    return sum((x - mean_x) * (y - mean_y) for x, y in values) / len(values)


def correlation(values):
    sigma_x = sum(xxx for xxx, yyy in values) / len(values)
    sigma_y = sum(yyy for xxx, yyy in values) / len(values)
    sigma_xy = sum(xxx * yyy for xxx, yyy in values) / len(values)
    sigma_x2 = sum(xxx ** 2 for xxx, yyy in values) / len(values)
    sigma_y2 = sum(yyy ** 2 for xxx, yyy in values) / len(values)
    return (sigma_xy - sigma_x * sigma_y) / (
        ((sigma_x2 - sigma_x ** 2) * (sigma_y2 - sigma_y ** 2)) ** 0.5
    )


def exponential_weight(decay, pos):
    return (1 - decay) * decay ** pos


def exp_mean_var(decay, iterable):
    indecies = list(range(len(iterable)))
    weights = list(map(lambda x: exponential_weight(decay, x), indecies))[::-1]

    mean = 0.0
    for val, weight in zip(iterable, weights):
        mean += val * weight

    variance = (0 - mean) ** 2 * (1 - sum(weights))
    for val, weight in zip(iterable, weights):
        variance += (val - mean) ** 2 * weight

    return mean, variance


def exp_cov_cor(decay, iterable):
    lst = list(iterable)
    indecies = list(range(len(lst)))
    weights = list(map(lambda x: exponential_weight(decay, x), indecies))[::-1]

    mean_1 = 0.0
    mean_2 = 0.0
    for vals, weight in zip(lst, weights):
        x_1, x_2 = vals
        mean_1 += x_1 * weight
        mean_2 += x_2 * weight

    variance_1 = (0 - mean_1) ** 2 * (1 - sum(weights))
    variance_2 = (0 - mean_2) ** 2 * (1 - sum(weights))
    for vals, weight in zip(lst, weights):
        x_1, x_2 = vals
        variance_1 += (x_1 - mean_1) ** 2 * weight
        variance_2 += (x_2 - mean_2) ** 2 * weight

    covar = (0 - mean_1) * (0 - mean_2) * (1 - sum(weights))
    for vals, weight in zip(lst, weights):
        x_1, x_2 = vals
        covar += (x_1 - mean_1) * (x_2 - mean_2) * weight

    correlation = covar / (variance_1 * variance_2) ** 0.5

    return covar, correlation


def error(value, test):
    return abs((test - value) / value)


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_statistics(Statistics, Regression):
    random.seed(0)
    alpha = [random.random() for _ in range(count)]

    alpha_stats = Statistics()

    for val in alpha:
        alpha_stats.push(val)

    assert len(alpha_stats) == count
    assert error(mean(alpha), alpha_stats.mean()) < limit
    assert error(variance(alpha, 0.0), alpha_stats.variance(0.0)) < limit
    assert error(variance(alpha, 1.0), alpha_stats.variance(1.0)) < limit
    assert error(stddev(alpha, 0.0), alpha_stats.stddev(0.0)) < limit
    assert error(stddev(alpha, 1.0), alpha_stats.stddev(1.0)) < limit
    assert error(skewness(alpha), alpha_stats.skewness()) < limit
    assert error(kurtosis(alpha), alpha_stats.kurtosis()) < limit
    assert alpha_stats.minimum() == min(alpha)
    assert alpha_stats.maximum() == max(alpha)

    alpha_stats.clear()

    assert len(alpha_stats) == 0

    alpha_stats = Statistics(alpha)

    beta = [random.random() for _ in range(count)]

    beta_stats = Statistics()

    for val in beta:
        beta_stats.push(val)

    gamma_stats = alpha_stats + beta_stats

    assert len(beta_stats) != len(gamma_stats)
    assert error(mean(alpha + beta), gamma_stats.mean()) < limit
    assert (
        error(variance(alpha + beta, 1.0), gamma_stats.variance(1.0)) < limit
    )
    assert (
        error(variance(alpha + beta, 0.0), gamma_stats.variance(0.0)) < limit
    )
    assert error(stddev(alpha + beta, 1.0), gamma_stats.stddev(1.0)) < limit
    assert error(stddev(alpha + beta, 0.0), gamma_stats.stddev(0.0)) < limit
    assert error(skewness(alpha + beta), gamma_stats.skewness()) < limit
    assert error(kurtosis(alpha + beta), gamma_stats.kurtosis()) < limit
    assert gamma_stats.minimum() == min(alpha + beta)
    assert gamma_stats.maximum() == max(alpha + beta)

    delta_stats = beta_stats.copy()
    delta_stats += alpha_stats

    assert len(beta_stats) != len(delta_stats)
    assert error(mean(alpha + beta), delta_stats.mean()) < limit
    assert (
        error(variance(alpha + beta, 1.0), delta_stats.variance(1.0)) < limit
    )
    assert (
        error(variance(alpha + beta, 0.0), delta_stats.variance(0.0)) < limit
    )
    assert error(stddev(alpha + beta, 1.0), delta_stats.stddev(1.0)) < limit
    assert error(stddev(alpha + beta, 0.0), delta_stats.stddev(0.0)) < limit
    assert error(skewness(alpha + beta), delta_stats.skewness()) < limit
    assert error(kurtosis(alpha + beta), delta_stats.kurtosis()) < limit
    assert delta_stats.minimum() == min(alpha + beta)
    assert delta_stats.maximum() == max(alpha + beta)


@pytest.mark.parametrize(
    'ExponentialMovingStatistics',
    [CoreExponentialStatistics, FastExponentialStatistics],
)
def test_exponential_statistics(ExponentialMovingStatistics):
    random.seed(0)
    alpha = [random.random() for _ in range(count)]
    big_alpha = [random.random() for _ in range(count * 100)]

    alpha_exp_stats_zero = ExponentialMovingStatistics(0.9999)
    alpha_exp_stats_init = ExponentialMovingStatistics(
        decay=0.9999,
        mean=mean(alpha),
        variance=variance(alpha, 0),
    )

    for val in big_alpha:
        alpha_exp_stats_zero.push(val)
        alpha_exp_stats_init.push(val)

    assert error(mean(big_alpha), alpha_exp_stats_zero.mean()) < limit
    assert error(mean(big_alpha), alpha_exp_stats_init.mean()) < limit
    assert (
        error(variance(big_alpha, 0), alpha_exp_stats_zero.variance()) < limit
    )
    assert (
        error(variance(big_alpha, 0), alpha_exp_stats_init.variance()) < limit
    )
    assert error(stddev(big_alpha, 0), alpha_exp_stats_zero.stddev()) < limit
    assert error(stddev(big_alpha, 0), alpha_exp_stats_init.stddev()) < limit

    alpha_exp_stats_zero.clear()
    alpha_exp_stats_zero.decay = 0.1
    alpha_exp_stats_init.clear()
    alpha_exp_stats_init.decay = 0.1

    for val in big_alpha:
        alpha_exp_stats_zero.push(val)
        alpha_exp_stats_init.push(val)

    assert (
        error(alpha_exp_stats_zero.mean(), alpha_exp_stats_init.mean()) < limit
    )
    assert (
        error(alpha_exp_stats_zero.variance(), alpha_exp_stats_init.variance())
        < limit
    )
    assert (
        error(alpha_exp_stats_zero.stddev(), alpha_exp_stats_init.stddev())
        < limit
    )

    alpha_exp_stats = ExponentialMovingStatistics(0.1, iterable=alpha)
    beta = [random.random() * 2 for _ in range(count)]
    beta_exp_stats = ExponentialMovingStatistics(0.1)

    assert alpha_exp_stats != beta_exp_stats

    for val in beta:
        alpha_exp_stats.push(val)
        beta_exp_stats.push(val)

    assert alpha_exp_stats == beta_exp_stats

    for val in alpha:
        alpha_exp_stats.push(val)
        beta_exp_stats.push(val)

    assert alpha_exp_stats == beta_exp_stats

    current_mean = alpha_exp_stats.mean()
    current_variance = alpha_exp_stats.variance()
    alpha_exp_stats.decay = 0.99999999

    for val in range(10):
        alpha_exp_stats.push(val)

    assert (error(current_mean, alpha_exp_stats.mean())) < limit
    assert (error(current_variance, alpha_exp_stats.variance())) < limit

    alpha_exp_stats.decay = 0.1

    for val in range(10):
        alpha_exp_stats.push(val)

    assert (error(current_mean, alpha_exp_stats.mean())) > limit
    assert (error(current_variance, alpha_exp_stats.variance())) > limit


@pytest.mark.parametrize(
    'ExponentialCovariance',
    [CoreExponentialCovariance, FastExponentialCovariance],
)
def test_exponential_covariance(ExponentialCovariance):
    random.seed(0)
    alpha = [random.random() for _ in range(count)]
    beta = [x * -10 for x in alpha]
    big_alpha = [random.random() for _ in range(count * 100)]
    big_beta = [x * -10 for x in big_alpha]
    data = list(zip(big_alpha, big_beta))

    exp_cov = ExponentialCovariance(
        decay=0.9999,
        mean_x=mean(alpha),
        variance_x=variance(alpha, 0),
        mean_y=mean(beta),
        variance_y=variance(beta),
        covariance=covariance(data),
    )

    for x, y in zip(big_alpha, big_beta):
        exp_cov.push(x, y)

    assert error(covariance(data), exp_cov.covariance()) < limit
    assert error(-1.0, exp_cov.correlation()) < limit

    exp_cov_2 = exp_cov.copy()
    assert exp_cov == exp_cov_2
    assert exp_cov.covariance() != covariance(data)
    exp_cov.clear()
    assert exp_cov != exp_cov_2
    assert exp_cov.covariance() == covariance(data)
    exp_cov_2.clear()
    exp_cov.decay = 0.1
    exp_cov_2.decay = 0.1
    assert exp_cov.decay == 0.1
    assert exp_cov == exp_cov_2

    exp_cov_3 = exp_cov * 0.5 + exp_cov * 0.5
    assert exp_cov_3 == exp_cov


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_add_statistics(Statistics, Regression):
    stats0 = Statistics()
    stats10 = Statistics(range(10))
    assert (stats0 + stats10) == stats10
    assert (stats10 + stats0) == stats10


@pytest.mark.parametrize(
    'ExponentialMovingStatistics',
    [CoreExponentialStatistics, FastExponentialStatistics],
)
def test_add_exponential_statistics(ExponentialMovingStatistics):
    exp_stats0 = ExponentialMovingStatistics(0.9)
    exp_stats10 = ExponentialMovingStatistics(0.9, iterable=range(10))
    assert (exp_stats0 + exp_stats10) == exp_stats10
    assert (exp_stats10 + exp_stats0) == exp_stats10


@pytest.mark.parametrize(
    'ExponentialCovariance',
    [CoreExponentialCovariance, FastExponentialCovariance],
)
def test_add_exponential_covariance(ExponentialCovariance):
    exp_cov0 = ExponentialCovariance(0.9)
    exp_cov10 = ExponentialCovariance(0.9, iterable=zip(range(10), range(10)))
    assert (exp_cov0 + exp_cov10) == exp_cov10
    assert (exp_cov10 + exp_cov0) == exp_cov10


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_regression(Statistics, Regression):
    random.seed(0)
    alpha, beta, rand = 5.0, 10.0, 1.0

    points = [
        (xxx, alpha * xxx + beta + rand * (0.5 - random.random()))
        for xxx in range(count)
    ]

    regr = Regression()

    for xxx, yyy in points:
        regr.push(xxx, yyy)

    assert error(alpha, regr.slope()) < limit
    assert error(beta, regr.intercept()) < limit
    assert error(correlation(points), regr.correlation()) < limit

    regr_copy = regr.copy()

    more_points = [
        (xxx, alpha * xxx + beta + rand * (0.5 - random.random()))
        for xxx in range(count, 2 * count)
    ]

    for xxx, yyy in more_points:
        regr_copy.push(xxx, yyy)

    regr_more = Regression(more_points)

    regr_sum = regr + regr_more

    assert len(regr_copy) == len(regr_sum) == (2 * count)
    assert error(regr_copy.slope(), regr_sum.slope()) < limit
    assert error(regr_copy.intercept(), regr_sum.intercept()) < limit
    assert error(regr_copy.correlation(), regr_sum.correlation()) < limit

    regr += regr_more

    assert len(regr) == len(regr_copy) == (2 * count)
    assert error(regr.slope(), regr_copy.slope()) < limit
    assert error(regr.intercept(), regr_copy.intercept()) < limit
    assert error(regr.correlation(), regr_copy.correlation()) < limit


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_get_set_state_statistics(Statistics, Regression):
    random.seed(0)
    tail = -10
    vals = [random.random() for _ in range(count)]

    stats = Statistics(vals[:tail])
    state = stats.get_state()

    for num in vals[tail:]:
        stats.push(num)

    new_stats = Statistics()
    new_stats.set_state(state)

    for num in vals[tail:]:
        new_stats.push(num)

    assert stats.mean() == new_stats.mean()
    assert stats.variance() == new_stats.variance()
    assert stats.minimum() == new_stats.minimum()
    assert stats.maximum() == new_stats.maximum()
    assert stats.kurtosis() == new_stats.kurtosis()
    assert stats.skewness() == new_stats.skewness()

    assert stats == Statistics.fromstate(stats.get_state())


@pytest.mark.parametrize(
    'ExponentialMovingStatistics',
    [CoreExponentialStatistics, FastExponentialStatistics],
)
def test_get_set_state_exponential_statistics(ExponentialMovingStatistics):
    random.seed(0)
    vals = [random.random() for _ in range(count)]
    exp_stats = ExponentialMovingStatistics(iterable=vals)
    exp_state = exp_stats.get_state()

    new_exp_stats = ExponentialMovingStatistics(0.8)
    assert exp_stats != new_exp_stats
    assert new_exp_stats.decay == 0.8
    new_exp_stats.set_state(exp_state)
    assert new_exp_stats.decay == 0.9
    assert exp_stats == new_exp_stats
    new_exp_stats.decay = 0.1
    assert exp_stats != new_exp_stats
    assert exp_stats.mean() == new_exp_stats.mean()
    assert exp_stats.variance() == new_exp_stats.variance()
    assert new_exp_stats.decay == 0.1

    assert exp_stats == ExponentialMovingStatistics.fromstate(
        exp_stats.get_state()
    )


@pytest.mark.parametrize(
    'ExponentialCovariance',
    [CoreExponentialCovariance, FastExponentialCovariance],
)
def test_get_set_state_exponential_covariance(ExponentialCovariance):
    random.seed(0)
    vals = [(random.random(), random.random()) for _ in range(count)]
    exp_cov = ExponentialCovariance(iterable=vals)
    exp_state = exp_cov.get_state()

    new_exp_cov = ExponentialCovariance(0.8)
    assert exp_cov != new_exp_cov
    assert new_exp_cov.decay == 0.8
    new_exp_cov.set_state(exp_state)
    assert new_exp_cov.decay == 0.9
    assert exp_cov == new_exp_cov
    new_exp_cov.decay = 0.1
    assert exp_cov != new_exp_cov
    assert exp_cov.covariance() == new_exp_cov.covariance()
    assert new_exp_cov.decay == 0.1

    assert exp_cov == ExponentialCovariance.fromstate(exp_cov.get_state())


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_get_set_state_regression(Statistics, Regression):
    random.seed(0)
    tail = -10
    alpha, beta, rand = 5.0, 10.0, 20.0
    points = [
        (xxx, alpha * xxx + beta + rand * (0.5 - random.random()))
        for xxx in range(count)
    ]

    regr = Regression(points[:tail])
    state = regr.get_state()

    for xxx, yyy in points[tail:]:
        regr.push(xxx, yyy)

    new_regr = Regression()
    new_regr.set_state(state)

    for xxx, yyy in points[tail:]:
        new_regr.push(xxx, yyy)

    assert regr.slope() == new_regr.slope()
    assert regr.intercept() == new_regr.intercept()
    assert regr.correlation() == new_regr.correlation()

    assert regr == Regression.fromstate(regr.get_state())


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_pickle_statistics(Statistics, Regression):
    stats = Statistics(range(10))
    for num in range(pickle.HIGHEST_PROTOCOL):
        pickled_stats = pickle.dumps(stats, protocol=num)
        unpickled_stats = pickle.loads(pickled_stats)
        assert stats == unpickled_stats, 'protocol: %s' % num


@pytest.mark.parametrize(
    'ExponentialMovingStatistics',
    [CoreExponentialStatistics, FastExponentialStatistics],
)
def test_pickle_exponential_statistics(ExponentialMovingStatistics):
    exp_stats = ExponentialMovingStatistics(0.9, iterable=range(10))
    for num in range(pickle.HIGHEST_PROTOCOL):
        pickled_exp_stats = pickle.dumps(exp_stats, protocol=num)
        unpickled_exp_stats = pickle.loads(pickled_exp_stats)
        assert exp_stats == unpickled_exp_stats, 'protocol: %s' % num


@pytest.mark.parametrize(
    'ExponentialCovariance',
    [CoreExponentialCovariance, FastExponentialCovariance],
)
def test_pickle_exponential_covariance(ExponentialCovariance):
    exp_cov = ExponentialCovariance(0.9, iterable=zip(range(10), range(10)))
    for num in range(pickle.HIGHEST_PROTOCOL):
        pickled_exp_cov = pickle.dumps(exp_cov, protocol=num)
        unpickled_exp_cov = pickle.loads(pickled_exp_cov)
        assert exp_cov == unpickled_exp_cov, 'protocol: %s' % num


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_pickle_regression(Statistics, Regression):
    regr = Regression(enumerate(range(10)))
    for num in range(pickle.HIGHEST_PROTOCOL):
        pickled_regr = pickle.dumps(regr, protocol=num)
        unpickled_regr = pickle.loads(pickled_regr)
        assert regr == unpickled_regr, 'protocol: %s' % num


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_copy_statistics(Statistics, Regression):
    stats = Statistics(range(10))
    copy_stats = copy.copy(stats)
    assert stats == copy_stats
    deepcopy_stats = copy.deepcopy(stats)
    assert stats == deepcopy_stats


@pytest.mark.parametrize(
    'ExponentialMovingStatistics',
    [CoreExponentialStatistics, FastExponentialStatistics],
)
def test_copy_exponential_statistics(ExponentialMovingStatistics):
    exp_stats = ExponentialMovingStatistics(0.9, iterable=range(10))
    copy_exp_stats = copy.copy(exp_stats)
    assert exp_stats == copy_exp_stats
    deepcopy_exp_stats = copy.deepcopy(exp_stats)
    assert exp_stats == deepcopy_exp_stats


@pytest.mark.parametrize(
    'ExponentialCovariance',
    [CoreExponentialCovariance, FastExponentialCovariance],
)
def test_copy_exponential_covariance(ExponentialCovariance):
    exp_cov = ExponentialCovariance(0.9, iterable=zip(range(10), range(10)))
    copy_exp_cov = copy.copy(exp_cov)
    assert exp_cov == copy_exp_cov
    deepcopy_exp_cov = copy.deepcopy(exp_cov)
    assert exp_cov == deepcopy_exp_cov


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_copy_regression(Statistics, Regression):
    regr = Regression(enumerate(range(10)))
    copy_regr = copy.copy(regr)
    assert regr == copy_regr
    deepcopy_regr = copy.deepcopy(regr)
    assert regr == deepcopy_regr


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_equality_statistics(Statistics, Regression):
    stats1 = Statistics(range(10))
    stats2 = Statistics(range(10))
    assert stats1 == stats2
    stats2.push(42)
    assert stats1 != stats2


@pytest.mark.parametrize(
    'ExponentialMovingStatistics',
    [CoreExponentialStatistics, FastExponentialStatistics],
)
def test_equality_exponential_statistics(ExponentialMovingStatistics):
    exp_stats1 = ExponentialMovingStatistics(0.9, iterable=range(10))
    exp_stats2 = ExponentialMovingStatistics(0.9, iterable=range(10))
    assert exp_stats1 == exp_stats2
    exp_stats2.push(42)
    assert exp_stats1 != exp_stats2


@pytest.mark.parametrize(
    'ExponentialCovariance',
    [CoreExponentialCovariance, FastExponentialCovariance],
)
def test_equality_exponential_covariance(ExponentialCovariance):
    exp_cov1 = ExponentialCovariance(0.9, iterable=enumerate(range(10)))
    exp_cov2 = ExponentialCovariance(0.9, iterable=enumerate(range(10)))
    assert exp_cov1 == exp_cov2
    exp_cov2.push(42, 42)
    assert exp_cov1 != exp_cov2


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_equality_regression(Statistics, Regression):
    regr1 = Regression(enumerate(range(10)))
    regr2 = Regression(enumerate(range(10)))
    assert regr1 == regr2
    regr2.push(42, 42)
    assert regr1 != regr2


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_sum_stats_count0(Statistics, Regression):
    stats1 = Statistics()
    stats2 = Statistics()
    sumstats = stats1 + stats2
    assert len(sumstats) == 0


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_sum_regr_count0(Statistics, Regression):
    regr1 = Regression()
    regr2 = Regression()
    sumregr = regr1 + regr2
    assert len(sumregr) == 0


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_multiply(Statistics, Regression):
    stats1 = Statistics(range(10))
    stats2 = Statistics(range(10)) * 2
    stats4 = 2 * stats2
    assert len(stats2) == 2 * len(stats1)
    assert len(stats4) == 2 * len(stats2)
    assert stats1.mean() == stats2.mean()
    assert stats1.mean() == stats4.mean()
    assert stats1.minimum() == stats2.minimum()
    assert stats1.maximum() == stats2.maximum()
    assert stats1.minimum() == stats4.minimum()
    assert stats1.maximum() == stats4.maximum()
    assert (stats1 + stats1).variance() == stats2.variance()
    assert (stats1 + stats1).kurtosis() == stats2.kurtosis()
    assert (stats1 + stats1).skewness() == stats2.skewness()
    assert (stats2 + stats2).variance() == stats4.variance()
    assert (stats2 + stats2).kurtosis() == stats4.kurtosis()
    assert (stats2 + stats2).skewness() == stats4.skewness()
    assert (2 * stats2) == stats4
    stats1 *= 4
    assert stats1 == stats4
    stats5 = math.e * stats1
    assert stats1.mean() == stats5.mean()


@pytest.mark.parametrize(
    'ExponentialMovingStatistics',
    [CoreExponentialStatistics, FastExponentialStatistics],
)
def test_exponential_statistics_batch(ExponentialMovingStatistics):
    random.seed(0)

    alpha = [random.random() for _ in range(count)]
    beta = [random.random() * 2 for _ in range(count)]

    alpha_exp_stats = ExponentialMovingStatistics(0.1, iterable=alpha)

    assert (alpha_exp_stats * 0.5 + alpha_exp_stats * 0.5) == alpha_exp_stats

    beta_exp_stats = ExponentialMovingStatistics(0.9, iterable=beta)

    gamma_exp_stats = alpha_exp_stats * 0.3 + beta_exp_stats * 0.7

    weighted_mean = alpha_exp_stats.mean() * 0.3 + beta_exp_stats.mean() * 0.7
    assert weighted_mean == gamma_exp_stats.mean()

    weighted_var = (
        alpha_exp_stats.variance() * 0.3 + beta_exp_stats.variance() * 0.7
    )
    assert weighted_var == gamma_exp_stats.variance()
    assert alpha_exp_stats._decay == gamma_exp_stats._decay
    assert beta_exp_stats._decay != gamma_exp_stats._decay


@pytest.mark.parametrize(
    'ExponentialCovariance',
    [CoreExponentialCovariance, FastExponentialCovariance],
)
def test_exponential_covariance_batch(ExponentialCovariance):
    random.seed(0)

    alpha = [(random.random(), random.random()) for _ in range(count)]
    beta = [(random.random() * 2, random.random() * 2) for _ in range(count)]

    alpha_exp_cov = ExponentialCovariance(0.1, iterable=alpha)

    assert (alpha_exp_cov * 0.5 + alpha_exp_cov * 0.5) == alpha_exp_cov

    beta_exp_cov = ExponentialCovariance(0.9, iterable=beta)

    gamma_exp_cov = alpha_exp_cov * 0.3 + beta_exp_cov * 0.7

    weighted_cov = (
        alpha_exp_cov.covariance() * 0.3 + beta_exp_cov.covariance() * 0.7
    )
    assert weighted_cov == gamma_exp_cov.covariance()

    assert alpha_exp_cov._decay == gamma_exp_cov._decay
    assert beta_exp_cov._decay != gamma_exp_cov._decay


@pytest.mark.parametrize(
    'ExponentialMovingStatistics, decay',
    list(
        itertools.product(
            [CoreExponentialStatistics, FastExponentialStatistics],
            [0.01, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99],
        )
    ),
)
def test_exponential_statistics_decays(ExponentialMovingStatistics, decay):
    random.seed(0)
    alpha = [random.random() for _ in range(count)]
    exp_stats = ExponentialMovingStatistics(decay=decay, iterable=alpha)
    true_mean, true_variance = exp_mean_var(decay=decay, iterable=alpha)

    assert (error(true_mean, exp_stats.mean())) < limit
    assert (error(true_mean, exp_stats.mean())) < limit


@pytest.mark.parametrize(
    'ExponentialCovariance, decay',
    list(
        itertools.product(
            [CoreExponentialCovariance, FastExponentialCovariance],
            [0.01, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99],
        )
    ),
)
def test_exponential_covariance_decays(ExponentialCovariance, decay):
    random.seed(0)
    alpha = [(random.random(), random.random()) for _ in range(count)]
    exp_stats = ExponentialCovariance(decay=decay, iterable=alpha)
    true_cov, true_cor = exp_cov_cor(decay=decay, iterable=alpha)

    assert (error(true_cov, exp_stats.covariance())) < limit
    assert (error(true_cor, exp_stats.correlation())) < limit


@pytest.mark.parametrize(
    'ExponentialMovingStatistics',
    [CoreExponentialStatistics, FastExponentialStatistics],
)
def test_exponential_statistics_clear(ExponentialMovingStatistics):
    random.seed(0)
    alpha = [random.random() for _ in range(count)]
    mean = 10
    variance = 100
    exp_stats = ExponentialMovingStatistics(mean=mean, variance=variance)

    for val in alpha:
        exp_stats.push(val)

    assert exp_stats.mean() != mean
    assert exp_stats.variance() != variance
    exp_stats.clear()
    assert exp_stats.mean() == mean
    assert exp_stats.variance() == variance


@pytest.mark.parametrize(
    'ExponentialCovariance',
    [CoreExponentialCovariance, FastExponentialCovariance],
)
def test_exponential_covariance_clear(ExponentialCovariance):
    random.seed(0)
    alpha = [(random.random(), random.random()) for _ in range(count)]
    mean_x = 10
    variance_x = 100
    mean_y = 1000
    variance_y = 2
    covariance = 20
    exp_cov = ExponentialCovariance(mean_x=mean_x, variance_x=variance_x, mean_y=mean_y, variance_y=variance_y, covariance=covariance)

    for x, y in alpha:
        exp_cov.push(x, y)

    assert exp_cov.covariance() != covariance
    assert exp_cov._xstats.mean() != mean_x
    assert exp_cov._xstats.variance() != variance_x
    assert exp_cov._ystats.mean() != mean_y
    assert exp_cov._ystats.variance() != variance_y
    exp_cov.clear()
    assert exp_cov.covariance() == covariance
    assert exp_cov._xstats.mean() == mean_x
    assert exp_cov._xstats.variance() == variance_x
    assert exp_cov._ystats.mean() == mean_y
    assert exp_cov._ystats.variance() == variance_y


@pytest.mark.parametrize(
    'Statistics,Regression',
    [
        (CoreStatistics, CoreRegression),
        (FastStatistics, FastRegression),
    ],
)
def test_raise_if_invalid_multiply(Statistics, Regression):
    stats1 = Statistics(range(10))
    stats2 = Statistics(range(10)) * 2
    with pytest.raises(TypeError):
        stats1 * stats2


@pytest.mark.parametrize(
    'ExponentialMovingStatistics',
    [CoreExponentialStatistics, FastExponentialStatistics],
)
def test_raise_if_invalid_decay_exp_stats(ExponentialMovingStatistics):
    with pytest.raises(ValueError):
        ExponentialMovingStatistics(0)
        ExponentialMovingStatistics(1)
        ExponentialMovingStatistics(-1)
        ExponentialMovingStatistics(2)


@pytest.mark.parametrize(
    'ExponentialCovariance',
    [CoreExponentialCovariance, FastExponentialCovariance],
)
def test_raise_if_invalid_decay_exp_cov(ExponentialCovariance):
    with pytest.raises(ValueError):
        ExponentialCovariance(0)
        ExponentialCovariance(1)
        ExponentialCovariance(-1)
        ExponentialCovariance(2)
