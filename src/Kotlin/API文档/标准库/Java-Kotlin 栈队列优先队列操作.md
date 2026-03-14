---
title: Java/Kotlin 栈、队列、优先队列操作
date: 2026-03-09
footer: Trae编辑
---


## 目录

1. [概述](#概述)
2. [Stack（栈）](#stack栈)
3. [Queue（队列）](#queue队列)
4. [PriorityQueue（优先队列）](#priorityqueue优先队列)
5. [Deque（双端队列）](#deque双端队列)
6. [Kotlin 扩展用法](#kotlin-扩展用法)
7. [性能对比](#性能对比)
8. [应用场景](#应用场景)

## 概述

| 数据结构 | 特性 | Java 类 | Kotlin 用法 |
|---------|------|---------|-------------|
| 栈 (Stack) | 后进先出 LIFO | `java.util.Stack` | 直接使用 Java 类 |
| 队列 (Queue) | 先进先出 FIFO | `java.util.Queue` | 直接使用 Java 接口 |
| 优先队列 | 按优先级出队 | `java.util.PriorityQueue` | 直接使用 Java 类 |
| 双端队列 | 两端都可操作 | `java.util.ArrayDeque` | 直接使用 Java 类 |

## Stack（栈）

### 创建 Stack

```kotlin
import java.util.Stack

// 创建空栈
val stack = Stack<String>()

// 创建并初始化
val stack2 = Stack<Int>().apply {
    push(1)
    push(2)
    push(3)
}
```

### 基本操作

```kotlin
import java.util.Stack

val stack = Stack<String>()

// 压栈 (push)
stack.push("First")
stack.push("Second")
stack.push("Third")

// 弹栈 (pop) - 移除并返回栈顶元素
val top = stack.pop()  // 返回 "Third"

// 查看栈顶 (peek) - 不移除
val peek = stack.peek()  // 返回 "Second"

// 检查是否为空
val isEmpty = stack.isEmpty()  // false

// 获取栈大小
val size = stack.size  // 2

// 搜索元素位置（从栈顶开始计数，1-based）
val position = stack.search("First")  // 返回 2

// 检查是否包含元素
val contains = stack.contains("Second")  // true
```

### 遍历 Stack

```kotlin
import java.util.Stack

val stack = Stack<String>().apply {
    push("A")
    push("B")
    push("C")
}

// 使用迭代器（从栈底到栈顶）
for (element in stack) {
    println(element)  // A, B, C
}

// 使用 forEach
stack.forEach { println(it) }

// 使用索引遍历
for (i in 0 until stack.size) {
    println(stack[i])
}
```

### Stack 完整示例

```kotlin
import java.util.Stack

fun main() {
    // 括号匹配检查
    fun isValidParentheses(s: String): Boolean {
        val stack = Stack<Char>()
        val pairs = mapOf(')' to '(', '}' to '{', ']' to '[')
        
        for (char in s) {
            when (char) {
                '(', '{', '[' -> stack.push(char)
                ')', '}', ']' -> {
                    if (stack.isEmpty() || stack.pop() != pairs[char]) {
                        return false
                    }
                }
            }
        }
        return stack.isEmpty()
    }
    
    println(isValidParentheses("(){}[]"))  // true
    println(isValidParentheses("([)]"))    // false
    println(isValidParentheses("{[]}"))    // true
}
```

## Queue（队列）

### 创建 Queue

```kotlin
import java.util.LinkedList
import java.util.ArrayDeque

// 使用 LinkedList 实现
val queue1: Queue<String> = LinkedList()

// 使用 ArrayDeque 实现（推荐，性能更好）
val queue2: Queue<String> = ArrayDeque()

// Kotlin 风格创建
val queue3 = ArrayDeque<String>().apply {
    add("A")
    add("B")
}
```

### 基本操作

```kotlin
import java.util.ArrayDeque

val queue = ArrayDeque<String>()

// 入队 - add/offer
queue.add("First")      // 失败时抛出异常
queue.offer("Second")   // 失败时返回 false

// 出队 - remove/poll
val first1 = queue.remove()  // 空队列时抛出异常
val first2 = queue.poll()    // 空队列时返回 null

// 查看队首 - element/peek
val head1 = queue.element()  // 空队列时抛出异常
val head2 = queue.peek()     // 空队列时返回 null

// 检查大小
val size = queue.size

// 检查是否为空
val isEmpty = queue.isEmpty()
```

### 操作对比表

| 操作 | 抛出异常 | 返回特殊值 |
|-----|---------|-----------|
| 入队 | `add(e)` | `offer(e)` |
| 出队 | `remove()` | `poll()` |
| 查看队首 | `element()` | `peek()` |

### Queue 完整示例

```kotlin
import java.util.ArrayDeque

fun main() {
    // 使用队列实现任务调度
    class TaskScheduler {
        private val queue = ArrayDeque<String>()
        
        fun addTask(task: String) {
            queue.offer(task)
            println("添加任务: $task")
        }
        
        fun executeTask(): String? {
            val task = queue.poll()
            if (task != null) {
                println("执行任务: $task")
            } else {
                println("没有待执行的任务")
            }
            return task
        }
        
        fun pendingTasks(): Int = queue.size
    }
    
    val scheduler = TaskScheduler()
    scheduler.addTask("发送邮件")
    scheduler.addTask("备份数据")
    scheduler.addTask("生成报表")
    
    println("待处理任务数: ${scheduler.pendingTasks()}")
    
    repeat(4) { scheduler.executeTask() }
}

// 输出：
// 添加任务: 发送邮件
// 添加任务: 备份数据
// 添加任务: 生成报表
// 待处理任务数: 3
// 执行任务: 发送邮件
// 执行任务: 备份数据
// 执行任务: 生成报表
// 没有待执行的任务
```

## PriorityQueue（优先队列）

### 创建 PriorityQueue

```kotlin
import java.util.PriorityQueue

// 创建自然顺序的优先队列（最小堆）
val pq1 = PriorityQueue<Int>()

// 创建指定初始容量的优先队列
val pq2 = PriorityQueue<String>(100)

// 创建自定义比较器的优先队列（最大堆）
val maxHeap = PriorityQueue<Int>(compareByDescending { it })

// 从集合创建
val pq3 = PriorityQueue(listOf(3, 1, 4, 1, 5, 9, 2, 6))
```

### 基本操作

```kotlin
import java.util.PriorityQueue

val pq = PriorityQueue<Int>()

// 添加元素 - add/offer
pq.add(5)
pq.offer(3)
pq.add(7)
pq.offer(1)

// 查看队首（不移除）
val peek = pq.peek()  // 返回 1（最小值）

// 移除队首
val poll = pq.poll()  // 返回 1

// 检查大小
val size = pq.size  // 3

// 检查是否为空
val isEmpty = pq.isEmpty()

// 清空队列
pq.clear()
```

### 自定义对象和比较器

```kotlin
import java.util.PriorityQueue

data class Task(
    val name: String,
    val priority: Int,
    val deadline: Long
)

fun main() {
    // 按优先级排序（数字越小优先级越高）
    val priorityQueue = PriorityQueue<Task>(
        compareBy { it.priority }
    )
    
    priorityQueue.add(Task("紧急Bug修复", 1, System.currentTimeMillis()))
    priorityQueue.add(Task("功能开发", 3, System.currentTimeMillis() + 86400000))
    priorityQueue.add(Task("代码审查", 2, System.currentTimeMillis() + 3600000))
    
    // 按优先级出队
    while (priorityQueue.isNotEmpty()) {
        val task = priorityQueue.poll()
        println("执行: ${task.name} (优先级: ${task.priority})")
    }
}

// 输出：
// 执行: 紧急Bug修复 (优先级: 1)
// 执行: 代码审查 (优先级: 2)
// 执行: 功能开发 (优先级: 3)
```

### 多字段比较器

```kotlin
import java.util.PriorityQueue

data class Student(
    val name: String,
    val score: Int,
    val age: Int
)

fun main() {
    // 先按分数降序，分数相同按年龄升序
    val students = PriorityQueue<Student>(
        compareByDescending<Student> { it.score }
            .thenBy { it.age }
    )
    
    students.add(Student("Alice", 90, 20))
    students.add(Student("Bob", 95, 22))
    students.add(Student("Charlie", 90, 18))
    students.add(Student("David", 85, 21))
    
    while (students.isNotEmpty()) {
        val s = students.poll()
        println("${s.name}: ${s.score}分, ${s.age}岁")
    }
}

// 输出：
// Bob: 95分, 22岁
// Charlie: 90分, 18岁
// Alice: 90分, 20岁
// David: 85分, 21岁
```

### PriorityQueue 完整示例：Top K 问题

```kotlin
import java.util.PriorityQueue

fun main() {
    // 查找数组中第 K 大的元素
    fun findKthLargest(nums: IntArray, k: Int): Int {
        // 使用最小堆，保持堆的大小为 k
        val minHeap = PriorityQueue<Int>(k)
        
        for (num in nums) {
            if (minHeap.size < k) {
                minHeap.offer(num)
            } else if (num > minHeap.peek()) {
                minHeap.poll()
                minHeap.offer(num)
            }
        }
        
        return minHeap.peek()
    }
    
    val nums = intArrayOf(3, 2, 1, 5, 6, 4)
    println("第2大的元素: ${findKthLargest(nums, 2)}")  // 5
    println("第4大的元素: ${findKthLargest(nums, 4)}")  // 3
    
    // 合并 K 个有序链表
    class ListNode(var `val`: Int) {
        var next: ListNode? = null
    }
    
    fun mergeKLists(lists: Array<ListNode?>): ListNode? {
        val dummy = ListNode(0)
        var current: ListNode? = dummy
        
        val pq = PriorityQueue<ListNode>(compareBy { it.`val` })
        
        // 将每个链表的头节点加入优先队列
        for (list in lists) {
            if (list != null) {
                pq.offer(list)
            }
        }
        
        while (pq.isNotEmpty()) {
            val node = pq.poll()
            current?.next = node
            current = node
            
            if (node.next != null) {
                pq.offer(node.next)
            }
        }
        
        return dummy.next
    }
}
```

## Deque（双端队列）

### 创建 Deque

```kotlin
import java.util.ArrayDeque
import java.util.LinkedList

// 使用 ArrayDeque（推荐）
val deque1: Deque<String> = ArrayDeque()

// 使用 LinkedList
val deque2: Deque<String> = LinkedList()

// Kotlin 风格创建
val deque = ArrayDeque<Int>().apply {
    addFirst(1)
    addLast(2)
}
```

### 双端操作

```kotlin
import java.util.ArrayDeque

val deque = ArrayDeque<String>()

// 头部操作
deque.addFirst("First")      // 失败抛异常
deque.offerFirst("First")    // 失败返回 false
deque.removeFirst()          // 失败抛异常
deque.pollFirst()            // 失败返回 null
deque.getFirst()             // 失败抛异常
deque.peekFirst()            // 失败返回 null

// 尾部操作
deque.addLast("Last")        // 等同于 add/offer
deque.offerLast("Last")
deque.removeLast()           // 失败抛异常
deque.pollLast()             // 失败返回 null
deque.getLast()              // 失败抛异常
deque.peekLast()             // 失败返回 null

// 栈操作（使用 Deque 作为栈）
deque.push("Top")      // 等同于 addFirst
deque.pop()            // 等同于 removeFirst
deque.peek()           // 等同于 peekFirst
```

### Deque 作为栈和队列使用

```kotlin
import java.util.ArrayDeque

fun main() {
    // 作为栈使用（LIFO）
    val stack = ArrayDeque<String>()
    stack.push("First")
    stack.push("Second")
    stack.push("Third")
    
    println("栈顶: ${stack.peek()}")  // Third
    while (stack.isNotEmpty()) {
        println("弹出: ${stack.pop()}")  // Third, Second, First
    }
    
    // 作为队列使用（FIFO）
    val queue = ArrayDeque<String>()
    queue.offer("Alice")
    queue.offer("Bob")
    queue.offer("Charlie")
    
    println("\n队首: ${queue.peek()}")  // Alice
    while (queue.isNotEmpty()) {
        println("出队: ${queue.poll()}")  // Alice, Bob, Charlie
    }
}
```

## Kotlin 扩展用法

### 使用 Kotlin 集合操作

```kotlin
import java.util.ArrayDeque
import java.util.PriorityQueue

fun main() {
    // Queue 与 Kotlin 集合操作结合
    val queue = ArrayDeque(listOf(1, 2, 3, 4, 5))
    
    // 过滤
    val filtered = queue.filter { it > 2 }
    println(filtered)  // [3, 4, 5]
    
    // 映射
    val doubled = queue.map { it * 2 }
    println(doubled)  // [2, 4, 6, 8, 10]
    
    // 转换为 List
    val list = queue.toList()
    
    // PriorityQueue 的 Kotlin 操作
    val pq = PriorityQueue(listOf(5, 2, 8, 1, 9))
    
    // 转换为有序列表
    val sortedList = generateSequence { pq.poll() }
        .takeWhile { true }
        .toList()
    println(sortedList)  // [1, 2, 5, 8, 9]
}
```

### 自定义扩展函数

```kotlin
import java.util.PriorityQueue
import java.util.Stack
import java.util.ArrayDeque

// 获取栈的中间元素
fun <T> Stack<T>.middle(): T? {
    if (isEmpty()) return null
    return this[size / 2]
}

// 队列旋转
fun <T> ArrayDeque<T>.rotate(n: Int) {
    val steps = n % size
    repeat(if (steps < 0) steps + size else steps) {
        offerLast(pollFirst())
    }
}

// 获取优先队列的前 K 个元素
fun <T> PriorityQueue<T>.topK(k: Int): List<T> {
    val result = mutableListOf<T>()
    val temp = PriorityQueue(this)
    repeat(minOf(k, size)) {
        temp.poll()?.let { result.add(it) }
    }
    return result
}

fun main() {
    val stack = Stack<Int>().apply {
        push(1)
        push(2)
        push(3)
        push(4)
        push(5)
    }
    println("中间元素: ${stack.middle()}")  // 3
    
    val queue = ArrayDeque(listOf(1, 2, 3, 4, 5))
    queue.rotate(2)
    println("旋转后: $queue")  // [3, 4, 5, 1, 2]
    
    val pq = PriorityQueue(listOf(5, 2, 8, 1, 9, 3))
    println("前3个: ${pq.topK(3)}")  // [1, 2, 3]
}
```

## 性能对比

| 操作 | Stack | ArrayDeque (Queue) | LinkedList (Queue) | PriorityQueue |
|-----|-------|-------------------|-------------------|---------------|
| push/add | O(1) | O(1) | O(1) | O(log n) |
| pop/remove | O(1) | O(1) | O(1) | O(log n) |
| peek | O(1) | O(1) | O(1) | O(1) |
| search | O(n) | - | - | - |
| 内存占用 | 中等 | 低 | 高 | 中等 |

**推荐选择：**
- 需要栈：使用 `ArrayDeque`（比 `Stack` 更快，无同步开销）
- 需要队列：使用 `ArrayDeque`（比 `LinkedList` 内存效率更高）
- 需要优先队列：使用 `PriorityQueue`
- 需要线程安全：使用 `ConcurrentLinkedQueue` 或 `BlockingQueue`

## 应用场景

### Stack 应用场景

```kotlin
import java.util.ArrayDeque

// 1. 表达式求值
fun evaluateExpression(expression: String): Int {
    val stack = ArrayDeque<Int>()
    var num = 0
    var op = '+'
    
    for (i in expression.indices) {
        val char = expression[i]
        
        if (char.isDigit()) {
            num = num * 10 + (char - '0')
        }
        
        if ((!char.isDigit() && char != ' ') || i == expression.length - 1) {
            when (op) {
                '+' -> stack.push(num)
                '-' -> stack.push(-num)
                '*' -> stack.push(stack.pop() * num)
                '/' -> stack.push(stack.pop() / num)
            }
            op = char
            num = 0
        }
    }
    
    return stack.sum()
}

// 2. 浏览器前进后退
class BrowserHistory(homepage: String) {
    private val backStack = ArrayDeque<String>()
    private val forwardStack = ArrayDeque<String>()
    private var current = homepage
    
    fun visit(url: String) {
        backStack.push(current)
        current = url
        forwardStack.clear()
    }
    
    fun back(steps: Int): String {
        repeat(steps) {
            if (backStack.isEmpty()) return current
            forwardStack.push(current)
            current = backStack.pop()
        }
        return current
    }
    
    fun forward(steps: Int): String {
        repeat(steps) {
            if (forwardStack.isEmpty()) return current
            backStack.push(current)
            current = forwardStack.pop()
        }
        return current
    }
}
```

### Queue 应用场景

```kotlin
import java.util.ArrayDeque

// 1. BFS 广度优先搜索
fun bfs(graph: Map<String, List<String>>, start: String): List<String> {
    val visited = mutableSetOf<String>()
    val queue = ArrayDeque<String>()
    val result = mutableListOf<String>()
    
    queue.offer(start)
    visited.add(start)
    
    while (queue.isNotEmpty()) {
        val node = queue.poll()
        result.add(node)
        
        for (neighbor in graph[node] ?: emptyList()) {
            if (neighbor !in visited) {
                visited.add(neighbor)
                queue.offer(neighbor)
            }
        }
    }
    
    return result
}

// 2. 滑动窗口最大值
fun maxSlidingWindow(nums: IntArray, k: Int): IntArray {
    if (nums.isEmpty() || k == 0) return intArrayOf()
    
    val deque = ArrayDeque<Int>() // 存储索引
    val result = mutableListOf<Int>()
    
    for (i in nums.indices) {
        // 移除窗口外的元素
        if (deque.isNotEmpty() && deque.first() < i - k + 1) {
            deque.pollFirst()
        }
        
        // 移除所有小于当前元素的索引
        while (deque.isNotEmpty() && nums[deque.last()] < nums[i]) {
            deque.pollLast()
        }
        
        deque.offerLast(i)
        
        // 记录窗口最大值
        if (i >= k - 1) {
            result.add(nums[deque.first()])
        }
    }
    
    return result.toIntArray()
}
```

### PriorityQueue 应用场景

```kotlin
import java.util.PriorityQueue

// 1. 任务调度器
class TaskScheduler {
    data class Task(
        val id: Int,
        val priority: Int,
        val executionTime: Long
    )
    
    private val taskQueue = PriorityQueue<Task>(
        compareByDescending { it.priority }
    )
    
    fun addTask(task: Task) {
        taskQueue.offer(task)
    }
    
    fun getNextTask(): Task? = taskQueue.poll()
    
    fun hasTasks(): Boolean = taskQueue.isNotEmpty()
}

// 2. 数据流中的中位数
class MedianFinder {
    // 大顶堆，存储较小的一半
    private val smallHalf = PriorityQueue<Int>(compareByDescending { it })
    // 小顶堆，存储较大的一半
    private val largeHalf = PriorityQueue<Int>()
    
    fun addNum(num: Int) {
        if (smallHalf.isEmpty() || num <= smallHalf.peek()) {
            smallHalf.offer(num)
        } else {
            largeHalf.offer(num)
        }
        
        // 平衡两个堆
        if (smallHalf.size > largeHalf.size + 1) {
            largeHalf.offer(smallHalf.poll())
        } else if (largeHalf.size > smallHalf.size) {
            smallHalf.offer(largeHalf.poll())
        }
    }
    
    fun findMedian(): Double {
        return if (smallHalf.size == largeHalf.size) {
            (smallHalf.peek() + largeHalf.peek()) / 2.0
        } else {
            smallHalf.peek().toDouble()
        }
    }
}

// 3. Dijkstra 最短路径算法
fun dijkstra(graph: Map<String, Map<String, Int>>, start: String): Map<String, Int> {
    val distances = mutableMapOf<String, Int>().withDefault { Int.MAX_VALUE }
    val pq = PriorityQueue<Pair<String, Int>>(compareBy { it.second })
    val visited = mutableSetOf<String>()
    
    distances[start] = 0
    pq.offer(start to 0)
    
    while (pq.isNotEmpty()) {
        val (node, dist) = pq.poll()
        
        if (node in visited) continue
        visited.add(node)
        
        for ((neighbor, weight) in graph[node] ?: emptyMap()) {
            val newDist = dist + weight
            if (newDist < distances.getValue(neighbor)) {
                distances[neighbor] = newDist
                pq.offer(neighbor to newDist)
            }
        }
    }
    
    return distances
}
```

## 总结

| 数据结构 | 核心特点 | 推荐实现 | 主要用途 |
|---------|---------|---------|---------|
| Stack | LIFO 后进先出 | `ArrayDeque` | 括号匹配、表达式求值、回溯算法 |
| Queue | FIFO 先进先出 | `ArrayDeque` | BFS、任务调度、缓冲处理 |
| PriorityQueue | 按优先级出队 | `PriorityQueue` | Top K、合并有序序列、调度算法 |
| Deque | 双端操作 | `ArrayDeque` | 滑动窗口、双端队列场景 |

在 Kotlin 中使用这些数据结构时，建议：
1. 优先使用 `ArrayDeque` 替代 `Stack` 和 `LinkedList`
2. 利用 Kotlin 的扩展函数简化操作
3. 根据具体场景选择合适的比较器
4. 注意线程安全问题，必要时使用并发集合