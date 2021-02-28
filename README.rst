RunStats: Computing Statistics and Regression in One Pass
=========================================================

`RunStats`_ is an Apache2 licensed Python module for online statistics and
online regression. Statistics and regression summaries are computed in a single
pass. Previous values are not recorded in summaries.

Long running systems often generate numbers summarizing performance. It could
be the latency of a response or the time between requests. It's often useful to
use these numbers in summary statistics like the arithmetic mean, minimum,
standard deviation, etc. When many values are generated, computing these
summaries can be computationally intensive. It may even be infeasible to keep
every recorded value. In such cases computing online statistics and online
regression is necessary.

In other cases, you may only have one opportunity to observe all the recorded
values. Python's generators work exactly this way. Traditional methods for
calculating the variance and other higher moments requires multiple passes over
the data. With generators, this is not possible and so computing statistics in
a single pass is necessary.

There are also scenarios where a user is not interested in a complete summary
of the entire stream of data but rather wants to observe the current state of
the system based on the recent past. In these cases exponential statistics are
used. Instead of weighting all values uniformly in the statistics computation,
an exponential decay weight is applied to older values. The decay rate is
configurable and provides a mechanism for balancing recent values with past
values.

The Python `RunStats`_ module was designed for these cases by providing classes
for computing online summary statistics and online linear regression in a
single pass. Summary objects work on sequences which may be larger than memory
or disk space permit. They may also be efficiently combined together to create
aggregate summaries.


Features
--------

- Pure-Python
- Fully Documented
- 100% Test Coverage
- Numerically Stable
- Optional Cython-optimized Extension (20-40 times faster)
- Statistics summary computes mean, variance, standard deviation, skewness,
  kurtosis, minimum and maximum.
- Regression summary computes slope, intercept and correlation.
- Developed on Python 3.9
- Tested on CPython 3.6, 3.7, 3.8, 3.9
- Tested on Linux, Mac OS X, and Windows
- Tested using GitHub Actions

.. image:: https://github.com/grantjenks/python-runstats/workflows/integration/badge.svg
   :target: http://www.grantjenks.com/docs/runstats/


Quickstart
----------

Installing `RunStats`_ is simple with `pip <http://www.pip-installer.org/>`_::

  $ pip install runstats

If you want the Cython-optimized version then first install `Cython
<http://cython.org/>`_::

  $ pip install cython
  $ pip install runstats

You can access documentation in the interpreter with Python's built-in help
function:

.. code-block:: python

   >>> import runstats
   >>> help(runstats)                             # doctest: +SKIP
   >>> help(runstats.Statistics)                  # doctest: +SKIP
   >>> help(runstats.Regression)                  # doctest: +SKIP
   >>> help(runstats.ExponentialMovingStatistics)       # doctest: +SKIP


Tutorial
--------

The Python `RunStats`_ module provides four types for computing running
statistics: Statistics, ExponentialMovingStatistics,
ExponentialMovingCovariance and Regression.
The Regression object leverages Statistics internally for its calculations.
Each can be initialized without arguments:

.. code-block:: python

   >>> from runstats import Statistics, Regression, ExponentialMovingStatistics, ExponentialMovingCovariance
   >>> stats = Statistics()
   >>> regr = Regression()
   >>> exp_stats = ExponentialMovingStatistics()
   >>> exp_cov = ExponentialMovingCovariance()

Statistics objects support four methods for modification. Use `push` to add
values to the summary, `clear` to reset the the object to its initialization
state, sum to combine Statistics summaries and multiply to weight summary
Statistics by a scalar.

.. code-block:: python

   >>> for num in range(10):
   ...     stats.push(num)
   >>> stats.mean()
   4.5
   >>> stats.maximum()
   9.0
   >>> stats += stats
   >>> stats.mean()
   4.5
   >>> stats.variance()
   8.68421052631579
   >>> len(stats)
   20
   >>> stats *= 2
   >>> len(stats)
   40
   >>> stats.clear()
   >>> len(stats)
   0
   >>> stats.minimum()
   nan

Use the Python built-in `len` for the number of pushed values. Unfortunately
the Python `min` and `max` built-ins may not be used for the minimum and
maximum as sequences are expected instead. Therefore, there are `minimum` and
`maximum` methods provided for that purpose:

.. code-block:: python

   >>> import random
   >>> random.seed(0)
   >>> for __ in range(1000):
   ...     stats.push(random.random())
   >>> len(stats)
   1000
   >>> min(stats)
   Traceback (most recent call last):
       ...
   TypeError: 'Statistics' object is not iterable
   >>> stats.minimum()
   0.00024069652516689466
   >>> stats.maximum()
   0.9996851255769114

Statistics summaries provide five measures of a series: mean, variance,
standard deviation, skewness and kurtosis:

.. code-block:: python

   >>> stats = Statistics([1, 2, 5, 12, 5, 2, 1])
   >>> stats.mean()
   4.0
   >>> stats.variance()
   15.33333333333333
   >>> stats.stddev()
   3.915780041490243
   >>> stats.skewness()
   1.33122127314735
   >>> stats.kurtosis()
   0.5496219281663506

All internal calculations use Python's `float` type.

Like Statistics, the Regression type supports some methods for modification:
`push`, `clear` and sum:

.. code-block:: python

   >>> regr.clear()
   >>> len(regr)
   0
   >>> for num in range(10):
   ...     regr.push(num, num + 5)
   >>> len(regr)
   10
   >>> regr.slope()
   1.0
   >>> more = Regression((num, num + 5) for num in range(10, 20))
   >>> total = regr + more
   >>> len(total)
   20
   >>> total.slope()
   1.0
   >>> total.intercept()
   5.0
   >>> total.correlation()
   1.0

Regression summaries provide three measures of a series of pairs: slope,
intercept and correlation. Note that, as a regression, the points need not
exactly lie on a line:

.. code-block:: python

   >>> regr = Regression([(1.2, 1.9), (3, 5.1), (4.9, 8.1), (7, 11)])
   >>> regr.slope()
   1.5668320150154176
   >>> regr.intercept()
   0.21850113956294415
   >>> regr.correlation()
   0.9983810791694997

Both constructors accept an optional iterable that is consumed and pushed into
the summary. Note that you may pass a generator as an iterable and the
generator will be entirely consumed.

The ExponentialMovingStatistics are constructed by providing a decay rate,
initial mean, and initial variance. The decay rate defaults to 0.9 and must be
between 0 and 1. The initial mean and variance default to zero.

.. code-block:: python

   >>> exp_stats = ExponentialMovingStatistics()
   >>> exp_stats.decay
   0.9
   >>> exp_stats.mean()
   0.0
   >>> exp_stats.variance()
   0.0

The decay rate is the weight by which the current statistics are discounted
by. Consequently, (1 - decay) is the weight of the new value. Like the
`Statistics` class, there are four methods for modification: `push`, `clear`,
sum and multiply.

.. code-block:: python

   >>> for num in range(10):
   ...     exp_stats.push(num)
   >>> exp_stats.mean()
   3.486784400999999
   >>> exp_stats.variance()
   11.593430921943071
   >>> exp_stats.stddev()
   3.4049127627507683

The decay of the exponential statistics can also be changed during the lifetime
of the object.

.. code-block:: python

   >>> exp_stats.decay
   0.9
   >>> exp_stats.decay = 0.5
   >>> exp_stats.decay
   0.5
   >>> exp_stats.decay = 10
   Traceback (most recent call last):
     ...
   ValueError: decay must be between 0 and 1

Combining `ExponentialMovingStatistics` is done by adding them together. The
mean and variance are simply added to create a new object. To weight each
`ExponentialMovingStatistics`, multiply them by a constant factor.
Note how this behaviour differs from the two previous classes. When two
`ExponentialMovingStatistics` are added the decay of the left object is used for
the new object. The clear method resets the object to its state at
construction. The `len` method as well as minimum and maximum are not
supported.

.. code-block:: python

   >>> alpha_stats = ExponentialMovingStatistics(iterable=range(10))
   >>> beta_stats = ExponentialMovingStatistics(decay=0.1)
   >>> for num in range(10):
   ...     beta_stats.push(num)
   >>> exp_stats = beta_stats * 0.5 + alpha_stats * 0.5
   >>> exp_stats.decay
   0.1
   >>> exp_stats.mean()
   6.187836645

The `ExponentialMovingCovariance` works equivalently to
`ExponentialMovingStatistics`.

.. code-block:: python

    >>> exp_cov = ExponentialMovingCovariance(
    ... decay=0.9,
    ... mean_x=0.0,
    ... variance_x=0.0,
    ... mean_y=0.0,
    ... variance_y=0.0,
    ... covariance=0.0,
    ... iterable=(),
    ... )
    >>> for num in range(10):
    ...     exp_cov.push(num, num + 5)
    >>> round(exp_cov.covariance(), 2)
    17.67
    >>> round(exp_cov.correlation(), 2)
    0.96

`ExponentialMovingStatistics` can also work in a time-based mode i.e. old
statistics are not simply discounted by the decay rate each time a value is
pushed but an effective decay rate is calculated based on the provided decay
rate and the time difference between the last push and the current push.
`ExponentialMovingStatistics` operate in time based mode when a `delay` value
> 0 is provided at construction. The delay is the no. of seconds that need to
pass for the effective decay rate to be equal to the provided decay rate.
For example, if a delay of 60 and a delay of 0.9 is provided, than after 60
seconds pass between calls to push() the effective decay rate for discounting
the old statistics equals 0.9, when 120 seconds pass than it equals
0.9 ** 2 = 0.81 and so on. The exact formula for calculating the effective
decay rate at a given call to push is:
decay ** ((current_timestamp - timestamp_at_last_push) / delay). The initial
timestamp is the timestamp at object construction.

.. code-block:: python

   >>> import time
   >>> alpha_stats = ExponentialMovingStatistics(decay=0.9, delay=1)
   >>> time.sleep(1)
   >>> alpha_stats.push(100)
   >>> round(alpha_stats.mean())
   10
   >>> alpha_stats.clear()  # note that clear() resets the timer as well
   >>> time.sleep(2)
   >>> alpha_stats.push(100)
   >>> round(alpha_stats.mean())
   19

There are a few things to note about an time_based
`ExponentialMovingStatistics` object:
- When providing an iterable at construction together with a delay, the iterable
is first processed in non-time based mode i.e. as if there would be no delay
- The delay can also be set after object construction. In this case the initial
timestamp is the time when the delay is set. If a non `None` delay is changed,
this does not effect the timer. Setting delay to `None` deactivates time based
mode.
- When two ExponentialMovingStatistics objects are added the state of the delay
is taken from the left object. If the left object is time-based (non `None`
delay) the timer is reset during an regular __add__ (a + b) for the resulting
object while it is not during an incremental add __iadd__ (a += b).
- Last but not least the timer can be stopped with a call to freeze(). This can
be useful when saving the state of the object (get_state()) for later usage.
With a call to unfreeze() the timer continues where it left of (e.g. after
loading). Note that pushes onto a freezed object use a effective decay rate
based on the time difference between the last call to push and the moment
freeze was called().
- It is not recommended to use time based discounting for use cases that
require high precision on below seconds granularity.

.. code-block:: python

   >>> alpha_stats = ExponentialMovingStatistics(decay=0.9, delay=1)
   >>> time.sleep(1)
   >>> alpha_stats.freeze()
   >>> saved_state = alpha_stats.get_state()
   >>> time.sleep(2)
   >>> beta_stats = ExponentialMovingStatistics.fromstate(saved_state)
   >>> beta_stats.push(10)
   >>> round(beta_stats.mean())
   1
   >>> beta_stats.unfreeze()
   >>> time.sleep(1)
   >>> beta_stats.push(10)
   >>> round(beta_stats.mean())
   3

All internal calculations of the Statistics and Regression classes are based
entirely on the C++ code by John Cook as posted in a couple of articles:

* `Computing Skewness and Kurtosis in One Pass`_
* `Computing Linear Regression in One Pass`_

.. _`Computing Skewness and Kurtosis in One Pass`: http://www.johndcook.com/blog/skewness_kurtosis/
.. _`Computing Linear Regression in One Pass`: http://www.johndcook.com/blog/running_regression/

The ExponentialMovingStatistics implementation is based on:

* `Finch, 2009, Incremental Calculation of Weighted Mean and Variance`_

.. _`Finch, 2009, Incremental Calculation of Weighted Mean and Variance`: https://fanf2.user.srcf.net/hermes/doc/antiforgery/stats.pdf

The pure-Python version of `RunStats`_ is directly available if preferred.

.. code-block:: python

   >>> import runstats.core   # Pure-Python
   >>> runstats.core.Statistics
   <class 'runstats.core.Statistics'>

When importing from `runstats` the Cython-optimized version `_core` is
preferred and the `core` version is used as fallback. Micro-benchmarking
Statistics and Regression by calling `push` repeatedly shows the
Cython-optimized extension as 20-40 times faster than the pure-Python
extension.


Reference and Indices
---------------------

* `RunStats Documentation`_
* `RunStats API Reference`_
* `RunStats at PyPI`_
* `RunStats at GitHub`_
* `RunStats Issue Tracker`_

.. _`RunStats Documentation`: http://www.grantjenks.com/docs/runstats/
.. _`RunStats API Reference`: http://www.grantjenks.com/docs/runstats/api.html
.. _`RunStats at PyPI`: https://pypi.python.org/pypi/runstats/
.. _`RunStats at GitHub`: https://github.com/grantjenks/python-runstats/
.. _`RunStats Issue Tracker`: https://github.com/grantjenks/python-runstats/issues/


License
-------

Copyright 2013-2021 Grant Jenks

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License.  You may obtain a copy of the
License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.
