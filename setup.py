#!/usr/bin/env python
import os

from setuptools import setup
from setuptools import find_packages
from setuptools.command.test import test as TestCommand


def long_description():
    path = os.path.dirname(__file__)
    path = os.path.join(path, 'README.rst')
    with open(path) as f:
        return f.read()


__doc__ = long_description()


class pytest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        # self.test_args = ['--pdb']
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)


from structurarium import __version__


setup(
    name='Structurarium',
    version=__version__,
    url='https://github.com/amirouche/Structurarium',
    license='AGPLv3',
    author='Amirouche Boubekki',
    author_email='amirouche.boubekki@gmail.com',
    description='Databases written in Python',
    long_description=__doc__,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    platforms='POSIX',
    install_requires=[
        'msgpack-python',
        'setproctitle',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    tests_require=['pytest'],
    cmdclass={'test': pytest},
    entry_points={
        'console_scripts': [
            'structurarium.graph = structurarium.graph.database:main',
            'structurarium.memo = structurarium.memo.database:main',
        ]
    }
)
