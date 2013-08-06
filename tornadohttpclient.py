#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/08/05 10:49:47
#   Desc    :
#
from __future__ import print_function

import time
import atexit
import pycurl
import threading
try:
    from cookielib import Cookie, CookieJar
except ImportError:
    from http.cookiejar import Cookie, CookieJar  #py3

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from functools import partial

from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.ioloop import IOLoop

COOKIE_FILE = ".cookie_jar"

class TornadoHTTPClient(CurlAsyncHTTPClient):
    def initialize(self, *args, **kwargs):
        super(TornadoHTTPClient, self).initialize(*args, **kwargs)
        self._cookie = {}
        self._proxy = {}
        self._user_agent = None
        self.use_cookie = True
        self.debug = False


    def set_user_agent(self, user_agent):
        self._user_agent = user_agent


    def set_proxy(self, host, port = 8080, username = None, password = None):
        assert isinstance(port, (int, long))
        self._proxy["proxy_host"] = host
        self._proxy["proxy_port"] = port
        if username:
            self._proxy["proxy_username"] = username

        if password:
            self._proxy["proxy_password"] = password


    def unset_proxy(self):
        self._proxy = {}


    def wrap_prepare_curl_callback(self, callback):
        def _wrap_prepare_curl_callback(curl):
            if self.use_cookie:
                curl.setopt(pycurl.COOKIEFILE, COOKIE_FILE)
                curl.setopt(pycurl.COOKIEJAR, COOKIE_FILE)

            if self.debug:
                curl.setopt(pycurl.VERBOSE, 1)

            if callback:
                return callback(curl)
        return _wrap_prepare_curl_callback


    def wrap_callback(self, callback,  args = (), kwargs = {}):
        return partial(callback, *args, **kwargs)


    def fetch(self, request, callback, **kwargs):
        delay = kwargs.pop("delay", 0)
        if delay:
            t = threading.Thread(target = self._fetch,
                                args = (request, callback, kwargs, delay))
            t.setDaemon(True)
            t.start()
            return

        curl_callback = kwargs.pop("prepare_curl_callback", None)
        curl_callback = self.wrap_prepare_curl_callback(curl_callback)

        kwargs.update(self._proxy)
        self._user_agent and kwargs.update(user_agent = self._user_agent)
        kwargs.update(prepare_curl_callback = curl_callback)

        args, kw = kwargs.pop("args", ()), kwargs.pop("kwargs", {})
        if callable(callback):
            callback = self.wrap_callback(callback, args, kw)

        super(TornadoHTTPClient, self).fetch(request, callback, **kwargs)


    def _fetch(self, request, callback, kwargs, delay):
        if isinstance(threading.currentThread(), threading._MainThread):
            raise threading.ThreadError, "Can't run this function in _MainThread"
        time.sleep(delay)
        self.fetch(request, callback, **kwargs)


    def post(self, url, params = {}, callback = None, **kwargs):
        kwargs.pop("method", None)
        kwargs.update(body = urlencode(params))
        self.fetch(url, callback, method="POST", **kwargs)


    def get(self, url, params = {}, callback = None, **kwargs):
        kwargs.pop("method", None)
        url = "{0}?{1}".format(url, urlencode(params))
        self.fetch(url, callback, **kwargs)


    @property
    def cookie(self):
        lst = []
        for curl in self._curls:
            lst.extend(curl.getinfo(pycurl.INFO_COOKIELIST))

        return self._parse_cookie(lst)

    def _parse_cookie(self, lst):
        for item in lst:
            domain, domain_specified, path, path_specified, expires,\
             name, value = item.split("\t")

            cookie = Cookie(0, name, value, None, False, domain,
                            domain_specified.lower() == "true",
                            domain.startswith("."), path,
                            path_specified.lower() == "true", False, expires,
                            False, None, None, {})

            self._cookie.update({domain:{path:{name:cookie}}})

        return self._cookie


    @property
    def cookiejar(self):
        cookiejar = CookieJar()
        for domain, items in self.cookie.items():
            for path, names in items.items():
                for name, cookie in names.items():
                    cookiejar.set_cookie(cookie)

        return cookiejar


    def start(self):
        IOLoop.instance().start()


    def stop(self):
        IOLoop.instance().stop()




if __name__ == "__main__":
    http = TornadoHTTPClient()
    http.debug = False
    def callback(response):
        print(response.headers)
        print(http.cookie)
        http.stop()

    http.get("http://www.baidu.com", callback = callback)
    try:
        http.start()
    except KeyboardInterrupt:
        print("exiting...")

    def show_cookie():
        print(http.cookie)
