---
title: mbt 语法学习笔记（一）
date: 2026-04-20
---
[[toc]]
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

### 基本数据类型
#### Unit
常用于函数的**空返回值**
```js
fn print_hello() -> Unit {
  println("Hello, world!")
}
```

> `Unit` 类似于 C/C++/Java 中的 `void`，但与 `void` 不同的是，它是一个真正的类型，可以在任何需要类型的地方使用
> 与其他一些语言不同，MoonBit 将 `Unit` 视为一等类型，允许它在泛型中使用、存储在数据结构中以及作为函数参数传递。

#### 布尔值
```js
let a = true
let b = false
let c = a && b
let d = a || b
let e = !a
let f = !(a && b)
```
- mbt内置的布尔值是`true`和`false`
- `!statement`等价于`not(statement)`
#### 数值
- 包括**整型**和**浮点型**

| 类型       | 描述           | 示例                         |
| -------- | ------------ | -------------------------- |
| `Int16`  | *略 (下同)*     | `(42 : Int16)`             |
| `Int`    |              | `42`                       |
| `Int64`  |              | `1000L`                    |
| `UInt16` |              | `(14 : UInt16)`            |
| `UInt`   |              | `14U`                      |
| `UInt64` |              | `14UL`                     |
| `Double` |              | `3.14`                     |
| `Float`  |              | `(3.14 : Float)`           |
| `BigInt` | 表示比其他类型更大的数值 | `10000000000000000000000N` |
- MoonBit 还支持数字**字面量**，包括十进制、二进制、八进制和十六进制数字
- MoonBit 允许在较大的数字字面量中间放置下划线，如`1_000_000`；**可以放在任意位之间**，而不是必须每三位才能放一个
- 以下是Moonbit其他**可以提升代码可读性**的特性：
	- 十进制数之间可以有下划线
		默认情况下，整数字面量是有符号的 32 位数字。对于无符号数字，需要后缀 `U`；对于 64 位数字，需要后缀 `L`。
		```js
		let a = 1234
		let b : Int = 1_000_000 + a
		let unsigned_num       : UInt   = 4_294_967_295U
		let large_num          : Int64  = 9_223_372_036_854_775_807L
		let unsigned_large_num : UInt64 = 18_446_744_073_709_551_615UL
		```
	- 二进制数有一个前导零，后跟字母 “B”，即 `0b`/`0B`
		```js
		let bin = 0b110010
		let another_bin = 0B110010
		```
	- 八进制数有一个前导零，后跟字母 “O”，即 `0o`/`0O`
		```js
		let octal = 0o1234
		let another_octal = 0O1234
		```
	- 十六进制数有一个前导零，后跟字母 “X”，即 `0x`/`0X`
		请注意，`0x`/`0X` 后的数字必须在 `0123456789ABCDEF` 范围内
		```js
		let hex = 0XA
		let another_hex = 0xA_B_C
		```
	- 浮点数字面量是 64 位浮点数
		要定义一个浮点数，需要类型注释
		```js
		let double = 3.14 // Double
		let float : Float = 3.14
		let float2 = (3.14 : Float)
		```
		64 位浮点数也可以使用十六进制格式定义：
		```js
		let hex_double = 0x1.2P3 // (1.0 + 2 / 16) * 2^(+3) == 9
		```
- 当期望的类型已知时，MoonBit 可以自动重载字面量，无需通过字母后缀指定数字的类型：
```js
let int : Int = 42
let uint : UInt = 42
let int64 : Int64 = 42
let double : Double = 42
let float : Float = 42
let bigint : BigInt = 42
```
#### 字符串
#### 字符
#### 字节
#### 元组
#### 引用 / Ref
#### Option 和 Result
#### 数组
#### Map
#### Json

### 小测试：找到通过考试的人

***
# 页面底部

