#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/08/05 16:37:37
#   Desc    :
#
from __future__ import absolute_import, print_function, division, with_statement


import time
import unittest

from tornado import testing

from tornadohttpclient import TornadoHTTPClient


class TornadoHTTPClientTest(unittest.TestCase):
    def setUp(self):
        self.http = TornadoHTTPClient()
        self.http.debug = True

    def _callback(self, response):
        print(response.code)
        print("当前链接地址: ")
        print(response.effective_url)
        self.http.stop()

    def test_get(self):
        self.http.get("http://www.linuxzen.com", callback=self._callback)
        self.http.start()

    def test_get_args(self):
        self.http.get("http://www.baidu.com/s", (("wd", "tornado"),),
                      callback=self._callback)

    def test_post(self):
        params = [("vimcn", u"# 这是TornadoHTTPClient单元测试提交的".encode("utf-8"))]
        url = "http://p.vim-cn.com"
        def callback(response):
            print("打开此链接:", end=" ")
            print(response.effective_url)
            self.http.stop()

        self.http.post(url, params, callback=callback)
        self.http.start()

    def test_head(self):
        def callback(response):
            pass

        self.http.head("http://linuxzen.com", callback=callback)

    def test_callback_args(self):
        def callback(times, response):
            print(response.code)
            print("当前链接地址: ")
            print(response.effective_url)
            print("当前请求次数", end=" ")
            print(times)
            if times == 9:
                self.http.stop()

        for i in range(10):
            self.http.get("http://www.linuxzen.com", callback=callback,
                          args=(i,))

        self.http.start()

    def test_user_agent(self):
        user_agent =  "Mozilla/5.0 (X11; Linux x86_64)"\
                " AppleWebKit/537.11 (KHTML, like Gecko)"\
                " Chrome/23.0.1271.97 Safari/537.11"
        self.http.set_user_agent(user_agent)

        def callback(response):
            #self.assertEqual(response.request.headers["User-Agent"], user_agent)
            self.http.stop()

        self.http.get("http://www.linuxzen.com", callback=callback)
        self.http.start()

    def test_header(self):
        headers = {"Origin":"http://www.linuxzen.com"}
        def callback(response):
            self.assertEqual(response.request.headers["Origin"],
                             headers.get("Origin"))
            self.http.stop()

        self.http.get("http://www.linuxzen.com", callback=callback)
        self.http.start()

    def test_cookie(self):
        def callback(response):
            print("cookie >>>>>>>>>>>>>>>>>>", end=" ")
            print(self.http.cookie)
            self.http.stop()

        self.http.get("http://www.baidu.com", callback=callback)
        self.http.start()

    def test_cookie_jar(self):
        def callback(response):
            print("cookie jar>>>>>>>>>>>>>>>>>>", end=" ")
            print(self.http.cookiejar)
            self.http.stop()

        self.http.get("http://www.baidu.com", callback=callback)
        self.http.start()

    def test_upload_img(self):
        def callback(response):
            print("打开图片链接", end = " ")
            print(response.effective_url)
            self.http.stop()

        self.http.upload("http://dimg.vim-cn.com", "name", "img_test.png",
                         callback=callback)
        self.http.start()


class TornadoHTTPClientCoroutineTest(testing.AsyncTestCase):
    def setUp(self):
        super(TornadoHTTPClientCoroutineTest, self).setUp()
        self.http = TornadoHTTPClient()
        self.http.debug = True

    def _callback(self, response):
        print(response.code)
        print("当前链接地址: ")
        print(response.effective_url)
        self.http.stop()

    @testing.gen_test
    def test_get(self):
        resp = yield self.http.get("http://www.linuxzen.com")
        self._callback(resp)

    @testing.gen_test
    def test_get_args(self):
        yield self.http.get("http://www.baidu.com/s", (("wd", "tornado"),),
                            callback=self._callback)

    @testing.gen_test
    def test_post(self):
        params = [("vimcn", u"# 这是TornadoHTTPClient单元测试提交的".encode("utf-8"))]
        url = "http://p.vim-cn.com"
        def callback(response):
            print("打开此链接:", end=" ")
            print(response.effective_url)

        resp = yield self.http.post(url, params)
        callback(resp)

    @testing.gen_test
    def test_head(self):
        resp = yield self.http.head("http://linuxzen.com")
        self.assertEqual(resp.code, 200)

    @testing.gen_test
    def test_user_agent(self):
        user_agent =  "Mozilla/5.0 (X11; Linux x86_64)"\
                " AppleWebKit/537.11 (KHTML, like Gecko)"\
                " Chrome/23.0.1271.97 Safari/537.11"
        self.http.set_user_agent(user_agent)

        resp = yield self.http.get("http://www.linuxzen.com")
        self.assertEqual(resp.request.user_agent, user_agent)

    @testing.gen_test
    def test_header(self):
        headers = {"Origin":"http://www.linuxzen.com"}
        resp = yield self.http.get("http://www.linuxzen.com", headers=headers)
        self.assertEqual(resp.request.headers["Origin"], headers["Origin"])

    @testing.gen_test
    def test_cookie(self):
        yield self.http.get("http://www.baidu.com")
        print(self.http.cookie)

    @testing.gen_test
    def test_cookie_jar(self):
        yield self.http.get("http://www.baidu.com")
        print("cookie jar>>>>>>>>>>>>>>>>>>", end=" ")
        print(self.http.cookiejar)

    @testing.gen_test
    def test_upload_img(self):
        def callback(response):
            self.http.stop()

        resp = yield self.http.upload("http://dimg.vim-cn.com", "name",
                                        "img_test.png")
        print("打开图片链接", end = " ")
        print(resp.effective_url)


def main():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(["tests.TornadoHTTPClientTest",
                                       "tests.TornadoHTTPClientCoroutineTest"])
    runner = unittest.TextTestRunner(verbosity = 2)
    runner.run(suite)

if __name__ == "__main__":
    main()

