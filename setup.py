"""Package Setup for RunStats

Build binary extension in-place for testing with:

$ python setup.py build_ext --inplace

"""

from setuptools import Extension, setup
from setuptools.command.test import test as TestCommand

import runstats


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import tox
        errno = tox.cmdline(self.test_args)
        exit(errno)


with open('README.rst') as reader:
    readme = reader.read()

args = dict(
    name=runstats.__title__,
    version=runstats.__version__,
    description='Compute statistics and regression in one pass',
    long_description=readme,
    author='Grant Jenks',
    author_email='contact@grantjenks.com',
    url='http://www.grantjenks.com/docs/runstats/',
    license='Apache 2.0',
    packages=['runstats'],
    tests_require=['tox'],
    cmdclass={'test': Tox},
    install_requires=[],
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ),
)

try:
    from Cython.Build import cythonize
    ext_modules = [Extension('runstats.fast', ['runstats/fast.pyx'])]
    setup(ext_modules=cythonize(ext_modules), **args)
except Exception as exception:
    print('*' * 75)
    print(exception)
    print('*' * 75)
    print('Failed to setup runstats with Cython. See error message above.')
    print('Using pure-Python implementation.')
    print ('*' * 75)
    setup(**args)
