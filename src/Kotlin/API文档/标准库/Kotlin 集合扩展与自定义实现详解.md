---
title: Kotlin 集合扩展与自定义实现详解
date: 2026-03-19
footer: Trae编辑
---


## 目录

1. [概述](#概述)
2. [扩展函数基础](#扩展函数基础)
3. [为集合类型添加扩展函数](#为集合类型添加扩展函数)
4. [扩展属性](#扩展属性)
5. [重写集合 API](#重写集合-api)
6. [自定义集合实现](#自定义集合实现)
7. [运算符重载](#运算符重载)
8. [委托模式](#委托模式)
9. [最佳实践](#最佳实践)
10. [常见问题与解决方案](#常见问题与解决方案)
11. [总结](#总结)

## 概述

Kotlin 提供了强大的扩展机制，允许开发者为现有的类添加新功能，而无需继承或修改原始类。这对于集合类型尤其有用，因为：

1. **增强现有功能**：为标准集合添加自定义操作
2. **提高代码可读性**：创建更符合业务语义的方法
3. **避免工具类**：减少静态工具方法的使用
4. **统一 API 风格**：保持代码风格的一致性

## 扩展函数基础

### 什么是扩展函数？

扩展函数是一种特殊的函数，它可以在不继承类的情况下，为现有类添加新的方法。

### 基本语法

```kotlin
fun String.addExclamation(): String {
    return this + "!"
}

// 使用
val text = "Hello"
println(text.addExclamation())  // Hello!
```

### 扩展函数的特点

1. **静态解析**：扩展函数在编译时确定，不是运行时
2. **不修改原始类**：扩展函数不会真正修改原始类
3. **作用域**：扩展函数需要导入才能使用
4. **优先级**：成员函数优先于扩展函数

```kotlin
class MyClass {
    fun print() {
        println("Member function")
    }
}

fun MyClass.print() {
    println("Extension function")
}

fun main() {
    val obj = MyClass()
    obj.print()  // 输出: Member function（成员函数优先）
}
```

## 为集合类型添加扩展函数

### 基本集合扩展

```kotlin
// 为 List 添加扩展函数
fun <T> List<T>.second(): T {
    if (this.size < 2) {
        throw NoSuchElementException("List has less than 2 elements")
    }
    return this[1]
}

// 为 MutableList 添加扩展函数
fun <T> MutableList<T>.swap(index1: Int, index2: Int) {
    val temp = this[index1]
    this[index1] = this[index2]
    this[index2] = temp
}

// 使用
fun main() {
    val list = listOf(1, 2, 3, 4, 5)
    println(list.second())  // 2
    
    val mutableList = mutableListOf(1, 2, 3, 4, 5)
    mutableList.swap(0, 4)
    println(mutableList)  // [5, 2, 3, 4, 1]
}
```

### 过滤和转换扩展

```kotlin
// 过滤非空元素
fun <T : Any> List<T?>.filterNotNull(): List<T> {
    return this.filterNotNull()
}

// 分组并计数
fun <T, K> List<T>.groupByCount(keySelector: (T) -> K): Map<K, Int> {
    return this.groupBy(keySelector).mapValues { it.value.size }
}

// 分批处理
fun <T> List<T>.chunked(size: Int): List<List<T>> {
    return this.chunked(size)
}

// 使用
fun main() {
    val list = listOf("apple", "banana", "cherry", "date", "elderberry")
    
    // 按首字母分组并计数
    val countByFirstLetter = list.groupByCount { it.first() }
    println(countByFirstLetter)  // {a=1, b=1, c=1, d=1, e=1}
    
    // 分批处理
    val chunks = list.chunked(2)
    println(chunks)  // [[apple, banana], [cherry, date], [elderberry]]
}
```

### 统计和聚合扩展

```kotlin
// 计算平均值（数值类型）
fun List<Int>.average(): Double {
    if (this.isEmpty()) return 0.0
    return this.sum().toDouble() / this.size
}

// 计算中位数
fun <T : Comparable<T>> List<T>.median(): T? {
    if (this.isEmpty()) return null
    val sorted = this.sorted()
    return if (sorted.size % 2 == 0) {
        sorted[sorted.size / 2 - 1]
    } else {
        sorted[sorted.size / 2]
    }
}

// 计算众数
fun <T> List<T>.mode(): T? {
    if (this.isEmpty()) return null
    return this.groupBy { it }
        .maxByOrNull { it.value.size }
        ?.key
}

// 使用
fun main() {
    val numbers = listOf(1, 2, 3, 4, 5, 5, 6, 7, 8, 9, 10)
    
    println("Average: ${numbers.average()}")  // Average: 5.454545...
    println("Median: ${numbers.median()}")    // Median: 5
    println("Mode: ${numbers.mode()}")        // Mode: 5
}
```

### 字符串处理扩展

```kotlin
// 连接字符串并添加分隔符
fun <T> List<T>.joinToStringWithSeparator(
    separator: String = ", ",
    prefix: String = "",
    postfix: String = ""
): String {
    return this.joinToString(separator, prefix, postfix)
}

// 转换为 JSON 格式字符串
fun List<String>.toJsonArray(): String {
    return "[${this.joinToString(", ") { "\"$it\"" }}]"
}

// 使用
fun main() {
    val fruits = listOf("apple", "banana", "cherry")
    
    println(fruits.joinToStringWithSeparator(" | ", "[", "]"))
    // [apple | banana | cherry]
    
    println(fruits.toJsonArray())
    // ["apple", "banana", "cherry"]
}
```

## 扩展属性

### 基本扩展属性

```kotlin
// 为 List 添加扩展属性
val <T> List<T>.lastIndex: Int
    get() = this.size - 1

val <T> List<T>.isNotEmpty: Boolean
    get() = this.size > 0

// 为 String 添加扩展属性
val String.isNumeric: Boolean
    get() = this.all { it.isDigit() }

val String.wordCount: Int
    get() = this.split(Regex("\\s+")).filter { it.isNotEmpty() }.size

// 使用
fun main() {
    val list = listOf(1, 2, 3, 4, 5)
    println("Last index: ${list.lastIndex}")      // 4
    println("Is not empty: ${list.isNotEmpty}")   // true
    
    val text = "Hello World Kotlin"
    println("Word count: ${text.wordCount}")      // 3
}
```

### 计算属性

```kotlin
// 计算集合的统计信息
val List<Int>.stats: Stats
    get() = Stats(this)

data class Stats(
    val count: Int,
    val sum: Int,
    val average: Double,
    val min: Int,
    val max: Int
) {
    constructor(numbers: List<Int>) : this(
        count = numbers.size,
        sum = numbers.sum(),
        average = if (numbers.isEmpty()) 0.0 else numbers.average(),
        min = numbers.minOrNull() ?: 0,
        max = numbers.maxOrNull() ?: 0
    )
}

// 使用
fun main() {
    val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    println("Stats: ${numbers.stats}")
    // Stats(count=10, sum=55, average=5.5, min=1, max=10)
}
```

## 重写集合 API

### 继承 AbstractList

```kotlin
class CustomList<T>(
    private val elements: List<T>
) : AbstractList<T>() {
    
    override val size: Int
        get() = elements.size
    
    override fun get(index: Int): T {
        return elements[index]
    }
    
    // 重写其他方法以提供更高效的实现
    override fun contains(element: T): Boolean {
        return elements.contains(element)
    }
    
    override fun indexOf(element: T): Int {
        return elements.indexOf(element)
    }
    
    override fun lastIndexOf(element: T): Int {
        return elements.lastIndexOf(element)
    }
}

// 使用
fun main() {
    val list = CustomList(listOf(1, 2, 3, 4, 5))
    println("Size: ${list.size}")           // 5
    println("Element at 2: ${list[2]}")     // 3
    println("Contains 3: ${list.contains(3)}")  // true
}
```

### 继承 AbstractMutableList

```kotlin
class ObservableList<T>(
    private val delegate: MutableList<T> = mutableListOf()
) : AbstractMutableList<T>() {
    
    private val listeners = mutableListOf<ListChangeListener<T>>()
    
    fun addListener(listener: ListChangeListener<T>) {
        listeners.add(listener)
    }
    
    fun removeListener(listener: ListChangeListener<T>) {
        listeners.remove(listener)
    }
    
    override val size: Int
        get() = delegate.size
    
    override fun get(index: Int): T {
        return delegate[index]
    }
    
    override fun add(index: Int, element: T) {
        delegate.add(index, element)
        notifyListeners(ListChange.Added(index, element))
    }
    
    override fun removeAt(index: Int): T {
        val element = delegate.removeAt(index)
        notifyListeners(ListChange.Removed(index, element))
        return element
    }
    
    override fun set(index: Int, element: T): T {
        val oldElement = delegate.set(index, element)
        notifyListeners(ListChange.Updated(index, oldElement, element))
        return oldElement
    }
    
    private fun notifyListeners(change: ListChange<T>) {
        listeners.forEach { it.onListChanged(change) }
    }
}

interface ListChangeListener<T> {
    fun onListChanged(change: ListChange<T>)
}

sealed class ListChange<T> {
    data class Added<T>(val index: Int, val element: T) : ListChange<T>()
    data class Removed<T>(val index: Int, val element: T) : ListChange<T>()
    data class Updated<T>(val index: Int, val oldElement: T, val newElement: T) : ListChange<T>()
}

// 使用
fun main() {
    val list = ObservableList<String>()
    
    list.addListener(object : ListChangeListener<String> {
        override fun onListChanged(change: ListChange<String>) {
            when (change) {
                is ListChange.Added -> println("Added ${change.element} at index ${change.index}")
                is ListChange.Removed -> println("Removed ${change.element} from index ${change.index}")
                is ListChange.Updated -> println("Updated index ${change.index}: ${change.oldElement} -> ${change.newElement}")
            }
        }
    })
    
    list.add("Hello")      // Added Hello at index 0
    list.add("World")      // Added World at index 1
    list[0] = "Hi"         // Updated index 0: Hello -> Hi
    list.removeAt(1)       // Removed World from index 1
}
```

## 自定义集合实现

### 实现自定义 Set

```kotlin
class OrderedSet<T>(
    private val delegate: MutableSet<T> = LinkedHashSet()
) : MutableSet<T> by delegate {
    
    private val order = mutableListOf<T>()
    
    override fun add(element: T): Boolean {
        val added = delegate.add(element)
        if (added) {
            order.add(element)
        }
        return added
    }
    
    override fun remove(element: T): Boolean {
        val removed = delegate.remove(element)
        if (removed) {
            order.remove(element)
        }
        return removed
    }
    
    override fun clear() {
        delegate.clear()
        order.clear()
    }
    
    fun get(index: Int): T {
        return order[index]
    }
    
    fun indexOf(element: T): Int {
        return order.indexOf(element)
    }
    
    fun toOrderedList(): List<T> {
        return order.toList()
    }
}

// 使用
fun main() {
    val orderedSet = OrderedSet<String>()
    
    orderedSet.add("apple")
    orderedSet.add("banana")
    orderedSet.add("cherry")
    orderedSet.add("apple")  // 重复元素，不会添加
    
    println("Ordered list: ${orderedSet.toOrderedList()}")
    // [apple, banana, cherry]
    
    println("Element at index 1: ${orderedSet.get(1)}")
    // banana
}
```

### 实现自定义 Map

```kotlin
class CaseInsensitiveMap<V>(
    private val delegate: MutableMap<String, V> = mutableMapOf()
) : MutableMap<String, V> by delegate {
    
    override fun containsKey(key: String): Boolean {
        return delegate.containsKey(key.lowercase())
    }
    
    override fun get(key: String): V? {
        return delegate[key.lowercase()]
    }
    
    override fun put(key: String, value: V): V? {
        return delegate.put(key.lowercase(), value)
    }
    
    override fun remove(key: String): V? {
        return delegate.remove(key.lowercase())
    }
    
    override fun putAll(from: Map<out String, V>) {
        from.forEach { (key, value) ->
            put(key, value)
        }
    }
}

// 使用
fun main() {
    val map = CaseInsensitiveMap<String>()
    
    map["Hello"] = "World"
    map["HELLO"] = "Kotlin"  // 会覆盖之前的值
    
    println("hello: ${map["hello"]}")    // Kotlin
    println("HELLO: ${map["HELLO"]}")    // Kotlin
    println("HeLLo: ${map["HeLLo"]}")    // Kotlin
}
```

### 实现自定义队列

```kotlin
class CircularQueue<T>(private val capacity: Int) {
    private val elements = arrayOfNulls<Any?>(capacity)
    private var head = 0
    private var tail = 0
    private var size = 0
    
    fun enqueue(element: T): Boolean {
        if (isFull()) return false
        
        elements[tail] = element
        tail = (tail + 1) % capacity
        size++
        return true
    }
    
    fun dequeue(): T? {
        if (isEmpty()) return null
        
        val element = elements[head] as T
        elements[head] = null
        head = (head + 1) % capacity
        size--
        return element
    }
    
    fun peek(): T? {
        if (isEmpty()) return null
        return elements[head] as T
    }
    
    fun isEmpty(): Boolean = size == 0
    
    fun isFull(): Boolean = size == capacity
    
    fun size(): Int = size
    
    fun toList(): List<T> {
        val result = mutableListOf<T>()
        var current = head
        repeat(size) {
            result.add(elements[current] as T)
            current = (current + 1) % capacity
        }
        return result
    }
}

// 使用
fun main() {
    val queue = CircularQueue<Int>(3)
    
    queue.enqueue(1)
    queue.enqueue(2)
    queue.enqueue(3)
    println("Enqueue 4: ${queue.enqueue(4)}")  // false (队列已满)
    
    println("Dequeue: ${queue.dequeue()}")     // 1
    println("Peek: ${queue.peek()}")           // 2
    
    queue.enqueue(4)
    println("Queue: ${queue.toList()}")        // [2, 3, 4]
}
```

## 运算符重载

### 基本运算符

```kotlin
class Vector2D(val x: Double, val y: Double) {
    // 加法运算符
    operator fun plus(other: Vector2D): Vector2D {
        return Vector2D(x + other.x, y + other.y)
    }
    
    // 减法运算符
    operator fun minus(other: Vector2D): Vector2D {
        return Vector2D(x - other.x, y - other.y)
    }
    
    // 乘法运算符（标量乘法）
    operator fun times(scalar: Double): Vector2D {
        return Vector2D(x * scalar, y * scalar)
    }
    
    // 除法运算符（标量除法）
    operator fun div(scalar: Double): Vector2D {
        return Vector2D(x / scalar, y / scalar)
    }
    
    // 取反运算符
    operator fun unaryMinus(): Vector2D {
        return Vector2D(-x, -y)
    }
    
    override fun toString(): String = "Vector2D($x, $y)"
}

// 使用
fun main() {
    val v1 = Vector2D(1.0, 2.0)
    val v2 = Vector2D(3.0, 4.0)
    
    println("v1 + v2 = ${v1 + v2}")      // Vector2D(4.0, 6.0)
    println("v1 - v2 = ${v1 - v2}")      // Vector2D(-2.0, -2.0)
    println("v1 * 2 = ${v1 * 2.0}")      // Vector2D(2.0, 4.0)
    println("v1 / 2 = ${v1 / 2.0}")      // Vector2D(0.5, 1.0)
    println("-v1 = ${-v1}")              // Vector2D(-1.0, -2.0)
}
```

### 索引运算符

```kotlin
class Matrix(private val rows: Int, private val cols: Int) {
    private val data = Array(rows) { DoubleArray(cols) }
    
    // 索引访问运算符
    operator fun get(row: Int, col: Int): Double {
        return data[row][col]
    }
    
    // 索引设置运算符
    operator fun set(row: Int, col: Int, value: Double) {
        data[row][col] = value
    }
    
    // 矩阵加法
    operator fun plus(other: Matrix): Matrix {
        require(rows == other.rows && cols == other.cols)
        val result = Matrix(rows, cols)
        for (i in 0 until rows) {
            for (j in 0 until cols) {
                result[i, j] = this[i, j] + other[i, j]
            }
        }
        return result
    }
    
    // 矩阵乘法
    operator fun times(other: Matrix): Matrix {
        require(cols == other.rows)
        val result = Matrix(rows, other.cols)
        for (i in 0 until rows) {
            for (j in 0 until other.cols) {
                var sum = 0.0
                for (k in 0 until cols) {
                    sum += this[i, k] * other[k, j]
                }
                result[i, j] = sum
            }
        }
        return result
    }
    
    override fun toString(): String {
        return data.joinToString("\n") { row ->
            row.joinToString(" ", "[", "]")
        }
    }
}

// 使用
fun main() {
    val m1 = Matrix(2, 2)
    m1[0, 0] = 1.0
    m1[0, 1] = 2.0
    m1[1, 0] = 3.0
    m1[1, 1] = 4.0
    
    val m2 = Matrix(2, 2)
    m2[0, 0] = 5.0
    m2[0, 1] = 6.0
    m2[1, 0] = 7.0
    m2[1, 1] = 8.0
    
    println("Matrix 1:")
    println(m1)
    
    println("\nMatrix 2:")
    println(m2)
    
    println("\nMatrix 1 + Matrix 2:")
    println(m1 + m2)
    
    println("\nMatrix 1 * Matrix 2:")
    println(m1 * m2)
}
```

### 迭代器运算符

```kotlin
class Range<T : Comparable<T>>(
    private val start: T,
    private val end: T,
    private val step: (T) -> T
) : Iterable<T> {
    
    override fun iterator(): Iterator<T> {
        return object : Iterator<T> {
            private var current = start
            
            override fun hasNext(): Boolean {
                return current <= end
            }
            
            override fun next(): T {
                val result = current
                current = step(current)
                return result
            }
        }
    }
}

// 使用
fun main() {
    val intRange = Range(1, 10) { it + 2 }
    println("Int range: ${intRange.toList()}")
    // [1, 3, 5, 7, 9]
    
    val doubleRange = Range(0.0, 1.0) { it + 0.1 }
    println("Double range: ${doubleRange.toList()}")
    // [0.0, 0.1, 0.2, 0.30000000000000004, 0.4, 0.5, 0.6, 0.7, 0.7999999999999999, 0.8999999999999999, 0.9999999999999999]
}
```

## 委托模式

### 使用委托简化实现

```kotlin
class LoggingList<T>(
    private val delegate: MutableList<T> = mutableListOf()
) : MutableList<T> by delegate {
    
    private val logger = mutableListOf<String>()
    
    override fun add(element: T): Boolean {
        log("add($element)")
        return delegate.add(element)
    }
    
    override fun remove(element: T): Boolean {
        log("remove($element)")
        return delegate.remove(element)
    }
    
    override fun add(index: Int, element: T) {
        log("add($index, $element)")
        delegate.add(index, element)
    }
    
    override fun removeAt(index: Int): T {
        log("removeAt($index)")
        return delegate.removeAt(index)
    }
    
    private fun log(message: String) {
        logger.add("[${System.currentTimeMillis()}] $message")
    }
    
    fun getLog(): List<String> = logger.toList()
}

// 使用
fun main() {
    val list = LoggingList<String>()
    
    list.add("Hello")
    list.add("World")
    list.remove("Hello")
    
    println("List: $list")
    println("Log:")
    list.getLog().forEach { println(it) }
}
```

### 属性委托

```kotlin
import kotlin.reflect.KProperty

class ListProperty<T>(private val list: MutableList<T> = mutableListOf()) {
    operator fun getValue(thisRef: Any?, property: KProperty<*>): MutableList<T> {
        return list
    }
    
    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: List<T>) {
        list.clear()
        list.addAll(value)
    }
}

class Example {
    var items: MutableList<String> by ListProperty()
}

// 使用
fun main() {
    val example = Example()
    
    example.items.add("Hello")
    example.items.add("World")
    
    println("Items: ${example.items}")
    // [Hello, World]
    
    example.items = listOf("New", "Items")
    println("Items: ${example.items}")
    // [New, Items]
}
```

## 最佳实践

### 1. 保持扩展函数的职责单一

```kotlin
// 推荐：每个扩展函数只做一件事
fun <T> List<T>.secondOrNull(): T? {
    return if (this.size >= 2) this[1] else null
}

fun <T> List<T>.second(): T {
    return this[1] ?: throw NoSuchElementException("List has less than 2 elements")
}

// 不推荐：一个函数做太多事情
fun <T> List<T>.getElement(index: Int, default: T? = null): T? {
    return if (index in this.indices) this[index] else default
}
```

### 2. 使用泛型约束提高类型安全

```kotlin
// 推荐：使用泛型约束
fun <T : Comparable<T>> List<T>.sortedDescending(): List<T> {
    return this.sortedDescending()
}

// 不推荐：没有类型约束
fun <T> List<T>.sortedDescending(): List<T> {
    // 编译错误或运行时错误
}
```

### 3. 提供合理的默认值

```kotlin
// 推荐：提供合理的默认值
fun <T> List<T>.joinToString(
    separator: String = ", ",
    prefix: String = "",
    postfix: String = ""
): String {
    return this.joinToString(separator, prefix, postfix)
}

// 不推荐：没有默认值
fun <T> List<T>.joinToString(
    separator: String,
    prefix: String,
    postfix: String
): String {
    return this.joinToString(separator, prefix, postfix)
}
```

### 4. 文档化扩展函数

```kotlin
/**
 * 返回列表中的第二个元素。
 *
 * @return 列表中的第二个元素
 * @throws NoSuchElementException 如果列表包含少于 2 个元素
 */
fun <T> List<T>.second(): T {
    if (this.size < 2) {
        throw NoSuchElementException("List has less than 2 elements")
    }
    return this[1]
}

/**
 * 返回列表中的第二个元素，如果列表包含少于 2 个元素则返回 null。
 *
 * @return 列表中的第二个元素，如果不存在则返回 null
 */
fun <T> List<T>.secondOrNull(): T? {
    return if (this.size >= 2) this[1] else null
}
```

### 5. 避免扩展函数与成员函数冲突

```kotlin
class MyClass {
    fun print() {
        println("Member function")
    }
}

// 不推荐：与成员函数同名
fun MyClass.print() {
    println("Extension function")  // 永远不会被调用
}

// 推荐：使用不同的名称
fun MyClass.printWithPrefix(prefix: String) {
    println("$prefix: Member function")
}
```

### 6. 使用扩展属性简化常见操作

```kotlin
// 推荐：使用扩展属性
val <T> List<T>.secondOrNull: T?
    get() = if (this.size >= 2) this[1] else null

// 使用
val list = listOf(1, 2, 3, 4, 5)
println(list.secondOrNull)  // 2
```

## 常见问题与解决方案

### 1. 扩展函数无法访问私有成员

**问题**：扩展函数无法访问类的私有成员

**解决方案**：
- 使用公共 API
- 将扩展函数定义在同一个文件中（可以访问同一文件中的私有成员）
- 使用成员函数代替扩展函数

### 2. 扩展函数的导入问题

**问题**：扩展函数需要显式导入

**解决方案**：
- 使用 `import` 语句导入扩展函数
- 将扩展函数定义在常用的包中
- 使用 IDE 的自动导入功能

### 3. 扩展函数的性能问题

**问题**：扩展函数可能有性能开销

**解决方案**：
- 使用 `inline` 关键字优化扩展函数
- 避免在扩展函数中创建不必要的对象
- 使用性能分析工具检测性能瓶颈

### 4. 扩展函数的命名冲突

**问题**：不同包中的扩展函数可能同名

**解决方案**：
- 使用有意义的函数名
- 使用包名作为前缀
- 使用 `as` 关键字重命名导入

```kotlin
import com.example.extensions.second as secondElement

val list = listOf(1, 2, 3)
println(list.secondElement())
```

### 5. 扩展函数的可空性

**问题**：扩展函数的可空性处理

**解决方案**：
- 使用可空类型接收者
- 使用非空类型接收者并处理空值

```kotlin
// 可空类型接收者
fun <T> List<T>?.secondOrNull(): T? {
    if (this == null || this.size < 2) return null
    return this[1]
}

// 非空类型接收者
fun <T> List<T>.second(): T {
    if (this.size < 2) {
        throw NoSuchElementException("List has less than 2 elements")
    }
    return this[1]
}
```

## 总结

Kotlin 的扩展机制为集合类型提供了强大的定制能力：

1. **扩展函数**：为现有类添加新功能，无需继承
2. **扩展属性**：为现有类添加新属性
3. **重写 API**：通过继承和委托自定义集合行为
4. **运算符重载**：为集合定义自定义运算符
5. **委托模式**：简化集合实现，避免样板代码

**核心要点**：
- 保持扩展函数的职责单一
- 使用泛型约束提高类型安全
- 提供合理的默认值
- 文档化扩展函数
- 避免与成员函数冲突
- 考虑性能和可维护性

通过合理使用这些技术，可以创建更加灵活、可读和可维护的 Kotlin 代码，同时保持与标准库的一致性和兼容性。