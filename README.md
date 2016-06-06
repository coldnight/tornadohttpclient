TornadoHTTPClient 对tornado.curl_httpclient.CurlAsyncHTTPClient的封装, 支持cookie

## 安装
```bash
python setup.py install
```

## 教程
### GET
TornadoHTTPClient的get方法可以发起一个get请求
```python
from tornado import gen
from tornado.ioloop import IOLoop

from tornadohttpclient import TornadoHTTPClient

# 实例化
http = TornadoHTTPClient()

@gen.coroutine
def get():
    # 发出get请求
    response = yield http.get("http://www.linuxzen.com")
    print(response.body)

IOLoop.instance().run_sync(get)
```

### 上传文件

```python
from tornado import gen
from tornado.ioloop import IOLoop

from tornadohttpclient import TornadoHTTPClient

# 实例化
http = TornadoHTTPClient()

@gen.coroutine
def run():
    response = yield http.upload("http://paste.linuxzen.com", "img", 
                                 "img_test.png", callback=callback)
    print("打开图片链接", end=" ")
    print(response.effective_url)

IOLoop.instance().run_sync(run)
```

### 给请求传递参数
TornadoHTTPClient 的 `get`/`post`方法的第二个参数`data`可以定义请求时传递的参数`data`的类型为字典或者`((key, value), )`类型的元组或列表,例如使用百度搜索`TornadoHTTPClient`
```python
from tornado import gen
from tornado.ioloop import IOLoop

from tornadohttpclient import TornadoHTTPClient

# 实例化
http = TornadoHTTPClient()

@gen.coroutine
def run():
    response = yield http.get("http://www.baidu.com/s", (("wd", "tornado"),))
    print(response.effective_url)

IOLoop.instance().run_sync(run)
```

以上也使用与POST方法, 比如登录网站
```python
from tornado import gen
from tornado.ioloop import IOLoop

from tornadohttpclient import TornadoHTTPClient

# 实例化
http = TornadoHTTPClient()

@gen.coroutine
def run():
    yield http.post("http://ip.or.domain/login", (("username", "cold"), ("password", "pwd")))

IOLoop.instance().run_sync(run)
```


## 设置User-Agent
```python
from tornadohttpclient import TornadoHTTPClient

http = TornadoHTTPClient()
http.set_user_agent( "Mozilla/5.0 (X11; Linux x86_64)"\
                " AppleWebKit/537.11 (KHTML, like Gecko)"\
                " Chrome/23.0.1271.97 Safari/537.11")

# 后续的请求都会使用此 User-Agent 头
# ...
```

### 指定HTTP头
TornadoHTTPClient 的`get`/`post`方法的 `headers`关键字参数可以自定额外的HTTP头信息, 参数类型为一个字典

指定User-Agent头

```python
from tornado import gen
from tornado.ioloop import IOLoop

from tornadohttpclient import TornadoHTTPClient

# 实例化
http = TornadoHTTPClient()

@gen.coroutine
def run():
    headers = dict((("User-Agent",
                "Mozilla/5.0 (X11; Linux x86_64)"\
                " AppleWebKit/537.11 (KHTML, like Gecko)"\
                " Chrome/23.0.1271.97 Safari/537.11"), ))

    yield http.get("http://www.linuxzen.com", headers=headers)

IOLoop.instance().run_sync(run)
```

### 使用代理

TornadoHTTPClient 的`set_proxy`方法可以设置代理, 其接受四个参数, 分别是代理的 主机名/ip 代理的端口 代理用户名 代理用户密码, 如无认证只传前两个即可, `unset_proxy`可以取消代理
```python
from tornado import gen
from tornado.ioloop import IOLoop

from tornadohttpclient import TornadoHTTPClient

# 实例化
http = TornadoHTTPClient()

@gen.coroutine
def run():
    http.set_proxy("127.0.0.1", 8087)
    response = yield http.get("http://shell.appspot.com", callback=callback)
    print response.body
    http.unset_proxy()

IOLoop.instance().run_sync(run)
```

### Cookie

TornadoHTTPClient会自动记录和装载Cookie, 可以通过 TornadoHTTPClient实例属性 cookie 获取Cookie
