---
title: Kotlin Array 操作与并发优化
date: 2026-03-13
footer: Trae编辑
---


## 目录

1. [Array 基础](#array-基础)
2. [创建与初始化](#创建与初始化)
3. [基本操作](#基本操作)
4. [高阶函数](#高阶函数)
5. [并发环境下的稳健写法](#并发环境下的稳健写法)
6. [激进优化写法](#激进优化写法)
7. [性能对比与最佳实践](#性能对比与最佳实践)

## Array 基础

### Array 与 List 的区别

| 特性 | Array | List |
|------|-------|------|
| 大小 | 固定 | 可变 |
| 性能 | 访问更快 | 操作更灵活 |
| 内存 | 连续存储 | 可能不连续 |
| 协变 | 支持 | 支持 |
| 原始类型 | 有专门类型 | 自动装箱 |

### 原始类型数组

Kotlin 为原始类型提供了专门的数组类，避免装箱开销：

```kotlin
val intArray = IntArray(10)      // IntArray
val longArray = LongArray(10)    // LongArray
val doubleArray = DoubleArray(10)// DoubleArray
val charArray = CharArray(10)    // CharArray
val byteArray = ByteArray(10)    // ByteArray
val shortArray = ShortArray(10)  // ShortArray
val floatArray = FloatArray(10)  // FloatArray
val booleanArray = BooleanArray(10) // BooleanArray
```

## 创建与初始化

### 基本创建方式

```kotlin
// 1. 使用 arrayOf()
val arr1 = arrayOf(1, 2, 3, 4, 5)

// 2. 使用构造函数
val arr2 = Array(5) { i -> i * 2 }  // [0, 2, 4, 6, 8]

// 3. 使用工厂函数
val arr3 = IntArray(5) { i -> i * i }  // [0, 1, 4, 9, 16]

// 4. 空数组
val emptyArray = emptyArray<String>()

// 5. 指定大小的空数组
val sizedArray = arrayOfNulls<String>(10)
```

### 初始化技巧

```kotlin
// 预分配并初始化
val buffer = ByteArray(1024) { 0 }

// 使用特定值填充
val ones = IntArray(100) { 1 }

// 随机初始化
val randomArray = DoubleArray(100) { Math.random() }

// 从集合转换
val list = listOf(1, 2, 3)
val array = list.toTypedArray()
val intArray = list.toIntArray()
```

## 基本操作

### 访问与修改

```kotlin
val arr = intArrayOf(1, 2, 3, 4, 5)

// 访问元素
val first = arr[0]        // 1
val last = arr[arr.size - 1]  // 5

// 修改元素
arr[0] = 10

// 安全访问
val element = arr.getOrElse(10) { -1 }  // -1 (越界时返回默认值)
val element2 = arr.getOrNull(10)        // null
```

### 遍历操作

```kotlin
val arr = intArrayOf(1, 2, 3, 4, 5)

// for 循环
for (i in arr.indices) {
    println("$i: ${arr[i]}")
}

// for-each
for (element in arr) {
    println(element)
}

// withIndex
for ((index, value) in arr.withIndex()) {
    println("$index: $value")
}

// forEach
arr.forEach { println(it) }
arr.forEachIndexed { index, value -> println("$index: $value") }
```

### 切片与复制

```kotlin
val arr = intArrayOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

// 切片
val slice = arr.sliceArray(2..5)      // [3, 4, 5, 6]
val slice2 = arr.sliceArray(0 until 3) // [1, 2, 3]

// 复制
val copy = arr.copyOf()
val partialCopy = arr.copyOfRange(2, 5)  // [3, 4, 5]

// 填充
arr.fill(0, 0, 3)  // 将前3个元素填充为0
```

## 高阶函数

### 转换操作

```kotlin
val arr = intArrayOf(1, 2, 3, 4, 5)

// map
val doubled = arr.map { it * 2 }  // [2, 4, 6, 8, 10]

// filter
val evens = arr.filter { it % 2 == 0 }  // [2, 4]

// reduce
val sum = arr.reduce { acc, i -> acc + i }  // 15

// fold
val sumWithInitial = arr.fold(10) { acc, i -> acc + i }  // 25

// flatMap
val nested = arrayOf(intArrayOf(1, 2), intArrayOf(3, 4))
val flat = nested.flatMap { it.asIterable() }  // [1, 2, 3, 4]
```

### 排序与查找

```kotlin
val arr = intArrayOf(3, 1, 4, 1, 5, 9, 2, 6)

// 排序
arr.sort()                          // 原地排序
val sorted = arr.sortedArray()      // 返回新数组
val sortedDesc = arr.sortedArrayDescending()

// 自定义排序
val customSorted = arr.sortedArrayWith(compareBy { it % 3 })

// 二分查找（数组必须先排序）
arr.sort()
val index = arr.binarySearch(5)     // 返回索引或负数

// 查找极值
val max = arr.maxOrNull()           // 9
val min = arr.minOrNull()           // 1
```

### 分组与聚合

```kotlin
val arr = intArrayOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

// groupBy
val grouped = arr.groupBy { it % 2 == 0 }  // {false=[1, 3, 5, 7, 9], true=[2, 4, 6, 8, 10]}

// partition
val (evens, odds) = arr.partition { it % 2 == 0 }

// 统计
val count = arr.count { it > 5 }    // 5
val sum = arr.sum()                 // 55
val average = arr.average()         // 5.5
```

## 并发环境下的稳健写法

### 线程安全基础

```kotlin
import java.util.concurrent.atomic.AtomicIntegerArray
import java.util.concurrent.locks.ReentrantReadWriteLock
import kotlin.concurrent.withLock

// 1. 使用 Atomic 数组（适用于基本类型）
class AtomicIntArray(size: Int) {
    private val array = AtomicIntegerArray(size)
    
    fun get(index: Int): Int = array.get(index)
    fun set(index: Int, value: Int) = array.set(index, value)
    fun addAndGet(index: Int, delta: Int): Int = array.addAndGet(index, delta)
    fun compareAndSet(index: Int, expect: Int, update: Int): Boolean = 
        array.compareAndSet(index, expect, update)
}

// 2. 使用读写锁
class ThreadSafeArray<T>(size: Int, init: (Int) -> T) {
    private val array = Array(size, init)
    private val lock = ReentrantReadWriteLock()
    
    fun get(index: Int): T = lock.readLock().withLock {
        array[index]
    }
    
    fun set(index: Int, value: T) = lock.writeLock().withLock {
        array[index] = value
    }
    
    fun update(index: Int, updater: (T) -> T): T = lock.writeLock().withLock {
        array[index] = updater(array[index])
        array[index]
    }
}
```

### 并发集合替代方案

```kotlin
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.ConcurrentHashMap

// 1. CopyOnWriteArrayList（读多写少场景）
class ConcurrentArrayList<T> {
    private val list = CopyOnWriteArrayList<T>()
    
    fun add(element: T) = list.add(element)
    fun get(index: Int): T = list[index]
    fun removeAt(index: Int): T = list.removeAt(index)
    fun toArray(): Array<Any?> = list.toTypedArray()
}

// 2. 使用 ConcurrentHashMap 模拟数组
class ConcurrentArrayMap<T>(size: Int) {
    private val map = ConcurrentHashMap<Int, T>()
    private val size = size
    
    operator fun get(index: Int): T? = map[index]
    operator fun set(index: Int, value: T) { map[index] = value }
    fun compareAndSet(index: Int, expect: T?, update: T?): Boolean {
        return if (expect == null) {
            map.putIfAbsent(index, update!!) == null
        } else {
            map.replace(index, expect, update!!)
        }
    }
}
```

### 分段锁优化

```kotlin
import java.util.concurrent.locks.ReentrantLock
import kotlin.concurrent.withLock

// 分段锁数组（减少锁竞争）
class SegmentedArray<T>(
    size: Int,
    segments: Int = Runtime.getRuntime().availableProcessors(),
    init: (Int) -> T
) {
    private val array = Array(size, init)
    private val locks = Array(segments) { ReentrantLock() }
    private val segmentSize = (size + segments - 1) / segments
    
    private fun getLock(index: Int): ReentrantLock {
        return locks[index / segmentSize]
    }
    
    fun get(index: Int): T = getLock(index).withLock {
        array[index]
    }
    
    fun set(index: Int, value: T) = getLock(index).withLock {
        array[index] = value
    }
    
    // 批量操作（减少锁获取次数）
    fun batchUpdate(indices: IntRange, updater: (Int, T) -> T) {
        val affectedLocks = indices.map { getLock(it) }.distinct()
        affectedLocks.forEach { it.lock() }
        try {
            for (i in indices) {
                array[i] = updater(i, array[i])
            }
        } finally {
            affectedLocks.forEach { it.unlock() }
        }
    }
}
```

### 无锁算法

```kotlin
import java.util.concurrent.atomic.AtomicReferenceArray
import java.util.concurrent.atomic.AtomicInteger

// 无锁数组（使用 CAS 操作）
class LockFreeArray<T>(size: Int) {
    private val array = AtomicReferenceArray<T>(size)
    private val size = AtomicInteger(0)
    
    fun get(index: Int): T? = array.get(index)
    
    fun set(index: Int, value: T): Boolean {
        while (true) {
            val current = array.get(index)
            if (array.compareAndSet(index, current, value)) {
                return true
            }
        }
    }
    
    fun compareAndSet(index: Int, expect: T?, update: T?): Boolean {
        return array.compareAndSet(index, expect, update)
    }
    
    fun getAndSet(index: Int, value: T): T? = array.getAndSet(index, value)
}
```

## 激进优化写法

### 内存布局优化

```kotlin
import java.nio.ByteBuffer
import java.nio.ByteOrder

// 使用 Direct ByteBuffer 减少 GC 压力
class OffHeapArray(size: Int) {
    private val buffer = ByteBuffer.allocateDirect(size * 4)
        .order(ByteOrder.nativeOrder())
    
    operator fun get(index: Int): Int {
        return buffer.getInt(index * 4)
    }
    
    operator fun set(index: Int, value: Int) {
        buffer.putInt(index * 4, value)
    }
    
    fun asIntBuffer() = buffer.asIntBuffer()
}

// 使用 sun.misc.Unsafe（不推荐，但性能极致）
@Suppress("UNCHECKED_CAST")
class UnsafeArray<T>(size: Int) {
    companion object {
        private val unsafe = sun.misc.Unsafe::class.java.getDeclaredField("theUnsafe").apply {
            isAccessible = true
        }.get(null) as sun.misc.Unsafe
    }
    
    private val baseOffset = unsafe.arrayBaseOffset(Array<Any>::class.java)
    private val indexScale = unsafe.arrayIndexScale(Array<Any>::class.java)
    private val array = arrayOfNulls<Any>(size)
    
    operator fun get(index: Int): T? {
        return unsafe.getObject(array, baseOffset + index * indexScale) as T?
    }
    
    operator fun set(index: Int, value: T?) {
        unsafe.putObject(array, baseOffset + index * indexScale, value)
    }
}
```

### SIMD 优化

```kotlin
// 使用 Vector API（JDK 16+）
import jdk.incubator.vector.*

class SimdArray {
    companion object {
        private val SPECIES = IntVector.SPECIES_PREFERRED
        
        fun simdAdd(a: IntArray, b: IntArray, result: IntArray) {
            val upperBound = SPECIES.loopBound(a.size)
            var i = 0
            
            while (i < upperBound) {
                val va = IntVector.fromArray(SPECIES, a, i)
                val vb = IntVector.fromArray(SPECIES, b, i)
                val vc = va.add(vb)
                vc.intoArray(result, i)
                i += SPECIES.length()
            }
            
            // 处理剩余元素
            while (i < a.size) {
                result[i] = a[i] + b[i]
                i++
            }
        }
    }
}
```

### 缓存友好访问

```kotlin
// 缓存行对齐（避免伪共享）
class CacheAlignedArray(size: Int) {
    companion object {
        private const val CACHE_LINE_SIZE = 64
        private const val PADDING = CACHE_LINE_SIZE / 8  // 8 bytes per Long
    }
    
    // 每个元素占用一个缓存行
    private val array = LongArray(size * PADDING)
    
    operator fun get(index: Int): Long = array[index * PADDING]
    operator fun set(index: Int, value: Long) { array[index * PADDING] = value }
}

// 分块处理（提高缓存命中率）
fun <T> Array<T>.blockProcess(blockSize: Int = 1024, processor: (Int, T) -> Unit) {
    for (blockStart in indices step blockSize) {
        val blockEnd = minOf(blockStart + blockSize, size)
        for (i in blockStart until blockEnd) {
            processor(i, this[i])
        }
    }
}
```

### 并行处理优化

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.ForkJoinPool
import java.util.concurrent.RecursiveAction

// Kotlin Coroutines 并行处理
suspend fun <T> Array<T>.parallelMap(
    parallelism: Int = Runtime.getRuntime().availableProcessors(),
    transform: (T) -> T
): Array<T> {
    val chunkSize = (size + parallelism - 1) / parallelism
    return coroutineScope {
        (0 until parallelism).map { chunkIndex ->
            async {
                val start = chunkIndex * chunkSize
                val end = minOf(start + chunkSize, size)
                for (i in start until end) {
                    this@parallelMap[i] = transform(this@parallelMap[i])
                }
            }
        }.awaitAll()
        this@parallelMap
    }
}

// Fork/Join 框架
class ParallelArrayTask(
    private val array: IntArray,
    private val start: Int,
    private val end: Int,
    private val threshold: Int = 10000
) : RecursiveAction() {
    
    override fun compute() {
        if (end - start <= threshold) {
            // 直接处理
            for (i in start until end) {
                array[i] = array[i] * 2  // 示例操作
            }
        } else {
            val mid = (start + end) / 2
            val left = ParallelArrayTask(array, start, mid, threshold)
            val right = ParallelArrayTask(array, mid, end, threshold)
            invokeAll(left, right)
        }
    }
}

// 使用
fun processArrayParallel(array: IntArray) {
    ForkJoinPool.commonPool().invoke(ParallelArrayTask(array, 0, array.size))
}
```

## 性能对比与最佳实践

### 性能对比表

| 场景 | 普通数组 | 线程安全数组 | 分段锁数组 | 无锁数组 | 堆外数组 |
|------|---------|-------------|-----------|---------|---------|
| 单线程读 | 最快 | 慢 | 中等 | 中等 | 快 |
| 单线程写 | 最快 | 慢 | 中等 | 中等 | 快 |
| 多线程读 | 不安全 | 快 | 快 | 快 | 快 |
| 多线程写 | 不安全 | 慢 | 中等 | 中等 | 中等 |
| 内存占用 | 低 | 低 | 中等 | 低 | 低（但需手动管理） |
| GC 压力 | 正常 | 正常 | 正常 | 正常 | 低 |

### 最佳实践建议

1. **默认使用普通数组**：在单线程环境下，普通数组性能最优
2. **读多写少用 CopyOnWriteArrayList**：适合配置类数据
3. **高并发写用分段锁**：减少锁竞争，提高吞吐量
4. **极致性能用无锁算法**：但需要处理 ABA 问题
5. **大数组考虑堆外内存**：减少 GC 停顿，但需要手动管理
6. **计算密集型用并行处理**：利用多核 CPU 优势

### 代码示例：综合应用

```kotlin
import java.util.concurrent.atomic.AtomicIntegerArray
import java.util.concurrent.ForkJoinPool
import java.util.concurrent.RecursiveTask

// 高性能计数器数组
class HighPerformanceCounterArray(size: Int) {
    private val counters = AtomicIntegerArray(size)
    
    fun increment(index: Int): Int = counters.incrementAndGet(index)
    fun add(index: Int, delta: Int): Int = counters.addAndGet(index, delta)
    fun get(index: Int): Int = counters.get(index)
    fun getAndReset(index: Int): Int = counters.getAndSet(index, 0)
    
    // 批量获取并清零
    fun getAndResetAll(): IntArray {
        return IntArray(counters.length()) { i ->
            counters.getAndSet(i, 0)
        }
    }
}

// 并行数组求和
class ParallelSumTask(
    private val array: IntArray,
    private val start: Int,
    private val end: Int,
    private val threshold: Int = 10000
) : RecursiveTask<Long>() {
    
    override fun compute(): Long {
        if (end - start <= threshold) {
            var sum = 0L
            for (i in start until end) {
                sum += array[i]
            }
            return sum
        }
        
        val mid = (start + end) / 2
        val left = ParallelSumTask(array, start, mid, threshold)
        val right = ParallelSumTask(array, mid, end, threshold)
        left.fork()
        val rightResult = right.compute()
        val leftResult = left.join()
        return leftResult + rightResult
    }
}

// 使用示例
fun main() {
    val size = 1_000_000
    val array = IntArray(size) { it }
    
    // 并行求和
    val sum = ForkJoinPool.commonPool().invoke(ParallelSumTask(array, 0, size))
    println("Sum: $sum")
    
    // 高性能计数器
    val counters = HighPerformanceCounterArray(100)
    repeat(1000) {
        counters.increment(it % 100)
    }
    println("Counter[0]: ${counters.get(0)}")
}
```

## 总结

Kotlin Array 提供了丰富的操作能力，在不同场景下需要选择合适的实现方式：

1. **基础操作**：使用 Kotlin 标准库提供的高阶函数
2. **并发场景**：根据读写比例选择 Atomic、分段锁或无锁实现
3. **极致性能**：考虑堆外内存、SIMD 优化和缓存友好访问
4. **并行处理**：利用 Fork/Join 或 Kotlin Coroutines 实现并行计算

选择合适的数组实现方式，可以在保证线程安全的同时，获得最佳的性能表现。