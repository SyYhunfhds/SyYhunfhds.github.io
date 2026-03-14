---
title: Ktor Client HTTP客户端
date: 2026-03-14
footer: Trae编辑
---


## 目录

1. [Ktor Client 概述](#ktor-client-概述)
2. [安装与配置](#安装与配置)
3. [创建 HTTP 客户端](#创建-http-客户端)
4. [基本 HTTP 操作](#基本-http-操作)
5. [高级功能](#高级功能)
6. [序列化与反序列化](#序列化与反序列化)
7. [错误处理](#错误处理)
8. [Bad Practice](#bad-practice)
9. [最佳实践](#最佳实践)
10. [性能优化](#性能优化)

## Ktor Client 概述

Ktor Client 是一个用于 Kotlin 的异步 HTTP 客户端，基于 Kotlin 协程构建，提供了简洁、灵活的 API 来进行 HTTP 请求。

**核心特性**：
- 完全基于 Kotlin 协程，支持异步非阻塞操作
- 模块化的架构，可按需添加功能
- 支持多种引擎（CIO、OkHttp、Apache、Java 等）
- 内置内容协商和序列化支持
- 支持 WebSocket
- 支持请求和响应拦截

## 安装与配置

### Gradle 配置

```kotlin
// build.gradle.kts
plugins {
    kotlin("jvm") version "1.9.0"
    kotlin("plugin.serialization") version "1.9.0"
}

repositories {
    mavenCentral()
}

dependencies {
    // Ktor Client 核心
    implementation("io.ktor:ktor-client-core:2.3.0")
    
    // 选择引擎（推荐 CIO）
    implementation("io.ktor:ktor-client-cio:2.3.0")
    
    // 或者使用 OkHttp
    implementation("io.ktor:ktor-client-okhttp:2.3.0")
    
    // 内容协商和序列化
    implementation("io.ktor:ktor-client-content-negotiation:2.3.0")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.0")
    
    // 日志（可选）
    implementation("io.ktor:ktor-client-logging:2.3.0")
    
    // 身份验证（可选）
    implementation("io.ktor:ktor-client-auth:2.3.0")
}
```

### Maven 配置

```xml
<!-- pom.xml -->
<dependencies>
    <!-- Ktor Client 核心 -->
    <dependency>
        <groupId>io.ktor</groupId>
        <artifactId>ktor-client-core</artifactId>
        <version>2.3.0</version>
    </dependency>
    
    <!-- CIO 引擎 -->
    <dependency>
        <groupId>io.ktor</groupId>
        <artifactId>ktor-client-cio</artifactId>
        <version>2.3.0</version>
    </dependency>
    
    <!-- 内容协商 -->
    <dependency>
        <groupId>io.ktor</groupId>
        <artifactId>ktor-client-content-negotiation</artifactId>
        <version>2.3.0</version>
    </dependency>
    
    <!-- Kotlinx JSON 序列化 -->
    <dependency>
        <groupId>io.ktor</groupId>
        <artifactId>ktor-serialization-kotlinx-json</artifactId>
        <version>2.3.0</version>
    </dependency>
</dependencies>
```

## 创建 HTTP 客户端

### 基本创建

```kotlin
import io.ktor.client.*
import io.ktor.client.engine.cio.*

// 创建基本客户端
val client = HttpClient(CIO)

// 使用默认配置
val client = HttpClient()

// 配置客户端
val client = HttpClient(CIO) {
    // 引擎配置
    engine {
        maxConnectionsCount = 1000
        requestTimeout = 30000
        endpoint {
            maxConnectionsPerRoute = 100
            pipelineMaxSize = 20
            keepAliveTime = 5000
            connectTimeout = 5000
            connectAttempts = 5
        }
    }
    
    // 默认请求配置
    defaultRequest {
        url("https://api.example.com")
        header("Accept", "application/json")
        header("User-Agent", "MyApp/1.0")
    }
    
    // 安装插件
    install(ContentNegotiation) {
        json()
    }
    
    install(Logging) {
        level = LogLevel.ALL
    }
}
```

### 客户端配置选项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `followRedirects` | 是否自动跟随重定向 | `true` |
| `expectSuccess` | 是否期望成功响应（非2xx抛出异常） | `true` |
| `developmentMode` | 开发模式 | `false` |

```kotlin
val client = HttpClient(CIO) {
    followRedirects = true
    expectSuccess = true
    developmentMode = true
}
```

## 基本 HTTP 操作

### GET 请求

```kotlin
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*

suspend fun getExample() {
    val client = HttpClient(CIO)
    
    // 简单 GET 请求
    val response: HttpResponse = client.get("https://api.example.com/users")
    
    // 带参数的 GET 请求
    val responseWithParams = client.get("https://api.example.com/users") {
        parameter("page", 1)
        parameter("limit", 10)
        parameter("sort", "name")
    }
    
    // 带请求头的 GET 请求
    val responseWithHeaders = client.get("https://api.example.com/users") {
        headers {
            append("Authorization", "Bearer token123")
            append("Accept", "application/json")
        }
    }
    
    // 读取响应体
    val body: String = response.bodyAsText()
    println(body)
    
    client.close()
}
```

### POST 请求

```kotlin
import io.ktor.client.request.*
import io.ktor.http.*
import kotlinx.serialization.Serializable

@Serializable
data class User(val name: String, val email: String)

suspend fun postExample() {
    val client = HttpClient(CIO) {
        install(ContentNegotiation) {
            json()
        }
    }
    
    // 发送 JSON 数据
    val user = User("Alice", "alice@example.com")
    val response = client.post("https://api.example.com/users") {
        contentType(ContentType.Application.Json)
        setBody(user)
    }
    
    // 发送表单数据
    val formResponse = client.submitForm(
        url = "https://api.example.com/login",
        formParameters = Parameters.build {
            append("username", "alice")
            append("password", "secret123")
        }
    )
    
    // 发送 multipart 数据
    val multipartResponse = client.submitFormWithBinaryData(
        url = "https://api.example.com/upload",
        formData = formData {
            append("description", "My file")
            append("file", byteArrayOf(1, 2, 3), Headers.build {
                append(HttpHeaders.ContentDisposition, "filename=\"test.txt\"")
            })
        }
    )
    
    client.close()
}
```

### PUT、DELETE、PATCH 请求

```kotlin
suspend fun otherMethodsExample() {
    val client = HttpClient(CIO) {
        install(ContentNegotiation) {
            json()
        }
    }
    
    // PUT 请求
    val putResponse = client.put("https://api.example.com/users/1") {
        contentType(ContentType.Application.Json)
        setBody(User("Alice Updated", "alice.new@example.com"))
    }
    
    // DELETE 请求
    val deleteResponse = client.delete("https://api.example.com/users/1")
    
    // PATCH 请求
    val patchResponse = client.patch("https://api.example.com/users/1") {
        contentType(ContentType.Application.Json)
        setBody(mapOf("name" to "Alice Patched"))
    }
    
    client.close()
}
```

### 响应处理

```kotlin
import io.ktor.client.call.*
import io.ktor.http.*

suspend fun responseHandlingExample() {
    val client = HttpClient(CIO)
    
    val response = client.get("https://api.example.com/users")
    
    // 检查响应状态
    when (response.status) {
        HttpStatusCode.OK -> {
            val users: List<User> = response.body()
            println("Users: $users")
        }
        HttpStatusCode.NotFound -> {
            println("Resource not found")
        }
        HttpStatusCode.Unauthorized -> {
            println("Unauthorized access")
        }
        else -> {
            println("Unexpected status: ${response.status}")
        }
    }
    
    // 读取响应头
    val contentType = response.headers["Content-Type"]
    val totalCount = response.headers["X-Total-Count"]?.toIntOrNull()
    
    // 读取响应体为不同类型
    val text: String = response.bodyAsText()
    val bytes: ByteArray = response.readBytes()
    val stream: InputStream = response.bodyAsChannel().toInputStream()
    
    client.close()
}
```

## 高级功能

### 请求超时配置

```kotlin
import io.ktor.client.plugins.*

val client = HttpClient(CIO) {
    install(HttpTimeout) {
        requestTimeoutMillis = 30000      // 请求超时
        connectTimeoutMillis = 10000      // 连接超时
        socketTimeoutMillis = 30000       // 套接字超时
    }
}

// 单个请求的超时配置
val response = client.get("https://api.example.com/slow-endpoint") {
    timeout {
        requestTimeoutMillis = 60000
    }
}
```

### 重试机制

```kotlin
import io.ktor.client.plugins.*

val client = HttpClient(CIO) {
    install(HttpRequestRetry) {
        retryOnServerErrors(maxRetries = 3)
        exponentialDelay()
        modifyRequest { request ->
            request.headers.append("X-Retry-Count", retryCount.toString())
        }
    }
}

// 自定义重试条件
val client = HttpClient(CIO) {
    install(HttpRequestRetry) {
        maxRetries = 5
        retryIf { request, response ->
            !response.status.isSuccess()
        }
        retryOnExceptionIf { request, cause ->
            cause is IOException
        }
        delayMillis { retry ->
            retry * 1000L  // 线性退避
        }
    }
}
```

### 身份验证

```kotlin
import io.ktor.client.plugins.auth.*
import io.ktor.client.plugins.auth.providers.*

// Basic 认证
val client = HttpClient(CIO) {
    install(Auth) {
        basic {
            credentials {
                BasicAuthCredentials(username = "alice", password = "secret")
            }
            realm = "ktor"
        }
    }
}

// Bearer Token 认证
val client = HttpClient(CIO) {
    install(Auth) {
        bearer {
            loadTokens {
                BearerTokens(
                    accessToken = "access-token",
                    refreshToken = "refresh-token"
                )
            }
            refreshTokens {
                // 刷新 token 的逻辑
                BearerTokens(
                    accessToken = "new-access-token",
                    refreshToken = "new-refresh-token"
                )
            }
        }
    }
}

// Digest 认证
val client = HttpClient(CIO) {
    install(Auth) {
        digest {
            credentials {
                DigestAuthCredentials(username = "alice", password = "secret")
            }
            realm = "ktor"
        }
    }
}
```

### 请求和响应拦截

```kotlin
val client = HttpClient(CIO) {
    install(DefaultRequest) {
        header("X-Custom-Header", "value")
    }
    
    // 请求拦截
    defaultRequest {
        url {
            protocol = URLProtocol.HTTPS
            host = "api.example.com"
        }
    }
    
    // 使用插件进行拦截
    install(createClientPlugin("CustomInterceptor") {
        onRequest { request, _ ->
            println("Request: ${request.method.value} ${request.url}")
        }
        
        onResponse { response ->
            println("Response: ${response.status}")
        }
    })
}
```

### 代理配置

```kotlin
import io.ktor.client.engine.*

val client = HttpClient(CIO) {
    engine {
        proxy = ProxyBuilder.http("http://proxy.example.com:8080")
    }
}

// 带认证的代理
val client = HttpClient(CIO) {
    engine {
        proxy = ProxyBuilder.http(
            url = "http://proxy.example.com:8080",
            user = "proxyUser",
            password = "proxyPassword"
        )
    }
}
```

### WebSocket 支持

```kotlin
import io.ktor.client.plugins.websocket.*
import io.ktor.websocket.*

val client = HttpClient(CIO) {
    install(WebSockets)
}

suspend fun websocketExample() {
    client.webSocket("wss://echo.websocket.org") {
        // 发送消息
        send(Frame.Text("Hello, WebSocket!"))
        
        // 接收消息
        for (frame in incoming) {
            when (frame) {
                is Frame.Text -> {
                    val text = frame.readText()
                    println("Received: $text")
                }
                is Frame.Binary -> {
                    val bytes = frame.readBytes()
                    println("Received binary: ${bytes.size} bytes")
                }
                else -> {
                    // 处理其他类型的帧
                }
            }
        }
    }
}

// 使用 DSL 方式
suspend fun websocketDslExample() {
    client.webSocket({
        url("wss://echo.websocket.org")
        header("Custom-Header", "value")
    }) {
        send(Frame.Text("Hello"))
        
        val response = incoming.receive() as Frame.Text
        println(response.readText())
    }
}
```

## 序列化与反序列化

### Kotlinx Serialization

```kotlin
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import io.ktor.serialization.kotlinx.json.*

@Serializable
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val age: Int? = null
)

@Serializable
data class ApiResponse<T>(
    val data: T,
    val message: String,
    val success: Boolean
)

val client = HttpClient(CIO) {
    install(ContentNegotiation) {
        json(Json {
            prettyPrint = true
            isLenient = true
            ignoreUnknownKeys = true  // 忽略未知字段
            encodeDefaults = true      // 编码默认值
        })
    }
}

suspend fun serializationExample() {
    // 发送对象
    val newUser = User(0, "Alice", "alice@example.com", 25)
    val response = client.post("https://api.example.com/users") {
        contentType(ContentType.Application.Json)
        setBody(newUser)
    }
    
    // 接收对象
    val createdUser: User = response.body()
    println("Created user: $createdUser")
    
    // 接收泛型响应
    val apiResponse: ApiResponse<List<User>> = client
        .get("https://api.example.com/users")
        .body()
    
    println("Users: ${apiResponse.data}")
}
```

### 自定义序列化

```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.descriptors.*
import kotlinx.serialization.encoding.*

@Serializable(with = DateSerializer::class)
data class Date(val timestamp: Long)

object DateSerializer : KSerializer<Date> {
    override val descriptor: SerialDescriptor = 
        PrimitiveSerialDescriptor("Date", PrimitiveKind.LONG)
    
    override fun serialize(encoder: Encoder, value: Date) {
        encoder.encodeLong(value.timestamp)
    }
    
    override fun deserialize(decoder: Decoder): Date {
        return Date(decoder.decodeLong())
    }
}

// 使用自定义序列化
@Serializable
data class Event(
    val name: String,
    val date: Date
)
```

## 错误处理

### 基本错误处理

```kotlin
import io.ktor.client.network.sockets.*
import io.ktor.client.plugins.*
import java.io.IOException

suspend fun errorHandlingExample() {
    val client = HttpClient(CIO)
    
    try {
        val response = client.get("https://api.example.com/users")
        val users: List<User> = response.body()
        println(users)
    } catch (e: ClientRequestException) {
        // 4xx 错误
        println("Client error: ${e.response.status}")
    } catch (e: ServerResponseException) {
        // 5xx 错误
        println("Server error: ${e.response.status}")
    } catch (e: HttpRequestTimeoutException) {
        // 超时
        println("Request timeout")
    } catch (e: ConnectTimeoutException) {
        // 连接超时
        println("Connection timeout")
    } catch (e: SocketTimeoutException) {
        // 套接字超时
        println("Socket timeout")
    } catch (e: IOException) {
        // 网络错误
        println("Network error: ${e.message}")
    } catch (e: Exception) {
        // 其他错误
        println("Unexpected error: ${e.message}")
    } finally {
        client.close()
    }
}
```

### 使用 Result 类型

```kotlin
suspend fun fetchUsers(): Result<List<User>> {
    val client = HttpClient(CIO) {
        install(ContentNegotiation) {
            json()
        }
    }
    
    return try {
        val users: List<User> = client
            .get("https://api.example.com/users")
            .body()
        Result.success(users)
    } catch (e: Exception) {
        Result.failure(e)
    } finally {
        client.close()
    }
}

// 使用
suspend fun main() {
    when (val result = fetchUsers()) {
        is Result.Success -> {
            println("Users: ${result.getOrNull()}")
        }
        is Result.Failure -> {
            println("Error: ${result.exceptionOrNull()?.message}")
        }
    }
}
```

### 自定义异常处理

```kotlin
sealed class ApiException(message: String) : Exception(message) {
    class NotFound(message: String) : ApiException(message)
    class Unauthorized(message: String) : ApiException(message)
    class BadRequest(message: String) : ApiException(message)
    class ServerError(message: String) : ApiException(message)
    class NetworkError(message: String) : ApiException(message)
}

suspend fun <T> safeApiCall(call: suspend () -> T): T {
    return try {
        call()
    } catch (e: ClientRequestException) {
        when (e.response.status) {
            HttpStatusCode.NotFound -> throw ApiException.NotFound("Resource not found")
            HttpStatusCode.Unauthorized -> throw ApiException.Unauthorized("Unauthorized")
            HttpStatusCode.BadRequest -> throw ApiException.BadRequest("Bad request")
            else -> throw ApiException.BadRequest("Client error: ${e.response.status}")
        }
    } catch (e: ServerResponseException) {
        throw ApiException.ServerError("Server error: ${e.response.status}")
    } catch (e: IOException) {
        throw ApiException.NetworkError("Network error: ${e.message}")
    }
}

// 使用
suspend fun getUser(id: Int): User {
    return safeApiCall {
        client.get("https://api.example.com/users/$id").body()
    }
}
```

## Bad Practice

### 1. 不关闭客户端

```kotlin
// ❌ 错误：不关闭客户端会导致资源泄漏
suspend fun badExample() {
    val client = HttpClient(CIO)
    val response = client.get("https://api.example.com")
    println(response.bodyAsText())
    // 忘记关闭客户端
}

// ✅ 正确：使用 use 自动关闭
suspend fun goodExample() {
    HttpClient(CIO).use { client ->
        val response = client.get("https://api.example.com")
        println(response.bodyAsText())
    }
}

// ✅ 正确：使用 try-finally
suspend fun goodExample2() {
    val client = HttpClient(CIO)
    try {
        val response = client.get("https://api.example.com")
        println(response.bodyAsText())
    } finally {
        client.close()
    }
}
```

### 2. 每次请求创建新客户端

```kotlin
// ❌ 错误：每次请求都创建新客户端
suspend fun badExample() {
    repeat(100) {
        val client = HttpClient(CIO)  // 每次都创建新客户端
        val response = client.get("https://api.example.com")
        println(response.bodyAsText())
        client.close()
    }
}

// ✅ 正确：复用客户端
suspend fun goodExample() {
    val client = HttpClient(CIO)
    try {
        repeat(100) {
            val response = client.get("https://api.example.com")
            println(response.bodyAsText())
        }
    } finally {
        client.close()
    }
}
```

### 3. 忽略响应关闭

```kotlin
// ❌ 错误：不读取响应体可能导致连接泄漏
suspend fun badExample() {
    val client = HttpClient(CIO)
    val response = client.get("https://api.example.com")
    // 不读取响应体
    client.close()
}

// ✅ 正确：始终读取响应体
suspend fun goodExample() {
    val client = HttpClient(CIO)
    client.use {
        val response = it.get("https://api.example.com")
        val body = response.bodyAsText()  // 读取响应体
        println(body)
    }
}
```

### 4. 硬编码 URL 和配置

```kotlin
// ❌ 错误：硬编码配置
suspend fun badExample() {
    val client = HttpClient(CIO)
    val response = client.get("https://api.example.com/users")
    // ...
}

// ✅ 正确：使用配置类
class ApiConfig(
    val baseUrl: String,
    val timeout: Long = 30000,
    val retryCount: Int = 3
)

class ApiClient(private val config: ApiConfig) {
    private val client = HttpClient(CIO) {
        install(HttpTimeout) {
            requestTimeoutMillis = config.timeout
        }
        defaultRequest {
            url(config.baseUrl)
        }
    }
    
    suspend fun getUsers(): List<User> {
        return client.get("/users").body()
    }
}
```

### 5. 不使用适当的错误处理

```kotlin
// ❌ 错误：忽略错误处理
suspend fun badExample() {
    val client = HttpClient(CIO)
    val response = client.get("https://api.example.com/users")
    val users: List<User> = response.body()  // 可能抛出异常
    println(users)
}

// ✅ 正确：添加错误处理
suspend fun goodExample(): Result<List<User>> {
    val client = HttpClient(CIO)
    return try {
        val response = client.get("https://api.example.com/users")
        if (response.status.isSuccess()) {
            Result.success(response.body())
        } else {
            Result.failure(Exception("Failed to fetch users: ${response.status}"))
        }
    } catch (e: Exception) {
        Result.failure(e)
    } finally {
        client.close()
    }
}
```

### 6. 在 UI 线程执行网络请求

```kotlin
// ❌ 错误：在主线程执行网络请求（Android）
fun badExample() {
    val client = HttpClient(CIO)
    val response = runBlocking {  // 阻塞主线程
        client.get("https://api.example.com")
    }
}

// ✅ 正确：使用协程在后台线程执行
fun goodExample() {
    lifecycleScope.launch {
        val client = HttpClient(CIO)
        try {
            val response = client.get("https://api.example.com")
            // 更新 UI
        } finally {
            client.close()
        }
    }
}
```

## 最佳实践

### 1. 使用依赖注入管理客户端

```kotlin
// 使用 Koin 进行依赖注入
val networkModule = module {
    single {
        HttpClient(CIO) {
            install(ContentNegotiation) {
                json(Json {
                    ignoreUnknownKeys = true
                    prettyPrint = true
                })
            }
            install(Logging) {
                level = LogLevel.BODY
            }
            defaultRequest {
                url("https://api.example.com")
                header("Accept", "application/json")
            }
        }
    }
    
    single { ApiService(get()) }
}

class ApiService(private val client: HttpClient) {
    suspend fun getUsers(): List<User> = client.get("/users").body()
    suspend fun getUser(id: Int): User = client.get("/users/$id").body()
    suspend fun createUser(user: User): User = client.post("/users") {
        setBody(user)
    }.body()
}
```

### 2. 实现 Repository 模式

```kotlin
interface UserRepository {
    suspend fun getUsers(): Result<List<User>>
    suspend fun getUser(id: Int): Result<User>
    suspend fun createUser(user: User): Result<User>
    suspend fun updateUser(id: Int, user: User): Result<User>
    suspend fun deleteUser(id: Int): Result<Unit>
}

class UserRepositoryImpl(private val apiService: ApiService) : UserRepository {
    override suspend fun getUsers(): Result<List<User>> {
        return safeApiCall { apiService.getUsers() }
    }
    
    override suspend fun getUser(id: Int): Result<User> {
        return safeApiCall { apiService.getUser(id) }
    }
    
    override suspend fun createUser(user: User): Result<User> {
        return safeApiCall { apiService.createUser(user) }
    }
    
    override suspend fun updateUser(id: Int, user: User): Result<User> {
        return safeApiCall { apiService.updateUser(id, user) }
    }
    
    override suspend fun deleteUser(id: Int): Result<Unit> {
        return safeApiCall { apiService.deleteUser(id) }
    }
}
```

### 3. 使用密封类表示状态

```kotlin
sealed class ApiState<out T> {
    object Loading : ApiState<Nothing>()
    data class Success<T>(val data: T) : ApiState<T>()
    data class Error(val message: String, val exception: Throwable? = null) : ApiState<Nothing>()
}

class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _users = MutableStateFlow<ApiState<List<User>>>(ApiState.Loading)
    val users: StateFlow<ApiState<List<User>>> = _users.asStateFlow()
    
    fun loadUsers() {
        viewModelScope.launch {
            _users.value = ApiState.Loading
            _users.value = when (val result = repository.getUsers()) {
                is Result.Success -> ApiState.Success(result.getOrNull()!!)
                is Result.Failure -> ApiState.Error(
                    result.exceptionOrNull()?.message ?: "Unknown error"
                )
            }
        }
    }
}
```

### 4. 实现请求拦截和日志记录

```kotlin
val client = HttpClient(CIO) {
    install(Logging) {
        logger = Logger.DEFAULT
        level = LogLevel.ALL
        filter { request ->
            request.url.host.contains("api.example.com")
        }
    }
    
    install(createClientPlugin("RequestInterceptor") {
        onRequest { request, _ ->
            request.headers.append("X-Request-ID", generateRequestId())
            request.headers.append("X-Timestamp", System.currentTimeMillis().toString())
        }
        
        onResponse { response ->
            val duration = response.headers["X-Timestamp"]?.toLongOrNull()?.let {
                System.currentTimeMillis() - it
            }
            println("Request took ${duration}ms")
        }
    })
}

fun generateRequestId(): String {
    return java.util.UUID.randomUUID().toString()
}
```

### 5. 使用连接池和连接复用

```kotlin
val client = HttpClient(CIO) {
    engine {
        maxConnectionsCount = 1000
        endpoint {
            maxConnectionsPerRoute = 100
            keepAliveTime = 5000
            pipelineMaxSize = 20
        }
    }
    
    install(HttpRequestRetry) {
        retryOnServerErrors(maxRetries = 3)
        exponentialDelay()
    }
}
```

### 6. 实现缓存策略

```kotlin
import io.ktor.client.plugins.cache.*
import io.ktor.client.plugins.cache.storage.*

val client = HttpClient(CIO) {
    install(HttpCache) {
        publicStorage(FileStorage(File("cache")))
        privateStorage(FileStorage(File("private-cache")))
    }
}

// 手动控制缓存
suspend fun fetchWithCache() {
    val response = client.get("https://api.example.com/data") {
        header(HttpHeaders.CacheControl, "max-age=3600")
    }
}
```

## 性能优化

### 1. 选择合适的引擎

| 引擎 | 适用场景 | 性能特点 |
|------|---------|---------|
| CIO | 通用场景，推荐 | 纯 Kotlin 实现，性能好 |
| OkHttp | Android 开发 | 功能丰富，与 Android 集成好 |
| Apache | 企业级应用 | 成熟稳定，功能全面 |
| Java | 简单应用 | 基于 Java HttpClient |

```kotlin
// CIO 引擎（推荐）
val client = HttpClient(CIO)

// OkHttp 引擎（Android）
val client = HttpClient(OkHttp)

// Apache 引擎
val client = HttpClient(Apache)
```

### 2. 优化 JSON 序列化

```kotlin
val json = Json {
    ignoreUnknownKeys = true      // 忽略未知字段，提高兼容性
    isLenient = true              // 宽松解析
    encodeDefaults = false        // 不编码默认值，减少数据量
    allowSpecialFloatingPointValues = true
    useArrayPolymorphism = true
}

val client = HttpClient(CIO) {
    install(ContentNegotiation) {
        json(json)
    }
}
```

### 3. 使用流式处理大响应

```kotlin
import io.ktor.utils.io.*

suspend fun streamLargeResponse() {
    val client = HttpClient(CIO)
    
    client.prepareGet("https://api.example.com/large-file").execute { response ->
        val channel: ByteReadChannel = response.body()
        
        while (!channel.isClosedForRead) {
            val packet = channel.readRemaining(DEFAULT_BUFFER_SIZE.toLong())
            while (!packet.isEmpty) {
                val bytes = packet.readBytes()
                // 处理数据块
                processChunk(bytes)
            }
        }
    }
}
```

### 4. 并发请求优化

```kotlin
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll

suspend fun fetchMultipleUsers(userIds: List<Int>): List<User> {
    val client = HttpClient(CIO) {
        install(ContentNegotiation) {
            json()
        }
    }
    
    return client.use {
        userIds.map { id ->
            async {
                it.get("https://api.example.com/users/$id").body<User>()
            }
        }.awaitAll()
    }
}

// 限制并发数
suspend fun fetchWithLimit(userIds: List<Int>, limit: Int = 10): List<User> {
    val client = HttpClient(CIO)
    val semaphore = Semaphore(limit)
    
    return client.use {
        userIds.map { id ->
            async {
                semaphore.withPermit {
                    it.get("https://api.example.com/users/$id").body<User>()
                }
            }
        }.awaitAll()
    }
}
```

### 5. 监控和指标收集

```kotlin
val client = HttpClient(CIO) {
    install(createClientPlugin("Metrics") {
        onRequest { request, _ ->
            request.attributes.put(requestStartTime, System.currentTimeMillis())
        }
        
        onResponse { response ->
            val startTime = response.call.attributes[requestStartTime]
            val duration = System.currentTimeMillis() - startTime
            
            // 记录指标
            metrics.recordHttpRequest(
                method = response.call.request.method.value,
                status = response.status.value,
                duration = duration
            )
        }
    })
}

val requestStartTime = AttributeKey<Long>("RequestStartTime")

interface Metrics {
    fun recordHttpRequest(method: String, status: Int, duration: Long)
}
```

## 总结

Ktor Client 是一个功能强大、灵活的 HTTP 客户端，适用于各种 Kotlin 应用场景：

1. **核心优势**：基于协程的异步非阻塞、模块化架构、多引擎支持
2. **功能丰富**：支持各种 HTTP 方法、WebSocket、身份验证、序列化
3. **易于使用**：简洁的 DSL API、与 Kotlin 语言特性完美集成
4. **生产就绪**：提供完整的错误处理、重试机制、日志记录

**核心要点**：
- 始终正确关闭客户端，避免资源泄漏
- 复用客户端实例，不要每次请求都创建新客户端
- 使用依赖注入管理客户端配置
- 实现适当的错误处理和重试机制
- 选择合适的引擎和配置以优化性能
- 遵循最佳实践，避免常见的 Bad Practice

通过掌握 Ktor Client 的使用技巧，可以构建高效、可靠的 HTTP 客户端应用。