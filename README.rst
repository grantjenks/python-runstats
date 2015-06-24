RunStats: Compute Statistics and Regression in One Pass
=======================================================

`RunStats <http://www.grantjenks.com/docs/tribool/>`_ is an Apache2 licensed
Python module that computes statistics and regression in a single pass.

.. todo::
   Describe use cases.

Features
--------

- Pure-Python (easy to hack with)
- Fully Documented
- 100% Test Coverage
- Pragmatic Design (based entirely on Knuth and Welford algorithms)
- Developed on Python 2.7
- Tested on CPython 2.6, 2.7, 3.2, 3.3, 3.4 and PyPy 2.5+, PyPy3 2.4+

Quickstart
----------

Installing RunStats is simple with
`pip <http://www.pip-installer.org/>`_::

  $ pip install runstats

You can access documentation in the interpreter with Python's built-in help
function:

  >>> from runstats import Statistics, Regression
  >>> help(Statistics)
  >>> help(Regression)

Tutorial
--------

.. todo::
   Give a tutorial of Statistics and Regression objects.

Reference and Indices
---------------------

.. toctree::

   api

* `RunStats Documentation`_
* `RunStats at PyPI`_
* `RunStats at GitHub`_
* `RunStats Issue Tracker`_
* :ref:`search`
* :ref:`genindex`

.. _`RunStats Documentation`: http://www.grantjenks.com/docs/runstats/
.. _`RunStats at PyPI`: https://pypi.python.org/pypi/runstats/
.. _`RunStats at GitHub`: https://github.com/grantjenks/python_runstats/
.. _`RunStats Issue Tracker`: https://github.com/grantjenks/python_runstats/issues/

License
-------

.. include:: ../LICENSE

.. todo::
   Fix links to old project page at
   http://www.grantjenks.com/blog/portfolio-post/python-runstats-module/
