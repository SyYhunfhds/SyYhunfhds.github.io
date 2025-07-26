---
title: 八个让我不再手写轮子的Python库
category:
  - Medium
  - 搬运
author: Abdur Rahman - https://medium.com/@abdur.rahman12
date: 2025-07-25
footer: |-
  原文来自：https://python.plainenglish.io/8-python-libraries-so-good-i-stopped-writing-my-own-scripts-8b5cca0d6aa1
  请支持原作者
tags:
  - Medium
  - 搬运
  - Python
  - Programming
  - Data-Science
  - MariaDB
  - Technology
aliases:
  - 8 Python Libraries So Good, I Stopped Writing My Own Scripts
---
:::important 版权声明
**原作者**：Abdur Rahman
**他的Medium主页**：https://medium.com/@abdur.rahman12
**原文标题**：Python in Plain English - 8 Python Libraries So Good, I Stopped Writing My Own Scripts
**原文链接**：https://python.plainenglish.io/8-python-libraries-so-good-i-stopped-writing-my-own-scripts-8b5cca0d6aa1
:::
:::warning
原文为**Member Only**限制级阅读
:::
[[toc]]
***
## 前言
斯认为，我曾是这样一个人——一个坚持从零开始造轮子的人。需要一个JSON转CSV转换器？我当场写一个出来！需要一个快捷CLI告示板？给我三十分钟，我去去vim就回来！

但随着时间推移，我已经意识到尽管拿Python造轮子是一件令人怡然的事（是的，这有点 *凡尔赛* 了），却并不总是一件**明智之举**，特别是已经有人把我的想法写了出来，测试过边界条件，然后封装进干净的API的情况

所以现在，我将要介绍下面的八个Python库为什么这么好用，以至于我的小脚本直接变成了路边一条。这8个Python库不只是受欢迎的库，也是因为它们久经考验、设计规范，优雅地解决了实际开发中的阵痛。不论你是在构建工具、自动化工作流亦或者只是赶紧把活儿干完，免得凌晨两点还在debug 剪不断理还乱的代码，你都可以试试下面这些Python库

## 1. `Rich` —— CLI不是 *丑陋* 的代名词
**Rich**（带着**style**）让你的CLI输出不再是Windows95风格的上古文物

只需一行导入语句，你的终端输出将如有Figma加持一般让人眼前一亮。Rich提供了很多组件：表格、Markdown渲染、语法高亮堆栈跟踪、进度条，应有尽有，琳琅满目，应接不暇……
```Python
from rich.console import Console  
console = Console()  
console.print("Hello, [bold magenta]world[/bold magenta]!")
```

✔*可以用在哪里*：**打印**不再让你看得眼花的**日志**
🧠*高级用法*：`rich.traceback.install`让味同嚼蜡的Python原版堆栈跟踪变得华丽（Gorgeous）和充满blingbling的富文本——开箱即用，无需其他配置

## 2. `Typer` —— 不会卡壳的CLI工具的最速构建传说
我喜欢`argparse`。我真心的，我不是在说反话。但我也确实喜欢`Typer`

基于`Click`开发的`Typer`让CLI工具开发变得有如玩泥巴一样简单，只需排列组合**函数签名**和**类型注解**即可。添加docstrings便是在编写`--help`参数。
```Python
import typer  
  
def main(name: str):  
    typer.echo(f"Hello {name}")  
  
if __name__ == "__main__":  
    typer.run(main)
```

✔*可以用在哪里*：写API两小时，写CLI五分钟
💡为什么这很重要：
	- **类型注解**即为更好的**自动补全**
	- **docstrings** = 少花点时间翻看`--help`

:::info 评论搬运
**Paul Robello**：
>如果你想开发一个TUI（文本形式的用户界面），那么我会推荐基于`Rich`构建的`Textual`


:::
## 3.`Pendulum` —— `datatime`会背叛你，但`Pendulum`不会
你是否曾经尝试过在Python中导出两个`datetime`对象然后……发现结果好像有点不对劲？是的，我也一样。来试试`Pendulum`吧——`datetime`的替代品，一样能**时区**，**格式化时间**、**持续时间**和**历法**，还能像大人一样算数

```Python
import pendulum  
  
dt = pendulum.now("UTC").add(days=3)  
print(dt.to_datetime_string())
```

✔*可以用在哪里*：
- **定时运行脚本**
- **处理时区**
- **省出摸鱼的时间**
📌*你知道吗？*
- `Pendulum`可以格式化人类可读的时间字符串（比如不同语言下的`next Thursday at 5pm`）
## 4. `Pydantic` —— 无需猴戏（Ceremony）的强大的类型装饰库
我曾经手动校验JSON（轻喷）……然后，我发现了`Pydantic`，使用类型注解定义一个类，Pydantic便会自动完成解析、存档和校验工作

```Python
from pydantic import BaseModel  
  
class User(BaseModel):  
    id: int  
    name: str  
    is_active: bool = True
```

✔*用在哪里*：校验API响应、配置信息和用户输入
⚠*注意看*：Pydantic已经成为FastAPI的核心骨。那么Web的其他领域呢？仍然有待Pydantic的发掘
## 5. `Faker` —— 真实数据要么繁杂乱麻要么不适合测试使用
不论是在模拟API、测试dev数据库，或是尝试生成具有可信度的用户数据（当然，不要用于非法目的），`Faker`都能做到这些

```Python
from faker import Faker  
fake = Faker()  
print(fake.name(), fake.email(), fake.address())
```

✔*用在哪里*：生成随机假数据
😂*P.S.*：相信我，试一下生成 *海盗的姓名* （*Pirate names*）
:::info 译者的疑问
*Pirate names*是有什么俚语意义吗？
:::
## 6. `Tqdm` —— 专为不耐烦的人准备的进度条
你可能已经听说过`Tqdm`的大名，但如果你还没有用过，那我们可能要坐下来好好谈谈了。

`Tqdm`能包裹任何可迭代的对象，并显示一个智能的、响应式的进度条。非常适合**循环**、**下载**或**查看大文件**的任务（不用看着阻塞的CLI发呆）

```Python
from tqdm import tqdm  
for i in tqdm(range(10000)):  
    pass
```

✔*用在哪里*：任何耗时**大于0.5秒**的任务
🔨*调试技巧*：帮助你及早发现死循环

:::tip 译者补充
`Tqdm`本身不是**线程安全**的。需要**异步支持的进度条**，请移步`aiotqdm`；需要**多线程支持的进度条**，请移步`alive_progess`
:::
## 7. `Requests-HTML` —— 让Web爬虫不再令人抓耳挠腮
我喜欢`requests`，也厌倦`BeautifulSoup`，但`requests-html`呢？我的至爱！

 `requests-html`继承了`requests`的简洁易用和无头浏览器的强大解析能力。
==它使用`JS`⚠渲染，意味着我们可以简单实现现代化爬虫==

```Python
from requests_html import HTMLSession  
  
session = HTMLSession()  
r = session.get('https://example.com')  
r.html.render()  
print(r.html.find('h1')[0].text)
``` 

✔*用在哪里*：爬取网页，但又不想使用传统的HTML解析器
⚡*有趣的事实*：它底层使用了`Pyppeteer`。Python中调用JS渲染——Selenium可以扔路边了

:::info Pyppeteer
*Kimi K2生成*
**Pyppeteer** 是 **Puppeteer** 的 Python 非官方移植版，用于通过 **DevTools 协议** 控制 **无头 Chrome 或 Chromium** 浏览器。它允许开发者以编程方式自动化浏览器操作，如页面抓取、表单提交、截图、PDF 生成等。
Pyppeteer 的更新频率较低，可能滞后于 Puppeteer 的新特性；若需更活跃的维护，可考虑 **Playwright**（支持 Python，功能更强大）。首次运行时会自动下载 Chromium，可能因网络问题失败（需手动配置镜像或跳过）。
:::

:::info 搬运评论
![](assets/Pasted%20image%2020250726114930.png)
> 它有什么安全性能考量吗？这不禁令我担心，当`requests-html`渲染网站的代码时，它会在我的进程里跑什么奇奇怪怪的妙妙代码

:::
## 8. `Loguru` —— 让日志调试不再如同杂物活一般令人烦躁

Python标准`logging`库的配置未免有些太详细了……也有点反直觉。试试`loguru`吧，让写日志就像写日记一样简单——还有不同等级的日志、开箱即用的文件轮转和彩色输出

```Python
from loguru import logger  
  
logger.add("debug.log", rotation="1 MB")  
logger.info("Processing started...")
```

✔*用在哪里*：调试、开发环境日志……以及优质睡眠
👀*你知道吗？* 一行代码取代`print()`调用和繁杂的日志系统配置

## 尾声 && 联系方式
>[让Python运行飞快！🚀点击下载你的免费终极Python作弊指南](https://arconfusionnnn.systeme.io/the-ultimate-python-cheat-sheet)

*如果你喜欢原作者的文章，请帮原作者达成50赞目标！请关注原作者，跟踪最新博文——订阅原作者的个人主页以获取每日必读更新*

*再次感谢阅读*

:::info 译者注
Medium的*赞* 指的是 *Claps*
:::
## 致谢
**感谢你成为社区（白话说Python）的一员**
在你离开页面之前，请：
- **点赞**并**关注**原作者👏
- 关注社区：
	- [X](https://x.com/inPlainEngHQ)
	- [领英](https://www.linkedin.com/company/inplainenglish/)
	- [油管](https://www.youtube.com/@InPlainEnglish)
	- [Newsletter](https://newsletter.plainenglish.io/)
	- [Podcast](https://open.spotify.com/show/7qxylRWKhvZwMz2WuEoua0)
	- [Twitch](https://twitch.tv/inplainenglish)
- [**使用Differ平台创建属于你的免费AI赋能博客**🚀](https://differ.blog/)
- [**加入社区的内容创作者DIS频道**](https://discord.gg/in-plain-english-709094664682340443)
- 更多内容，请访问[plainenglish.io](https://plainenglish.io/)和[stackademic.com](https://stackademic.com/)