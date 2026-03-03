---
title: Kotlin 标准库扫盲：文件操作
date: 2026-03-02
---
[[toc]]
- **第一阶段**：基础读写
- **第二阶段**：大文件处理 与 内存优化
- **第三阶段**：文件与目录管理
- **第四阶段**：核心工具——`use`函数

***
## 文件操作
### 基础读写
使用`java.io.File`库进行演示：
```kotlin
import java.io.File

// 仅仅是创建了一个文件句柄（引用），并不会在硬盘上生成文件
val file = File("test.txt")
```
#### 文件读取
Kotlin 提供了三种最直接的读取方式，它们都有一个可选参数：`charset`（编码），默认是 `Charsets.UTF_8`。

##### 1. `readText()`：一把梭读取
适合配置文件、小文章。
- **用法：** `val content = file.readText()`
- **细节：** 它内部其实是开了流，读完后帮你自动关闭了。
- **风险：** 如果文件 1GB，你的内存会直接爆掉（`OutOfMemoryError`）。

##### 2. `readLines()`：按行切割
返回一个 `List<String>`，每一行是一个元素（自动去掉了换行符）。
- **用法：** `val lines = file.readLines()`
- **场景：** 适合处理那种每行代表一条记录的文件（如 CSV 的简单版）。

##### 3. `readBytes()`：二进制原始数据
- **用法：** `val bytes = file.readBytes()`
- **场景：** 读取图片、音频或加密文件。

```kotlin
import java.io.File  
import kotlin.test.Test  

class BasicFileOperationTest {  
    // 只是创建了一个文件句柄  
    private val fileForRead = File("src/main/resources/tmp/novels.txt")  
  
    // 读操作测试  
    // 读取文件时如果找不到文件会抛出FileNotFoundException  
    @Test  
    fun testReadText() {  
        val content = fileForRead.readText()  
  
        println(content)  
        /*  
         晨雾如液态的白银般流淌在翡翠色的山谷之间，  
         古老的浮空岛屿在云层之上缓缓旋转，         它们的底部垂挂着千年藤蔓与发光的晶簇，  
        * */    }  
  
    @Test  
    fun testReadLines() {  
        val lines = fileForRead.readLines()  
  
        for ((idx, line) in lines.withIndex()) {  
            println("Line ${idx + 1}: $line")  
        }  
        /*  
        Line 1:  晨雾如液态的白银般流淌在翡翠色的山谷之间，  
        Line 2:  古老的浮空岛屿在云层之上缓缓旋转，  
        Line 3:  它们的底部垂挂着千年藤蔓与发光的晶簇，  
        * */    }  
  
    @Test  
    fun testReadBytes() {  
        val bytes = fileForRead.readBytes()  
  
        println(bytes) // 不是二进制数据, 测试不出来, 看看就好  
    }  
}
```
#### 文件写入
##### 1. `writeText(text)`：**覆盖写入**
```kotlin
	val file = File("hello.txt")
	file.writeText("第一次写入")
	file.writeText("第二次写入") // 此时文件内容只有“第二次写入”，旧内容被清空了
```
##### 2. `appendText(text)`：**追加写入**
```kotlin
	file.appendText("\n我是追加的内容") 
	// \n 是换行符，如果你想另起一行，别忘了加它
```
##### 3. `writeBytes(byteArray)`：**二进制写入**
> 常用于保存从网络下载的数据包

```kotlin
import java.io.File  
import kotlin.test.Test  
import kotlin.test.assertEquals  
  
class BasicFileOperationTest {  
    // 只是创建了一个文件句柄  
    private val fileForRead = File("src/main/resources/tmp/novels.txt")  

  
    // 写操作测试  
    private val resourcePath = "src/main/resources/tmp"  
    @Test  
    fun testWriteText() {  
        val file = File("$resourcePath/override.txt")  
  
        file.writeText("第一次写入").also {  
            println("文件内容: ${file.readText()}")  
        }  
        file.writeText("第二次写入").also {  
            println("文件内容: ${file.readText()}")  
        }  
  
        assertEquals("第二次写入", file.readText())  
    }  
  
    @Test  
    fun testAppendText() {  
        val file = File("$resourcePath/append.txt")  
        // 显式清空  
        file.writeText("")  
  
        file.appendText("第一次写入").also {  
            println("文件内容:\n===START===\n ${file.readText()} \n===END===END")  
        }  
        file.appendText("\n第二次写入").also {  
            println("文件内容:\n===START===\n ${file.readText()} \n===END===END")  
        }  
  
        assertEquals("第一次写入\n第二次写入", file.readText())  
    }  
}
```
#### 注意事项
##### 编码转换
```kotlin
// 读取一个 Windows 上古时期的 GBK 文件
val gbkContent = file.readText(charset("GBK"))

// 以 ISO_8859_1 编码写入文件
file.writeText("Some text", Charsets.ISO_8859_1)
```

##### 防御性编程
直接读写一个不存在的文件会抛出 `FileNotFoundException`，有必要的话应该检查文件是否存在：
```kotlin
val file = File("data.txt")

if (file.exists()) {
    val text = file.readText()
    println(text)
} else {
    println("文件还没准备好呢！")
    // 或者你可以先创建它
    file.createNewFile() 
}
```

或者进行异常捕获（代码为AoC 2025 Day1的解题测试代码）：
```kotlin
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

### 进阶读写：大文件处理与内存优化
> 在上一节中，我们用的 readText() 和 readLines() 会把文件的**所有内容**一次性加载到内存里。
- 如果文件 10KB，没问题。
- 如果文件 1GB，而分配给程序的内存只有 512MB，程序会直接崩溃（**`OutOfMemoryError`**）。
> 为了解决这个问题，我们需要“**流式读取（Streaming）**”——也就是每次只读一小块，处理完再读下一块。

##### 1. `forEachLine`：**最省心的逐行处理**
这是 Kotlin 最推荐的日常方案。它会一行一行读取文件，处理完一行就丢掉，内存占用极低
```kotlin
val file = File("big_data.txt")

file.forEachLine { line ->
    // 每次内存里只存在这一行字符串
    if (line.contains("Error")) {
        println(line)
    }
}
// 执行完毕后，文件流会自动关闭，非常安全
```

##### 2. `useLines`：**强大的序列操作**
如果你不仅想遍历，还想用 `filter`（过滤）、`map`（转换）、`take`（取前几行）等高级操作，`useLines` 是神兵利器。

它返回的是一个 `Sequence`（序列）。序列是**惰性求值**的，只有当你真正需要数据时，它才会去读文件
```kotlin
val file = File("logs.txt")

val errorCount = file.useLines { lines ->
    // 这里的 lines 是 Sequence<String>
    lines.filter { it.startsWith("2023") }
         .filter { it.contains("ERROR") }
         .count() // 直到调用 count()，读取操作才会真正开始
}

println("2023年的错误条数: $errorCount")
```
- **注意：** 必须在 `useLines` 的花括号 `{}` 内部完成操作，因为一旦跳出花括号，文件流就会关闭，无法再读取

##### 3. `bufferedReader`：**更底层的控制**
如果你需要更精细的控制（比如一次读 4096 个字节，或者手动判断 `readLine()` 是否为空），可以使用 Java 风格的缓冲读取器，但结合 Kotlin 的 `.use`
```kotlin
val file = File("data.txt")

file.bufferedReader().use { reader ->
    var line: String?
    while (reader.readLine().also { line = it } != null) {
        println(line)
    }
}
```
- `.use` 的作用：即使在读取过程中发生了报错，它也保证会把 reader 关闭

| 方法          | 返回值          | 内存占用        | 适用场景            |
| ----------- | ------------ | ----------- | --------------- |
| readText()  | String       | **高** (全加载) | 配置文件、小文本        |
| readLines() | List<String> | **高** (全加载) | 小文本，且需要通过索引访问各行 |
| forEachLine | Unit         | **极低**      | 简单地逐行处理大文件      |
| useLines    | T (自定义)      | **极低**      | 需要对大文件进行复杂过滤、转换 |

```kotlin
class EnhancedFileOperationTest {  
    // 网上搞来的20000行Linux API手册  
    private val file = File("src/main/resources/tmp/index.html")  
  
    @Test  
    fun testForEachLine() {  
        file.forEachLine {  
            line -> if (line.contains("<div class=\"")) println(line)  
        }  
    }  
  
    @Test  
    fun testUseLines() {  
        // 就取50行得了  
        val matchedLines =  file.useLines {  
            lines -> lines.filter {  
                it.contains("<div class=\"")  
        }.take(50).count()  
        }  
  
        assertEquals(50, matchedLines) // 没道理没有50个div  
        // for (line in matchedLines) println(line)  
		// file.useLines本身是惰性的, matchedLines也会是惰性的，流关闭之后就读不出东西来了
    }  
}
```

### 文件与目录管理
##### 1. 文件属性查看
Kotlin 为 `File` 对象提供了几个非常贴心的扩展属性，处理文件名时再也不用自己去找那个“点” `.` 在哪里了。

```kotlin
val file = File("src/main/kotlin/Main.kt")

println(file.name)                // Main.kt
println(file.extension)           // kt (后缀名)
println(file.nameWithoutExtension)// Main (不带后缀的文件名)
println(file.parent)              // src/main/kotlin
println(file.length())            // 文件大小（字节）
```

##### 2. 目录管理
*   **创建目录**：
    *   `mkdir()`: 创建单层目录，如果父目录不存在则失败。
    *   `mkdirs()`: **常用**，递归创建所有不存在的父目录（类似 `mkdir -p`）。
*   **删除**：
    *   `delete()`: 删除文件或**空**目录。
    *   `deleteRecursively()`: **大杀器**，删除目录及其内部所有子文件（类似 `rm -rf`）。
*   **重命名/移动**：
    *   `renameTo(destFile)`: 成功返回 true。注意，跨硬盘分区移动可能会失败。

##### 3.  文件树遍历： `File.walk()` 
这是 Kotlin 相比 Java 最方便的地方之一。它返回一个 `Sequence<File>`，可以让你用函数式编程的方式横扫整个硬盘。

###### 常用三种模式：
1.  **`walk()`**: 默认模式（通常是从上往下）。
2.  **`walkTopDown()`**: 从上往下（先处理文件夹，再处理里面的文件）。
3.  **`walkBottomUp()`**: 从下往上（先处理文件，最后处理最外层文件夹，适合**清空式删除**）。

```kotlin
val root = File("my_project")

root.walk()
    .maxDepth(3) // 限制深度，防止扫全盘
    .onEnter { dir -> 
        println("正在进入目录: ${dir.name}")
        true // 返回 true 表示继续进入，false 表示跳过此目录
    }
    .filter { it.isFile && it.extension == "pdf" }
    .filter { it.length() > 1024 * 1024 } // 大于 1MB
    .forEach { 
        println("找到大PDF文件: ${it.absolutePath}") 
    }
```

##### 4. 复制操作：`copyTo` 与 `copyRecursively`
Kotlin 让复制变得像拼单词一样简单。

```kotlin
val source = File("config.json")
val backup = File("config.json.bak")

// 1. 简单复制文件
source.copyTo(backup, overwrite = true) 

// 2. 递归复制整个文件夹
val srcDir = File("photos")
val destDir = File("photos_backup")
srcDir.copyRecursively(destDir, overwrite = true) { file, exception ->
    // 错误处理器：如果某个文件复制失败，该怎么办？
    println("复制 ${file.name} 失败: ${exception.message}")
    OnErrorAction.TERMINATE // 或者 OnErrorAction.SKIP
}
```


```kotlin
class DirectoryOperationTest {  
    @Test  
    fun retrieveFileStat() {  
        val yes = "是"  
        val no = "否"  
        val file = File("src/main/resources/tmp/澤野弘之 - 4ゅN.flac")  
  
        println(file.name)  
        assertEquals("澤野弘之 - 4ゅN.flac", file.name)  
        println(file.extension)  
        assertEquals("flac", file.extension)  
        println(file.absolutePath)  
        println(file.nameWithoutExtension)  
        assertEquals("澤野弘之 - 4ゅN", file.nameWithoutExtension)  
        println("这是文件吗? ${file.isFile}")  
        assertEquals(true, file.isFile)  
        println(file.parent)  
        assertEquals("src\\main\\resources\\tmp", file.parent)  
        println("这是目录吗? ${file.isDirectory}")  
        assertEquals(false, file.isDirectory)  
        println(file.length())  
        println("文件被隐藏了吗? ${file.isHidden}")  
        assertEquals(false, file.isHidden)  
    }  
  
    @Test  
    fun testDirectoryOperation() {  
        val rootDir = File("src/main/resources/tmp")  
        assertEquals(true, rootDir.exists())  
        assertEquals(true, rootDir.isDirectory)  
  
        val appendiceDir = File("${rootDir.absolutePath}\\a\\b\\c")  
        if (!appendiceDir.mkdirs()) {  
            println("创建目录失败")  
            return  
        }  
        assertEquals(true, appendiceDir.exists())  
        val tobeDeletedDir = File("${rootDir.absolutePath}\\a")  
        if (!tobeDeletedDir.deleteRecursively()) { // 递归删除测试目录  
            println("删除目录失败")  
            return  
        }  
        assertEquals(false, tobeDeletedDir.exists())  
    }  
  
    @Test  
    fun testFileTreeWalk() {  
        val root = File(".") // IDEA的工作目录默认为项目根目录  
  
        root.walk().maxDepth(5) // 扫个五层吧  
            .onEnter {  
                dir ->  
                    println("进入目录: ${dir.absolutePath}")  
                    true  
            }  
            .onLeave { dir ->  
                // println("离开目录: ${dir.absolutePath}")  
            }  
            .filter { it.extension == "kt" }  
            .forEach { println("找到Kotlin代码文件: ${it.absolutePath}") }  
	        // 进入目录: F:\KotlinProjects\AoC2025\.\src\test\kotlin\ApiLearning  
            //找到Kotlin代码文件: F:\KotlinProjects\AoC2025\.\src\test\kotlin\ApiLearning\FileOperationTest.kt  
            //进入目录: F:\KotlinProjects\AoC2025\.\src\test\kotlin\Day1  
    }  
    
    @Test  
	fun testComprehensiveExamination() {  
	    val root = File(".")  
	    val archive = File("src/main/resources/tmp/archive")  
	    if (!archive.exists()) {  
	        if (!archive.mkdirs()) {  
	            println("${archive.absolutePath}目录创建失败")  
	            return  
	        }  
	    }  
	  
	    root.walk().maxDepth(5)  
	        .filter { it.isFile }  
	        .filter { it.extension == "html" || it.extension == "txt" }  
	        .filter { it.length() < 10 * 1024 } // 小于10KB的文件  
	        .forEach {  
	            val source = it  
	            val target = File("${archive.absolutePath}/${it.nameWithoutExtension}_${it.length()}.${it.extension}")  
	  
	            it.copyTo(target, overwrite = true)  
	  
	            println("${source.name} copied to ${target.name}")  
	        }  
	}
}
```

![](assets/Pasted%20image%2020260302213113.png)


#### 注意事项
:::important 注意事项
1.  **返回值检查**：很多操作（如 `mkdir`）返回的是 `Boolean`。如果你不检查，可能目录没创建成功，后面的写文件代码就报错了。
2.  **绝对路径 vs 相对路径**：
    *   在服务器/PC上，相对路径是相对于 JVM 启动目录。
    *   调用 `file.absolutePath` 永远比 `file.path` 更保险。
3.  **符号链接（Symbolic Links）**：`walk()` 默认会跟踪符号链接。如果目录结构存在死循环，可能会出问题（虽然不常见）。
:::
### `use`作用域函数
> 在 Java 里，如果你手动打开一个 `FileInputStream`，你必须在 `finally` 块里关掉它。在 Kotlin 中，我们基本不手动关流，我们用 **`.use()`**。

##### 1. `.use` 的威力
`.use` 是一个扩展函数，它可以用在所有实现了 Closeable 接口的对象上。它保证了：**无论代码运行成功还是抛出异常，花括号结束时，流都会自动关闭。**

```kotlin
// 传统的底层写法（读取第一行）
val firstLine = File("config.txt").bufferedReader().use { reader ->
    reader.readLine() // 处理完后，reader 自动 close
}
```

##### 2. 写操作的“原子性”与安全
对于写操作，Kotlin 也提供了底层的 `outputStream()`。

```kotlin
File("output.bin").outputStream().use { stream ->
    stream.write(byteArrayOf(65, 66, 67))
} // 流在这里安全关闭
```
## 协程
- 🟢 **第一阶段：基本概念与“挂起”的真相**
	- **核心目标**：理解协程到底是什么，以及 `suspend` 关键字的神奇之处。
	- **关键词**：`launch`, `runBlocking`, `delay`, `suspend`。
	- **解决痛点**：为什么不能在普通函数里调用挂起函数？协程比线程快在哪？

- **🟡 第二阶段：结构化并发 (Structured Concurrency)**
	- **核心目标**：学习如何管理协程，避免“内存泄漏”和“孤儿协程”。
	- **关键词**：`CoroutineScope`, `GlobalScope`, `cancel`, `Job`。
	- **解决痛点**：当 Activity/页面 销毁时，还没跑完的后台任务怎么自动关掉？

- **🟠 第三阶段：上下文与调度器 (Context & Dispatchers)**
	- **核心目标**：决定协程跑在哪个线程上。
	- **关键词**：`Dispatchers.Main`, `Dispatchers.IO`, `Dispatchers.Default`, `withContext`。
	- **解决痛点**：如何在后台读文件（IO），然后回到主线程更新界面（Main）？

- **🔴 第四阶段：并发进阶与异常处理**
	- **核心目标**：多个任务同时跑，以及其中一个崩了怎么办。
	- **关键词**：`async`, `await`, `coroutineScope`, `SupervisorJob`。
	- **解决痛点**：同时下载三个文件，全部下载完后再提示用户，如果一个失败了，其他两个要不要停？

#### 依赖补全
:::note 参考文档
- [官方 - 协程指南](https://kotlinlang.org/docs/coroutines-guide.html)
:::

协程不是标准库的一部分，而是官方扩展库。因此需要在`build.gradle.kts`里加上依赖：
```kotlin
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
}
```
### 第一阶段：基本概念与协程挂起
- **关键字**
	**协程**最核心的**关键字**是 `suspend`。
	-  **表面看**：被 `suspend` 修饰的函数可以调用其他的 `suspend` 函数（比如 `delay`）。
	-  **本质看**：`suspend` 意味着 **“暂时剥夺这个函数运行的权利”**。
	**核心规则**：suspend 函数只能在**另一个 suspend 函数**或者**协程作用域**里被调用

- **构建器**
要开启协程，你得有*入口*：
1. **`runBlocking { ... }`**：
    - 它是连接*普通世界* 和*协程世界* 的桥梁。
    - 它会**阻塞当前线程**，直到*大括号里所有的代码（包括它里面的子协程）* 执行完。
    - **用途**：主要用于 `main` 函数和测试。
2. **`launch { ... }`**：
    - 它是*发射后不管* 的操作。
    - 它会开启一个新协程去跑，但**不会阻塞**它所在的代码行。它会立即返回一个 `Job` 对象

```kotlin
// 稍微过一下runBlocking和suspend的特性
    @Test
    fun testBasicDemo() {
        fun testBlocking() {
            println("1. 准备睡觉 (Thread)")
            Thread.sleep(1000) // 线程死等，什么也干不了
            println("2. 醒了 (Thread)")
        }
        fun testSuspending() = runBlocking {
            println("1. 准备挂起 (Coroutine)")

            launch {
                delay(1000) // 协程暂停，不影响外面的代码
                println("3. 协程任务完成")
            }

            println("2. launch 之后，我没有被 delay 挡住")
        }

        println("===开始测试===")
        testBlocking()
        testSuspending()

        /*
        1. 准备睡觉 (Thread)
        2. 醒了 (Thread)
        3. 准备挂起 (Coroutine)
        4. launch 之后，我没有被 delay 挡住
        5. 协程任务完成
        * */
    }
```

***
# 页面底部