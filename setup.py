#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='oscar-schedules',
    version=0.77,
    description='library to help calculating OSCAR schedules',
    author='Timo Proescholdt',
    author_email='tproescholdt@wmo.int',
    url='https://github.com/kurt-hectic/oscar-schedules',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'requests'
      ],
    
    )
