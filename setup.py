#!/usr/bin/env python

from distutils.core import setup

setup(
    name='oscar-schedules',
    version='0.1',
    description='library to help calculating OSCAR schedules',
    author='Timo Proescholdt',
    author_email='tproescholdt@wmo.int',
    url='https://github.com/kurt-hectic/oscar-schedules',
    packages=['oscar-schedules'],
    install_requires=[
        'setuptools',
        'requests',
      ],
    
    )