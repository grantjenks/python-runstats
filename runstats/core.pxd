import cython


cdef public double NAN


cdef class Statistics:

    cdef public double _count, _eta, _rho, _tau, _phi, _min, _max

    cpdef clear(self)

    cpdef get_state(self)

    cpdef set_state(self, state)

    cpdef __reduce__(self)

    cpdef Statistics copy(self, _=*)

    @cython.locals(
        delta=double,
        delta_n=double,
        delta_n2=double,
        term=double,
    )
    cpdef push(self, double value)

    cpdef double minimum(self)

    cpdef double maximum(self)

    cpdef double mean(self)

    cpdef double variance(self, double ddof=*)

    cpdef double stddev(self, double ddof=*)

    cpdef double skewness(self)

    cpdef double kurtosis(self)

    @cython.locals(sigma=Statistics)
    cpdef Statistics _add(self, Statistics that)

    @cython.locals(
        sum_count=double,
        delta=double,
        delta2=double,
        delta3=double,
        delta4=double,
        sum_eta=double,
        sum_rho=double,
        sum_tau=double,
        sum_phi=double,
    )
    cpdef Statistics _iadd(self, Statistics that)

    @cython.locals(sigma=Statistics)
    cpdef Statistics _mul(self, double that)

    cpdef Statistics _imul(self, double that)


cpdef Statistics make_statistics(state)


cdef class ExponentialMovingStatistics:
    cdef public double _decay, _mean, _variance, _initial_mean, _initial_variance, _delay, _time_diff, _current_time

    cpdef _set_decay(self, double value)

    cpdef _set_delay(self, double value)

    cpdef clear(self)

    cpdef get_state(self)

    cpdef set_state(self, state)

    cpdef __reduce__(self)

    cpdef ExponentialMovingStatistics copy(self, _=*)

    cpdef clear_timer(self)

    cpdef freeze(self)

    cpdef unfreeze(self)

    cpdef is_time_based(self)

    @cython.locals(
        alpha=double,
        diff=double,
        incr=double,
        norm_diff=double,
        decay=double,
        now=double
    )
    cpdef push(self, double value)

    cpdef double mean(self)

    cpdef double variance(self)

    cpdef double stddev(self)

    @cython.locals(sigma=ExponentialMovingStatistics)
    cpdef ExponentialMovingStatistics _add(self, ExponentialMovingStatistics that)

    cpdef ExponentialMovingStatistics _iadd(self, ExponentialMovingStatistics that)

    @cython.locals(
        sigma=ExponentialMovingStatistics,
    )
    cpdef ExponentialMovingStatistics _mul(self, double that)

    cpdef ExponentialMovingStatistics _imul(self, double that)


cpdef ExponentialMovingStatistics make_exponential_statistics(state)


cdef class Regression:
    cdef public Statistics _xstats, _ystats
    cdef public double _count, _sxy

    cpdef clear(self)

    cpdef get_state(self)

    cpdef set_state(self, state)

    cpdef __reduce__(self)

    cpdef Regression copy(self, _=*)

    cpdef push(self, double xcoord, double ycoord)

    @cython.locals(sxx=double)
    cpdef double slope(self, double ddof=*)

    cpdef double intercept(self, double ddof=*)

    @cython.locals(term=double)
    cpdef double correlation(self, double ddof=*)

    @cython.locals(sigma=Regression)
    cpdef Regression _add(self, Regression that)

    @cython.locals(
        sum_count=double,
        sum_xstats=Statistics,
        sum_ystats=Statistics,
        deltax=double,
        deltay=double,
        sum_sxy=double,
    )
    cpdef Regression _iadd(self, Regression that)


cpdef Regression make_regression(state)


cdef class ExponentialMovingCovariance:
    cdef public ExponentialMovingStatistics _xstats, _ystats
    cdef public double _decay, _initial_covariance, _covariance

    cpdef _set_decay(self, double value)

    cpdef clear(self)

    cpdef get_state(self)

    cpdef set_state(self, state)

    cpdef __reduce__(self)

    cpdef ExponentialMovingCovariance copy(self, _=*)

    @cython.locals(
        alpha=double
    )
    cpdef push(self, double x_val, double y_val)

    cpdef double covariance(self)

    @cython.locals(
        denom=double
    )
    cpdef double correlation(self)

    @cython.locals(sigma=ExponentialMovingCovariance)
    cpdef ExponentialMovingCovariance _add(self, ExponentialMovingCovariance that)

    cpdef ExponentialMovingCovariance _iadd(self, ExponentialMovingCovariance that)

    @cython.locals(
        sigma=ExponentialMovingCovariance,
    )
    cpdef ExponentialMovingCovariance _mul(self, double that)

    cpdef ExponentialMovingCovariance _imul(self, double that)


cpdef ExponentialMovingCovariance make_exponential_statistics(state)
