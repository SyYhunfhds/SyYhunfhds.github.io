---
title: Kotlin Collection Build 方法大全
date: 2026-03-08
footer: Trae编辑
---

## 目录

1. [概述](#概述)
2. [buildList](#buildlist)
3. [buildSet](#buildset)
4. [buildMap](#buildmap)
5. [buildMutableList](#buildmutablelist)
6. [buildMutableSet](#buildmutableset)
7. [buildMutableMap](#buildmutablemap)
8. [实际应用场景](#实际应用场景)
9. [性能对比](#性能对比)
10. [最佳实践](#最佳实践)

---

## 概述

Kotlin 标准库提供了一组 `buildXXX` 函数，用于高效构建集合。这些函数允许在构建过程中动态添加元素，最终返回一个不可变或可变的集合。

### 主要特点

- **类型安全**：编译时类型检查
- **性能优化**：内部优化了构建过程
- **简洁语法**：使用 lambda 表达式，代码更清晰
- **灵活性**：支持条件添加、循环添加等复杂逻辑

### 函数分类

| 函数 | 返回类型 | 可变性 | 说明 |
|------|---------|--------|------|
| `buildList` | `List<T>` | 不可变 | 构建不可变列表 |
| `buildSet` | `Set<T>` | 不可变 | 构建不可变集合 |
| `buildMap` | `Map<K, V>` | 不可变 | 构建不可变映射 |
| `buildMutableList` | `MutableList<T>` | 可变 | 构建可变列表 |
| `buildMutableSet` | `MutableSet<T>` | 可变 | 构建可变集合 |
| `buildMutableMap` | `MutableMap<K, V>` | 可变 | 构建可变映射 |

---

## buildList

### 基本语法

```kotlin
inline fun <T> buildList(
    builderAction: MutableList<T>.() -> Unit
): List<T>

inline fun <T> buildList(
    capacity: Int,
    builderAction: MutableList<T>.() -> Unit
): List<T>
```

### 基本用法

```kotlin
val list = buildList {
    add(1)
    add(2)
    add(3)
    addAll(listOf(4, 5))
}

println(list)  // 输出: [1, 2, 3, 4, 5]
```

### 指定容量

```kotlin
val list = buildList(10) {
    add(1)
    add(2)
    add(3)
}
```

### 内部可修改，外部不可变

```kotlin
val list = buildList {
    add(1)
    add(2)
    add(3)
    this[0] = 10  // 内部可以修改
}

println(list)  // 输出: [10, 2, 3]
// list[0] = 20  // 编译错误，外部不可修改
```

### 条件添加

```kotlin
val list = buildList {
    add("Apple")
    add("Banana")
    
    if (true) {
        add("Orange")
    }
    
    if (false) {
        add("Grape")
    }
}

println(list)  // 输出: [Apple, Banana, Orange]
```

### 循环添加

```kotlin
val list = buildList {
    for (i in 1..5) {
        add(i * i)
    }
}

println(list)  // 输出: [1, 4, 9, 16, 25]
```

### 过滤和转换

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val evenNumbers = buildList {
    for (num in numbers) {
        if (num % 2 == 0) {
            add(num * num)
        }
    }
}

println(evenNumbers)  // 输出: [4, 16, 36, 64, 100]
```

### 嵌套结构

```kotlin
val matrix = buildList {
    for (i in 1..3) {
        add(buildList {
            for (j in 1..3) {
                add(i * j)
            }
        })
    }
}

println(matrix)  // 输出: [[1, 2, 3], [2, 4, 6], [3, 6, 9]]
```

---

## buildSet

### 基本语法

```kotlin
inline fun <T> buildSet(
    builderAction: MutableSet<T>.() -> Unit
): Set<T>

inline fun <T> buildSet(
    capacity: Int,
    builderAction: MutableSet<T>.() -> Unit
): Set<T>
```

### 基本用法

```kotlin
val set = buildSet {
    add(1)
    add(2)
    add(3)
    add(1)  // 重复元素会被忽略
}

println(set)  // 输出: [1, 2, 3]
```

### 自动去重

```kotlin
val set = buildSet {
    add("Apple")
    add("Banana")
    add("Apple")  // 重复
    add("Orange")
    add("Banana")  // 重复
}

println(set)  // 输出: [Apple, Banana, Orange]
```

### 条件添加

```kotlin
val set = buildSet {
    add(1)
    add(2)
    
    if (true) {
        add(3)
    }
    
    if (false) {
        add(4)
    }
}

println(set)  // 输出: [1, 2, 3]
```

### 循环添加

```kotlin
val set = buildSet {
    for (i in 1..10) {
        if (i % 2 == 0) {
            add(i)
        }
    }
}

println(set)  // 输出: [2, 4, 6, 8, 10]
```

---

## buildMap

### 基本语法

```kotlin
inline fun <K, V> buildMap(
    builderAction: MutableMap<K, V>.() -> Unit
): Map<K, V>

inline fun <K, V> buildMap(
    capacity: Int,
    builderAction: MutableMap<K, V>.() -> Unit
): Map<K, V>
```

### 基本用法

```kotlin
val map = buildMap {
    put("key1", "value1")
    put("key2", "value2")
    put("key3", "value3")
}

println(map)  // 输出: {key1=value1, key2=value2, key3=value3}
```

### 覆盖键值

```kotlin
val map = buildMap {
    put("key1", "value1")
    put("key2", "value2")
    put("key1", "newValue1")  // 覆盖之前的值
}

println(map)  // 输出: {key1=newValue1, key2=value2}
```

### 使用索引操作符

```kotlin
val map = buildMap {
    this["name"] = "Alice"
    this["age"] = "25"
    this["city"] = "New York"
}

println(map)  // 输出: {name=Alice, age=25, city=New York}
```

### 条件添加

```kotlin
val map = buildMap {
    put("key1", "value1")
    put("key2", "value2")
    
    if (true) {
        put("key3", "value3")
    }
    
    if (false) {
        put("key4", "value4")
    }
}

println(map)  // 输出: {key1=value1, key2=value2, key3=value3}
```

### 循环添加

```kotlin
val map = buildMap {
    for (i in 1..5) {
        put("key$i", "value$i")
    }
}

println(map)  // 输出: {key1=value1, key2=value2, key3=value3, key4=value4, key5=value5}
```

### 复杂数据结构

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 35)
)

val personMap = buildMap {
    for (person in people) {
        put(person.name, person.age)
    }
}

println(personMap)  // 输出: {Alice=25, Bob=30, Charlie=35}
```

---

## buildMutableList

### 基本语法

```kotlin
inline fun <T> buildMutableList(
    builderAction: MutableList<T>.() -> Unit
): MutableList<T>

inline fun <T> buildMutableList(
    capacity: Int,
    builderAction: MutableList<T>.() -> Unit
): MutableList<T>
```

### 基本用法

```kotlin
val mutableList = buildMutableList {
    add(1)
    add(2)
    add(3)
}

mutableList.add(4)  // 可以修改
println(mutableList)  // 输出: [1, 2, 3, 4]
```

### 外部可修改

```kotlin
val mutableList = buildMutableList {
    add(1)
    add(2)
    add(3)
}

mutableList[0] = 10  // 外部可以修改
mutableList.add(4)
mutableList.removeAt(1)

println(mutableList)  // 输出: [10, 3, 4]
```

### 动态更新

```kotlin
val mutableList = buildMutableList {
    add(1)
    add(2)
    add(3)
}

mutableList.addAll(listOf(4, 5, 6))
mutableList.removeIf { it % 2 == 0 }

println(mutableList)  // 输出: [1, 3, 5]
```

---

## buildMutableSet

### 基本语法

```kotlin
inline fun <T> buildMutableSet(
    builderAction: MutableSet<T>.() -> Unit
): MutableSet<T>

inline fun <T> buildMutableSet(
    capacity: Int,
    builderAction: MutableSet<T>.() -> Unit
): MutableSet<T>
```

### 基本用法

```kotlin
val mutableSet = buildMutableSet {
    add(1)
    add(2)
    add(3)
}

mutableSet.add(4)  // 可以修改
println(mutableSet)  // 输出: [1, 2, 3, 4]
```

### 外部可修改

```kotlin
val mutableSet = buildMutableSet {
    add(1)
    add(2)
    add(3)
}

mutableSet.add(4)
mutableSet.remove(2)
mutableSet.addAll(listOf(5, 6, 7))

println(mutableSet)  // 输出: [1, 3, 4, 5, 6, 7]
```

### 动态更新

```kotlin
val mutableSet = buildMutableSet {
    add(1)
    add(2)
    add(3)
    add(4)
    add(5)
}

mutableSet.removeIf { it % 2 == 0 }

println(mutableSet)  // 输出: [1, 3, 5]
```

---

## buildMutableMap

### 基本语法

```kotlin
inline fun <K, V> buildMutableMap(
    builderAction: MutableMap<K, V>.() -> Unit
): MutableMap<K, V>

inline fun <K, V> buildMutableMap(
    capacity: Int,
    builderAction: MutableMap<K, V>.() -> Unit
): MutableMap<K, V>
```

### 基本用法

```kotlin
val mutableMap = buildMutableMap {
    put("key1", "value1")
    put("key2", "value2")
}

mutableMap["key3"] = "value3"  // 可以修改
println(mutableMap)  // 输出: {key1=value1, key2=value2, key3=value3}
```

### 外部可修改

```kotlin
val mutableMap = buildMutableMap {
    put("key1", "value1")
    put("key2", "value2")
    put("key3", "value3")
}

mutableMap["key1"] = "newValue1"
mutableMap.remove("key2")
mutableMap["key4"] = "value4"

println(mutableMap)  // 输出: {key1=newValue1, key3=value3, key4=value4}
```

### 动态更新

```kotlin
val mutableMap = buildMutableMap {
    put("a", 1)
    put("b", 2)
    put("c", 3)
    put("d", 4)
    put("e", 5)
}

mutableMap.keys.removeIf { it == "a" || it == "c" }

println(mutableMap)  // 输出: {b=2, d=4, e=5}
```

---

## 实际应用场景

### 1. 数据转换

```kotlin
data class User(val id: Int, val name: String, val age: Int)

val users = listOf(
    User(1, "Alice", 25),
    User(2, "Bob", 30),
    User(3, "Charlie", 35)
)

val userNames = buildList {
    for (user in users) {
        add(user.name)
    }
}

println(userNames)  // 输出: [Alice, Bob, Charlie]
```

### 2. 条件过滤

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val filtered = buildList {
    for (num in numbers) {
        when {
            num % 2 == 0 -> add("Even: $num")
            num % 3 == 0 -> add("Divisible by 3: $num")
            else -> add("Other: $num")
        }
    }
}

println(filtered)
// 输出: [Other: 1, Even: 2, Divisible by 3: 3, Even: 4, Other: 5, Even: 6, Other: 7, Even: 8, Divisible by 3: 9, Even: 10]
```

### 3. 分组统计

```kotlin
val words = listOf("apple", "banana", "cherry", "date", "elderberry")

val wordGroups = buildMap {
    for (word in words) {
        val firstLetter = word[0].uppercaseChar()
        if (firstLetter !in this) {
            this[firstLetter.toString()] = mutableListOf()
        }
        this[firstLetter.toString()]!!.add(word)
    }
}

println(wordGroups)
// 输出: {A=[apple], B=[banana], C=[cherry], D=[date], E=[elderberry]}
```

### 4. 嵌套数据处理

```kotlin
val data = listOf(
    listOf(1, 2, 3),
    listOf(4, 5, 6),
    listOf(7, 8, 9)
)

val flattened = buildList {
    for (row in data) {
        for (item in row) {
            add(item * item)
        }
    }
}

println(flattened)  // 输出: [1, 4, 9, 16, 25, 36, 49, 64, 81]
```

### 5. 配置构建

```kotlin
data class Config(
    val name: String,
    val port: Int,
    val debug: Boolean,
    val features: Set<String>
)

val config = buildMap {
    put("name", "MyApp")
    put("port", 8080)
    put("debug", true)
    put("features", buildSet {
        add("auth")
        add("logging")
        add("caching")
    })
}

println(config)
// 输出: {name=MyApp, port=8080, debug=true, features=[auth, logging, caching]}
```

### 6. 树形结构构建

```kotlin
data class TreeNode(val value: Int, val children: List<TreeNode>)

fun buildTree(depth: Int, maxDepth: Int): TreeNode {
    return TreeNode(depth, buildList {
        if (depth < maxDepth) {
            for (i in 1..3) {
                add(buildTree(depth + 1, maxDepth))
            }
        }
    })
}

val tree = buildTree(0, 2)
println(tree)
// 输出: TreeNode(value=0, children=[TreeNode(value=1, children=[TreeNode(value=2, children=[]), TreeNode(value=2, children=[]), TreeNode(value=2, children=[])]), TreeNode(value=1, children=[TreeNode(value=2, children=[]), TreeNode(value=2, children=[]), TreeNode(value=2, children=[])]), TreeNode(value=1, children=[TreeNode(value=2, children=[]), TreeNode(value=2, children=[]), TreeNode(value=2, children=[])])])
```

### 7. 矩阵转置

```kotlin
val matrix = listOf(
    listOf(1, 2, 3),
    listOf(4, 5, 6),
    listOf(7, 8, 9)
)

val transposed = buildList {
    for (col in matrix[0].indices) {
        add(buildList {
            for (row in matrix.indices) {
                add(matrix[row][col])
            }
        })
    }
}

println(transposed)
// 输出: [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
```

### 8. 扁平化嵌套结构

```kotlin
val nested = listOf(
    listOf(listOf(1, 2), listOf(3, 4)),
    listOf(listOf(5, 6), listOf(7, 8))
)

val flattened = buildList {
    for (outer in nested) {
        for (inner in outer) {
            for (item in inner) {
                add(item)
            }
        }
    }
}

println(flattened)  // 输出: [1, 2, 3, 4, 5, 6, 7, 8]
```

---

## 性能对比

### buildList vs mutableListOf + toList

```kotlin
// 不推荐
val list1 = mutableListOf<Int>().apply {
    add(1)
    add(2)
    add(3)
}.toList()

// 推荐
val list2 = buildList {
    add(1)
    add(2)
    add(3)
}
```

### 性能优势

1. **避免不必要的复制**：`buildList` 内部优化了构建过程
2. **预分配容量**：可以指定初始容量，减少扩容开销
3. **内联优化**：编译器可以内联 lambda 表达式

### 性能测试

```kotlin
import kotlin.system.measureTimeMillis

// 测试 buildList
val time1 = measureTimeMillis {
    repeat(10000) {
        val list = buildList {
            for (i in 1..100) {
                add(i)
            }
        }
    }
}

// 测试 mutableListOf + toList
val time2 = measureTimeMillis {
    repeat(10000) {
        val list = mutableListOf<Int>().apply {
            for (i in 1..100) {
                add(i)
            }
        }.toList()
    }
}

println("buildList: ${time1}ms")
println("mutableListOf + toList: ${time2}ms")
```

---

## 最佳实践

### 1. 选择合适的构建函数

```kotlin
// 需要不可变集合时
val immutableList = buildList { }
val immutableSet = buildSet { }
val immutableMap = buildMap { }

// 需要可变集合时
val mutableList = buildMutableList { }
val mutableSet = buildMutableSet { }
val mutableMap = buildMutableMap { }
```

### 2. 指定初始容量

```kotlin
// 如果知道大概的元素数量，指定容量以提高性能
val list = buildList(1000) {
    for (i in 1..1000) {
        add(i)
    }
}
```

### 3. 使用条件添加

```kotlin
val list = buildList {
    add("always")
    
    if (condition) {
        add("conditional")
    }
}
```

### 4. 避免过度嵌套

```kotlin
// 不推荐
val list = buildList {
    buildList {
        buildList {
            add(1)
        }
    }
}

// 推荐
val list = buildList {
    add(listOf(listOf(1)))
}
```

### 5. 使用标准库函数

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// 不推荐
val squares = buildList {
    for (num in numbers) {
        add(num * num)
    }
}

// 推荐
val squares = numbers.map { it * it }
```

### 6. 复杂逻辑使用 buildXXX

```kotlin
// 复杂逻辑时使用 buildXXX 更清晰
val result = buildList {
    for (item in items) {
        if (item.isValid()) {
            add(item.transform())
        }
    }
    
    if (result.isEmpty()) {
        add(defaultValue)
    }
}
```

### 7. 避免在 lambda 中使用外部可变状态

```kotlin
// 不推荐
var counter = 0
val list = buildList {
    add(counter++)
    add(counter++)
}

// 推荐
val list = buildList {
    var counter = 0
    add(counter++)
    add(counter++)
}
```

---

## 注意事项

1. **不可变性**：`buildList`、`buildSet`、`buildMap` 返回的是不可变集合
2. **线程安全**：构建过程不是线程安全的，需要在单线程中使用
3. **内存泄漏**：在 lambda 中捕获外部变量可能导致内存泄漏
4. **性能考虑**：对于简单场景，使用标准库函数可能更高效
5. **代码可读性**：过度使用 `buildXXX` 可能降低代码可读性

---

## 相关资源

- [Kotlin 官方文档 - Collections](https://kotlinlang.org/docs/collections-overview.html)
- [Kotlin 标准库 - buildList](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/build-list.html)
- [Kotlin 标准库 - buildSet](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/build-set.html)
- [Kotlin 标准库 - buildMap](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/build-map.html)
