RunStats: Compute Statistics and Regression in One Pass
=======================================================

`RunStats <http://www.grantjenks.com/docs/runstats/>`_ is an Apache2 licensed
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
function::

  >>> from runstats import Statistics, Regression
  >>> help(Statistics)
  >>> help(Regression)

Tutorial
--------

.. todo::
   Give a tutorial of Statistics and Regression objects.

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
.. _`RunStats at GitHub`: https://github.com/grantjenks/python_runstats/
.. _`RunStats Issue Tracker`: https://github.com/grantjenks/python_runstats/issues/

License
-------

Copyright 2015 Grant Jenks

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
