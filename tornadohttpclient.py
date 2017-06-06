#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/08/05 10:49:47
#   Desc    :
#
from __future__ import absolute_import, print_function, division
from __future__ import with_statement

import os
import json
import mimetypes
import itertools

from functools import partial

try:
    from mimetools import choose_boundary
except ImportError:
    from email.generator import _make_boundary as choose_boundary

try:
    from cookielib import Cookie, CookieJar
except ImportError:
    from http.cookiejar import Cookie, CookieJar  # py3

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

import pycurl

from tornado import httputil
from tornado import httpclient
from tornado import escape
from tornado import util

try:
    from tornado.curl_httpclient import CurlAsyncHTTPClient
except ImportError:
    CurlAsyncHTTPClient = httpclient.AsyncHTTPClient

from tornado.ioloop import IOLoop


class TornadoHTTPClient(CurlAsyncHTTPClient):
    """ 封装 tornado.curl_httpclient.CurlAsyncHTTPClient 支持 cookie 并封装的
    更加易用是指支持如下方法:
        get/post/put/patch/head/delete/options
    ::
        from tornado import gen
        from tornado.web import RequestHandler
        from tornadohttpclient import TornadoHTTPClient
        class DemoHandler(RequestHandler):
            @gen.coroutine
            def get(self):
                http_client = TornadoHTTPClient()
                response = yield http_client.get("http://www.google.com",
                                                 {"s": "word"})
                self.write(response.body)
    """

    def initialize(self, *args, **kwargs):
        super(TornadoHTTPClient, self).initialize(*args, **kwargs)
        self._cookie = {}
        self._proxy = {}
        self._user_agent = None
        self.keep_alive = True
        self.use_cookie = True
        self.debug = False
        self.validate_cert = True
        self._headers = {}

        self._share = None
        if pycurl is not None:
            self._share = pycurl.CurlShare()
            self._share.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_COOKIE)
            self._share.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_DNS)
            for curl in self._curls:
                self._setup_curl(curl)

    def _setup_curl(self, curl):
        curl.setopt(pycurl.SHARE, self._share)

    def set_user_agent(self, user_agent):
        self._user_agent = user_agent

    def set_global_headers(self, headers):
        self._headers = headers

    def set_proxy(self, host, port=8080, username=None, password=None):
        assert isinstance(port, int)
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
            if self.debug:
                curl.setopt(pycurl.VERBOSE, 1)

            if callback:
                return callback(curl)
        return _wrap_prepare_curl_callback

    def wrap_callback(self, callback,  args=(), kwargs={}):
        return partial(callback, *args, **kwargs)

    def get_url(self, url, params):
        """ 拼接 URL
        :param url: url
        :param params: URL 参数
        """
        if params is not None:
            if isinstance(params, (list, dict, tuple)):
                params = urlencode(params)

            if "?" not in url:
                url += "?" + params
            else:
                url += "&" + params
        return url.rstrip("?")

    def get_urlencoded_body(self, data):
        result = []
        data = data.items() if isinstance(data, dict) else data

        for key, val in data:
            if val is not None:
                result.append((key, val))

        return urlencode(result)

    def get_json_body(self, data):
        return json.dumps(data)

    def get_multipart_body(self, data):
        raise NotImplementedError()

    def get_request_body(self, content_type, data):
        """ 根据请求内容的类型来获取请求包体 """
        if isinstance(data, util.basestring_type):
            return escape.utf8(data)

        if content_type is None:
            return self.get_urlencoded_body(data)

        if content_type[:16] == "application/json":
            return self.get_json_body(data)
        elif content_type[:19] == "multipart/form-data":
            return self.get_multipart_body(data)
        else:
            return self.get_urlencoded_body(data)

    def make_request(self, url, data=None, **kwargs):
        """ 构造 HTTP 请求
        :param url: 请求路径
        :param data: 请求参数
        :param url_params: 放在 URL 路径上的请求参数, 用于请求方法非 GET 但
                           有参数放在 URL 上
        :param **kwargs: 传递给 tornado.httpclient.HTTPRequest 的其他参数
        """
        headers = httputil.HTTPHeaders()
        headers.update(kwargs.get("headers", {}))
        headers.update(self._headers)
        self.keep_alive and headers.update(Connection="keep-alive")
        kwargs.update(validate_cert=self.validate_cert)

        kwargs["headers"] = headers

        method = kwargs.get("method", "GET").upper()
        if method in ["GET", "HEAD", "DELETE"]:
            url_params = data
        else:
            url_params = kwargs.pop("url_params", {})
            if not kwargs.get('body'):
                kwargs["body"] = self.get_request_body(
                    headers.get("content-type"), data)

        curl_callback = kwargs.pop("prepare_curl_callback", None)
        curl_callback = self.wrap_prepare_curl_callback(curl_callback)

        kwargs.update(self._proxy)
        self._user_agent and kwargs.update(user_agent=self._user_agent)
        kwargs.update(prepare_curl_callback=curl_callback)

        url = self.get_url(url, url_params)
        return httpclient.HTTPRequest(url, **kwargs)

    def request(self, url, data=None, **kwargs):
        """ 封装 Tornado 异步 HTTP 请求, 并记录日志 """
        callback = kwargs.pop("callback", None)
        args, kw = kwargs.pop("args", ()), kwargs.pop("kwargs", {})

        if callable(callback):
            callback = self.wrap_callback(callback, args, kw)

        request = self.make_request(url, data, **kwargs)
        return self.fetch(request, callback=callback)

    def get(self, url, data=None, **kwargs):
        return self.request(url, data, **kwargs)

    def post(self, url, data, **kwargs):
        return self.request(url, data, method="POST", **kwargs)

    def put(self, url, data, **kwargs):
        return self.request(url, data, method="PUT", **kwargs)

    def head(self, url, data=None, **kwargs):
        return self.request(url, data, method="HEAD", **kwargs)

    def delete(self, url, data=None, **kwargs):
        return self.request(url, data, method="DELETE", **kwargs)

    def options(self, url, data, **kwargs):
        return self.request(url, data, method="OPTIONS", **kwargs)

    def patch(self, url, data, **kwargs):
        return self.request(url, data, method="PATCH", **kwargs)

    def close(self):
        super(TornadoHTTPClient, self).close()
        self._force_timeout_callback.callback = None
        self._multi = None

    def upload(self, url, field, path, params={}, mimetype=None,
               callback=None, **kwargs):
        method = kwargs.pop("method", "POST")
        form = UploadForm()
        [form.add_field(name, value) for name, value in params.items()]
        _, fname = os.path.split(path)
        form.add_file(field, fname, open(path, 'rb'), mimetype)
        kwargs.update(body=str(form))
        kwargs.update(method=method)
        kwargs.update(headers={"Content-Type": form.get_content_type()})
        kwargs["callback"] = callback
        return self.request(url, **kwargs)

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

            self._cookie.setdefault(domain, {})
            self._cookie[domain].setdefault(path, {})
            self._cookie[domain][path].update({name: cookie})

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


class UploadForm(object):
    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = choose_boundary()
        self.content_type = 'multipart/form-data; boundary=%s' % self.boundary
        return

    def get_content_type(self):
        return self.content_type

    def add_field(self, name, value):
        self.form_fields.append((str(name), str(value)))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        # use str convert to str to compatible with py35
        body = str(fileHandle.read())
        if mimetype is None:
            mimetype = (mimetypes.guess_type(filename)[0] or
                        'applicatioin/octet-stream')
        self.files.append((fieldname, filename, mimetype, body))
        return

    def __str__(self):
        parts = []
        part_boundary = '--' + self.boundary

        parts.extend(
            [
                part_boundary,
                'Content-Disposition: form-data; name="%s"' % name,
                '',
                value,
            ] for name, value in self.form_fields)
        if self.files:
            parts.extend([
                part_boundary,
                'Content-Disposition: form-data; name="%s"; filename="%s"' % (
                    field_name, filename),
                'Content-Type: %s' % content_type,
                '',
                body,
            ] for field_name, filename, content_type, body in self.files)

        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)
