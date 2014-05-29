#!/usr/bin/env python
# -*- coding:utf-8 -*-
from setuptools import setup


requires = ['tornado', 'pycurl']

setup(name='tornadohttpclient',
      version= '0.3.2',
      description='Asynchronous http client.',
      long_description="TornadoHTTPClient 对tornado.curl_httpclient.CurlAsyncHTTPClient的封装, 支持cookie",
      author='cold',
      author_email='wh_linux@126.com',
      url='http://www.linuxzen.com',
      py_modules=['tornadohttpclient'],
      scripts=[],
      install_requires = requires,
      license='Apache 2.0',
      platforms = 'any',
      classifiers=['Development Status :: 3 - Alpha',
        "Intended Audience :: Developers",
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.3',
        ],
     )
