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
## Day 2
### Part 1
#### 题目描述
You get inside and take the elevator to its only other stop: the gift shop. "Thank you for visiting the North Pole!" gleefully exclaims a nearby sign. You aren't sure who is even allowed to visit the North Pole, but you know you can access the lobby through here, and from there you can access the rest of the North Pole base.

As you make your way through the surprisingly extensive selection, one of the clerks recognizes you and asks for your help.

As it turns out, one of the younger Elves was playing on a gift shop computer and managed to add a whole bunch of invalid product IDs to their gift shop database! Surely, it would be no trouble for you to identify the invalid product IDs for them, right?

They've even checked most of the product ID ranges already; they only have a few product ID ranges (your puzzle input) that you'll need to check. For example:

```
11-22,95-115,998-1012,1188511880-1188511890,222220-222224,
1698522-1698528,446443-446449,38593856-38593862,565653-565659,
824824821-824824827,2121212118-2121212124
```

(The ID ranges are wrapped here for legibility; in your input, they appear on a single long line.)

The ranges are separated by commas (`,`); each range gives its _first ID_ and _last ID_ separated by a dash (`-`).

Since the young Elf was just doing silly patterns, you can find the _invalid IDs_ by looking for any ID which is made only of some sequence of digits repeated twice. So, `55` (`5` twice), `6464` (`64` twice), and `123123` (`123` twice) would all be invalid IDs.

None of the numbers have leading zeroes; `0101` isn't an ID at all. (`101` is a _valid_ ID that you would ignore.)

Your job is to find all of the invalid IDs that appear in the given ranges. In the above example:

- `11-22` has two invalid IDs, `_11_` and `_22_`.
- `95-115` has one invalid ID, `_99_`.
- `998-1012` has one invalid ID, `_1010_`.
- `1188511880-1188511890` has one invalid ID, `_1188511885_`.
- `222220-222224` has one invalid ID, `_222222_`.
- `1698522-1698528` contains no invalid IDs.
- `446443-446449` has one invalid ID, `_446446_`.
- `38593856-38593862` has one invalid ID, `_38593859_`.
- The rest of the ranges contain no invalid IDs.

Adding up all the invalid IDs in this example produces `_1227775554_`.

_What do you get if you add up all of the invalid IDs?_
#### 解题代码
**解题输出及对应的计算思路**：

| 计算思路                                                                                                 | 输出                                  | 备注                                                    |
| ---------------------------------------------------------------------------------------------------- | ----------------------------------- | ----------------------------------------------------- |
| 区间上下界转`Long`接`Double`，进行以10为底的对数运算，拿到*十进制位数* <br>使用纯数学计算拿到`Long`数值的前半部分和后半部分，比较是否一致<br>若一致则为**无效ID** | 18952700106<br>Too Low<br>601毫秒运行时间 | 以10为底的对数计算过程中，可能会在整十整百之类的数值上面出现*精度丢失*<br>导致一些较大的区间被跳过 |
| 区间上下界转`Long`接`String`<br>若字符串长度不为偶数则直接排除<br>然后对半分割字符串，比较前后是否一致                                       | *同上*                                | 思路一和思路二都使用`MutableSet`<br>暂存ID序列，可能不小心去重了ID           |
|                                                                                                      | 18952700150                         | 发现字符串切割时不知道为什么把最后一个区间给漏掉了，恰好漏了最后一个ID                  |

| 计算思路                                                                                                                                                                | 关键计算代码                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 区间上下界转`Long`接`Double`，进行以10为底的对数运算，拿到*十进制位数* <br>使用纯数学计算拿到`Long`数值的前半部分和后半部分，比较是否一致<br>若一致则为**无效ID**                                                                | fun Long.invalidOrNull(): Long? {<br>    // 十进制位数长度<br>    val rawDecimalLen = log10(this.toDouble())<br>    val decimalLen = ceil(rawDecimalLen)<br>    // 不是偶数长度, 就说明不是前后对称, 直接排除<br>    if (decimalLen % 2 != 0.0) return null<br><br>    val gadge = 10.0.pow(decimalLen / 2)// .also { print("gadge line: $it\|") }<br>    val front = floor(this.toDouble() / gadge)// .also { print("front part is $it\|") }<br>    val back = floor(this.toDouble() % gadge)// .also { println("backend part is $it") }<br><br>    // 如果前半部分和后半部分一样，那就是无效的ID<br>    return if (front == back) this else null<br>} |
| 区间上下界转`Long`接`String`<br>若字符串长度不为偶数则直接排除<br>然后对半分割字符串，比较前后是否一致                                                                                                      | fun Long.invalidOrNull(): Long? {  <br>    val str = this.toString()  <br>    val gap = str.length / 2  <br>    if (str.length % 2 != 0) return null  <br>  <br>    val front = str.substring(0, gap)  <br>    val back = str.substring(gap)  <br>      <br>    return if (front == back) this else null  <br>}                                                                                                                                                                                                                                                                                           |
| 【补丁】<br>Windows文本文件末尾带着个`\r\n`<br>这会导致切割出来的末尾区间带着<br>`\r\n`，`toLongOrNull`时这个末尾换行符<br>会导致转换失败，进而导致程序不会处理<br>位于文件末尾的区间<br><br>补丁就是在解析字符串行之前先调用一下<br>`trim`去除空白字符<br> | infix fun resolveOneLine(input: String): `List<Long>?` {  <br>    val parts = input.trim().split("-")  <br>    if (parts.count() < 2) return null  <br>  <br>    val start = parts`[0]`.toLongOrNull()?: return null  <br>    val end = parts`[1]`.toLongOrNull()?: return null  <br>  <br>    return findInvalidIDs(start..end).also { invalidIDs.addAll(it) }  <br>}<br>                                                                                                                                                                                                                                |

```kotlin
fun Long.invalidOrNull(): Long? {  
    val str = this.toString()  
    val gap = str.length / 2  
    if (str.length % 2 != 0) return null  
  
    val front = str.substring(0, gap)  
    val back = str.substring(gap)  
      
    return if (front == back) this else null  
}  
  
class Day2 {  
    val password: Long  
        get() = invalidIDs.sum()  
    private val invalidIDs: MutableList<Long> = mutableListOf()  
  
    infix fun findInvalidIDs(input: LongRange): List<Long> {  
        return buildList {  
            for (id in input) {  
                // buildList内部的迭代式需要显示调用`add`方法来添加元素到其内部的可变列表中  
                id.also{  
                    // print("processing $it|")  
                }.invalidOrNull()?.let {  
                    println("found invalid id $it in ${input.min()} to ${input.max()}")  
                    add(it)  
                }  
            }  
        }  
    }  
  
    infix fun resolveOneLine(input: String): List<Long>? {  
        val parts = input.trim().split("-")  
        if (parts.count() < 2) return null  
  
        val start = parts[0].toLongOrNull()?: return null  
        val end = parts[1].toLongOrNull()?: return null  
  
        return findInvalidIDs(start..end).also { invalidIDs.addAll(it) }  
    }  
  
    infix fun resolveLines(input: List<String>): List<Long> {  
        val recursivedListLong = buildList {  
            for (l in input) {  
                add(resolveOneLine(l))  
            }  
        }.filterNotNull()  
  
        // 二维列表展平  
        return recursivedListLong.flatten()  
    }  
  
    infix fun resolveFile(filename: String): List<Long>? {  
        val file = File(filename)  
        if (!file.exists()) {  
            println("File ${file.absolutePath} not found!")  
            return null  
        }  
  
        val text = file.readText().split(",")  
  
        return resolveLines(text)  
    }  
  
    fun reset() {  
        invalidIDs.clear()  
    }  
  
    companion object Runner {  
        fun main() {  
            val filename = "src/main/resources/puzzles/2025/day2-part1.txt"  
            val sample = Day2()  
  
            val output = sample.resolveFile(filename)?.let {  
                println(it)  
                println("Answer is ${sample.password}")  
            }?: println("Can't calculate")  
        }  
    }  
}
```

```kotlin
package org.example.Day2  
  
import io.ktor.util.length  
import org.junit.jupiter.api.Assertions.*  
import kotlin.math.ceil  
import kotlin.math.roundToInt  
import kotlin.math.round  
import kotlin.test.Test  
  
class Day2Test {  
    @Test  
    fun testRound() {  
        val sample = Day2()  
  
        val cases = mapOf<Double, Int>(3.1 to 4, 3.9 to 4)  
  
        cases.forEach { d, i -> assertEquals(i, ceil(d).toInt()) }  
    }  
  
    @Test  
    fun testResolveOneLineByOneLine() {  
        val sample = Day2()  
  
        val cases = mapOf(  
            // 11L..22L to listOf(11L, 22L),  
            // 95L .. 115L to listOf(99L),            // 998L .. 1012L to listOf(1010L),            1188511880L .. 1188511890L to listOf(1188511885L),  
            222220L .. 222224L to listOf(222222L),  
            1698522L .. 1698528L to listOf(),  
            446443L .. 446449L to listOf(446446L),  
            38593856L .. 38593862L to listOf(38593859L)  
        )  
  
        cases.forEach { (input, output) ->  
            // 光写一个Lambda函数不会被调用  
            run {  
                // println("$input -> $output")  
                val actualOutput = sample.findInvalidIDs(input)  
                // assertEquals(input.toList().count(), actualOutput.count())  
                assertEquals(output, actualOutput)  
            }  
        }        return  
    }  
  
    @Test  
    fun testResolverLinesString() {  
        val text = "11-22,95-115,998-1012,1188511880-1188511890,222220-222224," +  
                "1698522-1698528,446443-446449,38593856-38593862,565653-565659," +  
                "824824821-824824827,2121212118-2121212124"  
        val lines = text.split(",")  
  
        val sample = Day2()  
        val output = sample.resolveLines(lines)  
        val expectedOutput: List<Long> = listOf(  
            11, 22, 99, 1010, 1188511885, 222222, 446446, 38593859,  
        )  
        println(output)  
        assertEquals(expectedOutput, output)  
        assertEquals(1227775554L, sample.password)  
    }  
  
    @Test  
    fun testResolveFile() {  
        // 测试题目输入样例  
        val filename = "src/main/resources/puzzles/2025/day2-example.txt"  
        val sample = Day2()  
  
        val actualOutput: List<Long> = sample.resolveFile(filename)?: listOf()  
        val expectedOutput: List<Long> = listOf(  
            11, 22, 99, 1010, 1188511885, 222222, 446446, 38593859,  
        )  
  
        println(actualOutput)  
        println("The password is ${sample.password}")  
  
        assertEquals(expectedOutput, actualOutput)  
        assertEquals(1227775554L, sample.password)  
    }  
  
    @Test  
    fun testEdgeCases() {  
        val cases: List<String> = listOf(  
            "35-54",  
            "116-152",  
            "4408053-4520964",  
        )  
  
        val sample = Day2()  
        for (input in cases) {  
            val output = sample.resolveOneLine(input)  
            println("invalid ids in $input is $output")  
        }  
    }  
  
    @Test  
    fun testStringSplit() {  
        val text = "9100-11052,895949-1034027,4408053-4520964,530773-628469,4677-6133,2204535-2244247,55-75,77-96,6855-8537,55102372-55256189,282-399,228723-269241,5874512-6044824,288158-371813,719-924,1-13,496-645,8989806846-8989985017,39376-48796,1581-1964,699387-735189,85832568-85919290,6758902779-6759025318,198-254,1357490-1400527,93895907-94024162,21-34,81399-109054,110780-153182,1452135-1601808,422024-470134,374195-402045,58702-79922,1002-1437,742477-817193,879818128-879948512,407-480,168586-222531,116-152,35-54"  
        val lines = text.split(",")  
        lines.forEach { println(it) }  
  
        assertEquals("35-54", lines.last())  
    }  
}
```

### Part 2
#### 题目描述
The clerk quickly discovers that there are still invalid IDs in the ranges in your list. Maybe the young Elf was doing other silly patterns as well?

Now, an ID is invalid if it is made only of some sequence of digits repeated _at least_ twice. So, `12341234` (`1234` two times), `123123123` (`123` three times), `1212121212` (`12` five times), and `1111111` (`1` seven times) are all invalid IDs.

From the same example as before:

- `11-22` still has two invalid IDs, `_11_` and `_22_`.
- `95-115` now has two invalid IDs, `_99_` and `_111_`.
- `998-1012` now has two invalid IDs, `_999_` and `_1010_`.
- `1188511880-1188511890` still has one invalid ID, `_1188511885_`.
- `222220-222224` still has one invalid ID, `_222222_`.
- `1698522-1698528` still contains no invalid IDs.
- `446443-446449` still has one invalid ID, `_446446_`.
- `38593856-38593862` still has one invalid ID, `_38593859_`.
- `565653-565659` now has one invalid ID, `_565656_`.
- `824824821-824824827` now has one invalid ID, `_824824824_`.
- `2121212118-2121212124` now has one invalid ID, `_2121212121_`.

Adding up all the invalid IDs in this example produces `_4174379265_`.

_What do you get if you add up all of the invalid IDs using these new rules?_
#### 解题代码
| 计算思路        | 关键计算代码                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 直接暴力穷举字符串片段 | fun Long.invalidOrNullV2(): Long? {  <br>    val str = this.toString()  <br>    // 至少重复两次, 所以字符串长度小于2的都丢掉  <br>    if (str.length < 2) return null  <br>  <br>    for (i in 1..(str.length / 2)) {  <br>        val sub = str.substring(0, i)  <br>        val concated = sub.repeat(str.length / i)  <br>        // println("$str -> \|snippet: $sub\|concat string: $concated")  <br>        if (str == concated) return this  <br>    }  <br>  <br>    return null  <br>} |
历时16.7秒一步到位算出正确答案：
```
[9191, 9292, 9393, 9494, 9595, 9696, 9797, 9898, 9999, 896896, 897897, 898898, 898989, 899899, 900900, 901901, 902902, 903903, 904904, 905905, 906906, 907907, 908908, 909090, 909909, 910910, 911911, 912912, 913913, 914914, 915915, 916916, 917917, 918918, 919191, 919919, 920920, 921921, 922922, 923923, 924924, 925925, 926926, 927927, 928928, 929292, 929929, 930930, 931931, 932932, 933933, 934934, 935935, 936936, 937937, 938938, 939393, 939939, 940940, 941941, 942942, 943943, 944944, 945945, 946946, 947947, 948948, 949494, 949949, 950950, 951951, 952952, 953953, 954954, 955955, 956956, 957957, 958958, 959595, 959959, 960960, 961961, 962962, 963963, 964964, 965965, 966966, 967967, 968968, 969696, 969969, 970970, 971971, 972972, 973973, 974974, 975975, 976976, 977977, 978978, 979797, 979979, 980980, 981981, 982982, 983983, 984984, 985985, 986986, 987987, 988988, 989898, 989989, 990990, 991991, 992992, 993993, 994994, 995995, 996996, 997997, 998998, 999999, 4444444, 531531, 532532, 533533, 534534, 535353, 535535, 536536, 537537, 538538, 539539, 540540, 541541, 542542, 543543, 544544, 545454, 545545, 546546, 547547, 548548, 549549, 550550, 551551, 552552, 553553, 554554, 555555, 556556, 557557, 558558, 559559, 560560, 561561, 562562, 563563, 564564, 565565, 565656, 566566, 567567, 568568, 569569, 570570, 571571, 572572, 573573, 574574, 575575, 575757, 576576, 577577, 578578, 579579, 580580, 581581, 582582, 583583, 584584, 585585, 585858, 586586, 587587, 588588, 589589, 590590, 591591, 592592, 593593, 594594, 595595, 595959, 596596, 597597, 598598, 599599, 600600, 601601, 602602, 603603, 604604, 605605, 606060, 606606, 607607, 608608, 609609, 610610, 611611, 612612, 613613, 614614, 615615, 616161, 616616, 617617, 618618, 619619, 620620, 621621, 622622, 623623, 624624, 625625, 626262, 626626, 627627, 4747, 4848, 4949, 5050, 5151, 5252, 5353, 5454, 5555, 5656, 5757, 5858, 5959, 6060, 2222222, 55, 66, 77, 88, 6868, 6969, 7070, 7171, 7272, 7373, 7474, 7575, 7676, 7777, 7878, 7979, 8080, 8181, 8282, 8383, 8484, 55105510, 55115511, 55125512, 55135513, 55145514, 55155515, 55165516, 55175517, 55185518, 55195519, 55205520, 55215521, 55225522, 55235523, 55245524, 55255525, 333, 229229, 230230, 231231, 232232, 232323, 233233, 234234, 235235, 236236, 237237, 238238, 239239, 240240, 241241, 242242, 242424, 243243, 244244, 245245, 246246, 247247, 248248, 249249, 250250, 251251, 252252, 252525, 253253, 254254, 255255, 256256, 257257, 258258, 259259, 260260, 261261, 262262, 262626, 263263, 264264, 265265, 266266, 267267, 268268, 288288, 289289, 290290, 291291, 292292, 292929, 293293, 294294, 295295, 296296, 297297, 298298, 299299, 300300, 301301, 302302, 303030, 303303, 304304, 305305, 306306, 307307, 308308, 309309, 310310, 311311, 312312, 313131, 313313, 314314, 315315, 316316, 317317, 318318, 319319, 320320, 321321, 322322, 323232, 323323, 324324, 325325, 326326, 327327, 328328, 329329, 330330, 331331, 332332, 333333, 334334, 335335, 336336, 337337, 338338, 339339, 340340, 341341, 342342, 343343, 343434, 344344, 345345, 346346, 347347, 348348, 349349, 350350, 351351, 352352, 353353, 353535, 354354, 355355, 356356, 357357, 358358, 359359, 360360, 361361, 362362, 363363, 363636, 364364, 365365, 366366, 367367, 368368, 369369, 370370, 371371, 777, 888, 11, 555, 8989889898, 8989898989, 44444, 1616, 1717, 1818, 1919, 699699, 700700, 701701, 702702, 703703, 704704, 705705, 706706, 707070, 707707, 708708, 709709, 710710, 711711, 712712, 713713, 714714, 715715, 716716, 717171, 717717, 718718, 719719, 720720, 721721, 722722, 723723, 724724, 725725, 726726, 727272, 727727, 728728, 729729, 730730, 731731, 732732, 733733, 734734, 85838583, 85848584, 85858585, 85868586, 85878587, 85888588, 85898589, 85908590, 85918591, 6758967589, 222, 93899389, 93909390, 93919391, 93929392, 93939393, 93949394, 93959395, 93969396, 93979397, 93989398, 93999399, 94009400, 94019401, 22, 33, 88888, 99999, 100100, 101010, 101101, 102102, 103103, 104104, 105105, 106106, 107107, 108108, 111111, 112112, 113113, 114114, 115115, 116116, 117117, 118118, 119119, 120120, 121121, 121212, 122122, 123123, 124124, 125125, 126126, 127127, 128128, 129129, 130130, 131131, 131313, 132132, 133133, 134134, 135135, 136136, 137137, 138138, 139139, 140140, 141141, 141414, 142142, 143143, 144144, 145145, 146146, 147147, 148148, 149149, 150150, 151151, 151515, 152152, 153153, 422422, 423423, 424242, 424424, 425425, 426426, 427427, 428428, 429429, 430430, 431431, 432432, 433433, 434343, 434434, 435435, 436436, 437437, 438438, 439439, 440440, 441441, 442442, 443443, 444444, 445445, 446446, 447447, 448448, 449449, 450450, 451451, 452452, 453453, 454454, 454545, 455455, 456456, 457457, 458458, 459459, 460460, 461461, 462462, 463463, 464464, 464646, 465465, 466466, 467467, 468468, 469469, 374374, 375375, 376376, 377377, 378378, 379379, 380380, 381381, 382382, 383383, 383838, 384384, 385385, 386386, 387387, 388388, 389389, 390390, 391391, 392392, 393393, 393939, 394394, 395395, 396396, 397397, 398398, 399399, 400400, 401401, 66666, 77777, 1010, 1111, 1212, 1313, 1414, 742742, 743743, 744744, 745745, 746746, 747474, 747747, 748748, 749749, 750750, 751751, 752752, 753753, 754754, 755755, 756756, 757575, 757757, 758758, 759759, 760760, 761761, 762762, 763763, 764764, 765765, 766766, 767676, 767767, 768768, 769769, 770770, 771771, 772772, 773773, 774774, 775775, 776776, 777777, 778778, 779779, 780780, 781781, 782782, 783783, 784784, 785785, 786786, 787787, 787878, 788788, 789789, 790790, 791791, 792792, 793793, 794794, 795795, 796796, 797797, 797979, 798798, 799799, 800800, 801801, 802802, 803803, 804804, 805805, 806806, 807807, 808080, 808808, 809809, 810810, 811811, 812812, 813813, 814814, 815815, 816816, 879879879, 444, 169169, 170170, 171171, 171717, 172172, 173173, 174174, 175175, 176176, 177177, 178178, 179179, 180180, 181181, 181818, 182182, 183183, 184184, 185185, 186186, 187187, 188188, 189189, 190190, 191191, 191919, 192192, 193193, 194194, 195195, 196196, 197197, 198198, 199199, 200200, 201201, 202020, 202202, 203203, 204204, 205205, 206206, 207207, 208208, 209209, 210210, 211211, 212121, 212212, 213213, 214214, 215215, 216216, 217217, 218218, 219219, 220220, 221221, 222222, 44]
Answer is 28858486244
```
### 使用到的API和语法以及优化建议
#### 作用域函数
##### `also`
```kotlin
@IgnorableReturnValue
@InlineOnly
@SinceKotlin
public inline fun <T> T.also(
    block: (T) -> Unit
): T
```
用于在链式操作中进行调试打印

![](assets/Pasted%20image%2020260308191217.png)
##### `let` 非空分支下执行语句
通常和`?.`连用，用于在前置变量不为`null`时执行`let{}`函数体中的操作
#### 列表操作
##### `buildList`构造不可变列表
**例：**
```kotlin
val list = buildList {
    add(1)
    add(2)
    add(3)
    addAll(listOf(4, 5))
}

println(list)  // 输出: [1, 2, 3, 4, 5]
```
- 当`buildList{}`传入的lambda函数体为空时，`buildList`返回`List<T>`类型的不可变空列表
	- **不可变**在这里指修改列表本身，无法使用`add`、`remove`等修改列表自身的操作

在题目中用于构造包含指定区间中所有**无效ID**的`List<Long>`：
```kotlin
open infix fun findInvalidIDs(input: LongRange): List<Long> {  
    return buildList {  
        for (id in input) {  
            id.invalidOrNull()?.let {  
                println("found invalid id $it in ${input.min()} to ${input.max()}")  
                add(it)  
            }  
        }  
    }  
}
```
- 【条件添加】使用了`?.let`操作符，仅当给定长整型数值为**无效ID**（也就是不为`null`时才执行`add`操作）
##### `filterNotNull`过滤`null`元素
```kotlin
val list = listOf(1, null, 2, null, 3, null, 4)

val result = list.filterNotNull()
println(result)  // 输出: [1, 2, 3, 4]
```

题目中用于清洗`resolveOneLine`产生的`null`值：
```kotlin
infix fun resolveOneLine(input: String): List<Long>? {  
    val parts = input.split("-")  
    if (parts.count() < 2) return null  
  
    val start = parts[0].toLongOrNull()?: return null  
    val end = parts[1].toLongOrNull()?: return null  
  
    return findInvalidIDs(start..end).also { invalidIDs.addAll(it) }  
}
infix fun resolveLines(input: List<String>): List<Long> {  
    val recursivedListLong = buildList {  
        for (l in input) {  
            add(resolveOneLine(l))  
        }  
    }.filterNotNull()  
  
    // 二维列表展平  
    return recursivedListLong.flatten()  
}
```
- `resolveOneLine`采用快速`null`返回机制，配合`resolveLines`中的`filterNotNull`，可以移除那些可能无效的区间带来的脏数据

##### `map`映射转换列表中的元素
对集合中的每个元素应用指定的转换函数，返回新的列表。
```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val squares = numbers.map { it * it }
println(squares)  // 输出: [1, 4, 9, 16, 25]

val doubled = numbers.map { it * 2 }
println(doubled)  // 输出: [2, 4, 6, 8, 10]
```

题目中用于辅助去除文本字符串列表元素两端的空白字符：
![](assets/Pasted%20image%2020260308192832.png)

##### flatten列表展平
```kotlin
val nested = listOf(listOf(1, 2), listOf(3, 4), listOf(5, 6))

val flattened = nested.flatten()
println(flattened)  // 输出: [1, 2, 3, 4, 5, 6]
```

题目中用于展开`resolveLines`函数的中间结果`List<List<Long>>`：
![](assets/Pasted%20image%2020260308192447.png)
##### `sum`计算列表中的值的总和
```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers.sum()
println(result)  // 输出: 15
```

题目中用于计算缓存`invalidIDs`列表中所有无效ID的数值和：
```kotlin
val password: Long  
    get() = invalidIDs.sum()  // 绑在password的getter方法上
private val invalidIDs: MutableList<Long> = mutableListOf()

infix fun resolveOneLine(input: String): List<Long>? {  
    val parts = input.split("-")  
    if (parts.count() < 2) return null  
  
    val start = parts[0].toLongOrNull()?: return null  
    val end = parts[1].toLongOrNull()?: return null  
  
    return findInvalidIDs(start..end).also { invalidIDs.addAll(it) }  
}
```

##### 【优化建议】`Sequence<Long>`替换`List<Long>`
尽管题目给出的区间跨度并不大，但`List<Long>`毕竟没有缓存机制，ID太多的时候仍然可能造成OOM
可以考虑`Sequence`类型，它是**流式处理**的，处理完一个数值就丢弃一个，不会占用*中间集合内存* ：
```kotlin
fun findInvalidIDsLazy(input: LongRange): Sequence<Long> = 
    input.asSequence().filter { it.isInvalidPart2() } 
    // 这里需要设置isInvalidPart2的返回值类型为Boolean

// 使用时
val total = findInvalidIDsLazy(range).sum()
```
#### 键值对操作
##### `forEach`键值对遍历

- 如果一定要在`(k, v) ->`后面用`{}`包裹语句，那么得用`run`或其他能够执行lambda函数的东西来运行`{}`中的语句，否则Kotlin编译器会把`{}`本身当成（惰性求值）的lambda函数
```kotlin
val cases = mapOf(  
    // 11L..22L to listOf(11L, 22L),  
    // 95L .. 115L to listOf(99L),    
    // 998L .. 1012L to listOf(1010L),    
    1188511880L .. 1188511890L to listOf(1188511885L),  
    222220L .. 222224L to listOf(222222L),  
    1698522L .. 1698528L to listOf(),  
    446443L .. 446449L to listOf(446446L),  
    38593856L .. 38593862L to listOf(38593859L)  
)  
  
cases.forEach { (input, output) ->  
    // 光写一个Lambda函数不会被调用  
    run {  
        // println("$input -> $output")  
        val actualOutput = sample.findInvalidIDs(input)  
        // assertEquals(input.toList().count(), actualOutput.count())  
        assertEquals(output, actualOutput)  
    }  
}
```
#### 字符串操作
##### `split`根据指定的分隔符分割字符串
```kotlin
val str = "Hello,World,Kotlin"
val parts = str.split(",")
println(parts)  // 输出: [Hello, World, Kotlin]
```

题目中用于按`,`逗号分隔单行文本，生成区间字符串列表：
```kotlin
infix fun resolveFile(filename: String): List<Long>? {  
    val file = File(filename)  
    if (!file.exists()) {  
        println("File ${file.absolutePath} not found!")  
        return null  
    }  
  
    val text = file.readText().split(",").map { it.trim() }  
  
    return resolveLines(text)  
}
```
##### `trim`移除字符串两端的空白字符
```kotlin
val str = "  Hello World  "
println(str.trim())  // 输出: Hello World
```

题目中用于移除Windows文件末尾可能的`\r\n`字符，避免影响`toLongOrNull`的解析：
![](assets/Pasted%20image%2020260308192330.png)
##### `substring`按索引或迭代切割子字符串
提取子字符串
```kotlin
val str = "Hello World"
println(str.substring(0, 5))  // 输出: Hello
println(str.substring(6))  // 输出: World
```

题目中用于切割给定长整型数值的`String`值的前半部分与后半部分：
![](assets/Pasted%20image%2020260308193014.png)

##### 【优化建议】`take`与`takeLast`提取子字符串
> 可以替换`substring`函数

- 取前 n 个字符
```kotlin
val str = "Hello World"
println(str.take(5))  // 输出: Hello
```
- 取后 n 个字符
```kotlin
val str = "Hello World"
println(str.takeLast(5))  // 输出: World
```

#### `null`检查
##### `?.let`操作
仅当前体变量不为`null`时才执行`let{}`函数体中的操作

#### 扩展函数
参考**语法**：
```kotlin
fun 已有类型.函数名() {
	// 函数体
}
```

在本题中用于拓展`Long`的函数，便携计算给定`Long`是否为无效ID：
```kotlin
fun Long.invalidOrNull(): Long? {  
    val str = this.toString()  
    val gap = str.length / 2  
    if (str.length % 2 != 0) return null  
  
    val front = str.substring(0, gap)  
    val back = str.substring(gap)  
      
    return if (front == back) this else null  
}
```
- 将返回值设为可空的`Long`类型，配合调用方的`?.let`操作符，可以避免把`null`值添加到列表中
#### 其他
##### `toLongOrNull`
[详情请见](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.text/to-long-or-null.html)

##### 非抽象类的继承
- 被继承的类需要使用`open`修饰；Kotlin的类默认是`final`的，不可继承的
- 父类中的属性或方法若要被继承，也需要使用`open`来修饰
```kotlin
open class Parent

class Child: Parent() {}
```
- 子类不需要继承的属性和方法就不用写，Kotlin会自动调用父类的字段

![](assets/Pasted%20image%2020260308194438.png)

##### 伴生对象
- **伴生对象**是类级别的共享`static`变量
```kotlin
class cls{
	companion object Somebody{}
}
```

题目中用于创建与具体的类绑定的`main`方法，避免与`Main.kt`的`main`函数冲突，也便于快速调用解题：
![](assets/Pasted%20image%2020260308194707.png)

##### `LongRange`
- `Int`类型对应的区间迭代器是`IntRange`
- `Long`类型对应的区间迭代器是`LongRange`

![](assets/Pasted%20image%2020260308194902.png)
***
# 页面底部