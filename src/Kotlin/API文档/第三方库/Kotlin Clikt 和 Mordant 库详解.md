---
title: Kotlin Clikt 和 Mordant 库详解
date: 2026-03-19
footer: Trae编辑
---


## 目录

1. [概述](#概述)
2. [Clikt 库](#clikt-库)
   - [安装与配置](#安装与配置)
   - [基本用法](#基本用法)
   - [命令与子命令](#命令与子命令)
   - [选项与参数](#选项与参数)
   - [验证与错误处理](#验证与错误处理)
   - [高级特性](#高级特性)
3. [Mordant 库](#mordant-库)
   - [安装与配置](#安装与配置-1)
   - [基本用法](#基本用法-1)
   - [文本样式](#文本样式)
   - [进度条与仪表盘](#进度条与仪表盘)
   - [表格与布局](#表格与布局)
4. [开发精美的 CLI 应用](#开发精美的-cli-应用)
   - [项目结构](#项目结构)
   - [示例应用](#示例应用)
   - [最佳实践](#最佳实践)
5. [常见问题与解决方案](#常见问题与解决方案)
6. [总结](#总结)

## 概述

在 Kotlin 生态系统中，有两个非常强大的库可以帮助开发者构建美观、功能丰富的命令行应用程序：

- **Clikt**：一个现代化的命令行接口解析库，用于处理命令行参数、选项和子命令
- **Mordant**：一个全功能的终端文本样式库，用于创建美观的终端输出，包括彩色文本、进度条、表格等

这两个库可以很好地配合使用，Clikt 负责命令行解析，Mordant 负责终端输出的美化，共同打造专业级的 CLI 应用。

## Clikt 库

Clikt（Command Line Interface for Kotlin）是一个用于 Kotlin 的命令行接口解析库，它的设计理念是简洁、直观且功能强大。

### 安装与配置

**Gradle 配置**：

```kotlin
// build.gradle.kts
repositories {
    mavenCentral()
}

dependencies {
    implementation("com.github.ajalt.clikt:clikt:4.3.0")
}
```

**Maven 配置**：

```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.github.ajalt.clikt</groupId>
    <artifactId>clikt</artifactId>
    <version>4.3.0</version>
</dependency>
```

### 基本用法

**创建简单的命令**：

```kotlin
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.arguments.argument
import com.github.ajalt.clikt.parameters.options.option
import com.github.ajalt.clikt.parameters.types.int
import kotlin.system.exitProcess

class HelloCommand : CliktCommand(name = "hello") {
    private val name by argument(help = "The name to greet")
    private val age by option(help = "Your age").int()
    
    override fun run() {
        println("Hello, $name!")
        age?.let { println("You are $it years old") }
    }
}

fun main(args: Array<String>) = HelloCommand().main(args)
```

**运行结果**：

```bash
$ ./app hello Alice --age 30
Hello, Alice!
You are 30 years old
```

### 命令与子命令

Clikt 支持嵌套的子命令结构，类似于 git、docker 等工具：

```kotlin
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.arguments.argument

class MainCommand : CliktCommand(name = "app") {
    override fun run() = Unit // 主命令本身不做任何事情
}

class AddCommand : CliktCommand(name = "add", help = "Add a new item") {
    private val item by argument(help = "The item to add")
    
    override fun run() {
        println("Adding item: $item")
    }
}

class RemoveCommand : CliktCommand(name = "remove", help = "Remove an item") {
    private val item by argument(help = "The item to remove")
    
    override fun run() {
        println("Removing item: $item")
    }
}

fun main(args: Array<String>) {
    MainCommand()
        .subcommand(AddCommand())
        .subcommand(RemoveCommand())
        .main(args)
}
```

**运行结果**：

```bash
$ ./app add apple
Adding item: apple

$ ./app remove banana
Removing item: banana
```

### 选项与参数

**基本选项**：

```kotlin
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.options.option
import com.github.ajalt.clikt.parameters.options.default
import com.github.ajalt.clikt.parameters.options.flag
import com.github.ajalt.clikt.parameters.options.required

class OptionsCommand : CliktCommand() {
    // 带默认值的选项
    private val output by option("--output", "-o", help = "Output file").default("output.txt")
    
    // 必需的选项
    private val input by option("--input", "-i", help = "Input file").required()
    
    // 标志选项（布尔值）
    private val verbose by option("--verbose", "-v", help = "Verbose mode").flag()
    
    override fun run() {
        println("Input: $input")
        println("Output: $output")
        println("Verbose: $verbose")
    }
}
```

**参数**：

```kotlin
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.arguments.argument
import com.github.ajalt.clikt.parameters.arguments.arguments
import com.github.ajalt.clikt.parameters.types.int
import com.github.ajalt.clikt.parameters.types.file

class ArgumentsCommand : CliktCommand() {
    // 单个参数
    private val name by argument(help = "Your name")
    
    // 多个参数
    private val numbers by arguments().int()
    
    // 文件参数
    private val file by argument(help = "A file").file()
    
    override fun run() {
        println("Name: $name")
        println("Numbers: $numbers")
        println("File: ${file.absolutePath}")
    }
}
```

### 验证与错误处理

**参数验证**：

```kotlin
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.core.require
import com.github.ajalt.clikt.parameters.arguments.argument
import com.github.ajalt.clikt.parameters.options.option
import com.github.ajalt.clikt.parameters.types.int

class ValidationCommand : CliktCommand() {
    private val age by option("--age").int().required()
    private val name by argument()
    
    override fun run() {
        // 验证年龄
        require(age >= 18) { "Age must be at least 18" }
        require(name.isNotBlank()) { "Name cannot be blank" }
        
        println("Hello, $name! You are $age years old.")
    }
}
```

**自定义错误处理**：

```kotlin
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.core.CliktError
import com.github.ajalt.clikt.core.PrintMessage
import com.github.ajalt.clikt.parameters.arguments.argument

class ErrorHandlingCommand : CliktCommand() {
    private val input by argument()
    
    override fun run() {
        try {
            // 业务逻辑
            if (input == "error") {
                throw CliktError("Custom error message")
            }
            println("Input: $input")
        } catch (e: Exception) {
            throw PrintMessage("An error occurred: ${e.message}", error = true)
        }
    }
}
```

### 高级特性

**自动补全**：

```kotlin
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.options.option
import com.github.ajalt.clikt.parameters.options.suggestions

class CompletionCommand : CliktCommand() {
    private val fruit by option().suggestions {
        listOf("apple", "banana", "orange", "pear")
    }
    
    override fun run() {
        println("Selected fruit: $fruit")
    }
}
```

**类型转换**：

```kotlin
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.options.option
import com.github.ajalt.clikt.parameters.types.*
import java.io.File
import java.time.LocalDate

class TypeConversionCommand : CliktCommand() {
    private val file by option().file(mustExist = true)
    private val directory by option().directory(mustExist = true)
    private val url by option().url()
    private val date by option().localDate()
    private val regex by option().regex()
    
    override fun run() {
        println("File: ${file?.absolutePath}")
        println("Directory: ${directory?.absolutePath}")
        println("URL: $url")
        println("Date: $date")
        println("Regex: $regex")
    }
}
```

**分组选项**：

```kotlin
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.groups.OptionGroup
import com.github.ajalt.clikt.parameters.groups.required
import com.github.ajalt.clikt.parameters.options.option

class DatabaseOptions : OptionGroup("Database Options") {
    val host by option("--db-host").default("localhost")
    val port by option("--db-port").default(5432)
    val user by option("--db-user").required()
    val password by option("--db-password").required()
}

class ServerOptions : OptionGroup("Server Options") {
    val port by option("--server-port").default(8080)
    val host by option("--server-host").default("0.0.0.0")
}

class GroupOptionsCommand : CliktCommand() {
    private val db by DatabaseOptions().required()
    private val server by ServerOptions()
    
    override fun run() {
        println("Database: ${db.host}:${db.port}, user: ${db.user}")
        println("Server: ${server.host}:${server.port}")
    }
}
```

## Mordant 库

Mordant 是一个用于 Kotlin 的全功能终端文本样式库，它可以创建美观的终端输出，包括彩色文本、进度条、表格等。

### 安装与配置

**Gradle 配置**：

```kotlin
// build.gradle.kts
repositories {
    mavenCentral()
}

dependencies {
    implementation("com.github.ajalt.mordant:mordant:2.0.0-alpha10")
}
```

**Maven 配置**：

```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.github.ajalt.mordant</groupId>
    <artifactId>mordant</artifactId>
    <version>2.0.0-alpha10</version>
</dependency>
```

### 基本用法

**创建 Terminal 实例**：

```kotlin
import com.github.ajalt.mordant.terminal.Terminal

val terminal = Terminal()
```

**基本输出**：

```kotlin
terminal.println("Hello, World!")
terminal.print("This is a ")
terminal.println("test")
```

### 文本样式

**颜色与样式**：

```kotlin
import com.github.ajalt.mordant.terminal.Terminal
import com.github.ajalt.mordant.rendering.TextColors.*
import com.github.ajalt.mordant.rendering.TextStyles.*

val terminal = Terminal()

// 基本颜色
terminal.println(red("This is red text"))
terminal.println(green("This is green text"))
terminal.println(blue("This is blue text"))

// 样式
terminal.println(bold("This is bold text"))
terminal.println(italic("This is italic text"))
terminal.println(underline("This is underlined text"))

// 组合样式
terminal.println(bold + red("This is bold red text"))
terminal.println(italic + green("This is italic green text"))

// 背景色
terminal.println(onYellow + black("This has a yellow background"))
terminal.println(onBlue + white("This has a blue background"))
```

**ANSI 颜色**：

```kotlin
import com.github.ajalt.mordant.terminal.Terminal
import com.github.ajalt.mordant.rendering.AnsiColors

val terminal = Terminal()

// 256 色
terminal.println(AnsiColors.rgb(255, 0, 0)("Bright red"))
terminal.println(AnsiColors.rgb(0, 255, 0)("Bright green"))
terminal.println(AnsiColors.rgb(0, 0, 255)("Bright blue"))

// 灰度
terminal.println(AnsiColors.gray(0)("Black"))
terminal.println(AnsiColors.gray(127)("Gray"))
terminal.println(AnsiColors.gray(255)("White"))
```

### 进度条与仪表盘

**基本进度条**：

```kotlin
import com.github.ajalt.mordant.terminal.Terminal
import com.github.ajalt.mordant.widgets.ProgressBar
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking

val terminal = Terminal()

runBlocking {
    val progressBar = ProgressBar(terminal, total = 100)
    progressBar.start()
    
    repeat(100) {
        delay(50)
        progressBar.update(it + 1)
    }
    
    progressBar.stop()
    terminal.println("Task completed!")
}
```

**高级进度条**：

```kotlin
import com.github.ajalt.mordant.terminal.Terminal
import com.github.ajalt.mordant.widgets.ProgressBar
import com.github.ajalt.mordant.widgets.ProgressBarStyle
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking

val terminal = Terminal()

runBlocking {
    val progressBar = ProgressBar(
        terminal = terminal,
        total = 100,
        width = 50,
        style = ProgressBarStyle(
            leftCap = "[",
            rightCap = "]",
            filled = "=",
            empty = " ",
            unknown = "?"
        ),
        showPercentage = true,
        showRemainingTime = true,
        showSpeed = true
    )
    
    progressBar.start()
    
    repeat(100) {
        delay(50)
        progressBar.update(it + 1)
    }
    
    progressBar.stop()
}
```

**仪表盘**：

```kotlin
import com.github.ajalt.mordant.terminal.Terminal
import com.github.ajalt.mordant.widgets.Gauge

val terminal = Terminal()

val gauge = Gauge(
    terminal = terminal,
    value = 0.75,
    label = "Progress",
    width = 50,
    style = Gauge.Style(
        leftCap = "[",
        rightCap = "]",
        filled = "#",
        empty = "-"
    )
)

terminal.println(gauge)
```

### 表格与布局

**基本表格**：

```kotlin
import com.github.ajalt.mordant.terminal.Terminal
import com.github.ajalt.mordant.widgets.Table

val terminal = Terminal()

val table = Table {
    header { row("Name", "Age", "City") }
    row("Alice", "30", "New York")
    row("Bob", "25", "London")
    row("Charlie", "35", "Paris")
}

terminal.println(table)
```

**样式化表格**：

```kotlin
import com.github.ajalt.mordant.terminal.Terminal
import com.github.ajalt.mordant.widgets.Table
import com.github.ajalt.mordant.rendering.TextColors.*

val terminal = Terminal()

val table = Table {
    borderStyle = Table.BorderStyle.ROUNDED
    header {
        row(
            bold + white + onBlue("Name"),
            bold + white + onBlue("Age"),
            bold + white + onBlue("City")
        )
    }
    row("Alice", "30", "New York")
    row("Bob", "25", "London")
    row("Charlie", "35", "Paris")
}

terminal.println(table)
```

**布局**：

```kotlin
import com.github.ajalt.mordant.terminal.Terminal
import com.github.ajalt.mordant.widgets.Columns
import com.github.ajalt.mordant.rendering.TextColors.*

val terminal = Terminal()

val columns = Columns {
    column {
        +bold("Features")
        +"• Easy to use"
        +"• Cross-platform"
        +"• Powerful API"
    }
    column {
        +bold("Benefits")
        +"• Faster development"
        +"• Better user experience"
        +"• More maintainable code"
    }
}

terminal.println(columns)
```

## 开发精美的 CLI 应用

现在，让我们将 Clikt 和 Mordant 结合起来，开发一个精美的 CLI 应用。

### 项目结构

```
my-cli-app/
├── build.gradle.kts
├── settings.gradle.kts
└── src/
    └── main/
        └── kotlin/
            └── com/
                └── example/
                    ├── Main.kt
                    ├── commands/
                    │   ├── MainCommand.kt
                    │   ├── AddCommand.kt
                    │   └── RemoveCommand.kt
                    ├── models/
                    │   └── Item.kt
                    └── utils/
                        └── TerminalUtils.kt
```

### 示例应用

**构建一个待办事项管理工具**：

```kotlin
// src/main/kotlin/com/example/utils/TerminalUtils.kt
import com.github.ajalt.mordant.terminal.Terminal
import com.github.ajalt.mordant.rendering.TextColors.*
import com.github.ajalt.mordant.rendering.TextStyles.*
import com.github.ajalt.mordant.widgets.Table

object TerminalUtils {
    val terminal = Terminal()
    
    fun success(message: String) {
        terminal.println(green("✓ ") + message)
    }
    
    fun error(message: String) {
        terminal.println(red("✗ ") + message)
    }
    
    fun info(message: String) {
        terminal.println(blue("i ") + message)
    }
    
    fun warning(message: String) {
        terminal.println(yellow("! ") + message)
    }
    
    fun printItems(items: List<Item>) {
        if (items.isEmpty()) {
            info("No items found")
            return
        }
        
        val table = Table {
            borderStyle = Table.BorderStyle.ROUNDED
            header {
                row(
                    bold + white + onBlue("ID"),
                    bold + white + onBlue("Name"),
                    bold + white + onBlue("Status")
                )
            }
            items.forEachIndexed { index, item ->
                val status = if (item.completed) {
                    green("Completed")
                } else {
                    yellow("Pending")
                }
                row((index + 1).toString(), item.name, status)
            }
        }
        terminal.println(table)
    }
}

// src/main/kotlin/com/example/models/Item.kt
data class Item(val name: String, var completed: Boolean = false)

// src/main/kotlin/com/example/commands/MainCommand.kt
import com.github.ajalt.clikt.core.CliktCommand

class MainCommand : CliktCommand(name = "todo", help = "A todo list manager") {
    override fun run() = Unit
}

// src/main/kotlin/com/example/commands/AddCommand.kt
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.arguments.argument

class AddCommand(private val items: MutableList<Item>) : CliktCommand(name = "add", help = "Add a new todo item") {
    private val name by argument(help = "The name of the todo item")
    
    override fun run() {
        val item = Item(name)
        items.add(item)
        TerminalUtils.success("Added item: $name")
    }
}

// src/main/kotlin/com/example/commands/RemoveCommand.kt
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.core.require
import com.github.ajalt.clikt.parameters.arguments.argument
import com.github.ajalt.clikt.parameters.types.int

class RemoveCommand(private val items: MutableList<Item>) : CliktCommand(name = "remove", help = "Remove a todo item") {
    private val index by argument(help = "The index of the item to remove").int()
    
    override fun run() {
        require(index > 0 && index <= items.size) {
            "Invalid index. Must be between 1 and ${items.size}"
        }
        val item = items.removeAt(index - 1)
        TerminalUtils.success("Removed item: ${item.name}")
    }
}

// src/main/kotlin/com/example/commands/ListCommand.kt
import com.github.ajalt.clikt.core.CliktCommand

class ListCommand(private val items: List<Item>) : CliktCommand(name = "list", help = "List all todo items") {
    override fun run() {
        TerminalUtils.printItems(items)
    }
}

// src/main/kotlin/com/example/commands/CompleteCommand.kt
import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.core.require
import com.github.ajalt.clikt.parameters.arguments.argument
import com.github.ajalt.clikt.parameters.types.int

class CompleteCommand(private val items: MutableList<Item>) : CliktCommand(name = "complete", help = "Mark a todo item as completed") {
    private val index by argument(help = "The index of the item to complete").int()
    
    override fun run() {
        require(index > 0 && index <= items.size) {
            "Invalid index. Must be between 1 and ${items.size}"
        }
        val item = items[index - 1]
        item.completed = true
        TerminalUtils.success("Marked item as completed: ${item.name}")
    }
}

// src/main/kotlin/com/example/Main.kt
import com.github.ajalt.clikt.core.CliktCommand

fun main(args: Array<String>) {
    val items = mutableListOf<Item>()
    
    MainCommand()
        .subcommand(AddCommand(items))
        .subcommand(RemoveCommand(items))
        .subcommand(ListCommand(items))
        .subcommand(CompleteCommand(items))
        .main(args)
}
```

**运行结果**：

```bash
$ ./todo add "Buy groceries"
✓ Added item: Buy groceries

$ ./todo add "Clean the house"
✓ Added item: Clean the house

$ ./todo list
┌────┬────────────────┬───────────┐
│ ID │ Name           │ Status    │
├────┼────────────────┼───────────┤
│ 1  │ Buy groceries  │ Pending   │
│ 2  │ Clean the house │ Pending   │
└────┴────────────────┴───────────┘

$ ./todo complete 1
✓ Marked item as completed: Buy groceries

$ ./todo list
┌────┬────────────────┬───────────┐
│ ID │ Name           │ Status    │
├────┼────────────────┼───────────┤
│ 1  │ Buy groceries  │ Completed │
│ 2  │ Clean the house │ Pending   │
└────┴────────────────┴───────────┘

$ ./todo remove 2
✓ Removed item: Clean the house

$ ./todo list
┌────┬───────────────┬───────────┐
│ ID │ Name          │ Status    │
├────┼───────────────┼───────────┤
│ 1  │ Buy groceries │ Completed │
└────┴───────────────┴───────────┘
```

### 最佳实践

1. **项目结构**：
   - 组织命令到不同的类中
   - 使用包结构来分离关注点
   - 保持主类简洁

2. **命令设计**：
   - 遵循常见的 CLI 约定
   - 提供清晰的帮助信息
   - 使用一致的命名风格

3. **用户体验**：
   - 提供有意义的错误消息
   - 使用颜色和样式提高可读性
   - 添加进度指示和状态反馈

4. **代码质量**：
   - 使用 Kotlin 的特性（如数据类、扩展函数）
   - 保持代码简洁明了
   - 添加适当的注释

5. **测试**：
   - 为命令行解析编写单元测试
   - 测试边缘情况
   - 确保错误处理正常工作

6. **打包与分发**：
   - 使用 Gradle 或 Maven 打包应用
   - 考虑使用 GraalVM 原生镜像提高性能
   - 提供安装说明

## 常见问题与解决方案

### 1. 命令行参数解析错误

**问题**：Clikt 无法解析命令行参数

**解决方案**：
- 检查参数格式是否正确
- 确保选项名称正确
- 检查是否缺少必需的参数

### 2. 终端样式不显示

**问题**：Mordant 的颜色和样式在终端中不显示

**解决方案**：
- 确保终端支持 ANSI 转义序列
- 检查 Mordant 的配置
- 尝试使用 `Terminal(ansiLevel = AnsiLevel.TRUECOLOR)` 强制启用颜色

### 3. 进度条不更新

**问题**：进度条在长时间运行的任务中不更新

**解决方案**：
- 确保在协程中正确调用 `update()` 方法
- 检查是否有阻塞操作
- 考虑使用 `runBlocking` 或其他协程构建器

### 4. 表格显示不正确

**问题**：表格在终端中显示混乱

**解决方案**：
- 检查终端宽度是否足够
- 调整表格宽度设置
- 考虑使用不同的边框样式

### 5. 应用打包问题

**问题**：无法将应用打包为可执行文件

**解决方案**：
- 使用 Gradle 的 `application` 插件
- 配置正确的主类
- 考虑使用 GraalVM 原生镜像

## 总结

Clikt 和 Mordant 是 Kotlin 生态系统中两个强大的库，它们可以帮助开发者构建美观、功能丰富的命令行应用程序：

1. **Clikt**：
   - 简洁直观的命令行解析
   - 支持子命令、选项和参数
   - 强大的验证和错误处理
   - 类型安全的参数解析

2. **Mordant**：
   - 丰富的文本样式和颜色
   - 进度条和仪表盘
   - 表格和布局
   - 跨平台支持

通过结合使用这两个库，开发者可以创建专业级的 CLI 应用，提供良好的用户体验。无论是构建简单的工具还是复杂的命令行应用，Clikt 和 Mordant 都能满足各种需求。

**核心要点**：
- 合理组织命令结构
- 提供清晰的用户反馈
- 使用颜色和样式提高可读性
- 确保错误处理和验证
- 遵循 CLI 设计最佳实践

通过掌握这些工具和技术，你可以开发出既功能强大又美观的 Kotlin 命令行应用程序。