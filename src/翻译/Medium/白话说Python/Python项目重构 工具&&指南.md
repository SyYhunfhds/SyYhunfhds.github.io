---
title: 我只使用这8个工具便重构了五千行Python历史项目代码 - 自动化工具如何将我从屎山代码中拯救出来，并帮助我更快编写规模化代码
category:
  - 搬运
  - Python
  - Medium
tags:
  - 搬运
  - Medium
  - Python重构
  - Python开发规范
author: Abdul Ahad
footer: 版权及浏览收益为原作者所有。如侵犯版权，请通知译者尽快删除
---
:::important
- **原作者**：Abdul Ahad
- **原作者的Medium主页**：[https://medium.com/@abdul.ahadmahmood555?source=post_page---byline--db7f87b5bc1d---------------------------------------](https://medium.com/@abdul.ahadmahmood555?source=post_page---byline--db7f87b5bc1d---------------------------------------)
- **原文标题**：I Refactored 5,000 Lines of Legacy Python Using Just These 8 Tools
- **原文副标题**：How Automation Saved Me from Debugging Doom and Helped Ship
Production Code 10x Faster
- **原文链接**：[https://python.plainenglish.io/i-refactored-5-000-lines-of-legacy-python-using-just-these-8-tools-db7f87b5bc1d](https://python.plainenglish.io/i-refactored-5-000-lines-of-legacy-python-using-just-these-8-tools-db7f87b5bc1d)
:::
:::warning
原文为**Member Only**限制级阅读。如有版权侵犯，译者将尽快删除译文
:::
[[toc]]
## 引言
*长话短说*：重构代码不亚于打扫一个乱糟糟的后院——后院是起火的，代码是混乱的，维护者是已经离职的。我最近接手了一个五千行代码的Python 2.7仓库，没有测试样例、没有类型注解，没有版本控制，只有无力的程序员。

但有趣的地方来了：我并没有花费数周的时间清理这坨屎山，也没有一行一行重写代码——我选择将繁重的事交给冰冷的工具去做

下面是***八个帮助我无san速通重构Python屎山代码的工具***。如果你已经深陷技术债的池沼，那么这篇文章一定能帮你省下买 *妙界* 的钱

## 正文
### `Ruff` —— 让类型注解不再形如坐牢
忘记`flake8`和`pylint`吧！**Ruff** 使用Rust编写，运行飞快。我用它处理了一整个仓库，而它仅花了几秒钟就找到了类型错误

```shell
pip install ruff
ruff check .
```

我到底喜欢ruff的什么地方呢？它并不是单纯指出代码的问题——它会进行自动修正，代码里的多余逗号、不必要的导入语句、不使用的变量都会立刻消失得无影无踪

:::tip Pro Tip
*类型警告乃BUG之母， 不修好它们的话就等着老板来修理你吧*
:::
### `black` —— 人生苦短，我用`black`整理代码格式
我曾经还会关心一下函数参数什么时候应该有尾随的逗号，直到我发现了`black`，现在我看都不看代码格式一眼

```shell
black .
```

`black`会自动格式化项目中的每一个文件，一切都会突然变得养眼起来，就好像打开了闹鬼的房子的电灯

### `isort` —— 让你的导入语句变得和图书馆一样井然有序
你体验过那种代码里满是乱作一团的导入语句时的松弛感吗？`isort`可以立刻完成这样的杂务活

```shell
isort .
```

配合`black`，它们能使我的模块看起来就像是由真正关心加载顺序的人编写的一样。

:::tip **Bounus Tip**
在`pre-commit`阶段整合`black`+`isort`+`ruff`让你不再担心代码格式
:::

### `pyupgrade` —— 化干戈(Python2)为玉帛(python3)
还记得`print`是一个 *声明* 而不是一个 *函数* 的日子吗？亦或是`str.format()`与`f-string`的搏斗？

```shell
pip install pyuprade
pyupgrade --py38-plus **/*.py
```

`pyupgrade` 会遍历所有文件，并自动进行现代化语法改写。不到一分钟，上古代码便能摇身一变成为最时尚的“靓仔”

### `refurb` —— 最好心的Code Review助理
`Refurb`不是简单的类型注解修饰 —— 它进行的是***重构***。它会像得力队友一样，在看了你的代码后说，“嘿，你可以给这里换成列表推导式(*list comprehension*)。”

```shell
pip install refurb
refurb path/to/code
```

`refurb`能把握住我之前从没注意到的微小的性能损失，省去我数个小时的手动代码扫描

### `autoflake` —— 和未使用的导入语句和变量说再见吧
历史遗留代码和未使用的`import`语句常常狼狈为奸。就好像一个自 *Y2K* 以来就没有打扫过的车库。`autoflake`会使用精湛的手术操作移除所有不必要的代码

```shell
autoflake -in-place --remove-unused-variables --remove-all-unused-imports -r .
```

整理完之后，我的仓库从五千行代码锐减到4320行代码。这并非优化，而是*神迹*

### `rope` —— 强大的结构化重构工具
有时候只是重命名变量、提取方法也不一定够 —— 你还需要重构整个类乃至整个模块。`rope` 可以帮助你进行深度重构：

- 重命名了47个变量
- 提取出12个辅助函数
- 将整整3个类移动到新的模块

全部遵循最小拆包原则

:::tip **Rope Tip**
如果你需要可视化的帮助，请在`vscode`或`emcaes`里使用它
:::

### `pytest` + `coverage` —— 别猜，要测
没有被测试样例拷打过的代码清理注定是无法完成的。我会通过运行脚本、观察输出，根据预期行为编写测试样例来逆向研究函数

然后使用：

```shell
pytest --cov=.
```

来确保我的重构部分能够被程序所覆盖

:::tip **我的黄金原则**
如果你的代码没有经过单元测试修正，那就是不完美的。你只是还没吃过教训
:::
## 后面是作者的碎碎念
### 曾经我所避之不及的，如今成了可达的目标
在我拥抱自动化之前，重构代码就像是用刀叉切割黄油。现在呢？就好像在指挥一支镭射机器人大军。开发的秘诀不在于追求完美无瑕的代码，而在于编写可维护的代码——然后使用正确的工具实现完美的代码

### 快速回顾：八个拯救了我的代码
Let me break it down the way I wish someone had for me back when I was drowning in legacy Python.
当我坠入代码重构的深渊时，我曾经希望有人能以下面的方式拉我一把

First, I started with `**ruff**`, which instantly linted thousands of lines without breaking a sweat. It was like hiring a no-nonsense proofreader with a speed addiction.
我首先接触了`ruff`，帮助我无痛检查数千行代码的类型。`ruff`就像一个精益求精的任劳任怨的代码先锋

Then came `**black**` — the strict, opinionated formatter that enforced structure so I didn’t have to argue with myself (or teammates) over spaces and commas. It just did the job.
然后是`black` —— 严格的代码格式化工具，妈妈再也不用担心我会左右脑互搏了

Once the formatting was locked in, `**isort**` showed up to clean up my chaotic imports like Marie Kondo for Python files. Everything went exactly where it belonged.
代码格式确定下来之后，就该`isort`上场清理我混乱的导入语句了。

I followed that with `**pyupgrade**`, which felt like casting a time-travel spell over my code — turning archaic Python 2 constructs into shiny, modern Python 3 syntax. Goodbye `.format()`, hello f-strings.
接下来是`pyupgrade`，将古老的Python2结构变成最靓丽最时尚的Python3语法。再见`.format()`，你好`f-string`

For deeper insights, `**refurb**` whispered gentle nudges like, “You could really turn this into a list comprehension,” and I listened. It read my code like a mentor, pointing out spots I didn’t even think to improve.
而`refurb`则会低语，“你可以在这里换成列表推导式”，然后我会听取。它像一个保姆一样阅读我的代码，指出我根本就想不到可以优化的地方

Then I unleashed `**autoflake**` to vacuum up the junk: dead imports, unused variables, and the forgotten debris of past edits. It was surgical, precise, and very satisfying.
之后我又使用`autoflake`清除垃圾代码：不再使用的`import`语句、未使用的变量以及已经遗忘的代码。`autoflake`无疑是一位手法精湛的外科大夫

When I needed to restructure things — like moving classes or renaming 40 variables — `**rope**` became my scalpel. No more find-and-replace headaches or breaking code with manual changes.
而当我需要重构代码 —— 比如移动`class`或是重命名40个变量时，`rope`便成为了我的得力助手，我不再需要手动查找并替换变量名或是强行肢解代码

And of course, none of this would be complete without `**pytest**` paired with `coverage`. I wrote tests based on observed behavior and made sure that everything I changed was covered and protected from regressions.
当然，上述工作都需要`pytest + coverage`进行收尾。我会编写测试样例，并确保我的每一处改动都能被程序覆盖

Each of these tools served a distinct purpose, like members of a refactoring SWAT team. Used together? They turned an old, tangled mess into clean, maintainable, Pythonic beauty — in days, not weeks.
这八个工具的职责互不重合，就好像一支专门重构代码的团队一样，在几天之内（而不是数周之内）将尘封已久的、乱作一团的代码变成整洁的、可维护的、Pythonic美的项目

### 总结：不要 *我独自重构*
Automation isn’t just about laziness. It’s about consistency, safety, and speed. When you hand off the grunt work to these tools, you free up your brain to focus on _real_ problems: like architecture, performance, and user experience.
自动化不是懒惰的代名词，自动化关乎代码连续性、安全性和效率。当你将繁杂的工作丢给工具后，你便能专注于解决 *实际* 问题：比如架构、性能和用户体验

Want to be 10x faster at Python? **Automate your cleanup.**  
想要Python跑得飞快？**自动化你的代码清理**
Want to be respected by future you? **Refactor like a surgeon, not a sledgehammer.**
想要被未来的你称赞？**那就像剑客而不是巨武器大师一样重构你的代码**
#### **牢记**
> _“好的代码不是无以复加，而是无可失去.”_

现在拿上新的工具去打扫你吃灰的代码仓库吧

> ==**_“点击[这里](https://abdulahad28.gumroad.com/l/rwnlrm)获得一揽子加速Python开发的工具包==**_“
> 
> [**_Level Up Your Python Skills Instantly! 🐍 Download the Ultimate Python Cheat Sheet — 100% FREE & Beginner-Friendly!_**](https://abdul-ahadmahmood555.systeme.io/f23aa384)

**_If you want more conetnt like this follow me_** [**_Abdul Ahad_**](https://medium.com/u/92af3948e758)**_, also here are some links of my best ones do not forget to read them also.🥰_**

:::info NOTE:  
> IF YOU LIKED THE ARTICLE AND FOUND IT USEFUL, DO NOT FORGET TO GIVE 50 CLAPS 👏 ON THIS ARTICLE AND YOUR OPINION ABOUT THIS ARTICLE BELOW 💬_**

:::
## 来自白话说Python社区的一封信
**Hey,** [**Sunil**](https://linkedin.com/in/sunilsandhu) **here.** I wanted to take a moment to thank you for reading until the end and for being a part of this community.

Did you know that our team run these publications as a volunteer effort to over 200k supporters? **We do not get paid by Medium**!

If you want to show some love, please take a moment to **follow me on** [**LinkedIn**](https://linkedin.com/in/sunilsandhu)**,** [**TikTok**](https://tiktok.com/@messyfounder) **and** [**Instagram**](https://instagram.com/sunilsandhu). And before you go, don’t forget to **clap** and **follow** the writer️!


