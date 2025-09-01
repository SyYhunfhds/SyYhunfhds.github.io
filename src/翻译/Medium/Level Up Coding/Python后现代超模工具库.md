---
title: 2025年 Python超模标准工具库
author: Adam Green
footer: 版权及浏览收益为原作者所有。如侵犯版权，请通知译者尽快删除
tags:
  - 搬运
  - Medium
  - Python
date: 2025-02-17
---
:::info
- **原作者**：**Adam Green**
- **原作者个人主页**：[https://levelup.gitconnected.com/hypermodern-python-toolbox-2025-c336a534adb0](https://levelup.gitconnected.com/hypermodern-python-toolbox-2025-c336a534adb0)
- **原文标题**：**Hypermodern Python Toolbox 2025**
- **原文副标题**：## Python tools setting the standard in 2025.
- **原文链接**：[https://levelup.gitconnected.com/hypermodern-python-toolbox-2025-c336a534adb0](https://levelup.gitconnected.com/hypermodern-python-toolbox-2025-c336a534adb0)
:::
:::important
原文为**Member Only**会员制博文
:::
[[toc]]

## 前言
**Python生态系统的快速进化和壮大是每一位Python开发者都将面临的问题**😤
**Every Python developer is challenged by the size and velocity of the Python ecosystem** 😤
这篇帖子将清晰地介绍**Python超现代工具箱**——决定2025年Python开发标准的数个工具
This post provides clarity with a **Hypermodern Python Toolbox** — tools that are setting the standard for Python in 2025.
## 工具介绍
### Python 3.11
Python 3.11h和3.12 均为Python带来了性能提升，但在这里我选择Python 3.11的原因是Python 3.12在某些热点数据科学分析上还欠缺稳定
Python 3.11 and 3.12 have both brought performance improvements to Python. We choose 3.11 as 3.12 is still a bit unstable with some popular data science libraries.
日常开发往往需要处理海量的报错信息 —— 优化调试日志也有助于提高2025年的Python开发者的生活质量
So much of programming is reading & responding error messages — error message improvements are a great quality of life improvement for Python developers in 2025.
**Python 3.11 便添加了更好的堆栈跟踪** —— 添加了发生报错的精准堆栈位置，更加便利开发和调试
**Python 3.11 added better tracebacks** — the exact location of the error is pointed out in the traceback. This improves the information available to you during development and debugging.
下面是一段存在错误的代码。我们试图给`data`数组的第一个元素赋值，但代码实际上在尝试操作一个不存在的变量`datas`：
The code below has a mistake. We want to assign a value to the first element of `data`, but the code refers to a non-existent variable `datas`:

```Python
data = [1, 4, 8]  
# the variable datas does not exist!  
datas[0] = 2
```
在Python 3.10 及之前的版本中，Python只会报错`datas`变量不存在
With pre 3.10 versions of Python, this results in an error traceback that points out that the variable `datas` doesn't exist:

```Python
$ uv run --python 3.9 --no-project mistake.py  
Traceback (most recent call last):  
  File "/Users/adamgreen/data-science-south-neu/mistake.py", line 3, in <module>  
    datas[0] = 2  
NameError: name 'datas' is not defined
```
而Python 3.11 的堆栈诊断则做了进一步细化，并给出了解决方法，指出开发者应该转而调用`data`变量，并给出报错发生时的具体行号：
Python 3.11 takes its diagnosis two steps further and also offers a solution that the variable should be called `data` instead, and points out where on the line the error occurred:

```Python
$ uv run --python 3.11 --no-project mistake.py  
Traceback (most recent call last):  
  File "/Users/adamgreen/data-science-south-neu/mistake.py", line 3, in <module>  
    datas[0] = 2  
    ^^^^^  
NameError: name 'datas' is not defined. Did you mean: 'data'?
```

### uv
**学习Python最难的一件事在于学习安装 & 管理 Python**。即便是高级开发者也常会头疼于Python项目管理之复杂，特别是Python不是他们的“母语”的时候。
**The hardest thing about learning Python is learning to install & manage Python**. Even senior developers can struggle with the complexity of managing Python, especially if it is not their main language.
[**uv**](https://docs.astral.sh/uv/) **便是一款用于管理Python不同版本的工具**。uv是pyenv，miniconda或是直接下载Python等方式的替代品
[**uv**](https://docs.astral.sh/uv/) **is a tool for managing different versions of Python**. It’s an alternative to using pyenv, miniconda or installing Python from a downloaded installer.
uv 也可用来执行Python指令以及Python指定某个版本提供的脚本 —— 必要的话uv会自动下载Python。这极大降低了本地管理Python不同版本的复杂度
uv can be used to run Python commands and scripts with the Python version specified — uv will download the Python version if it needs to. This massively simplifies the complexity of managing different versions of Python locally.
下面的指令用于运行Python 3.12下的`hello world`
The command below runs a `hello world` program with Python 3.12:

```shell
$ uv run --python 3.12 --no-project python -c "print('hello world')"  
hello
```
==**uv亦可用于管理Python的虚拟环境**==——uv在这一点上也是venv或miniconda的替代品。虚拟环境会允许多个解释器环境（及其依赖库）独立运行，这使得本地管理不同项目成为可能
==**uv is also a tool for managing virtual environments in Python**==. It’s an alternative to venv or miniconda. Virtual environments allow separate installations of Python to live side-by-side, which makes working on different projects possible locally.
下面的指令演示了如何使用Python 3.11创建一个虚拟环境：
The command below creates a virtual environment with Python 3.11:

```shell
$ uv venv --python 3.11  
Using CPython 3.11.10  
Creating virtual environment at: .venv  
Activate with: source .venv/bin/activate
```
你还需要`$ source activate .venv/bin`激活虚拟环境
You will need to activate the virtual environment to use it with `$ source activate .venv/bin`.
**uv亦可用于管理Python依赖和第三方模块**。uv在这一点上是pip的替代品。pip，poetry、uv都可用于安装和升级Python模块
**uv is also a tool for managing Python dependencies and packages**. It’s an alternative to pip. Pip, Poetry and uv can all be used to install and upgrade Python packages.
下面是使用`pyproject.toml`管理uv项目的示例：
Below is an example `pyproject.toml` for a uv managed project:

```toml
[project]  
name = "hypermodern"  
version = "0.0.1"  
requires-python = ">=3.11,<3.12"  
dependencies = [  
    "pandas>=2.0.0",  
    "requests>=2.31.0"  
]  
  
[project.optional-dependencies]  
test = ["pytest>=7.0.0"]

Installing a project can be done by pointing `uv pip install` at our `pyproject.toml`:

$ uv pip install -r pyproject.toml  
Resolved 11 packages in 1.69s  
Installed 11 packages in 61ms  
 + certifi==2024.12.14  
 + charset-normalizer==3.4.0  
 + idna==3.10  
 + numpy==2.2.0  
 + pandas==2.2.3  
 + python-dateutil==2.9.0.post0  
 + pytz==2024.2  
 + requests==2.32.3  
 + six==1.17.0  
 + tzdata==2024.2  
 + urllib3==2.2.3
```
和poetry一样，uv也可以给依赖库枷锁：
Like Poetry, uv can lock the dependencies into `uv.lock`:

```shell
$ uv lock  
Resolved 17 packages in 5ms
```
uv 也可以用来给项目添加模块，并全局启用Python工具。下面安装Pytest的指令允许我们在任何地方使用其测试框架：
uv can also be used to add tools, which are globally available Python tools. The command below installs `pytest` as tool we can use anywhere:

```shell
$ uv tool install --python 3.11 pytest   
Resolved 4 packages in 525ms  
Installed 4 packages in 7ms  
 + iniconfig==2.0.0  
 + packaging==24.2  
 + pluggy==1.5.0  
 + pytest==8.3.4  
Installed 2 executables: py.test, pytest
```
这将在虚拟环境之外安装一个全局可用的pytest
This will add programs that are available outside of a virtual environment:

```
$ which pytest  
/Users/adamgreen/.local/bin/pytest
```
:::tip
*使用 `_.envrc_` 添加direnv工具，以便在进入一个目录时自动切换到正确的Python版本 *
_add the direnv tool with a_ `_.envrc_` _to automatically switch to the correct Python version when you enter a directory._
:::

### ruff
[**Ruff**](https://docs.astral.sh/ruff/) **用于标注类型和格式化Python代码** —— 是Black或autopep8之类的工具的替代品
[**Ruff**](https://docs.astral.sh/ruff/) **is a tool to lint and format Python code** — it is an alternatives to tools like Black or autopep8.
Ruff的最大的不同在于它是用Rust编写的 —— 所以Ruff很快。Ruff覆盖了Flake8规则的大部分，也引入了isort的一些规则
Ruff’s big thing is being written in Rust — this makes it fast. Ruff covers much of the Flake8 rule set, along with other rules such as isort.
下面的代码演示了三个问题：
The code below has three problems:

1. We use an undefined variable `datas`.
	1. 未定义的变量`datas`
2. It has imports in the wrong place.
	2. 在变量定义之后才引入模块
3. Imports something we don’t use.
	3. 导入了未使用到的模块

```python
data = datas[0]  
import collections
```
在脚本所在目录运行Ruff：
Running Ruff in the same directory points out the issues:

```shell
$ ruff check .  
ruff.py:1:8: F821 Undefined name `datas`  
ruff.py:2:1: E402 Module level import not at top of file  
ruff.py:2:8: F401 [*] `collections` imported but unused  
Found 3 errors.  
[*] 1 potentially fixable with the --fix option.
```
:::tip
*Ruff 快到能在热部署间隙运行 —— 所以请确保你在保存修改时已经格式化好了文本*
_Ruff is quick enough to run on file save during development — make sure you have formatting on save configured in your text editor!_
:::

### mypy
[**mypy**](http://www.mypy-lang.org/) **是一款用于强制规范Python类型的工具** —— 它是用于标注doc文档的数据类型的不二选择
[**mypy**](http://www.mypy-lang.org/) **is a tool for enforcing type safety in Python** — it’s an alternative to limiting type declarations to unexecuted documentation.
近年来Python也经历了类似于JS到TS的转变，静态类型检查在Python开发中逐渐占据核心位置。静态Python现在已经成为很多使用Python的开发团队的标准
Recently Python has undergone a similar transition to the Javascript to Typescript transition, with static typing becoming core to Python development (if you want). Statically typed Python is the standard for many teams developing Python in 2025.
静态类型校验可以发现常规单元测试无法发现的BUG。静态类型相比单文件测试会更在意执行路径 —— 也因此可以发现生产环境限定的边缘情况
Static type checking will catch some bugs that many unit test suites won’t. Static typing will check more paths than a single unit test often does — catching edge cases that would otherwise only occur in production.
下面的`mypy_error.py`存在一个问题 —— 尝试进行字符串对数字的除法：
`mypy_error.py` has a problem - we attempt to divide a string by `10`:

```Python
def process(user):  
    # line below causes an error  
    user['name'] / 10  
  
user = {'name': 'alpha'}  
process(user)
```
我们可以使用`mypy`来发现这一错误 —— 而不需要真正执行这段代码：
We can catch this error by running mypy — catching the error without actually executing the Python code:

```shell
$ mypy --strict mypy_error.py  
mypy_error.py:1: error: Function is missing a type annotation  
mypy_error.py:5: error: Call to untyped function "process" in typed context  
Found 2 errors in 1 file (checked 1 source file)
```
这里首先发现的错误是因为我们的代码没有添加类型注解 —— 我们可以添加下面两个注解
These first errors are because our code has no typing — we can add two type annotations to make our code typed:

1. `user: dict[str,str]` - `user` is a dictionary with strings as keys and values,
	1.  `user: dict[str,str]` —— `user` 是一个以字符串为键和值的字典
2. `-> None:` - the `process` function returns `None`.
	2. `-> None:` —— `process`函数会返回`None`值

```Python
def process(user: dict[str,str]) -> None:  
    user['name'] / 10  
  
user = {'name': 'alpha'}  
process(user)
```
运行`mypy`检查 `mypy_intermediate.py` 并指出代码中的错误：
Running mypy on `mypy_intermediate.py`, mypy points out the error in our code:

```shell
$ mypy --strict mypy_intermediate.py  
mypy_fixed.py:2: error: Unsupported operand types for / ("str" and "int")  
Found 1 error in 1 file (checked 1 source file)
```
无需运行指定测试逻辑便可检查出语法和类型错误 —— 这真是太棒了！
This is a test we can run without writing any specific test logic — very cool!
:::info
*在调试类型问题时使用 `_reveal_type(variable)_` ，mypy会告诉你它认为变量应该是什么类型 *
_Use_ `_reveal_type(variable)_` _in your code when debugging type issues. mypy will show you what type it thinks a variable has._
:::

### Pydantic
[**Pydantic**](https://pydantic-docs.helpmanual.io/) **是一个用于规范Python类行为并校验构造参数的Python第三方库** —— 它是`dictionaries`或`dataclasses`的替代品
**P**[**ydantic**](https://pydantic-docs.helpmanual.io/) **is a tool for organizing and validating data in Python** — it’s an alternative to using dictionaries or dataclasses.
**Pydantic助力了Python类型进化** —— Pydantic 创建和校验自定义类型 的能力可使Python项目更加简洁和安全
**Pydantic is part of Python’s typing revolution** — pydantic’s ability to create and validate custom types makes your Python code clearer and safer.
Pydantic使用Python类型注解来定义数据类型。想象一下，我们想要一个用户拥有`name`和`id`属性，那么我们会用dict实现一个数据模型
Pydantic uses Python type hints to define data types. Imagine we want a user with a `name` and `id`, which we could model with a dictionary:

```Python
import uuid  
  
users = [  
    {'name': 'alpha', 'id': str(uuid.uuid4())},  
    {'name': 'beta'},  
    {'name': 'omega', 'id': 'invalid'}  
]
```
我们亦可使用`Pydantic.BaseModel`作为父类创建一个数据模型
We could also model this with Pydantic — introducing a class that inherits from `pydantic.BaseModel`:

```Python
import uuid  
import pydantic  
  
class User(pydantic.BaseModel):  
    name: str  
    id: str = None  
  
users = [  
    User(name='alpha', 'id'= str(uuid.uuid4())),  
    User(name='beta'),  
    User(name='omega', id='invalid'),  
]
```
Pydantic的一大长处便是数据校验 —— 我们可以给用户的ID属性引入一些校验 —— 下面将检查`id`属性是否为有效的GUID —— 如果不是则设置为`None`
A strength of Pydantic is validation — we can introduce some validation of our user ids — below checking that the `id` is a valid GUID - otherwise setting to `None`:

```Python
import uuid  
import pydantic  
  
class User(pydantic.BaseModel):  
    name: str  
    id: str = None  
  
    @pydantic.validator('id')  
    def validate_id(cls, user_id:str ) -> str | None:  
        try:  
            user_id = uuid.UUID(user_id, version=4)  
            print(f"{user_id} is valid")  
            return user_id  
        except ValueError:  
            print(f"{user_id} is invalid")  
            return None  
  
users = [  
    User(name='alpha', id= str(uuid.uuid4())),  
    User(name='beta'),  
    User(name='omega', id='invalid'),  
]  
[print(user) for user in users]
```
运行上面的代码，我们的Pydantic数据模型将会拒绝其中一组ID —— `omega`因为值为`invalid`字符串而被拒绝并被设置为`NOne`
Running the code above, our Pydantic model has rejected one of our ids — our `omega` has had it's original ID of `invalid` rejected and ends up with an `id=None`:

```shell
$ python pydantic_eg.py  
45f3c126-1f50-48bf-933f-cfb268dca39a is valid  
invalid is invalid  
name='alpha' id=UUID('45f3c126-1f50-48bf-933f-cfb268dca39a')  
name='beta' id=None  
name='omega' id=None
```
这些Pydantic类型将成为你的Python项目中的第一优先级数据结构（而不是dictionaries） —— 使得其他开发者更易于理解代码逻辑
These Pydantic types can become the primitive data structures in your Python programs (instead of dictionaries) — making it eaiser for other developers to understand what is going on.
:::tip
*可以使用Pydantic数据模型生产TS类型 —— 以便在TS前端和Python后端间共享一致的数据结构*
_you can generate Typescript types from Pydantic models — making it possible to share the same data structures with your Typescript frontend and Python backend._
:::
### Typer
[**Typer**](https://typer.tiangolo.com/) **是一个使用类型注解搭建CLI界面的Python第三方库** —— 它是`sys.argv`和`argparse`的平替
[**Typer**](https://typer.tiangolo.com/) **is a tool for building command line interfaces (CLIs) using type hints in Python** — it’s an alternative to sys.argv or argparse.
我们可以先用`uv`创建一个Python项目，然后用`Typer`构建Python CLI
We can build a Python CLI with uv and Typer by first creating a Python package with uv, adding `typer` as a dependency).
首先创建一个虚拟环境
First create a virtual environment:

```shell
$ uv venv --python=3.11.10  
Using CPython 3.11.10  
Creating virtual environment at: .venv  
Activate with: source .venv/bin/activate
```
然后使用`uv init`初始化新项目
Then use `uv init` to create a new project from scratch:

```shell
$ uv init --name demo --python 3.11.10 --package  
Initialized project `demo`
```
这将创建下面的项目结构
This creates a project:

```shell
$ tree  
.  
├── pyproject.toml  
├── README.md  
└── src  
    └── demo  
        └── __init__.py
```
然后使用`uv add`添加`typer`依赖：
We can then add `typer` as a dependency with `uv add`:

```shell
$ uv add typer  
Using CPython 3.11.10  
Creating virtual environment at: .venv  
Resolved 10 packages in 2ms  
Installed 8 packages in 9ms  
 + click==8.1.8  
 + markdown-it-py==3.0.0  
 + mdurl==0.1.2  
 + pygments==2.18.0  
 + rich==13.9.4  
 + shellingham==1.5.4  
 + typer==0.15.1  
 + typing-extensions==4.12.2
```
在`src/demo/__init__.py`中构建一个简单的CLI：
We then add modify the Python file `src/demo/__init__.py` to include a simple CLI:

```Python
import typer  
  
  
app = typer.Typer()  
  
  
@app.command()  
def main(name: str) -> None:  
    print(f"Hello {name}")
```
在`pyproject.toml`中加入下面的配置，以使用`demo`指令运行我们的CLI：
We need to add this to our `pyproject.toml` to be able to run our CLI with the `demo` command:

```toml
demo = "demo:app"
```
`pyproject.toml`全配置如下：
This is our full `pyproject.toml`:

```toml
[project]  
name = "demo"  
version = "0.1.0"  
description = "Add your description here"  
readme = "README.md"  
authors = [  
    { name = "Adam Green", email = "adam.green@adgefficiency.com" }  
]  
requires-python = ">=3.11.10"  
dependencies = [  
    "typer>=0.15.1",  
]  
  
[project.scripts]  
demo = "demo:app"  
  
[build-system]  
requires = ["hatchling"]  
build-backend = "hatchling.build"
```
使用`[project.scripts]`包裹`demo = "demo:app"`后便可以使用`uv run <command>`运行我们的CLI
Because we have included a `[project.scripts]` in our `pyproject.toml`, we can run this CLI with `uv run`:

```shell
$ uv run demo omega  
Hello omega
```
Typer会自动生成`--help`文档
Typer gives us a `--help` flag for free:

```shell
$ python src/demo/__init__.py --help  
 Usage: demo [OPTIONS] NAME  
  
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────╮  
│ *    name      TEXT  [default: None] [required]                                              │  
╰──────────────────────────────────────────────────────────────────────────────────────────────╯  
╭─ Options ────────────────────────────────────────────────────────────────────────────────────╮  
│ --install-completion          Install completion for the current shell.                      │  
│ --show-completion             Show completion for the current shell, to copy it or customize │  
│                               the installation.                                              │  
│ --help                        Show this message and exit.                                    │  
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```
:::tip
*在Typer中可以使用嵌套CLI组以实现多命令和命令组*
_you can create nested CLI groups in typer using commands and command groups._
:::
### Rich
[**Rich**](https://rich.readthedocs.io/en/stable/) **是Python一款提供了终端富文本样式的第三方库** —— 它是大多数追求终端美化输出的Python项目的不二选择
[**Rich**](https://rich.readthedocs.io/en/stable/) **is a tool for printing pretty text to a terminal** — it’s an alternative to the monotone terminal output of most Python programs.
Rich支持打印彩色文本和emoji表情：
Rich’s features pretty printing of color and emojis:

```Python
import rich  
  
user = {'name': 'omega', 'id': 'invalid'}  
print(f" normal printing\nuser {user}\n")  
rich.print(f" :wave: rich printing\nuser {user}\n")

 normal printing  
user {'name': 'omega', 'id': 'invalid'}  
  
 👋 rich printing  
user {'name': 'omega', 'id': 'invalid'}

If you are happy with Rich you can simplify your code by replacing the built-in print with the Rich print:

from rich import print  
  
print('this will be printed with rich :clap:')

this will be printed with rich 👏
```
:::tip
Rich额外支持超多颜色和emoji表情 —— 包括有色打印表格数据和更好的堆栈报错输出
_Rich offers much more than color and emojis — including displaying tabular data and better trackbacks of Python errors._
:::

### Polars
==**Polars是一个用于操作表格数据的Python库**== ==—— 它是`Pandas`或`Spark`的平替==
==**Polars is a tool for tabular data manipulation in Python**== ==— it’s an alternative to Pandas or Spark.==
Polars支持优化查询、并行处理和更大的存储在内存中的数据集的操作。它还有与Pandas相近的语法
Polars offers query optimization, parallel processing and can work with larger than memory datasets. It also has a syntax that many prefer to Pandas.
查询优化允许多组数据转换成聚合数据并进行深度优化，这在Pandas以即时操作（数据转换不会事先检查查询先后顺序）为核心的框架来说是无法做到的
Query optimization allows multiple data transformations to be grouped together and optimized over. This cannot be done in eager-execution frameworks like Pandas, each data transformation is run without knowledge of what came before and after.
现在让我们创建一个含有三行数据的表格：
Let’s start with a dataset with three columns:

```Python
import polars as pl  
  
df = pl.DataFrame({  
    'date': ['2025-01-01', '2025-01-02', '2025-01-03'],  
    'sales': [1000, 1200, 950],  
    'region': ['North', 'South', 'North']  
})

# Below we chain together column creation and aggregation into one query:

query = (  
    df  
    # start lazy evaluation - Polars won't execute anything until .collect()  
    .lazy()  
    # with_columns adds new columns  
    .with_columns(  
        [  
            # parse string to date  
            pl.col("date").str.strptime(pl.Date).alias("date"),  
            # add a new column with running total  
            pl.col("sales").cum_sum().alias("cumulative_sales"),  
        ]  
    )  
    # column to group by  
    .group_by("region")  
    # how to aggregate the groups  
    .agg(  
        [  
            pl.col("sales").mean().alias("avg_sales"),  
            pl.col("sales").count().alias("n_days"),  
        ]  
    )  
)  
```
#### 运行优化查询
```python
print(query.collect())

shape: (2, 3)  
┌────────┬───────────┬────────┐  
│ region ┆ avg_sales ┆ n_days │  
│ ---    ┆ ---       ┆ ---    │  
│ str    ┆ f64       ┆ u32    │  
╞════════╪═══════════╪════════╡  
│ North  ┆ 975.0     ┆ 2      │  
│ South  ┆ 1200.0    ┆ 1      │  
└────────┴───────────┴────────┘
```
Polars可以解析查询语句：
We can use Polars to explain our query:

```Python
print(query.explain())

AGGREGATE  
        [col("sales").mean().alias("avg_sales"), col("sales").count().alias("n_days")] BY [col("region")] FROM  
  DF ["date", "sales", "region"]; PROJECT 2/3 COLUMNS; SELECTION: Non
```
:::tip
在将Pandas管线架构重构成Polars管线架构时，可以先用`_pl.DataFrame.to_pandas()_`将Polars数据模型转换成Pandas数据模型以兼容历史代码
_you can use_ `_pl.DataFrame.to_pandas()_` _to convert a Polars DataFrame to a Pandas DataFrame. This can be useful to slowly refactor a Pandas based pipeline into a Polars based pipeline._
:::

### Pandera
**Pendera是一款为表格数据提供了数据校验的Python库** —— 它是`assert`结构的平替
**Pandera is a tool for data quality checks of tabular data** - it’s an alternative to Great Expectations or assert statements.
Pendera可为行列式数据提供架构定义，用于校验表格中的数据。通过显式设置架构，Pendara可以捕获类型异常，阻止不正确的数据进入程序流程
Pandera allows you to define schemas for tabular data (data with rows and columns), which are used validate a table of data. By defining schemas explicitly, Pandera can catch data issues before they propagate through your analysis pipeline.
接下来我们要为一个销售表创建架构并添加数据校验：
Below we create a schema for sales data, including a few data quality checks:

- null value checks,
	- 空值检查
- upper and lower bounds,
	- 大小写绑定
- accepted values.
	- 接受赋值

```Python
import polars as pl  
import pandera as pa  
from pandera.polars import DataFrameSchema, Column  
  
schema = DataFrameSchema(  
    {  
        "date": Column(  
            pa.DateTime,  
            nullable=False,  
            coerce=True,  
            title="Date of sale"  
        ),  
        "sales": Column(  
            int,  
            checks=[pa.Check.greater_than(0), pa.Check.less_than(10000)],  
            title="Daily sales amount",  
        ),  
        "region": Column(  
            str,  
            checks=[pa.Check.isin(["North", "South", "East", "West"])],  
            title="Sales region",  
        ),  
    }  
)
```
接下来使用下面的架构校验数据
We can now validate data using this schema:

```Python
data = pl.DataFrame({  
    "date": ["2025-01-01", "2025-01-02", "2025-01-03"],  
    "sales": [1000, 1200, 950],  
    "region": ["North", "South", "East"]  
})  
data = data.with_columns(pl.col("date").str.strptime(pl.Date, "%Y-%m-%d"))  
  
print(schema(data))

shape: (3, 3)  
┌────────────┬────────┬────────┐  
│ date       ┆ sales  ┆ region │  
│ ---        ┆ ---    ┆ ---    │  
│ datetime   ┆ f64    ┆ str    │  
╞════════════╪════════╪════════╡  
│ 2025-01-01 ┆ 1000.0 ┆ North  │  
│ 2025-01-02 ┆ 1200.0 ┆ South  │  
│ 2025-01-03 ┆ 950.0  ┆ North  │  
└────────────┴────────┴────────┘
```
当我们试图导入*脏数据* 时，Pendara会抛出异常
When we have _bad data_, Pandera will raise an exception:

```Python
data = pl.DataFrame({  
    "date": ["2025-01-01", "2025-01-02", "2025-01-03"],  
    "sales": [-1000, 1200, 950],  
    "region": ["North", "South", "East"]  
})  
data = data.with_columns(pl.col("date").str.strptime(pl.Date, "%Y-%m-%d"))  
  
print(schema(data))

SchemaError: Column 'sales' failed validator number 0: <Check greater_than: greater_than(0)> failure case examples: [{'sales': -1000}]
```
:::tip
Pendera也提供用于校验Python类型的API式的Pydantic style class
_Pandera also offers a Pydantic style class based API that can validate using Python types._
:::

### DuckDB
**DuckDB是为分析式SQL查询而生的数据库** —— 它是SQLite、Polars和Pandas的平替
**DuckDB is database for analytical SQL queries** — it’s an alternative to SQLite, Polars and Pandas.
DuckDB和SQlite差不多，也是单文件的数据库，但SQLite针对行式量化数据做了优化，而DuckDB则专为列式、分析式查询而生
DuckDB is a single-file database like SQLite. While SQLite is optimized for row based, transactional workloads, DuckDB is specifically designed for column based, analytical queries.
让我们使用创建一个同时适应CSV和Apache Parquet格式的样本数据：
Let’s create some sample data using both CSV and Parquet formats:

```Python
import duckdb  
import polars as pl  
  
sales = pl.DataFrame(  
    {  
        "date": ["2025-01-01", "2025-01-02", "2025-01-03"],  
        "product_id": [1, 2, 1],  
        "amount": [100, 150, 200],  
    }  
).to_csv("sales.csv", index=False)  
  
products = pl.DataFrame(  
    {"product_id": [1, 2], "name": ["Widget", "Gadget"], "category": ["A", "B"]}  
).to_parquet("products.parquet")
```
接下来对CSV和Parquet分别应用SQL查询：
Below we run a SQL query across both data formats:

```Python
con = duckdb.connect()  
  
print(  
    con.execute(  
        """  
    WITH daily_sales AS (  
        SELECT   
            date,  
            product_id,  
            SUM(amount) as daily_total  
        FROM 'sales.csv'  
        GROUP BY date, product_id  
    )  
    SELECT   
        s.date,  
        p.name as product_name,  
        p.category,  
        s.daily_total  
    FROM daily_sales s  
    JOIN 'products.parquet' p ON s.product_id = p.product_id  
    ORDER BY s.date, p.name  
"""  
    ).df()  
)

         date product_name category  daily_total  
0  2025-01-01      Widget        A         100  
1  2025-01-02      Gadget        B         150  
2  2025-01-03      Widget        A         200
```
DuckDB适宜操作无法在内存中整块读取的数据，可以在不将数据加载到内存中的情况下有效查询Parquet数据
DuckDB shines when working with larger than memory datasets. It can efficiently query Parquet files directly without loading them into memory first.
:::tip
使用DuckDB EXPLAIN指令分析查询语句计划，以优化你的查询
_Use DuckDB’s EXPLAIN command to understand query execution plans and optimize your queries._
:::
### Loguru
[**Loguru**](https://github.com/Delgan/loguru) **是一个比`logging`快得多的日志库** —— 它是标准库`logging`和`structlog`的上位替代品
[**Loguru**](https://github.com/Delgan/loguru) **is a logger** — it’s an alternative to the standard library’s logging module and structlog.
Loguru基于标准库`logging`开发，不是彻底重构，而是做了一些魔改，让`logging`变得拟人了很多
Loguru builds on top of the Python standard library `logging` module. It's not a complete rethinking, but a few tweaks here and there to make logging from Python programs less painful.
使用Loguru应确保程序全局只有一个`logger`实例（或命名空间）。正所谓约定大于契约 —— `logger`越少，越方便全局统一日志配置。也因为Loguru基于`logging`开发，所以将loggeing的日志引擎替换成logger
A central Loguru idea is that there is only one `logger`. This is a great example of the unintuitive value of constraints - having less `logger` objects is actually better than being able to create many. Because Loguru builds on top of the Python `logging` module, it's easy to swap in a Loguru logger for a Python standard library `logging.Logger`.
`from loguru import logger`一行代码便可开始使用Loguru日志：
Logging with Loguru is as simple as `from loguru import logger`:

```Python
from loguru import logger  
  
logger.info("Hello, Loguru!")

2025-01-04 02:28:37.622 | INFO     | __main__:<module>:3 - Hello, Loguru!

# Configuring the logger is all done through a single `logger.add` call.

# We can configure how we log to `std.out`:

logger.add(  
    sys.stdout,  
    colorize=True,  
    format="<green>{time}</green> <level>{message}</level>",  
    level="INFO"  
)

# The code below configures logging to a file:

logger.add(  
    "log.txt",  
    format="{time} {level} {message}",  
    level="DEBUG"  
)
```

:::tip
Loguru支持将结构化数据导出成JSON日志：`logger.add("log.txt", seralize=True)`
_Loguru supports structured logging of records to JSON via the_ `_logger.add("log.txt", seralize=True)_` _argument._
:::

### Marimo
[**Marimo**](https://marimo.io) **一款Python记事本编辑器和格式化工具** —— Jupyter Lab和JSON Jupyter 记事本文件格式化工具的平替
[**Marimo**](https://marimo.io) **is a Python notebook editor and format** — it’s an alternative to Jupyter Lab and the JSON Jupyter notebook file format.
Marimo基于下面三个领域对Python记事本做了改进：
Marimo offers multiple improvements over older ways of writing Python notebooks:

- **Safer** — Marimo notebook cells are executed based on variable references rather than order,
	- **安全性** —— Marimo几十倍基于变量引用而非变量顺序执行原子操作（这里不知道怎么翻）
- **Development Experience** — Marimo offers many quality of life features for developers,
	- **便利开发** —— Marimo可以显著改善开发者的体验
- **Interactive** — Marimo offers an interactive, web-app like experience.
	- **交互性** —— Marimo提供交互性的、类web app的体验
Marimo还实现了响应式功能 —— 当输入改变时脚本会自动重新运行。这对一些脚本来说无疑是双刃剑，任何对脚本的改动都可能对API查询或数据库查询产生副作用
Marimo also offers the feature of being reactive — cells can be re-executed when their inputs change. This can be a double-edged sword for some notebooks, where changing a call can cause side effects like querying APIs or databases.
Marimo记事本使用`.py`文件存储代码，这意味着`git diff`又可以分析文件差异了，并且记事本也可以以脚本的形式执行 
Marimo notebooks are stored as pure Python files, which means that:Git diffs are meaningful, and the notebook can be executed as a script.
下面演示Marimo notebook format：
Below is an example of the Marimo notebook format:

```Python
import marimo  
  
__generated_with = "0.10.12"  
app = marimo.App(width="medium")  
  
  
@app.cell  
def _():  
    import pandas as pd  
  
    def func():  
        return None  
  
    print("hello")  
    return func, pd  
  
  
if __name__ == "__main__":  
    app.run()
```
:::tip
Marimo整合了Github copliot和Ruff 代码格式化
_Marimo integrates with GitHub Copilot and Ruff code formatting._
:::

## 总结
**2025年的Python现代化工具箱**如下：
The **2025 Hypermodern Python Toolbox** is:

- [**Python 3.11**](https://www.python.org/downloads/release/python-3110/) 更好的报错消息
- [**uv**](https://docs.astral.sh/uv/) 管理Python多版本、管理虚拟环境和管理依赖
- [**Ruff**](https://docs.astral.sh/ruff/) 格式化和标记Python代码的类型
- [**mypy**](http://mypy-lang.org/) 静态类型检查
- [**Pydantic**](https://docs.pydantic.dev/latest/) 规范类的行为，校验构造传参
- [**Typer**](https://typer.tiangolo.com/) 快速构建界面养眼的CLI页面
- [**Rich**](https://rich.readthedocs.io/en/stable/) 终端富文本打印
- [**Polars**](https://docs.pola.rs/) 操作表格数据
- [**DuckDB**](https://duckdb.org/docs/) 单文件、适于分析的数据库
- [**Loguru**](https://loguru.readthedocs.io/en/stable/) 日志库
- [**Marimo**](https://docs.marimo.io/) 交互式Python notebooks

_首发于_ [_https://datasciencesouth.com_](https://datasciencesouth.com/blog/hypermodern-python/)_._