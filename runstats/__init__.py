"""Python RunStats - Online Statistics and Regression

"""

try:
    from .fast import Statistics, Regression
except ImportError:
    from .core import Statistics, Regression

__title__ = 'runstats'
__version__ = '1.0.0'
__build__ = 0x010000
__author__ = 'Grant Jenks'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2015 Grant Jenks'
