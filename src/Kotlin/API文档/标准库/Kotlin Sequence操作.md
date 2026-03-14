---
title: Kotlin Sequence API 完全指南
date: 2026-03-08
footer: Trae编辑
---


## 目录

1. [Sequence 类型介绍](#sequence-类型介绍)
2. [创建 Sequence](#创建-sequence)
3. [转换操作](#转换操作)
4. [过滤操作](#过滤操作)
5. [聚合操作](#聚合操作)
6. [查找操作](#查找操作)
7. [排序操作](#排序操作)
8. [分组操作](#分组操作)
9. [其他操作](#其他操作)
10. [Sequence vs List](#sequence-vs-list)
11. [性能优化](#性能优化)
12. [最佳实践](#最佳实践)

---

## Sequence 类型介绍

### 什么是 Sequence

`Sequence` 是 Kotlin 标准库中的一个接口，代表一个惰性求值的元素序列。与 `List` 不同，`Sequence` 不会立即计算所有元素，而是在需要时才计算。

### 核心特性

| 特性 | 描述 |
|------|------|
| **惰性求值** | 元素只在需要时才计算 |
| **懒加载** | 不会一次性加载所有元素到内存 |
| **链式优化** | 链式调用时只遍历一次 |
| **无索引访问** | 不支持随机访问（如 `get(index)`） |
| **可重用** | 可以多次遍历，但每次都会重新计算 |

### 与 List 的区别

| 特性 | List | Sequence |
|------|------|----------|
| 求值方式 | 立即求值 | 惰性求值 |
| 内存占用 | 一次性加载所有元素 | 按需加载 |
| 访问方式 | 支持索引访问 | 只支持顺序访问 |
| 适用场景 | 小集合、需要随机访问 | 大集合、链式操作 |
| 性能 | 简单操作更快 | 链式操作更高效 |

### Sequence 接口定义

```kotlin
interface Sequence<out T> {
    operator fun iterator(): Iterator<T>
}
```

### 基本使用

```kotlin
// 创建 Sequence
val sequence = sequenceOf(1, 2, 3, 4, 5)

// 遍历 Sequence
sequence.forEach { println(it) }
// 输出: 1 2 3 4 5

// 转换为 List
val list = sequence.toList()
println(list)  // 输出: [1, 2, 3, 4, 5]
```

---

## 创建 Sequence

### sequenceOf

从一组元素创建 Sequence。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
println(sequence.toList())  // 输出: [1, 2, 3, 4, 5]
```

### asSequence

将集合转换为 Sequence。

```kotlin
val list = listOf(1, 2, 3, 4, 5)
val sequence = list.asSequence()
println(sequence.toList())  // 输出: [1, 2, 3, 4, 5]
```

### generateSequence

使用生成器函数创建无限 Sequence。

```kotlin
val numbers = generateSequence(1) { it + 1 }
val result = numbers.take(5).toList()
println(result)  // 输出: [1, 2, 3, 4, 5]
```

### sequence

使用 lambda 创建 Sequence。

```kotlin
val sequence = sequence {
    yield(1)
    yield(2)
    yield(3)
    yieldAll(listOf(4, 5))
}

println(sequence.toList())  // 输出: [1, 2, 3, 4, 5]
```

### iterator().asSequence()

从迭代器创建 Sequence。

```kotlin
val iterator = listOf(1, 2, 3, 4, 5).iterator()
val sequence = iterator.asSequence()
println(sequence.toList())  // 输出: [1, 2, 3, 4, 5]
```

### emptySequence

创建空 Sequence。

```kotlin
val empty = emptySequence<Int>()
println(empty.toList())  // 输出: []
```

### 从范围创建

```kotlin
val range = (1..10).asSequence()
println(range.toList())  // 输出: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

---

## 转换操作

### map

对每个元素应用转换函数。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.map { it * 2 }
println(result.toList())  // 输出: [2, 4, 6, 8, 10]
```

### mapIndexed

带索引的 map 操作。

```kotlin
val sequence = sequenceOf(10, 20, 30, 40, 50)
val result = sequence.mapIndexed { index, value ->
    "Index $index: $value"
}
println(result.toList())
// 输出: [Index 0: 10, Index 1: 20, Index 2: 30, Index 3: 40, Index 4: 50]
```

### mapNotNull

过滤掉 null 值的 map 操作。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.mapNotNull {
    if (it % 2 == 0) it * 2 else null
}
println(result.toList())  // 输出: [4, 8]
```

### flatMap

将每个元素转换为 Sequence，然后扁平化。

```kotlin
val sequence = sequenceOf(listOf(1, 2), listOf(3, 4), listOf(5, 6))
val result = sequence.flatMap { it.asSequence() }
println(result.toList())  // 输出: [1, 2, 3, 4, 5, 6]
```

### flatten

扁平化嵌套的 Sequence。

```kotlin
val sequence = sequenceOf(
    sequenceOf(1, 2),
    sequenceOf(3, 4),
    sequenceOf(5, 6)
).flatten()

println(sequence.toList())  // 输出: [1, 2, 3, 4, 5, 6]
```

### distinct

返回去重后的 Sequence。

```kotlin
val sequence = sequenceOf(1, 2, 2, 3, 3, 3, 4)
val result = sequence.distinct()
println(result.toList())  // 输出: [1, 2, 3, 4]
```

### distinctBy

根据指定键去重。

```kotlin
data class Person(val name: String, val age: Int)

val sequence = sequenceOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Alice", 30)
)

val result = sequence.distinctBy { it.name }
println(result.toList())  // 输出: [Person(name=Alice, age=25), Person(name=Bob, age=30)]
```

### sorted

返回排序后的 Sequence。

```kotlin
val sequence = sequenceOf(5, 2, 8, 1, 9, 3)
val result = sequence.sorted()
println(result.toList())  // 输出: [1, 2, 3, 5, 8, 9]
```

### sortedDescending

返回降序排序后的 Sequence。

```kotlin
val sequence = sequenceOf(5, 2, 8, 1, 9, 3)
val result = sequence.sortedDescending()
println(result.toList())  // 输出: [9, 8, 5, 3, 2, 1]
```

### sortedBy

根据指定键排序。

```kotlin
data class Person(val name: String, val age: Int)

val sequence = sequenceOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = sequence.sortedBy { it.age }
println(result.toList())
// 输出: [Person(name=Charlie, age=20), Person(name=Alice, age=25), Person(name=Bob, age=30)]
```

### sortedByDescending

根据指定键降序排序。

```kotlin
data class Person(val name: String, val age: Int)

val sequence = sequenceOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = sequence.sortedByDescending { it.age }
println(result.toList())
// 输出: [Person(name=Bob, age=30), Person(name=Alice, age=25), Person(name=Charlie, age=20)]
```

### sortedWith

使用自定义比较器排序。

```kotlin
data class Person(val name: String, val age: Int)

val sequence = sequenceOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = sequence.sortedWith(compareBy({ it.age }, { it.name }))
println(result.toList())
// 输出: [Person(name=Charlie, age=20), Person(name=Alice, age=25), Person(name=Bob, age=30)]
```

### reversed

返回反转后的 Sequence。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.reversed()
println(result.toList())  // 输出: [5, 4, 3, 2, 1]
```

### zip

将两个 Sequence 组合成键值对。

```kotlin
val sequence1 = sequenceOf(1, 2, 3)
val sequence2 = sequenceOf("a", "b", "c")

val result = sequence1.zip(sequence2)
println(result.toList())  // 输出: [(1, a), (2, b), (3, c)]
```

### zipWithNext

将相邻元素组合。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.zipWithNext()
println(result.toList())  // 输出: [(1, 2), (2, 3), (3, 4), (4, 5)]
```

### chunked

将 Sequence 分成指定大小的块。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val result = sequence.chunked(3)
println(result.toList())  // 输出: [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]
```

### windowed

创建滑动窗口。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.windowed(3)
println(result.toList())  // 输出: [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
```

---

## 过滤操作

### filter

保留满足条件的元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val result = sequence.filter { it % 2 == 0 }
println(result.toList())  // 输出: [2, 4, 6, 8, 10]
```

### filterNot

保留不满足条件的元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val result = sequence.filterNot { it % 2 == 0 }
println(result.toList())  // 输出: [1, 3, 5, 7, 9]
```

### filterNotNull

过滤掉 null 值。

```kotlin
val sequence = sequenceOf(1, null, 2, null, 3, null, 4)
val result = sequence.filterNotNull()
println(result.toList())  // 输出: [1, 2, 3, 4]
```

### filterIndexed

带索引的 filter 操作。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val result = sequence.filterIndexed { index, value ->
    index % 2 == 0 && value % 2 == 0
}
println(result.toList())  // 输出: [2, 6, 10]
```

### filterIsInstance

过滤指定类型的元素。

```kotlin
val sequence = sequenceOf(1, "hello", 2.5, "world", 3, true)
val strings = sequence.filterIsInstance<String>()
println(strings.toList())  // 输出: [hello, world]

val numbers = sequence.filterIsInstance<Int>()
println(numbers.toList())  // 输出: [1, 3]
```

### take

取前 n 个元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.take(3)
println(result.toList())  // 输出: [1, 2, 3]
```

### takeLast

取后 n 个元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.takeLast(2)
println(result.toList())  // 输出: [4, 5]
```

### takeWhile

取满足条件的开头元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val result = sequence.takeWhile { it < 5 }
println(result.toList())  // 输出: [1, 2, 3, 4]
```

### takeLastWhile

取满足条件的末尾元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val result = sequence.takeLastWhile { it > 5 }
println(result.toList())  // 输出: [6, 7, 8, 9, 10]
```

### drop

删除前 n 个元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.drop(2)
println(result.toList())  // 输出: [3, 4, 5]
```

### dropLast

删除后 n 个元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.dropLast(2)
println(result.toList())  // 输出: [1, 2, 3]
```

### dropWhile

删除满足条件的开头元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val result = sequence.dropWhile { it < 5 }
println(result.toList())  // 输出: [5, 6, 7, 8, 9, 10]
```

### dropLastWhile

删除满足条件的末尾元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val result = sequence.dropLastWhile { it > 5 }
println(result.toList())  // 输出: [1, 2, 3, 4, 5]
```

---

## 聚合操作

### reduce

从第一个元素开始，依次将元素累积。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val sum = sequence.reduce { acc, num -> acc + num }
println(sum)  // 输出: 15
```

### reduceIndexed

带索引的 reduce 操作。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.reduceIndexed { index, acc, num ->
    acc + num * index
}
println(result)  // 输出: 40
```

### fold

从初始值开始，依次将元素累积。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val sum = sequence.fold(0) { acc, num -> acc + num }
println(sum)  // 输出: 15
```

### foldIndexed

带索引的 fold 操作。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.foldIndexed(0) { index, acc, num ->
    acc + num * index
}
println(result)  // 输出: 40
```

### count

返回元素数量或满足条件的元素数量。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val totalCount = sequence.count()
println(totalCount)  // 输出: 10

val evenCount = sequence.count { it % 2 == 0 }
println(evenCount)  // 输出: 5
```

### sum

返回所有元素的和。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val sum = sequence.sum()
println(sum)  // 输出: 15
```

### sumOf

根据指定选择器计算和。

```kotlin
data class Item(val price: Double, val quantity: Int)

val sequence = sequenceOf(
    Item(10.0, 2),
    Item(20.0, 3),
    Item(30.0, 1)
)

val result = sequence.sumOf { it.price * it.quantity }
println(result)  // 输出: 110.0
```

### average

返回所有元素的平均值。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val avg = sequence.average()
println(avg)  // 输出: 3.0
```

### min

返回最小元素。

```kotlin
val sequence = sequenceOf(5, 2, 8, 1, 9, 3)
val min = sequence.min()
println(min)  // 输出: 1
```

### max

返回最大元素。

```kotlin
val sequence = sequenceOf(5, 2, 8, 1, 9, 3)
val max = sequence.max()
println(max)  // 输出: 9
```

### minOrNull

返回最小元素，如果为空则返回 null。

```kotlin
val sequence = sequenceOf(5, 2, 8, 1, 9, 3)
val result1 = sequence.minOrNull()
println(result1)  // 输出: 1

val empty = emptySequence<Int>()
val result2 = empty.minOrNull()
println(result2)  // 输出: null
```

### maxOrNull

返回最大元素，如果为空则返回 null。

```kotlin
val sequence = sequenceOf(5, 2, 8, 1, 9, 3)
val result1 = sequence.maxOrNull()
println(result1)  // 输出: 9

val empty = emptySequence<Int>()
val result2 = empty.maxOrNull()
println(result2)  // 输出: null
```

### minOf

根据指定选择器返回最小值。

```kotlin
data class Person(val name: String, val age: Int)

val sequence = sequenceOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = sequence.minOf { it.age }
println(result)  // 输出: 20
```

### maxOf

根据指定选择器返回最大值。

```kotlin
data class Person(val name: String, val age: Int)

val sequence = sequenceOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = sequence.maxOf { it.age }
println(result)  // 输出: 30
```

### minBy

根据指定键返回最小元素。

```kotlin
data class Person(val name: String, val age: Int)

val sequence = sequenceOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = sequence.minBy { it.age }
println(result)  // 输出: Person(name=Charlie, age=20)
```

### maxBy

根据指定键返回最大元素。

```kotlin
data class Person(val name: String, val age: Int)

val sequence = sequenceOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = sequence.maxBy { it.age }
println(result)  // 输出: Person(name=Bob, age=30)
```

### joinToString

将元素连接为字符串。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.joinToString()
println(result)  // 输出: 1, 2, 3, 4, 5

val result2 = sequence.joinToString(separator = " | ", prefix = "[", postfix = "]")
println(result2)  // 输出: [1 | 2 | 3 | 4 | 5]
```

### joinTo

将元素连接并添加到 StringBuilder。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val sb = StringBuilder()
sequence.joinTo(sb, ", ")
println(sb.toString())  // 输出: 1, 2, 3, 4, 5
```

---

## 查找操作

### find

返回第一个满足条件的元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.find { it > 3 }
println(result)  // 输出: 4
```

### findLast

返回最后一个满足条件的元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.findLast { it < 5 }
println(result)  // 输出: 4
```

### first

返回第一个元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.first()
println(result)  // 输出: 1
```

### firstOrNull

返回第一个元素，如果为空则返回 null。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result1 = sequence.firstOrNull()
println(result1)  // 输出: 1

val empty = emptySequence<Int>()
val result2 = empty.firstOrNull()
println(result2)  // 输出: null
```

### first { predicate }

返回第一个满足条件的元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.first { it > 3 }
println(result)  // 输出: 4
```

### firstOrNull { predicate }

返回第一个满足条件的元素，如果没有则返回 null。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result1 = sequence.firstOrNull { it > 3 }
println(result1)  // 输出: 4

val result2 = sequence.firstOrNull { it > 10 }
println(result2)  // 输出: null
```

### last

返回最后一个元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.last()
println(result)  // 输出: 5
```

### lastOrNull

返回最后一个元素，如果为空则返回 null。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result1 = sequence.lastOrNull()
println(result1)  // 输出: 5

val empty = emptySequence<Int>()
val result2 = empty.lastOrNull()
println(result2)  // 输出: null
```

### last { predicate }

返回最后一个满足条件的元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.last { it < 5 }
println(result)  // 输出: 4
```

### lastOrNull { predicate }

返回最后一个满足条件的元素，如果没有则返回 null。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result1 = sequence.lastOrNull { it < 5 }
println(result1)  // 输出: 4

val result2 = sequence.lastOrNull { it < 0 }
println(result2)  // 输出: null
```

### indexOf

返回指定元素的第一个索引。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.indexOf(3)
println(result)  // 输出: 2
```

### indexOfFirst

返回第一个满足条件的元素索引。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.indexOfFirst { it > 3 }
println(result)  // 输出: 3
```

### indexOfLast

返回最后一个满足条件的元素索引。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.indexOfLast { it < 5 }
println(result)  // 输出: 3
```

### elementAt

返回指定索引的元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.elementAt(2)
println(result)  // 输出: 3
```

### elementAtOrNull

返回指定索引的元素，如果越界则返回 null。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result1 = sequence.elementAtOrNull(2)
println(result1)  // 输出: 3

val result2 = sequence.elementAtOrNull(10)
println(result2)  // 输出: null
```

### elementAtOrElse

返回指定索引的元素，如果越界则返回默认值。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result1 = sequence.elementAtOrElse(2) { -1 }
println(result1)  // 输出: 3

val result2 = sequence.elementAtOrElse(10) { -1 }
println(result2)  // 输出: -1
```

### single

返回唯一元素，如果不止一个则抛出异常。

```kotlin
val sequence = sequenceOf(42)
val result = sequence.single()
println(result)  // 输出: 42
```

### singleOrNull

返回唯一元素，如果为空或不止一个则返回 null。

```kotlin
val sequence1 = sequenceOf(42)
val result1 = sequence1.singleOrNull()
println(result1)  // 输出: 42

val sequence2 = emptySequence<Int>()
val result2 = sequence2.singleOrNull()
println(result2)  // 输出: null
```

### single { predicate }

返回唯一满足条件的元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.single { it == 3 }
println(result)  // 输出: 3
```

### singleOrNull { predicate }

返回唯一满足条件的元素，如果没有或不止一个则返回 null。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result1 = sequence.singleOrNull { it == 3 }
println(result1)  // 输出: 3

val result2 = sequence.singleOrNull { it > 10 }
println(result2)  // 输出: null
```

---

## 排序操作

### sorted

返回排序后的 Sequence。

```kotlin
val sequence = sequenceOf(5, 2, 8, 1, 9, 3)
val result = sequence.sorted()
println(result.toList())  // 输出: [1, 2, 3, 5, 8, 9]
```

### sortedDescending

返回降序排序后的 Sequence。

```kotlin
val sequence = sequenceOf(5, 2, 8, 1, 9, 3)
val result = sequence.sortedDescending()
println(result.toList())  // 输出: [9, 8, 5, 3, 2, 1]
```

### sortedBy

根据指定键排序。

```kotlin
data class Person(val name: String, val age: Int)

val sequence = sequenceOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = sequence.sortedBy { it.age }
println(result.toList())
// 输出: [Person(name=Charlie, age=20), Person(name=Alice, age=25), Person(name=Bob, age=30)]
```

### sortedByDescending

根据指定键降序排序。

```kotlin
data class Person(val name: String, val age: Int)

val sequence = sequenceOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = sequence.sortedByDescending { it.age }
println(result.toList())
// 输出: [Person(name=Bob, age=30), Person(name=Alice, age=25), Person(name=Charlie, age=20)]
```

### sortedWith

使用自定义比较器排序。

```kotlin
data class Person(val name: String, val age: Int)

val sequence = sequenceOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = sequence.sortedWith(compareBy({ it.age }, { it.name }))
println(result.toList())
// 输出: [Person(name=Charlie, age=20), Person(name=Alice, age=25), Person(name=Bob, age=30)]
```

---

## 分组操作

### groupBy

根据指定键分组。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val grouped = sequence.groupBy { it % 2 }
println(grouped)
// 输出: {0=[2, 4, 6, 8, 10], 1=[1, 3, 5, 7, 9]}
```

### groupBy with value transform

分组并转换值。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val grouped = sequence.groupBy(
    keySelector = { it % 2 },
    valueTransform = { it * it }
)

println(grouped)
// 输出: {0=[4, 16, 36, 64, 100], 1=[1, 9, 25, 49, 81]}
```

### associateBy

根据指定键创建 Map。

```kotlin
data class Person(val id: Int, val name: String)

val sequence = sequenceOf(
    Person(1, "Alice"),
    Person(2, "Bob"),
    Person(3, "Charlie")
)

val map = sequence.associateBy { it.id }
println(map)
// 输出: {1=Person(id=1, name=Alice), 2=Person(id=2, name=Bob), 3=Person(id=3, name=Charlie)}
```

### associateBy with value transform

根据指定键创建 Map，并转换值。

```kotlin
data class Person(val id: Int, val name: String)

val sequence = sequenceOf(
    Person(1, "Alice"),
    Person(2, "Bob"),
    Person(3, "Charlie")
)

val map = sequence.associateBy({ it.id }, { it.name })
println(map)  // 输出: {1=Alice, 2=Bob, 3=Charlie}
```

### associate

将元素转换为键值对。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val map = sequence.associate { it to it * it }
println(map)  // 输出: {1=1, 2=4, 3=9, 4=16, 5=25}
```

### associateWith

使用元素作为键，指定值。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val map = sequence.associateWith { it * it }
println(map)  // 输出: {1=1, 2=4, 3=9, 4=16, 5=25}
```

### partition

根据条件将 Sequence 分成两个。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val (even, odd) = sequence.partition { it % 2 == 0 }
println(even.toList())  // 输出: [2, 4, 6, 8, 10]
println(odd.toList())   // 输出: [1, 3, 5, 7, 9]
```

---

## 其他操作

### forEach

对每个元素执行操作。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
sequence.forEach { println(it) }
// 输出:
// 1
// 2
// 3
// 4
// 5
```

### forEachIndexed

带索引的 forEach 操作。

```kotlin
val sequence = sequenceOf("apple", "banana", "cherry")
sequence.forEachIndexed { index, value ->
    println("$index: $value")
}
// 输出:
// 0: apple
// 1: banana
// 2: cherry
```

### onEach

对每个元素执行操作，并返回原 Sequence。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.onEach { println("Processing: $it") }
println(result.toList())
// 输出:
// Processing: 1
// Processing: 2
// Processing: 3
// Processing: 4
// Processing: 5
// [1, 2, 3, 4, 5]
```

### onEachIndexed

带索引的 onEach 操作。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence.onEachIndexed { index, value ->
    println("Index $index: $value")
}
println(result.toList())
```

### any

检查是否有任意元素满足条件。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result1 = sequence.any { it > 3 }
println(result1)  // 输出: true

val result2 = sequence.any { it > 10 }
println(result2)  // 输出: false
```

### all

检查是否所有元素都满足条件。

```kotlin
val sequence = sequenceOf(2, 4, 6, 8, 10)
val result1 = sequence.all { it % 2 == 0 }
println(result1)  // 输出: true

val result2 = sequence.all { it > 5 }
println(result2)  // 输出: false
```

### none

检查是否没有元素满足条件。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result1 = sequence.none { it > 10 }
println(result1)  // 输出: true

val result2 = sequence.none { it > 3 }
println(result2)  // 输出: false
```

### contains

检查是否包含指定元素。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result1 = sequence.contains(3)
println(result1)  // 输出: true

val result2 = sequence.contains(10)
println(result2)  // 输出: false
```

### requireNoNulls

确保 Sequence 中没有 null 值。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
sequence.requireNoNulls()  // 正常执行

val sequenceWithNull = sequenceOf(1, null, 2, 3)
sequenceWithNull.requireNoNulls()  // 抛出 IllegalArgumentException
```

### toList

转换为 List。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val list = sequence.toList()
println(list)  // 输出: [1, 2, 3, 4, 5]
```

### toMutableList

转换为 MutableList。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val list = sequence.toMutableList()
list.add(6)
println(list)  // 输出: [1, 2, 3, 4, 5, 6]
```

### toSet

转换为 Set。

```kotlin
val sequence = sequenceOf(1, 2, 2, 3, 3, 3, 4)
val set = sequence.toSet()
println(set)  // 输出: [1, 2, 3, 4]
```

### toMutableSet

转换为 MutableSet。

```kotlin
val sequence = sequenceOf(1, 2, 2, 3, 3, 3, 4)
val set = sequence.toMutableSet()
set.add(5)
println(set)  // 输出: [1, 2, 3, 4, 5]
```

### toMap

转换为 Map（适用于 Pair Sequence）。

```kotlin
val sequence = sequenceOf(1 to "a", 2 to "b", 3 to "c")
val map = sequence.toMap()
println(map)  // 输出: {1=a, 2=b, 3=c}
```

### toMutableMap

转换为 MutableMap。

```kotlin
val sequence = sequenceOf(1 to "a", 2 to "b", 3 to "c")
val map = sequence.toMutableMap()
map[4] = "d"
println(map)  // 输出: {1=a, 2=b, 3=c, 4=d}
```

### toCollection

添加到指定的集合。

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val list = mutableListOf<Int>()
sequence.toCollection(list)
println(list)  // 输出: [1, 2, 3, 4, 5]
```

### toHashSet

转换为 HashSet。

```kotlin
val sequence = sequenceOf(1, 2, 2, 3, 3, 3, 4)
val set = sequence.toHashSet()
println(set)  // 输出: [1, 2, 3, 4]
```

### toSortedSet

转换为 SortedSet。

```kotlin
val sequence = sequenceOf(5, 2, 8, 1, 9, 3)
val set = sequence.toSortedSet()
println(set)  // 输出: [1, 2, 3, 5, 8, 9]
```

---

## Sequence vs List

### 性能对比

#### List 链式调用

```kotlin
val list = (1..1000000).toList()

val result = list
    .filter { it % 2 == 0 }
    .map { it * it }
    .take(10)
    .toList()
```

**执行过程**：
1. `filter` 创建新的 List（50 万个元素）
2. `map` 创建新的 List（50 万个元素）
3. `take` 创建新的 List（10 个元素）
4. 总共遍历 3 次，创建 3 个中间集合

#### Sequence 链式调用

```kotlin
val sequence = (1..1000000).asSequence()

val result = sequence
    .filter { it % 2 == 0 }
    .map { it * it }
    .take(10)
    .toList()
```

**执行过程**：
1. 只遍历 1 次
2. 不创建中间集合
3. 只计算需要的 10 个元素

### 性能测试

```kotlin
import kotlin.system.measureTimeMillis

// List 版本
val listTime = measureTimeMillis {
    val list = (1..1000000).toList()
    val result = list
        .filter { it % 2 == 0 }
        .map { it * it }
        .take(10)
        .toList()
}
println("List: ${listTime}ms")

// Sequence 版本
val sequenceTime = measureTimeMillis {
    val sequence = (1..1000000).asSequence()
    val result = sequence
        .filter { it % 2 == 0 }
        .map { it * it }
        .take(10)
        .toList()
}
println("Sequence: ${sequenceTime}ms")
```

**结果**：Sequence 版本通常比 List 版本快 2-10 倍（取决于操作复杂度）。

### 适用场景

| 场景 | 推荐使用 | 原因 |
|------|----------|------|
| 大集合（>1000 元素） | Sequence | 避免创建中间集合 |
| 多个链式操作 | Sequence | 只遍历一次 |
| 需要提前终止 | Sequence | 惰性求值，可以提前终止 |
| 小集合（<100 元素） | List | 开销较小，简单操作更快 |
| 需要随机访问 | List | Sequence 不支持索引访问 |
| 需要多次遍历 | List | Sequence 每次都重新计算 |

---

## 性能优化

### 1. 使用 Sequence 处理大集合

```kotlin
// 不推荐：List 创建多个中间集合
val result = largeList
    .filter { it > 0 }
    .map { it * 2 }
    .sorted()
    .take(100)

// 推荐：Sequence 只遍历一次
val result = largeList
    .asSequence()
    .filter { it > 0 }
    .map { it * 2 }
    .sorted()
    .take(100)
    .toList()
```

### 2. 使用 take 提前终止

```kotlin
// 查找前 10 个满足条件的元素
val result = largeSequence
    .filter { it % 2 == 0 }
    .take(10)
    .toList()
```

### 3. 避免不必要的 toList()

```kotlin
// 不推荐：过早转换为 List
val result = largeSequence
    .filter { it > 0 }
    .toList()
    .map { it * 2 }
    .toList()

// 推荐：保持 Sequence 直到需要
val result = largeSequence
    .filter { it > 0 }
    .map { it * 2 }
    .toList()
```

### 4. 使用 distinctBy 代替 distinct

```kotlin
// 不推荐：distinct 需要遍历整个 Sequence
val result = sequence.distinct()

// 推荐：distinctBy 可以提前终止
data class Item(val id: Int, val name: String)
val result = sequence.distinctBy { it.id }
```

### 5. 使用 groupBy 代替多次 filter

```kotlin
// 不推荐：多次 filter
val even = sequence.filter { it % 2 == 0 }
val odd = sequence.filter { it % 2 != 0 }

// 推荐：一次遍历分组
val (even, odd) = sequence.partition { it % 2 == 0 }
```

---

## 最佳实践

### 1. 选择合适的集合类型

```kotlin
// 小集合：使用 List
val smallList = listOf(1, 2, 3, 4, 5)
val result = smallList.filter { it % 2 == 0 }.map { it * 2 }

// 大集合：使用 Sequence
val largeSequence = (1..1000000).asSequence()
val result = largeSequence.filter { it % 2 == 0 }.map { it * 2 }.take(10).toList()
```

### 2. 合理使用链式调用

```kotlin
// 推荐：保持 Sequence 直到需要结果
val result = largeSequence
    .filter { it > 0 }
    .map { it * 2 }
    .sorted()
    .take(10)
    .toList()

// 不推荐：中间转换为 List
val result = largeSequence
    .filter { it > 0 }
    .toList()
    .map { it * 2 }
    .toList()
```

### 3. 使用 take 提前终止

```kotlin
// 查找前 10 个满足条件的元素
val result = largeSequence
    .filter { it % 2 == 0 }
    .take(10)
    .toList()
```

### 4. 使用 distinctBy 优化去重

```kotlin
data class Item(val id: Int, val name: String)

val sequence = sequenceOf(
    Item(1, "A"),
    Item(2, "B"),
    Item(1, "C"),
    Item(3, "D")
)

val result = sequence.distinctBy { it.id }
println(result.toList())  // 输出: [Item(id=1, name=A), Item(id=2, name=B), Item(id=3, name=D)]
```

### 5. 使用 groupBy 优化分组

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val grouped = sequence.groupBy { it % 2 }
println(grouped)
// 输出: {0=[2, 4, 6, 8, 10], 1=[1, 3, 5, 7, 9]}
```

### 6. 避免重复遍历

```kotlin
// 不推荐：多次遍历
val sequence = sequenceOf(1, 2, 3, 4, 5)
val sum = sequence.sum()
val avg = sequence.average()
val max = sequence.max()

// 推荐：一次遍历计算多个值
val (sum, count) = sequence.fold(0 to 0) { (s, c), value -> (s + value) to (c + 1) }
val avg = sum.toDouble() / count
```

### 7. 使用 onEach 进行副作用

```kotlin
val sequence = sequenceOf(1, 2, 3, 4, 5)
val result = sequence
    .onEach { println("Processing: $it") }
    .map { it * 2 }
    .toList()
```

### 8. 合理使用缓存

```kotlin
// 如果需要多次遍历，转换为 List
val sequence = (1..1000000).asSequence()
val cachedList = sequence.filter { it % 2 == 0 }.toList()

// 多次使用缓存的结果
val sum = cachedList.sum()
val avg = cachedList.average()
```

---

## 注意事项

1. **惰性求值**：Sequence 的元素只在需要时才计算
2. **无索引访问**：不支持 `get(index)` 操作
3. **可重用**：可以多次遍历，但每次都重新计算
4. **状态管理**：Sequence 的状态在遍历时可能改变
5. **性能权衡**：小集合使用 List，大集合使用 Sequence
6. **转换时机**：只在需要结果时才转换为 List

---

## 相关资源

- [Kotlin 官方文档 - Sequences](https://kotlinlang.org/docs/sequences.html)
- [Kotlin 标准库 - Sequence](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.sequences/-sequence/)
- [Kotlin 标准库 - Sequence Scope](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.sequences/index.html)
