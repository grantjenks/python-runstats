"""
runstats - Module for computing statistics and regression in a single pass.

Written by Grant Jenks. Copyright (c) 2013.
This work may be used under the Apache2 License. See LICENSE file for details.

Based entirely on the C++ code by John D Cook at
* http://www.johndcook.com/skewness_kurtosis.html
* http://www.johndcook.com/running_regression.html

These methods are extremely useful for consuming values from generators
which may not all fit in memory.
"""

class Statistics:
    """
    Class for computing statistics in a single pass.

    Computes the mean, variance, stddev, skewness, and kurtosis.
    Statistics objects may also be added together and copied.
    """

    def __init__(self):
        self.clear()

    def clear(self):
        self._count = self._eta = self._rho = self._tau = self._phi = 0.0

    def copy(self):
        that = Statistics()
        that._count = self._count
        that._eta = self._eta
        that._rho = self._rho
        that._tau = self._tau
        that._phi = self._phi
        return that

    def __len__(self):
        """Number of values that have been pushed."""
        return int(self._count)

    def push(self, x):
        """Add a value to the Statistics summary."""
        delta = x - self._eta
        delta_n = delta / (self._count + 1)
        delta_n2 = delta_n * delta_n
        term = delta * delta_n * self._count
        self._count += 1
        self._eta += delta_n
        self._phi += term * delta_n2 * (self._count ** 2 - 3 * self._count + 3) \
                     + 6 * delta_n2 * self._rho \
                     - 4 * delta_n * self._tau
        self._tau += term * delta_n * (self._count - 2) \
                     - 3 * delta_n * self._rho;
        self._rho += term

    def mean(self):
        return self._eta

    def variance(self):
        return self._rho / (self._count - 1.0)

    def stddev(self):
        return self.variance() ** 0.5

    def skewness(self):
        return (self._count ** 0.5) * self._tau / pow(self._rho, 1.5)

    def kurtosis(self):
        return self._count * self._phi / (self._rho * self._rho) - 3.0

    def __add__(self, that):
        sigma = self.copy()
        sigma += that
        return sigma

    def __iadd__(self, that):
        sum_count = self._count + that._count

        delta = that._eta - self._eta
        delta2 = delta ** 2
        delta3 = delta ** 3
        delta4 = delta ** 4

        sum_eta = (self._count * self._eta + that._count * that._eta) / sum_count

        sum_rho = self._rho + that._rho \
            + delta2 * self._count * that._count / sum_count

        sum_tau = self._tau + that._tau \
            + delta3 * self._count * that._count * (self._count - that._count) / (sum_count ** 2) \
            + 3.0 * delta * (self._count * that._rho - that._count * self._rho) / sum_count

        sum_phi = self._phi + that._phi \
            + delta4 * self._count * that._count * (self._count ** 2 - self._count * that._count + that._count ** 2) / (sum_count ** 3) \
            + 6.0 * delta2 * (self._count * self._count * that._rho + that._count * that._count * self._rho) / (sum_count ** 2) \
            + 4.0 * delta * (self._count * that._tau - that._count * self._tau) / sum_count

        self._count = sum_count
        self._eta = sum_eta
        self._rho = sum_rho
        self._tau = sum_tau
        self._phi = sum_phi

        return self

class Regression:
    """
    Class for computing regression in a single pass.

    Computes the slope, intercept, and correlation.
    Regression objects may also be added together and copied.
    """

    def __init__(self):
        self._xstats = Statistics()
        self._ystats = Statistics()
        self.clear()

    def clear(self):
        self._xstats.clear()
        self._ystats.clear()
        self._count = self._sxy = 0.0

    def copy(self):
        that = Regression()
        that._xstats = self._xstats.copy()
        that._ystats = self._ystats.copy()
        that._count, that._sxy = self._count, self._sxy
        return that

    def __len__(self):
        """Number of values that have been pushed."""
        return int(self._count)

    def push(self, xcoord, ycoord):
        """Add a value to the Regression summary."""
        self._sxy += (self._xstats.mean() - xcoord) * (self._ystats.mean() - ycoord) * self._count / (self._count + 1)
        self._xstats.push(xcoord)
        self._ystats.push(ycoord)
        self._count += 1

    def slope(self):
        sxx = self._xstats.variance() * (self._count - 1)
        return self._sxy / sxx

    def intercept(self):
        return self._ystats.mean() - self.slope() * self._xstats.mean()

    def correlation(self):
        term = self._xstats.stddev() * self._ystats.stddev()
        return self._sxy / ((self._count - 1) * term)

    def __add__(self, that):
        sigma = self.copy()
        sigma += that
        return sigma

    def __iadd__(self, that):
        sum_xstats = self._xstats + that._xstats
        sum_ystats = self._ystats + that._ystats
        sum_count = self._count + that._count

        deltax = that._xstats.mean() - self._xstats.mean()
        deltay = that._ystats.mean() - self._ystats.mean()
        sum_sxy = self._sxy + that._sxy \
            + self._count * that._count * deltax * deltay / sum_count

        self._count = sum_count
        self._xstats = sum_xstats
        self._ystats = sum_ystats
        self._sxy = sum_sxy

        return self

__title__ = 'runstats'
__version__ = '0.0.1'
__build__ = 0x000001
__author__ = 'Grant Jenks'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright (c) 2013 Grant Jenks'
