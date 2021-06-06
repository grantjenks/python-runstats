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
        delta=float,
        delta_n=float,
        delta_n2=float,
        term=float,
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


cpdef Statistics make_statistics(state)


cdef class ExponentialStatistics:
    cdef public float _decay, _mean, _variance

    cpdef _set_decay(self, float value)

    cpdef clear(self, float mean=*, float variance=*, decay=*)

    cpdef get_state(self)

    cpdef set_state(self, state)

    cpdef __reduce__(self)

    cpdef ExponentialStatistics copy(self, _=*)

    @cython.locals(
        alpha=float,
        diff=float,
        incr=float,
    )
    cpdef push(self, float value)

    cpdef float mean(self)

    cpdef float variance(self)

    cpdef float stddev(self)

    @cython.locals(
        sigma=ExponentialStatistics,
    )
    cpdef ExponentialStatistics _add(self, ExponentialStatistics that)

    cpdef ExponentialStatistics _iadd(self, ExponentialStatistics that)

    @cython.locals(
        sigma=ExponentialStatistics,
    )
    cpdef ExponentialStatistics _mul(self, float that)

    cpdef ExponentialStatistics _imul(self, float that)


cpdef ExponentialStatistics make_exponential_statistics(state)


cdef class Regression:
    cdef public Statistics _xstats, _ystats
    cdef public float _count, _sxy

    cpdef clear(self)

    cpdef get_state(self)

    cpdef set_state(self, state)

    cpdef __reduce__(self)

    cpdef Regression copy(self, _=*)

    cpdef push(self, float xcoord, float ycoord)

    @cython.locals(sxx=float)
    cpdef float slope(self, float ddof=*)

    cpdef float intercept(self, float ddof=*)

    @cython.locals(term=float)
    cpdef float correlation(self, float ddof=*)

    @cython.locals(sigma=Regression)
    cpdef Regression _add(self, Regression that)

    @cython.locals(
        sum_count=float,
        sum_xstats=Statistics,
        sum_ystats=Statistics,
        deltax=float,
        deltay=float,
        sum_sxy=float,
    )
    cpdef Regression _iadd(self, Regression that)


cpdef Regression make_regression(state)
