---
title: Kotlin 协程安全列表详解
date: 2026-03-19
footer: Trae编辑
---


## 目录

1. [协程安全概述](#协程安全概述)
2. [协程安全列表的实现方法](#协程安全列表的实现方法)
3. [使用 Mutex 实现协程安全列表](#使用-mutex-实现协程安全列表)
4. [使用 Channel 作为协程安全队列](#使用-channel-作为协程安全队列)
5. [使用 Flow 处理数据流](#使用-flow-处理数据流)
6. [使用 AtomicReference 实现协程安全列表](#使用-atomicreference-实现协程安全列表)
7. [使用 synchronized 块](#使用-synchronized-块)
8. [第三方库支持](#第三方库支持)
9. [最佳实践](#最佳实践)
10. [性能考虑](#性能考虑)
11. [常见问题与解决方案](#常见问题与解决方案)
12. [总结](#总结)

## 协程安全概述

**协程安全**是指在多协程并发环境下，数据结构或操作能够正确处理并发访问，避免竞态条件和数据不一致的问题。

**注意**：Kotlin 标准库中的大部分集合类型（如 `ArrayList`、`LinkedList` 等）都不是协程安全的，它们在多协程环境下使用时需要额外的同步措施。

**协程安全 vs 线程安全**：
- **线程安全**：保护多个线程同时访问共享数据
- **协程安全**：保护多个协程同时访问共享数据，即使它们在同一个线程上执行

## 协程安全列表的实现方法

Kotlin 中实现协程安全列表的主要方法有：

1. **Mutex**：协程互斥锁，用于保护临界区
2. **Channel**：协程通道，可作为安全的队列使用
3. **Flow**：冷流，用于处理异步数据流
4. **AtomicReference**：原子引用，用于原子更新操作
5. **synchronized**：传统的线程同步机制
6. **第三方库**：如 `kotlinx-collections-immutable` 等

## 使用 Mutex 实现协程安全列表

`Mutex` 是 Kotlin 协程中最常用的同步原语，用于保护临界区。

### 基本实现

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

class CoroutineSafeList<T> {
    private val list = mutableListOf<T>()
    private val mutex = Mutex()
    
    suspend fun add(element: T) {
        mutex.withLock {
            list.add(element)
        }
    }
    
    suspend fun remove(element: T): Boolean {
        return mutex.withLock {
            list.remove(element)
        }
    }
    
    suspend fun get(index: Int): T? {
        return mutex.withLock {
            if (index in list.indices) list[index] else null
        }
    }
    
    suspend fun size(): Int {
        return mutex.withLock {
            list.size
        }
    }
    
    suspend fun clear() {
        mutex.withLock {
            list.clear()
        }
    }
    
    suspend fun forEach(action: suspend (T) -> Unit) {
        mutex.withLock {
            list.forEach { action(it) }
        }
    }
}

// 使用示例
fun main() = runBlocking {
    val safeList = CoroutineSafeList<Int>()
    
    // 启动多个协程并发操作
    val jobs = List(100) { i ->
        launch(Dispatchers.Default) {
            safeList.add(i)
            println("Added $i")
            
            if (i % 10 == 0) {
                val size = safeList.size()
                println("Current size: $size")
            }
        }
    }
    
    jobs.forEach { it.join() }
    println("Final size: ${safeList.size()}")
}
```

### 扩展功能

```kotlin
class CoroutineSafeList<T> {
    // 基础实现...
    
    suspend fun addAll(elements: Collection<T>) {
        mutex.withLock {
            list.addAll(elements)
        }
    }
    
    suspend fun removeAll(elements: Collection<T>): Boolean {
        return mutex.withLock {
            list.removeAll(elements)
        }
    }
    
    suspend fun retainAll(elements: Collection<T>): Boolean {
        return mutex.withLock {
            list.retainAll(elements)
        }
    }
    
    suspend fun contains(element: T): Boolean {
        return mutex.withLock {
            list.contains(element)
        }
    }
    
    suspend fun containsAll(elements: Collection<T>): Boolean {
        return mutex.withLock {
            list.containsAll(elements)
        }
    }
    
    suspend fun isEmpty(): Boolean {
        return mutex.withLock {
            list.isEmpty()
        }
    }
    
    suspend fun toList(): List<T> {
        return mutex.withLock {
            list.toList()
        }
    }
}
```

### 读写锁优化

对于读多写少的场景，可以使用 `ReadWriteMutex` 提高性能：

```kotlin
import kotlinx.coroutines.sync.ReadWriteMutex
import kotlinx.coroutines.sync.read
import kotlinx.coroutines.sync.write

class CoroutineSafeList<T> {
    private val list = mutableListOf<T>()
    private val mutex = ReadWriteMutex()
    
    suspend fun add(element: T) {
        mutex.write {
            list.add(element)
        }
    }
    
    suspend fun get(index: Int): T? {
        return mutex.read {
            if (index in list.indices) list[index] else null
        }
    }
    
    suspend fun size(): Int {
        return mutex.read {
            list.size
        }
    }
    
    // 其他方法...
}
```

## 使用 Channel 作为协程安全队列

`Channel` 是 Kotlin 协程中的通道，天然支持协程安全的元素传递。

### 基本用法

```kotlin
import kotlinx.coroutines.Channel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    // 创建一个无缓冲通道
    val channel = Channel<Int>()
    
    // 生产者协程
    launch(Dispatchers.Default) {
        repeat(10) {
            println("Producing $it")
            channel.send(it)  // 发送元素
            delay(100)  // 模拟生产延迟
        }
        channel.close()  // 关闭通道
    }
    
    // 消费者协程
    launch(Dispatchers.Default) {
        for (element in channel) {
            println("Consumed $element")
            delay(200)  // 模拟消费延迟
        }
        println("Channel closed")
    }
    
    // 等待所有协程完成
    delay(2000)
}
```

### 有缓冲通道

```kotlin
// 创建有缓冲通道
val channel = Channel<Int>(capacity = 5)

// 或者使用无限缓冲
val unlimitedChannel = Channel<Int>(Channel.UNLIMITED)

// 或者使用基于数组的缓冲
val arrayChannel = Channel<Int>(Channel.BUFFERED)
```

### 作为队列使用

```kotlin
class CoroutineQueue<T> {
    private val channel = Channel<T>()
    
    suspend fun enqueue(element: T) {
        channel.send(element)
    }
    
    suspend fun dequeue(): T {
        return channel.receive()
    }
    
    suspend fun tryDequeue(): T? {
        return channel.tryReceive().getOrNull()
    }
    
    fun close() {
        channel.close()
    }
    
    val isClosedForSend: Boolean
        get() = channel.isClosedForSend
    
    val isClosedForReceive: Boolean
        get() = channel.isClosedForReceive
}

// 使用示例
fun main() = runBlocking {
    val queue = CoroutineQueue<Int>()
    
    // 生产者
    launch { 
        repeat(5) { 
            queue.enqueue(it)
            println("Enqueued $it")
        }
        queue.close()
    }
    
    // 消费者
    launch { 
        while (!queue.isClosedForReceive) {
            val element = queue.tryDequeue()
            if (element != null) {
                println("Dequeued $element")
            } else {
                delay(50)
            }
        }
    }
    
    delay(1000)
}
```

## 使用 Flow 处理数据流

`Flow` 是 Kotlin 协程中的冷流，用于处理异步数据流。

### 基本用法

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.asFlow
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.flow.filter
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    // 从列表创建 Flow
    val flow: Flow<Int> = (1..10).asFlow()
    
    // 处理流
    launch(Dispatchers.Default) {
        flow
            .filter { it % 2 == 0 }  // 过滤偶数
            .map { it * 2 }  // 映射为原来的两倍
            .collect { println("Processed: $it") }  // 收集结果
    }
    
    delay(1000)
}
```

### 热流

对于需要多个消费者的场景，可以使用 `SharedFlow`：

```kotlin
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    // 创建热流
    val sharedFlow = MutableSharedFlow<Int>()
    
    // 消费者 1
    launch(Dispatchers.Default) {
        sharedFlow.collect {
            println("Consumer 1: $it")
        }
    }
    
    // 消费者 2
    launch(Dispatchers.Default) {
        sharedFlow.collect {
            println("Consumer 2: $it")
        }
    }
    
    // 生产者
    launch(Dispatchers.Default) {
        repeat(5) {
            sharedFlow.emit(it)
            delay(100)
        }
    }
    
    delay(1000)
}
```

### 状态流

对于需要保持最新状态的场景，可以使用 `StateFlow`：

```kotlin
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    // 创建状态流
    val stateFlow = MutableStateFlow(0)
    
    // 消费者
    launch(Dispatchers.Default) {
        stateFlow.collect {
            println("Current state: $it")
        }
    }
    
    // 更新状态
    launch(Dispatchers.Default) {
        repeat(5) {
            stateFlow.value = it
            delay(100)
        }
    }
    
    delay(1000)
}
```

## 使用 AtomicReference 实现协程安全列表

`AtomicReference` 可以用于原子性地更新列表引用。

### 基本实现

```kotlin
import kotlin.concurrent.atomic.AtomicReference
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

class AtomicList<T> {
    private val listRef = AtomicReference(mutableListOf<T>())
    
    fun add(element: T): Boolean {
        do {
            val currentList = listRef.value
            val newList = currentList.toMutableList()
            val result = newList.add(element)
        } while (!listRef.compareAndSet(currentList, newList))
        return result
    }
    
    fun remove(element: T): Boolean {
        do {
            val currentList = listRef.value
            val newList = currentList.toMutableList()
            val result = newList.remove(element)
        } while (!listRef.compareAndSet(currentList, newList))
        return result
    }
    
    fun get(index: Int): T? {
        return listRef.value.getOrNull(index)
    }
    
    fun size(): Int {
        return listRef.value.size
    }
    
    fun toList(): List<T> {
        return listRef.value.toList()
    }
}

// 使用示例
fun main() = runBlocking {
    val atomicList = AtomicList<Int>()
    
    val jobs = List(100) { i ->
        launch(Dispatchers.Default) {
            atomicList.add(i)
            if (i % 10 == 0) {
                println("Size: ${atomicList.size()}")
            }
        }
    }
    
    jobs.forEach { it.join() }
    println("Final size: ${atomicList.size()}")
}
```

### 注意事项

- `AtomicReference` 方法适用于读多写少的场景
- 每次修改都会创建新的列表副本，可能会有性能开销
- 不适合大型列表或频繁修改的场景

## 使用 synchronized 块

传统的 `synchronized` 块也可以用于协程环境，但需要注意协程挂起的问题。

### 基本用法

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

class SynchronizedList<T> {
    private val list = mutableListOf<T>()
    private val lock = Any()
    
    fun add(element: T) {
        synchronized(lock) {
            list.add(element)
        }
    }
    
    fun remove(element: T): Boolean {
        synchronized(lock) {
            return list.remove(element)
        }
    }
    
    fun get(index: Int): T? {
        synchronized(lock) {
            return if (index in list.indices) list[index] else null
        }
    }
    
    fun size(): Int {
        synchronized(lock) {
            return list.size
        }
    }
}

// 使用示例
fun main() = runBlocking {
    val syncList = SynchronizedList<Int>()
    
    val jobs = List(100) { i ->
        launch(Dispatchers.Default) {
            syncList.add(i)
            if (i % 10 == 0) {
                println("Size: ${syncList.size()}")
            }
        }
    }
    
    jobs.forEach { it.join() }
    println("Final size: ${syncList.size()}")
}
```

### 注意事项

- `synchronized` 块会阻塞线程，可能影响协程的性能
- 不应该在 `synchronized` 块中执行可能挂起的操作
- 适合简单的同步场景，复杂场景推荐使用 `Mutex`

## 第三方库支持

### kotlinx-collections-immutable

```kotlin
// build.gradle.kts
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-collections-immutable:0.3.6")
}

// 使用示例
import kotlinx.collections.immutable.PersistentList
import kotlinx.collections.immutable.persistentListOf
import kotlinx.collections.immutable.toPersistentList
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    var list: PersistentList<Int> = persistentListOf()
    
    val jobs = List(100) { i ->
        launch(Dispatchers.Default) {
            // 原子更新
            list = list.add(i)
            if (i % 10 == 0) {
                println("Size: ${list.size}")
            }
        }
    }
    
    jobs.forEach { it.join() }
    println("Final size: ${list.size}")
}
```

### ConcurrentHashMap 作为列表

```kotlin
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

class ConcurrentList<T> {
    private val map = ConcurrentHashMap<Int, T>()
    private var counter = 0
    
    fun add(element: T): Boolean {
        val index = counter++
        map[index] = element
        return true
    }
    
    fun remove(element: T): Boolean {
        val entry = map.entries.find { it.value == element }
        return entry?.let { map.remove(it.key) != null } ?: false
    }
    
    fun get(index: Int): T? {
        return map[index]
    }
    
    fun size(): Int {
        return map.size
    }
    
    fun toList(): List<T> {
        return map.values.toList()
    }
}

// 使用示例
fun main() = runBlocking {
    val concurrentList = ConcurrentList<Int>()
    
    val jobs = List(100) { i ->
        launch(Dispatchers.Default) {
            concurrentList.add(i)
            if (i % 10 == 0) {
                println("Size: ${concurrentList.size()}")
            }
        }
    }
    
    jobs.forEach { it.join() }
    println("Final size: ${concurrentList.size()}")
}
```

## 最佳实践

### 1. 根据场景选择合适的实现

| 场景 | 推荐实现 | 理由 |
|------|----------|------|
| 读多写少 | `ReadWriteMutex` | 允许多个读操作并发执行 |
| 队列操作 | `Channel` | 天然支持生产者-消费者模式 |
| 数据流处理 | `Flow` | 支持复杂的流操作和转换 |
| 简单场景 | `synchronized` | 实现简单，易于理解 |
| 原子更新 | `AtomicReference` | 无锁实现，性能较好 |

### 2. 避免在同步块中执行挂起操作

```kotlin
// 不推荐
mutex.withLock {
    // 执行可能挂起的操作
    delay(100)  // 挂起会阻塞其他协程
    list.add(element)
}

// 推荐
val processedElement = processElement(element)  // 在同步块外处理
mutex.withLock {
    list.add(processedElement)  // 快速操作
}
```

### 3. 合理使用协程调度器

```kotlin
// CPU 密集型操作
launch(Dispatchers.Default) {
    // 处理数据
}

// IO 密集型操作
launch(Dispatchers.IO) {
    // 网络请求、文件操作
}

// UI 操作（Android）
launch(Dispatchers.Main) {
    // 更新 UI
}
```

### 4. 实现适当的错误处理

```kotlin
suspend fun safeOperation() {
    try {
        mutex.withLock {
            // 操作列表
        }
    } catch (e: Exception) {
        // 处理异常
        println("Error: ${e.message}")
    }
}
```

### 5. 考虑使用封装类

```kotlin
class SafeList<T> {
    private val list = mutableListOf<T>()
    private val mutex = Mutex()
    
    suspend fun add(element: T) = mutex.withLock { list.add(element) }
    suspend fun remove(element: T) = mutex.withLock { list.remove(element) }
    suspend fun get(index: Int) = mutex.withLock { list.getOrNull(index) }
    suspend fun size() = mutex.withLock { list.size }
    suspend fun toList() = mutex.withLock { list.toList() }
    // 其他方法...
}
```

## 性能考虑

### 1. 锁竞争

- **减少锁的范围**：只在必要时使用锁
- **减少锁的持有时间**：快速完成临界区操作
- **使用细粒度锁**：不同部分使用不同的锁

### 2. 内存开销

- `AtomicReference` 每次修改都会创建新的列表副本
- `Channel` 有缓冲区开销
- `Mutex` 有协程调度开销

### 3. 并发性能

```kotlin
// 性能测试
fun measurePerformance(operation: suspend () -> Unit) {
    val startTime = System.currentTimeMillis()
    runBlocking { operation() }
    val endTime = System.currentTimeMillis()
    println("Execution time: ${endTime - startTime}ms")
}

// 测试不同实现的性能
fun main() {
    measurePerformance {
        // 测试 Mutex 实现
        val safeList = CoroutineSafeList<Int>()
        repeat(10000) { safeList.add(it) }
    }
    
    measurePerformance {
        // 测试 AtomicReference 实现
        val atomicList = AtomicList<Int>()
        repeat(10000) { atomicList.add(it) }
    }
    
    measurePerformance {
        // 测试 synchronized 实现
        val syncList = SynchronizedList<Int>()
        repeat(10000) { syncList.add(it) }
    }
}
```

### 4. 可扩展性

- 考虑使用无锁数据结构
- 考虑分片锁（分段锁）
- 考虑使用 actor 模式

## 常见问题与解决方案

### 1. 死锁

**问题**：多个协程相互等待对方释放锁

**解决方案**：
- 始终以相同的顺序获取多个锁
- 使用 `withTimeout` 避免长时间等待
- 避免嵌套锁

### 2. 竞态条件

**问题**：多个协程同时修改数据导致不一致

**解决方案**：
- 确保所有修改操作都是原子的
- 使用合适的同步机制
- 避免在多个地方修改同一数据

### 3. 内存泄漏

**问题**：协程持有锁但未释放

**解决方案**：
- 使用 `try-finally` 确保锁释放
- 使用 `withLock` 自动释放锁
- 避免在锁内使用可能抛出异常的操作

### 4. 性能瓶颈

**问题**：同步操作成为性能瓶颈

**解决方案**：
- 分析性能瓶颈
- 优化临界区代码
- 考虑使用更高效的同步机制
- 考虑使用并发数据结构

### 5. 协程挂起问题

**问题**：在同步块中执行挂起操作

**解决方案**：
- 避免在 `synchronized` 块中执行挂起操作
- 使用 `Mutex` 而不是 `synchronized`
- 将挂起操作移到同步块外

## 总结

Kotlin 中实现协程安全列表的主要方法包括：

1. **Mutex**：最常用的协程同步原语，适合大多数场景
2. **Channel**：天然支持生产者-消费者模式，适合队列操作
3. **Flow**：适合处理异步数据流，支持复杂的流操作
4. **AtomicReference**：无锁实现，适合读多写少的场景
5. **synchronized**：传统的线程同步机制，适合简单场景
6. **第三方库**：如 `kotlinx-collections-immutable` 提供的不可变集合

**核心要点**：
- 选择适合具体场景的实现方式
- 避免在同步块中执行挂起操作
- 合理使用协程调度器
- 实现适当的错误处理
- 考虑性能和可扩展性
- 遵循最佳实践，确保代码的可读性和可维护性

通过合理选择和使用这些方法，可以在 Kotlin 协程环境中安全、高效地处理列表操作，避免并发问题，提高应用的可靠性和性能。