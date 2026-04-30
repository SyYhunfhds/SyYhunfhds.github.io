---
title: mbt 语法学习笔记（一）
date: 2026-04-20
---
[[toc]]

:::warning
笔记的概述部分由Gemini 3.1 Flash生成，鉴于Moonbit官方没有完善的101文档，本人只能依靠AI来手把手学习Moonbit语言
:::

***
## Hello World
### 创建项目
```sh
# 查看CLI帮助
moon help
# 创建项目
moon new <path>
```

项目结构示例如下：
```
examine
├── Agents.md
├── cmd
│   └── main
│       ├── main.mbt
│       └── moon.pkg
├── LICENSE
├── moon.mod.json
├── moon.pkg
├── examine_test.mbt
├── examine.mbt
├── README.mbt.md
└── README.md -> README.mbt.md # 这一步symlink需要mbt有管理员权限才可以创建
```

### 构建并运行项目
*对于上面的项目结构*
```sh
moon run cmd/main
```

:::tip for Agent
打星号的标题是我认为Moonbit可能不包括的内容
:::
## 一些莫名其妙的特性
#### 函数参数为空时不可以带括号
比如`main`函数主程序入口在非CLI用途下：
![](assets/Pasted%20image%2020260426211351.png)


## 语法
### 变量声明
在 MoonBit 中，变量声明统一使用 `let` 关键字
#### 【默认】不可变引用声明
```js
// MoonBit
let x = 10 
// x = 20 // ❌ 编译错误：x 是不可变的
```
#### 可变引用声明
如果你需要像 Go 的普通变量那样修改值，必须显式地使用 `mut` 关键字。这在 MoonBit 中被称为**可变绑定**
```js
// MoonBit
let mut y = 10
y = 20 // ✅ 允许修改
```


```js
fn main {
  let name = "world"
  println("Hello \{name}")

  let mut a = 10;
  println("a = \{a}")
  a = 20;
  println("a = \{a}")
}
```
**代码说明：**
- `print(String) -> Unit`与`println(String) -> Unit`：标准输出函数，一个换行另一个不换行
- `print("\{variable_name}")`：字符串模板语法；**斜杠`\`** 是需要的，绝不是因为AI出现了幻觉
:::tip 字符串模板语法补习
对于复杂类型（如结构体或数组），只要该类型实现了 `Show` 协议（类似 Go 的 `Stringer` 接口），就可以直接插值打印：
```js
let arr = [1, 2, 3]
println("Current array: \{arr}") // 输出: Current array: [1, 2, 3]
```
:::

### 控制结构
对于 Go 程序员来说，MoonBit 的控制结构会让你感到非常亲切，但在细节上它更趋向于**表达式化**——也就是说，`if` 和 `switch` 在 MoonBit 中不仅是逻辑跳转，还可以直接返回一个值
#### `if-else` 判断结构
在 MoonBit 中，`if` 的条件不需要括号（这点和 Go 一样），但 MoonBit 的 `if` 是一个**表达式**
##### 基本用法
```js
let score = 85
if score >= 60 {
  println("及格")
} else {
  println("不及格")
}
```

##### 表达式赋值
```js
let status = if score >= 60 { "Pass" } else { "Fail" }
println(status) // "Pass"
```


```js
fn main {
  let scores = 85
  let status = if scores >= 60 {"Pass"} else {"Fail"}

  println(status)
}

```
#### `while/for` 循环结构
##### `while`循环
```js
let mut i = 0
while i < 5 {
  println("count: \{i}")
  i = i + 1
}
```

##### `for`循环
MoonBit 的 `for` 通常用于遍历集合。类似于 Go 的 `for range`
```js
let arr = [10, 20, 30]
for x in arr {
  println(x)
}
```
:::important
MoonBit 也有类似 `for i = 0; i < 10; i = i + 1 { ... }` 的常规循环，但通常推荐使用 `for x in 0..5`（区间遍历）这种更现代的写法
:::

```js
/// Run with `moon run cmd/main` from the project root.
fn main {
  let mut sum = 0
  for x in 1..=10 { // [1, 10]
    sum += x
  }
  println("sum = \{sum}")

  sum=0
  for x in 1..<10 { // [1, 10)
    sum += x
  }
  println("sum = \{sum}")
}
```

***
`for`和`while`循环也是表达式，不过这里就不弄了

#### `switch-case` 多分支结构
在 MoonBit 中，这不叫简单的 `switch`，而是强大的 **模式匹配（Match）**。它比 Go 的 `switch` 强大得多，支持解构和类型检查
##### 基本匹配
```js
let num = 2
match num {
  1 => println("One")
  2 => println("Two")
  _ => println("Other") // _ 相当于 Go 的 default
}
```

##### 表达式用法
```js
let result = match num {
  1 => "One"
  2 => "Two"
  _ => "Unknown"
}
```

:::important Go 程序员需要注意的差异
|**特性**|**Go 习惯**|**MoonBit 习惯**|
|---|---|---|
|**返回值**|`if` 仅作为语句|`if` 和 `match` 都是表达式，可以返回值|
|**括号**|`if (cond)` 可选|`if cond` 强制不带括号（带了编译器会提醒）|
|**Switch 行为**|默认 `break`，除非 `fallthrough`|匹配即停止，不支持 `fallthrough`|
|**默认分支**|`default:`|`_ =>`|
:::

### 变量类型
:::note
参见[Moonbit文档](https://docs.moonbitlang.cn/language/fundamentals.html#built-in-data-structures)，此处不再赘述
:::


### 函数
#### 基本定义
MoonBit 使用 `fn` 关键字来定义函数
##### 有返回值 VS 无返回值
- **无返回值（Unit）：** 如果函数不返回任何东西，你可以省略返回类型，或者显式写作 `Unit`（相当于 Go 的空返回）。
- **有返回值：** 使用 `->` 符号指明返回类型。

```js
// MoonBit: 无返回值
fn say_hello(name : String) -> Unit {
  println("Hello, \{name}")
}

// MoonBit: 有返回值 (计算两个 Int 的和)
fn add(a : Int, b : Int) -> Int {
  a + b  // 注意：最后一行表达式即为返回值，不需要写 return 关键字
}
```
:::tip
在 MoonBit 中，函数体内的最后一个表达式会自动作为返回值。虽然你也可以用 `return` 提前返回，但习惯上我们更倾向于省略它，让代码更简洁。
:::

#### 闭包函数
和 Go 的闭包类似，MoonBit 的函数可以捕获其作用域之外的变量。这在 UI 开发中处理点击事件或回调时非常常见。
```js
fn make_adder(x : Int) -> (Int) -> Int {
  fn(y) { x + y } // 捕获了外部的 x
}

let add_five = make_adder(5)
println(add_five(10)) // 输出 15
```

#### Lambda函数/匿名函数
在 Go 中你会写 `func(x int) int { return x + 1 }`。在 MoonBit 中，Lambda 表达式非常简洁，通常用于高阶函数（如 `map`, `filter`）

**语法格式：** `fn(参数) { 表达式 }`
```js
let numbers = [1, 2, 3]

// 使用 Lambda 函数将数组每个元素乘 2
// 这里的 map 接受一个函数作为参数
let doubled = numbers.map(fn(x) { x * 2 })
```

### 复合变量类型
#### Array
MoonBit 的 `Array` 最接近 Go 的 `slice`（切片）。它是**长度固定**且**连续存储**的，但你可以修改其中的元素。

- **特点：** 性能最高，随机访问快
- **语法**
```js
let arr = [1, 2, 3] // 自动推导为 Array[Int]
arr[0] = 10         // ✅ 修改元素
// arr.push(4)      // ❌ 错误：Array 长度是固定的
```

#### List
Go 程序员可能不太常用纯链表，但在 MoonBit 这种带有函数式基因的语言中，`List` 是递归处理数据的常客。

- **特点：** **不可变**。你不能修改 List 里的元素，只能通过“头+尾”的方式产生新 List。
- **语法：**
```js
let list : List[Int] = List::[1, 2, 3]
let newList = List::Cons(0, list) // 在头部插入，生成 [0, 1, 2, 3]
```

#### Map
对应 Go 的 `map[K]V`。MoonBit 提供了两种主要的 Map 实现：
- **`@immutable.Map`**：不可变 Map。每次修改都会返回一个包含新值的新 Map，而原始 Map 保持不变（非常适合 UI 状态撤销/重做功能）。
- **`@hashmap.HashMap`**：可变 Map。性能与 Go 的 `map` 相当，支持原地修改。

```js
// 使用 HashMap (需导入)
let scores = @hashmap.new()
scores.set("Alice", 90)
println(scores.get("Alice")) // Some(90)
```
#### *Set*
MoonBit 核心库目前通过 `@hashset` 或 `@sorted_set` 提供 Set 功能

```js
let s = @hashset.new()
s.insert(1)
println(s.contains(1)) // true
```

|**数据类型**|**Go 对应物**|**核心差异点**|
|---|---|---|
|**Array**|`slice` (切片)|MoonBit Array 长度固定（类似 `[3]int` 但底层更像 slice）|
|**FixedArray**|`[N]T` (数组)|更加底层的固定长度数组，常用于性能优化|
|**List**|(无直接对应)|Go 通常用 slice 代替，MoonBit 常用 List 做模式匹配|
|**Map**|`map[K]V`|MoonBit 区分可变 (HashMap) 和不可变 (Immutable Map)|
### OOP
#### 结构体定义
MoonBit 的 `struct` 是实实在在的数据容器，这点和 Go 非常像。
- **默认私有**：字段默认包内可见。
- **显式可变性**：字段前必须加 `mut` 才能被修改。

```js
// examine.mbt
pub struct Button {
  id : String
  pub label : String
  mut is_pressed : Bool // 只有这个字段能被修改
}
```

#### Trait实现
这是差异最大的地方。Go 是**隐式实现**（只要方法签对上了就行），而 MoonBit 是**显式实现**（使用 `impl` 关键字）
##### 定义接口
```js
trait Clickable {
  click(Self) -> Unit
}
```

##### 实现接口
在 MoonBit 中，你需要明确告诉编译器 *我要为某个类型实现某个 Trait*
```js
impl Clickable for Button with click(self) {
  self.is_pressed = true
  println("Button \{self.label} was clicked!")
}
```

#### 实例化
实例化不需要 `new`，也不强制使用指针
```js
let btn = { id: "btn-01", label: "Submit", is_pressed: false }
btn.click() // 调用 Trait 中定义的方法
```

```js
pub struct Button { // 当Button的定义和引用位于同一模块时，编译器会警告pub可以移除
  id : String
  pub label : String
  mut is_pressed : Bool // 只有这个字段能被修改
}


trait Clickable {
  click(Self) -> Unit
}
impl Clickable for Button with click(self) {
  self.is_pressed = true
  println("Button \{self.label} was clicked!")
}

fn main {
  let btn = { id: "btn-01", label: "Submit", is_pressed: false }
  btn.click() // 调用 Trait 中定义的方法
}
```

:::warning moonbit的**匿名结构体初始化**
当你写 `let u = { name: "Alice", age: 18 }` 时，MoonBit 的**类型推导系统**会根据当前上下文（Context）来匹配对应的结构体类型
```js
struct User { name : String; age : Int }
struct Admin { name : String; age : Int }

fn handle_user(u : User) { ... }

fn main {
  // 这里编译器会自动推导出这是 User，因为 handle_user 需要 User
  handle_user({ name: "Bob", age: 20 }) 
}
```

那么问题来了，**如果存在两个字段一模一样的结构体，怎么办？**
MoonBit 采用的是 **名义类型系统（Nominal Typing）**，而不是 Go 那种在特定条件下可以相互转换的**结构类型系统（Structural Typing）**
- **Go 的逻辑：** 如果两个匿名结构体字段一样，它们有时可以互相赋值或比较。
- **MoonBit 的逻辑：** 即使字段完全一样，`User` 就是 `User`，`Admin` 就是 `Admin`，它们是**完全不同**的类型。
***
如果你定义的两个结构体完全一样，且没有上下文提示，编译器会报错
```js
struct User { name : String }
struct Person { name : String }

fn main {
  let x = { name: "Alice" } // ❌ 编译错误：Ambiguous record literal
}
```

在这种情况下，你需要显式地指明其中一个字段的来源，或者给变量标类型
```js
let x : User = { name: "Alice" } // 方案 A：标类型
let y = { User::name: "Bob" }    // 方案 B：指明字段所属的命名空间
```
:::

### 【隐式行为合集】语法糖
#### 结构体深拷贝并更新字段
在 Go 中，修改并获取新结构体的常见方法是：
```go
// Go
newBtn := oldBtn
newBtn.Label = "Clicked"
// 此时 oldBtn 如果是值拷贝则没问题，如果是指针则原值也变了
```

而在Moonbit中则为：
```js
let new_btn = { ..old_btn, label: "Clicked" }
```
- **隐式行为：** 这行代码隐式地创建了一个 **新实例**，并将 `old_btn` 的其他字段拷贝过来。它不会修改 `old_btn`。
- **注意：** 如果字段是 `mut` 的，这种方式依然会创建一个全新的、独立的对象拷贝。

### 泛型
#### 泛型结构体
在 Go 中你写 `type Stack[T any] struct { ... }`，在 MoonBit 中也使用方括号 `[]`：
```js
// MoonBit
struct Box[T] {
  value : T
}

let int_box : Box[Int] = { value: 42 }
let str_box : Box[String] = { value: "Hello" }
```

#### 泛型函数
```js
// 一个简单的交换函数
fn swap[T](arr : Array[T], i : Int, j : Int) -> Unit {
  let temp = arr[i]
  arr[i] = arr[j]
  arr[j] = temp
}
```

#### 泛型约束
这是最关键的部分，对应 Go 里的 `[T comparable]` 或 `[T constraint]`。在 MoonBit 中，我们使用 **`T : Trait`** 语法。
```js
// 要求 T 必须实现了 Show 这个 Trait
fn print_item[T : Show](item : T) -> Unit {
  println(item)
}
```

|**特性**|**Go (Golang)**|**MoonBit**|
|---|---|---|
|**定义语法**|`[T any]`|`[T]` (默认为 any)|
|**约束语法**|`[T interface{...}]`|`[T : TraitName]`|
|**多重约束**|`[T interface{ C1; C2 }]`|`[T : C1 + C2]`|
|**性能**|运行时可能有开销 (GCShape)|编译期单态化 (类似 Rust)，零开销|
### 其他
#### 包管理
:::note 参考资料
- 中西合并英文混着中文写的[逆天官方文档](https://docs.moonbitlang.cn/language/packages.html)
- [官方 - 模块配置](https://docs.moonbitlang.cn/toolchain/moon/module.html)
- [官方 - 包配置](https://docs.moonbitlang.cn/toolchain/moon/package.html)
:::


#### 深度调试（变量结构打印）
#### 运算符重载
在 Go 中，你不能重载 `+` 或 `==`。但在 MoonBit 中，你可以为自定义类型定义特定的运算符逻辑。这在处理 UI 坐标计算或颜色叠加时极其方便。

**实现方式：** 只需实现以 `op_` 开头的特定函数。

|**运算符**|**对应函数**|
|---|---|
|`+`|`op_add`|
|`-`|`op_sub`|
|`[]`|`op_get` (索引读取)|
|`[]=`|`op_set` (索引写入)|

```js
struct Vec2 { x : Int; y : Int }

fn op_add(self : Vec2, other : Vec2) -> Vec2 {
  { x: self.x + other.x, y: self.y + other.y }
}

let v1 = { x: 1, y: 2 }
let v2 = { x: 3, y: 4 }
let v3 = v1 + v2 // ✅ 像内置类型一样运算
```

***
# 页面底部

