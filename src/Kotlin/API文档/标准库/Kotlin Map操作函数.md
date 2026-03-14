---
title: Kotlin Map 操作函数
date: 2026-03-09
footer: Trae编辑
---


本文档详细介绍 Kotlin 中 Map 类型的常用操作函数及其用法示例。

## 目录

- [创建 Map](#创建-map)
- [访问元素](#访问元素)
- [修改 Map](#修改-map)
- [遍历 Map](#遍历-map)
- [转换操作](#转换操作)
- [过滤操作](#过滤操作)
- [其他常用操作](#其他常用操作)

## 创建 Map

### 不可变 Map

```kotlin
// 使用 mapOf() 创建不可变 Map
val map1 = mapOf("a" to 1, "b" to 2, "c" to 3)

// 使用 emptyMap() 创建空的不可变 Map
val emptyMap = emptyMap<String, Int>()
```

### 可变 Map

```kotlin
// 使用 mutableMapOf() 创建可变 Map
val map2 = mutableMapOf("a" to 1, "b" to 2)

// 使用 HashMap() 构造函数
val map3 = HashMap<String, Int>()
map3["a"] = 1
map3["b"] = 2

// 使用 LinkedHashMap() 构造函数（保持插入顺序）
val map4 = LinkedHashMap<String, Int>()
map4["a"] = 1
map4["b"] = 2
```

## 访问元素

### 获取值

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3)

// 使用 [] 运算符
val value1 = map["a"] // 返回 1
val value2 = map["d"] // 返回 null

// 使用 get() 方法
val value3 = map.get("b") // 返回 2

// 使用 getOrDefault() 方法
val value4 = map.getOrDefault("d", 0) // 返回 0

// 使用 getOrElse() 方法
val value5 = map.getOrElse("d") { -1 } // 返回 -1
```

### 检查键是否存在

```kotlin
val map = mapOf("a" to 1, "b" to 2)

// 使用 containsKey() 方法
val hasKey = map.containsKey("a") // 返回 true

// 使用 in 运算符
val hasKey2 = "b" in map // 返回 true
```

### 检查值是否存在

```kotlin
val map = mapOf("a" to 1, "b" to 2)

// 使用 containsValue() 方法
val hasValue = map.containsValue(1) // 返回 true
```

## 修改 Map

> 注意：只有可变 Map（MutableMap）可以修改

### 添加或更新元素

```kotlin
val map = mutableMapOf("a" to 1, "b" to 2)

// 使用 [] 运算符添加或更新
map["c"] = 3 // 添加新元素
map["a"] = 10 // 更新现有元素

// 使用 put() 方法
map.put("d", 4) // 添加新元素
map.put("b", 20) // 更新现有元素

// 使用 putAll() 方法添加多个元素
map.putAll(mapOf("e" to 5, "f" to 6))
```

### 删除元素

```kotlin
val map = mutableMapOf("a" to 1, "b" to 2, "c" to 3)

// 使用 [] 运算符设置为 null
map["a"] = null // 删除键 "a"

// 使用 remove() 方法
map.remove("b") // 删除键 "b"

// 使用 clear() 方法清空所有元素
map.clear()
```

## 遍历 Map

### 遍历键值对

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3)

// 使用 forEach() 方法
map.forEach { (key, value) ->
    println("$key: $value")
}

// 使用 for 循环
for ((key, value) in map) {
    println("$key: $value")
}
```

### 遍历键

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3)

// 使用 keys 属性
for (key in map.keys) {
    println(key)
}

// 使用 forEach 遍历键
map.keys.forEach { key ->
    println(key)
}
```

### 遍历值

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3)

// 使用 values 属性
for (value in map.values) {
    println(value)
}

// 使用 forEach 遍历值
map.values.forEach { value ->
    println(value)
}
```

## 转换操作

### 转换为其他集合

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3)

// 转换为 List<Pair<String, Int>>
val list = map.toList()

// 转换为 Set<Pair<String, Int>>
val set = map.toSet()

// 转换为可变 Map
val mutableMap = map.toMutableMap()

// 转换为 HashMap
val hashMap = map.toHashMap()

// 转换为 LinkedHashMap
val linkedHashMap = map.toLinkedHashMap()
```

### 映射操作

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3)

// 映射键值对
val mapped = map.map { (key, value) ->
    "$key: ${value * 2}"
}
// 结果: ["a: 2", "b: 4", "c: 6"]

// 映射为新的 Map
val newMap = map.mapKeys { (key, _) -> key.uppercase() }
// 结果: {"A" to 1, "B" to 2, "C" to 3}

val newMap2 = map.mapValues { (_, value) -> value * 2 }
// 结果: {"a" to 2, "b" to 4, "c" to 6}

// 使用 associate() 创建新的 Map
val list = listOf("a", "b", "c")
val associated = list.associateWith { it.length }
// 结果: {"a" to 1, "b" to 1, "c" to 1}

val associated2 = list.associate { it to it.uppercase() }
// 结果: {"a" to "A", "b" to "B", "c" to "C"}
```

## 过滤操作

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3, "d" to 4)

// 过滤键值对
val filtered = map.filter { (key, value) ->
    key > "a" && value > 2
}
// 结果: {"c" to 3, "d" to 4}

// 过滤键
val filteredKeys = map.filterKeys { it > "b" }
// 结果: {"c" to 3, "d" to 4}

// 过滤值
val filteredValues = map.filterValues { it > 2 }
// 结果: {"c" to 3, "d" to 4}
```

## 其他常用操作

### 大小操作

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3)

// 获取大小
val size = map.size // 返回 3

// 检查是否为空
val isEmpty = map.isEmpty() // 返回 false
val isNotEmpty = map.isNotEmpty() // 返回 true
```

### 合并操作

```kotlin
val map1 = mapOf("a" to 1, "b" to 2)
val map2 = mapOf("b" to 3, "c" to 4)

// 使用 plus 运算符合并
val merged = map1 + map2
// 结果: {"a" to 1, "b" to 3, "c" to 4}（map2 中的值覆盖 map1 中的值）

// 使用 minus 运算符移除元素
val removed = merged - "b"
// 结果: {"a" to 1, "c" to 4}
```

### 分组操作

```kotlin
val list = listOf("apple", "banana", "cherry", "date")

// 按首字母分组
val grouped = list.groupBy { it.first() }
// 结果: {"a" to ["apple"], "b" to ["banana"], "c" to ["cherry"], "d" to ["date"]}

// 按长度分组
val groupedByLength = list.groupBy { it.length }
// 结果: {5 to ["apple"], 6 to ["banana", "cherry"], 4 to ["date"]}
```

### 排序操作

```kotlin
val map = mapOf("c" to 3, "a" to 1, "b" to 2)

// 按键排序
val sortedByKey = map.toSortedMap()
// 结果: {"a" to 1, "b" to 2, "c" to 3}

// 按值排序
val sortedByValue = map.toList()
    .sortedBy { (_, value) -> value }
    .toMap()
// 结果: {"a" to 1, "b" to 2, "c" to 3}
```

### 计算操作

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3)

// 求和
val sum = map.values.sum() // 返回 6

// 求平均值
val average = map.values.average() // 返回 2.0

// 求最大值
val max = map.values.maxOrNull() // 返回 3

// 求最小值
val min = map.values.minOrNull() // 返回 1
```

## 示例：综合运用

```kotlin
fun main() {
    // 创建一个可变 Map
    val userScores = mutableMapOf(
        "Alice" to 85,
        "Bob" to 92,
        "Charlie" to 78,
        "David" to 95
    )
    
    // 添加新用户
    userScores["Eve"] = 88
    
    // 更新分数
    userScores["Charlie"] = 82
    
    // 过滤出分数大于 90 的用户
    val highScorers = userScores.filterValues { it > 90 }
    println("High scorers: $highScorers")
    
    // 计算平均分数
    val averageScore = userScores.values.average()
    println("Average score: $averageScore")
    
    // 按分数排序
    val sortedByScore = userScores.toList()
        .sortedByDescending { (_, score) -> score }
        .toMap()
    println("Sorted by score: $sortedByScore")
    
    // 转换为用户名大写的 Map
    val uppercaseNames = userScores.mapKeys { (name, _) -> name.uppercase() }
    println("Uppercase names: $uppercaseNames")
}

// 输出结果：
// High scorers: {Bob=92, David=95}
// Average score: 86.4
// Sorted by score: {David=95, Bob=92, Eve=88, Alice=85, Charlie=82}
// Uppercase names: {ALICE=85, BOB=92, CHARLIE=82, DAVID=95, EVE=88}
```

## 总结

Kotlin 的 Map 类型提供了丰富的操作函数，使得对键值对集合的处理变得简单而直观。通过本文档的示例，您应该能够掌握 Map 的基本操作和高级用法，从而在实际开发中更加高效地使用 Map 类型。