---
title: Kotlin Range 操作
date: 2026-03-14
footer: Trae编辑
---


## 目录

1. [Range 概述](#range-概述)
2. [IntRange](#intrange)
3. [LongRange](#longrange)
4. [CharRange](#charrange)
5. [ClosedRange](#closedranget)
6. [OpenEndRange](#openendranget)
7. [Progression](#progressiont)
8. [Range 操作符](#range-操作符)
9. [使用注意事项](#使用注意事项)
10. [最佳实践](#最佳实践)

## Range 概述

Kotlin Range 是用于表示一系列值的类，主要用于循环和条件判断。Range 提供了简洁的语法来表示连续的值序列，支持整数、长整数和字符类型。

**核心特性**：
- 支持闭区间和半开区间
- 支持步长控制
- 提供丰富的操作符和函数
- 与 for 循环和 when 表达式完美集成

## IntRange

### 基本属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `start` | Int | 范围的起始值（包含） |
| `endInclusive` | Int | 范围的结束值（包含） |
| `endExclusive` | Int | 范围的结束值（不包含） |
| `first` | Int | 范围的第一个元素 |
| `last` | Int | 范围的最后一个元素 |
| `step` | Int | 范围的步长 |

### 基本方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `contains(value: Int)` | Boolean | 检查值是否在范围内 |
| `isEmpty()` | Boolean | 检查范围是否为空 |
| `iterator()` | IntIterator | 获取范围的迭代器 |

### 用法示例

```kotlin
// 创建 IntRange
val range1 = 1..10        // [1, 10] 闭区间
val range2 = 1 until 10    // [1, 10) 半开区间
val range3 = 10 downTo 1    // [10, 1] 递减区间
val range4 = 1..10 step 2   // [1, 3, 5, 7, 9] 步长为2

// 访问属性
println(range1.start)        // 1
println(range1.endInclusive)  // 10
println(range1.first)         // 1
println(range1.last)          // 10
println(range1.step)          // 1

// 使用方法
println(range1.contains(5))   // true
println(range1.contains(11))  // false
println(range1.isEmpty())     // false

// 在循环中使用
for (i in 1..10) {
    println(i)  // 1, 2, 3, ..., 10
}

for (i in 1 until 10) {
    println(i)  // 1, 2, 3, ..., 9
}

for (i in 10 downTo 1) {
    println(i)  // 10, 9, 8, ..., 1
}

for (i in 1..10 step 2) {
    println(i)  // 1, 3, 5, 7, 9
}
```

## LongRange

### 基本属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `start` | Long | 范围的起始值（包含） |
| `endInclusive` | Long | 范围的结束值（包含） |
| `endExclusive` | Long | 范围的结束值（不包含） |
| `first` | Long | 范围的第一个元素 |
| `last` | Long | 范围的最后一个元素 |
| `step` | Long | 范围的步长 |

### 基本方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `contains(value: Long)` | Boolean | 检查值是否在范围内 |
| `isEmpty()` | Boolean | 检查范围是否为空 |
| `iterator()` | LongIterator | 获取范围的迭代器 |

### 用法示例

```kotlin
// 创建 LongRange
val range1 = 1L..100L          // [1L, 100L] 闭区间
val range2 = 1L until 100L      // [1L, 100L) 半开区间
val range3 = 100L downTo 1L      // [100L, 1L] 递减区间
val range4 = 1L..100L step 10L  // [1L, 11L, 21L, ..., 91L] 步长为10

// 访问属性
println(range1.start)        // 1
println(range1.endInclusive)  // 100
println(range1.first)         // 1
println(range1.last)          // 100
println(range1.step)          // 1

// 使用方法
println(range1.contains(50L))  // true
println(range1.contains(101L)) // false
println(range1.isEmpty())      // false

// 在循环中使用
for (i in 1L..100L) {
    println(i)  // 1L, 2L, 3L, ..., 100L
}

for (i in 1L until 100L) {
    println(i)  // 1L, 2L, 3L, ..., 99L
}
```

## CharRange

### 基本属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `start` | Char | 范围的起始值（包含） |
| `endInclusive` | Char | 范围的结束值（包含） |
| `endExclusive` | Char | 范围的结束值（不包含） |
| `first` | Char | 范围的第一个元素 |
| `last` | Char | 范围的最后一个元素 |
| `step` | Int | 范围的步长 |

### 基本方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `contains(value: Char)` | Boolean | 检查字符是否在范围内 |
| `isEmpty()` | Boolean | 检查范围是否为空 |
| `iterator()` | CharIterator | 获取范围的迭代器 |

### 用法示例

```kotlin
// 创建 CharRange
val range1 = 'a'..'z'        // ['a', 'z'] 小写字母
val range2 = 'A'..'Z'        // ['A', 'Z'] 大写字母
val range3 = '0'..'9'        // ['0', '9'] 数字字符
val range4 = 'a' until 'z'    // ['a', 'z') 不包含 'z'

// 访问属性
println(range1.start)        // a
println(range1.endInclusive)  // z
println(range1.first)         // a
println(range1.last)          // z
println(range1.step)          // 1

// 使用方法
println(range1.contains('m'))  // true
println(range1.contains('A'))  // false
println(range1.isEmpty())      // false

// 在循环中使用
for (c in 'a'..'z') {
    println(c)  // a, b, c, ..., z
}

// 检查字符类型
fun isLetter(c: Char): Boolean = c in 'a'..'z' || c in 'A'..'Z'
fun isDigit(c: Char): Boolean = c in '0'..'9'

println(isLetter('a'))  // true
println(isDigit('5'))   // true
```

## `ClosedRange<T>`

### 基本方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `contains(value: T)` | Boolean | 检查值是否在闭区间内 |
| `isEmpty()` | Boolean | 检查范围是否为空 |
| `start` | T | 范围的起始值 |
| `endInclusive` | T | 范围的结束值 |

### 用法示例

```kotlin
// 使用 ClosedRange 接口
val range: ClosedRange<Int> = 1..10

println(range.contains(5))   // true
println(range.contains(11))  // false
println(range.isEmpty())     // false
println(range.start)        // 1
println(range.endInclusive)  // 10

// 自定义 ClosedRange
data class MyDate(val day: Int, val month: Int, val year: Int) : Comparable<MyDate> {
    override fun compareTo(other: MyDate): Int {
        return when {
            year != other.year -> year - other.year
            month != other.month -> month - other.month
            else -> day - other.day
        }
    }
}

val dateRange: ClosedRange<MyDate> = MyDate(1, 1, 2024)..MyDate(31, 12, 2024)
val testDate = MyDate(15, 6, 2024)
println(testDate in dateRange)  // true
```

## `OpenEndRange<T>`

### 基本方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `contains(value: T)` | Boolean | 检查值是否在半开区间内 |
| `isEmpty()` | Boolean | 检查范围是否为空 |
| `start` | T | 范围的起始值 |
| `endExclusive` | T | 范围的结束值（不包含） |

### 用法示例

```kotlin
// 使用 OpenEndRange 接口
val range: OpenEndRange<Int> = 1 until 10

println(range.contains(9))   // true
println(range.contains(10))  // false
println(range.isEmpty())     // false
println(range.start)        // 1
println(range.endExclusive)  // 10

// 在循环中使用
for (i in 1 until 10) {
    println(i)  // 1, 2, 3, ..., 9
}
```

## `Progression<T>`

### 基本属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `start` | T | 进度的起始值 |
| `endInclusive` | T | 进度的结束值（包含） |
| `last` | T | 进度的最后一个元素 |
| `step` | Int | 进度的步长 |

### 基本方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `iterator()` | Iterator<T> | 获取进度的迭代器 |
| `isEmpty()` | Boolean | 检查进度是否为空 |
| `contains(value: T)` | Boolean | 检查值是否在进度中 |

### 用法示例

```kotlin
// 使用 Progression
val progression: IntProgression = 1..10 step 2

println(progression.start)        // 1
println(progression.endInclusive)  // 10
println(progression.last)          // 9
println(progression.step)          // 2

// 遍历进度
for (i in progression) {
    println(i)  // 1, 3, 5, 7, 9
}

// 递减进度
val descending: IntProgression = 10 downTo 1 step 2
for (i in descending) {
    println(i)  // 10, 8, 6, 4, 2
}
```

## Range 操作符

### 基本操作符

| 操作符 | 说明 | 示例 |
|--------|------|------|
| `..` | 创建闭区间 | `1..10` |
| `until` | 创建半开区间 | `1 until 10` |
| `downTo` | 创建递减区间 | `10 downTo 1` |
| `step` | 设置步长 | `1..10 step 2` |
| `in` | 检查包含 | `5 in 1..10` |
| `!in` | 检查不包含 | `15 !in 1..10` |

### 用法示例

```kotlin
// 创建区间
val closedRange = 1..10        // [1, 10]
val openRange = 1 until 10    // [1, 10)
val descendingRange = 10 downTo 1  // [10, 1]
val steppedRange = 1..10 step 2    // [1, 3, 5, 7, 9]

// 检查包含
println(5 in 1..10)       // true
println(15 in 1..10)      // false
println(15 !in 1..10)     // true

// 在 when 表达式中使用
val score = 85
val grade = when (score) {
    in 90..100 -> "A"
    in 80..89 -> "B"
    in 70..79 -> "C"
    in 60..69 -> "D"
    else -> "F"
}
println(grade)  // B

// 检查字符范围
val char = 'm'
val type = when (char) {
    in 'a'..'z' -> "小写字母"
    in 'A'..'Z' -> "大写字母"
    in '0'..'9' -> "数字"
    else -> "其他字符"
}
println(type)  // 小写字母
```

## 使用注意事项

### 1. 步长为零

```kotlin
// 错误：步长为零
val range = 1..10 step 0  // IllegalArgumentException: Step must be non-zero.

// 正确：步长必须非零
val range = 1..10 step 1  // 正确
val range = 1..10 step 2  // 正确
val range = 10 downTo 1 step 1  // 正确
```

### 2. 空范围

```kotlin
// 空范围示例
val empty1 = 5..1              // 空范围（递增但起始大于结束）
val empty2 = 1 downTo 5         // 空范围（递减但起始小于结束）
val empty3 = 1..10 step 100      // 空范围（步长过大）

println(empty1.isEmpty())  // true
println(empty2.isEmpty())  // true
println(empty3.isEmpty())  // true

// 处理空范围
for (i in 5..1) {
    println(i)  // 不会执行任何迭代
}
```

### 3. 浮点数范围

```kotlin
// Kotlin 标准库不支持浮点数范围
// val range = 1.0..10.0  // 编译错误

// 解决方案1：使用自定义函数
fun closedFloatingPointRange(start: Double, endInclusive: Double, step: Double): DoubleProgression {
    require(step > 0) { "Step must be positive, but was $step." }
    val count = ((endInclusive - start) / step).toInt() + 1
    return DoubleProgression.fromClosedRange(start, endInclusive, step)
}

// 解决方案2：使用第三方库或自定义实现
data class DoubleRange(val start: Double, val endInclusive: Double, val step: Double = 1.0) : Iterable<Double> {
    override fun iterator(): Iterator<Double> {
        return object : Iterator<Double> {
            var current = start
            override fun hasNext() = current <= endInclusive
            override fun next(): Double {
                val result = current
                current += step
                return result
            }
        }
    }
}

val doubleRange = DoubleRange(1.0, 10.0, 0.5)
for (d in doubleRange) {
    println(d)  // 1.0, 1.5, 2.0, ..., 10.0
}
```

### 4. 大范围性能

```kotlin
// 大范围可能导致性能问题
val hugeRange = 1..1_000_000_000

// 错误：遍历整个大范围
for (i in hugeRange) {
    // 这会非常慢
}

// 正确：使用更高效的方式
val count = hugeRange.count { it % 2 == 0 }  // 使用 count 而不是手动遍历

// 或者使用并行处理
val result = hugeRange.asSequence()
    .filter { it % 2 == 0 }
    .take(1000)  // 限制处理数量
    .toList()
```

### 5. 类型转换

```kotlin
// 不同类型的 Range 不能直接比较
val intRange = 1..10
val longRange = 1L..10L

// 错误：类型不匹配
// if (5L in intRange) { }  // 编译错误

// 正确：类型转换
if (5L in longRange) { }  // 正确
if (5.toInt() in intRange) { }  // 正确

// 使用泛型函数
fun <T : Comparable<T>> inRange(value: T, range: ClosedRange<T>): Boolean {
    return value in range
}

inRange(5L, longRange)  // 正确
```

### 6. 可变性

```kotlin
// Range 是不可变的
val range = 1..10
// range.start = 5  // 编译错误：val 不能重新赋值

// 如果需要可变范围，使用变量
var range = 1..10
range = 5..15  // 正确

// 或者使用自定义可变范围类
class MutableIntRange(var start: Int, var endInclusive: Int, var step: Int = 1) {
    fun toRange(): IntRange = IntProgression.fromClosedRange(start, endInclusive, step)
}

val mutableRange = MutableIntRange(1, 10)
mutableRange.start = 5
val range = mutableRange.toRange()
```

## 最佳实践

### 1. 选择合适的范围类型

```kotlin
// 使用 IntRange 进行整数操作
val intRange = 1..100

// 使用 LongRange 处理大数
val longRange = 1L..1_000_000_000L

// 使用 CharRange 处理字符
val charRange = 'a'..'z'

// 使用 until 避免边界错误
val array = arrayOf(1, 2, 3, 4, 5)
for (i in 0 until array.size) {  // 使用 until 而不是 ..
    println(array[i])
}
```

### 2. 合理使用步长

```kotlin
// 使用步长优化性能
val range = 1..1000 step 10  // 只处理需要的元素

// 递减范围
val descending = 100 downTo 1 step 5

// 负步长（不推荐，使用 downTo 更清晰）
val negativeStep = 100 downTo 1  // 比 100..1 step -1 更清晰
```

### 3. 在条件判断中使用范围

```kotlin
// 使用 in 操作符简化条件判断
val age = 25

// 传统方式
if (age >= 18 && age <= 30) {
    println("青年")
}

// Kotlin 方式
if (age in 18..30) {
    println("青年")
}

// 在 when 表达式中使用
val category = when (age) {
    in 0..12 -> "儿童"
    in 13..17 -> "青少年"
    in 18..59 -> "成年人"
    in 60..120 -> "老年人"
    else -> "无效年龄"
}
```

### 4. 避免常见陷阱

```kotlin
// 陷阱1：边界错误
val array = arrayOf(1, 2, 3)
// for (i in 0..array.size) { }  // 错误：会越界
for (i in 0 until array.size) { }  // 正确

// 陷阱2：空范围
val range = 10..1
// for (i in range) { }  // 不会执行任何迭代
if (!range.isEmpty()) {
    for (i in range) { }  // 先检查是否为空
}

// 陷阱3：浮点数精度
val range = 0.0..1.0 step 0.1  // 不支持
// 使用自定义实现或整数范围后转换
for (i in 0..10) {
    val value = i / 10.0
    println(value)  // 0.0, 0.1, 0.2, ..., 1.0
}
```

### 5. 性能优化

```kotlin
// 使用 count 而不是手动计数
val range = 1..1_000_000
val count = range.count { it % 2 == 0 }  // 高效

// 使用 first/last 快速访问
val range = 1..100
val first = range.first   // O(1)
val last = range.last     // O(1)

// 使用 contains 快速检查
val range = 1..100
val isInside = 50 in range  // O(1)

// 使用 asSequence 处理大范围
val range = 1..1_000_000
val result = range.asSequence()
    .filter { it % 2 == 0 }
    .map { it * it }
    .take(100)
    .toList()
```

## 总结

Kotlin Range 提供了强大而简洁的方式来处理数值和字符范围：

1. **丰富的类型**：IntRange、LongRange、CharRange 等支持不同数据类型
2. **灵活的操作符**：`..`、`until`、`downTo`、`step` 等提供直观的语法
3. **与语言集成**：与 for 循环、when 表达式等完美配合
4. **性能优化**：提供高效的 contains、count 等方法

**核心要点**：
- 选择合适的范围类型（IntRange、LongRange、CharRange）
- 注意步长为零和空范围的情况
- 在数组索引等场景优先使用 `until` 避免边界错误
- 合理使用步长优化性能
- 在条件判断中使用 `in` 操作符简化代码

通过掌握 Kotlin Range 的使用技巧，可以编写出更简洁、更高效的代码。