"""Python RunStats

Compute Statistics and Regression in a single pass.

"""

from __future__ import division

class Statistics(object):
    """Compute statistics in a single pass.

    Computes the minimum, maximum, mean, variance, standard deviation,
    skewness, and kurtosis.
    Statistics objects may also be added together and copied.

    Based entirely on the C++ code by John D Cook at
    http://www.johndcook.com/skewness_kurtosis.html
    """
    def __init__(self, iterable=()):
        """Initialize Statistics object.

        Iterates optional parameter `iterable` and pushes each value into the
        statistics summary.
        """
        self.clear()

        for value in iterable:
            self.push(value)

    def clear(self):
        """Clear Statistics object."""
        self._count = self._eta = self._rho = self._tau = self._phi = 0.0
        self._min = self._max = float('nan')

    def __copy__(self):
        """Copy Statistics object."""
        that = Statistics()
        that._count = self._count
        that._min = self._min
        that._max = self._max
        that._eta = self._eta
        that._rho = self._rho
        that._tau = self._tau
        that._phi = self._phi
        return that

    copy = __copy__

    def __len__(self):
        """Number of values that have been pushed."""
        return int(self._count)

    def push(self, value):
        """Add `value` to the Statistics summary."""
        value = float(value)

        if self._count == 0.0:
            self._min = value
            self._max = value
        else:
            self._min = min(self._min, value)
            self._max = max(self._max, value)

        delta = value - self._eta
        delta_n = delta / (self._count + 1)
        delta_n2 = delta_n * delta_n
        term = delta * delta_n * self._count

        self._count += 1
        self._eta += delta_n
        self._phi += (
            term * delta_n2 * (self._count ** 2 - 3 * self._count + 3)
            + 6 * delta_n2 * self._rho
            - 4 * delta_n * self._tau
        )
        self._tau += (
            term * delta_n * (self._count - 2)
            - 3 * delta_n * self._rho
        )
        self._rho += term

    def minimum(self):
        """Minimum of values."""
        return self._min

    def maximum(self):
        """Maximum of values."""
        return self._max

    def mean(self):
        """Mean of values."""
        return self._eta

    def variance(self):
        """Variance of values."""
        return self._rho / (self._count - 1.0)

    def stddev(self):
        """Standard deviation of values."""
        return self.variance() ** 0.5

    def skewness(self):
        """Skewness of values."""
        return (self._count ** 0.5) * self._tau / pow(self._rho, 1.5)

    def kurtosis(self):
        """Kurtosis of values."""
        return self._count * self._phi / (self._rho * self._rho) - 3.0

    def __add__(self, that):
        """Add two Statistics objects together."""
        sigma = self.copy()
        sigma += that
        return sigma

    def __iadd__(self, that):
        """Add another Statistics object to this one."""
        sum_count = self._count + that._count

        delta = that._eta - self._eta
        delta2 = delta ** 2
        delta3 = delta ** 3
        delta4 = delta ** 4

        sum_eta = (
            (self._count * self._eta + that._count * that._eta)
            / sum_count
        )

        sum_rho = (
            self._rho + that._rho
            + delta2 * self._count * that._count / sum_count
        )

        sum_tau = (
            self._tau + that._tau
            + delta3 * self._count * that._count
            * (self._count - that._count) / (sum_count ** 2)
            + 3.0 * delta
            * (self._count * that._rho - that._count * self._rho) / sum_count
        )

        sum_phi = (
            self._phi + that._phi
            + delta4 * self._count * that._count
            * (self._count ** 2 - self._count * that._count + that._count ** 2)
            / (sum_count ** 3)
            + 6.0 * delta2 * (
                self._count * self._count * that._rho
                + that._count * that._count * self._rho
            )
            / (sum_count ** 2)
            + 4.0 * delta
            * (self._count * that._tau - that._count * self._tau) / sum_count
        )

        if self._count == 0.0:
            self._min = that._min
            self._max = that._max
        elif that._count == 0.0:
            pass  # self._min, self._max are unchanged.
        else:
            self._min = min(self._min, that._min)
            self._max = max(self._max, that._max)

        self._count = sum_count
        self._eta = sum_eta
        self._rho = sum_rho
        self._tau = sum_tau
        self._phi = sum_phi

        return self

class Regression(object):
    """
    Compute simple linear regression in a single pass.

    Computes the slope, intercept, and correlation.
    Regression objects may also be added together and copied.

    Based entirely on the C++ code by John D Cook at
    http://www.johndcook.com/running_regression.html
    """

    def __init__(self, iterable=()):
        """Initialize Regression object.

        Iterates optional parameter `iterable` and pushes each pair into the
        regression summary.
        """
        self._xstats = Statistics()
        self._ystats = Statistics()
        self.clear()

        for xcoord, ycoord in iterable:
            self.push(xcoord, ycoord)

    def clear(self):
        """Clear Regression object."""
        self._xstats.clear()
        self._ystats.clear()
        self._count = self._sxy = 0.0

    def __copy__(self):
        """Copy Regression object."""
        that = Regression()
        that._xstats = self._xstats.copy()
        that._ystats = self._ystats.copy()
        that._count, that._sxy = self._count, self._sxy
        return that

    copy = __copy__

    def __len__(self):
        """Number of values that have been pushed."""
        return int(self._count)

    def push(self, xcoord, ycoord):
        """Add a pair `(x, y)` to the Regression summary."""
        self._sxy += (
            (self._xstats.mean() - xcoord)
            * (self._ystats.mean() - ycoord)
            * self._count
            / (self._count + 1)
        )
        self._xstats.push(xcoord)
        self._ystats.push(ycoord)
        self._count += 1

    def slope(self):
        """Slope of values."""
        sxx = self._xstats.variance() * (self._count - 1)
        return self._sxy / sxx

    def intercept(self):
        """Intercept of values."""
        return self._ystats.mean() - self.slope() * self._xstats.mean()

    def correlation(self):
        """Correlation of values."""
        term = self._xstats.stddev() * self._ystats.stddev()
        return self._sxy / ((self._count - 1) * term)

    def __add__(self, that):
        """Add two Regression objects together."""
        sigma = self.copy()
        sigma += that
        return sigma

    def __iadd__(self, that):
        """Add another Regression object to this one."""
        sum_xstats = self._xstats + that._xstats
        sum_ystats = self._ystats + that._ystats
        sum_count = self._count + that._count

        deltax = that._xstats.mean() - self._xstats.mean()
        deltay = that._ystats.mean() - self._ystats.mean()
        sum_sxy = (
            self._sxy + that._sxy
            + self._count * that._count * deltax * deltay / sum_count
        )

        self._count = sum_count
        self._xstats = sum_xstats
        self._ystats = sum_ystats
        self._sxy = sum_sxy

        return self
