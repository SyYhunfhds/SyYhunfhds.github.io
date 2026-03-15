---
title: Kotlin 错误处理详解
date: 2026-03-15
footer: Trae编辑
---


## 目录

1. [错误处理概述](#错误处理概述)
2. [传统异常处理](#传统异常处理)
3. [Kotlin 特有的错误处理](#kotlin-特有的错误处理)
4. [Result 类型](#result-类型)
5. [协程中的异常处理](#协程中的异常处理)
6. [自定义异常](#自定义异常)
7. [错误处理的设计模式](#错误处理的设计模式)
8. [Bad Practice](#bad-practice)
9. [最佳实践](#最佳实践)
10. [常见问题与解决方案](#常见问题与解决方案)

## 错误处理概述

Kotlin 提供了多种错误处理机制，从传统的异常处理到现代的函数式错误处理：

- **传统异常处理**：`try-catch-finally`
- **函数式错误处理**：`runCatching`、`Result` 类型
- **协程异常处理**：`CoroutineExceptionHandler`、`supervisorScope`
- **空安全**：`?.`、`?:`、`!!` 操作符
- **自定义异常**：创建特定业务逻辑的异常

**错误处理的目标**：
- 提高代码的健壮性
- 提供清晰的错误信息
- 便于调试和维护
- 避免程序崩溃

## 传统异常处理

### 1. try-catch-finally

```kotlin
fun readFile(filePath: String): String {
    val file = File(filePath)
    var reader: BufferedReader? = null
    
    try {
        reader = file.bufferedReader()
        return reader.readText()
    } catch (e: FileNotFoundException) {
        println("文件不存在: $filePath")
        throw e  // 重新抛出异常
    } catch (e: IOException) {
        println("读取文件失败: ${e.message}")
        return ""
    } finally {
        // 确保资源关闭
        reader?.close()
    }
}
```

### 2. try-with-resources (use 函数)

Kotlin 提供了 `use` 函数来自动管理资源，相当于 Java 的 try-with-resources：

```kotlin
fun readFileSafe(filePath: String): String {
    return File(filePath).bufferedReader().use {
        try {
            it.readText()
        } catch (e: Exception) {
            println("读取文件失败: ${e.message}")
            ""
        }
    }
}

// 多个资源
fun copyFile(source: String, dest: String) {
    File(source).inputStream().use {input ->
        File(dest).outputStream().use {output ->
            input.copyTo(output)
        }
    }
}
```

### 3. 异常层次结构

Kotlin 的异常层次结构与 Java 类似：

- `Throwable`：所有错误和异常的基类
  - `Error`：严重错误，通常不应该捕获
  - `Exception`：可恢复的异常
    - `RuntimeException`：运行时异常
    - 其他检查异常（如 `IOException`、`SQLException` 等）

## Kotlin 特有的错误处理

### 1. runCatching

`runCatching` 是 Kotlin 提供的函数式错误处理工具，返回 `Result<T>`：

```kotlin
fun divide(a: Int, b: Int): Int? {
    return runCatching {
        a / b
    }.getOrNull()
}

fun readFileWithRunCatching(filePath: String): String {
    return runCatching {
        File(filePath).readText()
    }.onSuccess {
        println("文件读取成功")
    }.onFailure {
        println("读取失败: ${it.message}")
    }.getOrDefault("")
}

// 链式操作
fun processData(input: String): String {
    return runCatching {
        input.toInt()
    }.map {
        it * 2
    }.mapCatching {
        if (it > 100) throw IllegalArgumentException("值太大")
        it.toString()
    }.getOrElse {
        "错误: ${it.message}"
    }
}
```

### 2. 其他 try 函数

Kotlin 还提供了其他类似的函数：

```kotlin
// tryCatch
val result = kotlin.runCatching {
    // 可能抛出异常的代码
}

// 类似的函数
val result1 = runCatching { "test".toInt() }  // Result<Int>
val result2 = "test".toIntOrNull()          // Int?
val result3 = "test".toIntOrNull() ?: 0     // Int

// 安全调用
val value = nullableValue?.toString() ?: "默认值"

// Elvis 操作符
val result = try {
    riskyOperation()
} catch (e: Exception) {
    fallbackValue
}
```

## Result 类型

### 1. Result 基本用法

`Result<T>` 是 Kotlin 1.3+ 引入的类型，用于表示可能成功或失败的操作：

```kotlin
fun calculate(a: Int, b: Int): Result<Int> {
    return if (b == 0) {
        Result.failure(ArithmeticException("除数不能为零"))
    } else {
        Result.success(a / b)
    }
}

fun main() {
    val result = calculate(10, 2)
    
    // 方式 1：isSuccess/isFailure
    if (result.isSuccess) {
        println("结果: ${result.getOrThrow()}")
    } else {
        println("错误: ${result.exceptionOrNull()?.message}")
    }
    
    // 方式 2：fold
    val output = result.fold(
        onSuccess = { "成功: $it" },
        onFailure = { "失败: ${it.message}" }
    )
    println(output)
    
    // 方式 3：getOrNull/getOrDefault
    val value = result.getOrNull() ?: 0
    val value2 = result.getOrDefault(0)
    
    // 方式 4：recover
    val recovered = result.recover {
        println("发生错误，使用默认值 0")
        0
    }
}
```

### 2. Result 链式操作

```kotlin
fun processUserInput(input: String): Result<String> {
    return runCatching {
        input.toInt()
    }.map {
        it * 2
    }.mapCatching {
        if (it > 100) {
            throw IllegalArgumentException("值太大")
        }
        "处理结果: $it"
    }
}

fun main() {
    val result1 = processUserInput("42")
    println(result1.getOrThrow())  // 处理结果: 84
    
    val result2 = processUserInput("60")
    println(result2.exceptionOrNull()?.message)  // 值太大
    
    val result3 = processUserInput("abc")
    println(result3.exceptionOrNull()?.message)  // For input string: "abc"
}
```

### 3. 自定义 Result 扩展

```kotlin
// 扩展函数
fun <T> Result<T>.onSuccess(action: (T) -> Unit): Result<T> {
    if (isSuccess) action(getOrThrow())
    return this
}

fun <T> Result<T>.onFailure(action: (Throwable) -> Unit): Result<T> {
    if (isFailure) action(exceptionOrNull()!!)
    return this
}

// 使用
fun fetchData(): Result<String> {
    return runCatching {
        // 网络请求
        "数据"
    }
}

fun main() {
    fetchData()
        .onSuccess { println("获取数据成功: $it") }
        .onFailure { println("获取数据失败: ${it.message}") }
        .getOrElse { "默认数据" }
}
```

## 协程中的异常处理

### 1. 基本异常处理

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    // 方式 1：在协程体内使用 try-catch
    val job1 = launch {
        try {
            throw RuntimeException("协程异常")
        } catch (e: Exception) {
            println("捕获到异常: ${e.message}")
        }
    }
    job1.join()
    
    // 方式 2：使用 CoroutineExceptionHandler
    val handler = CoroutineExceptionHandler {
        context, exception ->
        println("异常处理器捕获: ${exception.message}")
    }
    
    val job2 = launch(handler) {
        throw RuntimeException("未捕获的异常")
    }
    job2.join()
}
```

### 2. 异常传播

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    // 异常会向上传播
    val parentJob = launch {
        launch {
            delay(100)
            throw RuntimeException("子协程异常")
        }
    }
    
    try {
        parentJob.join()
    } catch (e: Exception) {
        println("父协程捕获: ${e.message}")
    }
}
```

### 3. SupervisorJob

`SupervisorJob` 可以防止子协程的异常影响其他子协程：

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val supervisor = SupervisorJob()
    val scope = CoroutineScope(supervisor + Dispatchers.Default)
    
    // 第一个子协程
    scope.launch {
        delay(100)
        throw RuntimeException("子协程 1 异常")
    }
    
    // 第二个子协程
    scope.launch {
        delay(200)
        println("子协程 2 正常执行")
    }
    
    delay(300)
    scope.cancel()
}
```

### 4. supervisorScope

`supervisorScope` 用于结构化并发中的异常隔离：

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    supervisorScope {
        launch {
            delay(100)
            throw RuntimeException("任务 1 失败")
        }
        
        launch {
            delay(200)
            println("任务 2 完成")
        }
    }
    
    println("supervisorScope 结束")
}
```

### 5. 协程中的 Result

```kotlin
import kotlinx.coroutines.*

suspend fun fetchData(): Result<String> {
    return runCatching {
        delay(100)
        // 模拟网络请求
        "数据"
    }
}

suspend fun processData(): Result<Int> {
    return fetchData()
        .mapCatching { it.toInt() }
}

fun main() = runBlocking {
    val result = processData()
    result.fold(
        onSuccess = { println("处理成功: $it") },
        onFailure = { println("处理失败: ${it.message}") }
    )
}
```

## 自定义异常

### 1. 基本自定义异常

```kotlin
// 自定义检查异常
class BusinessException(message: String) : Exception(message)

// 自定义运行时异常
class ValidationException(message: String) : RuntimeException(message)

// 使用
fun validateInput(input: String) {
    if (input.isBlank()) {
        throw ValidationException("输入不能为空")
    }
    if (input.length < 3) {
        throw ValidationException("输入长度不能少于 3 个字符")
    }
}

fun processBusinessLogic(value: Int) {
    if (value < 0) {
        throw BusinessException("值不能为负数")
    }
    // 业务逻辑
}
```

### 2. 异常层次结构

```kotlin
// 基础异常
open class AppException(message: String, cause: Throwable? = null) : RuntimeException(message, cause)

// 业务异常
class BusinessException(message: String, cause: Throwable? = null) : AppException(message, cause)

// 验证异常
class ValidationException(message: String, cause: Throwable? = null) : AppException(message, cause)

// 网络异常
class NetworkException(message: String, cause: Throwable? = null) : AppException(message, cause)

// 数据库异常
class DatabaseException(message: String, cause: Throwable? = null) : AppException(message, cause)

// 使用
fun fetchUserData(userId: Long): User {
    try {
        // 网络请求
        return api.getUser(userId)
    } catch (e: IOException) {
        throw NetworkException("网络请求失败", e)
    } catch (e: SQLException) {
        throw DatabaseException("数据库操作失败", e)
    }
}
```

### 3. 异常携带额外信息

```kotlin
class ApiException(
    val statusCode: Int,
    message: String,
    cause: Throwable? = null
) : RuntimeException(message, cause)

fun callApi(endpoint: String): Response {
    try {
        return apiClient.call(endpoint)
    } catch (e: HttpException) {
        throw ApiException(e.code(), "API 调用失败: ${e.message}", e)
    }
}

// 使用
fun main() {
    try {
        val response = callApi("/user")
        println("API 调用成功")
    } catch (e: ApiException) {
        println("API 错误: ${e.statusCode} - ${e.message}")
        when (e.statusCode) {
            401 -> println("需要登录")
            403 -> println("权限不足")
            404 -> println("资源不存在")
            else -> println("其他错误")
        }
    }
}
```

## 错误处理的设计模式

### 1. 错误结果模式

```kotlin
sealed class Result<out T> {
    data class Success<out T>(val data: T) : Result<T>()
    data class Error(val message: String, val cause: Throwable? = null) : Result<Nothing>()
}

fun divide(a: Int, b: Int): Result<Int> {
    return if (b == 0) {
        Result.Error("除数不能为零")
    } else {
        Result.Success(a / b)
    }
}

fun main() {
    val result = divide(10, 2)
    when (result) {
        is Result.Success -> println("结果: ${result.data}")
        is Result.Error -> println("错误: ${result.message}")
    }
}
```

### 2. 状态模式

```kotlin
sealed class LoadingState {
    object Idle : LoadingState()
    object Loading : LoadingState()
    data class Success<T>(val data: T) : LoadingState()
    data class Error(val message: String) : LoadingState()
}

class ViewModel {
    var state by mutableStateOf<LoadingState>(LoadingState.Idle)
    
    fun loadData() {
        state = LoadingState.Loading
        viewModelScope.launch {
            val result = fetchData()
            state = when (result) {
                is Result.Success -> LoadingState.Success(result.data)
                is Result.Error -> LoadingState.Error(result.message)
            }
        }
    }
}
```

### 3. 服务层错误处理

```kotlin
interface UserService {
    suspend fun getUserById(id: Long): Result<User>
    suspend fun createUser(user: UserCreate): Result<User>
    suspend fun updateUser(id: Long, user: UserUpdate): Result<User>
    suspend fun deleteUser(id: Long): Result<Unit>
}

class UserServiceImpl(private val api: UserApi) : UserService {
    override suspend fun getUserById(id: Long): Result<User> {
        return runCatching {
            api.getUser(id)
        }.mapCatching {response ->
            if (response.isSuccessful) {
                response.body() ?: throw Exception("空响应")
            } else {
                throw Exception("API 错误: ${response.code()}")
            }
        }
    }
    
    // 其他方法...
}
```

## Bad Practice

### 1. 捕获所有异常

```kotlin
// ❌ 错误：捕获所有异常
fun badExample() {
    try {
        // 业务逻辑
    } catch (e: Exception) {
        println("发生错误")
        // 没有处理具体异常
    }
}

// ✅ 正确：捕获具体异常
fun goodExample() {
    try {
        // 业务逻辑
    } catch (e: IOException) {
        println("IO 错误: ${e.message}")
    } catch (e: IllegalArgumentException) {
        println("参数错误: ${e.message}")
    } catch (e: Exception) {
        println("其他错误: ${e.message}")
    }
}
```

### 2. 空 catch 块

```kotlin
// ❌ 错误：空 catch 块
fun badExample() {
    try {
        // 可能抛出异常的代码
    } catch (e: Exception) {
        // 什么都不做
    }
}

// ✅ 正确：处理异常
fun goodExample() {
    try {
        // 可能抛出异常的代码
    } catch (e: Exception) {
        logger.error("处理失败", e)
        // 适当的错误处理
    }
}
```

### 3. 过度使用 !! 操作符

```kotlin
// ❌ 错误：过度使用 !!
fun badExample(user: User?) {
    val name = user!!.name  // 可能抛出 NullPointerException
    println(name)
}

// ✅ 正确：使用安全调用
fun goodExample(user: User?) {
    val name = user?.name ?: "未知"
    println(name)
}
```

### 4. 异常用作控制流

```kotlin
// ❌ 错误：使用异常作为控制流
fun badExample(value: Int): String {
    return try {
        if (value < 0) throw IllegalArgumentException("负值")
        "正数: $value"
    } catch (e: IllegalArgumentException) {
        "负数: ${-value}"
    }
}

// ✅ 正确：使用条件判断
fun goodExample(value: Int): String {
    return if (value < 0) {
        "负数: ${-value}"
    } else {
        "正数: $value"
    }
}
```

### 5. 重新抛出异常时丢失原始异常

```kotlin
// ❌ 错误：丢失原始异常
fun badExample() {
    try {
        riskyOperation()
    } catch (e: Exception) {
        throw RuntimeException("操作失败")  // 丢失了原始异常
    }
}

// ✅ 正确：保留原始异常
fun goodExample() {
    try {
        riskyOperation()
    } catch (e: Exception) {
        throw RuntimeException("操作失败", e)  // 保留原始异常
    }
}
```

### 6. 协程中未处理的异常

```kotlin
// ❌ 错误：协程异常未处理
fun badExample() {
    GlobalScope.launch {
        throw RuntimeException("未处理的异常")
    }
    // 异常会导致应用崩溃
}

// ✅ 正确：处理协程异常
fun goodExample() {
    val handler = CoroutineExceptionHandler {
        context, exception ->
        println("捕获到协程异常: ${exception.message}")
    }
    
    GlobalScope.launch(handler) {
        throw RuntimeException("已处理的异常")
    }
}
```

## 最佳实践

### 1. 明确异常类型

```kotlin
// ✅ 好的做法：明确异常类型
fun processUserData(userId: Long): User {
    require(userId > 0) { "用户 ID 必须大于 0" }
    
    try {
        return userRepository.findById(userId)
            ?: throw UserNotFoundException("用户不存在: $userId")
    } catch (e: SQLException) {
        throw DatabaseException("数据库查询失败", e)
    }
}

// 自定义异常
class UserNotFoundException(message: String) : RuntimeException(message)
class DatabaseException(message: String, cause: Throwable? = null) : RuntimeException(message, cause)
```

### 2. 使用 Result 类型处理可恢复错误

```kotlin
// ✅ 好的做法：使用 Result 处理可恢复错误
fun validateInput(input: String): Result<Unit> {
    return runCatching {
        when {
            input.isBlank() -> throw ValidationException("输入不能为空")
            input.length < 3 -> throw ValidationException("输入长度不能少于 3 个字符")
            !input.matches(Regex("^[a-zA-Z0-9]+")) -> throw ValidationException("输入只能包含字母和数字")
            else -> Unit
        }
    }
}

fun processInput(input: String) {
    validateInput(input)
        .onSuccess {
            println("输入验证通过")
            // 处理业务逻辑
        }
        .onFailure {
            println("输入验证失败: ${it.message}")
            // 显示错误信息
        }
}
```

### 3. 资源管理

```kotlin
// ✅ 好的做法：使用 use 函数管理资源
fun readFileContent(filePath: String): String {
    return File(filePath).inputStream().use {input ->
        input.bufferedReader().use {reader ->
            reader.readText()
        }
    }
}

// 多个资源
fun copyFile(source: String, dest: String) {
    File(source).inputStream().use {input ->
        File(dest).outputStream().use {output ->
            input.copyTo(output)
        }
    }
}
```

### 4. 协程异常处理

```kotlin
// ✅ 好的做法：协程异常处理
import kotlinx.coroutines.*

class CoroutineErrorHandler {
    private val exceptionHandler = CoroutineExceptionHandler {
        context, exception ->
        println("协程异常: ${exception.message}")
        // 记录日志、显示错误等
    }
    
    fun launchSafe(block: suspend CoroutineScope.() -> Unit): Job {
        return CoroutineScope(Dispatchers.IO + exceptionHandler).launch {
            try {
                block()
            } catch (e: Exception) {
                println("捕获到异常: ${e.message}")
                // 额外处理
            }
        }
    }
}

// 使用
val errorHandler = CoroutineErrorHandler()
errorHandler.launchSafe {
    // 可能抛出异常的协程代码
}
```

### 5. 统一错误处理

```kotlin
// ✅ 好的做法：统一错误处理
class ErrorHandler {
    fun handleError(e: Throwable): String {
        return when (e) {
            is ValidationException -> "验证错误: ${e.message}"
            is NetworkException -> "网络错误: ${e.message}"
            is DatabaseException -> "数据库错误: ${e.message}"
            is UserNotFoundException -> "用户不存在: ${e.message}"
            else -> "未知错误: ${e.message}"
        }
    }
}

// 使用
fun processRequest() {
    val errorHandler = ErrorHandler()
    
    try {
        // 业务逻辑
    } catch (e: Exception) {
        val errorMessage = errorHandler.handleError(e)
        println(errorMessage)
        // 显示错误信息
    }
}
```

### 6. 日志记录

```kotlin
// ✅ 好的做法：合理记录日志
import org.slf4j.LoggerFactory

class UserService {
    private val logger = LoggerFactory.getLogger(UserService::class.java)
    
    fun getUserById(id: Long): User? {
        try {
            logger.info("获取用户信息: id=$id")
            val user = userRepository.findById(id)
            if (user == null) {
                logger.warn("用户不存在: id=$id")
            }
            return user
        } catch (e: Exception) {
            logger.error("获取用户信息失败: id=$id", e)
            throw e
        }
    }
}
```

### 7. 错误传递模式

```kotlin
// ✅ 好的做法：错误传递
sealed class ApiResponse<out T> {
    data class Success<out T>(val data: T) : ApiResponse<T>()
    data class Error(val code: Int, val message: String) : ApiResponse<Nothing>()
    data class NetworkError(val message: String) : ApiResponse<Nothing>()
    data class ServerError(val message: String) : ApiResponse<Nothing>()
}

class ApiService(private val client: HttpClient) {
    suspend fun getUser(id: Long): ApiResponse<User> {
        return try {
            val response = client.get("/users/$id")
            if (response.isSuccessful) {
                val user = response.body<User>()
                ApiResponse.Success(user)
            } else {
                ApiResponse.Error(response.code(), "API 错误")
            }
        } catch (e: IOException) {
            ApiResponse.NetworkError("网络错误: ${e.message}")
        } catch (e: Exception) {
            ApiResponse.ServerError("服务器错误: ${e.message}")
        }
    }
}

// 使用
fun main() = runBlocking {
    val apiService = ApiService(httpClient)
    val response = apiService.getUser(1)
    
    when (response) {
        is ApiResponse.Success -> println("获取用户成功: ${response.data}")
        is ApiResponse.Error -> println("API 错误: ${response.code} - ${response.message}")
        is ApiResponse.NetworkError -> println("网络错误: ${response.message}")
        is ApiResponse.ServerError -> println("服务器错误: ${response.message}")
    }
}
```

## 常见问题与解决方案

### 1. 异常丢失

**问题**：在某些情况下，异常可能会丢失，特别是在协程中。

**解决方案**：
- 使用 `CoroutineExceptionHandler`
- 在 `supervisorScope` 中处理异常
- 确保每个协程都有适当的异常处理

```kotlin
// 解决方案
val handler = CoroutineExceptionHandler {
    context, exception ->
    println("捕获到异常: ${exception.message}")
}

val job = GlobalScope.launch(handler) {
    throw RuntimeException("测试异常")
}
```

### 2. 嵌套 try-catch

**问题**：代码中嵌套了多层 try-catch，导致可读性差。

**解决方案**：
- 使用 `runCatching` 和 `Result` 类型
- 提取方法，减少嵌套
- 使用异常处理工具类

```kotlin
// 解决方案
fun processData(input: String): Result<Int> {
    return runCatching {
        validateInput(input)
        parseInput(input)
        processValidatedInput(input)
    }
}

fun validateInput(input: String) {
    if (input.isBlank()) throw ValidationException("输入不能为空")
    // 其他验证
}

fun parseInput(input: String): Int {
    return input.toInt()
}

fun processValidatedInput(input: String): Int {
    // 处理逻辑
    return input.length
}
```

### 3. 错误信息不明确

**问题**：异常信息不够详细，难以定位问题。

**解决方案**：
- 使用自定义异常，提供详细的错误信息
- 在异常中包含上下文信息
- 使用结构化的错误处理

```kotlin
// 解决方案
class ValidationException(
    field: String,
    value: Any?, 
    message: String
) : RuntimeException("字段 '$field' 值 '$value': $message")

fun validateEmail(email: String?) {
    if (email.isNullOrBlank()) {
        throw ValidationException("email", email, "不能为空")
    }
    if (!email.matches(Regex("^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$"))) {
        throw ValidationException("email", email, "格式不正确")
    }
}
```

### 4. 性能问题

**问题**：异常处理可能影响性能，特别是在高频操作中。

**解决方案**：
- 对于可预期的错误，使用返回值而非异常
- 只在真正的异常情况下使用异常
- 避免在循环中使用异常作为控制流

```kotlin
// 解决方案
// 不好的做法
fun parseNumber(value: String): Int {
    try {
        return value.toInt()
    } catch (e: NumberFormatException) {
        return 0
    }
}

// 好的做法
fun parseNumber(value: String): Int {
    return value.toIntOrNull() ?: 0
}

// 更好的做法
fun parseNumber(value: String): Result<Int> {
    return runCatching { value.toInt() }
}
```

### 5. 测试异常处理

**问题**：如何测试异常处理逻辑？

**解决方案**：
- 使用 JUnit 5 的 `assertThrows`
- 测试 Result 类型的失败路径
- 模拟异常场景

```kotlin
// 测试示例
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class UserServiceTest {
    private val userService = UserService()
    
    @Test
    fun `should throw UserNotFoundException when user not found`() {
        assertThrows<UserNotFoundException> {
            userService.getUserById(999)
        }
    }
    
    @Test
    fun `should return error when input is invalid`() {
        val result = userService.validateInput("")
        assert(result.isFailure)
        assert(result.exceptionOrNull() is ValidationException)
    }
}
```

## 总结

Kotlin 提供了丰富的错误处理机制，包括：

1. **传统异常处理**：`try-catch-finally` 和 `use` 函数
2. **函数式错误处理**：`runCatching` 和 `Result` 类型
3. **协程异常处理**：`CoroutineExceptionHandler` 和 `supervisorScope`
4. **自定义异常**：创建业务相关的异常类型
5. **错误处理模式**：错误结果模式、状态模式等

**最佳实践总结**：
- 明确异常类型，避免捕获所有异常
- 使用 `Result` 类型处理可恢复错误
- 正确管理资源，使用 `use` 函数
- 在协程中妥善处理异常
- 统一错误处理，提供清晰的错误信息
- 合理记录日志，便于调试和监控
- 避免使用异常作为控制流
- 性能敏感场景使用返回值而非异常

通过合理选择和组合这些错误处理机制，可以编写更加健壮、可维护的 Kotlin 代码。