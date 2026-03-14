---
title: Kotlin 并发同步与原子操作
date: 2026-03-13
footer: Trae编辑
---


## 目录

1. [同步基础](#同步基础)
2. [synchronized 关键字](#synchronized-关键字)
3. [ReentrantLock](#reentrantlock)
4. [ReadWriteLock](#readwritelock)
5. [原子值操作](#原子值操作)
6. [与 Kotlinx 协程配合](#与-kotlinx-协程配合)
7. [高级同步模式](#高级同步模式)
8. [性能优化与最佳实践](#性能优化与最佳实践)

## 同步基础

### 并发问题概述

在 Kotlin 中，多线程并发访问共享数据时可能遇到以下问题：

| 问题 | 描述 | 解决方案 |
|------|------|---------|
| 竞态条件 | 多个线程同时读写数据导致结果不确定 | 同步机制、原子操作 |
| 死锁 | 线程互相等待对方释放资源 | 避免嵌套锁、超时机制 |
| 活锁 | 线程不断改变状态但无法继续执行 | 引入随机等待 |
| 饥饿 | 某些线程长期无法获得资源 | 公平锁 |

### Kotlin 同步工具概览

```kotlin
// Java 并发工具（Kotlin 完全兼容）
import java.util.concurrent.locks.ReentrantLock
import java.util.concurrent.locks.ReentrantReadWriteLock
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.CountDownLatch
import java.util.concurrent.CyclicBarrier
import java.util.concurrent.Semaphore

// Kotlin 协程同步工具
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.Semaphore as CoroutineSemaphore
import kotlinx.coroutines.channels.Channel
```

## synchronized 关键字

### 基本用法

```kotlin
class Counter {
    private var count = 0
    private val lock = Any()
    
    // 使用 synchronized 代码块
    fun increment() {
        synchronized(lock) {
            count++
        }
    }
    
    fun getCount(): Int {
        return synchronized(lock) {
            count
        }
    }
}

// 使用 @Synchronized 注解（方法级别）
class SynchronizedCounter {
    private var count = 0
    
    @Synchronized
    fun increment() {
        count++
    }
    
    @Synchronized
    fun getCount(): Int = count
}
```

### 高级 synchronized 用法

```kotlin
class BankAccount {
    private var balance = 0.0
    private val lock = Any()
    
    // 条件同步
    fun withdraw(amount: Double): Boolean {
        return synchronized(lock) {
            if (balance >= amount) {
                balance -= amount
                true
            } else {
                false
            }
        }
    }
    
    fun deposit(amount: Double) {
        synchronized(lock) {
            balance += amount
            lock.notifyAll() // 通知等待的线程
        }
    }
    
    // 带超时的等待
    fun waitForBalance(minAmount: Double, timeout: Long): Boolean {
        return synchronized(lock) {
            val deadline = System.currentTimeMillis() + timeout
            while (balance < minAmount) {
                val remaining = deadline - System.currentTimeMillis()
                if (remaining <= 0) return false
                lock.wait(remaining)
            }
            true
        }
    }
}
```

## ReentrantLock

### 基本用法

```kotlin
import java.util.concurrent.locks.ReentrantLock
import kotlin.concurrent.withLock

class ReentrantLockCounter {
    private var count = 0
    private val lock = ReentrantLock()
    
    fun increment() {
        lock.withLock {
            count++
        }
    }
    
    fun getCount(): Int {
        return lock.withLock {
            count
        }
    }
}

// 手动管理锁
class ManualLockExample {
    private val lock = ReentrantLock()
    private var data = ""
    
    fun updateData(newData: String) {
        lock.lock()
        try {
            data = newData
        } finally {
            lock.unlock()
        }
    }
}
```

### 高级 ReentrantLock 特性

```kotlin
import java.util.concurrent.TimeUnit
import java.util.concurrent.locks.ReentrantLock

class AdvancedLockExample {
    private val lock = ReentrantLock()
    private val condition = lock.newCondition()
    private var ready = false
    
    // 可中断锁
    fun interruptibleOperation() {
        lock.lockInterruptibly()
        try {
            // 执行操作
        } finally {
            lock.unlock()
        }
    }
    
    // 尝试获取锁（带超时）
    fun tryOperation(timeout: Long, unit: TimeUnit): Boolean {
        if (lock.tryLock(timeout, unit)) {
            try {
                // 执行操作
                return true
            } finally {
                lock.unlock()
            }
        }
        return false
    }
    
    // 公平锁
    class FairLockExample {
        private val fairLock = ReentrantLock(true) // 公平锁
        
        fun fairOperation() {
            fairLock.withLock {
                // 按请求顺序获取锁
            }
        }
    }
    
    // 条件变量
    fun waitForCondition() {
        lock.withLock {
            while (!ready) {
                condition.await()
            }
            // 条件满足，继续执行
        }
    }
    
    fun signalCondition() {
        lock.withLock {
            ready = true
            condition.signalAll()
        }
    }
}
```

## ReadWriteLock

### 基本用法

```kotlin
import java.util.concurrent.locks.ReentrantReadWriteLock
import kotlin.concurrent.read
import kotlin.concurrent.write

class ReadWriteLockCache<K, V> {
    private val cache = mutableMapOf<K, V>()
    private val lock = ReentrantReadWriteLock()
    
    fun get(key: K): V? {
        return lock.read {
            cache[key]
        }
    }
    
    fun put(key: K, value: V) {
        lock.write {
            cache[key] = value
        }
    }
    
    fun getOrPut(key: K, defaultValue: () -> V): V {
        return lock.read {
            cache[key]
        } ?: lock.write {
            cache.getOrPut(key, defaultValue)
        }
    }
    
    fun clear() {
        lock.write {
            cache.clear()
        }
    }
}
```

### 锁降级

```kotlin
class LockDowngradeExample {
    private val lock = ReentrantReadWriteLock()
    private var data = ""
    private var cachedHash = 0
    
    fun updateAndGetHash(newData: String): Int {
        lock.write {
            data = newData
            cachedHash = data.hashCode()
            
            // 锁降级：获取读锁后再释放写锁
            val readLock = lock.readLock()
            readLock.lock()
            lock.writeLock().unlock() // 释放写锁
            
            try {
                return cachedHash
            } finally {
                readLock.unlock()
            }
        }
    }
}
```

## 原子值操作

### 基本原子类型

```kotlin
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

class AtomicExamples {
    // 原子整数
    private val atomicInt = AtomicInteger(0)
    
    fun increment() {
        atomicInt.incrementAndGet()
    }
    
    fun add(delta: Int): Int {
        return atomicInt.addAndGet(delta)
    }
    
    fun compareAndSet(expect: Int, update: Int): Boolean {
        return atomicInt.compareAndSet(expect, update)
    }
    
    // 原子布尔
    private val atomicBool = AtomicBoolean(false)
    
    fun setFlag() {
        atomicBool.set(true)
    }
    
    fun compareAndSetFlag(expect: Boolean, update: Boolean): Boolean {
        return atomicBool.compareAndSet(expect, update)
    }
    
    // 原子引用
    private val atomicRef = AtomicReference<String>("initial")
    
    fun updateRef(newValue: String): String? {
        return atomicRef.getAndSet(newValue)
    }
    
    fun compareAndUpdateRef(expect: String, update: String): Boolean {
        return atomicRef.compareAndSet(expect, update)
    }
}
```

### 原子数组

```kotlin
import java.util.concurrent.atomic.AtomicIntegerArray
import java.util.concurrent.atomic.AtomicReferenceArray

class AtomicArrayExamples {
    // 原子整数数组
    private val atomicIntArray = AtomicIntegerArray(100)
    
    fun incrementAt(index: Int): Int {
        return atomicIntArray.incrementAndGet(index)
    }
    
    fun addAt(index: Int, delta: Int): Int {
        return atomicIntArray.addAndGet(index, delta)
    }
    
    fun compareAndSetAt(index: Int, expect: Int, update: Int): Boolean {
        return atomicIntArray.compareAndSet(index, expect, update)
    }
    
    // 原子引用数组
    private val atomicRefArray = AtomicReferenceArray<String>(100)
    
    fun setAt(index: Int, value: String) {
        atomicRefArray.set(index, value)
    }
    
    fun getAndSetAt(index: Int, value: String): String? {
        return atomicRefArray.getAndSet(index, value)
    }
}
```

### 原子累加器（Java 8+）

```kotlin
import java.util.concurrent.atomic.LongAdder
import java.util.concurrent.atomic.DoubleAdder
import java.util.concurrent.atomic.LongAccumulator
import java.util.concurrent.atomic.DoubleAccumulator

class AtomicAccumulatorExamples {
    // LongAdder（高并发下性能优于 AtomicLong）
    private val longAdder = LongAdder()
    
    fun increment() {
        longAdder.increment()
    }
    
    fun add(value: Long) {
        longAdder.add(value)
    }
    
    fun getSum(): Long {
        return longAdder.sum()
    }
    
    fun reset() {
        longAdder.reset()
    }
    
    // LongAccumulator（支持自定义累加函数）
    private val maxAccumulator = LongAccumulator(Math::max, Long.MIN_VALUE)
    
    fun accumulateMax(value: Long) {
        maxAccumulator.accumulate(value)
    }
    
    fun getMax(): Long {
        return maxAccumulator.get()
    }
}
```

### 原子字段更新器

```kotlin
import java.util.concurrent.atomic.AtomicIntegerFieldUpdater
import java.util.concurrent.atomic.AtomicReferenceFieldUpdater

class AtomicFieldUpdaterExample {
    companion object {
        private val intUpdater = AtomicIntegerFieldUpdater.newUpdater(
            AtomicFieldUpdaterExample::class.java, "counter"
        )
        
        private val refUpdater = AtomicReferenceFieldUpdater.newUpdater(
            AtomicFieldUpdaterExample::class.java, String::class.java, "name"
        )
    }
    
    @Volatile
    private var counter = 0
    
    @Volatile
    private var name = ""
    
    fun incrementCounter(): Int {
        return intUpdater.incrementAndGet(this)
    }
    
    fun updateName(newName: String): String? {
        return refUpdater.getAndSet(this, newName)
    }
}
```

## 与 Kotlinx 协程配合

### Mutex（协程互斥锁）

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class CoroutineSafeCounter {
    private var count = 0
    private val mutex = Mutex()
    
    suspend fun increment() {
        mutex.withLock {
            count++
        }
    }
    
    suspend fun getCount(): Int {
        return mutex.withLock {
            count
        }
    }
}

// 使用示例
fun main() = runBlocking {
    val counter = CoroutineSafeCounter()
    
    val jobs = List(1000) {
        launch {
            repeat(100) {
                counter.increment()
            }
        }
    }
    
    jobs.joinAll()
    println("Final count: ${counter.getCount()}") // 100000
}
```

### Semaphore（协程信号量）

```kotlin
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

class CoroutineResourcePool {
    private val semaphore = Semaphore(10) // 最多10个并发
    
    suspend fun useResource(action: suspend () -> Unit) {
        semaphore.withPermit {
            action()
        }
    }
}

// 使用示例
fun main() = runBlocking {
    val pool = CoroutineResourcePool()
    
    val jobs = List(100) {
        launch {
            pool.useResource {
                println("Using resource in coroutine $it")
                delay(100)
            }
        }
    }
    
    jobs.joinAll()
}
```

### Channel（协程通信）

```kotlin
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.consumeEach
import kotlinx.coroutines.channels.produce

class CoroutineChannelExample {
    // 有缓冲通道
    private val channel = Channel<Int>(capacity = 10)
    
    suspend fun produce() {
        for (i in 1..100) {
            channel.send(i)
        }
        channel.close()
    }
    
    suspend fun consume() {
        channel.consumeEach { value ->
            println("Received: $value")
        }
    }
}

// 使用 produce 构建器
fun CoroutineScope.produceNumbers() = produce {
    for (x in 1..5) send(x * x)
}

fun CoroutineScope.launchProcessor(id: Int, channel: ReceiveChannel<Int>) = launch {
    for (msg in channel) {
        println("Processor #$id received $msg")
    }
}
```

### 原子操作与协程

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicReference

class CoroutineAtomicExample {
    private val counter = AtomicInteger(0)
    private val state = AtomicReference<State>(State.Idle)
    
    enum class State { Idle, Running, Completed }
    
    suspend fun process() {
        // 原子操作不需要 suspend，但可以在协程中使用
        if (state.compareAndSet(State.Idle, State.Running)) {
            try {
                // 执行处理
                delay(100)
                counter.incrementAndGet()
            } finally {
                state.set(State.Completed)
            }
        }
    }
    
    fun getCount(): Int = counter.get()
    fun getState(): State = state.get()
}

// 结合 Flow 使用
import kotlinx.coroutines.flow.*

class FlowAtomicExample {
    private val counter = AtomicInteger(0)
    
    fun countFlow(): Flow<Int> = flow {
        while (true) {
            emit(counter.get())
            delay(100)
        }
    }
    
    suspend fun increment() {
        counter.incrementAndGet()
    }
}
```

### Actor（协程 Actor 模式）

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class CounterMsg
object IncCounter : CounterMsg()
class GetCounter(val response: CompletableDeferred<Int>) : CounterMsg()

fun CoroutineScope.counterActor() = actor<CounterMsg> {
    var counter = 0
    for (msg in channel) {
        when (msg) {
            is IncCounter -> counter++
            is GetCounter -> msg.response.complete(counter)
        }
    }
}

// 使用示例
fun main() = runBlocking {
    val counter = counterActor()
    
    val jobs = List(1000) {
        launch {
            repeat(100) {
                counter.send(IncCounter)
            }
        }
    }
    
    jobs.joinAll()
    
    val response = CompletableDeferred<Int>()
    counter.send(GetCounter(response))
    println("Counter = ${response.await()}")
    
    counter.close()
}
```

## 高级同步模式

### 双重检查锁定

```kotlin
class DoubleCheckedLockingExample {
    @Volatile
    private var instance: ExpensiveObject? = null
    private val lock = Any()
    
    fun getInstance(): ExpensiveObject {
        // 第一次检查（无锁）
        if (instance == null) {
            synchronized(lock) {
                // 第二次检查（有锁）
                if (instance == null) {
                    instance = ExpensiveObject()
                }
            }
        }
        return instance!!
    }
}

class ExpensiveObject {
    init {
        println("ExpensiveObject created")
    }
}
```

### 分段锁

```kotlin
import java.util.concurrent.locks.ReentrantLock
import kotlin.concurrent.withLock

class StripedLockMap<K, V> {
    private val locks = Array(16) { ReentrantLock() }
    private val maps = Array(16) { mutableMapOf<K, V>() }
    
    private fun getLock(key: K): ReentrantLock {
        return locks[key.hashCode() and 0xF]
    }
    
    private fun getMap(key: K): MutableMap<K, V> {
        return maps[key.hashCode() and 0xF]
    }
    
    operator fun get(key: K): V? {
        return getLock(key).withLock {
            getMap(key)[key]
        }
    }
    
    operator fun set(key: K, value: V) {
        getLock(key).withLock {
            getMap(key)[key] = value
        }
    }
}
```

### 无锁队列

```kotlin
import java.util.concurrent.atomic.AtomicReference

class LockFreeQueue<T> {
    private class Node<T>(val value: T, val next: AtomicReference<Node<T>?> = AtomicReference(null))
    
    private val head = AtomicReference<Node<T>?>(null)
    private val tail = AtomicReference<Node<T>?>(null)
    
    init {
        val dummy = Node<T?>(null)
        head.set(dummy)
        tail.set(dummy)
    }
    
    fun enqueue(value: T) {
        val newNode = Node(value)
        while (true) {
            val currentTail = tail.get()
            val tailNext = currentTail?.next?.get()
            
            if (currentTail == tail.get()) {
                if (tailNext == null) {
                    if (currentTail?.next?.compareAndSet(null, newNode) == true) {
                        tail.compareAndSet(currentTail, newNode)
                        return
                    }
                } else {
                    tail.compareAndSet(currentTail, tailNext)
                }
            }
        }
    }
    
    fun dequeue(): T? {
        while (true) {
            val currentHead = head.get()
            val currentTail = tail.get()
            val headNext = currentHead?.next?.get()
            
            if (currentHead == head.get()) {
                if (currentHead == currentTail) {
                    if (headNext == null) return null
                    tail.compareAndSet(currentTail, headNext)
                } else {
                    val value = headNext?.value
                    if (head.compareAndSet(currentHead, headNext)) {
                        return value
                    }
                }
            }
        }
    }
}
```

### 读写锁优化模式

```kotlin
import java.util.concurrent.locks.ReentrantReadWriteLock
import kotlin.concurrent.read
import kotlin.concurrent.write

class OptimizedReadWriteCache<K, V> {
    private val cache = mutableMapOf<K, V>()
    private val lock = ReentrantReadWriteLock()
    private val stats = CacheStats()
    
    data class CacheStats(var reads: Long = 0, var writes: Long = 0, var hits: Long = 0)
    
    fun get(key: K): V? {
        return lock.read {
            stats.reads++
            val value = cache[key]
            if (value != null) stats.hits++
            value
        }
    }
    
    fun put(key: K, value: V) {
        lock.write {
            stats.writes++
            cache[key] = value
        }
    }
    
    fun getStats(): CacheStats {
        return lock.read {
            CacheStats(stats.reads, stats.writes, stats.hits)
        }
    }
    
    // 批量操作（减少锁获取次数）
    fun putAll(entries: Map<K, V>) {
        lock.write {
            cache.putAll(entries)
            stats.writes += entries.size
        }
    }
}
```

## 性能优化与最佳实践

### 同步工具选择指南

| 场景 | 推荐工具 | 说明 |
|------|---------|------|
| 简单计数 | AtomicInteger/LongAdder | 无锁，性能最好 |
| 高并发计数 | LongAdder | 分散竞争，性能优于 AtomicLong |
| 读多写少 | ReadWriteLock | 读操作并行，写操作独占 |
| 协程环境 | Mutex/Semaphore | 不阻塞线程，挂起协程 |
| 复杂状态机 | AtomicReference + CAS | 实现无锁算法 |
| 批量操作 | synchronized/ReentrantLock | 减少锁获取次数 |

### 性能对比

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.LongAdder

class PerformanceComparison {
    
    suspend fun compareAtomicVsAdder() {
        val atomic = AtomicInteger(0)
        val adder = LongAdder()
        
        // 测试 AtomicInteger
        val atomicTime = measureTimeMillis {
            coroutineScope {
                repeat(100) {
                    launch {
                        repeat(10000) {
                            atomic.incrementAndGet()
                        }
                    }
                }
            }
        }
        
        // 测试 LongAdder
        val adderTime = measureTimeMillis {
            coroutineScope {
                repeat(100) {
                    launch {
                        repeat(10000) {
                            adder.increment()
                        }
                    }
                }
            }
        }
        
        println("AtomicInteger: ${atomicTime}ms, result: ${atomic.get()}")
        println("LongAdder: ${adderTime}ms, result: ${adder.sum()}")
    }
}
```

### 最佳实践

1. **优先使用原子操作**：对于简单的计数、标志位等，使用原子类
2. **避免过度同步**：只在必要时同步，减少锁粒度
3. **使用不可变对象**：减少同步需求
4. **协程环境使用协程同步工具**：Mutex、Semaphore、Channel
5. **注意死锁**：避免嵌套锁，使用超时机制
6. **测试并发代码**：使用压力测试验证正确性

### 常见陷阱

```kotlin
// 错误：在 synchronized 块中调用外部方法
class BadExample {
    private val lock = Any()
    private var callback: (() -> Unit)? = null
    
    fun setCallback(cb: () -> Unit) {
        synchronized(lock) {
            callback = cb
        }
    }
    
    fun execute() {
        synchronized(lock) {
            callback?.invoke() // 危险：可能持有锁时调用外部代码
        }
    }
}

// 正确：减少锁持有时间
class GoodExample {
    private val lock = Any()
    @Volatile
    private var callback: (() -> Unit)? = null
    
    fun setCallback(cb: () -> Unit) {
        callback = cb // volatile 保证可见性
    }
    
    fun execute() {
        val cb = callback // 获取引用
        cb?.invoke() // 无锁调用
    }
}
```

## 总结

Kotlin 提供了丰富的同步和原子操作工具，可以满足不同场景的需求：

1. **基础同步**：synchronized、ReentrantLock、ReadWriteLock
2. **原子操作**：AtomicInteger、AtomicReference、LongAdder 等
3. **协程同步**：Mutex、Semaphore、Channel、Actor
4. **高级模式**：双重检查锁定、分段锁、无锁算法

选择合适的同步机制，可以在保证线程安全的同时，获得最佳的性能表现。在协程环境中，优先使用协程专用的同步工具，避免阻塞线程。