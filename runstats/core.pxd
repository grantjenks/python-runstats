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


cdef class ExponentialStatistics:
    cdef public double _decay, _mean, _variance

    cpdef _set_decay(self, double value)

    cpdef clear(self, double mean=*, double variance=*, decay=*)

    cpdef get_state(self)

    cpdef set_state(self, state)

    cpdef __reduce__(self)

    cpdef ExponentialStatistics copy(self, _=*)

    @cython.locals(
        alpha=double,
        diff=double,
        incr=double,
    )
    cpdef push(self, double value)

    cpdef double mean(self)

    cpdef double variance(self)

    cpdef double stddev(self)

    @cython.locals(
        sigma=ExponentialStatistics,
    )
    cpdef ExponentialStatistics _add(self, ExponentialStatistics that)

    cpdef ExponentialStatistics _iadd(self, ExponentialStatistics that)

    @cython.locals(
        sigma=ExponentialStatistics,
    )
    cpdef ExponentialStatistics _mul(self, double that)

    cpdef ExponentialStatistics _imul(self, double that)


cpdef ExponentialStatistics make_exponential_statistics(state)


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
