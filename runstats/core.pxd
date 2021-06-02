import cython

cdef public float NAN


cdef class Statistics:

    cdef public float _count, _eta, _rho, _tau, _phi, _min, _max

    cpdef clear(self)

    cpdef get_state(self)

    cpdef set_state(self, state)

    cpdef __reduce__(self)

    cpdef Statistics copy(self, _=*)

    @cython.locals(
        delta=cython.float,
        delta_n=cython.float,
        delta_n2=cython.float,
        term=cython.float,
    )
    cpdef push(self, float value)

    cpdef float minimum(self)

    cpdef float maximum(self)

    cpdef float mean(self)

    cpdef float variance(self, float ddof=*)

    cpdef float stddev(self, float ddof=*)

    cpdef float skewness(self)

    cpdef float kurtosis(self)

    @cython.locals(sigma=Statistics)
    cpdef Statistics _add(self, Statistics that)

    @cython.locals(
        sum_count=float,
        delta=float,
        delta2=float,
        delta3=float,
        delta4=float,
        sum_eta=float,
        sum_rho=float,
        sum_tau=float,
        sum_phi=float,
    )
    cpdef Statistics _iadd(self, Statistics that)

    @cython.locals(sigma=Statistics)
    cpdef Statistics _mul(self, float that)

    cpdef Statistics _imul(self, float that)


cpdef make_statistics(state)


# cdef class ExponentialStatistics:
#     cdef public float decay, mean, variance

#     @property
#     cpdef decay(self)

#     @decay.setter
#     cpdef decay(self, float value)

#     def clear(self, mean=0.0, variance=0.0, decay=None):
#         """Clear ExponentialStatistics object."""
#         self._mean = float(mean)
#         self._variance = float(variance)
#         if decay is not None:
#             self.decay = decay

#     def __eq__(self, that):
#         return self.get_state() == that.get_state()

#     def __ne__(self, that):
#         return self.get_state() != that.get_state()

#     def get_state(self):
#         """Get internal state."""
#         return self._decay, self._mean, self._variance

#     def set_state(self, state):
#         """Set internal state."""
#         (
#             self._decay,
#             self._mean,
#             self._variance,
#         ) = state

#     @classmethod
#     def fromstate(cls, state):
#         """Return ExponentialStatistics object from state."""
#         stats = cls()
#         stats.set_state(state)
#         return stats

#     def __reduce__(self):
#         return make_exponential_statistics, (self.get_state(),)

#     def copy(self, _=None):
#         """Copy ExponentialStatistics object."""
#         return self.fromstate(self.get_state())

#     __copy__ = copy
#     __deepcopy__ = copy

#     def push(self, value):
#         """Add `value` to the ExponentialStatistics summary."""
#         value = float(value)
#         alpha = 1.0 - self._decay
#         diff = value - self._mean
#         incr = alpha * diff
#         self._variance += alpha * (self._decay * diff ** 2 - self._variance)
#         self._mean += incr

#     def mean(self):
#         """Exponential mean of values."""
#         return self._mean

#     def variance(self):
#         """Exponential variance of values."""
#         return self._variance

#     def stddev(self):
#         """Exponential standard deviation of values."""
#         return self.variance() ** 0.5

#     def __add__(self, that):
#         """Add two ExponentialStatistics objects together."""
#         sigma = self.copy()
#         sigma += that
#         return sigma

#     def __iadd__(self, that):
#         """Add another ExponentialStatistics object to this one."""
#         self._mean += that.mean()
#         self._variance += that.variance()
#         return self

#     def __mul__(self, that):
#         """Multiply by a scalar to change ExponentialStatistics weighting."""
#         sigma = self.copy()
#         sigma *= that
#         return sigma

#     __rmul__ = __mul__

#     def __imul__(self, that):
#         """Multiply by a scalar to change ExponentialStatistics weighting
#         in-place.

#         """
#         that = float(that)
#         self._mean *= that
#         self._variance *= that
#         return self


# def make_exponential_statistics(state):
#     """Make ExponentialStatistics object from state."""
#     return ExponentialStatistics.fromstate(state)


# class Regression:
#     """
#     Compute simple linear regression in a single pass.

#     Computes the slope, intercept, and correlation.
#     Regression objects may also be added together and copied.

#     Based entirely on the C++ code by John D Cook at
#     http://www.johndcook.com/running_regression.html
#     """

#     def __init__(self, iterable=()):
#         """Initialize Regression object.

#         Iterates optional parameter `iterable` and pushes each pair into the
#         regression summary.
#         """
#         self._xstats = Statistics()
#         self._ystats = Statistics()
#         self._count = self._sxy = 0.0

#         for xcoord, ycoord in iterable:
#             self.push(xcoord, ycoord)

#     def __eq__(self, that):
#         return self.get_state() == that.get_state()

#     def __ne__(self, that):
#         return self.get_state() != that.get_state()

#     def clear(self):
#         """Clear Regression object."""
#         self._xstats.clear()
#         self._ystats.clear()
#         self._count = self._sxy = 0.0

#     def get_state(self):
#         """Get internal state."""
#         return (
#             self._count,
#             self._sxy,
#             self._xstats.get_state(),
#             self._ystats.get_state(),
#         )

#     def set_state(self, state):
#         """Set internal state."""
#         count, sxy, xstats, ystats = state
#         self._count = count
#         self._sxy = sxy
#         self._xstats.set_state(xstats)
#         self._ystats.set_state(ystats)

#     @classmethod
#     def fromstate(cls, state):
#         """Return Regression object from state."""
#         regr = cls()
#         regr.set_state(state)
#         return regr

#     def __reduce__(self):
#         return make_regression, (self.get_state(),)

#     def copy(self, _=None):
#         """Copy Regression object."""
#         return self.fromstate(self.get_state())

#     __copy__ = copy
#     __deepcopy__ = copy

#     def __len__(self):
#         """Number of values that have been pushed."""
#         return int(self._count)

#     def push(self, xcoord, ycoord):
#         """Add a pair `(x, y)` to the Regression summary."""
#         self._sxy += (
#             (self._xstats.mean() - xcoord)
#             * (self._ystats.mean() - ycoord)
#             * self._count
#             / (self._count + 1)
#         )
#         self._xstats.push(xcoord)
#         self._ystats.push(ycoord)
#         self._count += 1

#     def slope(self, ddof=1.0):
#         """Slope of values (with `ddof` degrees of freedom)."""
#         sxx = self._xstats.variance(ddof) * (self._count - ddof)
#         return self._sxy / sxx

#     def intercept(self, ddof=1.0):
#         """Intercept of values (with `ddof` degrees of freedom)."""
#         return self._ystats.mean() - self.slope(ddof) * self._xstats.mean()

#     def correlation(self, ddof=1.0):
#         """Correlation of values (with `ddof` degrees of freedom)."""
#         term = self._xstats.stddev(ddof) * self._ystats.stddev(ddof)
#         return self._sxy / ((self._count - ddof) * term)

#     def __add__(self, that):
#         """Add two Regression objects together."""
#         sigma = self.copy()
#         sigma += that
#         return sigma

#     def __iadd__(self, that):
#         """Add another Regression object to this one."""
#         sum_count = self._count + that._count
#         if sum_count == 0:
#             return self

#         sum_xstats = self._xstats + that._xstats
#         sum_ystats = self._ystats + that._ystats

#         deltax = that._xstats.mean() - self._xstats.mean()
#         deltay = that._ystats.mean() - self._ystats.mean()
#         sum_sxy = (
#             self._sxy
#             + that._sxy
#             + self._count * that._count * deltax * deltay / sum_count
#         )

#         self._count = sum_count
#         self._xstats = sum_xstats
#         self._ystats = sum_ystats
#         self._sxy = sum_sxy

#         return self


# def make_regression(state):
#     """Make Regression object from state."""
#     return Regression.fromstate(state)
