---
title: 六个让Python运行飞快的库，我已经抛弃Multithreading
category:
  - 搬运
  - Medium
tags:
  - 搬运
  - Python
author: Abdur Rahman - https://medium.com/@abdur.rahman12
footer: 版权及浏览收益为原作者所有。如侵犯版权，请通知译者尽快删除
---
:::important
- **原作者**：Abdur Rahman
- **原作者的Medium主页**：https://medium.com/@abdur.rahman12
- **原文标题**：**6 Python Libraries So Fast, I Stopped Using Multithreading**
- **原文链接**：[https://python.plainenglish.io/6-python-libraries-so-fast-i-stopped-using-multithreading-9f80e914ed2c](https://python.plainenglish.io/6-python-libraries-so-fast-i-stopped-using-multithreading-9f80e914ed2c)
:::
:::warning
原文为**Member Only**限制级阅读。如有版权侵犯，译者将尽快删除译文
:::
[[toc]]
## 引言
首先要明确一点：**Python不以性能而著称**，相反，**它以可读性、简洁性和使用`IndentationError`折磨你到凌晨两点而知名**

但如果我告诉你确实有Python库能让Python性能一步登天，你可以在抛弃`multithreading`、`multiprocessing`，甚至是`Cython`的同时暴打`benchmark`测试？

这些并不是你的每日Github头版第三方库，而是十分高效的、在底层优化Python性能的库，它们会迫使你询问自己到底需不需要高并发运行。

让我们开始吧。

## 正文
### 1. `Polars` —— 薄纱`Pandas`的数据处理库
Rust编写，跑起来像C++，用起来像`Pandas`

如果你以前用过`Pandas`，发现`Pandas`尽管强大但也运行得有点慢，那么欢迎来到`Polars`的世界

`Polars`是专注于高性能的数据处理库。当`Pandas`被数个GB的数据集噎住时，`Polars`只会 *呵呵一笑*。

```Python
import polars as pl

df = pl.read_csv("big_data.csv")
filtered = df.filter(pl.col("views") > 1000)
print(filtered.head())
```

**为什么`Polars`杀死了游戏：**
- Lazy - 执行查询（和`Spark`类似，但要 *快得多* ）
- 内置多线程 —— 无需编写额外的多线程操作逻辑
- 处理数据时**零拷贝**

###  2. `Numba` —— JIT编译魔法
写的是Python，得到的是C语言的性能。没有依赖地狱

`Numba` 就好像是专为作弊而生的库。只需要用装饰器装饰一下函数，函数立刻跑得百倍甚至十倍得快。也不需要切换上下文，不需要线程池，只需要纯粹的JIT编译机制

```Python
from numba import njit

@njit
def heavy_computation(arr):
	total = 0.0
	for x in arr:
		total += x ** 0.5
	return total
```

**为什么`Numba`这么腻害：**
- LLVM赋能
- 支持非常规NumPy
- 不需要展开循环或向量化操作

只使用`@njit`装饰器便能将一个纯Python实现的斐波那契数列的运行时间从`1.2s`降至`0.01s`

### 3. `Orjson` —— 曲速JSON解析库
比`json`快10倍，比`ujson`快2倍的JSON序列化库

Rust编写的`Orjson`不只是一般地快，而是史诗级地快。`Orjson`使用SIMD加速、预分配内存池，以及底层支持的零拷贝反序列化实现了这般恐怖的性能

```Python
import orjson

data = {"id": 123, "title": "Python is fast?"}
json_bytes = orjson.dumps(data)
parsed = orjson.loads(json_bytes)
```

**为什么说`Orjson`杀死了比赛：**
- 原生支持`datetime`时间和`numpy`数组
- 输出`UTF-8`编码的字节
- 暴打`json`的序列化性能

*一个`50MB`的JSON载荷，`osjson`只用了42毫秒便完全序列化，而标准`json`库则使用了480毫秒。这不只是快，这已经是范式转变了*

### 4. `PyO3 + Rust` —— 当你需要系统级的性能时
如果你想用`Rust`编写业务的核心部分……染后像调用Python函数一样调用它呢？

如果你还没有试过`PyO3`，那么你就无法不费吹灰之力编写 *原生插件* 。用`Rust`编写性能敏感型任务，然后在`Python`里调用它——于是，你便获得了牺牲Python工程效率才能得到的即时性能

```Python
#[pyfunction]  
fn double(x: usize) -> usize {  
    x * 2  
}
```
```Python
from fastlib import double  
print(double(21))  # Outputs: 42
```

**为什么`PyO3`这么快：**
- 零运行时损耗
- 原生多线程和内存管理
- 在`Dropbox`、`Cloudflare`甚至是`Python` 中都有使用

***使用示例**：我基于Rust写了一个PyO3函数来处理Python中的大型字符串正则匹配，实现了150倍的性能飙升*

### 5. `Blosc` —— 非法超快压缩
比磁盘I/O还要快的压缩和解压缩

`Blosc` 是专门用于二进制数据（比如NumPy数组）设计的高性能压缩库。`Blosc`不止会压缩数据，还解压缩快得遥遥领先，比从磁盘中读取未压缩的数据都要快

```Python
import blosc
import numpy as np

arr = np.random.rand(1_000_000) .astype('float64')
compressed = blosc.compress(arr.tobytes(), typesize=8)
decompressed = np.frombuffer(blosc.decompress(compressed) , dtype='float64')
```

**为什么`Blosc`这么快：**
- 底层使用SIMD指令和多线程处理
- 比调用原生I/O要快得多的 压缩 -> 存储 -> 解压缩
- 转为内存敏感型或IO密集型负载而生

*使用`Blosc`辅助在多个服务之间传输 `Numpy` 数组 —— 你会获得巨大的性能提升，减少不必要的带宽消耗*

### 6. `Awkward Array` —— 专为复杂、嵌套、不统一的数据而生
专为取代`Pandas`而生

苦恼于解决嵌套列表或嵌套字典吗？`Awkward Array`专为非常规结构化数据而生，和`Pandas`处理2D表一样适用于差不多的情形，但`Awkward Array`要快得多

```Python
import awkward as ak

data = ak.Array([
	{"id": l, "tags": ["python", "fast"]},
	{"id": 2, "tags": ["performance"]},
])
print(data["tags"].count())
```

**为什么`Awkward Array`如此独特：**
- 专为无法适用传统表结构的数据设计
- 高性能的C++后端
- 常用于粒子物理学，但也可以用于其他领域

**使用示例**：如果你的API会返回不可预测的嵌套JSON，请不要再尝试展平它，请直接使用`Awkward Array`，更原生，也更快

***
## 文末
> [**快速掌握Python！🚀点击链接免费下载终极Python编程课程**](https://arconfusionnnn.systeme.io/the-ultimate-python-cheat-sheet)

_如果你喜欢我的博文，请助力我完成_ **_50_** **_赞目标！_** **_关注我_** _不要错过我的每一篇博文 —_ **_订阅_** _我的个人主页以跟踪最新的博文_

**_谢谢阅读！_**

### 感谢您成为白话说Python社区的成员

_在你离开页面之前：_

- 请记得**点赞**和**关注**作者 👏️**️**
- 关注社区: [**X**](https://x.com/inPlainEngHQ) | [**LinkedIn**](https://www.linkedin.com/company/inplainenglish/) | [**YouTube**](https://www.youtube.com/@InPlainEnglish) | [**Newsletter**](https://newsletter.plainenglish.io/) | [**Podcast**](https://open.spotify.com/show/7qxylRWKhvZwMz2WuEoua0) | [**Twitch**](https://twitch.tv/inplainenglish)
- [**在Differ上部署你的博客**](https://differ.blog/) 🚀
- [**加入我们的创作者Discord频道**](https://discord.gg/in-plain-english-709094664682340443) 🧑🏻‍💻
- 点击 [**plainenglish.io**](https://plainenglish.io/) + [**stackademic.com**](https://stackademic.com/) 浏览更多内容
