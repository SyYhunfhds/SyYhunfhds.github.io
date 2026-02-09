---
title: Nim（一）：Hello World
date: 2026-02-08
---
[[toc]]

:::tip
由于Obsidian尚不支持Nim语法高亮，因此下面的代码块全部使用python语言的语法高亮
:::

***
## Hello World
#### 注释
```python
# 单行注释

#[
	多行
	注释
]#
```

### 变量声明关键字
#### var
- `var`：声明（并赋值）变量；类型注解可选：
```python
var                     # Declare (and assign) variables,
  letter: char = 'n'    # with or without type annotations
  lang = "N" & "im"
  nLength: int = len(lang)
  boat: float
  truth: bool = false
```

#### let
- `let`：声明并 *仅绑定一次* 变量；声明的变量是不可变的
```python
let            # Use let to declare and bind variables *once*.
  legs = 400   # legs is immutable.
  arms = 2_000 # _ are ignored and are useful for long numbers.
  aboutPi = 3.15
```
- `_`下划线可用于分割长一点的数字；编译器会自动忽略`_`

#### const
- `const`：声明编译期进行计算、运行时固定的常量
```python
const            # Constants are computed at compile time. This provides
  debug = true   # performance and is useful in compile time expressions.
  compileBadCode = false
```

#### when
- `when`：仅在`when expression`为`true`时声明变量
```python
when compileBadCode:            # `when` is a compile time `if`
  legs = legs + 1               # This error will never be compiled.
  const input = readline(stdin) # Const values must be known at compile time.
```
- 忽略编译期对常量进行计算时发生的错误，比如这里尝试从`stdin`标准输入流读取数据

### 特殊关键字
#### discard
- `discard`：**显式**忽略函数返回值
```python
discard """
This can also work as a multiline comment.
Or for unparsable, broken code
"""

discard 1 > 2 # Note: The compiler will complain if the result of an expression
              # is unused. `discard` bypasses this.
```

### 变量类型
#### 基本变量类型

#### 数据结构类型
##### 元组/Tuple
- **元组**既有字段名也有*顺序* （Python的元组是不可索引和遍历的）
```python
var
  child: tuple[name: string, age: int]   # Tuples have *both* field names
  today: tuple[sun: string, temp: float] # *and* order.

child = (name: "Rudiger", age: 2) # Assign all at once with literal ()
today.sun = "Overcast"            # or individual fields.
today[1] = 70.1                   # or by index.

let impostor = ("Rudiger", 2) # Two tuples are the same as long as they have
assert child == impostor      # the same type and the same content
```
- 判断元组是否相等看的是二者的**字段类型**和**字段值**

##### 动态数组/Seq
```python
var
  drinks: seq[string]

drinks = @["Water", "Juice", "Chocolate"] # @[V1,..,Vn] is the sequence literal

drinks.add("Milk")

if "Milk" in drinks:
  echo "We have Milk and ", drinks.len - 1, " other drinks"

let myDrink = drinks[2]
```

*哦牛逼，这个Seq还有`in`操作符*， 但是是`for`循环遍历出来的，只是一个语法糖，查找效率当然也是`O(n)`的

#### 其他数据类型
##### 枚举
```python
# Enumerations allow a type to have one of a limited number of values

type
  Color = enum cRed, cBlue, cGreen
  Direction = enum # Alternative formatting
    dNorth
    dWest
    dEast
    dSouth
var
  orient = dNorth # `orient` is of type Direction, with the value `dNorth`
  pixel = cGreen # `pixel` is of type Color, with the value `cGreen`
  
discard dNorth > dEast # Enums are usually an "ordinal" type
```

:::warning Nim的**非限定枚举值 (Unqualified Enum Values)**
在 Nim 中，默认情况下，枚举定义的成员（如 `cRed`, `dNorth`）会被注入到**枚举类型所属的命名空间**中。**这绝对会导致冲突**，例如下面的例子：
```python
type
  UserStatus = enum id, active, inactive
  ProductStatus = enum id, available, soldOut # 报错：符号 id 重复定义
```

为了解决这个问题，Nim 提供了两个非常成熟的方案：
1. **手动加前缀（传统的做法）**
	正如官方示例里写的是 `cRed` (Color Red) 和 `dNorth` (Direction North)。这是早期的 Nim 代码风格，通过手动加小写字母前缀来强行区分
2. **使用 `{.pure.}` 标注（现代推荐做法）**
	给枚举加一个特殊标记，强制要求必须通过 `Type.Value` 的方式访问
```python
type
  Color {.pure.} = enum
    Red, Blue, Green

  Status {.pure.} = enum
    Red, Pending, Done # 这里的 Red 不会冲突

var c = Color.Red  # 必须带前缀
var s = Status.Red # 必须带前缀
```

:::
##### 子域/Subranges
```python
# Subranges specify a limited valid range

type
  DieFaces = range[1..20] # Only an int from 1 to 20 is a valid value
var
  my_roll: DieFaces = 13

when compileBadCode:
  my_roll = 23 # Error!
```

##### 数组/Arrays
```python
# Arrays

type
  RollCounter = array[DieFaces, int]  # Arrays are fixed length and
  DirNames = array[Direction, string] # indexed by any ordinal type.
  Truths = array[42..44, bool]
var
  counter: RollCounter
  directions: DirNames
  possible: Truths

possible = [false, false, false] # Literal arrays are created with [V1,..,Vn]
possible[42] = true

directions[dNorth] = "Ahh. The Great White North!"
directions[dWest] = "No, don't go there."

my_roll = 13
counter[my_roll] += 1
counter[my_roll] += 1

var anotherArray = ["Default index", "starts at", "0"]
```
#### 更多数据类型
[详情请见](http://nim-lang.org/docs/lib.html#collections-and-algorithms)
##### tables
##### sets
##### lists
##### queues
##### crit bit trees
#### 类型声明关键字
##### 类型别名 `type new_type = old_type`
```python
# Defining your own types puts the compiler to work for you. It's what makes
# static typing powerful and useful.

type
  Name = string # A type alias gives you a new type that is interchangeable
  Age = int     # with the old type but is more descriptive.
  Person = tuple[name: Name, age: Age] # Define data structures too.
  AnotherSyntax = tuple
    fieldOne: string
    secondField: int

var
  john: Person = (name: "John B.", age: 17)
  newage: int = 18 # It would be better to use Age than int

john.age = newage # But still works because int and Age are synonyms
```
##### 类型定义 `type new_type = distinct old_type`
```python
type
  Cash = distinct int    # `distinct` makes a new type incompatible with its
  Desc = distinct string # base type.

var
  money: Cash = 100.Cash # `.Cash` converts the int to our type
  description: Desc  = "Interesting".Desc
```

**类型定义**与原始类型不同，不可直接赋值：
```python
when compileBadCode:
  john.age  = money        # Error! age is of type int and money is Cash
  john.name = description  # Compiler says: "No way!"
```
*前情提要：*
```python
type
	Person = tuple[name: Name, age: Age]
var
	john: Person = (name: "John B.", age: 17)
	newage: int = 18	
```

#### 对象
- **对象**可以设置默认值
```python
type
  Room = ref object # reference to an object, useful for big objects or
    windows: int    # objects inside objects
    doors: int = 1  # Change the default value of a field (since Nim 2.0)
  House = object
    address: string  
    rooms: seq[Room]
```
- `ref`修饰符：声明**引用类型**

**对象的初始化**：
```python
var
  defaultHouse = House() # initialize with default values
  defaultRoom = Room() # create new instance of ref object with default values

  # Create and initialize instances with given values
  sesameRoom = Room(windows: 4, doors: 2)
  sesameHouse = House(address: "123 Sesame St.", rooms: @[sesameRoom])
```

## IO与控制流
### 多分支 `case ... of ...`
- 示例里还用到了`readLine()`函数
```python
# `case`, `readLine()`

echo "Read any good books lately?"
case readLine(stdin)
of "no", "No":
  echo "Go to your local library."
of "yes", "Yes":
  echo "Carry on, then."
else:
  echo "That's great; I assume."
```
- `case ... of ...` 必须处理每一种情况，否则过不了编译——当然，Nim给了另一个关键字`else`用来覆盖*剩余情况* 
- `of`分支可以处理多个值，例如这里的`of "no", "No"`

:::note `case of`模式匹配
- **范围匹配**
```python
let score = 85
case score
of 0..59:   echo "不及格"
of 60..89:  echo "良好"
of 90..100: echo "优秀"
else:       echo "非法分数"
```
:::
### 循环：`while`
- `continue`
- `break`
### 判断：`if-elif`
- *官方文档* 把这里的四个关键字放在一起演示了

```python
# `while`, `if`, `continue`, `break`

import strutils as str # http://nim-lang.org/docs/strutils.html
echo "I'm thinking of a number between 41 and 43. Guess which!"
let number: int = 42
var
  raw_guess: string
  guess: int # Variables in Nim are always initialized with a zero value
while guess != number:
  raw_guess = readLine(stdin)
  if raw_guess == "": continue # Skip this iteration
  guess = str.parseInt(raw_guess)
  if guess == 1001:
    echo("AAAAAAGGG!")
    break
  elif guess > number:
    echo("Nope. Too high.")
  elif guess < number:
    echo(guess, " is too low")
  else:
    echo("Yeeeeeehaw!")
```

### 遍历/迭代 (Iteration)
```python
# Iteration
#

for i, elem in ["Yes", "No", "Maybe so"]: # Or just `for elem in`
  echo(elem, " is at index: ", i)

for k, v in items(@[(person: "You", power: 100), (person: "Me", power: 9000)]):
  echo v

let myString = """
an <example>
`string` to
play with
""" # Multiline raw string

for line in splitLines(myString):
  echo(line)

for i, c in myString:       # Index and letter. Or `for j in` for just letter
  if i mod 2 == 0: continue # Compact `if` form
  elif c == 'X': break
  else: echo(c)
```

## 过程/函数 (Procedures)
**格式**：
```python
proc function_name(value1: type1, value2: type2, ...): ret_value_name = 
#[
	function_body
]#
```
- 无返回值函数 不需要声明返回值
- `return`可写可不写，Nim默认给每个函数一个空的返回值，运行到没有`return`的末尾就把末尾语句的输出作为返回值

```python
# Procedures
#

type Answer = enum aYes, aNo

proc ask(question: string): Answer =
  echo(question, " (y/n)")
  while true:
    case readLine(stdin)
    of "y", "Y", "yes", "Yes":
      return Answer.aYes  # Enums can be qualified
    of "n", "N", "no", "No":
      return Answer.aNo
    else: echo("Please be clear: yes or no")

proc addSugar(amount: int = 2) = # Default amount is 2, returns nothing
  assert(amount > 0 and amount < 9000, "Crazy Sugar")
  for a in 1..amount:
    echo(a, " sugar...")

case ask("Would you like sugar in your tea?")
of aYes:
  addSugar(3)
of aNo:
  echo "Oh do take a little!"
  addSugar()
# No need for an `else` here. Only `yes` and `no` are possible.
```
- 由于`addSugar`函数没有返回值，所以不需要`discard addSugar()`丢弃函数返回值


:::tip 为什么Nim的函数叫`proc`？
Nim 的设计深受 **Pascal**, **Modula-3** 和 **Ada** 的影响。在这些经典的系统级语言中，**函数**和**过程**是有严格定义的：

- **Function (函数)**：必须有返回值。它的本意是数学意义上的映射（输入 → 输出）。
    
- **Procedure (过程)**：不一定有返回值，它更像是一系列执行动作的指令集合。
    

Nim 统一使用了 `proc` 这个关键字，但它在内部保留了这种区分：

- 如果写 `proc add(a, b: int): int`，它在逻辑上是一个函数。
    
- 如果写 `proc sayHello()`，没有返回值，它就是一个纯粹的过程。
:::

:::note Nim的`func`关键字
`func` 是 `proc` 的一个语法糖，它强制要求该过程必须是**副作用受限**的（即不能访问全局变量，不能有明显的副作用）
```python
func add(a, b: int): int = a + b # 这是一个纯函数，编译器会帮你检查副作用
```
:::

### 调用C语言函数
```python
# FFI
#

# Because Nim compiles to C, FFI is easy:

proc strcmp(a, b: cstring): cint {.importc: "strcmp", nodecl.}

let cmp = strcmp("C?", "Easy!")
```
***
# 页面底部
