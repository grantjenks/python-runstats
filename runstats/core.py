"""Python RunStats

Compute Statistics, Exponential Statistics and Regression in a single pass.

"""

from __future__ import division

NAN = float('nan')


class Statistics:
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
        self._min = self._max = NAN

    def __eq__(self, that):
        return self.get_state() == that.get_state()

    def __ne__(self, that):
        return self.get_state() != that.get_state()

    def get_state(self):
        """Get internal state."""
        return (
            self._count,
            self._eta,
            self._rho,
            self._tau,
            self._phi,
            self._min,
            self._max,
        )

    def set_state(self, state):
        """Set internal state."""
        (
            self._count,
            self._eta,
            self._rho,
            self._tau,
            self._phi,
            self._min,
            self._max,
        ) = state

    @classmethod
    def fromstate(cls, state):
        """Return Statistics object from state."""
        stats = cls()
        stats.set_state(state)
        return stats

    def __reduce__(self):
        return make_statistics, (self.get_state(),)

    def copy(self, _=None):
        """Copy Statistics object."""
        return self.fromstate(self.get_state())

    def __copy__(self, _=None):
        """Copy Statistics object."""
        return self.copy(_)

    __deepcopy__ = __copy__

    def __len__(self):
        """Number of values that have been pushed."""
        return int(self._count)

    def push(self, value):
        """Add `value` to the Statistics summary."""
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
            term * delta_n * (self._count - 2) - 3 * delta_n * self._rho
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

    def variance(self, ddof=1.0):
        """Variance of values (with `ddof` degrees of freedom)."""
        return self._rho / (self._count - ddof)

    def stddev(self, ddof=1.0):
        """Standard deviation of values (with `ddof` degrees of freedom)."""
        return self.variance(ddof) ** 0.5

    def skewness(self):
        """Skewness of values."""
        return (self._count ** 0.5) * self._tau / (self._rho ** 1.5)

    def kurtosis(self):
        """Kurtosis of values."""
        return self._count * self._phi / (self._rho * self._rho) - 3.0

    def _add(self, that):
        """Add two Statistics objects together."""
        sigma = self.copy()
        sigma._iadd(that)
        return sigma

    def __add__(self, that):
        """Add two Statistics objects together."""
        return self._add(that)

    def _iadd(self, that):
        """Add another Statistics object to this one."""
        sum_count = self._count + that._count
        if sum_count == 0:
            return self

        delta = that._eta - self._eta
        delta2 = delta ** 2
        delta3 = delta ** 3
        delta4 = delta ** 4

        sum_eta = (
            self._count * self._eta + that._count * that._eta
        ) / sum_count

        sum_rho = (
            self._rho
            + that._rho
            + delta2 * self._count * that._count / sum_count
        )

        sum_tau = (
            self._tau
            + that._tau
            + delta3
            * self._count
            * that._count
            * (self._count - that._count)
            / (sum_count ** 2)
            + 3.0
            * delta
            * (self._count * that._rho - that._count * self._rho)
            / sum_count
        )

        sum_phi = (
            self._phi
            + that._phi
            + delta4
            * self._count
            * that._count
            * (self._count ** 2 - self._count * that._count + that._count ** 2)
            / (sum_count ** 3)
            + 6.0
            * delta2
            * (
                self._count * self._count * that._rho
                + that._count * that._count * self._rho
            )
            / (sum_count ** 2)
            + 4.0
            * delta
            * (self._count * that._tau - that._count * self._tau)
            / sum_count
        )

        if self._count == 0.0:
            self._min = that._min
            self._max = that._max
        elif that._count != 0.0:
            self._min = min(self._min, that._min)
            self._max = max(self._max, that._max)

        self._count = sum_count
        self._eta = sum_eta
        self._rho = sum_rho
        self._tau = sum_tau
        self._phi = sum_phi

        return self

    def __iadd__(self, that):
        """Add another Statistics object to this one."""
        return self._iadd(that)

    def _mul(self, that):
        """Multiply by a scalar to change Statistics weighting."""
        sigma = self.copy()
        sigma._imul(that)
        return sigma

    def __mul__(self, that):
        """Multiply by a scalar to change Statistics weighting."""
        if isinstance(self, Statistics):
            return self._mul(that)
        # https://stackoverflow.com/q/33218006/232571
        return that._mul(self)  # pragma: no cover

    __rmul__ = __mul__

    def _imul(self, that):
        """Multiply by a scalar to change Statistics weighting in-place."""
        self._count *= that
        self._rho *= that
        self._tau *= that
        self._phi *= that
        return self

    def __imul__(self, that):
        """Multiply by a scalar to change Statistics weighting in-place."""
        return self._imul(that)


def make_statistics(state):
    """Make Statistics object from state."""
    return Statistics.fromstate(state)


class ExponentialStatistics:
    """Compute exponential mean and variance in a single pass.

    ExponentialStatistics objects may also be copied.

    Based on
    "Finch, 2009, Incremental Calculation of Weighted Mean and Variance" at
    https://nanopdf.com/download/incremental-calculation-of-weighted-mean-and-variance_pdf

    For an explanation of these statistics refer to e.g.:
    https://nestedsoftware.com/2018/04/04/exponential-moving-average-on-streaming-data-4hhl.24876.html

    """

    def __init__(self, decay=0.9, mean=0.0, variance=0.0, iterable=()):
        """Initialize ExponentialStatistics object.

        Incrementally tracks mean and variance and exponentially discounts old
        values.

        Requires a `decay` rate in exclusive range (0, 1) for discounting
        previous statistics.

        Optionally allows setting initial mean and variance. Default 0.

        Iterates optional parameter `iterable` and pushes each value into the
        statistics summary.

        """
        self.clear(mean, variance, decay)
        for value in iterable:
            self.push(value)

    @property
    def decay(self):
        """Exponential decay rate of old values."""
        return self._decay

    @decay.setter
    def decay(self, value):
        self._set_decay(value)

    def _set_decay(self, value):
        if not 0 <= value <= 1:
            raise ValueError('decay must be between 0 and 1')
        self._decay = value

    def clear(self, mean=0.0, variance=0.0, decay=None):
        """Clear ExponentialStatistics object."""
        self._mean = mean
        self._variance = variance
        if decay is not None:
            self._set_decay(decay)

    def __eq__(self, that):
        return self.get_state() == that.get_state()

    def __ne__(self, that):
        return self.get_state() != that.get_state()

    def get_state(self):
        """Get internal state."""
        return self._decay, self._mean, self._variance

    def set_state(self, state):
        """Set internal state."""
        (
            self._decay,
            self._mean,
            self._variance,
        ) = state

    @classmethod
    def fromstate(cls, state):
        """Return ExponentialStatistics object from state."""
        stats = cls()
        stats.set_state(state)
        return stats

    def __reduce__(self):
        return make_exponential_statistics, (self.get_state(),)

    def copy(self, _=None):
        """Copy ExponentialStatistics object."""
        return self.fromstate(self.get_state())

    def __copy__(self, _=None):
        """Copy ExponentialStatistics object."""
        return self.copy(_)

    __deepcopy__ = __copy__

    def push(self, value):
        """Add `value` to the ExponentialStatistics summary."""
        alpha = 1.0 - self._decay
        diff = value - self._mean
        incr = alpha * diff
        self._variance += alpha * (self._decay * diff ** 2 - self._variance)
        self._mean += incr

    def mean(self):
        """Exponential mean of values."""
        return self._mean

    def variance(self):
        """Exponential variance of values."""
        return self._variance

    def stddev(self):
        """Exponential standard deviation of values."""
        return self.variance() ** 0.5

    def _add(self, that):
        """Add two ExponentialStatistics objects together."""
        sigma = self.copy()
        sigma._iadd(that)
        return sigma

    def __add__(self, that):
        """Add two ExponentialStatistics objects together."""
        return self._add(that)

    def _iadd(self, that):
        """Add another ExponentialStatistics object to this one."""
        self._mean += that.mean()
        self._variance += that.variance()
        return self

    def __iadd__(self, that):
        """Add another ExponentialStatistics object to this one."""
        return self._iadd(that)

    def _mul(self, that):
        """Multiply by a scalar to change ExponentialStatistics weighting."""
        sigma = self.copy()
        sigma._imul(that)
        return sigma

    def __mul__(self, that):
        """Multiply by a scalar to change ExponentialStatistics weighting."""
        if isinstance(self, ExponentialStatistics):
            return self._mul(that)
        # https://stackoverflow.com/q/33218006/232571
        return that._mul(self)  # pragma: no cover

    def _imul(self, that):
        """Multiply by a scalar to change ExponentialStatistics weighting
        in-place.

        """
        self._mean *= that
        self._variance *= that
        return self

    def __imul__(self, that):
        """Multiply by a scalar to change ExponentialStatistics weighting
        in-place.

        """
        return self._imul(that)


def make_exponential_statistics(state):
    """Make ExponentialStatistics object from state."""
    return ExponentialStatistics.fromstate(state)


class Regression:
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
        self._count = self._sxy = 0.0

        for xcoord, ycoord in iterable:
            self.push(xcoord, ycoord)

    def __eq__(self, that):
        return self.get_state() == that.get_state()

    def __ne__(self, that):
        return self.get_state() != that.get_state()

    def clear(self):
        """Clear Regression object."""
        self._xstats.clear()
        self._ystats.clear()
        self._count = self._sxy = 0.0

    def get_state(self):
        """Get internal state."""
        return (
            self._count,
            self._sxy,
            self._xstats.get_state(),
            self._ystats.get_state(),
        )

    def set_state(self, state):
        """Set internal state."""
        count, sxy, xstats, ystats = state
        self._count = count
        self._sxy = sxy
        self._xstats.set_state(xstats)
        self._ystats.set_state(ystats)

    @classmethod
    def fromstate(cls, state):
        """Return Regression object from state."""
        regr = cls()
        regr.set_state(state)
        return regr

    def __reduce__(self):
        return make_regression, (self.get_state(),)

    def copy(self, _=None):
        """Copy Regression object."""
        return self.fromstate(self.get_state())

    def __copy__(self, _=None):
        """Copy Regression object."""
        return self.copy(_)

    __deepcopy__ = __copy__

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

    def slope(self, ddof=1.0):
        """Slope of values (with `ddof` degrees of freedom)."""
        sxx = self._xstats.variance(ddof) * (self._count - ddof)
        return self._sxy / sxx

    def intercept(self, ddof=1.0):
        """Intercept of values (with `ddof` degrees of freedom)."""
        return self._ystats.mean() - self.slope(ddof) * self._xstats.mean()

    def correlation(self, ddof=1.0):
        """Correlation of values (with `ddof` degrees of freedom)."""
        term = self._xstats.stddev(ddof) * self._ystats.stddev(ddof)
        return self._sxy / ((self._count - ddof) * term)

    def _add(self, that):
        """Add two Regression objects together."""
        sigma = self.copy()
        sigma._iadd(that)
        return sigma

    def __add__(self, that):
        """Add two Regression objects together."""
        return self._add(that)

    def _iadd(self, that):
        """Add another Regression object to this one."""
        sum_count = self._count + that._count
        if sum_count == 0:
            return self

        sum_xstats = self._xstats._add(that._xstats)
        sum_ystats = self._ystats._add(that._ystats)

        deltax = that._xstats.mean() - self._xstats.mean()
        deltay = that._ystats.mean() - self._ystats.mean()
        sum_sxy = (
            self._sxy
            + that._sxy
            + self._count * that._count * deltax * deltay / sum_count
        )

        self._count = sum_count
        self._xstats = sum_xstats
        self._ystats = sum_ystats
        self._sxy = sum_sxy

        return self

    def __iadd__(self, that):
        """Add another Regression object to this one."""
        return self._iadd(that)


def make_regression(state):
    """Make Regression object from state."""
    return Regression.fromstate(state)
