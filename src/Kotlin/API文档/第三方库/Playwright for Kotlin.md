---
title: Playwright for Kotlin
date: 2026-03-14
footer: Trae编辑
---


::: warning Kotlin Native 支持限制

**Playwright for Kotlin** 基于 Playwright Java 实现，**不支持 Kotlin Native**。

**技术原因**：
- Playwright 依赖 Chromium、Firefox、WebKit 等浏览器的原生二进制文件
- 这些浏览器引擎需要特定的运行时环境（JVM、Node.js、Python 等）
- Kotlin Native 无法直接调用这些浏览器原生二进制文件

**支持的平台**：
- **JVM**（完全支持）
- **Android**（有限支持，仅用于 WebView 测试）
- **JavaScript/Node.js**（官方原生支持）
- **Python**（官方原生支持）
- **.NET**（官方原生支持）

**替代方案（如需 Native 支持）**：
- 使用 **Ktor Client** + **JSoup** 进行静态页面抓取
- 使用 **Selenium WebDriver**（如果目标平台支持）
- 在 Native 代码中通过 FFI 调用其他语言的 Playwright 绑定

**推荐用法**：
- 在 JVM 环境中使用 Playwright 进行 Web 自动化测试
- 在 Native 项目中使用 Ktor Client 进行 HTTP 请求

:::

## 目录

1. [Playwright 概述](#playwright-概述)
2. [安装与配置](#安装与配置)
3. [核心概念](#核心概念)
4. [初级 API](#初级-api)
5. [中级 API](#中级-api)
6. [高级 API](#高级-api)
7. [Bad Practice](#bad-practice)
8. [最佳实践](#最佳实践)
9. [常见问题与解决方案](#常见问题与解决方案)

## Playwright 概述

Playwright 是微软开源的端到端（End-to-End）测试框架，支持现代 Web 应用的自动化测试。它提供了跨浏览器、跨平台的统一 API，支持 Chromium、Firefox 和 WebKit。

**核心特性**：
- 跨浏览器支持（Chromium、Firefox、WebKit）
- 自动等待机制，减少 flaky tests
- 支持有头和无头模式
- 支持移动端模拟
- 支持网络拦截和模拟
- 支持截图和视频录制
- 支持并行测试执行

## 安装与配置

### Maven 配置

```xml
<!-- pom.xml -->
<dependencies>
    <!-- Playwright Java/Kotlin -->
    <dependency>
        <groupId>com.microsoft.playwright</groupId>
        <artifactId>playwright</artifactId>
        <version>1.40.0</version>
    </dependency>
    
    <!-- 测试框架（可选） -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.0</version>
        <scope>test</scope>
    </dependency>
    
    <!-- Kotlin 协程支持 -->
    <dependency>
        <groupId>org.jetbrains.kotlinx</groupId>
        <artifactId>kotlinx-coroutines-core</artifactId>
        <version>1.7.3</version>
    </dependency>
</dependencies>
```

### Gradle 配置

```kotlin
// build.gradle.kts
dependencies {
    implementation("com.microsoft.playwright:playwright:1.40.0")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
}
```

### 安装浏览器

#### Maven 方式

```bash
# 安装 Playwright 浏览器
mvn exec:java -e -Dexec.mainClass=com.microsoft.playwright.CLI -Dexec.args="install"

# 或者只安装特定浏览器
mvn exec:java -e -Dexec.mainClass=com.microsoft.playwright.CLI -Dexec.args="install chromium"
mvn exec:java -e -Dexec.mainClass=com.microsoft.playwright.CLI -Dexec.args="install firefox"
mvn exec:java -e -Dexec.mainClass=com.microsoft.playwright.CLI -Dexec.args="install webkit"
```

#### Gradle 方式

```bash
# 安装 Playwright 浏览器
./gradlew run --args="install"

# 或者只安装特定浏览器
./gradlew run --args="install chromium"
./gradlew run --args="install firefox"
./gradlew run --args="install webkit"
```

**注意**：Gradle 方式需要在 `build.gradle.kts` 中添加以下配置：

```kotlin
tasks.register("run", JavaExec::class) {
    mainClass.set("com.microsoft.playwright.CLI")
    classpath = sourceSets["main"].runtimeClasspath
}
```

**替代方案**：也可以直接通过代码在首次运行时自动安装：

```kotlin
import com.microsoft.playwright.*

fun main() {
    // 首次运行时自动安装浏览器
    Playwright.install()
    
    // 然后创建 Playwright 实例
    Playwright.create().use { playwright ->
        val browser = playwright.chromium().launch()
        // ...
    }
}
```

## 核心概念

### Browser、BrowserContext、Page 关系

```
Browser (浏览器实例)
├── BrowserContext 1 (独立的会话环境)
│   ├── Page 1 (标签页)
│   ├── Page 2 (标签页)
│   └── Page 3 (标签页)
├── BrowserContext 2 (独立的会话环境)
│   ├── Page 1 (标签页)
│   └── Page 2 (标签页)
└── ...
```

| 概念 | 说明 | 使用场景 |
|------|------|---------|
| **Browser** | 浏览器实例 | 管理浏览器生命周期 |
| **BrowserContext** | 浏览器上下文，独立的会话环境 | 实现测试隔离、多用户场景 |
| **Page** | 浏览器标签页 | 执行页面操作 |

### Locator vs ElementHandle

| 特性 | Locator | ElementHandle |
|------|---------|---------------|
| 定位方式 | 捕获定位逻辑 | 指向特定元素 |
| 重新定位 | 自动重新定位 | 需要手动重新获取 |
| 推荐使用 | ✅ 推荐 | ⚠️ 尽量避免 |
| 性能 | 更好 | 较差 |

**核心区别**：
- **Locator**：捕获如何检索元素的逻辑，每次使用时都会重新定位元素
- **ElementHandle**：指向特定元素的引用，元素变化后可能失效

## 初级 API

### 1. 启动和关闭浏览器

```kotlin
import com.microsoft.playwright.*

// 基本启动
fun basicLaunch() {
    // 创建 Playwright 实例
    val playwright = Playwright.create()
    
    // 启动 Chromium 浏览器
    val browser = playwright.chromium().launch()
    
    // 创建新页面
    val page = browser.newPage()
    
    // 导航到 URL
    page.navigate("https://example.com")
    
    // 关闭资源（重要！）
    page.close()
    browser.close()
    playwright.close()
}

// 使用 use 自动关闭（推荐）
fun launchWithUse() {
    Playwright.create().use { playwright ->
        playwright.chromium().launch().use { browser ->
            browser.newPage().use { page ->
                page.navigate("https://example.com")
                println(page.title())
            }
        }
    }
}

// 带配置的启动
fun launchWithOptions() {
    Playwright.create().use { playwright ->
        val browser = playwright.chromium().launch(
            BrowserType.LaunchOptions()
                .setHeadless(false)           // 有头模式
                .setSlowMo(100)               // 慢动作（毫秒）
                .setArgs(listOf("--start-maximized"))  // 启动参数
        )
        
        browser.newPage().use { page ->
            page.navigate("https://example.com")
        }
        
        browser.close()
    }
}

// 启动有头浏览器的调试模式
fun launchWithDebug() {
    Playwright.create().use { playwright ->
        val browser = playwright.chromium().launch(
            BrowserType.LaunchOptions()
                .setHeadless(false)           // 有头模式
                .setSlowMo(200)               // 慢动作，便于观察
                .setDevtools(true)            // 自动打开 DevTools
                .setArgs(listOf(
                    "--start-maximized",        // 最大化窗口
                    "--auto-open-devtools-for-tabs"  // 每个标签页都打开 DevTools
                ))
        )
        
        browser.newPage().use { page ->
            page.navigate("https://example.com")
            // 在此处设置断点或进行手动操作
            // 程序会暂停，直到手动关闭浏览器
            println("Press Enter to continue...")
            readLine()  // 等待用户输入
        }
        
        browser.close()
    }
}

// 启动带有远程调试端口的浏览器
fun launchWithRemoteDebug() {
    Playwright.create().use { playwright ->
        val browser = playwright.chromium().launch(
            BrowserType.LaunchOptions()
                .setHeadless(false)
                .setArgs(listOf(
                    "--remote-debugging-port=9222",  // 远程调试端口
                    "--user-data-dir=/tmp/playwright-debug"  // 独立的用户数据目录
                ))
        )
        
        println("Remote debugging port: 9222")
        println("Open chrome://inspect in Chrome to debug")
        
        browser.newPage().use { page ->
            page.navigate("https://example.com")
            // 在此处进行调试
            println("Press Enter to exit...")
            readLine()
        }
        
        browser.close()
    }
}
```

### 2. 页面导航

```kotlin
// 基本导航
page.navigate("https://example.com")

// 带选项的导航
page.navigate("https://example.com", 
    Page.NavigateOptions()
        .setWaitUntil(WaitUntilState.NETWORKIDLE)  // 等待网络空闲
        .setTimeout(30000.0)                        // 超时时间
)

// 等待加载状态
page.waitForLoadState(LoadState.NETWORKIDLE)

// 前进和后退
page.goBack()
page.goForward()

// 重新加载
page.reload()

// 获取当前 URL
val currentUrl = page.url()

// 获取页面标题
val title = page.title()

// 相对路径导航
page.navigate("electronics")           // 相对路径：https://example.com/products/electronics
page.navigate("../services")            // 上级目录：https://example.com/services
page.navigate("./details")              // 当前目录：https://example.com/products/details
page.navigate("?page=2")               // 添加查询参数：https://example.com/products?page=2
page.navigate("#section")               // 添加锚点：https://example.com/products#section
page.navigate("settings?tab=general#preferences")  // 组合使用
```

### 3. 元素定位（Locator）

```kotlin
// CSS 选择器
val button = page.locator("button.submit")
val input = page.locator("#username")
val link = page.locator("a[href='/login']")

// XPath
val xpathElement = page.locator("xpath=//div[@class='container']")

// 文本内容
val textElement = page.locator("text=Click me")
val exactText = page.locator("text='Exact Text'")

// 角色（ARIA）
val roleElement = page.locator("role=button[name='Submit']")

// 测试 ID
val testIdElement = page.locator("data-testid=submit-button")

// 链式定位
val nestedElement = page.locator(".container").locator("button").locator("span")

// 过滤定位
val filteredButton = page.locator("button").filter(
    Locator.FilterOptions().setHasText("Submit")
)

// 获取多个元素
val buttons = page.locator("button")
val count = buttons.count()
```

### 4. 基本元素操作

```kotlin
// 点击
page.locator("button").click()

// 带选项的点击
page.locator("button").click(
    Locator.ClickOptions()
        .setButton(MouseButton.RIGHT)   // 右键点击
        .setClickCount(2)               // 双击
        .setDelay(100.0)                // 延迟（毫秒）
        .setForce(true)                 // 强制点击
)

// 填充输入框
page.locator("#username").fill("alice")

// 清空输入框
page.locator("#username").clear()

// 输入文本（模拟键盘输入）
page.locator("#username").type("alice")

// 按键盘按键
page.keyboard().press("Enter")
page.keyboard().press("Control+a")
page.keyboard().press("Tab")

// 获取文本内容
val text = page.locator(".title").textContent()

// 获取输入框值
val value = page.locator("#username").inputValue()

// 获取属性
val href = page.locator("a").getAttribute("href")

// 获取元素数量
val count = page.locator(".item").count()
```

### 5. 等待机制

```kotlin
// 等待元素可见
page.locator(".loading").waitFor(
    Locator.WaitForOptions()
        .setState(WaitForSelectorState.VISIBLE)
        .setTimeout(10000.0)
)

// 等待元素隐藏
page.locator(".loading").waitFor(
    Locator.WaitForOptions()
        .setState(WaitForSelectorState.HIDDEN)
)

// 等待网络空闲
page.waitForLoadState(LoadState.NETWORKIDLE)

// 等待特定请求
page.waitForRequest("**/api/users")
page.waitForResponse("**/api/users")

// 等待函数返回 true
page.waitForFunction("() => document.title === 'Loaded'")

// 等待超时
page.waitForTimeout(1000.0)  // 等待 1 秒

// 内置调试器
page.pause()  // 暂停执行并打开 Playwright Inspector

// 手动断点
page.evaluate("debugger;")  // 在浏览器中触发断点
```

### 调试工具

#### Playwright Inspector

Playwright 提供了一个内置的调试工具叫做 Playwright Inspector，可以帮助你：
- 查看当前页面状态
- 检查元素选择器
- 步进执行测试
- 查看网络请求

**使用方法**：

```kotlin
// 方法 1：使用 page.pause()
fun debugWithPause() {
    Playwright.create().use { playwright ->
        val browser = playwright.chromium().launch(
            BrowserType.LaunchOptions().setHeadless(false)
        )
        
        browser.newPage().use { page ->
            page.navigate("https://example.com")
            
            // 暂停并打开 Inspector
            page.pause()
            
            // 在此处，Playwright Inspector 会打开
            // 你可以在 Inspector 中执行各种操作
            page.locator("button").click()
        }
        
        browser.close()
    }
}

// 方法 2：设置环境变量
// 运行测试前设置环境变量：
// set PWDEBUG=1 (Windows)
// export PWDEBUG=1 (Linux/Mac)

// 方法 3：使用 Playwright CLI
// npx playwright codegen https://example.com
```

#### 调试模式的配置选项

```kotlin
// 启动调试模式
fun launchWithDebugMode() {
    Playwright.create().use { playwright ->
        val browser = playwright.chromium().launch(
            BrowserType.LaunchOptions()
                .setHeadless(false)
                .setSlowMo(100)  // 慢动作执行
                .setEnv(mapOf(
                    "PWDEBUG" to "1",  // 启用调试模式
                    "PWDEBUG_JSON" to "true"  // 启用 JSON 输出
                ))
        )
        
        browser.newPage().use { page ->
            page.navigate("https://example.com")
            // 执行操作...
        }
        
        browser.close()
    }
}
```

## 中级 API

### 1. 表单处理

```kotlin
// 填写表单
page.locator("#username").fill("alice")
page.locator("#password").fill("secret123")
page.locator("button[type='submit']").click()

// 选择下拉框
page.locator("#country").selectOption("USA")
page.locator("#country").selectOption(
    Locator.SelectOptionOptions().setLabel("United States")
)

// 选择多个选项
page.locator("#hobbies").selectOption(arrayOf("reading", "gaming"))

// 勾选复选框
page.locator("#agree").check()
page.locator("#agree").uncheck()

// 检查复选框状态
val isChecked = page.locator("#agree").isChecked()

// 单选按钮
page.locator("input[type='radio'][value='male']").check()

// 文件上传
page.locator("input[type='file']").setInputFiles(Paths.get("/path/to/file.txt"))

// 多文件上传
page.locator("input[type='file']").setInputFiles(arrayOf(
    Paths.get("/path/to/file1.txt"),
    Paths.get("/path/to/file2.txt")
))
```

### 2. 断言和验证

```kotlin
import com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat

// 元素可见性
assertThat(page.locator(".success-message")).isVisible()
assertThat(page.locator(".error-message")).isHidden()

// 文本内容
assertThat(page.locator(".title")).hasText("Welcome")
assertThat(page.locator(".description")).containsText("important")

// 输入框值
assertThat(page.locator("#username")).hasValue("alice")

// 属性
assertThat(page.locator("a")).hasAttribute("href", "/home")

// 元素数量
assertThat(page.locator(".item")).hasCount(5)

// 复选框状态
assertThat(page.locator("#agree")).isChecked()

// URL
assertThat(page).hasURL("https://example.com/dashboard")

// 标题
assertThat(page).hasTitle("Dashboard")

// 自定义超时
assertThat(page.locator(".slow-element")).isVisible(
    LocatorAssertions.IsVisibleOptions().setTimeout(10000.0)
)
```

### 3. 截图和录制

```kotlin
// 页面截图
page.screenshot(Page.ScreenshotOptions()
    .setPath(Paths.get("screenshot.png"))
    .setFullPage(true)           // 完整页面
    .setType(ScreenshotType.PNG)
)

// 元素截图
page.locator(".chart").screenshot(Locator.ScreenshotOptions()
    .setPath(Paths.get("chart.png"))
)

// 视频录制
val context = browser.newContext(Browser.NewContextOptions()
    .setRecordVideoDir(Paths.get("videos/"))
    .setRecordVideoSize(1280, 720)
)

val page = context.newPage()
page.navigate("https://example.com")
// ... 执行操作

context.close()  // 视频会在关闭时保存
```

### 4. 对话框处理

```kotlin
// 监听对话框
page.onDialog { dialog ->
    println("Dialog message: ${dialog.message()}")
    when (dialog.type()) {
        "alert" -> dialog.accept()
        "confirm" -> dialog.accept()  // 或 dialog.dismiss()
        "prompt" -> dialog.accept("input text")
    }
}

// 自动处理对话框
page.onDialog { dialog ->
    dialog.accept()
}

// 特定对话框处理
page.onceDialog { dialog ->
    if (dialog.message().contains("Are you sure")) {
        dialog.accept()
    } else {
        dialog.dismiss()
    }
}
```

### 5. 网络拦截和模拟

```kotlin
// 拦截请求
page.route("**/api/users") { route ->
    route.fulfill(Route.FulfillOptions()
        .setStatus(200)
        .setContentType("application/json")
        .setBody("""{"users": []}""")
    )
}

// 修改请求
page.route("**/api/users") { route ->
    val headers = route.request().headers()
    headers["X-Custom-Header"] = "value"
    route.resume(Route.ResumeOptions().setHeaders(headers))
}

// 中止请求
page.route("**/*.png") { route ->
    route.abort()
}

// 模拟网络条件
val context = browser.newContext(Browser.NewContextOptions()
    .setOffline(true)  // 离线模式
)

// 模拟慢速网络
val context = browser.newContext(Browser.NewContextOptions()
    .setViewportSize(1280, 720)
)

// 在页面级别模拟
page.route("**") { route ->
    route.resume(Route.ResumeOptions().setSlowMo(100))
}
```

### 6. 浏览器上下文管理

```kotlin
// 创建新的浏览器上下文
val context = browser.newContext()

// 带配置的上下文
val context = browser.newContext(Browser.NewContextOptions()
    .setViewportSize(1920, 1080)
    .setUserAgent("Custom User Agent")
    .setLocale("zh-CN")
    .setTimezoneId("Asia/Shanghai")
    .setGeolocation(39.9042, 116.4074)  // 北京坐标
    .setPermissions(listOf("geolocation"))
    .setColorScheme(ColorScheme.DARK)
)

// 创建新页面
val page1 = context.newPage()
val page2 = context.newPage()

// 页面间通信
page1.evaluate("window.sharedData = 'hello'")

// 存储状态（Cookies、LocalStorage 等）
val storageState = context.storageState()

// 从存储状态恢复
val newContext = browser.newContext(Browser.NewContextOptions()
    .setStorageState(storageState)
)

// 清除 Cookies
context.clearCookies()

// 添加 Cookie
context.addCookies(listOf(
    Cookie("session", "value123")
        .setDomain(".example.com")
        .setPath("/")
))
```

## 高级 API

### 1. 移动端模拟

```kotlin
// iPhone 模拟
val iPhone = playwright.devices()["iPhone 14 Pro Max"]
val context = browser.newContext(Browser.NewContextOptions()
    .setViewportSize(iPhone.viewportSize)
    .setUserAgent(iPhone.userAgent)
    .setDeviceScaleFactor(iPhone.deviceScaleFactor)
    .setIsMobile(iPhone.isMobile)
    .setHasTouch(iPhone.hasTouch)
)

// 自定义移动设备
val context = browser.newContext(Browser.NewContextOptions()
    .setViewportSize(375, 812)      // iPhone X 尺寸
    .setDeviceScaleFactor(3.0)
    .setIsMobile(true)
    .setHasTouch(true)
    .setUserAgent("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)")
)

// 触摸事件
page.locator("button").tap()

// 多点触控（缩放）
page.touchscreen().pinch(200.0, 300.0, 1.5)  // 放大 1.5 倍
```

### 2. 文件下载处理

```kotlin
// 等待下载
val download = page.waitForDownload {
    page.locator("a[download]").click()
}

// 获取下载信息
println("Downloaded file: ${download.suggestedFilename()}")
println("Download URL: ${download.url()}")

// 保存下载文件
val path = download.path()
download.saveAs(Paths.get("/custom/path/${download.suggestedFilename()}"))

// 取消下载
download.cancel()
```

### 3. 多窗口和标签页管理

```kotlin
// 监听新页面
val newPage = context.waitForPage {
    page.locator("a[target='_blank']").click()
}

// 获取所有页面
val pages = context.pages()

// 切换到特定页面
val popup = pages.find { it.url().contains("popup") }
popup?.bringToFront()

// 关闭页面
popup?.close()

// 监听窗口关闭
page.onClose { _ ->
    println("Page closed")
}
```

### 4. 执行 JavaScript

```kotlin
// 执行脚本并获取结果
val title = page.evaluate("document.title")

// 带参数的执行
val result = page.evaluate("(a, b) => a + b", 5, 3)
println(result)  // 8

// 执行并返回复杂对象
val data = page.evaluate("() => {
    return {
        title: document.title,
        url: window.location.href,
        width: window.innerWidth
    }
}")

// 在特定元素上执行
val element = page.locator("#myElement")
val text = element.evaluate("el => el.textContent")

// 添加脚本到页面
page.addScriptTag(Page.AddScriptTagOptions()
    .setContent("window.myVar = 'hello'")
)

// 添加外部脚本
page.addScriptTag(Page.AddScriptTagOptions()
    .setUrl("https://example.com/script.js")
)
```

### 5. 认证和状态管理

```kotlin
// HTTP Basic 认证
val context = browser.newContext(Browser.NewContextOptions()
    .setHttpCredentials("username", "password")
)

// 表单认证（推荐方式）
fun login(page: Page, username: String, password: String) {
    page.navigate("https://example.com/login")
    page.locator("#username").fill(username)
    page.locator("#password").fill(password)
    page.locator("button[type='submit']").click()
    
    // 等待登录成功
    page.waitForURL("**/dashboard")
}

// 保存认证状态
fun saveAuthState(browser: Browser, username: String, password: String): String {
    val context = browser.newContext()
    val page = context.newPage()
    
    login(page, username, password)
    
    // 保存存储状态
    val state = context.storageState()
    context.close()
    
    return state
}

// 使用保存的认证状态
fun createAuthenticatedContext(browser: Browser, authState: String): BrowserContext {
    return browser.newContext(Browser.NewContextOptions()
        .setStorageState(authState)
    )
}
```

### 6. 并行测试执行

```kotlin
import kotlinx.coroutines.*

// 使用 JUnit 5 并行执行
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class ParallelTests {
    
    private lateinit var playwright: Playwright
    private lateinit var browser: Browser
    
    @BeforeAll
    fun setup() {
        playwright = Playwright.create()
        browser = playwright.chromium().launch()
    }
    
    @AfterAll
    fun teardown() {
        browser.close()
        playwright.close()
    }
    
    @Test
    fun test1() {
        browser.newContext().use { context ->
            val page = context.newPage()
            page.navigate("https://example.com/page1")
            // 测试逻辑
        }
    }
    
    @Test
    fun test2() {
        browser.newContext().use { context ->
            val page = context.newPage()
            page.navigate("https://example.com/page2")
            // 测试逻辑
        }
    }
}

// 使用协程并行执行
suspend fun runParallelTests() = coroutineScope {
    val playwright = Playwright.create()
    val browser = playwright.chromium().launch()
    
    try {
        val jobs = listOf(
            async { runTest(browser, "https://example.com/page1") },
            async { runTest(browser, "https://example.com/page2") },
            async { runTest(browser, "https://example.com/page3") }
        )
        
        jobs.awaitAll()
    } finally {
        browser.close()
        playwright.close()
    }
}

suspend fun runTest(browser: Browser, url: String) {
    browser.newContext().use { context ->
        val page = context.newPage()
        page.navigate(url)
        // 测试逻辑
    }
}
```

### 7. 自定义选择器引擎

```kotlin
// 注册自定义选择器引擎
playwright.selectors().register("data-test", "{
    query(root, selector) {
        return root.querySelector('[data-test=\"' + selector + '\"]');
    },
    queryAll(root, selector) {
        return root.querySelectorAll('[data-test=\"' + selector + '\"]');
    }
}")

// 使用自定义选择器
val element = page.locator("data-test=submit-button")
```

### 8. 性能监控

```kotlin
// 监听性能指标
page.onPageError { error ->
    println("Page error: $error")
}

page.onConsoleMessage { message ->
    println("Console ${message.type()}: ${message.text()}")
}

page.onRequest { request ->
    println("Request: ${request.method()} ${request.url()}")
}

page.onResponse { response ->
    println("Response: ${response.status()} ${response.url()}")
}

page.onRequestFailed { request ->
    println("Failed: ${request.url()}")
}

page.onRequestFinished { request ->
    val response = request.response()
    println("Finished: ${request.url()} - ${response?.status()}")
}

// 获取性能指标
val metrics = page.evaluate("() => JSON.stringify(performance.getEntriesByType('navigation')[0])")
println(metrics)
```
## 其他
### 1. 保存页面
```kotlin
// 保存页面的N种方式

// 1. 保存为截图
fun savePageAsScreenshot(page: Page) {
    // 完整页面截图
    page.screenshot(Page.ScreenshotOptions()
        .setPath(Paths.get("full-page.png"))
        .setFullPage(true)
        .setType(ScreenshotType.PNG)
    )
    
    // 可视区域截图
    page.screenshot(Page.ScreenshotOptions()
        .setPath(Paths.get("viewport.png"))
        .setFullPage(false)
    )
    
    // 高质量截图
    page.screenshot(Page.ScreenshotOptions()
        .setPath(Paths.get("high-quality.png"))
        .setQuality(100.0)  // 0-100
    )
    
    // 特定元素截图
    page.locator(".main-content").screenshot(Locator.ScreenshotOptions()
        .setPath(Paths.get("element.png"))
    )
}

// 2. 保存为 PDF
fun savePageAsPdf(page: Page) {
    page.pdf(Page.PdfOptions()
        .setPath(Paths.get("page.pdf"))
        .setFormat("A4")  // A3, A4, A5, Legal, Letter, Tabloid
        .setMarginTop("1cm")
        .setMarginBottom("1cm")
        .setMarginLeft("1cm")
        .setMarginRight("1cm")
        .setPrintBackground(true)  // 包含背景
        .setLandscape(false)  // 纵向
    )
}

// 3. 保存为 HTML
fun savePageAsHtml(page: Page) {
    // 获取完整 HTML
    val html = page.content()
    
    // 保存到文件
    Files.writeString(Paths.get("page.html"), html)
    
    // 保存为 MHTML（包含所有资源）
    val mhtml = page.content(Page.ContentOptions().setType(Page.ContentOptions.Type.MHTML))
    Files.writeString(Paths.get("page.mhtml"), mhtml)
}

// 4. 保存为文本
fun savePageAsText(page: Page) {
    // 获取纯文本
    val text = page.textContent("html")
    text?.let {
        Files.writeString(Paths.get("page.txt"), it)
    }
}

// 5. 保存网络请求和响应
fun saveNetworkTraffic(page: Page) {
    val requests = mutableListOf<Map<String, Any>>()
    
    // 监听所有请求
    page.onRequest { request ->
        val requestInfo = mapOf(
            "method" to request.method(),
            "url" to request.url(),
            "headers" to request.headers(),
            "postData" to request.postData()
        )
        requests.add(requestInfo)
    }
    
    // 监听所有响应
    page.onResponse { response ->
        val responseInfo = mapOf(
            "status" to response.status(),
            "url" to response.url(),
            "headers" to response.headers()
            // 注意：响应体可能很大，需要谨慎保存
        )
        requests.add(responseInfo)
    }
    
    // 导航到页面
    page.navigate("https://example.com")
    
    // 等待网络空闲
    page.waitForLoadState(LoadState.NETWORKIDLE)
    
    // 保存网络流量到文件
    val gson = com.google.gson.GsonBuilder().setPrettyPrinting().create()
    val json = gson.toJson(requests)
    Files.writeString(Paths.get("network-traffic.json"), json)
}

// 6. 保存特定区域
fun saveRegion(page: Page) {
    // 定位元素
    val element = page.locator(".product-grid")
    
    // 获取元素边界
    val box = element.boundingBox()
    box?.let {
        // 截取特定区域
        page.screenshot(Page.ScreenshotOptions()
            .setPath(Paths.get("region.png"))
            .setClip(Page.Clip()
                .setX(it.x)
                .setY(it.y)
                .setWidth(it.width)
                .setHeight(it.height)
            )
        )
    }
}

// 7. 保存为视频（详细版）
fun savePageAsVideo() {
    Playwright.create().use { playwright ->
        val context = playwright.chromium().newContext(
            Browser.NewContextOptions()
                .setRecordVideoDir(Paths.get("videos/"))
                .setRecordVideoSize(1920, 1080)  // 1080p
        )
        
        val page = context.newPage()
        
        try {
            page.navigate("https://example.com")
            // 执行操作...
            page.locator("button").click()
            page.waitForTimeout(2000)
        } finally {
            // 关闭上下文时自动保存视频
            context.close()
        }
    }
}
```
## Bad Practice

### 1. 不关闭资源

```kotlin
// ❌ 错误：不关闭资源会导致内存泄漏
fun badExample() {
    val playwright = Playwright.create()
    val browser = playwright.chromium().launch()
    val page = browser.newPage()
    
    page.navigate("https://example.com")
    // 忘记关闭 page、browser、playwright
}

// ✅ 正确：使用 use 自动关闭
fun goodExample() {
    Playwright.create().use { playwright ->
        playwright.chromium().launch().use { browser ->
            browser.newPage().use { page ->
                page.navigate("https://example.com")
            }
        }
    }
}
```

### 2. 使用 ElementHandle 而非 Locator

```kotlin
// ❌ 错误：使用 ElementHandle，元素可能失效
fun badExample(page: Page) {
    val handle = page.querySelector(".dynamic-element")
    page.waitForTimeout(1000)  // 元素可能在此期间变化
    handle?.click()  // 可能点击到错误的元素或抛出异常
}

// ✅ 正确：使用 Locator，每次操作都重新定位
fun goodExample(page: Page) {
    val locator = page.locator(".dynamic-element")
    locator.click()  // 自动等待并重新定位
}
```

### 3. 使用固定等待时间

```kotlin
// ❌ 错误：使用固定等待时间
fun badExample(page: Page) {
    page.locator("button").click()
    page.waitForTimeout(2000)  // 固定等待 2 秒
    page.locator(".result").click()
}

// ✅ 正确：使用智能等待
fun goodExample(page: Page) {
    page.locator("button").click()
    page.locator(".result").waitFor()  // 自动等待元素出现
    page.locator(".result").click()
}
```

### 4. 不使用断言

```kotlin
// ❌ 错误：不使用断言验证结果
fun badExample(page: Page) {
    page.locator("#username").fill("alice")
    page.locator("#password").fill("secret")
    page.locator("button").click()
    
    // 没有验证登录是否成功
    val title = page.title()
    println(title)  // 只是打印，没有验证
}

// ✅ 正确：使用断言验证
fun goodExample(page: Page) {
    page.locator("#username").fill("alice")
    page.locator("#password").fill("secret")
    page.locator("button").click()
    
    // 验证登录成功
    assertThat(page).hasURL("**/dashboard")
    assertThat(page.locator(".welcome-message")).containsText("Welcome, alice")
}
```

### 5. 硬编码选择器

```kotlin
// ❌ 错误：硬编码脆弱的选择器
fun badExample(page: Page) {
    page.locator("div > div:nth-child(3) > span").click()
    page.locator("#app > div > button").fill("text")
}

// ✅ 正确：使用语义化选择器
fun goodExample(page: Page) {
    page.locator("[data-testid=submit-button]").click()
    page.locator("role=textbox[name='Username']").fill("text")
}
```

### 6. 忽略错误处理

```kotlin
// ❌ 错误：忽略可能的异常
fun badExample(page: Page) {
    page.navigate("https://example.com")
    page.locator(".might-not-exist").click()
}

// ✅ 正确：添加错误处理
fun goodExample(page: Page) {
    try {
        page.navigate("https://example.com")
        
        // 检查元素是否存在
        val locator = page.locator(".might-not-exist")
        if (locator.count() > 0) {
            locator.click()
        } else {
            println("Element not found, skipping")
        }
    } catch (e: PlaywrightException) {
        println("Error: ${e.message}")
        // 适当的错误处理
    }
}
```

### 7. 在测试中使用真实数据

```kotlin
// ❌ 错误：使用真实用户数据
fun badExample(page: Page) {
    page.locator("#username").fill("real.user@company.com")
    page.locator("#password").fill("RealPassword123!")
}

// ✅ 正确：使用测试专用数据
fun goodExample(page: Page) {
    page.locator("#username").fill("test.user@example.com")
    page.locator("#password").fill("TestPassword123!")
}
```

## 最佳实践

### 1. 使用 Page Object Model 模式

```kotlin
// 基础页面类
abstract class BasePage(protected val page: Page) {
    abstract fun waitForPageLoaded()
    
    fun navigate(url: String) {
        page.navigate(url)
        waitForPageLoaded()
    }
}

// 登录页面
class LoginPage(page: Page) : BasePage(page) {
    private val usernameInput = page.locator("[data-testid=username-input]")
    private val passwordInput = page.locator("[data-testid=password-input]")
    private val submitButton = page.locator("[data-testid=login-button]")
    private val errorMessage = page.locator("[data-testid=error-message]")
    
    override fun waitForPageLoaded() {
        assertThat(usernameInput).isVisible()
        assertThat(passwordInput).isVisible()
        assertThat(submitButton).isVisible()
    }
    
    fun login(username: String, password: String): DashboardPage {
        usernameInput.fill(username)
        passwordInput.fill(password)
        submitButton.click()
        
        return DashboardPage(page)
    }
    
    fun getErrorMessage(): String? {
        return if (errorMessage.isVisible) {
            errorMessage.textContent()
        } else {
            null
        }
    }
}

// 仪表板页面
class DashboardPage(page: Page) : BasePage(page) {
    private val welcomeMessage = page.locator("[data-testid=welcome-message]")
    private val logoutButton = page.locator("[data-testid=logout-button]")
    
    override fun waitForPageLoaded() {
        assertThat(welcomeMessage).isVisible()
        assertThat(page).hasURL("**/dashboard")
    }
    
    fun getWelcomeText(): String {
        return welcomeMessage.textContent() ?: ""
    }
    
    fun logout(): LoginPage {
        logoutButton.click()
        return LoginPage(page)
    }
}

// 使用示例
@Test
fun testLogin() {
    Playwright.create().use { playwright ->
        playwright.chromium().launch().use { browser ->
            browser.newPage().use { page ->
                val loginPage = LoginPage(page)
                loginPage.navigate("https://example.com/login")
                
                val dashboardPage = loginPage.login("test.user", "password123")
                assertThat(dashboardPage.getWelcomeText()).contains("Welcome")
                
                val returnedLoginPage = dashboardPage.logout()
                assertThat(page).hasURL("**/login")
            }
        }
    }
}
```

### 2. 使用 Fixture 管理测试资源

```kotlin
// 测试基类
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
abstract class PlaywrightTestBase {
    
    protected lateinit var playwright: Playwright
    protected lateinit var browser: Browser
    
    @BeforeAll
    fun setup() {
        playwright = Playwright.create()
        browser = playwright.chromium().launch(
            BrowserType.LaunchOptions()
                .setHeadless(System.getenv("CI") != null)
                .setSlowMo(if (System.getenv("DEBUG") != null) 1000 else 0)
        )
    }
    
    @AfterAll
    fun teardown() {
        browser.close()
        playwright.close()
    }
    
    protected fun newContext(): BrowserContext {
        return browser.newContext(Browser.NewContextOptions()
            .setViewportSize(1920, 1080)
            .setRecordVideoDir(Paths.get("test-results/videos/"))
            .setRecordVideoSize(1920, 1080)
        )
    }
}

// 具体测试类
class LoginTests : PlaywrightTestBase() {
    
    @Test
    fun `successful login`() {
        newContext().use { context ->
            val page = context.newPage()
            val loginPage = LoginPage(page)
            
            loginPage.navigate("https://example.com/login")
            val dashboardPage = loginPage.login("test.user", "password123")
            
            assertThat(dashboardPage.getWelcomeText()).contains("Welcome")
        }
    }
}
```

### 3. 数据驱动测试

```kotlin
@ParameterizedTest
@CsvSource(
    "valid.user, correct.password, true",
    "invalid.user, wrong.password, false",
    "empty.user, , false",
    "locked.user, correct.password, false"
)
fun `login with different credentials`(
    username: String,
    password: String,
    shouldSucceed: Boolean
) {
    Playwright.create().use { playwright ->
        playwright.chromium().launch().use { browser ->
            browser.newPage().use { page ->
                val loginPage = LoginPage(page)
                loginPage.navigate("https://example.com/login")
                
                if (shouldSucceed) {
                    val dashboardPage = loginPage.login(username, password)
                    assertThat(page).hasURL("**/dashboard")
                } else {
                    loginPage.login(username, password)
                    assertThat(loginPage.getErrorMessage()).isNotNull()
                }
            }
        }
    }
}
```

### 4. 配置管理

```kotlin
// 配置类
data class TestConfig(
    val baseUrl: String,
    val browser: String = "chromium",
    val headless: Boolean = true,
    val slowMo: Int = 0,
    val timeout: Double = 30000.0,
    val viewportWidth: Int = 1920,
    val viewportHeight: Int = 1080
) {
    companion object {
        fun fromEnvironment(): TestConfig {
            return TestConfig(
                baseUrl = System.getenv("TEST_BASE_URL") ?: "https://example.com",
                browser = System.getenv("TEST_BROWSER") ?: "chromium",
                headless = System.getenv("TEST_HEADLESS")?.toBoolean() ?: true,
                slowMo = System.getenv("TEST_SLOW_MO")?.toInt() ?: 0
            )
        }
    }
}

// 使用配置
class ConfigurableTest {
    private val config = TestConfig.fromEnvironment()
    
    @Test
    fun `test with config`() {
        Playwright.create().use { playwright ->
            val browserType = when (config.browser) {
                "chromium" -> playwright.chromium()
                "firefox" -> playwright.firefox()
                "webkit" -> playwright.webkit()
                else -> playwright.chromium()
            }
            
            browserType.launch(
                BrowserType.LaunchOptions()
                    .setHeadless(config.headless)
                    .setSlowMo(config.slowMo.toDouble())
            ).use { browser ->
                browser.newContext(Browser.NewContextOptions()
                    .setViewportSize(config.viewportWidth, config.viewportHeight)
                ).use { context ->
                    val page = context.newPage()
                    page.navigate(config.baseUrl)
                    // 测试逻辑
                }
            }
        }
    }
}
```

### 5. 截图和日志记录

```kotlin
// 自动截图扩展
fun Page.screenshotOnFailure(testName: String) {
    try {
        screenshot(Page.ScreenshotOptions()
            .setPath(Paths.get("test-results/screenshots/$testName-failure.png"))
            .setFullPage(true)
        )
    } catch (e: Exception) {
        println("Failed to take screenshot: ${e.message}")
    }
}

// 测试中使用
@Test
fun `test with auto screenshot`() {
    Playwright.create().use { playwright ->
        playwright.chromium().launch().use { browser ->
            browser.newPage().use { page ->
                try {
                    page.navigate("https://example.com")
                    // 测试逻辑
                    assertThat(page.locator(".non-existent")).isVisible()
                } catch (e: AssertionError) {
                    page.screenshotOnFailure("test_with_auto_screenshot")
                    throw e
                }
            }
        }
    }
}
```

### 6. 测试隔离

```kotlin
// 每个测试使用独立的上下文
@TestInstance(TestInstance.Lifecycle.PER_METHOD)
class IsolatedTests {
    
    private lateinit var playwright: Playwright
    private lateinit var browser: Browser
    
    @BeforeEach
    fun setup() {
        playwright = Playwright.create()
        browser = playwright.chromium().launch()
    }
    
    @AfterEach
    fun teardown() {
        browser.close()
        playwright.close()
    }
    
    @Test
    fun `test 1`() {
        browser.newContext().use { context ->
            val page = context.newPage()
            // 测试逻辑，不会影响其他测试
        }
    }
    
    @Test
    fun `test 2`() {
        browser.newContext().use { context ->
            val page = context.newPage()
            // 测试逻辑，完全隔离
        }
    }
}
```

## 常见问题与解决方案

### 1. 元素定位失败

```kotlin
// 问题：元素定位超时
// 解决方案：增加超时时间或使用更稳定的选择器

// 增加超时
page.locator(".slow-element").waitFor(
    Locator.WaitForOptions().setTimeout(10000.0)
)

// 使用更稳定的选择器
// ❌ 避免
page.locator("div > div:nth-child(3) > span")

// ✅ 推荐
page.locator("[data-testid=submit-button]")
page.locator("role=button[name='Submit']")
```

### 2. Flaky Tests（不稳定测试）

```kotlin
// 问题：测试有时通过有时失败
// 解决方案：使用智能等待和稳定的选择器

// 等待网络空闲
page.waitForLoadState(LoadState.NETWORKIDLE)

// 等待特定请求完成
page.waitForResponse("**/api/data")

// 使用自动重试的断言
assertThat(page.locator(".dynamic-content")).hasText("Expected Text", 
    LocatorAssertions.HasTextOptions().setTimeout(10000.0)
)
```

### 3. 处理动态加载内容

```kotlin
// 问题：内容通过 AJAX 动态加载
// 解决方案：等待网络空闲或特定请求

// 方法1：等待网络空闲
page.navigate("https://example.com")
page.waitForLoadState(LoadState.NETWORKIDLE)

// 方法2：等待特定请求
page.navigate("https://example.com")
page.waitForResponse("**/api/users")

// 方法3：等待元素出现
page.navigate("https://example.com")
page.locator(".loaded-content").waitFor()
```

### 4. 文件上传失败

```kotlin
// 问题：文件上传不工作
// 解决方案：确保选择正确的文件输入元素

// ✅ 正确做法
page.locator("input[type='file']").setInputFiles(Paths.get("/path/to/file.txt"))

// 如果文件输入是隐藏的，先让它可见
page.evaluate("document.querySelector('input[type=file]').style.display = 'block'")
page.locator("input[type='file']").setInputFiles(Paths.get("/path/to/file.txt"))
```

### 5. 跨域问题

```kotlin
// 问题：跨域请求被阻止
// 解决方案：在浏览器启动参数中禁用 web 安全

val browser = playwright.chromium().launch(
    BrowserType.LaunchOptions()
        .setArgs(listOf("--disable-web-security"))
)
```

### 6. 并发爬虫

```kotlin
// 并发爬虫示例
class ConcurrentCrawler {
    fun crawl(urls: List<String>) {
        Playwright.create().use { playwright ->
            val browser = playwright.chromium().launch(
                BrowserType.LaunchOptions()
                    .setHeadless(true)
                    .setArgs(listOf("--disable-gpu"))
            )
            
            try {
                runBlocking { 
                    val results = urls.mapIndexed { index, url ->
                        async(Dispatchers.IO) { 
                            println("开始爬取: $url")
                            val result = crawlPage(browser, url)
                            println("完成爬取: $url")
                            result
                        }
                    }.awaitAll()
                    
                    println("爬取完成，共 ${results.size} 个页面")
                    results.forEachIndexed { index, result ->
                        println("${index + 1}. ${result.title} - ${result.url}")
                    }
                }
            } finally {
                browser.close()
            }
        }
    }
    
    private fun crawlPage(browser: Browser, url: String): PageResult {
        browser.newContext().use { context ->
            val page = context.newPage()
            
            try {
                page.navigate(url, 
                    Page.NavigateOptions()
                        .setTimeout(30000.0)
                )
                
                // 等待页面加载
                page.waitForLoadState(LoadState.NETWORKIDLE)
                
                // 提取标题
                val title = page.title()
                
                // 提取链接
                val links = page.locator("a[href]")
                val linkCount = links.count()
                
                // 提取文本内容
                val text = page.textContent("body")?.take(500) ?: ""
                
                return PageResult(url, title, linkCount, text)
            } catch (e: Exception) {
                println("爬取失败: $url - ${e.message}")
                return PageResult(url, "错误", 0, "")
            }
        }
    }
    
    data class PageResult(
        val url: String,
        val title: String,
        val linkCount: Int,
        val content: String
    )
}

// 带并发控制的爬虫
suspend fun crawlWithConcurrencyControl(urls: List<String>, maxConcurrency: Int = 5) {
    Playwright.create().use { playwright ->
        val browser = playwright.chromium().launch()
        
        try {
            val semaphore = kotlinx.coroutines.sync.Semaphore(maxConcurrency)
            
            val results = urls.map { url ->
                async { 
                    semaphore.acquire()
                    try {
                        crawlPageWithSemaphore(browser, url)
                    } finally {
                        semaphore.release()
                    }
                }
            }.awaitAll()
            
            println("爬取完成，结果: ${results.size} 个页面")
        } finally {
            browser.close()
        }
    }
}

suspend fun crawlPageWithSemaphore(browser: Browser, url: String): ConcurrentCrawler.PageResult {
    return withContext(Dispatchers.IO) {
        browser.newContext().use { context ->
            val page = context.newPage()
            
            try {
                // 添加随机延迟，模拟真实用户
                delay((1000..3000).random().toLong())
                
                page.navigate(url)
                page.waitForLoadState(LoadState.NETWORKIDLE)
                
                val title = page.title()
                val links = page.locator("a[href]").count()
                val content = page.textContent("body")?.take(500) ?: ""
                
                ConcurrentCrawler.PageResult(url, title, links, content)
            } catch (e: Exception) {
                println("爬取失败: $url - ${e.message}")
                ConcurrentCrawler.PageResult(url, "错误", 0, "")
            }
        }
    }
}
```

### 7. 并发爬虫注意事项

**1. 浏览器实例管理**
- 每个协程使用独立的 `BrowserContext`
- 不要在多个协程间共享 `Page` 实例
- 适当控制浏览器实例数量，避免资源耗尽
- 使用 `use` 函数确保资源及时释放

**2. 速率限制**
- 添加适当的延迟，避免被网站封禁
- 模拟真实用户行为（随机延迟、鼠标移动等）
- 遵守 `robots.txt` 规则
- 考虑使用代理 IP 轮换

**3. 错误处理**
- 每个爬取任务都要单独处理异常
- 实现重试机制（针对网络错误等临时问题）
- 记录失败的 URL 和错误原因
- 避免因为单个任务失败而影响整个爬取过程

**4. 内存管理**
- 及时关闭不再使用的 `Page` 和 `BrowserContext`
- 处理大页面时注意内存消耗
- 定期清理缓存和 cookie
- 考虑使用流式处理避免一次性加载过多数据

**5. 并发控制**
- 使用 `Semaphore` 控制并发数
- 避免创建过多协程导致系统资源耗尽
- 根据目标网站的承受能力调整并发数
- 监控系统资源使用情况

**6. 数据存储**
- 合理处理爬取的数据
- 考虑使用数据库或文件存储
- 避免内存溢出
- 实现数据去重机制

**7. 法律和道德考量**
- 遵守网站的使用条款
- 不要过度请求导致网站服务中断
- 尊重网站的 robots.txt 规则
- 仅爬取公开可访问的信息

## 协程安全性分析

### 协程安全概述

Playwright for Kotlin 本身不是协程安全的，这意味着：

- **Page 实例不是协程安全的**：不应在多个协程之间共享同一个 `Page` 实例
- **BrowserContext 不是协程安全的**：不应在多个协程之间共享同一个 `BrowserContext` 实例
- **Browser 实例是线程安全的**：可以在多个协程之间共享同一个 `Browser` 实例

### 协程并发警告

1. **不要在多个协程间共享 Page 或 BrowserContext**
   - 每个协程应创建自己的 `BrowserContext` 和 `Page`
   - 共享这些实例会导致不可预测的行为和竞态条件

2. **注意浏览器资源限制**
   - 每个 `Browser` 实例有资源限制（内存、CPU、连接数）
   - 过多的并发页面会导致浏览器崩溃或性能下降
   - 建议限制并发数，通常 5-10 个并发页面是合理的

3. **避免阻塞操作**
   - 在协程中执行 Playwright 操作时，避免使用阻塞操作
   - 如必须执行阻塞操作，应使用 `withContext(Dispatchers.IO)` 包装

4. **正确处理异常**
   - 每个协程中的异常应单独处理
   - 避免异常冒泡导致整个爬虫或测试流程中断

5. **资源释放**
   - 确保每个协程结束时释放所有资源（Page、BrowserContext）
   - 使用 `use` 函数或 `try-finally` 确保资源正确释放

### 协程安全最佳实践

1. **使用独立的 BrowserContext**
   - 每个协程使用独立的 `BrowserContext`
   - 这提供了完全的隔离，避免会话冲突

2. **控制并发数**
   - 使用 `Semaphore` 控制最大并发数
   - 根据系统资源和目标网站承受能力调整并发数

3. **合理使用协程调度器**
   - Playwright 操作本身是异步的，不需要额外的调度器
   - 对于 IO 密集型操作（如文件读写），使用 `Dispatchers.IO`

4. **实现超时机制**
   - 为每个页面操作设置合理的超时
   - 避免单个页面操作阻塞整个流程

5. **监控和错误处理**
   - 实现全局错误处理机制
   - 监控系统资源使用情况
   - 记录详细的日志以便调试

## 总结

Playwright for Kotlin 提供了强大而灵活的 Web 自动化测试能力：

1. **核心优势**：跨浏览器支持、自动等待机制、丰富的 API
2. **最佳实践**：使用 Locator 而非 ElementHandle、智能等待、Page Object Model
3. **避免陷阱**：及时关闭资源、避免固定等待时间、使用语义化选择器
4. **高级特性**：并行测试、移动端模拟、网络拦截、性能监控、并发爬虫
5. **协程安全**：理解并遵循协程安全最佳实践，避免共享非协程安全的实例

**核心要点**：
- 始终使用 `use` 或 `try-finally` 确保资源关闭
- 优先使用 Locator 而非 ElementHandle
- 使用智能等待而非固定等待时间
- 使用语义化选择器（data-testid、ARIA 角色）
- 实现适当的错误处理和断言
- 使用 Page Object Model 组织测试代码
- 保持测试的独立性和可重复性
- 并发爬虫时注意速率限制和资源管理
- 遵循协程安全最佳实践，避免共享非协程安全的实例

通过掌握 Playwright 的使用技巧，可以构建稳定、可维护的 Web 自动化测试套件和高效的网络爬虫。