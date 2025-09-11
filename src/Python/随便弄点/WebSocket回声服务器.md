---
title: 使用FlaskSocketIO搭建WebSocket回声服务器
icon: square-code
category:
  - Python
  - WebSocket
tags:
  - WebSocket
  - Python
---

## 参考资料
- [BetterStack - Flask Websoceketio指南](https://betterstack.com/community/guides/scaling-python/flask-websockets/)

# 正文
## IOI
### WebSocket协议介绍
> **WebSocket 协议** 是一种在单个 TCP 连接上进行**全双工通信**的网络协议，它允许客户端和服务器之间建立持久、低延迟、双向的数据通道。与传统的 HTTP 协议不同，WebSocket 在建立连接后，客户端和服务器可以随时主动向对方发送数据，而无需每次请求都重新建立连接。

### Flask-SocketIO库 初见
> `Flask-SocketIO` 是 Flask 的一个扩展库，用于在 Flask 应用中集成 WebSocket 和长轮询等实时通信功能（基于 [Socket.IO](https://socket.io/) 协议）。它提供了多个**装饰器（decorators）**，用于注册不同类型的事件处理器（event handlers），包括连接、断开、自定义事件、错误处理等。

Flask-SocketIO提供如下常见装饰器用于定义不同类型的事件：

| 事件类型         | 装饰器                       | 事件描述              |
| ------------ | ------------------------- | ----------------- |
| `connect`    | `@socketio.on_connect`    | 客户端连接             |
| `disconnect` | `@socketio.on_disconnect` | 客户端断开             |
| 自定义事件        | `@socketio.on('xxx')`     | 如`message`、`ping` |
| 异常           | `@socketio.on_error`      | 事件处理异常            |

装饰器都支持`namespace`参数，用于处理不同*命名空间* 的事件，例如：
```python
@socketio.on('join', namespace='/chat') 
def on_join(data): 
	room = data['room'] 
	join_room(room) # 这里join_room是sio库提供的函数
	emit('status', 
		{'msg': f'Joined {room}'}, 
	room=room # sio从库层面支持了room分割频道
	)
```

#### 最简单的服务端和对应的客户端
```Python
from flask import Flask, request
from flask_socketio import SocketIO

from misc.toollib import config, get_logger
logger = get_logger()

app = Flask(__name__)
# SocketIO需要密钥来管理会话
app.config['SECERT_KEY'] = "A secret key"
# cors_allowed_origins='*' 允许所有来源的跨域请求
# 这在开发时将允许来自任何客户端的请求
socketio = SocketIO(app, cors_allowed_origins='*', logger=True)
# 作为Flask的拓展, Flask-SocketIO的sio实例也需要使用socketIO(app)或sio.init_app(app)来将socketio注册到flask实例中

@socketio.on('connect')
def test_connect():
    print("Client connected")

@socketio.on('disconnect')
def test_disconnect():
    print("Client disconnected")
    
if __name__ == '__main__':
    host, port = config.server.host, config.server.port
    logger.info(f"启动SocketIO服务端，监听 ws://{host}:{port}...")
    # 这是同步写法，会阻塞主线程
    # 需要的话可以使用socketio.start_background_task()
    socketio.run(app, host=config.server.host, port=config.server.port)

```

```Python
# 客户端
from misc.toollib import config, get_logger
logger = get_logger()

from colorama import Fore, Back, Style, init
init() # 初始化终端样式

import socketio

sio = socketio.Client()

@sio.event
def connect():
    logger.info(f"{Fore.GREEN}连接成功!{Style.RESET_ALL}")
    sio.emit('my event', {'data': 'Hello from client!'})

@sio.event
def disconnect():
    logger.info(f"{Fore.RED}断开连接!{Style.RESET_ALL}")

@sio.event
def my_response(data):
    logger.info(f"{Fore.CYAN}收到服务器响应: {data}{Style.RESET_ALL}")
    


def run_socketio_client():
    server_host, server_port = config.server.host, config.server.port
    while True:
        try:
            # 这里需要向服务器发送HTTP请求，因此还需要requests库
            # wait=False使得程序不会阻塞主线程，可以用Ctrl + C中断程序
            sio.connect(f'ws://127.0.0.1:{server_port}', wait=False)
        except Exception as e:
            logger.error(f"{Fore.RED}连接失败: {e}{Style.RESET_ALL}")
            decision = input("按回车键重新尝试...")
            if decision != '':
                logger.info(f"{Fore.YELLOW}用户取消重连, 将退出客户端{Style.RESET_ALL}")
                sio.disconnect() # 断开连接
                break

if __name__ == '__main__':
    run_socketio_client()
```
如上，代码注册了两个事件`connect`和`disconnect`的监听器，对应*客户端连接* 和 *客户端断开连接* 事件：
```Python
@socketio.on('connect')
def test_connect():
    print("Client connected")

@socketio.on('disconnect')
def test_disconnect():
    print("Client disconnected")
```
![](assets/Pasted%20image%2020250911190158.png)
使用`request.sid`可以获得与每个客户端唯一相关的会话ID

#### 实现回声服务端
前面的服务端只能（被动）响应客户端连接和断连事件，若想服务端主动回应客户端（以及客户端向服务端发送数据），我们需要`emit`和`send`函数：

| 方向         | 函数                       | 说明                         |
| ---------- | ------------------------ | -------------------------- |
| 服务端 -> 客户端 | `emit(event, data, ...)` | 最常用，支持广播、房间和指定用户           |
| 服务端 -> 客户端 | `send(event, data, ...)` | 等价于`emit('message', data)` |
| 客户端 -> 服务端 | `send(data)`             | 发送默认`message`事件            |
| 客户端 -> 服务端 | `emit(event, data, ...)` | 发送自定义事件                    |

![](assets/Pasted%20image%2020250911204346.png)
比方说，服务端写了：
```Python
    socketio.emit('available_events', 
                  {
                      'to_server': ['message'],
                      'from_server': ['echo']
                  } # 发送可用事件
                  )
```
那么就是往`available_events`里的所有客户端发送指定数据，在客户端使用`socketio.event`注册事件监听器，给装饰的函数添加传参`data`，就可以接收数据了

接下来，为了实现客户端消息可控的回声服务器，需要确保socketio不会阻塞到`input`函数的标准输入输出——可以使用`threading`及`threaing.Event`将`input`分离到其他线程：
```Python
sio = socketio.Client()
stop_input_thread = threading.Event() # 用于停止输入线程的事件

def input_thread():
    while not stop_input_thread.is_set():
        try:
            msg = input(f"{Fore.BLUE} 请输入要发送的消息: \n{Style.RESET_ALL}")
            if msg.lower() == 'exit':
                logger.info(f"{Fore.YELLOW}用户请求退出，断开连接...{Style.RESET_ALL}")
                sio.disconnect()
                break
            sio.emit('message', msg)
        except EOFError: # 处理Ctrl+D
            logger.info(f"{Fore.YELLOW}检测到EOF，断开连接...{Style.RESET_ALL}")
            sio.disconnect()
            break
        except Exception as e:
            logger.error(f"{Fore.RED}输入线程发生错误: {e}{Style.RESET_ALL}")
            break

@sio.event
def connect():
    logger.info(f"{Fore.GREEN}连接成功!{Style.RESET_ALL}")
    # 连接成功后启动输入线程
    threading.Thread(target=input_thread, daemon=True).start()

@sio.event
def disconnect():
    logger.info(f"{Fore.RED}断开连接!{Style.RESET_ALL}")
    stop_input_thread.set() # 设置事件以停止输入线程
```
由于`input`被分离到了子线程中，因此，需要确保子线程在父进程（也就是客户端进程）结束之后正确终止。在这里使用`threading.Event`**作为一种线程间通信机制，用来安全地停止我们创建的输入线程**
> [`threading.Event`](https://docs.python.org/zh-cn/3/library/threading.html#event-objects "https://docs.python.org/zh-cn/3/library/threading.html#event-objects") 是 Python [`threading`](https://docs.python.org/zh-cn/3/library/threading.html "https://docs.python.org/zh-cn/3/library/threading.html") 模块提供的一个同步原语。它维护一个内部标志（flag），这个标志可以被设置为 `True` 或 `False`。

它主要有下面四个方法：
- [`set()`](https://docs.python.org/zh-cn/3/library/threading.html#threading.Event.set "https://docs.python.org/zh-cn/3/library/threading.html#threading.Event.set")：将内部标志设置为 `True`。
- [`clear()`](https://docs.python.org/zh-cn/3/library/threading.html#threading.Event.clear "https://docs.python.org/zh-cn/3/library/threading.html#threading.Event.clear")：将内部标志设置为 `False`。
- [`is_set()`](https://docs.python.org/zh-cn/3/library/threading.html#threading.Event.is_set "https://docs.python.org/zh-cn/3/library/threading.html#threading.Event.is_set")：检查内部标志是否为 `True`。
- [`wait(timeout=None)`](https://docs.python.org/zh-cn/3/library/threading.html#threading.Event.wait "https://docs.python.org/zh-cn/3/library/threading.html#threading.Event.wait")：阻塞当前线程，直到内部标志变为 `True`，或者达到超时时间。

在上面的代码中，客户端在`connect`成功后就会启动`input_thread`进程，进程内部，`while`循环检查`stop_input_thread`标志是否设置为`True`，若为`False`则进入循环，`input`函数等待用户输入同时阻塞其所在的子线程，而socketio主线程不受干扰
客户端断开连接后使用`set()`方法将`stop_input_thread`标志设置为`True`，进而通过`threading`进行进程间通信，通知`input_thread`退出，确保子线程资源得到回收
![](assets/Pasted%20image%2020250911222015.png)
但是，因为线程的无限循环和主线程本身就不同步，因此，`input`的提示词总会在主线程打印日志之前输出……
![](assets/Pasted%20image%2020250911224156.png)
为了修正消息顺序，我们可以添加一个新的标志（这里是`continue_input_thread`），加在`input_thread`函数中，`input`的前面，使用`wait()`方法阻塞线程，等待主线程给出`True`（调用`set()`方法）信号
![](assets/Pasted%20image%2020250911224315.png)
现在代码全貌如下：
```Python
from misc.toollib import config, get_logger
logger = get_logger()

from colorama import Fore, Back, Style, init
init() # 初始化终端样式

# 创建一个针对Flask-Websocketio的简易客户端
import socketio
import threading
import time

sio = socketio.Client()
stop_input_thread = threading.Event() # 用于停止输入线程的事件
continue_input_thread = threading.Event() # 用于继续输入线程的事件

def input_thread():
    while not stop_input_thread.is_set():
        continue_input_thread.wait() # 等待主线程或其他地方发出可以继续输入的事件
        try:
            msg = input(f"{Fore.BLUE} 请输入要发送的消息: \n{Style.RESET_ALL}")
            if msg.lower() == 'exit':
                logger.info(f"{Fore.YELLOW}用户请求退出，断开连接...{Style.RESET_ALL}")
                sio.disconnect()
                break
            sio.emit('message', msg)
            # 发送消息后暂停输入线程
            continue_input_thread.clear() # 清除事件以暂停输入线程
        except EOFError: # 处理Ctrl+D
            logger.info(f"{Fore.YELLOW}检测到EOF，断开连接...{Style.RESET_ALL}")
            sio.disconnect()
            break
        except Exception as e:
            logger.error(f"{Fore.RED}输入线程发生错误: {e}{Style.RESET_ALL}")
            break
input_thread_controller = threading.Thread(target=input_thread, daemon=True)

@sio.event
def connect():
    logger.info(f"{Fore.GREEN}连接成功!{Style.RESET_ALL}")
    sio.emit('my event', {'data': 'Hello from client!'})
    # 连接成功后启动输入线程
    input_thread_controller.start()
    # 输入线程进入阻塞状态后暂停输入线程
    continue_input_thread.set() # 设置事件，发送信号，放行输入线程

@sio.event
def disconnect():
    logger.info(f"{Fore.RED}断开连接!{Style.RESET_ALL}")
    stop_input_thread.set() # 设置事件以停止输入线程
    continue_input_thread.clear() # 清除事件以暂停输入线程

@sio.on('available_events')
def receive_available_events(data):
    logger.info(f"{Fore.CYAN}接收到可用事件: {data}{Style.RESET_ALL}")

@sio.on('echo')
def receive_echo(data):
    logger.info(f"接收到回显消息: {Fore.MAGENTA}{data}{Style.RESET_ALL}")
    # 现在放行输入线程
    continue_input_thread.set()

def run_socketio_client():
    server_host, server_port = config.server.host, config.server.port
    while True:
        try:
            logger.info(f"{Fore.YELLOW}尝试连接到 ws://127.0.0.1:{server_port}...{Style.RESET_ALL}")
            sio.connect(f'ws://127.0.0.1:{server_port}', wait=True) # wait=True 确保连接成功或失败才继续
            sio.wait() # 等待客户端断开连接
            break # 客户端断开连接后退出循环
        except socketio.exceptions.ConnectionError as e:
            logger.error(f"{Fore.RED}连接失败: {e}{Style.RESET_ALL}")
            logger.info(f"{Fore.YELLOW}5秒后自动重新尝试连接...{Style.RESET_ALL}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"{Fore.RED}发生未知错误: {e}{Style.RESET_ALL}")
            logger.info(f"{Fore.YELLOW}5秒后自动重新尝试连接...{Style.RESET_ALL}")
            time.sleep(5)

if __name__ == '__main__':
    try:
        run_socketio_client()
    except KeyboardInterrupt:
        logger.info(f"{Fore.YELLOW}用户中断，退出程序...{Style.RESET_ALL}")
    finally:
        stop_input_thread.set() # 确保在程序退出时停止输入线程
        continue_input_thread.set() # 确保在程序退出时暂停输入线程
        # 解除input_thread_controller的守护线程状态
        if sio.connected:
            sio.disconnect()

```
程序会在连接成功后*放行输入线程* ：
```Python
@sio.event
def connect():
    logger.info(f"{Fore.GREEN}连接成功!{Style.RESET_ALL}")
    # 连接成功后启动输入线程
    input_thread_controller.start()
    # 输入线程进入阻塞状态后暂停输入线程
    continue_input_thread.set() # 设置事件为True，发送信号，放行输入线程
```
断开连接现在不仅要设置`stop_input_thread`为`True`，还要设置`continue_input_thread`为`False`，以防客户端有重连的需求（当然，我这里没有）：
```Python
@sio.event
def disconnect():
    logger.info(f"{Fore.RED}断开连接!{Style.RESET_ALL}")
    stop_input_thread.set() # 设置事件以停止输入线程
    continue_input_thread.clear() # 清除事件以暂停输入线程
```
为了确保先打印回显日志再给出提示词，程序会在打印日志后才将`continue_input_thread`设置为`True`：
```Python
@sio.on('echo')
def receive_echo(data):
    logger.info(f"接收到回显消息: {Fore.MAGENTA}{data}{Style.RESET_ALL}")
    # 现在放行输入线程
    continue_input_thread.set()
```




***
# 页面尾部