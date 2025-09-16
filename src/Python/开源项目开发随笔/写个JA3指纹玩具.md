---
title: 写写玩具
tags:
  - Python
  - 爬虫
  - 反爬
category:
  - Python
  - 开发
  - 爬虫
date: 2025-09-04
---
## 参考资料
- [Mozilla开发者文档 - TLS传输层安全性协议](https://developer.mozilla.org/zh-CN/docs/Glossary/TLS)
- [维基百科 - TLS传输层安全性协议](https://zh.wikipedia.org/wiki/%E5%82%B3%E8%BC%B8%E5%B1%A4%E5%AE%89%E5%85%A8%E6%80%A7%E5%8D%94%E5%AE%9A)
- [Python dpkt库API文档列表](https://dpkt.readthedocs.io/en/latest/api/api_auto.html#module-dpkt.ssl_ciphersuites)

- [IBM - TLS握手介绍](https://www.ibm.com/docs/en/ibm-mq/9.3.x?topic=tls-overview-ssltls-handshake)

- [MiguelGrinberg - 简单构建使用HTTPS协议的Flask网站](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https)
***
## 前言
### 何为TLS协议
> **传输层安全性协议**（Transport Layer Security，缩写作 TLS），前身安全套接层（Secure Sockets Layer，缩写作 SSL），是一个被应用程序用来在网络中安全通信的[协议](https://developer.mozilla.org/zh-CN/docs/Glossary/Protocol)，防止电子邮件、网页、消息以及其他协议被篡改或是窃听。TLS 和 SSL 都是客户端/服务器协议，通过使用加密协议来提供网络安全。当服务器和客户端使用 TLS 通信时，它确保没有第三方可以窃听或篡改任何消息。

### TLS握手流程
1. ![](assets/Pasted%20image%2020250905160128.png)
	客户端发送`client hello`消息，消息中包含客户端所支持的加密配置（例如TLS版本、客户端所支持的加密曲线等等）；消息同时包含用于后续计算的随机字符串；协议还允许客户端在`client hello`消息中包含客户端所支持的数据压缩方法
2. ![](assets/Pasted%20image%2020250905160302.png)
	服务器响应`server hello`消息，消息中包含服务器选用的（来自客户端）加密方法、服务器生成的会话ID和另一个随机字符串；服务器亦会发送其证书；如果服务器需要用于客户端身份认证的证书，那么还会发送`client certificate request`消息，消息中包含服务器所支持的所有证书类型及服务器可接受的CA辨识名称
3. 
	TLS客户端校验服务端的证书
4. 
	TLS客户端发出客户端和服务端皆可用于计算密钥，以加密后续消息数据的随机字符串。服务器会使用它自己的公钥加密这个随机字符串
5. 
	如果服务器要求`client certificate request`，那么客户端会使用它自己的私钥加密从TLS客户端那里拿到的随机字符串，然后连同客户端的证书一起发给服务器；客户端有时会发送`no digital certificate alert`，警告服务器它没有证书——当然，这通常只是一个`warning`，但在某些强制要求客户端身份认证的实现下，这会导致TLS握手失败
6. 
	TLS服务器验证客户端的证书
7. ![](assets/Pasted%20image%2020250905160838.png)
	TLS客户端向服务器发送使用私钥加密了的`finished`消息，表示TLS握手的客户端部分完成
8. ![](assets/Pasted%20image%2020250905160856.png)
	TLS服务器向客户端发送使用密钥加密了的`finished`消息，表示TLS握手的服务端部分也完成了
9. ![](assets/Pasted%20image%2020250905160933.png)
	在TLS会话的有效期内，服务端和客户端现在可以互相发送使用共享密钥进行堆对称加密了的消息

![](assets/q009930b.gif)

### 环境准备
#### 本地使用`Flask`+`OpenSSL`搭建测试用的HTTPS环境
```Python
from yaml import safe_load
from dataclasses import dataclass
# 定位根目录并加载配置文件
@lru_cache(maxsize=1)
def _locate_root(
    flag: str = 'config.yaml',
    recursion_limit: int = 5
    ) -> Path:
    curr_dir = Path(__file__).parent
    for i in range(recursion_limit):
        candidate = curr_dir / flag
        if candidate.exists():
            return curr_dir
        if curr_dir.parent == curr_dir:
            break
        curr_dir = curr_dir.parent
    raise FileNotFoundError(f"无法根据{flag}找到项目根目录")

root = _locate_root()
config_path = root / 'config.yaml'
if not config_path.exists():
    raise FileNotFoundError(f"配置文件{config_path}不存在，请创建")
with open(config_path, 'r', encoding='utf-8') as f:
    cfg = safe_load(f)
# Config dataclass配置
class config:
    @dataclass(frozen=True)
    class ssl:
        cert: str = cfg.get('ssl', {}).get('cert', '')
        key: str = cfg.get('ssl', {}).get('key', '')

    @dataclass(frozen=True)
    class server:
        host: str = cfg.get('server', {}).get('host', '0.0.0.0')
        port: int = cfg.get('server', {}).get('port', 5000)
```

```Python
# Flask app.py页面入口文件
from typing import Literal, Any
from toollib import get_logger, config

from flask import Flask, request

app = Flask(__name__)
logger = get_logger()

@app.route('/')
def main() -> Any:
    logger.debug(f"Client {request.user_agent} accessed the main page.")
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(
        ssl_context=(config.ssl.cert, config.ssl.key),
        # openssl生成的自签名证书用于测试
    )

```

```shell
# 生成本地用的SSL证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem
```

`curl`默认会丢弃不安全的HTTPS请求，所以，需要用`curl`测试网络连通性的时候请带上`-k/--insecure`参数：
```shell
C:\Users\SyYhunfhds>curl https://127.0.0.1:5000
curl: (60) schannel: SEC_E_UNTRUSTED_ROOT (0x80090325) - 证书链是由不受信任的颁发机构颁发的。
More details here: https://curl.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. To learn more about this situation and
how to fix it, please visit the webpage mentioned above.

C:\Users\SyYhunfhds>curl https://127.0.0.1:5000 -k
Hello, World!
```

***
# 页面尾部