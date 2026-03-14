---
title: Kotlin List Lambda 函数大全
date: 2026-03-08
footer: Trae编辑
---


## 目录

1. [概述](#概述)
2. [map 系列函数](#map-系列函数)
3. [filter 系列函数](#filter-系列函数)
4. [flatMap 系列函数](#flatmap-系列函数)
5. [reduce 系列函数](#reduce-系列函数)
6. [fold 系列函数](#fold-系列函数)
7. [forEach 系列函数](#foreach-系列函数)
8. [find 系列函数](#find-系列函数)
9. [sort 系列函数](#sort-系列函数)
10. [groupBy 系列函数](#groupby-系列函数)
11. [partition 系列函数](#partition-系列函数)
12. [zip 系列函数](#zip-系列函数)
13. [其他常用函数](#其他常用函数)
14. [链式调用](#链式调用)
15. [性能优化](#性能优化)
16. [最佳实践](#最佳实践)

---

## 概述

Kotlin 的 List 提供了丰富的 Lambda 函数（高阶函数），使得集合操作更加简洁和函数式。这些函数接受 Lambda 表达式作为参数，对集合中的每个元素进行处理。

### 主要特点

- **函数式编程**：支持函数式编程范式
- **链式调用**：支持链式调用，代码更简洁
- **不可变性**：大多数函数返回新的集合，不修改原集合
- **类型安全**：编译时类型检查
- **懒加载**：部分函数支持序列（Sequence）的懒加载

### 函数分类

| 分类 | 函数 | 说明 |
|------|------|------|
| 转换 | map, mapNotNull, mapIndexed | 转换元素 |
| 过滤 | filter, filterNot, filterNotNull | 过滤元素 |
| 扁平化 | flatMap, flatten | 扁平化嵌套结构 |
| 聚合 | reduce, fold, count | 聚合操作 |
| 遍历 | forEach, forEachIndexed | 遍历元素 |
| 查找 | find, findLast, firstOrNull | 查找元素 |
| 排序 | sortedBy, sortedWith | 排序 |
| 分组 | groupBy, associateBy | 分组和关联 |
| 分区 | partition | 分区 |
| 组合 | zip, zipWithNext | 组合元素 |

---

## map 系列函数

### map

对集合中的每个元素应用指定的转换函数，返回新的列表。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val squares = numbers.map { it * it }
println(squares)  // 输出: [1, 4, 9, 16, 25]

val doubled = numbers.map { it * 2 }
println(doubled)  // 输出: [2, 4, 6, 8, 10]
```

### mapIndexed

带索引的 map 函数，Lambda 接收索引和元素。

```kotlin
val numbers = listOf(10, 20, 30, 40, 50)

val result = numbers.mapIndexed { index, value ->
    "Index $index: $value"
}

println(result)
// 输出: [Index 0: 10, Index 1: 20, Index 2: 30, Index 3: 40, Index 4: 50]
```

### mapNotNull

过滤掉 null 值的 map 函数。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.mapNotNull {
    if (it % 2 == 0) it * 2 else null
}

println(result)  // 输出: [4, 8]
```

### mapIndexedNotNull

带索引且过滤 null 值的 map 函数。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.mapIndexedNotNull { index, value ->
    if (index % 2 == 0) value * 2 else null
}

println(result)  // 输出: [2, 6, 10]
```

### mapKeys

对 Map 的键进行转换。

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3)

val result = map.mapKeys { it.key.uppercase() }
println(result)  // 输出: {A=1, B=2, C=3}
```

### mapValues

对 Map 的值进行转换。

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3)

val result = map.mapValues { it.value * 10 }
println(result)  // 输出: {a=10, b=20, c=30}
```

---

## filter 系列函数

### filter

保留满足条件的元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val evenNumbers = numbers.filter { it % 2 == 0 }
println(evenNumbers)  // 输出: [2, 4, 6, 8, 10]

val oddNumbers = numbers.filter { it % 2 != 0 }
println(oddNumbers)  // 输出: [1, 3, 5, 7, 9]
```

### filterNot

保留不满足条件的元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val notEven = numbers.filterNot { it % 2 == 0 }
println(notEven)  // 输出: [1, 3, 5, 7, 9]
```

### filterNotNull

过滤掉 null 值。

```kotlin
val list = listOf(1, null, 2, null, 3, null, 4)

val result = list.filterNotNull()
println(result)  // 输出: [1, 2, 3, 4]
```

### filterIndexed

带索引的 filter 函数。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.filterIndexed { index, value ->
    index % 2 == 0 && value % 2 == 0
}

println(result)  // 输出: [2, 6, 10]
```

### filterIsInstance

过滤指定类型的元素。

```kotlin
val list = listOf(1, "hello", 2.5, "world", 3, true)

val strings = list.filterIsInstance<String>()
println(strings)  // 输出: [hello, world]

val numbers = list.filterIsInstance<Int>()
println(numbers)  // 输出: [1, 3]
```

### takeIf

如果条件满足则返回自身，否则返回 null。

```kotlin
val number = 5

val result = number.takeIf { it > 0 }
println(result)  // 输出: 5

val result2 = number.takeIf { it < 0 }
println(result2)  // 输出: null
```

### takeUnless

如果条件不满足则返回自身，否则返回 null。

```kotlin
val number = 5

val result = number.takeUnless { it < 0 }
println(result)  // 输出: 5

val result2 = number.takeUnless { it > 0 }
println(result2)  // 输出: null
```

---

## flatMap 系列函数

### flatMap

将每个元素转换为集合，然后扁平化为一个集合。

```kotlin
val lists = listOf(listOf(1, 2), listOf(3, 4), listOf(5, 6))

val flattened = lists.flatMap { it }
println(flattened)  // 输出: [1, 2, 3, 4, 5, 6]
```

### flatMapIndexed

带索引的 flatMap 函数。

```kotlin
val lists = listOf(listOf(1, 2), listOf(3, 4), listOf(5, 6))

val result = lists.flatMapIndexed { index, list ->
    list.map { it * (index + 1) }
}

println(result)  // 输出: [1, 2, 6, 8, 15, 18]
```

### flatMapTo

将结果添加到指定的可变集合。

```kotlin
val lists = listOf(listOf(1, 2), listOf(3, 4), listOf(5, 6))
val result = mutableListOf<Int>()

lists.flatMapTo(result) { it }
println(result)  // 输出: [1, 2, 3, 4, 5, 6]
```

### flatten

扁平化嵌套的集合。

```kotlin
val nested = listOf(listOf(1, 2), listOf(3, 4), listOf(5, 6))

val flattened = nested.flatten()
println(flattened)  // 输出: [1, 2, 3, 4, 5, 6]
```

---

## reduce 系列函数

### reduce

从第一个元素开始，依次将元素累积。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val sum = numbers.reduce { acc, num -> acc + num }
println(sum)  // 输出: 15

val product = numbers.reduce { acc, num -> acc * num }
println(product)  // 输出: 120
```

### reduceIndexed

带索引的 reduce 函数。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.reduceIndexed { index, acc, num ->
    acc + num * index
}

println(result)  // 输出: 40 (1 + 2*1 + 3*2 + 4*3 + 5*4)
```

### reduceOrNull

如果集合为空则返回 null，否则执行 reduce。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result1 = numbers.reduceOrNull { acc, num -> acc + num }
println(result1)  // 输出: 15

val emptyList = emptyList<Int>()
val result2 = emptyList.reduceOrNull { acc, num -> acc + num }
println(result2)  // 输出: null
```

### reduceRight

从最后一个元素开始，反向累积。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.reduceRight { num, acc -> num - acc }
println(result)  // 输出: 3 (1 - (2 - (3 - (4 - 5))))
```

### reduceRightIndexed

带索引的 reduceRight 函数。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.reduceRightIndexed { index, num, acc ->
    num - acc * index
}

println(result)
```

---

## fold 系列函数

### fold

从初始值开始，依次将元素累积。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val sum = numbers.fold(0) { acc, num -> acc + num }
println(sum)  // 输出: 15

val product = numbers.fold(1) { acc, num -> acc * num }
println(product)  // 输出: 120
```

### foldIndexed

带索引的 fold 函数。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.foldIndexed(0) { index, acc, num ->
    acc + num * index
}

println(result)  // 输出: 40
```

### foldRight

从初始值开始，反向累积。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.foldRight(0) { num, acc -> num - acc }
println(result)  // 输出: 3
```

### foldRightIndexed

带索引的 foldRight 函数。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.foldRightIndexed(0) { index, num, acc ->
    num - acc * index
}

println(result)
```

---

## forEach 系列函数

### forEach

对每个元素执行指定的操作。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

numbers.forEach { println(it) }
// 输出:
// 1
// 2
// 3
// 4
// 5
```

### forEachIndexed

带索引的 forEach 函数。

```kotlin
val numbers = listOf("apple", "banana", "cherry")

numbers.forEachIndexed { index, value ->
    println("$index: $value")
}
// 输出:
// 0: apple
// 1: banana
// 2: cherry
```

### onEach

对每个元素执行操作，并返回原集合。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.onEach { println(it) }
println(result)  // 输出: [1, 2, 3, 4, 5]
```

### onEachIndexed

带索引的 onEach 函数。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.onEachIndexed { index, value ->
    println("$index: $value")
}

println(result)  // 输出: [1, 2, 3, 4, 5]
```

---

## find 系列函数

### find

返回第一个满足条件的元素，如果没有则返回 null。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.find { it > 5 }
println(result)  // 输出: 6

val result2 = numbers.find { it > 20 }
println(result2)  // 输出: null
```

### findLast

返回最后一个满足条件的元素，如果没有则返回 null。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.findLast { it < 5 }
println(result)  // 输出: 4
```

### first

返回第一个元素，如果集合为空则抛出异常。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.first()
println(result)  // 输出: 1
```

### firstOrNull

返回第一个元素，如果集合为空则返回 null。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result1 = numbers.firstOrNull()
println(result1)  // 输出: 1

val emptyList = emptyList<Int>()
val result2 = emptyList.firstOrNull()
println(result2)  // 输出: null
```

### first { predicate }

返回第一个满足条件的元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.first { it > 5 }
println(result)  // 输出: 6
```

### firstOrNull { predicate }

返回第一个满足条件的元素，如果没有则返回 null。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result1 = numbers.firstOrNull { it > 5 }
println(result1)  // 输出: 6

val result2 = numbers.firstOrNull { it > 20 }
println(result2)  // 输出: null
```

### last

返回最后一个元素，如果集合为空则抛出异常。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.last()
println(result)  // 输出: 5
```

### lastOrNull

返回最后一个元素，如果集合为空则返回 null。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result1 = numbers.lastOrNull()
println(result1)  // 输出: 5

val emptyList = emptyList<Int>()
val result2 = emptyList.lastOrNull()
println(result2)  // 输出: null
```

### last { predicate }

返回最后一个满足条件的元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.last { it < 5 }
println(result)  // 输出: 4
```

### lastOrNull { predicate }

返回最后一个满足条件的元素，如果没有则返回 null。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result1 = numbers.lastOrNull { it < 5 }
println(result1)  // 输出: 4

val result2 = numbers.lastOrNull { it < 0 }
println(result2)  // 输出: null
```

### indexOf

返回指定元素的第一个索引，如果不存在则返回 -1。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 3, 2, 1)

val result = numbers.indexOf(3)
println(result)  // 输出: 2
```

### indexOfFirst

返回第一个满足条件的元素索引。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.indexOfFirst { it > 5 }
println(result)  // 输出: 5
```

### indexOfLast

返回最后一个满足条件的元素索引。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.indexOfLast { it < 5 }
println(result)  // 输出: 3
```

---

## sort 系列函数

### sorted

返回排序后的列表（升序）。

```kotlin
val numbers = listOf(5, 2, 8, 1, 9, 3)

val sorted = numbers.sorted()
println(sorted)  // 输出: [1, 2, 3, 5, 8, 9]
```

### sortedDescending

返回排序后的列表（降序）。

```kotlin
val numbers = listOf(5, 2, 8, 1, 9, 3)

val sorted = numbers.sortedDescending()
println(sorted)  // 输出: [9, 8, 5, 3, 2, 1]
```

### sortedBy

根据指定键排序（升序）。

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val sorted = people.sortedBy { it.age }
println(sorted)  // 输出: [Person(name=Charlie, age=20), Person(name=Alice, age=25), Person(name=Bob, age=30)]
```

### sortedByDescending

根据指定键排序（降序）。

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val sorted = people.sortedByDescending { it.age }
println(sorted)  // 输出: [Person(name=Bob, age=30), Person(name=Alice, age=25), Person(name=Charlie, age=20)]
```

### sortedWith

使用自定义比较器排序。

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val sorted = people.sortedWith(compareBy({ it.age }, { it.name }))
println(sorted)  // 输出: [Person(name=Charlie, age=20), Person(name=Alice, age=25), Person(name=Bob, age=30)]
```

### reversed

返回反转后的列表。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val reversed = numbers.reversed()
println(reversed)  // 输出: [5, 4, 3, 2, 1]
```

---

## groupBy 系列函数

### groupBy

根据指定键分组。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val grouped = numbers.groupBy { it % 2 }
println(grouped)
// 输出: {0=[2, 4, 6, 8, 10], 1=[1, 3, 5, 7, 9]}
```

### groupBy with value transform

分组并转换值。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val grouped = numbers.groupBy(
    keySelector = { it % 2 },
    valueTransform = { it * it }
)

println(grouped)
// 输出: {0=[4, 16, 36, 64, 100], 1=[1, 9, 25, 49, 81]}
```

### groupByTo

将分组结果添加到指定的 Map。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val result = mutableMapOf<Int, List<Int>>()

numbers.groupByTo(result) { it % 2 }
println(result)
// 输出: {0=[2, 4, 6, 8, 10], 1=[1, 3, 5, 7, 9]}
```

### associateBy

根据指定键创建 Map。

```kotlin
data class Person(val id: Int, val name: String)

val people = listOf(
    Person(1, "Alice"),
    Person(2, "Bob"),
    Person(3, "Charlie")
)

val map = people.associateBy { it.id }
println(map)  // 输出: {1=Person(id=1, name=Alice), 2=Person(id=2, name=Bob), 3=Person(id=3, name=Charlie)}
```

### associateBy with value transform

根据指定键创建 Map，并转换值。

```kotlin
data class Person(val id: Int, val name: String)

val people = listOf(
    Person(1, "Alice"),
    Person(2, "Bob"),
    Person(3, "Charlie")
)

val map = people.associateBy({ it.id }, { it.name })
println(map)  // 输出: {1=Alice, 2=Bob, 3=Charlie}
```

### associate

将元素转换为键值对。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val map = numbers.associate { it to it * it }
println(map)  // 输出: {1=1, 2=4, 3=9, 4=16, 5=25}
```

### associateWith

使用元素作为键，指定值。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val map = numbers.associateWith { it * it }
println(map)  // 输出: {1=1, 2=4, 3=9, 4=16, 5=25}
```

---

## partition 系列函数

### partition

根据条件将集合分成两个列表。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val (even, odd) = numbers.partition { it % 2 == 0 }
println(even)  // 输出: [2, 4, 6, 8, 10]
println(odd)   // 输出: [1, 3, 5, 7, 9]
```

---

## zip 系列函数

### zip

将两个列表组合成键值对列表。

```kotlin
val names = listOf("Alice", "Bob", "Charlie")
val ages = listOf(25, 30, 20)

val result = names.zip(ages)
println(result)  // 输出: [(Alice, 25), (Bob, 30), (Charlie, 20)]
```

### zip with transform

将两个列表组合并转换。

```kotlin
val names = listOf("Alice", "Bob", "Charlie")
val ages = listOf(25, 30, 20)

val result = names.zip(ages) { name, age -> "$name is $age years old" }
println(result)  // 输出: [Alice is 25 years old, Bob is 30 years old, Charlie is 20 years old]
```

### zipWithNext

将相邻元素组合。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.zipWithNext()
println(result)  // 输出: [(1, 2), (2, 3), (3, 4), (4, 5)]
```

### zipWithNext with transform

将相邻元素组合并转换。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.zipWithNext { a, b -> a + b }
println(result)  // 输出: [3, 5, 7, 9]
```

### unzip

将键值对列表拆分为两个列表。

```kotlin
val pairs = listOf(1 to "a", 2 to "b", 3 to "c")

val (numbers, letters) = pairs.unzip()
println(numbers)  // 输出: [1, 2, 3]
println(letters)  // 输出: [a, b, c]
```

---

## 其他常用函数

### count

返回满足条件的元素数量。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val evenCount = numbers.count { it % 2 == 0 }
println(evenCount)  // 输出: 5

val totalCount = numbers.count()
println(totalCount)  // 输出: 10
```

### any

检查是否有任意元素满足条件。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result1 = numbers.any { it > 3 }
println(result1)  // 输出: true

val result2 = numbers.any { it > 10 }
println(result2)  // 输出: false
```

### all

检查是否所有元素都满足条件。

```kotlin
val numbers = listOf(2, 4, 6, 8, 10)

val result1 = numbers.all { it % 2 == 0 }
println(result1)  // 输出: true

val result2 = numbers.all { it > 5 }
println(result2)  // 输出: false
```

### none

检查是否没有元素满足条件。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result1 = numbers.none { it > 10 }
println(result1)  // 输出: true

val result2 = numbers.none { it > 3 }
println(result2)  // 输出: false
```

### distinct

返回去重后的列表。

```kotlin
val numbers = listOf(1, 2, 2, 3, 3, 3, 4, 4, 4, 4)

val result = numbers.distinct()
println(result)  // 输出: [1, 2, 3, 4]
```

### distinctBy

根据指定键去重。

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 25),
    Person("Alice", 30)
)

val result = people.distinctBy { it.name }
println(result)  // 输出: [Person(name=Alice, age=25), Person(name=Bob, age=25)]
```

### intersect

返回两个集合的交集。

```kotlin
val list1 = listOf(1, 2, 3, 4, 5)
val list2 = listOf(3, 4, 5, 6, 7)

val result = list1.intersect(list2)
println(result)  // 输出: [3, 4, 5]
```

### union

返回两个集合的并集。

```kotlin
val list1 = listOf(1, 2, 3, 4, 5)
val list2 = listOf(3, 4, 5, 6, 7)

val result = list1.union(list2)
println(result)  // 输出: [1, 2, 3, 4, 5, 6, 7]
```

### subtract

返回在第一个集合但不在第二个集合的元素。

```kotlin
val list1 = listOf(1, 2, 3, 4, 5)
val list2 = listOf(3, 4, 5, 6, 7)

val result = list1.subtract(list2)
println(result)  // 输出: [1, 2]
```

### chunked

将列表分成指定大小的块。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val chunks = numbers.chunked(3)
println(chunks)  // 输出: [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]
```

### chunked with transform

将列表分成块并转换。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.chunked(3) { it.sum() }
println(result)  // 输出: [6, 15, 24, 10]
```

### windowed

创建滑动窗口。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val windows = numbers.windowed(3)
println(windows)  // 输出: [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
```

### windowed with transform

创建滑动窗口并转换。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.windowed(3) { it.sum() }
println(result)  // 输出: [6, 9, 12]
```

### windowed with step

指定步长的滑动窗口。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val windows = numbers.windowed(3, step = 2)
println(windows)  // 输出: [[1, 2, 3], [3, 4, 5], [5, 6, 7], [7, 8, 9]]
```

### drop

删除前 n 个元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.drop(2)
println(result)  // 输出: [3, 4, 5]
```

### dropLast

删除后 n 个元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.dropLast(2)
println(result)  // 输出: [1, 2, 3]
```

### dropWhile

删除满足条件的开头元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.dropWhile { it < 5 }
println(result)  // 输出: [5, 6, 7, 8, 9, 10]
```

### dropLastWhile

删除满足条件的末尾元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.dropLastWhile { it > 5 }
println(result)  // 输出: [1, 2, 3, 4, 5]
```

### take

取前 n 个元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.take(3)
println(result)  // 输出: [1, 2, 3]
```

### takeLast

取后 n 个元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.takeLast(2)
println(result)  // 输出: [4, 5]
```

### takeWhile

取满足条件的开头元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.takeWhile { it < 5 }
println(result)  // 输出: [1, 2, 3, 4]
```

### takeLastWhile

取满足条件的末尾元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.takeLastWhile { it > 5 }
println(result)  // 输出: [6, 7, 8, 9, 10]
```

### slice

返回指定索引范围的元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result1 = numbers.slice(2..5)
println(result1)  // 输出: [3, 4, 5, 6]

val result2 = numbers.slice(listOf(0, 2, 4, 6))
println(result2)  // 输出: [1, 3, 5, 7]
```

### single

返回唯一元素，如果集合不只有一个元素则抛出异常。

```kotlin
val list = listOf(42)

val result = list.single()
println(result)  // 输出: 42
```

### singleOrNull

返回唯一元素，如果集合为空或不止一个元素则返回 null。

```kotlin
val list1 = listOf(42)
val result1 = list1.singleOrNull()
println(result1)  // 输出: 42

val list2 = emptyList<Int>()
val result2 = list2.singleOrNull()
println(result2)  // 输出: null

val list3 = listOf(1, 2, 3)
val result3 = list3.singleOrNull()
println(result3)  // 输出: null
```

### single { predicate }

返回唯一满足条件的元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.single { it == 3 }
println(result)  // 输出: 3
```

### singleOrNull { predicate }

返回唯一满足条件的元素，如果没有或不止一个则返回 null。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result1 = numbers.singleOrNull { it == 3 }
println(result1)  // 输出: 3

val result2 = numbers.singleOrNull { it > 10 }
println(result2)  // 输出: null
```

### elementAt

返回指定索引的元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.elementAt(2)
println(result)  // 输出: 3
```

### elementAtOrElse

返回指定索引的元素，如果索引越界则返回默认值。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result1 = numbers.elementAtOrElse(2) { -1 }
println(result1)  // 输出: 3

val result2 = numbers.elementAtOrElse(10) { -1 }
println(result2)  // 输出: -1
```

### elementAtOrNull

返回指定索引的元素，如果索引越界则返回 null。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result1 = numbers.elementAtOrNull(2)
println(result1)  // 输出: 3

val result2 = numbers.elementAtOrNull(10)
println(result2)  // 输出: null
```

### random

返回随机元素。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.random()
println(result)  // 输出: 随机数
```

### randomOrNull

返回随机元素，如果集合为空则返回 null。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result1 = numbers.randomOrNull()
println(result1)  // 输出: 随机数

val emptyList = emptyList<Int>()
val result2 = emptyList.randomOrNull()
println(result2)  // 输出: null
```

### shuffle

返回随机打乱后的列表。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val shuffled = numbers.shuffled()
println(shuffled)  // 输出: 随机打乱的列表
```

### sum

返回所有元素的和。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.sum()
println(result)  // 输出: 15
```

### sumOf

根据指定选择器计算和。

```kotlin
data class Item(val price: Double, val quantity: Int)

val items = listOf(
    Item(10.0, 2),
    Item(20.0, 3),
    Item(30.0, 1)
)

val result = items.sumOf { it.price * it.quantity }
println(result)  // 输出: 110.0
```

### average

返回所有元素的平均值。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.average()
println(result)  // 输出: 3.0
```

### min

返回最小元素，如果集合为空则抛出异常。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.min()
println(result)  // 输出: 1
```

### minOrNull

返回最小元素，如果集合为空则返回 null。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result1 = numbers.minOrNull()
println(result1)  // 输出: 1

val emptyList = emptyList<Int>()
val result2 = emptyList.minOrNull()
println(result2)  // 输出: null
```

### minOf

根据指定选择器返回最小元素。

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = people.minOf { it.age }
println(result)  // 输出: 20
```

### minOfOrNull

根据指定选择器返回最小元素，如果集合为空则返回 null。

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = people.minOfOrNull { it.age }
println(result)  // 输出: 20
```

### minBy

根据指定键返回最小元素。

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = people.minBy { it.age }
println(result)  // 输出: Person(name=Charlie, age=20)
```

### minByOrNull

根据指定键返回最小元素，如果集合为空则返回 null。

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = people.minByOrNull { it.age }
println(result)  // 输出: Person(name=Charlie, age=20)
```

### max

返回最大元素，如果集合为空则抛出异常。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.max()
println(result)  // 输出: 5
```

### maxOrNull

返回最大元素，如果集合为空则返回 null。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result1 = numbers.maxOrNull()
println(result1)  // 输出: 5

val emptyList = emptyList<Int>()
val result2 = emptyList.maxOrNull()
println(result2)  // 输出: null
```

### maxOf

根据指定选择器返回最大元素。

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = people.maxOf { it.age }
println(result)  // 输出: 30
```

### maxOfOrNull

根据指定选择器返回最大元素，如果集合为空则返回 null。

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = people.maxOfOrNull { it.age }
println(result)  // 输出: 30
```

### maxBy

根据指定键返回最大元素。

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = people.maxBy { it.age }
println(result)  // 输出: Person(name=Bob, age=30)
```

### maxByOrNull

根据指定键返回最大元素，如果集合为空则返回 null。

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 20)
)

val result = people.maxByOrNull { it.age }
println(result)  // 输出: Person(name=Bob, age=30)
```

---

## 链式调用

Kotlin 的 Lambda 函数支持链式调用，使代码更加简洁和易读。

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers
    .filter { it % 2 == 0 }
    .map { it * it }
    .sortedDescending()
    .take(3)

println(result)  // 输出: [100, 64, 36]
```

### 复杂链式调用示例

```kotlin
data class Person(val name: String, val age: Int, val salary: Double)

val people = listOf(
    Person("Alice", 25, 50000.0),
    Person("Bob", 30, 60000.0),
    Person("Charlie", 20, 45000.0),
    Person("David", 35, 70000.0),
    Person("Eve", 28, 55000.0)
)

val result = people
    .filter { it.age >= 25 }
    .map { it.name to it.salary }
    .sortedByDescending { it.second }
    .take(2)
    .map { (name, salary) -> "$name: $${salary.toInt()}" }

println(result)  // 输出: [David: $70000, Bob: $60000]
```

---

## 性能优化

### 使用 Sequence 进行懒加载

对于大型集合，使用 Sequence 可以提高性能。

```kotlin
val numbers = (1..1000000).toList()

// 不推荐：立即执行
val result1 = numbers
    .filter { it % 2 == 0 }
    .map { it * it }
    .take(10)

// 推荐：懒加载
val result2 = numbers
    .asSequence()
    .filter { it % 2 == 0 }
    .map { it * it }
    .take(10)
    .toList()
```

### 避免不必要的中间集合

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// 不推荐：创建多个中间集合
val result1 = numbers.map { it * 2 }.filter { it > 5 }.map { it + 1 }

// 推荐：使用 Sequence
val result2 = numbers.asSequence().map { it * 2 }.filter { it > 5 }.map { it + 1 }.toList()
```

### 使用索引操作符

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// 不推荐
val result1 = numbers.filter { it == 3 }.first()

// 推荐
val result2 = numbers.find { it == 3 }
```

---

## 最佳实践

### 1. 选择合适的函数

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// 需要转换时使用 map
val squares = numbers.map { it * it }

// 需要过滤时使用 filter
val evenNumbers = numbers.filter { it % 2 == 0 }

// 需要查找时使用 find
val result = numbers.find { it > 3 }
```

### 2. 使用链式调用提高可读性

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers
    .filter { it % 2 == 0 }
    .map { it * it }
    .sortedDescending()
```

### 3. 使用 Sequence 处理大型集合

```kotlin
val largeList = (1..1000000).toList()

val result = largeList
    .asSequence()
    .filter { it % 2 == 0 }
    .map { it * it }
    .take(10)
    .toList()
```

### 4. 使用安全的查找函数

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// 推荐
val result = numbers.find { it > 10 }
println(result)  // 输出: null

// 不推荐
val result2 = numbers.first { it > 10 }  // 抛出异常
```

### 5. 使用索引函数提高性能

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// 推荐
val result = numbers.indexOf(3)

// 不推荐
val result2 = numbers.indexOfFirst { it == 3 }
```

### 6. 使用分组函数简化代码

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

// 推荐
val grouped = numbers.groupBy { it % 2 }

// 不推荐
val even = numbers.filter { it % 2 == 0 }
val odd = numbers.filter { it % 2 != 0 }
```

### 7. 使用 partition 简化条件分组

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

// 推荐
val (even, odd) = numbers.partition { it % 2 == 0 }

// 不推荐
val even = numbers.filter { it % 2 == 0 }
val odd = numbers.filter { it % 2 != 0 }
```

---

## 注意事项

1. **不可变性**：大多数函数返回新的集合，不修改原集合
2. **空集合处理**：使用 `OrNull` 版本的函数避免异常
3. **性能考虑**：大型集合使用 Sequence 提高性能
4. **链式调用**：合理使用链式调用，但避免过度嵌套
5. **类型安全**：利用 Kotlin 的类型系统，避免运行时错误

---

## 相关资源

- [Kotlin 官方文档 - Collections](https://kotlinlang.org/docs/collections-overview.html)
- [Kotlin 标准库 - List](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/-list/)
- [Kotlin 标准库 - Sequence](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.sequences/)
