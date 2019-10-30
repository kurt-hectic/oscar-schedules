#!/usr/bin/env python

from setuptools import setup, find_packages
import oscar_schedules

setup(
    name='oscar-schedules',
    version=oscar_schedules.__version__ ,
    description='library to help calculating OSCAR schedules',
    author='Timo Proescholdt',
    author_email='tproescholdt@wmo.int',
    url='https://github.com/kurt-hectic/oscar-schedules',
    packages=find_packages(),
    install_requires=[
        'setuptools','requests',
      ],
    
    )