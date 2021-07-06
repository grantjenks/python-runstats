"""Python RunStats

Compute Statistics, Exponential Statistics, Regression and Exponential
Covariance in a single pass.

"""

from __future__ import division

import time
from math import isnan

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


class ExponentialMovingStatistics:
    # pylint: disable=too-many-instance-attributes
    """Compute exponential mean and variance in a single pass.

    ExponentialMovingStatistics objects may also be added and copied.

    Based on
    "Finch, 2009, Incremental Calculation of Weighted Mean and Variance" at
    https://nanopdf.com/download/incremental-calculation-of-weighted-mean-and-variance_pdf

    For an explanation of these statistics refer to e.g.:
    https://nestedsoftware.com/2018/04/04/exponential-moving-average-on-streaming-data-4hhl.24876.html

    """

    def __init__(
        self, decay=0.9, mean=0.0, variance=0.0, delay=None, iterable=()
    ):  # pylint: disable=too-many-arguments
        """Initialize ExponentialMovingStatistics object.

        Incrementally tracks mean and variance and exponentially discounts old
        values.

        Requires a `decay` rate in exclusive range (0, 1) for discounting
        previous statistics. Default 0.9

        Optionally allows setting initial mean and variance. Default 0.

        Iterates optional parameter `iterable` and pushes each value into the
        statistics summary.

        Can discount values based on time passed instead of position if 'delay' is
        set. Setting delay (in seconds) computes a dynamic
        decay rate each time a value is pushed:
        dynamic_decay = decay ** (sec_from_last_push / delay).
        When the first value x is pushed, sec_from_last_push is the difference
        (in sec) between setting the delay from None to a value t (usually at
        object construction) and the times when x is being pushed.
        When freeze() has been called sec_from_last_push is the difference
        between the last call to push() and the time freeze() has been
        called().
        Note that at object initialization the values in iterable are weighted
        as if delay has not been set.
        """
        self.decay = decay
        self._initial_mean = mean
        self._initial_variance = variance
        self._mean = self._initial_mean
        self._variance = self._initial_variance

        # using float('nan') for cython compatibility
        self._current_time = NAN
        self._time_diff = NAN
        self.delay = NAN

        for value in iterable:
            self.push(value)

        self.delay = delay

    @property
    def decay(self):
        """Exponential decay rate of old values."""
        return self._decay

    @decay.setter
    def decay(self, value):
        self._set_decay(value)

    def _set_decay(self, value):
        if not 0 < value < 1:
            raise ValueError('decay must be between 0 and 1')
        self._decay = value

    @property
    def delay(self):
        """Delay in sec for time based discounting"""
        return self._delay

    @delay.setter
    def delay(self, value):
        self._set_delay(value)

    def _set_delay(self, value):
        value = NAN if value is None else value
        if not isnan(value):
            if value <= 0.0:
                raise ValueError('delay must be > 0')
            self._current_time = (
                self._current_time
                if not isnan(self._current_time)
                else time.time()
            )
        else:
            self._current_time = NAN
            self._time_diff = NAN

        self._delay = value

    def clear(self):
        """Clear ExponentialMovingStatistics object."""
        self._mean = self._initial_mean
        self._variance = self._initial_variance
        self._current_time = time.time() if self.is_time_based() else NAN
        self._time_diff = NAN

    def __eq__(self, that):
        return self.get_state() == that.get_state()

    def __ne__(self, that):
        return self.get_state() != that.get_state()

    def get_state(self):
        """Get internal state."""
        state = [
            self._decay,
            self._initial_mean,
            self._initial_variance,
            self._mean,
            self._variance,
            self._delay,
            self._current_time,
            self._time_diff,
        ]
        state = [None if isnan(i) else i for i in state]
        return tuple(state)

    def set_state(self, state):
        """Set internal state."""
        state = list(state)
        state = [NAN if i is None else i for i in state]

        (
            self._decay,
            self._initial_mean,
            self._initial_variance,
            self._mean,
            self._variance,
            self._delay,
            self._current_time,
            self._time_diff,
        ) = state

    @classmethod
    def fromstate(cls, state):
        """Return ExponentialMovingStatistics object from state."""
        stats = cls()
        stats.set_state(state)
        return stats

    def __reduce__(self):
        return make_exponential_statistics, (self.get_state(),)

    def copy(self, _=None):
        """Copy ExponentialMovingStatistics object."""
        return self.fromstate(self.get_state())

    def __copy__(self, _=None):
        """Copy ExponentialMovingStatistics object."""
        return self.copy(_)

    __deepcopy__ = __copy__

    def clear_timer(self):
        """Reset time counter"""
        if self.is_time_based():
            self._current_time = time.time()
            self._time_diff = NAN
        else:
            raise AttributeError(
                'clear_timer on a non-time time based (i.e. delay == None) '
                'ExponentialMovingStatistics object is illegal'
            )

    def freeze(self):
        """Freeze time i.e. save the difference between now and the last push"""
        if self.is_time_based():
            self._time_diff = time.time() - self._current_time
        else:
            raise AttributeError(
                'freeze on a non-time time based (i.e. delay == None) '
                'ExponentialMovingStatistics object is illegal'
            )

    def unfreeze(self):
        """Unfreeze time i.e. continue counting the time difference"""
        if not self.is_time_based():
            raise AttributeError(
                'unfreeze on a non-time time based (i.e. delay == None) '
                'ExponentialMovingStatistics object is illegal'
            )

        if isnan(self._time_diff):
            raise AttributeError(
                'Time must be freezed first before it can be unfreezed'
            )

        self._current_time = time.time() - self._time_diff
        self._time_diff = NAN

    def is_time_based(self):
        """Checks if object is time-based or not i.e. delay is set or None"""
        return not isnan(self.delay)

    def push(self, value):
        """Add `value` to the ExponentialMovingStatistics summary."""
        if self.is_time_based():
            now = time.time()
            diff = (
                self._time_diff
                if not isnan(self._time_diff)
                else (now - self._current_time)
            )
            norm_diff = diff / self.delay
            decay = self.decay ** norm_diff
            self._current_time = now
        else:
            decay = self.decay

        alpha = 1.0 - decay
        diff = value - self._mean
        incr = alpha * diff
        self._variance += alpha * (decay * diff ** 2 - self._variance)
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
        """Add two ExponentialMovingStatistics objects together."""
        sigma = self.copy()
        sigma._iadd(that)

        if sigma.is_time_based():
            sigma.clear_timer()

        return sigma

    def __add__(self, that):
        """Add two ExponentialMovingStatistics objects together."""
        return self._add(that)

    def _iadd(self, that):
        """Add another ExponentialMovingStatistics object to this one."""
        self._mean += that.mean()
        self._variance += that.variance()
        return self

    def __iadd__(self, that):
        """Add another ExponentialMovingStatistics object to this one."""
        return self._iadd(that)

    def _mul(self, that):
        """Multiply by a scalar to change ExponentialMovingStatistics weighting."""
        sigma = self.copy()
        sigma._imul(that)
        return sigma

    def __mul__(self, that):
        """Multiply by a scalar to change ExponentialMovingStatistics weighting."""
        if isinstance(self, ExponentialMovingStatistics):
            return self._mul(that)
        # https://stackoverflow.com/q/33218006/232571
        return that._mul(self)  # pragma: no cover

    __rmul__ = __mul__

    def _imul(self, that):
        """Multiply by a scalar to change ExponentialMovingStatistics weighting
        in-place.

        """
        self._mean *= that
        self._variance *= that
        return self

    def __imul__(self, that):
        """Multiply by a scalar to change ExponentialMovingStatistics weighting
        in-place.

        """
        return self._imul(that)


def make_exponential_statistics(state):
    """Make ExponentialMovingStatistics object from state."""
    return ExponentialMovingStatistics.fromstate(state)


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


class ExponentialMovingCovariance:
    """Compute exponential moving covariance and correlation in a single pass.

    ExponentialMovingCovariance objects may also be added and copied.

    """

    def __init__(
        self,
        decay=0.9,
        mean_x=0.0,
        variance_x=0.0,
        mean_y=0.0,
        variance_y=0.0,
        covariance=0.0,
        iterable=(),
    ):  # pylint: disable=too-many-arguments
        """Initialize ExponentialMovingCovariance object.

        Incrementally tracks covariance and exponentially discounts old
        values.

        Requires a `decay` rate in exclusive range (0, 1) for discounting
        previous statistics.

        Optionally allows setting initial covariance. Default 0.

        Iterates optional parameter `iterable` and pushes each pair into the
        statistics summary.

        """
        self._initial_covariance = covariance
        self._covariance = self._initial_covariance
        self._xstats = ExponentialMovingStatistics(
            decay=decay, mean=mean_x, variance=variance_x
        )
        self._ystats = ExponentialMovingStatistics(
            decay=decay, mean=mean_y, variance=variance_y
        )
        self.decay = decay

        for x_val, y_val in iterable:
            self.push(x_val, y_val)

    @property
    def decay(self):
        """Decay rate for old values."""
        return self._decay

    @decay.setter
    def decay(self, value):
        self._set_decay(value)

    def _set_decay(self, value):
        self._xstats.decay = value
        self._ystats.decay = value
        self._decay = value

    def clear(self):
        """Clear ExponentialMovingCovariance object."""
        self._xstats.clear()
        self._ystats.clear()
        self._covariance = self._initial_covariance

    def __eq__(self, that):
        return self.get_state() == that.get_state()

    def __ne__(self, that):
        return self.get_state() != that.get_state()

    def get_state(self):
        """Get internal state."""
        return (
            self._decay,
            self._initial_covariance,
            self._covariance,
            self._xstats.get_state(),
            self._ystats.get_state(),
        )

    def set_state(self, state):
        """Set internal state."""
        decay, initial_covariance, covariance, xstate, ystate = state
        self._decay = decay
        self._initial_covariance = initial_covariance
        self._covariance = covariance
        self._xstats.set_state(xstate)
        self._ystats.set_state(ystate)

    @classmethod
    def fromstate(cls, state):
        """Return ExponentialMovingCovariance object from state."""
        stats = cls()
        stats.set_state(state)
        return stats

    def __reduce__(self):
        return make_exponential_covariance, (self.get_state(),)

    def copy(self, _=None):
        """Copy ExponentialMovingCovariance object."""
        return self.fromstate(self.get_state())

    def __copy__(self, _=None):
        """Copy ExponentialMovingCovariance object."""
        return self.copy(_)

    __deepcopy__ = __copy__

    def push(self, x_val, y_val):
        """Add a pair `(x, y)` to the ExponentialMovingCovariance summary."""
        self._xstats.push(x_val)
        alpha = 1.0 - self.decay
        self._covariance = self.decay * self.covariance() + alpha * (
            x_val - self._xstats.mean()
        ) * (y_val - self._ystats.mean())
        self._ystats.push(y_val)

    def covariance(self):
        """Covariance of values"""
        return self._covariance

    def correlation(self):
        """Correlation of values"""
        denom = self._xstats.stddev() * self._ystats.stddev()
        return self.covariance() / denom

    def _add(self, that):
        """Add two ExponentialMovingCovariance objects together."""
        sigma = self.copy()
        sigma._iadd(that)
        return sigma

    def __add__(self, that):
        """Add two ExponentialMovingCovariance objects together."""
        return self._add(that)

    def _iadd(self, that):
        """Add another ExponentialMovingCovariance object to this one."""
        self._xstats += that._xstats
        self._ystats += that._ystats
        self._covariance += that.covariance()
        return self

    def __iadd__(self, that):
        """Add another ExponentialMovingCovariance object to this one."""
        return self._iadd(that)

    def _mul(self, that):
        """Multiply by a scalar to change ExponentialMovingCovariance weighting."""
        sigma = self.copy()
        sigma._imul(that)
        return sigma

    def __mul__(self, that):
        """Multiply by a scalar to change ExponentialMovingCovariance weighting."""
        if isinstance(self, ExponentialMovingCovariance):
            return self._mul(that)
        # https://stackoverflow.com/q/33218006/232571
        return that._mul(self)  # pragma: no cover

    __rmul__ = __mul__

    def _imul(self, that):
        """Multiply by a scalar to change ExponentialMovingCovariance weighting
        in-place.

        """
        that = float(that)
        self._xstats *= that
        self._ystats *= that
        self._covariance *= that
        return self

    def __imul__(self, that):
        """Multiply by a scalar to change ExponentialMovingCovariance weighting
        in-place.

        """
        return self._imul(that)


def make_exponential_covariance(state):
    """Make ExponentialMovingCovariance object from state."""
    return ExponentialMovingCovariance.fromstate(state)
