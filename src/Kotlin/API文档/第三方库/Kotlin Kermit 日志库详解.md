---
title: Kotlin Kermit 日志库详解
date: 2026-03-19
footer: Trae编辑
---


## 目录

1. [概述](#概述)
2. [安装与配置](#安装与配置)
3. [基本用法](#基本用法)
4. [核心 API](#核心-api)
5. [日志级别](#日志级别)
6. [LogWriter](#logwriter)
7. [标签和日志配置](#标签和日志配置)
8. [多平台支持](#多平台支持)
9. [高级特性](#高级特性)
10. [最佳实践](#最佳实践)
11. [常见问题与解决方案](#常见问题与解决方案)
12. [总结](#总结)

## 概述

Kermit 是由 Touchlab 开发的 Kotlin Multiplatform 集中式日志工具库。它的设计理念是提供一个统一的日志接口，可以在 Kotlin 多平台项目中使用，包括 Android、iOS、JVM、JavaScript 和 Native 平台。

**主要特点**：
- **Kotlin Multiplatform 支持**：可以在所有 Kotlin 支持的平台使用
- **统一的 API**：跨平台一致的日志接口
- **灵活的日志输出**：支持多种 LogWriter 实现
- **可配置的日志级别**：动态控制日志输出
- **标签支持**：便于分类和过滤日志
- **线程安全**：支持并发环境下的日志记录
- **协程安全**：与 Kotlin 协程完美集成

## 安装与配置

### Gradle 配置

**Kotlin Multiplatform 项目**：

```kotlin
// build.gradle.kts (Kotlin DSL)
plugins {
    kotlin("multiplatform")
}

kotlin {
    sourceSets {
        commonMain {
            dependencies {
                implementation("co.touchlab:kermit:2.0.4")
            }
        }
        
        androidMain {
            dependencies {
                implementation("co.touchlab:kermit-android:2.0.4")
            }
        }
        
        iosMain {
            dependencies {
                implementation("co.touchlab:kermit-ios:2.0.4")
            }
        }
        
        jvmMain {
            dependencies {
                implementation("co.touchlab:kermit-jvm:2.0.4")
            }
        }
        
        jsMain {
            dependencies {
                implementation("co.touchlab:kermit-js:2.0.4")
            }
        }
    }
}
```

**Android 项目**：

```kotlin
// build.gradle.kts
dependencies {
    implementation("co.touchlab:kermit-android:2.0.4")
}
```

**JVM 项目**：

```kotlin
// build.gradle.kts
dependencies {
    implementation("co.touchlab:kermit:2.0.4")
}
```

### Maven 配置

```xml
<dependency>
    <groupId>co.touchlab</groupId>
    <artifactId>kermit</artifactId>
    <version>2.0.4</version>
</dependency>
```

## 基本用法

### 创建 Logger 实例

```kotlin
import co.touchlab.kermit.Logger

// 创建默认 Logger
val logger = Logger

// 创建带标签的 Logger
val networkLogger = Logger.withTag("Network")
val databaseLogger = Logger.withTag("Database")

// 创建自定义配置的 Logger
val customLogger = Logger(
    config = LoggerConfig.default.copy(
        minSeverity = Severity.Info
    ),
    tag = "Custom"
)
```

### 基本日志记录

```kotlin
import co.touchlab.kermit.Logger

class MyClass {
    private val logger = Logger.withTag("MyClass")
    
    fun doSomething() {
        // 不同级别的日志
        logger.v("Verbose message")           // 详细日志
        logger.d("Debug message")             // 调试日志
        logger.i("Info message")              // 信息日志
        logger.w("Warning message")           // 警告日志
        logger.e("Error message")             // 错误日志
        logger.a("Assert message")            // 断言日志
        
        // 带异常的日志
        try {
            riskyOperation()
        } catch (e: Exception) {
            logger.e("Operation failed", e)
        }
        
        // 带格式化参数的日志
        logger.i("User %s logged in from %s", "Alice", "192.168.1.1")
        logger.d("Processing item %d of %d", 5, 100)
    }
}
```

## 核心 API

### Logger 类

Logger 是 Kermit 的核心类，提供了各种日志记录方法：

| 方法 | 描述 | 参数 |
|------|------|------|
| `v(message: String)` | 记录详细日志 | 消息内容 |
| `v(message: String, throwable: Throwable)` | 记录详细日志（带异常） | 消息内容和异常 |
| `d(message: String)` | 记录调试日志 | 消息内容 |
| `d(message: String, throwable: Throwable)` | 记录调试日志（带异常） | 消息内容和异常 |
| `i(message: String)` | 记录信息日志 | 消息内容 |
| `i(message: String, throwable: Throwable)` | 记录信息日志（带异常） | 消息内容和异常 |
| `w(message: String)` | 记录警告日志 | 消息内容 |
| `w(message: String, throwable: Throwable)` | 记录警告日志（带异常） | 消息内容和异常 |
| `e(message: String)` | 记录错误日志 | 消息内容 |
| `e(message: String, throwable: Throwable)` | 记录错误日志（带异常） | 消息内容和异常 |
| `a(message: String)` | 记录断言日志 | 消息内容 |
| `a(message: String, throwable: Throwable)` | 记录断言日志（带异常） | 消息内容和异常 |
| `log(severity: Severity, message: String)` | 记录指定级别的日志 | 日志级别和消息 |
| `log(severity: Severity, message: String, throwable: Throwable)` | 记录指定级别的日志（带异常） | 日志级别、消息和异常 |

### 带格式化参数的日志

```kotlin
// 字符串格式化
logger.i("User %s logged in", "Alice")
logger.d("Processing item %d of %d", 5, 100)
logger.w("Temperature: %.2f°C", 23.5)

// 使用 Kotlin 字符串模板（推荐）
val user = "Alice"
val ip = "192.168.1.1"
logger.i("User $user logged in from $ip")
```

### 日志检查

```kotlin
// 检查是否启用了特定级别的日志
if (logger.isLoggable(Severity.Debug)) {
    // 执行昂贵的日志准备操作
    val expensiveData = prepareExpensiveLogData()
    logger.d(expensiveData)
}
```

## 日志级别

Kermit 定义了以下日志级别（从低到高）：

| 级别 | 常量 | 描述 |
|------|------|------|
| Verbose | `Severity.Verbose` | 最详细的日志，用于开发调试 |
| Debug | `Severity.Debug` | 调试信息 |
| Info | `Severity.Info` | 一般信息 |
| Warn | `Severity.Warn` | 警告信息 |
| Error | `Severity.Error` | 错误信息 |
| Assert | `Severity.Assert` | 严重错误，需要立即处理 |

### 配置最小日志级别

```kotlin
import co.touchlab.kermit.LoggerConfig
import co.touchlab.kermit.Severity

// 设置最小日志级别为 Info
val config = LoggerConfig.default.copy(
    minSeverity = Severity.Info
)

val logger = Logger(config, "MyApp")

// 现在 Verbose 和 Debug 级别的日志不会被输出
logger.v("This will not be logged")
logger.d("This will not be logged")
logger.i("This will be logged")
```

## LogWriter

LogWriter 是 Kermit 中负责实际输出日志的组件。Kermit 支持多种 LogWriter 实现。

### 内置 LogWriter

#### 1. CommonWriter（通用写入器）

```kotlin
import co.touchlab.kermit.CommonWriter

val config = LoggerConfig(
    logWriterList = listOf(CommonWriter()),
    minSeverity = Severity.Debug
)

val logger = Logger(config, "MyApp")
```

#### 2. PlatformWriter（平台特定写入器）

```kotlin
import co.touchlab.kermit.PlatformWriter

// 自动选择适合当前平台的写入器
val config = LoggerConfig(
    logWriterList = listOf(PlatformWriter()),
    minSeverity = Severity.Debug
)
```

#### 3. 多个 LogWriter

```kotlin
import co.touchlab.kermit.CommonWriter
import co.touchlab.kermit.PlatformWriter

// 同时使用多个写入器
val config = LoggerConfig(
    logWriterList = listOf(
        CommonWriter(),      // 输出到控制台
        PlatformWriter(),    // 平台特定输出
        FileLogWriter()      // 自定义文件写入器
    ),
    minSeverity = Severity.Debug
)
```

### 自定义 LogWriter

```kotlin
import co.touchlab.kermit.LogWriter
import co.touchlab.kermit.Severity

class FileLogWriter(private val filePath: String) : LogWriter() {
    
    override fun log(severity: Severity, message: String, tag: String, throwable: Throwable?) {
        val timestamp = getCurrentTimestamp()
        val logLine = "[$timestamp] [$severity] [$tag] $message"
        
        // 写入文件
        File(filePath).appendText(logLine + "\n")
        
        // 如果有异常，也记录异常信息
        throwable?.let {
            File(filePath).appendText("Exception: ${it.message}\n")
            File(filePath).appendText(it.stackTraceToString() + "\n")
        }
    }
    
    private fun getCurrentTimestamp(): String {
        return SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(Date())
    }
}

// 使用自定义 LogWriter
val config = LoggerConfig(
    logWriterList = listOf(FileLogWriter("/path/to/log.txt")),
    minSeverity = Severity.Debug
)
```

### Android 特定 LogWriter

```kotlin
import co.touchlab.kermit.LogcatWriter

// Android 平台使用 Logcat
val config = LoggerConfig(
    logWriterList = listOf(LogcatWriter()),
    minSeverity = Severity.Debug
)
```

### iOS 特定 LogWriter

```kotlin
import co.touchlab.kermit.NSLogWriter

// iOS 平台使用 NSLog
val config = LoggerConfig(
    logWriterList = listOf(NSLogWriter()),
    minSeverity = Severity.Debug
)
```

## 标签和日志配置

### 使用标签

标签用于分类和过滤日志，便于在大量日志中快速定位问题：

```kotlin
// 创建带标签的 Logger
val networkLogger = Logger.withTag("Network")
val databaseLogger = Logger.withTag("Database")
val uiLogger = Logger.withTag("UI")

// 使用标签记录日志
networkLogger.i("Request sent: GET /api/users")
databaseLogger.d("Query executed: SELECT * FROM users")
uiLogger.w("Button click handled")
```

### 动态配置

```kotlin
import co.touchlab.kermit.mutableLoggerConfig

// 创建可变配置
val mutableConfig = mutableLoggerConfig(
    minSeverity = Severity.Info
)

val logger = Logger(mutableConfig, "MyApp")

// 运行时更改日志级别
fun enableDebugLogging() {
    mutableConfig.minSeverity = Severity.Debug
}

fun disableDebugLogging() {
    mutableConfig.minSeverity = Severity.Info
}
```

### 基于标签的过滤

```kotlin
import co.touchlab.kermit.LoggerConfig

// 只记录特定标签的日志
val config = LoggerConfig(
    logWriterList = listOf(CommonWriter()),
    minSeverity = Severity.Debug,
    tagFilter = { tag ->
        // 只记录 Network 和 Database 标签的日志
        tag == "Network" || tag == "Database"
    }
)
```

## 多平台支持

Kermit 的设计目标是在所有 Kotlin 支持的平台提供一致的日志接口。

### 通用代码（commonMain）

```kotlin
// commonMain/kotlin/com/example/Logger.kt
import co.touchlab.kermit.Logger

expect fun createPlatformLogger(): Logger

object AppLogger {
    val logger: Logger = createPlatformLogger()
    
    fun logNetworkRequest(url: String) {
        logger.i("Network request: $url")
    }
    
    fun logDatabaseQuery(query: String) {
        logger.d("Database query: $query")
    }
    
    fun logError(message: String, throwable: Throwable?) {
        logger.e(message, throwable)
    }
}
```

### Android 实现（androidMain）

```kotlin
// androidMain/kotlin/com/example/Logger.kt
import co.touchlab.kermit.Logger
import co.touchlab.kermit.LoggerConfig
import co.touchlab.kermit.LogcatWriter

actual fun createPlatformLogger(): Logger {
    return Logger(
        config = LoggerConfig(
            logWriterList = listOf(LogcatWriter()),
            minSeverity = Severity.Debug
        ),
        tag = "MyApp"
    )
}
```

### iOS 实现（iosMain）

```kotlin
// iosMain/kotlin/com/example/Logger.kt
import co.touchlab.kermit.Logger
import co.touchlab.kermit.LoggerConfig
import co.touchlab.kermit.NSLogWriter

actual fun createPlatformLogger(): Logger {
    return Logger(
        config = LoggerConfig(
            logWriterList = listOf(NSLogWriter()),
            minSeverity = Severity.Debug
        ),
        tag = "MyApp"
    )
}
```

### JVM 实现（jvmMain）

```kotlin
// jvmMain/kotlin/com/example/Logger.kt
import co.touchlab.kermit.Logger
import co.touchlab.kermit.LoggerConfig
import co.touchlab.kermit.CommonWriter

actual fun createPlatformLogger(): Logger {
    return Logger(
        config = LoggerConfig(
            logWriterList = listOf(CommonWriter()),
            minSeverity = Severity.Debug
        ),
        tag = "MyApp"
    )
}
```

## 高级特性

### 协程集成

Kermit 与 Kotlin 协程完美集成：

```kotlin
import kotlinx.coroutines.*
import co.touchlab.kermit.Logger

class CoroutineLogger {
    private val logger = Logger.withTag("Coroutine")
    
    suspend fun performAsyncOperation() {
        logger.d("Starting async operation")
        
        try {
            withContext(Dispatchers.IO) {
                logger.d("Switching to IO dispatcher")
                // 执行 IO 操作
                delay(1000)
                logger.i("IO operation completed")
            }
            
            logger.i("Async operation completed successfully")
        } catch (e: Exception) {
            logger.e("Async operation failed", e)
        }
    }
}
```

### 日志拦截器

```kotlin
import co.touchlab.kermit.LogWriter
import co.touchlab.kermit.Severity

class LoggingInterceptor(private val innerWriter: LogWriter) : LogWriter() {
    
    override fun log(severity: Severity, message: String, tag: String, throwable: Throwable?) {
        // 在日志记录前执行某些操作
        val enhancedMessage = "[${Thread.currentThread().name}] $message"
        
        // 调用内部写入器
        innerWriter.log(severity, enhancedMessage, tag, throwable)
        
        // 在日志记录后执行某些操作
        if (severity >= Severity.Error) {
            // 发送错误报告
            sendErrorReport(message, throwable)
        }
    }
    
    private fun sendErrorReport(message: String, throwable: Throwable?) {
        // 实现错误报告发送逻辑
    }
}

// 使用拦截器
val config = LoggerConfig(
    logWriterList = listOf(
        LoggingInterceptor(CommonWriter())
    ),
    minSeverity = Severity.Debug
)
```

### 结构化日志

```kotlin
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put

class StructuredLogWriter : LogWriter() {
    
    override fun log(severity: Severity, message: String, tag: String, throwable: Throwable?) {
        val jsonLog = buildJsonObject {
            put("timestamp", System.currentTimeMillis())
            put("severity", severity.name)
            put("tag", tag)
            put("message", message)
            throwable?.let {
                put("exception", it.message)
                put("stacktrace", it.stackTraceToString())
            }
        }
        
        println(Json.encodeToString(jsonLog))
    }
}
```

### 日志采样

```kotlin
class SamplingLogWriter(
    private val innerWriter: LogWriter,
    private val sampleRate: Double = 0.1
) : LogWriter() {
    
    override fun log(severity: Severity, message: String, tag: String, throwable: Throwable?) {
        // 只对 Debug 级别进行采样
        if (severity == Severity.Debug && Math.random() > sampleRate) {
            return
        }
        
        innerWriter.log(severity, message, tag, throwable)
    }
}
```

## 最佳实践

### 1. 使用标签组织日志

```kotlin
// 为不同模块创建专门的 Logger
object Loggers {
    val network = Logger.withTag("Network")
    val database = Logger.withTag("Database")
    val ui = Logger.withTag("UI")
    val security = Logger.withTag("Security")
}

// 使用
class UserRepository {
    fun fetchUser(id: String) {
        Loggers.database.d("Fetching user with id: $id")
        // ...
    }
}
```

### 2. 避免在日志中进行昂贵操作

```kotlin
// 不推荐
logger.d("Data: ${expensiveOperation()}")

// 推荐
if (logger.isLoggable(Severity.Debug)) {
    logger.d("Data: ${expensiveOperation()}")
}

// 或者使用 lambda（如果库支持）
logger.d { "Data: ${expensiveOperation()}" }
```

### 3. 正确处理异常

```kotlin
// 记录异常时包含上下文信息
try {
    riskyOperation()
} catch (e: NetworkException) {
    logger.e("Network request failed for user $userId", e)
} catch (e: DatabaseException) {
    logger.e("Database query failed: $query", e)
} catch (e: Exception) {
    logger.e("Unexpected error in operation", e)
}
```

### 4. 使用合适的日志级别

```kotlin
// Verbose: 最详细的调试信息
logger.v("Entering function with params: $params")

// Debug: 调试信息
logger.d("Processing item $itemId")

// Info: 重要事件
logger.i("User $userId logged in")

// Warn: 潜在问题
logger.w("Slow query detected: ${query.time}ms")

// Error: 错误
logger.e("Failed to save data", exception)

// Assert: 严重错误
logger.a("Critical system failure", exception)
```

### 5. 配置生产环境日志

```kotlin
// 生产环境配置
val productionConfig = LoggerConfig(
    logWriterList = listOf(
        FileLogWriter("/var/log/app.log"),
        RemoteLogWriter("https://logs.example.com")
    ),
    minSeverity = Severity.Info,
    tagFilter = { tag ->
        // 生产环境只记录重要标签的日志
        tag in listOf("Security", "Error", "Performance")
    }
)

// 开发环境配置
val developmentConfig = LoggerConfig(
    logWriterList = listOf(
        CommonWriter(),
        PlatformWriter()
    ),
    minSeverity = Severity.Debug
)
```

### 6. 日志脱敏

```kotlin
class SensitiveDataFilter(private val innerWriter: LogWriter) : LogWriter() {
    
    private val sensitivePatterns = listOf(
        Regex("password[=:]\\s*\\S+"),
        Regex("token[=:]\\s*\\S+"),
        Regex("api[_-]?key[=:]\\s*\\S+")
    )
    
    override fun log(severity: Severity, message: String, tag: String, throwable: Throwable?) {
        var filteredMessage = message
        
        sensitivePatterns.forEach { pattern ->
            filteredMessage = pattern.replace(filteredMessage, "***REDACTED***")
        }
        
        innerWriter.log(severity, filteredMessage, tag, throwable)
    }
}
```

## 常见问题与解决方案

### 1. 日志不输出

**问题**：配置了 Kermit 但日志不输出

**解决方案**：
- 检查 `minSeverity` 配置
- 确认 LogWriter 已正确配置
- 检查标签过滤器设置

```kotlin
// 调试配置
val config = LoggerConfig(
    logWriterList = listOf(CommonWriter()),
    minSeverity = Severity.Verbose  // 设置为最低级别
)
```

### 2. 多线程日志问题

**问题**：多线程环境下日志顺序混乱

**解决方案**：
- 使用线程安全的 LogWriter
- 添加时间戳
- 使用结构化日志

```kotlin
class ThreadSafeLogWriter(private val innerWriter: LogWriter) : LogWriter() {
    private val lock = Any()
    
    override fun log(severity: Severity, message: String, tag: String, throwable: Throwable?) {
        synchronized(lock) {
            innerWriter.log(severity, message, tag, throwable)
        }
    }
}
```

### 3. 内存泄漏

**问题**：长时间运行的应用出现内存泄漏

**解决方案**：
- 限制日志缓冲区大小
- 定期清理日志文件
- 使用循环日志文件

```kotlin
class RotatingFileLogWriter(
    private val baseFilePath: String,
    private val maxFileSize: Long = 10 * 1024 * 1024,  // 10MB
    private val maxFiles: Int = 5
) : LogWriter() {
    // 实现日志轮转逻辑
}
```

### 4. 性能问题

**问题**：日志记录影响应用性能

**解决方案**：
- 使用异步日志写入
- 实现日志采样
- 调整日志级别

```kotlin
class AsyncLogWriter(private val innerWriter: LogWriter) : LogWriter() {
    private val scope = CoroutineScope(Dispatchers.IO)
    
    override fun log(severity: Severity, message: String, tag: String, throwable: Throwable?) {
        scope.launch {
            innerWriter.log(severity, message, tag, throwable)
        }
    }
}
```

### 5. 跨平台兼容性问题

**问题**：在不同平台上日志行为不一致

**解决方案**：
- 使用 expect/actual 模式
- 为每个平台提供专门的实现
- 进行充分的跨平台测试

## 总结

Kermit 是一个功能强大且灵活的 Kotlin Multiplatform 日志库，它提供了：

1. **统一的 API**：在所有 Kotlin 平台上使用相同的日志接口
2. **灵活的配置**：支持动态日志级别和标签过滤
3. **可扩展的架构**：通过 LogWriter 实现自定义日志输出
4. **多平台支持**：支持 Android、iOS、JVM、JavaScript 和 Native
5. **协程友好**：与 Kotlin 协程完美集成

**核心要点**：
- 使用标签组织日志
- 选择合适的日志级别
- 避免在日志中进行昂贵操作
- 正确处理异常信息
- 根据环境配置不同的日志策略
- 注意日志的安全性和隐私保护

通过掌握 Kermit 的使用，可以为 Kotlin 多平台应用构建统一、高效的日志系统，便于开发调试和生产环境的监控。