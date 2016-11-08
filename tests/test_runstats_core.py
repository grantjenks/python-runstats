"""Test core (pure-Python) runstats module.

"""

from .test_runstats import *
# Now we monkey-patch to get the actual pure-python implementation
from runstats import core
import runstats

runstats.Statistics = core.Statistics
runstats.Regression = core.Regression


if __name__ == '__main__':
    import nose
    nose.run()
