#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
from distutils.core import setup

if sys.version_info < (2,7) or sys.version_info >= (3, 0):
    raise NotImplementedError("Sorry, you need at least Python 2.7 to use tornadohttpclient.")


requires = ['tornado']

setup(name='tornadohttpclient',
      version= '0.1',
      description='Asynchronous http client.',
      long_description="TornadoHTTPClient 是一个基于Tornado的高效的异步HTTP客户端库, 支持Cookie和代理",
      author='cold',
      author_email='wh_linux@126.com',
      url='http://www.linuxzen.com',
      py_modules=['tornadohttpclient'],
      scripts=['tornadohttpclient.py'],
      license='Apache',
      platforms = 'any',
      classifiers=['Development Status :: Beta',
        'License :: OSI Approved :: Apache License',
        'Topic :: Internet :: WWW/HTTP :: HTTP Client',
        'Programming Language :: Python :: 2.7',
        ],
     )
