---
title: JUnit 5 与 Kotlin.test API 用法指南
date:
footer: Trae编辑
---


## 目录

1. [概述](#概述)
2. [JUnit 5 API](#junit-5-api)
3. [Kotlin.test API](#kotlin-test-api)
4. [功能对比](#功能对比)
5. [混合使用](#混合使用)
6. [最佳实践](#最佳实践)
7. [示例代码](#示例代码)

---

## 概述

在 Kotlin 项目中，测试框架主要有两种选择：

- **JUnit 5**：Java 生态系统的标准测试框架，功能丰富，生态成熟
- **Kotlin.test**：Kotlin 标准库提供的测试工具，与 Kotlin 语言特性紧密集成

本文档详细介绍这两种框架的 API 用法和功能特点。

---

## JUnit 5 API

### 核心注解

| 注解 | 描述 | 适用范围 |
|------|------|----------|
| `@Test` | 标记测试方法 | 方法 |
| `@BeforeAll` | 所有测试方法执行前执行，必须是静态方法 | 方法 |
| `@AfterAll` | 所有测试方法执行后执行，必须是静态方法 | 方法 |
| `@BeforeEach` | 每个测试方法执行前执行 | 方法 |
| `@AfterEach` | 每个测试方法执行后执行 | 方法 |
| `@Disabled` | 禁用测试方法 | 方法 |
| `@DisplayName` | 设置测试方法的显示名称 | 方法/类 |
| `@Nested` | 标记嵌套测试类 | 类 |
| `@Tag` | 为测试添加标签 | 方法/类 |
| `@ParameterizedTest` | 参数化测试 | 方法 |
| `@RepeatedTest` | 重复执行测试 | 方法 |

### 断言方法

```kotlin
import org.junit.jupiter.api.Assertions.*

@Test
fun testAssertions() {
    // 基本断言
    assertEquals(expected, actual)
    assertEquals(expected, actual, "错误消息")
    assertNotEquals(unexpected, actual)
    
    // 布尔断言
    assertTrue(condition)
    assertTrue(condition, "错误消息")
    assertFalse(condition)
    
    // 空值断言
    assertNull(value)
    assertNotNull(value)
    
    // 异常断言
    assertThrows<Exception> { /* 代码 */ }
    
    // 超时断言
    assertTimeout(Duration.ofSeconds(1)) { /* 代码 */ }
    
    // 分组断言
    assertAll(
        { assertEquals(1, 1) },
        { assertEquals(2, 2) }
    )
    
    // 失败断言
    fail("测试失败")
}
```

### 测试生命周期

```kotlin
class LifecycleTest {
    companion object {
        @BeforeAll
        @JvmStatic
        fun setupAll() {
            // 所有测试前执行
        }
        
        @AfterAll
        @JvmStatic
        fun tearDownAll() {
            // 所有测试后执行
        }
    }
    
    @BeforeEach
    fun setup() {
        // 每个测试前执行
    }
    
    @AfterEach
    fun tearDown() {
        // 每个测试后执行
    }
    
    @Test
    fun test1() {}
    
    @Test
    fun test2() {}
}
```

### 参数化测试

```kotlin
@ParameterizedTest
@ValueSource(ints = [1, 2, 3, 4, 5])
fun testWithValueSource(value: Int) {
    assertTrue(value > 0)
}

@ParameterizedTest
@CsvSource(
    "1, 2, 3",
    "4, 5, 9"
)
fun testWithCsvSource(a: Int, b: Int, expected: Int) {
    assertEquals(expected, a + b)
}
```

### 嵌套测试

```kotlin
class NestedTest {
    @Test
    fun outerTest() {}
    
    @Nested
    inner class InnerTests {
        @Test
        fun innerTest() {}
    }
}
```

### 重复测试

```kotlin
@RepeatedTest(5)
fun repeatedTest() {
    // 执行 5 次
}

@RepeatedTest(3, name = RepeatedTest.LONG_DISPLAY_NAME)
fun repeatedTestWithName() {
    // 执行 3 次，显示详细名称
}
```

---

## Kotlin.test API

### 核心注解

| 注解 | 描述 | 适用范围 |
|------|------|----------|
| `@Test` | 标记测试方法 | 方法 |
| `@BeforeClass` | 所有测试方法执行前执行 | 方法 |
| `@AfterClass` | 所有测试方法执行后执行 | 方法 |
| `@Before` | 每个测试方法执行前执行 | 方法 |
| `@After` | 每个测试方法执行后执行 | 方法 |
| `@Ignore` | 禁用测试方法 | 方法 |

### 断言函数

```kotlin
import kotlin.test.*

@Test
fun testAssertions() {
    // 基本断言
    assertEquals(expected, actual)
    assertEquals(expected, actual, "错误消息")
    assertNotEquals(unexpected, actual)
    
    // 布尔断言
    assertTrue(condition)
    assertTrue(condition, "错误消息")
    assertFalse(condition)
    
    // 空值断言
    assertNull(value)
    assertNotNull(value)
    
    // 同一引用断言
    assertSame(expected, actual)
    assertNotSame(unexpected, actual)
    
    // 异常断言
    assertFails { /* 代码 */ }
    assertFailsWith<Exception> { /* 代码 */ }
    
    // 超时断言
    assertTimeout(1000) { /* 代码 */ }
    
    // 失败断言
    fail("测试失败")
}
```

### 测试生命周期

```kotlin
class LifecycleTest {
    companion object {
        @BeforeClass
        fun setupAll() {
            // 所有测试前执行
        }
        
        @AfterClass
        fun tearDownAll() {
            // 所有测试后执行
        }
    }
    
    @Before
    fun setup() {
        // 每个测试前执行
    }
    
    @After
    fun tearDown() {
        // 每个测试后执行
    }
    
    @Test
    fun test1() {}
    
    @Test
    fun test2() {}
}
```

### 扩展函数

Kotlin.test 提供了丰富的扩展函数：

```kotlin
// 集合断言
@Test
fun testCollections() {
    val list = listOf(1, 2, 3)
    list shouldContain 2
    list shouldNotContain 4
}

// 字符串断言
@Test
fun testStrings() {
    val str = "Hello"
    str shouldStartWith "He"
    str shouldEndWith "lo"
    str shouldContain "ell"
}

// 数值断言
@Test
fun testNumbers() {
    val number = 5
    number shouldBeGreaterThan 3
    number shouldBeLessThan 10
    number shouldBeBetween 1 and 10
}
```

### 超时测试

```kotlin
@Test
fun testWithTimeout() {
    assertTimeout(1000) {  // 1000 毫秒
        // 执行代码
    }
    
    assertTimeout(500) {
        // 执行代码
    }
}
```

---

## 功能对比

| 功能 | JUnit 5 | Kotlin.test | 优势 |
|------|---------|-------------|------|
| 基本断言 | ✅ | ✅ | 两者都支持 |
| 异常断言 | ✅ | ✅ | 两者都支持 |
| 超时断言 | ✅ | ✅ | 两者都支持 |
| 分组断言 | ✅ | ❌ | JUnit 5 更强大 |
| 参数化测试 | ✅ | ❌ | JUnit 5 更灵活 |
| 重复测试 | ✅ | ❌ | JUnit 5 支持 |
| 嵌套测试 | ✅ | ❌ | JUnit 5 支持 |
| 标签支持 | ✅ | ❌ | JUnit 5 支持 |
| 显示名称 | ✅ | ❌ | JUnit 5 支持 |
| Kotlin 扩展 | ❌ | ✅ | Kotlin.test 更 Kotlin 化 |
| 简洁语法 | ❌ | ✅ | Kotlin.test 更简洁 |
| 标准库集成 | ❌ | ✅ | Kotlin.test 是标准库的一部分 |
| 生态系统 | ✅ | ❌ | JUnit 5 生态更成熟 |
| 第三方集成 | ✅ | ❌ | JUnit 5 集成更多 |

## 功能详细对比

### 1. 断言方式

**JUnit 5**：
```kotlin
assertEquals(expected, actual)
assertTrue(condition)
```

**Kotlin.test**：
```kotlin
assertEquals(expected, actual)
assertTrue(condition)
// 扩展语法
actual shouldBe expected
condition shouldBe true
```

### 2. 异常处理

**JUnit 5**：
```kotlin
val exception = assertThrows<IllegalArgumentException> {
    throw IllegalArgumentException("Error")
}
assertEquals("Error", exception.message)
```

**Kotlin.test**：
```kotlin
val exception = assertFailsWith<IllegalArgumentException> {
    throw IllegalArgumentException("Error")
}
assertEquals("Error", exception.message)
```

### 3. 生命周期管理

**JUnit 5**：
- `@BeforeAll` (静态方法)
- `@AfterAll` (静态方法)
- `@BeforeEach`
- `@AfterEach`

**Kotlin.test**：
- `@BeforeClass`
- `@AfterClass`
- `@Before`
- `@After`

### 4. 参数化测试

**JUnit 5**：
```kotlin
@ParameterizedTest
@ValueSource(ints = [1, 2, 3])
fun testWithValues(value: Int) {
    assertTrue(value > 0)
}
```

**Kotlin.test**：
需要手动实现参数化测试

---

## 混合使用

在 Kotlin 项目中，可以混合使用 JUnit 5 和 Kotlin.test：

```kotlin
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*
import kotlin.test.*

class MixedTest {
    @Test
    fun testWithJUnit5() {
        assertEquals(2, 1 + 1)
        assertThrows<IllegalArgumentException> {
            throw IllegalArgumentException()
        }
    }
    
    @Test
    fun testWithKotlinTest() {
        assertEquals(2, 1 + 1)
        assertFailsWith<IllegalArgumentException> {
            throw IllegalArgumentException()
        }
        
        // 使用 Kotlin 扩展
        2 shouldBe 2
        true shouldBe true
    }
}
```

---

## 最佳实践

### 何时使用 JUnit 5

1. **需要高级特性**：参数化测试、重复测试、嵌套测试等
2. **团队协作**：团队中有 Java 开发者
3. **生态集成**：需要与第三方工具（如 Mockito）集成
4. **企业项目**：需要标准化的测试框架

### 何时使用 Kotlin.test

1. **纯 Kotlin 项目**：充分利用 Kotlin 语言特性
2. **简洁语法**：喜欢 DSL 风格的测试代码
3. **标准库依赖**：不想引入额外依赖
4. **快速原型**：小型项目或个人项目

### 混合使用的最佳实践

1. **基础断言**：使用 Kotlin.test 的简洁语法
2. **高级特性**：使用 JUnit 5 的参数化测试等功能
3. **保持一致性**：同一项目中选择一种主要风格
4. **文档清晰**：明确说明使用的测试框架

---

## 示例代码

### JUnit 5 示例

```kotlin
import org.junit.jupiter.api.*
import java.time.Duration

class JUnit5ExampleTest {
    companion object {
        @BeforeAll
        @JvmStatic
        fun setupAll() {
            println("Before all tests")
        }
        
        @AfterAll
        @JvmStatic
        fun tearDownAll() {
            println("After all tests")
        }
    }
    
    @BeforeEach
    fun setup() {
        println("Before each test")
    }
    
    @AfterEach
    fun tearDown() {
        println("After each test")
    }
    
    @Test
    @DisplayName("测试加法")
    fun testAddition() {
        val result = 1 + 1
        assertEquals(2, result)
    }
    
    @Test
    @Disabled("暂时禁用")
    fun testDisabled() {
        fail("这个测试被禁用了")
    }
    
    @Test
    fun testException() {
        val exception = assertThrows<IllegalArgumentException> {
            throw IllegalArgumentException("测试异常")
        }
        assertEquals("测试异常", exception.message)
    }
    
    @Test
    fun testTimeout() {
        assertTimeout(Duration.ofSeconds(1)) {
            Thread.sleep(500)
        }
    }
    
    @ParameterizedTest
    @ValueSource(ints = [1, 2, 3, 4, 5])
    fun testParameterized(value: Int) {
        assertTrue(value > 0)
    }
    
    @RepeatedTest(3)
    fun testRepeated() {
        println("重复测试")
    }
}
```

### Kotlin.test 示例

```kotlin
import kotlin.test.*

class KotlinTestExampleTest {
    companion object {
        @BeforeClass
        fun setupAll() {
            println("Before all tests")
        }
        
        @AfterClass
        fun tearDownAll() {
            println("After all tests")
        }
    }
    
    @Before
    fun setup() {
        println("Before each test")
    }
    
    @After
    fun tearDown() {
        println("After each test")
    }
    
    @Test
    fun testAddition() {
        val result = 1 + 1
        assertEquals(2, result)
        result shouldBe 2
    }
    
    @Test
    @Ignore("暂时禁用")
    fun testDisabled() {
        fail("这个测试被禁用了")
    }
    
    @Test
    fun testException() {
        val exception = assertFailsWith<IllegalArgumentException> {
            throw IllegalArgumentException("测试异常")
        }
        assertEquals("测试异常", exception.message)
    }
    
    @Test
    fun testTimeout() {
        assertTimeout(1000) {
            Thread.sleep(500)
        }
    }
    
    @Test
    fun testCollections() {
        val list = listOf(1, 2, 3, 4, 5)
        list shouldContain 3
        list shouldNotContain 6
    }
    
    @Test
    fun testStrings() {
        val str = "Hello Kotlin"
        str shouldStartWith "Hello"
        str shouldEndWith "Kotlin"
        str shouldContain "Kotlin"
    }
}
```

### 混合使用示例

```kotlin
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*
import kotlin.test.*

class MixedTestExample {
    @Test
    fun testWithJUnit5Features() {
        // 使用 JUnit 5 的分组断言
        assertAll(
            { assertEquals(1, 1) },
            { assertEquals(2, 2) },
            { assertEquals(3, 3) }
        )
    }
    
    @Test
    fun testWithKotlinSyntax() {
        // 使用 Kotlin.test 的扩展语法
        val result = 42
        result shouldBe 42
        result shouldBeGreaterThan 40
        result shouldBeLessThan 50
    }
    
    @Test
    fun testExceptionHandling() {
        // JUnit 5 方式
        assertThrows<IllegalArgumentException> {
            throw IllegalArgumentException("JUnit 5")
        }
        
        // Kotlin.test 方式
        assertFailsWith<IllegalArgumentException> {
            throw IllegalArgumentException("Kotlin.test")
        }
    }
}
```

---

## 总结

| 框架 | 适用场景 | 优势 | 劣势 |
|------|----------|------|------|
| JUnit 5 | 复杂项目、企业级应用 | 功能丰富、生态成熟、高级特性多 | 语法较冗长 |
| Kotlin.test | 纯 Kotlin 项目、小型项目 | 语法简洁、Kotlin 集成、标准库 | 功能相对有限 |

**选择建议**：
- 小型纯 Kotlin 项目：使用 Kotlin.test
- 大型复杂项目：使用 JUnit 5
- 混合项目：根据具体需求选择，可混合使用

无论选择哪种框架，重要的是保持测试代码的清晰、可读性和可维护性。