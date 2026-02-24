---
title: Kotlin 进阶
date: 2026-02-23
---
[[toc]]
***
## 扩展函数/Extension functions
在软件开发中，你经常需要在不修改原始源代码的情况下更改程序的行为。例如，你可能想为来自第三方库的类添加额外的功能。

你可以通过添加**扩展函数**来扩展一个类。调用扩展函数的方式与调用类的成员函数完全相同，即使用点符号 `.`。

在介绍扩展函数的完整语法之前，你需要理解什么是**接收者（receiver）**。接收者就是该函数被调用时所指向的对象。换句话说，接收者是信息共享的来源或对象。
![](assets/Pasted%20image%2020260223232010.png)

要创建一个扩展函数，先写下要扩展的类名，写个`.`号，再写上函数名称。记得写上函数参数和返回值类型
```kotlin
fun String.bold(): String = "<b>$this</b>"

fun main() {
    // "hello" is the receiver
    println("hello".bold())
    // <b>hello</b>
}
```
在这个例子中：
- `String`是被扩展的类
- `bold`是扩展函数的名称
- `.bold()`函数的返回值类型是`String`
- `"hello"`，`String`的实例，也是函数的接收者
- The receiver is accessed inside the body by the [keyword](https://kotlinlang.org/docs/keyword-reference.html): `this`.
- A string template (`$`) is used to access the value of `this`.
- The `.bold()` extension function takes a string and returns it in a `<b>` HTML element for bold text.
### 面向扩展设计
你可以在任何地方定义**扩展函数**，这使你能够创建“面向扩展”的设计。这种设计模式可以将**核心功能**与**有用但非必需的特性**分离开来，从而使你的代码更易于阅读和维护。

一个典型的例子是 Ktor 库中的 `HttpClient` 类，它用于执行网络请求。其核心功能仅由一个 `request()` 函数组成，该函数接收 HTTP 请求所需的所有信息：
```kotlin
class HttpClient {
    fun request(method: String, url: String, headers: Map<String, String>): HttpResponse {
        // 执行网络请求的核心代码
    }
}
```
在实际应用中，最常用的 HTTP 请求是 `GET` 或 `POST`。对于库来说，为这些常见用例提供更简短的名称（方法）是有意义的。然而，实现这些功能**并不需要**编写新的底层网络代码，而只需要调用特定的 `request` 即可。换句话说，它们是定义为独立的 `.get()` 和 `.post()` 扩展函数的绝佳选择：
```kotlin
fun HttpClient.get(url: String): HttpResponse = 
    request("GET", url, emptyMap())

fun HttpClient.post(url: String): HttpResponse = 
    request("POST", url, emptyMap())
```
这些 `.get()` 和 `.post()` 函数扩展了 `HttpClient` 类。由于它们是在 `HttpClient` 实例（作为**接收者**）上调用的，因此它们可以直接使用该类中的 `request()` 函数。通过使用这些扩展函数，你可以使用对应的 HTTP 方法来调用核心请求功能，这不仅简化了代码，还提升了可读性。
```kotlin
class HttpClient {
    fun request(method: String, url: String, headers: Map<String, String>): HttpResponse {
        println("Requesting $method to $url with headers: $headers")
        return HttpResponse("Response from $url")
    }
}

fun HttpClient.get(url: String): HttpResponse = request("GET", url, emptyMap())

fun main() {
    val client = HttpClient()

    // Making a GET request using request() directly
    val getResponseWithMember = client.request("GET", "https://example.com", emptyMap())

    // Making a GET request using the get() extension function
    // The client instance is the receiver
    val getResponseWithExtension = client.get("https://example.com")
}
```

* **Core vs. Non-essential**: 这种设计哲学建议保持类的“精简（Lean）”。类内部只存放必须访问私有成员的核心逻辑，而那些基于公开 API 实现的“便利方法（Convenience methods）”则应该放在类外部作为扩展。 
* **Separation of Concerns (关注点分离)**：这样做的好处是，如果你以后想给 `HttpClient` 增加 100 个方便的工具函数，你不需要把这个类变成一个拥有几千行代码的**上帝类（God Class）**
* **Discovery (易发现性)**：即便函数定义在类外面，IDE（如 IntelliJ 或 Android Studio）依然会在你输入 `httpClient.` 时自动提示这些扩展函数，使用体验与成员函数完全一致。 
这种模式在 Kotlin 的许多流行库（如 Ktor, Coil, Anko）中被广泛采用。

## 有限作用域函数/Scope functions
在编程中，**作用域（Scope）** 是指变量或对象能够被识别的区域。最常提到的作用域包括：

* **全局作用域（Global scope）**：可以从程序的任何地方访问的变量或对象。
* **局部作用域（Local scope）**：仅在定义它的代码块或函数内部才能访问的变量或对象。

在 Kotlin 中，还存在**作用域函数（Scope functions）**，它们允许你围绕一个对象创建一个**临时作用域**并执行特定代码。

作用域函数能让你的代码更加简洁，因为在临时作用域内，你无需反复引用对象的名称。根据所选的作用域函数，你可以通过关键字 `this`（引用对象本身）或关键字 `it`（作为参数引用）来访问该对象。

Kotlin 总共有五种作用域函数：`let`、`apply`、`run`、`also` 和 `with`。

每种作用域函数都接收一个 **Lambda 表达式**，并返回**该对象本身**或 **Lambda 表达式的结果**。在本次导览中，我们将逐一解释每种作用域函数及其用法。

:::tip
You can also watch the [Back to the Stdlib: Making the Most of Kotlin's Standard Library](https://youtu.be/DdvgvSHrN9g?feature=shared&t=1511) talk on scope functions by Sebastian Aigner, Kotlin developer advocate.
:::
### let

### apply

### run

### also

### with

***
# 页面底部