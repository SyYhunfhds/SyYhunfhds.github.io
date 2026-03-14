---
title: Kotlin String 方法大全
date: 2026-03-08
footer: Trae编辑
---


## 目录

1. [基本属性](#基本属性)
2. [访问元素](#访问元素)
3. [检查操作](#检查操作)
4. [查找操作](#查找操作)
5. [转换操作](#转换操作)
6. [修改操作](#修改操作)
7. [分割操作](#分割操作)
8. [连接操作](#连接操作)
9. [填充操作](#填充操作)
10. [反转操作](#反转操作)
11. [重复操作](#重复操作)
12. [比较操作](#比较操作)
13. [格式化操作](#格式化操作)
14. [正则表达式](#正则表达式)
15. [其他操作](#其他操作)

---

## 基本属性

### `length`
返回字符串的长度

```kotlin
val str = "Hello"
println(str.length)  // 输出: 5
```

### `indices`
返回字符串的有效索引范围

```kotlin
val str = "Hello"
println(str.indices)  // 输出: 0..4
for (i in str.indices) {
    println(str[i])  // 输出: H e l l o
}
```

### `lastIndex`
返回字符串的最后一个索引

```kotlin
val str = "Hello"
println(str.lastIndex)  // 输出: 4
```

---

## 访问元素

### `get(index)` / `[index]`
返回指定索引处的字符

```kotlin
val str = "Hello"
println(str[0])  // 输出: H
println(str[4])  // 输出: o
println(str.get(1))  // 输出: e
```

### `elementAt(index)`
返回指定索引处的字符，如果索引越界会抛出异常

```kotlin
val str = "Hello"
println(str.elementAt(0))  // 输出: H
```

### `first()`
返回第一个字符

```kotlin
val str = "Hello"
println(str.first())  // 输出: H
```

### `last()`
返回最后一个字符

```kotlin
val str = "Hello"
println(str.last())  // 输出: o
```

### `firstOrNull()`
返回第一个字符，如果字符串为空则返回 null

```kotlin
val str = "Hello"
println(str.firstOrNull())  // 输出: H
println("".firstOrNull())  // 输出: null
```

### `lastOrNull()`
返回最后一个字符，如果字符串为空则返回 null

```kotlin
val str = "Hello"
println(str.lastOrNull())  // 输出: o
println("".lastOrNull())  // 输出: null
```

---

## 检查操作

### `contains(charSequence)`
检查字符串是否包含指定的字符序列

```kotlin
val str = "Hello World"
println(str.contains("World"))  // 输出: true
println(str.contains("Kotlin"))  // 输出: false
```

### `startsWith(prefix)`
检查字符串是否以指定前缀开头

```kotlin
val str = "Hello World"
println(str.startsWith("Hello"))  // 输出: true
println(str.startsWith("World"))  // 输出: false
```

### `endsWith(suffix)`
检查字符串是否以指定后缀结尾

```kotlin
val str = "Hello World"
println(str.endsWith("World"))  // 输出: true
println(str.endsWith("Hello"))  // 输出: false
```

### `isEmpty()`
检查字符串是否为空

```kotlin
val str1 = ""
val str2 = "Hello"
println(str1.isEmpty())  // 输出: true
println(str2.isEmpty())  // 输出: false
```

### `isNotEmpty()`
检查字符串是否不为空

```kotlin
val str1 = ""
val str2 = "Hello"
println(str1.isNotEmpty())  // 输出: false
println(str2.isNotEmpty())  // 输出: true
```

### `isBlank()`
检查字符串是否为空或只包含空白字符

```kotlin
val str1 = ""
val str2 = "   "
val str3 = "Hello"
println(str1.isBlank())  // 输出: true
println(str2.isBlank())  // 输出: true
println(str3.isBlank())  // 输出: false
```

### `isNotBlank()`
检查字符串是否不为空且不只包含空白字符

```kotlin
val str1 = ""
val str2 = "   "
val str3 = "Hello"
println(str1.isNotBlank())  // 输出: false
println(str2.isNotBlank())  // 输出: false
println(str3.isNotBlank())  // 输出: true
```

---

## 查找操作

### `indexOf(char)`
返回指定字符第一次出现的索引，如果不存在则返回 -1

```kotlin
val str = "Hello World"
println(str.indexOf('o'))  // 输出: 4
println(str.indexOf('z'))  // 输出: -1
```

### `lastIndexOf(char)`
返回指定字符最后一次出现的索引，如果不存在则返回 -1

```kotlin
val str = "Hello World"
println(str.lastIndexOf('o'))  // 输出: 7
println(str.lastIndexOf('z'))  // 输出: -1
```

### `indexOfFirst(predicate)`
返回第一个满足条件的字符索引

```kotlin
val str = "Hello World"
println(str.indexOfFirst { it.isUpperCase() })  // 输出: 0
println(str.indexOfFirst { it == 'o' })  // 输出: 4
```

### `indexOfLast(predicate)`
返回最后一个满足条件的字符索引

```kotlin
val str = "Hello World"
println(str.indexOfLast { it.isUpperCase() })  // 输出: 6
println(str.indexOfLast { it == 'o' })  // 输出: 7
```

---

## 转换操作

### `toLowerCase()`
将字符串转换为小写

```kotlin
val str = "Hello World"
println(str.toLowerCase())  // 输出: hello world
```

### `toUpperCase()`
将字符串转换为大写

```kotlin
val str = "Hello World"
println(str.toUpperCase())  // 输出: HELLO WORLD
```

### `toInt()`
将字符串转换为整数

```kotlin
val str = "123"
println(str.toInt())  // 输出: 123
```

### `toLong()`
将字符串转换为长整数

```kotlin
val str = "1234567890123"
println(str.toLong())  // 输出: 1234567890123
```

### `toFloat()`
将字符串转换为浮点数

```kotlin
val str = "3.14"
println(str.toFloat())  // 输出: 3.14
```

### `toDouble()`
将字符串转换为双精度浮点数

```kotlin
val str = "3.14159"
println(str.toDouble())  // 输出: 3.14159
```

### `toBoolean()`
将字符串转换为布尔值

```kotlin
val str1 = "true"
val str2 = "false"
println(str1.toBoolean())  // 输出: true
println(str2.toBoolean())  // 输出: false
```

### `toCharArray()`
将字符串转换为字符数组

```kotlin
val str = "Hello"
val chars = str.toCharArray()
println(chars.contentToString())  // 输出: [H, e, l, l, o]
```

### `toList()`
将字符串转换为字符列表

```kotlin
val str = "Hello"
val list = str.toList()
println(list)  // 输出: [H, e, l, l, o]
```

---

## 修改操作

### `replace(oldValue, newValue)`
替换字符串中的所有匹配项

```kotlin
val str = "Hello World"
println(str.replace("World", "Kotlin"))  // 输出: Hello Kotlin
println(str.replace("l", "L"))  // 输出: HeLLo WorLd
```

### `replaceBefore(delimiter, replacement)`
替换指定分隔符之前的内容

```kotlin
val str = "Hello World"
println(str.replaceBefore(" ", "Hi"))  // 输出: Hi World
```

### `replaceAfter(delimiter, replacement)`
替换指定分隔符之后的内容

```kotlin
val str = "Hello World"
println(str.replaceAfter(" ", "Kotlin"))  // 输出: Hello Kotlin
```

### `replaceFirst(oldValue, newValue)`
替换第一个匹配项

```kotlin
val str = "Hello Hello"
println(str.replaceFirst("Hello", "Hi"))  // 输出: Hi Hello
```

### `trim()`
去除字符串两端的空白字符

```kotlin
val str = "  Hello World  "
println(str.trim())  // 输出: Hello World
```

### `trimStart()`
去除字符串开头的空白字符

```kotlin
val str = "  Hello World"
println(str.trimStart())  // 输出: Hello World
```

### `trimEnd()`
去除字符串末尾的空白字符

```kotlin
val str = "Hello World  "
println(str.trimEnd())  // 输出: Hello World
```

### `drop(n)`
删除前 n 个字符

```kotlin
val str = "Hello World"
println(str.drop(6))  // 输出: World
```

### `dropLast(n)`
删除后 n 个字符

```kotlin
val str = "Hello World"
println(str.dropLast(6))  // 输出: Hello
```

### `dropWhile(predicate)`
删除满足条件的开头字符

```kotlin
val str = "123Hello"
println(str.dropWhile { it.isDigit() })  // 输出: Hello
```

### `dropLastWhile(predicate)`
删除满足条件的末尾字符

```kotlin
val str = "Hello123"
println(str.dropLastWhile { it.isDigit() })  // 输出: Hello
```

### `take(n)`
取前 n 个字符

```kotlin
val str = "Hello World"
println(str.take(5))  // 输出: Hello
```

### `takeLast(n)`
取后 n 个字符

```kotlin
val str = "Hello World"
println(str.takeLast(5))  // 输出: World
```

### `takeWhile(predicate)`
取满足条件的开头字符

```kotlin
val str = "Hello123World"
println(str.takeWhile { it.isLetter() })  // 输出: Hello
```

### `takeLastWhile(predicate)`
取满足条件的末尾字符

```kotlin
val str = "Hello123World"
println(str.takeLastWhile { it.isLetter() })  // 输出: World
```

---

## 分割操作



### `split(delimiters, ignoreCase)`
忽略大小写分割

```kotlin
val str = "Hello,WORLD,kotlin"
val parts = str.split(",", ignoreCase = true)
println(parts)  // 输出: [Hello, WORLD, kotlin]
```

### `lines()`
将字符串按行分割

```kotlin
val str = "Line1\nLine2\nLine3"
val lines = str.lines()
println(lines)  // 输出: [Line1, Line2, Line3]
```

---

## 连接操作

### `plus(other)`
连接两个字符串

```kotlin
val str1 = "Hello"
val str2 = " World"
println(str1 + str2)  // 输出: Hello World
println(str1.plus(str2))  // 输出: Hello World
```

### `joinToString(separator)`
将集合转换为字符串，用指定分隔符连接

```kotlin
val list = listOf("Hello", "World", "Kotlin")
println(list.joinToString(", "))  // 输出: Hello, World, Kotlin
```

---

## 填充操作

### `padStart(length, padChar)`
在字符串开头填充指定字符

```kotlin
val str = "123"
println(str.padStart(5, '0'))  // 输出: 00123
```

### `padEnd(length, padChar)`
在字符串末尾填充指定字符

```kotlin
val str = "123"
println(str.padEnd(5, '0'))  // 输出: 12300
```

---

## 反转操作

### `reversed()`
返回反转后的字符串

```kotlin
val str = "Hello"
println(str.reversed())  // 输出: olleH
```

---

## 重复操作

### `repeat(n)`
重复字符串 n 次

```kotlin
val str = "Hello"
println(str.repeat(3))  // 输出: HelloHelloHello
```

---

## 比较操作

### `compareTo(other)`
比较两个字符串

```kotlin
val str1 = "Apple"
val str2 = "Banana"
println(str1.compareTo(str2))  // 输出: -1 (小于)
println(str2.compareTo(str1))  // 输出: 1 (大于)
println(str1.compareTo(str1))  // 输出: 0 (等于)
```

### `equals(other)`
检查两个字符串是否相等

```kotlin
val str1 = "Hello"
val str2 = "Hello"
val str3 = "World"
println(str1.equals(str2))  // 输出: true
println(str1.equals(str3))  // 输出: false
```

### `equals(other, ignoreCase)`
忽略大小写比较

```kotlin
val str1 = "Hello"
val str2 = "hello"
println(str1.equals(str2, ignoreCase = true))  // 输出: true
```

---

## 格式化操作

### `capitalize()`
将字符串首字母大写

```kotlin
val str = "hello"
println(str.capitalize())  // 输出: Hello
```

### `decapitalize()`
将字符串首字母小写

```kotlin
val str = "Hello"
println(str.decapitalize())  // 输出: hello
```

---

## 正则表达式

### `matches(regex)`
检查字符串是否匹配正则表达式

```kotlin
val str = "12345"
println(str.matches(Regex("\\d+")))  // 输出: true
println(str.matches(Regex("[a-z]+")))  // 输出: false
```

### `replace(regex, replacement)`
使用正则表达式替换

```kotlin
val str = "Hello123World456"
println(str.replace(Regex("\\d+"), ""))  // 输出: HelloWorld
```

### `split(regex)`
使用正则表达式分割字符串

```kotlin
val str = "Hello,World;Kotlin"
val parts = str.split(Regex("[,;]"))
println(parts)  // 输出: [Hello, World, Kotlin]
```

### `toRegex()`
将字符串转换为正则表达式

```kotlin
val pattern = "\\d+".toRegex()
println("12345".matches(pattern))  // 输出: true
```

---

## 其他操作

### `chunked(size)`
将字符串分成指定大小的块

```kotlin
val str = "HelloWorld"
val chunks = str.chunked(3)
println(chunks)  // 输出: [Hel, loW, orl, d]
```

### `windowed(size, step)`
创建滑动窗口

```kotlin
val str = "Hello"
val windows = str.windowed(3)
println(windows)  // 输出: [Hel, ell, llo]
```

### `substring(startIndex, endIndex)`
提取子字符串

```kotlin
val str = "Hello World"
println(str.substring(0, 5))  // 输出: Hello
println(str.substring(6))  // 输出: World
```

### `substring(startIndex)`
从指定索引开始到末尾

```kotlin
val str = "Hello World"
println(str.substring(6))  // 输出: World
```

---

## 扩展函数示例

### 自定义反转函数

```kotlin
fun String.reverse(): String {
    val reStr = StringBuilder()
    for (i in this.length - 1 downTo 0) {
        reStr.append(this[i])
    }
    return reStr.toString()
}

val str = "Hello"
println(str.reverse())  // 输出: olleH
```

### 检查是否为回文

```kotlin
fun String.isPalindrome(): Boolean {
    return this == this.reversed()
}

println("level".isPalindrome())  // 输出: true
println("hello".isPalindrome())  // 输出: false
```

### 统计字符出现次数

```kotlin
fun String.countChar(char: Char): Int {
    return this.count { it == char }
}

val str = "Hello World"
println(str.countChar('l'))  // 输出: 3
println(str.countChar('o'))  // 输出: 2
```

---

## 注意事项

1. **字符串不可变性**：Kotlin 中的字符串是不可变的，所有修改操作都会返回新的字符串
2. **索引范围**：字符串索引从 0 开始，最大索引为 `length - 1`
3. **空字符串 vs null**：空字符串 `""` 不是 `null`，调用方法不会抛出空指针异常
4. **性能考虑**：频繁的字符串拼接建议使用 `StringBuilder`
5. **正则表达式**：复杂匹配建议预编译正则表达式以提高性能

---

## 最佳实践

1. 使用 `isBlank()` 和 `isNotBlank()` 检查用户输入
2. 使用 `trim()` 清理用户输入的空白字符
3. 使用 `split()` 解析 CSV 或其他分隔符数据
4. 使用 `joinToString()` 构建格式化输出
5. 使用 `StringBuilder` 进行大量字符串拼接操作
6. 使用 `equals(other, ignoreCase)` 进行不区分大小写的比较
7. 使用 `toIntOrNull()` 等安全转换方法避免异常

---

## 相关资源

- [Kotlin 官方文档 - Strings](https://kotlinlang.org/docs/strings.html)
- [Kotlin 标准库 - String](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin/-string/)
