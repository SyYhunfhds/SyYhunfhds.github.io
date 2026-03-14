---
title: Kotlin StringBuilder 操作

date: 2026-03-13

footer: Trae编辑

---


## 目录

1. [概述](#概述)
2. [创建 StringBuilder](#创建-stringbuilder)
3. [基本操作](#基本操作)
4. [高级操作](#高级操作)
5. [转换操作](#转换操作)
6. [性能优化](#性能优化)
7. [注意事项](#注意事项)
8. [示例](#示例)
9. [与 StringBuffer 的对比](#与-stringbuffer-的对比)

## 概述

**StringBuilder** 是 Kotlin 中用于高效构建字符串的可变字符序列类。它提供了一系列方法来修改字符序列，而不会像 String 那样每次操作都创建新的对象，从而提高性能。

**主要特点**：
- 可变的字符序列
- 非线程安全（但性能更好）
- 支持链式调用
- 提供丰富的字符串操作方法
- 适合频繁修改字符串的场景

## 创建 StringBuilder

### 基本创建

```kotlin
// 创建空的 StringBuilder
val sb1 = StringBuilder()

// 指定初始容量
val sb2 = StringBuilder(100)  // 初始容量为 100

// 使用初始字符串
val sb3 = StringBuilder("Hello")

// 指定初始字符串和容量
val sb4 = StringBuilder("Hello", 100)
```

### 从其他类型创建

```kotlin
// 从 String 创建
val str = "Hello"
val sb1 = StringBuilder(str)

// 从 CharSequence 创建
val charSeq: CharSequence = "World"
val sb2 = StringBuilder(charSeq)
```

## 基本操作

### 追加操作

| 方法 | 说明 | 示例 |
|------|------|------|
| `append(value: Any?)` | 追加任意类型的值 | `sb.append("World")` |
| `append(char: Char)` | 追加单个字符 | `sb.append('!')` |
| `append(csq: CharSequence?)` | 追加字符序列 | `sb.append(" Kotlin")` |
| `append(csq: CharSequence?, start: Int, end: Int)` | 追加字符序列的一部分 | `sb.append("Hello World", 6, 11)` |
| `append(array: CharArray)` | 追加字符数组 | `sb.append(charArrayOf('a', 'b', 'c'))` |
| `append(array: CharArray, offset: Int, len: Int)` | 追加字符数组的一部分 | `sb.append(charArrayOf('a', 'b', 'c'), 1, 2)` |
| `appendCodePoint(codePoint: Int)` | 追加 Unicode 代码点 | `sb.appendCodePoint(0x1F600)` // 😀 |

### 插入操作

| 方法 | 说明 | 示例 |
|------|------|------|
| `insert(index: Int, value: Any?)` | 在指定位置插入任意类型 | `sb.insert(5, " ")` |
| `insert(index: Int, char: Char)` | 在指定位置插入单个字符 | `sb.insert(0, 'H')` |
| `insert(index: Int, csq: CharSequence?)` | 在指定位置插入字符序列 | `sb.insert(0, "Hello")` |
| `insert(index: Int, csq: CharSequence?, start: Int, end: Int)` | 插入字符序列的一部分 | `sb.insert(0, "Hello World", 6, 11)` |
| `insert(index: Int, array: CharArray)` | 插入字符数组 | `sb.insert(0, charArrayOf('a', 'b'))` |
| `insert(index: Int, array: CharArray, offset: Int, len: Int)` | 插入字符数组的一部分 | `sb.insert(0, charArrayOf('a', 'b', 'c'), 1, 2)` |
| `insert(index: Int, codePoint: Int)` | 插入 Unicode 代码点 | `sb.insert(0, 0x1F600)` |

### 删除操作

| 方法 | 说明 | 示例 |
|------|------|------|
| `delete(start: Int, end: Int)` | 删除从 start 到 end-1 的字符 | `sb.delete(5, 11)` |
| `deleteCharAt(index: Int)` | 删除指定位置的字符 | `sb.deleteCharAt(0)` |

### 替换操作

| 方法 | 说明 | 示例 |
|------|------|------|
| `replace(start: Int, end: Int, str: String)` | 替换从 start 到 end-1 的字符 | `sb.replace(0, 5, "Hi")` |
| `setCharAt(index: Int, ch: Char)` | 替换指定位置的字符 | `sb.setCharAt(0, 'h')` |

### 其他基本操作

| 方法 | 说明 | 示例 |
|------|------|------|
| `length` | 获取当前长度 | `val len = sb.length` |
| `capacity` | 获取当前容量 | `val cap = sb.capacity()` |
| `ensureCapacity(minimumCapacity: Int)` | 确保容量至少为指定值 | `sb.ensureCapacity(100)` |
| `trimToSize()` | 调整容量为实际长度 | `sb.trimToSize()` |
| `setLength(newLength: Int)` | 设置新长度 | `sb.setLength(5)` |
| `charAt(index: Int)` | 获取指定位置的字符 | `val char = sb.charAt(0)` |
| `get(index: Int)` | 获取指定位置的字符（运算符重载） | `val char = sb[0]` |
| `substring(start: Int, end: Int = length)` | 获取子字符串 | `val substr = sb.substring(0, 5)` |
| `subSequence(start: Int, end: Int)` | 获取子字符序列 | `val subseq = sb.subSequence(0, 5)` |

## 高级操作

### 反转操作

```kotlin
val sb = StringBuilder("Hello")
sb.reverse() // 结果: "olleH"
```

### 链式调用

```kotlin
val sb = StringBuilder()
    .append("Hello")
    .append(" ")
    .append("World")
    .append('!')
// 结果: "Hello World!"
```

### 查找操作

```kotlin
val sb = StringBuilder("Hello World")

// 查找字符
val index1 = sb.indexOf('W') // 返回 6

// 从指定位置查找
val index2 = sb.indexOf('o', 5) // 返回 7

// 查找字符串
val index3 = sb.indexOf("World") // 返回 6

// 从后向前查找
val index4 = sb.lastIndexOf('o') // 返回 7
```

### 字符遍历

```kotlin
val sb = StringBuilder("Hello")

// 使用 forEach
for (char in sb) {
    println(char)
}

// 使用 for 循环
for (i in 0 until sb.length) {
    println(sb[i])
}
```

## 转换操作

### 转换为 String

```kotlin
val sb = StringBuilder("Hello")
val str = sb.toString() // "Hello"
```

### 转换为其他类型

```kotlin
val sb = StringBuilder("12345")

// 转换为 Int
val intValue = sb.toString().toInt() // 12345

// 转换为 Long
val longValue = sb.toString().toLong() // 12345L

// 转换为 Double
val doubleValue = StringBuilder("3.14").toString().toDouble() // 3.14
```

## 性能优化

### 预分配容量

```kotlin
// 预估最终字符串长度，预分配容量
val sb = StringBuilder(200) // 避免频繁扩容
```

### 避免不必要的字符串创建

```kotlin
// 推荐：使用 StringBuilder 拼接
val sb = StringBuilder()
for (i in 1..1000) {
    sb.append(i).append(' ')
}
val result = sb.toString()

// 不推荐：每次循环都创建新字符串
var result = ""
for (i in 1..1000) {
    result += i + " " // 每次都创建新对象
}
```

### 合理使用 trimToSize

```kotlin
val sb = StringBuilder(1000) // 大容量
// 进行大量操作后
// ...
sb.trimToSize() // 释放多余容量
```

## 注意事项

1. **非线程安全**：StringBuilder 不是线程安全的，如果在多线程环境中使用，需要手动同步
2. **索引越界**：操作时要注意索引范围，避免 IndexOutOfBoundsException
3. **容量管理**：初始容量设置过小会导致频繁扩容，影响性能
4. **内存使用**：大型 StringBuilder 可能占用较多内存，使用后应及时处理
5. **null 值处理**：append(null) 会添加字符串 "null"，而不是空字符串
6. **字符编码**：注意 Unicode 字符的处理，特别是使用 appendCodePoint 时
7. **链式调用**：链式调用虽然方便，但过长的链式调用可能影响可读性

## 示例

### 示例 1：构建复杂字符串

```kotlin
fun buildUserInfo(name: String, age: Int, email: String): String {
    return StringBuilder()
        .append("User Info:\n")
        .append("Name: ").append(name).append("\n")
        .append("Age: ").append(age).append("\n")
        .append("Email: ").append(email)
        .toString()
}

// 使用
val userInfo = buildUserInfo("Alice", 30, "alice@example.com")
println(userInfo)

// 输出：
// User Info:
// Name: Alice
// Age: 30
// Email: alice@example.com
```

### 示例 2：处理 CSV 数据

```kotlin
fun createCSV(headers: List<String>, rows: List<List<String>>): String {
    val sb = StringBuilder()
    
    // 添加表头
    headers.forEachIndexed { index, header ->
        if (index > 0) sb.append(',')
        sb.append('"').append(header).append('"')
    }
    sb.append('\n')
    
    // 添加数据行
    rows.forEach { row ->
        row.forEachIndexed { index, value ->
            if (index > 0) sb.append(',')
            sb.append('"').append(value).append('"')
        }
        sb.append('\n')
    }
    
    return sb.toString()
}

// 使用
val headers = listOf("Name", "Age", "City")
val rows = listOf(
    listOf("Alice", "30", "New York"),
    listOf("Bob", "25", "London"),
    listOf("Charlie", "35", "Paris")
)
val csv = createCSV(headers, rows)
println(csv)

// 输出：
// "Name","Age","City"
// "Alice","30","New York"
// "Bob","25","London"
// "Charlie","35","Paris"
```

### 示例 3：字符串替换和删除

```kotlin
fun processText(text: String): String {
    return StringBuilder(text)
        // 替换敏感信息
        .replace(text.indexOf("password:"), text.indexOf("\n", text.indexOf("password:")), "password: *****")
        // 删除多余空格
        .replace(Regex("\\s+"), " ")
        // 首字母大写
        .also { if (it.isNotEmpty()) it.setCharAt(0, it[0].uppercaseChar()) }
        .toString()
}

// 使用
val text = "hello world\npassword: secret123\nwelcome to kotlin"
val processed = processText(text)
println(processed)

// 输出：
// Hello world password: ***** welcome to kotlin
```

## 与 StringBuffer 的对比

| 特性 | StringBuilder | StringBuffer |
|------|--------------|--------------|
| 线程安全 | 否 | 是 |
| 性能 | 更高 | 较低（同步开销） |
| API | 相同 | 相同 |
| 适用场景 | 单线程环境 | 多线程环境 |

**选择建议**：
- 大多数情况下使用 StringBuilder（性能更好）
- 仅在多线程环境且需要线程安全时使用 StringBuffer

## 总结

StringBuilder 是 Kotlin 中处理字符串构建的强大工具，特别适合需要频繁修改字符串的场景。通过合理使用其 API，可以显著提高字符串处理的性能和代码可读性。

**核心要点**：
1. 预分配合适的初始容量以提高性能
2. 利用链式调用简化代码
3. 注意线程安全问题（单线程环境使用 StringBuilder）
4. 避免索引越界错误
5. 合理使用 trimToSize 释放多余内存

通过掌握 StringBuilder 的使用技巧，可以在处理字符串时写出更高效、更简洁的代码。