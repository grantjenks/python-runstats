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
- Optional Cython-optimized Extension (5-100 times faster)
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

You can access documentation in the interpreter with Python's built-in help
function:

.. code-block:: python

   >>> import runstats
   >>> help(runstats)                             # doctest: +SKIP
   >>> help(runstats.Statistics)                  # doctest: +SKIP
   >>> help(runstats.Regression)                  # doctest: +SKIP
   >>> help(runstats.ExponentialStatistics)       # doctest: +SKIP


Tutorial
--------

The Python `RunStats`_ module provides three types for computing running
statistics: Statistics, ExponentialStatistics and Regression.The Regression
object leverages Statistics internally for its calculations. Each can be
initialized without arguments:

.. code-block:: python

   >>> from runstats import Statistics, Regression, ExponentialStatistics
   >>> stats = Statistics()
   >>> regr = Regression()
   >>> exp_stats = ExponentialStatistics()

Statistics objects support four methods for modification. Use `push` to add
values to the summary, `clear` to reset the summary, sum to combine Statistics
summaries and multiply to weight summary Statistics by a scalar.

.. code-block:: python

   >>> for num in range(10):
   ...     stats.push(float(num))
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
   TypeError: ...
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

The ExponentialStatistics are constructed by providing a decay rate, initial
mean, and initial variance. The decay rate has default 0.9 and must be between
0 and 1. The initial mean and variance default to zero.

.. code-block:: python

   >>> exp_stats = ExponentialStatistics()
   >>> exp_stats.decay
   0.9
   >>> exp_stats.mean()
   0.0
   >>> exp_stats.variance()
   0.0

The decay rate is the weight by which the current statistics are discounted
by. Consequently, (1 - decay) is the weight of the new value. Like the `Statistics` class,
there are four methods for modification: `push`, `clear`, sum and
multiply.

.. code-block:: python

   >>> for num in range(10):
   ...     exp_stats.push(num)
   >>> exp_stats.mean()
   3.486784400999999
   >>> exp_stats.variance()
   11.593430921943071
   >>> exp_stats.stddev()
   3.4049127627507683

The decay of the exponential statistics can also be changed. The value must be
between 0 and 1.

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

The clear method allows to optionally set a new mean, new variance and new
decay. If none are provided mean and variance reset to zero, while the decay is
not changed.

.. code-block:: python

   >>> exp_stats.clear()
   >>> exp_stats.decay
   0.5
   >>> exp_stats.mean()
   0.0
   >>> exp_stats.variance()
   0.0

Combining `ExponentialStatistics` is done by adding them together. The mean and
variance are simply added to create a new object. To weight each
`ExponentialStatistics`, multiply them by a constant factor. If two
`ExponentialStatistics` are added then the leftmost decay is used for the new
object. The `len` method is not supported.

.. code-block:: python

   >>> alpha_stats = ExponentialStatistics(iterable=range(10))
   >>> beta_stats = ExponentialStatistics(decay=0.1)
   >>> for num in range(10):
   ...     beta_stats.push(num)
   >>> exp_stats = beta_stats * 0.5 + alpha_stats * 0.5
   >>> exp_stats.decay
   0.1
   >>> exp_stats.mean()
   6.187836645

All internal calculations of the Statistics and Regression classes are based
entirely on the C++ code by John Cook as posted in a couple of articles:

* `Computing Skewness and Kurtosis in One Pass`_
* `Computing Linear Regression in One Pass`_

.. _`Computing Skewness and Kurtosis in One Pass`: http://www.johndcook.com/blog/skewness_kurtosis/
.. _`Computing Linear Regression in One Pass`: http://www.johndcook.com/blog/running_regression/

The ExponentialStatistics implementation is based on:

* Finch, 2009, Incremental Calculation of Weighted Mean and Variance

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

.. _`RunStats`: http://www.grantjenks.com/docs/runstats/


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
