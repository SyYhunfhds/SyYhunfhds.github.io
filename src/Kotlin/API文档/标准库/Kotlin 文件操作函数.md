---
title: Kotlin 文件操作函数
date: 2026-03-09
footer: Trae编辑
---


## 目录

1. [概述](#概述)
2. [创建文件和目录](#创建文件和目录)
3. [读取文件](#读取文件)
4. [写入文件](#写入文件)
5. [文件属性操作](#文件属性操作)
6. [文件复制和移动](#文件复制和移动)
7. [删除操作](#删除操作)
8. [目录遍历](#目录遍历)
9. [路径操作](#路径操作)
10. [流式操作](#流式操作)

## 概述

Kotlin 提供了多种方式进行文件操作，主要包括：

- **kotlin.io** 包：提供基本的文件读写操作
- **java.io** 包：Java 标准 IO 库
- **java.nio.file** 包：Java NIO 文件操作（更高效，支持大文件）
- **kotlinx.io**（第三方库）：Kotlin 原生 IO 库

本文档主要介绍 Kotlin 标准库中的文件操作 API。

## 创建文件和目录

### 创建文件

```kotlin
import java.io.File

// 创建新文件
val file = File("test.txt")
val created = file.createNewFile()

// 创建临时文件
val tempFile = File.createTempFile("prefix", ".tmp")

// 创建带父目录的文件
val nestedFile = File("dir/subdir/file.txt")
nestedFile.parentFile.mkdirs() // 先创建父目录
nestedFile.createNewFile()
```

### 创建目录

```kotlin
import java.io.File

// 创建单级目录
val dir = File("mydir")
dir.mkdir()

// 创建多级目录
val nestedDir = File("dir1/dir2/dir3")
nestedDir.mkdirs()

// 创建临时目录
val tempDir = createTempDir("prefix")
```

## 读取文件

### 读取整个文件

```kotlin
import java.io.File

val file = File("test.txt")

// 读取为字符串
val content = file.readText()

// 读取为字节数组
val bytes = file.readBytes()

// 读取为行列表
val lines = file.readLines()

// 指定字符编码读取
val contentUTF8 = file.readText(Charsets.UTF_8)
```

### 使用 useLines 逐行读取

```kotlin
import java.io.File

val file = File("test.txt")

// 逐行处理，自动关闭资源
file.useLines { lines ->
    lines.forEach { line ->
        println(line)
    }
}

// 带过滤的逐行处理
file.useLines { lines ->
    lines.filter { it.contains("keyword") }
         .forEach { println(it) }
}
```

### 使用 BufferedReader

```kotlin
import java.io.File

val file = File("test.txt")

file.bufferedReader().use { reader ->
    reader.forEachLine { line ->
        println(line)
    }
}
```

### 读取特定行数

```kotlin
import java.io.File

val file = File("test.txt")

// 读取前 N 行
val first10Lines = file.useLines { lines ->
    lines.take(10).toList()
}
```

## 写入文件

### 写入字符串

```kotlin
import java.io.File

val file = File("test.txt")

// 写入字符串（覆盖原有内容）
file.writeText("Hello, World!")

// 追加写入
file.appendText("\nNew line")

// 指定编码写入
file.writeText("你好，世界！", Charsets.UTF_8)
```

### 写入字节数组

```kotlin
import java.io.File

val file = File("test.bin")

// 写入字节数组
file.writeBytes(byteArrayOf(0x01, 0x02, 0x03))

// 追加字节
file.appendBytes(byteArrayOf(0x04, 0x05))
```

### 使用 PrintWriter

```kotlin
import java.io.File

val file = File("test.txt")

file.printWriter().use { writer ->
    writer.println("Line 1")
    writer.println("Line 2")
    writer.printf("Number: %d%n", 42)
}
```

### 使用 BufferedWriter

```kotlin
import java.io.File

val file = File("test.txt")

file.bufferedWriter().use { writer ->
    writer.write("Line 1")
    writer.newLine()
    writer.write("Line 2")
}
```

## 文件属性操作

### 基本属性

```kotlin
import java.io.File

val file = File("test.txt")

// 检查文件是否存在
val exists = file.exists()

// 检查是否是文件
val isFile = file.isFile

// 检查是否是目录
val isDirectory = file.isDirectory

// 检查是否可读/可写/可执行
val canRead = file.canRead()
val canWrite = file.canWrite()
val canExecute = file.canExecute()
```

### 文件大小和时间

```kotlin
import java.io.File

val file = File("test.txt")

// 获取文件大小（字节）
val length = file.length()

// 获取最后修改时间
val lastModified = file.lastModified()

// 设置最后修改时间
file.setLastModified(System.currentTimeMillis())
```

### 文件权限

```kotlin
import java.io.File

val file = File("test.txt")

// 设置可读/可写/可执行
file.setReadable(true)
file.setWritable(true)
file.setExecutable(true)

// 设置所有者读写权限（Java 7+）
file.setReadable(true, true)  // 仅所有者可读
file.setWritable(true, true)  // 仅所有者可写
```

## 文件复制和移动

### 复制文件

```kotlin
import java.io.File
import java.nio.file.Files
import java.nio.file.StandardCopyOption

val source = File("source.txt")
val target = File("target.txt")

// 使用 Kotlin 扩展函数复制
source.copyTo(target)

// 覆盖已存在的文件
source.copyTo(target, overwrite = true)

// 使用 Java NIO 复制（支持更多选项）
Files.copy(
    source.toPath(),
    target.toPath(),
    StandardCopyOption.REPLACE_EXISTING,
    StandardCopyOption.COPY_ATTRIBUTES
)
```

### 移动文件

```kotlin
import java.io.File
import java.nio.file.Files
import java.nio.file.StandardCopyOption

val source = File("source.txt")
val target = File("target.txt")

// 使用 Kotlin 扩展函数移动
source.renameTo(target)

// 使用 Java NIO 移动
Files.move(
    source.toPath(),
    target.toPath(),
    StandardCopyOption.REPLACE_EXISTING,
    StandardCopyOption.ATOMIC_MOVE
)
```

### 重命名文件

```kotlin
import java.io.File

val file = File("oldname.txt")
val newFile = File("newname.txt")

file.renameTo(newFile)
```

## 删除操作

### 删除文件

```kotlin
import java.io.File

val file = File("test.txt")

// 删除文件
val deleted = file.delete()

// 在 JVM 退出时删除
file.deleteOnExit()
```

### 删除目录

```kotlin
import java.io.File

val dir = File("mydir")

// 删除空目录
dir.delete()

// 递归删除目录及其内容
fun File.deleteRecursively(): Boolean {
    return if (isDirectory) {
        listFiles()?.forEach { it.deleteRecursively() }
        delete()
    } else {
        delete()
    }
}

// 使用 Kotlin 标准库的递归删除
dir.deleteRecursively()
```

## 目录遍历

### 列出目录内容

```kotlin
import java.io.File

val dir = File(".")

// 列出所有文件和目录
val files = dir.listFiles()

// 列出文件名
val names = dir.list()

// 带过滤器的列出
val txtFiles = dir.listFiles { file ->
    file.extension == "txt"
}
```

### 遍历目录树

```kotlin
import java.io.File

val dir = File(".")

// 遍历目录（不递归）
dir.walkTopDown().forEach { file ->
    println(file.name)
}

// 递归遍历（深度优先）
dir.walk().forEach { file ->
    println(file.path)
}

// 限制遍历深度
dir.walk().maxDepth(2).forEach { file ->
    println(file.path)
}

// 过滤遍历结果
dir.walk()
    .filter { it.isFile }
    .filter { it.extension == "kt" }
    .forEach { println(it.name) }

// 遍历并统计
val kotlinFiles = dir.walk()
    .filter { it.isFile }
    .filter { it.extension == "kt" }
    .toList()
```

### 使用 Files.newDirectoryStream

```kotlin
import java.nio.file.Files
import java.nio.file.Paths

val path = Paths.get(".")

Files.newDirectoryStream(path).use { stream ->
    stream.forEach { entry ->
        println(entry.fileName)
    }
}

// 带通配符的目录流
Files.newDirectoryStream(path, "*.txt").use { stream ->
    stream.forEach { println(it) }
}
```

## 路径操作

### 路径拼接

```kotlin
import java.io.File

// 使用 resolve 拼接路径
val baseDir = File("/home/user")
val file = baseDir.resolve("documents/file.txt")
// 结果: /home/user/documents/file.txt

// 使用 / 运算符（Kotlin 扩展）
val file2 = baseDir / "documents" / "file.txt"

// 使用 Paths
import java.nio.file.Paths
val path = Paths.get("/home/user", "documents", "file.txt")
```

### 路径解析

```kotlin
import java.io.File

val file = File("/home/user/documents/file.txt")

// 获取文件名
val name = file.name           // "file.txt"
val nameWithoutExt = file.nameWithoutExtension  // "file"
val extension = file.extension  // "txt"

// 获取父目录
val parent = file.parent       // "/home/user/documents"
val parentFile = file.parentFile

// 获取绝对路径
val absolutePath = file.absolutePath
val canonicalPath = file.canonicalPath

// 获取路径各部分
val pathComponents = file.toPath()
```

### 相对路径和绝对路径

```kotlin
import java.io.File

val file = File("test.txt")

// 转换为绝对路径
val absolute = file.absoluteFile

// 获取相对于某目录的路径
val base = File("/home/user")
val relative = file.relativeTo(base)
```

## 流式操作

### 输入流

```kotlin
import java.io.File

val file = File("test.txt")

// 使用输入流
file.inputStream().use { stream ->
    val bytes = stream.readBytes()
}

// 使用缓冲输入流
file.bufferedInputStream().use { stream ->
    val bytes = stream.readBytes()
}

// 使用 Reader
file.reader().use { reader ->
    val content = reader.readText()
}
```

### 输出流

```kotlin
import java.io.File

val file = File("test.txt")

// 使用输出流
file.outputStream().use { stream ->
    stream.write("Hello".toByteArray())
}

// 使用缓冲输出流
file.bufferedOutputStream().use { stream ->
    stream.write("Hello".toByteArray())
}

// 使用 Writer
file.writer().use { writer ->
    writer.write("Hello")
}
```

### 数据流

```kotlin
import java.io.DataInputStream
import java.io.DataOutputStream
import java.io.File

val file = File("data.bin")

// 写入数据
file.outputStream().use { fos ->
    DataOutputStream(fos).use { dos ->
        dos.writeInt(42)
        dos.writeDouble(3.14)
        dos.writeUTF("Hello")
    }
}

// 读取数据
file.inputStream().use { fis ->
    DataInputStream(fis).use { dis ->
        val intValue = dis.readInt()
        val doubleValue = dis.readDouble()
        val stringValue = dis.readUTF()
    }
}
```

## 示例：综合运用

```kotlin
import java.io.File

fun main() {
    // 创建测试目录
    val testDir = File("test_directory")
    testDir.mkdirs()
    
    // 创建测试文件
    val testFile = testDir.resolve("test.txt")
    testFile.writeText("Line 1\nLine 2\nLine 3")
    
    // 读取并处理文件
    println("文件内容:")
    testFile.readLines().forEachIndexed { index, line ->
        println("${index + 1}: $line")
    }
    
    // 复制文件
    val copyFile = testDir.resolve("test_copy.txt")
    testFile.copyTo(copyFile)
    println("\n文件已复制到: ${copyFile.path}")
    
    // 追加内容
    copyFile.appendText("\nLine 4 (追加)")
    
    // 获取文件信息
    println("\n文件信息:")
    println("文件名: ${testFile.name}")
    println("文件大小: ${testFile.length()} 字节")
    println("最后修改: ${testFile.lastModified()}")
    println("是否可读: ${testFile.canRead()}")
    println("是否可写: ${testFile.canWrite()}")
    
    // 遍历目录
    println("\n目录内容:")
    testDir.walk().forEach { file ->
        val type = if (file.isDirectory) "[目录]" else "[文件]"
        println("$type ${file.name}")
    }
    
    // 清理
    testDir.deleteRecursively()
    println("\n测试目录已删除")
}

// 输出结果：
// 文件内容:
// 1: Line 1
// 2: Line 2
// 3: Line 3
// 
// 文件已复制到: test_directory\test_copy.txt
// 
// 文件信息:
// 文件名: test.txt
// 文件大小: 18 字节
// 最后修改: 1709990400000
// 是否可读: true
// 是否可写: true
// 
// 目录内容:
// [目录] test_directory
// [文件] test.txt
// [文件] test_copy.txt
// 
// 测试目录已删除
```

## 总结

Kotlin 提供了丰富的文件操作 API，使得文件处理变得简单而直观。主要特点包括：

1. **简洁的语法**：使用扩展函数简化文件操作
2. **自动资源管理**：`use` 函数确保资源正确关闭
3. **与 Java 互操作**：可以无缝使用 Java NIO 和 IO 库
4. **函数式风格**：支持链式调用和 Lambda 表达式

通过本文档的示例，您应该能够掌握 Kotlin 文件操作的基本用法和高级技巧。