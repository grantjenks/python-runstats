# -*- coding: utf-8 -*-

import random
random.seed(0)

import nose
from nose.tools import raises

from .context import runstats
from runstats import Statistics, Regression

error_limit = 1e-2
count = 1000

def mean(values):
    return sum(values) / len(values)

def variance(values):
    temp = mean(values)
    return sum((value - temp) ** 2 for value in values) / len(values)

def stddev(values):
    return variance(values) ** 0.5

def skewness(values):
    temp = mean(values)
    numerator = sum((value - temp) ** 3 for value in values) / len(values)
    denominator = (sum((value - temp) ** 2 for value in values)
                   / len(values)) ** 1.5
    return numerator / denominator

def kurtosis(values):
    temp = mean(values)
    numerator = sum((value - temp) ** 4 for value in values) / len(values)
    denominator = (sum((value - temp) ** 2 for value in values) / len(values)) ** 2
    return (numerator / denominator) - 3

def error(value, test):
    return abs((test - value) / value)

def test_statistics():

    alpha = [random.random() for val in range(count)]

    alpha_stats = Statistics()
    for val in alpha:
        alpha_stats.push(val)

    assert len(alpha_stats) == count
    assert error(mean(alpha), alpha_stats.mean()) < error_limit
    assert error(variance(alpha), alpha_stats.variance()) < error_limit
    assert error(stddev(alpha), alpha_stats.stddev()) < error_limit
    assert error(skewness(alpha), alpha_stats.skewness()) < error_limit
    assert error(kurtosis(alpha), alpha_stats.kurtosis()) < error_limit
    assert alpha_stats.minimum() == min(alpha)
    assert alpha_stats.maximum() == max(alpha)

    alpha_stats.clear()

    assert len(alpha_stats) == 0

    alpha_stats = Statistics(alpha)

    beta = [random.random() for val in range(count)]

    beta_stats = Statistics()

    for val in beta:
        beta_stats.push(val)

    gamma_stats = alpha_stats + beta_stats

    assert len(beta_stats) != len(gamma_stats)
    assert error(mean(alpha + beta), gamma_stats.mean()) < error_limit
    assert error(variance(alpha + beta), gamma_stats.variance()) < error_limit
    assert error(stddev(alpha + beta), gamma_stats.stddev()) < error_limit
    assert error(skewness(alpha + beta), gamma_stats.skewness()) < error_limit
    assert error(kurtosis(alpha + beta), gamma_stats.kurtosis()) < error_limit
    assert gamma_stats.minimum() == min(alpha + beta)
    assert gamma_stats.maximum() == max(alpha + beta)

    delta_stats = beta_stats.copy()
    delta_stats += alpha_stats

    assert len(beta_stats) != len(delta_stats)
    assert error(mean(alpha + beta), delta_stats.mean()) < error_limit
    assert error(variance(alpha + beta), delta_stats.variance()) < error_limit
    assert error(stddev(alpha + beta), delta_stats.stddev()) < error_limit
    assert error(skewness(alpha + beta), delta_stats.skewness()) < error_limit
    assert error(kurtosis(alpha + beta), delta_stats.kurtosis()) < error_limit
    assert delta_stats.minimum() == min(alpha + beta)
    assert delta_stats.maximum() == max(alpha + beta)

def correlation(values):
    sigma_x = sum(xxx for xxx, yyy in values) / len(values)
    sigma_y = sum(yyy for xxx, yyy in values) / len(values)
    sigma_xy = sum(xxx * yyy for xxx, yyy in values) / len(values)
    sigma_x2 = sum(xxx ** 2 for xxx, yyy in values) / len(values)
    sigma_y2 = sum(yyy ** 2 for xxx, yyy in values) / len(values)
    return (sigma_xy - sigma_x * sigma_y) / (((sigma_x2 - sigma_x ** 2) * (sigma_y2 - sigma_y ** 2)) ** 0.5)

def test_regression():
    alpha, beta, rand = 5.0, 10.0, 20.0

    points = [(xxx, alpha * xxx + beta + rand * (0.5 - random.random()))
              for xxx in range(count)]

    regr = Regression()

    for xxx, yyy in points:
        regr.push(xxx, yyy)

    assert error(alpha, regr.slope()) < error_limit
    assert error(beta, regr.intercept()) < error_limit
    assert error(correlation(points), regr.correlation()) < error_limit

    regr_copy = regr.copy()

    more_points = [(xxx, alpha * xxx + beta + rand * (0.5 - random.random()))
                   for xxx in range(count, 2 * count)]

    for xxx, yyy in more_points:
        regr_copy.push(xxx, yyy)

    regr_more = Regression(more_points)

    regr_sum = regr + regr_more

    assert len(regr_copy) == len(regr_sum) == (2 * count)
    assert error(regr_copy.slope(), regr_sum.slope()) < error_limit
    assert error(regr_copy.intercept(), regr_sum.intercept()) < error_limit
    assert error(regr_copy.correlation(), regr_sum.correlation()) < error_limit

    regr += regr_more

    assert len(regr) == len(regr_copy) == (2 * count)
    assert error(regr.slope(), regr_copy.slope()) < error_limit
    assert error(regr.intercept(), regr_copy.intercept()) < error_limit
    assert error(regr.correlation(), regr_copy.correlation()) < error_limit

if __name__ == '__main__':
    nose.run()
