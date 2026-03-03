---
title: Aoc Kotlin个人解题记录（一）
date: 2026-03-01
---
[[toc]]
***
## Day 1 - Part 1
### 题目描述
The Elves have good news and bad news.

The good news is that they've discovered [project management](https://en.wikipedia.org/wiki/Project_management)! This has given them the tools they need to prevent their usual Christmas emergency. For example, they now know that the North Pole decorations need to be finished soon so that other critical tasks can start on time.

The bad news is that they've realized they have a _different_ emergency: according to their resource planning, none of them have any time left to decorate the North Pole!

To save Christmas, the Elves need _you_ to _finish decorating the North Pole by December 12th_.

Collect stars by solving puzzles. Two puzzles will be made available on each day; the second puzzle is unlocked when you complete the first. Each puzzle grants _one star_. Good luck!

You arrive at the secret entrance to the North Pole base ready to start decorating. Unfortunately, the _password_ seems to have been changed, so you can't get in. A document taped to the wall helpfully explains:

"Due to new security protocols, the password is locked in the safe below. Please see the attached document for the new combination."

The safe has a dial with only an arrow on it; around the dial are the numbers `0` through `99` in order. As you turn the dial, it makes a small _click_ noise as it reaches each number.

The attached document (your puzzle input) contains a sequence of _rotations_, one per line, which tell you how to open the safe. A rotation starts with an `L` or `R` which indicates whether the rotation should be to the _left_ (toward lower numbers) or to the _right_ (toward higher numbers). Then, the rotation has a _distance_ value which indicates how many clicks the dial should be rotated in that direction.

So, if the dial were pointing at `11`, a rotation of `R8` would cause the dial to point at `19`. After that, a rotation of `L19` would cause it to point at `0`.

Because the dial is a circle, turning the dial _left from `0`_ one click makes it point at `99`. Similarly, turning the dial _right from `99`_ one click makes it point at `0`.

So, if the dial were pointing at `5`, a rotation of `L10` would cause it to point at `95`. After that, a rotation of `R5` could cause it to point at `0`.

The dial starts by pointing at `50`.

You could follow the instructions, but your recent required official North Pole secret entrance security training seminar taught you that the safe is actually a decoy. The actual password is _the number of times the dial is left pointing at `0` after any rotation in the sequence_.

For example, suppose the attached document contained the following rotations:

```
L68
L30
R48
L5
R60
L55
L1
L99
R14
L82
```

Following these rotations would cause the dial to move as follows:

- The dial starts by pointing at `50`.
- The dial is rotated `L68` to point at `82`.
- The dial is rotated `L30` to point at `52`.
- The dial is rotated `R48` to point at `_0_`.
- The dial is rotated `L5` to point at `95`.
- The dial is rotated `R60` to point at `55`.
- The dial is rotated `L55` to point at `_0_`.
- The dial is rotated `L1` to point at `99`.
- The dial is rotated `L99` to point at `_0_`.
- The dial is rotated `R14` to point at `14`.
- The dial is rotated `L82` to point at `32`.

Because the dial points at `0` a total of three times during this process, the password in this example is `_3_`.

Analyze the rotations in your attached document. _What's the actual password to open the door?_
***
题目情景是一个`0`到`99`的圆形电话拨号转盘；`L`指的是往左转（递减数字），`R`指的是往右转（增加数字）；`0`和`99`挨在一起，`0 L1`的结果就是`99`，反之`99 R1`的结果是`0`
转盘初始指向为`50`，题目要求的输出是：转到`0`的次数
### 解题代码
#### 拨号转盘代码
**拨号转盘类**V1
```kotlin
class Day1 (  
    val dialMinNum: Int = 0, // 拨号键盘最小数字  
    val dialMaxNum: Int = 99, // 拨号键盘最大数字  
  
    val dialStartPoint: Int = 50, // 拨号键盘起始指向  
){  
    private val range: Int = dialMaxNum - dialMinNum + 1  
  
    var password: Int = 0  
    // 当前指向的数字  
    var dialCurrPoint: Int = dialStartPoint  
    fun Point(): Int = dialCurrPoint  
  
    private fun check() {  
        dialCurrPoint = when(dialCurrPoint) {  
            in dialMinNum..dialMaxNum -> dialCurrPoint  
            else -> (dialCurrPoint + range) % range  
        }  
  
        if (dialCurrPoint == 0) password++  
    }  
    infix fun L(step: Int) {  
        dialCurrPoint -= step  
        check()  
    }  
    infix fun R(step: Int) {  
        dialCurrPoint += step  
        check()  
    }  
}

class Day1Test {  
    @Test  
    fun testDemo() {  
        val obj = Day1()  
  
        obj L 68  
        obj L 30  
        obj R 48  
        obj L 5  
        obj R 60  
        obj L 55  
        obj L 1  
        obj L 99  
        obj R 14  
        obj L 82  
  
        assertEquals(obj.password, 3)  
    }  
}
```
- 本来想用`observable`或`vetoable`监控并修改值的，但是后面发现*值校正* 也会触发`observale`，导致栈溢出，所以就换成朴素的手动修正了

**V2**
- 换上`setter`函数
```kotlin
class Day1 (  
    val dialMinNum: Int = 0, // 拨号键盘最小数字  
    val dialMaxNum: Int = 99, // 拨号键盘最大数字  
  
    val dialStartPoint: Int = 50, // 拨号键盘起始指向  
){  
    private val range: Int = dialMaxNum - dialMinNum + 1  
  
    var password: Int = 0  
    // 当前指向的数字  
    var dialCurrPoint: Int = dialStartPoint  
        set(value) {  
            field = (value + range) % range  
            // println("[修正]Pointed at $field")  
  
            if (field == 0) password++  
        }  
    fun Point(): Int = dialCurrPoint  
    infix fun L(step: Int) {  
        dialCurrPoint -= step  
        // check()  
    }  
    infix fun R(step: Int) {  
        dialCurrPoint += step  
        // check()  
    }
```

#### HTTP客户端请求API获取题目输入
**引入依赖**：
```kotlin
dependencies {
    testImplementation(kotlin("test"))
    
    // Ktor HTTP Client
    implementation("io.ktor:ktor-client-core:2.3.12")
    implementation("io.ktor:ktor-client-cio:2.3.12")
    implementation("io.ktor:ktor-client-content-negotiation:2.3.12")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.12")
}
```
**参考示例**：
```kotlin
// Common code
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.client.statement.*

suspend fun makeHttpRequest() {
    val client = HttpClient() // Ktor handles the correct engine internally
    val response: HttpResponse = client.get("https://api.example.com")
    println(response.body<String>())
    client.close()
}

```

![](assets/Pasted%20image%2020260301233129.png)
暂时不清楚要怎么获取输入
#### 解析题目文本
- 直接拓展在题目类上
- 使用`useLines`逐行解析文本，避免一次性加载文本到内存中
```kotlin
package org.example.Day1  
  
import java.io.File  
  
class Day1 (  
    val dialMinNum: Int = 0, // 拨号键盘最小数字  
    val dialMaxNum: Int = 99, // 拨号键盘最大数字  
  
    val dialStartPoint: Int = 50, // 拨号键盘起始指向  
){  
	// ...
  
    // 从字符串中格式化解析出来拨号动作  
    fun resolveOneLine(line: String?) {  
        val rotation = line?.get(0) ?: return  
        val step = line.substring(1).toIntOrNull()?: return  
  
        when(rotation) {  
            'L' -> L(step)  
            'R' -> R(step)  
            else -> return  
        }  
    }  
    fun resolveLines(lines: Sequence<String>) {  
        for (line in lines) {  
            resolveOneLine(line)  
        }  
    }  
    infix fun readFile(fileName: String) {  
        File(fileName).useLines {  
            lines -> resolveLines(lines)  
        }  
    }  
}
```
- **工作目录**为项目根目录
- 使用`Path(String).toAbsolutePath`在发生`FileNotFoundException`时打印完整路径进行debug
```kotlin
@Test  
fun testReadFile() {  
    // 工作目录为: F:\KotlinProjects\AoC2025  
    // 或<PROJECT_ROOT_PATH>  
    val fileName = "src/main/resources/puzzles/2025/day1.txt"  
    val day1 = Day1()  
  
    try {  
        day1 readFile fileName  
    } catch (e: FileNotFoundException) {  
        // 解析并打印完整路径  
        println("File not found: ${Path(fileName).toAbsolutePath()}")  
    }  
  
    println("password: ${day1.password}")  
}
```
## Day 1 - Part 2
### 题目描述
You're sure that's the right password, but the door won't open. You knock, but nobody answers. You build a snowman while you think.

As you're rolling the snowballs for your snowman, you find another security document that must have fallen into the snow:

"Due to newer security protocols, please use _password method 0x434C49434B_ until further notice."

You remember from the training seminar that "method 0x434C49434B" means you're actually supposed to count the number of times _any click_ causes the dial to point at `0`, regardless of whether it happens during a rotation or at the end of one.

Following the same rotations as in the above example, the dial points at zero a few extra times during its rotations:

- The dial starts by pointing at `50`.
- The dial is rotated `L68` to point at `82`; during this rotation, it points at `0` _once_.
- The dial is rotated `L30` to point at `52`.
- The dial is rotated `R48` to point at `_0_`.
- The dial is rotated `L5` to point at `95`.
- The dial is rotated `R60` to point at `55`; during this rotation, it points at `0` _once_.
- The dial is rotated `L55` to point at `_0_`.
- The dial is rotated `L1` to point at `99`.
- The dial is rotated `L99` to point at `_0_`.
- The dial is rotated `R14` to point at `14`.
- The dial is rotated `L82` to point at `32`; during this rotation, it points at `0` _once_.

In this example, the dial points at `0` three times at the end of a rotation, plus three more times during a rotation. So, in this example, the new password would be `_6_`.

Be careful: if the dial were pointing at `50`, a single rotation like `R1000` would cause the dial to point at `0` ten times before returning back to `50`!

Using password method 0x434C49434B, _what is the password to open the door?_

现在不是刚好指到`0`才算数，是过程中只要有一刻指到就算
### 解题代码
#### 题目本类
- 给Part1的类加个`open`关键字，允许Part2类去继承
- 尝试写环形列表，但是不好处理步数很大的情况，于是退回到纯计算
**P2V1**
```kotlin
override var dialCurrPoint: Int = dialStartPoint  
    set(value) {  
        val lastField = field  
        field = if ((value % range) >= 0) value % range else range + (value % range)  
  
        // println("$lastField -> [raw]$value |[mod]$field by ${(value - lastField).absoluteValue}")  
        password += if (value <= 0 && lastField != 0) {  
            (value.absoluteValue + range) / range  
        } else value / range  
    }
```
- 这里实际上也处理不了步数很小的情况

- 没有用上的环形迭代器，因为不好处理多倍跨越
```kotlin
package org.example.Day1  
  
// 自制可选方向的环形迭代列表  
enum class CycleDirection {  
    LEFT, RIGHT  
}  
  
operator fun IntRange.plus(other: IntRange): IntRange {  
    return IntRange(this.first + other.first, this.last + other.last)  
}  
fun Int.circular(  
    min: Int = 0, curr: Int = 50, target: Int = 99, max: Int = 99,  
    stepLength: Int = 1, direction: CycleDirection = CycleDirection.RIGHT  
): Iterable<Int> {  
    return when (direction) {  
        CycleDirection.LEFT -> {  
            if (curr < target) (curr downTo min step stepLength) + (max downTo target step stepLength)  
            else curr downTo target step stepLength  
        }  
        CycleDirection.RIGHT -> {  
            if (curr > target) (curr..max step stepLength) + (min..target step stepLength)  
            else curr..target step stepLength  
        }  
    }  
}  
  
infix fun Int.toLeftCircular(target: Int): Iterable<Int> {  
    return this.circular(min = 0, curr = this, target = target, max = 99, direction = CycleDirection.LEFT)  
}  
infix fun Int.toRightCircular(target: Int): Iterable<Int> {  
    return this.circular(min = 0, curr = this, target = target, max = 99, direction = CycleDirection.RIGHT)  
}
```

**P2 Gemini**
- 鏖战三小时不得不请G老师出山
- G老师针对*终点为0*的情况做了优化，稍微偏转一下指针以计算跨越0的次数
```kotlin
override var dialCurrPoint: Int = dialStartPoint  
    set(value) {  
        val start = field  
        val end = value  

        // 核心逻辑：计算经过了多少次 range 的倍数（包括终点）  
        // 我们判断在 [min(start, end), max(start, end)] 区间内有多少个 0        
        // 但要排除掉起点（因为起点在上一回合已经算过了）  
  
        val delta = end - start  
        val count = if (delta > 0) {  
            // 顺时针旋转：计算 (start, end] 间的 0 点  
            Math.floorDiv(end.toLong(), range.toLong()) - Math.floorDiv(start.toLong(), range.toLong())  
        } else {  
            // 逆时针旋转：计算 [end, start) 间的 0 点  
            // 注意这里：为了包含 end 且排除 start，我们稍微反转一下  
            Math.floorDiv(start.toLong() - 1, range.toLong()) - Math.floorDiv(end.toLong() - 1, range.toLong())  
        }  
  
        password += count.absoluteValue.toInt()  
        field = value  
          
    }
```

***
# 页面底部