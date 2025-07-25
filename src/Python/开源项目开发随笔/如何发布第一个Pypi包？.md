---
title: 如何用uv包管理器创建一个项目、添加依赖并使用twine发布第一个Pypi包
date: 2025-07-25
category:
  - Python
  - Develop
icon: file-contract
---
[[toc]]
## 创建一个项目

### 使用uv包管理器
```shell
mkdir my-test-pypi
cd my-test-pypi
```

```shell
which python 
# 检查当前环境变量中的Python版本
# uv 新建虚拟环境默认使用当前Python版本
uv python list
# 列出所有Python版本，包括已安装的和未安装的
uv python pin <指定版本的别称>
```
![](assets/Pasted%20image%2020250725203440.png)
使用`uv python pin xxx`指令来锁定（当前目录）到具体的Python版本上
![](assets/Pasted%20image%2020250725203817.png)

![](assets/Pasted%20image%2020250725203955.png)
当项目根目录不存在`.python-version`文件时，uv会自动递归向上查找，直到遇到第一个`.python-version`，图上的测试目录并不存在`.python-version`，但uv还是找到了位于`uv-explore/`目录下的配置文件，并设置项目的python venv版本为`3.7.5`

![](assets/Pasted%20image%2020250725204127.png)
删掉项目根目录的`.python-version`重来后，可以发现uv确实会自动调用当前环境的Python构建`venv`环境

```shell
uv init # 创建完venv环境后可以初始化项目了
```
uv会自动在当前项目目录下创建如下文件：
- `.gitignore`：
	![](assets/Pasted%20image%2020250725204807.png)
- `pyproject.toml`， 项目配置文件
- 示例`main.py`
- 空的`README.md`
```
PS F:\CodePractice\uv-explore\my-test-pypi-py311> uv init
Initialized project `my-test-pypi-py311`
PS F:\CodePractice\uv-explore\my-test-pypi-py311> ls


    目录: F:\CodePractice\uv-explore\my-test-pypi-py311


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         2025/7/25     20:39                .venv
-a----         2025/7/25     20:42            109 .gitignore
-a----         2025/7/25     20:42              5 .python-version
-a----         2025/7/25     20:42             96 main.py
-a----         2025/7/25     20:42            164 pyproject.toml
-a----         2025/7/25     20:42              0 README.md
```

```shell
uv sync # 同步项目依赖
# 如果手动修改了toml配置文件，VSC插件会询问你要不要覆盖配置文件
uv version <新的版本号>
# 不接参数就是查看当前版本号；接参数就是修改当前的版本号
uv add <包名>
# 安装一个依赖
uv remove <包名>
# 卸载一个依赖
uv tree
# 显示项目的依赖树
```
![](assets/Pasted%20image%2020250725205851.png)
:::info
这里报错是因为uv尝试通过创建**硬链接**来快速移动文件，但是失败了，并报告称可能会降低文件系统性能……无伤大雅，可以不管
:::
![](assets/Pasted%20image%2020250725210009.png)
这里创建一个`my_test_pypi`目录，在`my_test_pypi/`下创建包初始化文件`__init__.py`，直接在里面写上示例代码
:::tip
Python工程开发时不建议在`__init__.py`中编写业务逻辑，这里为了演示就没打算管这么多
:::
也可以把示例代码移出去，放在哪里都行，但总归都要回到`__init__.py`使用**相对导入**将其他地方的组件导入进来。比如对于下面的文件结构
```Markdown
- my_test_pypi
	- __init__.py
	- something.py
```
在`something.py`里写上：
```Python
import requests

print("Hello World")
```
要回到`__init__.py`写上相对导入语句：
```python
import .something # 从当前目录下的something.py导入代码
# . 表示当前目录 # 同理 ..表示上一级目录
```
这样，在`my_test_pypi`之外的其他地方，比如项目根目录中的`main.py`或在新的环境安装你的包时，就可以使用下面的导入语句导入`my_test_pypi.__init__.py`从其他地方获得的组件，而不必关心组件具体所在的文件的路径：
```Python
import my_test_pypi
```

![](assets/Pasted%20image%2020250725210929.png)
（使用`uv run xxx.py`来运行项目中的代码）

## 发布一个pypi包

### 打包
```shell
uv build
```
一键打包
#### 微调项目结构
如果你的源代码目录直接就是你想要的包名，比如像下面这样：
```Markdown
- root/ 项目根目录
	- my_test_pypi
		- your_own_component.py
		- __init__.py
```
那么直接`uv build`就好了

如果你的项目结构是下面这样：
```Markdown
- root/ 项目根目录
	- src
		- my_test_pypi-1
			- your_own_component.py
			- __init__.py 
		- my_test_pypi-2
			- your_own_component.py
			- __init__.py 
		- my_test_pypi-3
			- your_own_component.py
			- __init__.py 
```
有好几个**位于`src/`布局下的顶层包**的话，uv（或者说是`setuptools`）扫描的时候就会把`my_test_pypi[1-3]`的名称都写入`top_level.txt`中，使用者自然也不知道该导入哪个为好
![](assets/Pasted%20image%2020250725215018.png)


这时可以在`pyproject.toml`中添加下面的配置：
```toml
[tool.hatch.build.targets.wheel]
# 显式指定源代码位于的目录, 这直接决定下载第三方库后从哪里导入组件
packages = ["src/my_test_pypi-1"]
# 即使这样也不是绝对能跑的，uv仍然会将src/下的所有顶层包都记录到top_level中
# 所以开发时尽量只留一个顶层包
```
显式指定要视作**顶层包**的目录
![](assets/Pasted%20image%2020250725214325.png)
（我自己的项目……）

:::tip
`uv build`打包时并不会自动清空`dist/`下的文件，因此，在发布新版本前务必直接删掉`dist/*`，以免旧版本的包影响到新版本
:::
#### 配置项目信息
让pypi侧边栏不至于太空
```toml
# 作者信息
authors = [
  { name="SyYhunfhds MemorySeer", email="syyhunfhdsmemoryseer@gmail.com" },
]
# 许可证信息 # 目录下的LICENSE文件
license = { file="LICENSE" }

# 项目相关的链接
[project.urls]
Homepage = "https://github.com/SyYhunfhds-s-House/python-fofa-sy"
"Bug Tracker" = "https://github.com/SyYhunfhds-s-House/python-fofa-sy/issues"
Repository = "https://github.com/SyYhunfhds-s-House/python-fofa-sy"
```

### 发布你的包
#### 安装`twine`
```shell
uv pip install twine
# 建议的运行方式
uv tool run twine 
# 直接twine的话twine无法搜索到项目目录
```
#### 创建一个token
![](assets/Pasted%20image%2020250725215653.png)
1. 个人信息页面选择`Account Settings`选项卡，拉到下面有一个`Create token`按钮
2. 输入token_name，这里为`my_test_pypi`
3. 选择API适用的仓库范围
	- 第一次上传项目的时候这个适用范围只可以选择`Entire Account`，因为没有项目给你选
	- 建议**一个项目一个API Token**，这个全局token用了之后立刻用上传的项目创建一个单独的TOKEN
- 点击生成即可
#### 发布到`testpypi`源

```shell
PS F:\CodePractice\uv-explore\my-test-pypi-py311> uv tool run twine check dist/*
Checking dist\my_test_pypi_py311-1.0.0-py3-none-any.whl: PASSED with warnings
WARNING  `long_description` missing.
Checking dist\my_test_pypi_py311-1.0.0.tar.gz: PASSED with warnings
WARNING  `long_description` missing.
PS F:\CodePractice\uv-explore\my-test-pypi-py311> uv tool run twine upload dist/* -r testpypi
Uploading distributions to https://test.pypi.org/legacy/
Enter your API token: 
Uploading my_test_pypi_py311-1.0.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.2/3.2 kB • 00:00 • ?
Uploading my_test_pypi_py311-1.0.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.8/2.8 kB • 00:00 • ?

View at:
https://test.pypi.org/project/my-test-pypi-py311/1.0.0/
```
输入`twine upload -r testpypi`后终端会要求你输入token，把上面得到的token复制粘贴过来即可
:::info 
`twine check`时抛出`long_description` missing异常是因为`README.md`文档还是空的。这是**非阻塞警告**，无关紧要，不会影响twine的上传
:::

#### 发布到生产`pypi`源
和发布到`testpypi`时一样，只是不需要`-r --repository`参数了而已：
```shell
uv tool run twine upload dist/*
```
终端会首先要求你输入**username**——输入`__token__`即可，这表示你正在用token登录
然后就是输入API Token了

生产`pypi`源，就是一般的pypi站，和测试用的`testpypi`源的数据是相互独立的，token也是不通用的
### 测测你的包
#### 对于`testpypi`源
```shell
 uv pip install my-test-pypi-py311 --index-url https://test.pypi.org/simple --extra-index-url https://pypi.org/simple --prerelease=allow python-fofa-sy --no-cache
```
- `--index-url` 主索引
	- pip下载包优先从`pypi`站点下载，对于尚在`testpypi`的包，需使用`--index-url`来指定优先索引
- `--extra-index-url` 备用索引
	- 如果项目依赖的库的版本在`testpypi`的源比在`pypi`的源版本不匹配或是在`testpypi`上压根就没有项目依赖时，需要使用`--extra-index-url`指定正式生产的`pypi`站点，这样uv就可以找到依赖了
- `--prerelease=allow `允许预发布版本，版本号有后缀`alpha`、`beta`之类的时会被pypi判定为`pre-release`版本
- `--no-cache` 禁用uv本地缓存，为了快速更迭演示
![](assets/Pasted%20image%2020250725214118.png)

:::tip
这里`my_test_pypi`被VSC标记出来了，是因为我现在使用的Python不是venv环境的Python，VSC自然找不到我们的包
:::

#### 对于`pypi`源
```shell
uv pip install my-test-pypi-py311
# 我没往正式生产环境发
# 这里只是一个示例
```