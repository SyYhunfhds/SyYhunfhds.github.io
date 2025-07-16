---
title: PromptTookit学习笔记
date: 2025-07-15
category:
  - Python
footer: 翻译自Prompt-Toolkit官方文档
---
[[toc]]
## Intro
>prompt_toolkit is a library for building powerful interactive command line and terminal applications in Python.
>It can be a very advanced pure Python replacement for [GNU readline](https://tiswww.case.edu/php/chet/readline/rltop.html), but it can also be used for building full screen applications.
### 参考资料
- [官方文档](https://python-prompt-toolkit.readthedocs.io/en/stable/)
- [维基百科 - ANSI转义序列](https://zh.wikipedia.org/wiki/ANSI%E8%BD%AC%E4%B9%89%E5%BA%8F%E5%88%97)
### 安装
```python
# pip
pip install prompt_toolkit
# conda
conda install -c https://conda.anaconda.org/conda-forge prompt_toolkit
```
### 一个小栗子
```Python
# https://python-prompt-toolkit.readthedocs.io/en/stable/pages/getting_started.html
from prompt_toolkit import prompt

text = prompt("Give me some input: ")
print(f"You said: {text}")
```
![](assets/Pasted%20image%2020250715224127.png)

## 打印格式化文本
`prompt_toolkit`的`print_formatted_text()`函数兼容Python内置`print`函数，但同时也支持**有色文本**和**格式化文本**
### 打印纯文本
导入`print_formatted_text()`函数
```Python
from prompt_toolkit import print_formatted_text

print_formatted_text('Hello world')
```
当然……也可以直接覆盖内置的`print`函数：
```Python
from prompt_toolkit import print_formatted_text as print

print('Hello world')
```

![](assets/Pasted%20image%2020250715225116.png)
效果和`print`一样

:::tip
对于Python 2，请先导入下面的函数，否则没法导入名为`print`的函数：
```Python
from __future__ import print_function
```
:::
### 格式化打印
`prompt-toolkit`支持有色打印下面四种（格式化）文本：
-  **`HTML`** 对象
- 包含 ANSI 转义序列的 **`ANSI`** 对象
- `list[tuple(style,text)]`对象
- 使用`Pygments.Token`封装的`list[tuple(pygments,.Token, text)]`对象
#### HTML
`HTML`对象用于定义一个拥有**伪HTML标签**的字符串，可以使用**粗体**、**斜体**和**下划线**三种字体，分别对应三种基础的HTML标签`<b>`、`<i>`和`<u>`：
```Python
from prompt_toolkit import print_formatted_text, HTML

print_formatted_text(HTML('<b>This is bold</b>'))
print_formatted_text(HTML('<i>This is italic</i>'))
print_formatted_text(HTML('<u>This is underlined</u>'))
```
![](assets/Pasted%20image%2020250715230009.png)

亦可以使用`<xxx>`标签指定**前景色**：
```Python
# Colors from the ANSI palette.
print_formatted_text(HTML('<ansired>This is red</ansired>'))
print_formatted_text(HTML('<ansigreen>This is green</ansigreen>'))

# Named colors (256 color palette, or true color, depending on the output).
print_formatted_text(HTML('<skyblue>This is sky blue</skyblue>'))
print_formatted_text(HTML('<seagreen>This is sea green</seagreen>'))
print_formatted_text(HTML('<violet>This is violet</violet>'))
```
![](assets/Pasted%20image%2020250715230144.png)
上面的`<ansired>`和`<skyblue>`都是Prompt-Toolkit封装好的**语义化标签**
ANSI语义标签的格式是`ansi + bright(可选) + 颜色名称`，比如：

| 颜色 (中文名)      | 标准强度标签          | 高强度/亮色标签                             |
| :------------ | :-------------- | :----------------------------------- |
| 黑色 (Black)    | `<ansiblack>`   | `<ansibrightblack>` (或 `<ansigray>`) |
| 红色 (Red)      | `<ansired>`     | `<ansibrightred>`                    |
| 绿色 (Green)    | `<ansigreen>`   | `<ansibrightgreen>`                  |
| 黄色 (Yellow)   | `<ansiyellow>`  | `<ansibrightyellow>`                 |
| 蓝色 (Blue)     | `<ansiblue>`    | `<ansibrightblue>`                   |
| 洋红色 (Magenta) | `<ansimagenta>` | `<ansibrightmagenta>`                |
| 青色 (Cyan)     | `<ansicyan>`    | `<ansibrightcyan>`                   |
| 白色 (White)    | `<ansiwhite>`   | `<ansibrightwhite>`                  |
![](assets/Pasted%20image%2020250715231608.png)
而256色调色板语义标签就没有这么有规律了。可以使用下面的代码打印查看：
```Python
# Gemini 2.5 Pro
from prompt_toolkit.styles.named_colors import NAMED_COLORS

# 为了方便查看，每行打印10个
count = 0
for color_name in sorted(NAMED_COLORS.keys()):
    print(f'{color_name:<20}', end='')
    count += 1
    if count % 10 == 0:
        print()
print()
```

可以使用`fg`和`bg`属性分别定义**前景色**和**背景色**：
```Python
# Colors from the ANSI palette.
print_formatted_text(HTML('<aaa fg="ansiwhite" bg="ansigreen">White on green</aaa>'))
```
![](assets/Pasted%20image%2020250715232049.png)

所有HTML标签都有对应的`stylesheet`标签——因此，可以使用`Style.from_dict`自定义标签
```Python
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style

style = Style.from_dict({
    'aaa': '#ff0066',
    'bbb': '#44ff00 italic',
})

print_formatted_text(HTML('<aaa>Hello</aaa> <bbb>world</bbb>!'), style=style)
```
![](assets/Pasted%20image%2020250715232456.png)
#### ANSI
`prompt_toolkit`也支持**VT100 ANSI转义序列**：
```Python
from prompt_toolkit import print_formatted_text, ANSI

print_formatted_text(ANSI('\x1b[31mhello \x1b[32mworld'))
```
![](assets/Pasted%20image%2020250716172910.png)
#### `(style, text)`元组
**HTML**和**ANSI**对象都是绑定在`list[(style, text)]`上的。使用`FormattedText`对象可以自定义`(style, text)`列表：
```Python
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText

text = FormattedText([
    ('#ff0066', 'Hello'),
    ('', ' '),
    ('#44ff00 italic', 'World'),
])

print_formatted_text(text)
```
![](assets/Pasted%20image%2020250716173126.png)

类似于**HTML**对象，`FormattedText`类也支持分别定义字体格式和样式：
```Python
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style

# The text.
text = FormattedText([
    ('class:aaa', 'Hello'),
    ('', ' '),
    ('class:bbb', 'World'),
])

# The style sheet.
style = Style.from_dict({
    'aaa': '#ff0066',
    'bbb': '#44ff00 italic',
})

print_formatted_text(text, style=style)
```
![](assets/Pasted%20image%2020250716173734.png)
#### Pygments `(Token, text)` 元组
#### `to_formatted_text()`
`to_formatted_text()`函数确保给定输入是**有效的格式化文本**，与此同时，还可以添加自定义样式：
```Python
from prompt_toolkit.formatted_text import to_formatted_text, HTML
from prompt_toolkit import print_formatted_text

html = HTML('<aaa>Hello</aaa> <bbb>world</bbb>!')
text = to_formatted_text(html, style='class:my_html bg:#00ff00 italic')

print_formatted_text(text)
```
![](assets/Pasted%20image%2020250716174021.png)
## Prompt 请求用户输入
使用`prompt()`函数请求用户输入，下面是一个简单的例子
![](assets/Pasted%20image%2020250716174409.png)
`prompt()`函数有很多配置项，下面我们一个一个来试试看
### `PromptSession`
当你需要调用多个`prompt`函数，这些`prompt()`又都共享同一套参数时，可以使用`PromptSession`，然后在`PromptSession`实例下调用`prompt()`即可：
```Python
from prompt_toolkit import PromptSession

session = PromptSession()
loop_length = 3
texts = [None] * loop_length
for _ in range(loop_length):
    texts[_] = session.prompt('Enter some text: ')
session.app.exit()  # Exit the session after input
for i, text in enumerate(texts):
    print(f'You entered: {text} (index: {i})')
```
![](assets/Pasted%20image%2020250716175618.png)
:::tip 小剧场
`PromptSession`不能使用**上下文管理器**
![](assets/Pasted%20image%2020250716175410.png)
:::
更进一步地，可以在连续多个调用的`prompt()`之间回溯输入历史
### 语法高亮
*添加语法高亮和添加 `lexer` 一样简单*。所有的`Pygments`**语法分析器(lexer)** 在使用`PygmentsLexer`  对象`wrap`之后都可以正常使用。也可以通过实现`Lexer`抽象父类来自定义语法分析器：
```Python
from pygments.lexers.html import HtmlLexer
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.lexers import PygmentsLexer

text = prompt("Enter HTML: ", lexer=PygmentsLexer(HtmlLexer))
print(f"You said: {text}")
```
![](assets/Pasted%20image%2020250716180346.png)

默认的Pygments语法分析器也是Prompt-Toolkit的默认样式的一部分。如果想使用其他Pygment样式和语法分析器，可以参考下面的例子：
```Python
from pygments.lexers.html import HtmlLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls

style = style_from_pygments_cls(get_style_by_name("monokai"))
text = prompt(
    "Enter HTML: ",
    lexer=PygmentsLexer(HtmlLexer),
    style=style,
    include_default_pygments_style=False
)
print(f"You said: {text}")
```
:::tip
这里传入`include_default_pygments_style=False`是因为默认情况下两种样式会被合并到一起，这可能会导致我们自己传入的语法分析器的行为出现些许差异
:::
### 颜色

***
## 页面尾部