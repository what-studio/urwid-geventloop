# -*- coding: utf-8 -*-
from __future__ import with_statement
import re
from setuptools import setup


# detect the current version
with open('urwid_geventloop.py') as f:
    version = re.search(r'__version__\s*=\s*\'(.+?)\'', f.read()).group(1)
assert version


setup(
    name='urwid-geventloop',
    version=version,
    license='BSD',
    author='Heungsub Lee',
    author_email='sub@nexon.co.kr',
    maintainer='What! Studio',
    url='https://github.com/what-studio/urwid-geventloop',
    description='Event loop based on gevent',
    long_description=__doc__,
    platforms='any',
    py_modules=['urwid_geventloop'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    install_requires=['gevent'],
)
