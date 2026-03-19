---
title: Java URL 相关类 API 详解
date: 2026-03-19
footer: Trae编辑
---


## 目录

1. [概述](#概述)
2. [URL 类](#url-类)
3. [URI 类](#uri-类)
4. [URLDecoder 类](#urldecoder-类)
5. [URLEncoder 类](#urlencoder-类)
6. [URLConnection 类](#urlconnection-类)
7. [HttpURLConnection 类](#httpurlconnection-类)
8. [URLStreamHandler 类](#urlstreamhandler-类)
9. [URLStreamHandlerFactory 接口](#urlstreamhandlerfactory-接口)
10. [使用示例](#使用示例)
11. [最佳实践](#最佳实践)
12. [常见问题与解决方案](#常见问题与解决方案)

## 概述

Java 提供了一组用于处理 URL（统一资源定位符）和 URI（统一资源标识符）的类，这些类位于 `java.net` 包中。Kotlin 作为 JVM 语言，可以直接使用这些类来处理 URL 相关操作。

**主要类包括**：
- `URL` - 表示统一资源定位符
- `URI` - 表示统一资源标识符
- `URLDecoder` - 解码 URL 编码的字符串
- `URLEncoder` - 编码字符串为 URL 格式
- `URLConnection` - 表示与 URL 之间的连接
- `HttpURLConnection` - 用于 HTTP 连接的特定实现
- `URLStreamHandler` - 处理特定协议的 URL 流
- `URLStreamHandlerFactory` - 创建 URL 流处理器的工厂

## URL 类

`URL` 类表示统一资源定位符，它是指向互联网资源的指针。

### 构造方法

```kotlin
// 1. 从字符串创建 URL
val url1 = URL("https://www.example.com")

// 2. 从协议、主机、路径创建
val url2 = URL("https", "www.example.com", "/path")

// 3. 从协议、主机、端口、路径创建
val url3 = URL("https", "www.example.com", 443, "/path")

// 4. 从基础 URL 和相对路径创建
val baseUrl = URL("https://www.example.com")
val relativeUrl = URL(baseUrl, "/path")
```

### 主要方法

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `getProtocol()` | 获取 URL 的协议部分 | `String` |
| `getHost()` | 获取 URL 的主机部分 | `String` |
| `getPort()` | 获取 URL 的端口部分 | `int` |
| `getDefaultPort()` | 获取协议的默认端口 | `int` |
| `getPath()` | 获取 URL 的路径部分 | `String` |
| `getQuery()` | 获取 URL 的查询部分 | `String` |
| `getRef()` | 获取 URL 的引用部分（片段标识符） | `String` |
| `getFile()` | 获取 URL 的文件部分（路径 + 查询） | `String` |
| `getUserInfo()` | 获取 URL 的用户信息部分 | `String` |
| `toExternalForm()` | 将 URL 转换为字符串 | `String` |
| `toString()` | 将 URL 转换为字符串 | `String` |
| `equals(Object)` | 比较两个 URL 是否相等 | `boolean` |
| `hashCode()` | 获取 URL 的哈希码 | `int` |
| `openConnection()` | 打开与 URL 的连接 | `URLConnection` |
| `openStream()` | 打开到 URL 的输入流 | `InputStream` |
| `getContent()` | 获取 URL 的内容 | `Object` |
| `getContent(Class[])` | 获取指定类型的 URL 内容 | `Object` |

### 示例

```kotlin
val url = URL("https://user:pass@www.example.com:8080/path?query=value#fragment")

println("Protocol: ${url.protocol}")      // https
println("Host: ${url.host}")              // www.example.com
println("Port: ${url.port}")              // 8080
println("Path: ${url.path}")              // /path
println("Query: ${url.query}")            // query=value
println("Ref: ${url.ref}")                // fragment
println("File: ${url.file}")              // /path?query=value
println("User Info: ${url.userInfo}")      // user:pass
```

## URI 类

`URI` 类表示统一资源标识符，它比 `URL` 更通用，不依赖于特定协议。

### 构造方法

```kotlin
// 1. 从字符串创建 URI
val uri1 = URI("https://www.example.com/path?query=value#fragment")

// 2. 从组件创建 URI
val uri2 = URI("https", "user:pass", "www.example.com", 8080, "/path", "query=value", "fragment")

// 3. 从协议、方案特定部分和片段创建
val uri3 = URI("https", "//www.example.com/path?query=value", "fragment")

// 4. 从方案特定部分创建（无协议）
val uri4 = URI("/path?query=value#fragment")
```

### 主要方法

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `getScheme()` | 获取 URI 的方案部分 | `String` |
| `getSchemeSpecificPart()` | 获取 URI 的方案特定部分 | `String` |
| `getAuthority()` | 获取 URI 的权威部分 | `String` |
| ` getUserInfo()` | 获取 URI 的用户信息部分 | `String` |
| `getHost()` | 获取 URI 的主机部分 | `String` |
| `getPort()` | 获取 URI 的端口部分 | `int` |
| `getPath()` | 获取 URI 的路径部分 | `String` |
| `getQuery()` | 获取 URI 的查询部分 | `String` |
| `getFragment()` | 获取 URI 的片段部分 | `String` |
| `isAbsolute()` | 检查 URI 是否为绝对 URI | `boolean` |
| `isOpaque()` | 检查 URI 是否为不透明 URI | `boolean` |
| `normalize()` | 规范化 URI | `URI` |
| `resolve(String)` | 解析相对 URI | `URI` |
| `resolve(URI)` | 解析相对 URI | `URI` |
| `relativize(URI)` | 创建相对 URI | `URI` |
| `toURL()` | 将 URI 转换为 URL | `URL` |
| `toString()` | 将 URI 转换为字符串 | `String` |
| `toASCIIString()` | 将 URI 转换为 ASCII 字符串 | `String` |
| `equals(Object)` | 比较两个 URI 是否相等 | `boolean` |
| `hashCode()` | 获取 URI 的哈希码 | `int` |

### 示例

```kotlin
val uri = URI("https://user:pass@www.example.com:8080/path?query=value#fragment")

println("Scheme: ${uri.scheme}")                  // https
println("Authority: ${uri.authority}")            // user:pass@www.example.com:8080
println("User Info: ${uri.userInfo}")            // user:pass
println("Host: ${uri.host}")                    // www.example.com
println("Port: ${uri.port}")                    // 8080
println("Path: ${uri.path}")                    // /path
println("Query: ${uri.query}")                  // query=value
println("Fragment: ${uri.fragment}")            // fragment
println("Is Absolute: ${uri.isAbsolute}")       // true
println("Is Opaque: ${uri.isOpaque}")          // false
```

## URLDecoder 类

`URLDecoder` 类用于解码 URL 编码的字符串。URL 编码将特殊字符转换为 `%xx` 格式。

### 主要方法

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `decode(String, String)` | 解码使用 application/x-www-form-urlencoded 格式编码的字符串 | `String` |
| `decode(String)` | 解码使用 application/x-www-form-urlencoded 格式编码的字符串（已废弃） | `String` |

### 示例

```kotlin
import java.net.URLDecoder

fun main() {
    val encoded = "Hello%20World%21%20%26%20%23"
    
    // 解码字符串
    val decoded = URLDecoder.decode(encoded, "UTF-8")
    println("Encoded: $encoded")
    println("Decoded: $decoded")  // Hello World! & #
    
    // 解码查询参数
    val query = "name=John+Doe&age=30&city=New+York"
    val decodedQuery = URLDecoder.decode(query, "UTF-8")
    println("Decoded query: $decodedQuery")  // name=John Doe&age=30&city=New York
}
```

## URLEncoder 类

`URLEncoder` 类用于将字符串编码为 URL 格式，将特殊字符转换为 `%xx` 格式。

### 主要方法

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `encode(String, String)` | 将字符串编码为 application/x-www-form-urlencoded 格式 | `String` |
| `encode(String)` | 将字符串编码为 application/x-www-form-urlencoded 格式（已废弃） | `String` |

### 示例

```kotlin
import java.net.URLEncoder

fun main() {
    val original = "Hello World! & #"
    
    // 编码字符串
    val encoded = URLEncoder.encode(original, "UTF-8")
    println("Original: $original")
    println("Encoded: $encoded")  // Hello+World%21+%26+%23
    
    // 编码查询参数
    val params = mapOf(
        "name" to "John Doe",
        "age" to "30",
        "city" to "New York"
    )
    
    val encodedParams = params
        .map { (key, value) -> 
            "${URLEncoder.encode(key, "UTF-8")}=${URLEncoder.encode(value, "UTF-8")}"
        }
        .joinToString("&")
    
    println("Encoded params: $encodedParams")
    // name=John+Doe&age=30&city=New+York
}
```

## URLConnection 类

`URLConnection` 类表示与 URL 之间的连接，是一个抽象类，具体实现由协议处理程序提供。

### 主要方法

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `connect()` | 打开与 URL 的连接 | `void` |
| `disconnect()` | 关闭与 URL 的连接 | `void` |
| `getInputStream()` | 获取输入流 | `InputStream` |
| `getOutputStream()` | 获取输出流 | `OutputStream` |
| `getContent()` | 获取 URL 的内容 | `Object` |
| `getContent(Class[])` | 获取指定类型的 URL 内容 | `Object` |
| `getContentType()` | 获取内容类型 | `String` |
| `getContentLength()` | 获取内容长度 | `int` |
| `getContentLengthLong()` | 获取内容长度（长整型） | `long` |
| `getDate()` | 获取内容的日期 | `long` |
| `getLastModified()` | 获取内容的最后修改时间 | `long` |
| `getExpiration()` | 获取内容的过期时间 | `long` |
| `getURL()` | 获取连接的 URL | `URL` |
| `getHeaderField(String)` | 获取指定头字段的值 | `String` |
| `getHeaderField(int)` | 获取指定索引的头字段的值 | `String` |
| `getHeaderFieldKey(int)` | 获取指定索引的头字段的键 | `String` |
| `getHeaderFields()` | 获取所有头字段 | `Map<String, List<String>>` |
| `setDoInput(boolean)` | 设置是否允许输入 | `void` |
| `setDoOutput(boolean)` | 设置是否允许输出 | `void` |
| `setUseCaches(boolean)` | 设置是否使用缓存 | `void` |
| `setIfModifiedSince(long)` | 设置 If-Modified-Since 头 | `void` |
| `setRequestProperty(String, String)` | 设置请求属性 | `void` |
| `getRequestProperty(String)` | 获取请求属性 | `String` |
| `getRequestProperties()` | 获取所有请求属性 | `Map<String, List<String>>` |

### 示例

```kotlin
import java.net.URL
import java.net.URLConnection

fun main() {
    val url = URL("https://www.example.com")
    val connection = url.openConnection()
    
    // 设置请求属性
    connection.setRequestProperty("User-Agent", "Mozilla/5.0")
    connection.setRequestProperty("Accept", "text/html")
    
    // 连接
    connection.connect()
    
    // 获取响应信息
    println("Content Type: ${connection.contentType}")
    println("Content Length: ${connection.contentLength}")
    println("Last Modified: ${connection.lastModified}")
    
    // 读取内容
    connection.inputStream.bufferedReader().use { reader ->
        val content = reader.readText()
        println("Content preview: ${content.take(100)}...")
    }
    
    // 断开连接
    connection.disconnect()
}
```

## HttpURLConnection 类

`HttpURLConnection` 是 `URLConnection` 的子类，专门用于 HTTP 连接。

### 主要方法

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `setRequestMethod(String)` | 设置请求方法（GET, POST, PUT, DELETE 等） | `void` |
| `getResponseCode()` | 获取 HTTP 响应码 | `int` |
| `getResponseMessage()` | 获取 HTTP 响应消息 | `String` |
| `setFollowRedirects(boolean)` | 设置是否跟随重定向 | `void` |
| `setInstanceFollowRedirects(boolean)` | 设置实例是否跟随重定向 | `void` |
| `getHeaderFieldKey(int)` | 获取指定索引的头字段的键 | `String` |
| `getHeaderField(int)` | 获取指定索引的头字段的值 | `String` |
| `getHeaderFields()` | 获取所有头字段 | `Map<String, List<String>>` |
| `setRequestProperty(String, String)` | 设置请求属性 | `void` |
| `getRequestProperty(String)` | 获取请求属性 | `String` |
| `addRequestProperty(String, String)` | 添加请求属性 | `void` |
| `setConnectTimeout(int)` | 设置连接超时时间 | `void` |
| `setReadTimeout(int)` | 设置读取超时时间 | `void` |
| `getConnectTimeout()` | 获取连接超时时间 | `int` |
| `getReadTimeout()` | 获取读取超时时间 | `int` |
| `getErrorStream()` | 获取错误流 | `InputStream` |

### 示例

```kotlin
import java.net.HttpURLConnection
import java.net.URL

fun main() {
    // GET 请求
    val url = URL("https://jsonplaceholder.typicode.com/posts/1")
    val connection = url.openConnection() as HttpURLConnection
    
    connection.requestMethod = "GET"
    connection.setRequestProperty("Accept", "application/json")
    
    val responseCode = connection.responseCode
    println("Response Code: $responseCode")
    
    if (responseCode == HttpURLConnection.HTTP_OK) {
        connection.inputStream.bufferedReader().use { reader ->
            val response = reader.readText()
            println("Response: $response")
        }
    } else {
        println("GET request failed")
    }
    
    connection.disconnect()
    
    // POST 请求
    val postUrl = URL("https://jsonplaceholder.typicode.com/posts")
    val postConnection = postUrl.openConnection() as HttpURLConnection
    
    postConnection.requestMethod = "POST"
    postConnection.setRequestProperty("Content-Type", "application/json")
    postConnection.doOutput = true
    
    val jsonInputString = "{\"title\": \"foo\", \"body\": \"bar\", \"userId\": 1}"
    postConnection.outputStream.use { os ->
        val input = jsonInputString.toByteArray(charset("UTF-8"))
        os.write(input, 0, input.size)
    }
    
    val postResponseCode = postConnection.responseCode
    println("POST Response Code: $postResponseCode")
    
    if (postResponseCode == HttpURLConnection.HTTP_CREATED) {
        postConnection.inputStream.bufferedReader().use { reader ->
            val response = reader.readText()
            println("POST Response: $response")
        }
    } else {
        println("POST request failed")
    }
    
    postConnection.disconnect()
}
```

## URLStreamHandler 类

`URLStreamHandler` 是一个抽象类，用于处理特定协议的 URL 流。

### 主要方法

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `openConnection(URL)` | 打开与 URL 的连接 | `URLConnection` |
| `openConnection(URL, Proxy)` | 使用代理打开与 URL 的连接 | `URLConnection` |
| `parseURL(URL, String, int, int)` | 解析 URL 字符串 | `void` |
| `toExternalForm(URL)` | 将 URL 转换为字符串 | `String` |
| `equals(URL, URL)` | 比较两个 URL 是否相等 | `boolean` |
| `getDefaultPort()` | 获取协议的默认端口 | `int` |
| `hashCode(URL)` | 获取 URL 的哈希码 | `int` |
| `hostsEqual(URL, URL)` | 比较两个 URL 的主机是否相等 | `boolean` |
| `sameFile(URL, URL)` | 比较两个 URL 是否指向同一文件 | `boolean` |

### 示例

```kotlin
import java.net.URL
import java.net.URLStreamHandler
import java.net.URLConnection

class CustomHandler : URLStreamHandler() {
    override fun openConnection(u: URL): URLConnection {
        // 实现自定义的连接逻辑
        throw UnsupportedOperationException("Not implemented")
    }
    
    override fun getDefaultPort(): Int {
        return 80  // 默认端口
    }
}

fun main() {
    // 注册自定义处理器
    URL.setURLStreamHandlerFactory {
        if (it == "custom") CustomHandler() else null
    }
    
    // 创建使用自定义协议的 URL
    val url = URL("custom://example.com/path")
    println("URL: $url")
    println("Protocol: ${url.protocol}")
    println("Host: ${url.host}")
}
```

## URLStreamHandlerFactory 接口

`URLStreamHandlerFactory` 接口用于创建 URL 流处理器。

### 方法

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `createURLStreamHandler(String)` | 创建指定协议的 URL 流处理器 | `URLStreamHandler` |

### 示例

```kotlin
import java.net.URL
import java.net.URLStreamHandler
import java.net.URLStreamHandlerFactory

class CustomURLStreamHandlerFactory : URLStreamHandlerFactory {
    override fun createURLStreamHandler(protocol: String): URLStreamHandler? {
        return when (protocol) {
            "custom" -> CustomHandler()
            else -> null  // 使用默认处理器
        }
    }
}

class CustomHandler : URLStreamHandler() {
    override fun openConnection(u: URL) = throw UnsupportedOperationException("Not implemented")
}

fun main() {
    // 设置 URL 流处理器工厂
    URL.setURLStreamHandlerFactory(CustomURLStreamHandlerFactory())
    
    // 现在可以使用自定义协议
    val url = URL("custom://example.com")
    println("Custom URL: $url")
}
```

## 使用示例

### 1. 基本 URL 解析

```kotlin
import java.net.URL

fun parseUrlExample() {
    val url = URL("https://www.example.com:8080/path/to/page?param1=value1&param2=value2#section1")
    
    println("=== URL 解析结果 ===")
    println("Protocol: ${url.protocol}")
    println("Host: ${url.host}")
    println("Port: ${url.port}")
    println("Path: ${url.path}")
    println("Query: ${url.query}")
    println("Ref: ${url.ref}")
    println("File: ${url.file}")
    println("Default Port: ${url.defaultPort}")
}
```

### 2. URI 操作

```kotlin
import java.net.URI

fun uriOperationsExample() {
    val baseUri = URI("https://www.example.com/path/")
    
    // 解析相对 URI
    val relativeUri = baseUri.resolve("subpath/file.html")
    println("Resolved URI: $relativeUri")
    
    // 创建相对 URI
    val otherUri = URI("https://www.example.com/path/other/file.html")
    val relativeToBase = baseUri.relativize(otherUri)
    println("Relative URI: $relativeToBase")
    
    // 规范化 URI
    val messyUri = URI("https://www.example.com/path/../other/./file.html")
    val normalizedUri = messyUri.normalize()
    println("Original: $messyUri")
    println("Normalized: $normalizedUri")
}
```

### 3. URL 编码和解码

```kotlin
import java.net.URLDecoder
import java.net.URLEncoder

fun urlEncodingExample() {
    // 编码示例
    val original = "Hello World! This is a test with spaces & special chars: #$%"
    val encoded = URLEncoder.encode(original, "UTF-8")
    println("Original: $original")
    println("Encoded: $encoded")
    
    // 解码示例
    val decoded = URLDecoder.decode(encoded, "UTF-8")
    println("Decoded: $decoded")
    
    // 编码查询参数
    val params = mapOf(
        "name" to "John Doe",
        "age" to "30",
        "city" to "New York",
        "message" to "Hello & Welcome!"
    )
    
    val queryString = params
        .map { (key, value) -> 
            "${URLEncoder.encode(key, "UTF-8")}=${URLEncoder.encode(value, "UTF-8")}"
        }
        .joinToString("&")
    
    println("Query String: $queryString")
}
```

### 4. 简单 HTTP 请求

```kotlin
import java.net.HttpURLConnection
import java.net.URL

fun httpRequestExample() {
    // GET 请求
    val url = URL("https://api.github.com/users/octocat")
    val connection = url.openConnection() as HttpURLConnection
    
    connection.requestMethod = "GET"
    connection.setRequestProperty("Accept", "application/json")
    connection.setRequestProperty("User-Agent", "Mozilla/5.0")
    
    val responseCode = connection.responseCode
    println("GET Response Code: $responseCode")
    
    if (responseCode == HttpURLConnection.HTTP_OK) {
        connection.inputStream.bufferedReader().use { reader ->
            val response = reader.readText()
            println("Response: $response")
        }
    }
    
    connection.disconnect()
    
    // POST 请求
    val postUrl = URL("https://httpbin.org/post")
    val postConnection = postUrl.openConnection() as HttpURLConnection
    
    postConnection.requestMethod = "POST"
    postConnection.setRequestProperty("Content-Type", "application/json")
    postConnection.doOutput = true
    
    val json = "{\"name\": \"Test\", \"value\": 123}"
    postConnection.outputStream.use { os ->
        val input = json.toByteArray(charset("UTF-8"))
        os.write(input, 0, input.size)
    }
    
    val postResponseCode = postConnection.responseCode
    println("POST Response Code: $postResponseCode")
    
    if (postResponseCode == HttpURLConnection.HTTP_OK) {
        postConnection.inputStream.bufferedReader().use { reader ->
            val response = reader.readText()
            println("POST Response: $response")
        }
    }
    
    postConnection.disconnect()
}
```

### 5. 下载文件

```kotlin
import java.io.FileOutputStream
import java.io.InputStream
import java.net.URL

fun downloadFileExample() {
    val url = URL("https://example.com/image.jpg")
    val fileName = "downloaded_image.jpg"
    
    url.openStream().use { inputStream ->
        FileOutputStream(fileName).use { outputStream ->
            val buffer = ByteArray(4096)
            var bytesRead: Int
            while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                outputStream.write(buffer, 0, bytesRead)
            }
        }
    }
    
    println("File downloaded successfully: $fileName")
}
```

## 最佳实践

### 1. 异常处理

```kotlin
import java.net.MalformedURLException
import java.net.URL

fun safeUrlCreation() {
    try {
        val url = URL("https://www.example.com")
        // 使用 URL
    } catch (e: MalformedURLException) {
        println("Invalid URL: ${e.message}")
    }
}
```

### 2. 资源管理

```kotlin
import java.net.HttpURLConnection
import java.net.URL

fun resourceManagementExample() {
    val url = URL("https://www.example.com")
    var connection: HttpURLConnection? = null
    
    try {
        connection = url.openConnection() as HttpURLConnection
        // 使用连接
    } finally {
        connection?.disconnect()
    }
    
    // 或者使用 use 函数（Kotlin）
    url.openConnection().use { conn ->
        // 使用连接
    }
}
```

### 3. 超时设置

```kotlin
import java.net.HttpURLConnection
import java.net.URL

fun timeoutExample() {
    val url = URL("https://www.example.com")
    val connection = url.openConnection() as HttpURLConnection
    
    // 设置超时时间（毫秒）
    connection.connectTimeout = 5000  // 连接超时
    connection.readTimeout = 10000   // 读取超时
    
    try {
        connection.connect()
        // 使用连接
    } finally {
        connection.disconnect()
    }
}
```

### 4. 代理设置

```kotlin
import java.net.HttpURLConnection
import java.net.InetSocketAddress
import java.net.Proxy
import java.net.URL

fun proxyExample() {
    val proxy = Proxy(Proxy.Type.HTTP, InetSocketAddress("proxy.example.com", 8080))
    val url = URL("https://www.example.com")
    val connection = url.openConnection(proxy) as HttpURLConnection
    
    try {
        connection.connect()
        // 使用连接
    } finally {
        connection.disconnect()
    }
}
```

### 5. 处理重定向

```kotlin
import java.net.HttpURLConnection
import java.net.URL

fun handleRedirectsExample() {
    val url = URL("https://example.com/redirect")
    val connection = url.openConnection() as HttpURLConnection
    
    // 跟随重定向
    connection.instanceFollowRedirects = true
    
    val responseCode = connection.responseCode
    println("Response Code: $responseCode")
    
    // 检查是否发生了重定向
    if (responseCode in 300..399) {
        val redirectUrl = connection.getHeaderField("Location")
        println("Redirected to: $redirectUrl")
    }
    
    connection.disconnect()
}
```

## 常见问题与解决方案

### 1. MalformedURLException

**问题**：创建 URL 时抛出 `MalformedURLException`

**解决方案**：
- 确保 URL 格式正确
- 捕获异常并处理
- 使用 `URI` 先验证，再转换为 `URL`

```kotlin
fun createUrlSafely(urlString: String): URL? {
    return try {
        URL(urlString)
    } catch (e: MalformedURLException) {
        println("Invalid URL: $urlString")
        null
    }
}

// 或者使用 URI
fun createUrlFromUri(urlString: String): URL? {
    return try {
        URI(urlString).toURL()
    } catch (e: Exception) {
        println("Invalid URL: $urlString")
        null
    }
}
```

### 2. 连接超时

**问题**：网络连接超时

**解决方案**：
- 设置合理的超时时间
- 实现重试机制
- 检查网络连接状态

```kotlin
fun connectWithTimeout(urlString: String, timeout: Int = 5000): HttpURLConnection? {
    return try {
        val url = URL(urlString)
        val connection = url.openConnection() as HttpURLConnection
        connection.connectTimeout = timeout
        connection.readTimeout = timeout
        connection
    } catch (e: Exception) {
        println("Connection failed: ${e.message}")
        null
    }
}
```

### 3. 403 Forbidden

**问题**：服务器返回 403 Forbidden

**解决方案**：
- 设置 User-Agent 头
- 确保请求合法
- 检查是否需要认证

```kotlin
fun setUserAgent(connection: HttpURLConnection) {
    connection.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
}
```

### 4. 字符编码问题

**问题**：URL 编码/解码时出现字符乱码

**解决方案**：
- 始终指定编码（推荐 UTF-8）
- 避免使用已废弃的方法

```kotlin
// 正确做法
val encoded = URLEncoder.encode(text, "UTF-8")
val decoded = URLDecoder.decode(encoded, "UTF-8")

// 错误做法（已废弃）
// val encoded = URLEncoder.encode(text)  // 不指定编码
```

### 5. 内存泄漏

**问题**：未关闭 URLConnection 导致内存泄漏

**解决方案**：
- 使用 try-with-resources 或 finally 块
- 在 Kotlin 中使用 use 函数

```kotlin
// Java 风格
val connection = url.openConnection()
try {
    // 使用连接
} finally {
    connection.disconnect()
}

// Kotlin 风格
url.openConnection().use {
    // 使用连接
}
```

### 6. 跨域问题

**问题**：浏览器中的跨域请求被阻止

**解决方案**：
- 服务器设置 CORS 头
- 使用代理服务器
- 在 Java 应用中不受此限制

### 7. SSL/TLS 问题

**问题**：HTTPS 连接失败

**解决方案**：
- 确保证书有效
- 配置 SSL 上下文
- 处理证书验证

```kotlin
import javax.net.ssl.HttpsURLConnection
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

fun disableSslVerification() {
    val trustAllCerts = arrayOf<TrustManager>(object : X509TrustManager {
        override fun checkClientTrusted(chain: Array<java.security.cert.X509Certificate>, authType: String) {}
        override fun checkServerTrusted(chain: Array<java.security.cert.X509Certificate>, authType: String) {}
        override fun getAcceptedIssuers(): Array<java.security.cert.X509Certificate> = arrayOf()
    })
    
    val sc = SSLContext.getInstance("SSL")
    sc.init(null, trustAllCerts, java.security.SecureRandom())
    HttpsURLConnection.setDefaultSSLSocketFactory(sc.socketFactory)
}

// 注意：仅用于测试，生产环境不应禁用 SSL 验证
```

## 总结

Java 提供了丰富的 URL 相关类，用于处理网络资源的定位、访问和操作：

1. **URL** - 用于表示和操作统一资源定位符
2. **URI** - 更通用的统一资源标识符表示
3. **URLDecoder/URLEncoder** - 用于 URL 编码和解码
4. **URLConnection** - 用于与 URL 建立连接
5. **HttpURLConnection** - 专门用于 HTTP 连接
6. **URLStreamHandler** - 处理特定协议的 URL 流
7. **URLStreamHandlerFactory** - 创建 URL 流处理器

**核心要点**：
- 始终处理异常，特别是 `MalformedURLException`
- 使用 try-with-resources 或 use 函数确保资源释放
- 设置合理的超时时间
- 正确处理 URL 编码和解码
- 遵循 HTTP 协议规范
- 注意安全问题，尤其是 SSL/TLS 配置

通过掌握这些 API，可以在 Kotlin 应用中有效地处理网络资源，实现各种网络操作，如 HTTP 请求、文件下载、API 调用等。