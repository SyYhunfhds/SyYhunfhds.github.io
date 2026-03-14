---
title: Kotlin 类、接口与继承
date: 2026-03-13
footer: Trae编辑
---


## 目录

1. [类（Class）](#类class)
2. [接口（Interface）](#接口interface)
3. [继承（Inheritance）](#继承inheritance)
4. [抽象类](#抽象类)
5. [数据类](#数据类)
6. [密封类](#密封类)
7. [嵌套类](#嵌套类)
8. [对象表达式与对象声明](#对象表达式与对象声明)
9. [最佳实践](#最佳实践)

## 类（Class）

### 基本定义

```kotlin
// 基本类定义
class Person {
    var name: String = ""
    var age: Int = 0
}

// 带主构造函数的类
class Person(val name: String, var age: Int)

// 带次构造函数的类
class Person(val name: String) {
    var age: Int = 0
    
    constructor(name: String, age: Int) : this(name) {
        this.age = age
    }
}
```

### 构造函数

| 类型 | 说明 | 示例 |
|------|------|------|
| **主构造函数** | 在类头中定义，可以包含初始化块 | `class Person(val name: String)` |
| **次构造函数** | 使用 `constructor` 关键字，必须委托给主构造函数 | `constructor(name: String, age: Int) : this(name)` |
| **初始化块** | 在主构造函数中执行的代码块 | `init { println("初始化") }` |

```kotlin
class Person(val name: String, var age: Int) {
    // 初始化块
    init {
        require(name.isNotBlank()) { "姓名不能为空" }
        require(age >= 0) { "年龄不能为负数" }
    }
    
    // 次构造函数
    constructor(name: String) : this(name, 0)
}
```

### 属性

```kotlin
class Person {
    // 可变属性
    var name: String = ""
    
    // 只读属性（val）
    val age: Int = 0
    
    // 自定义 getter
    val isAdult: Boolean
        get() = age >= 18
    
    // 自定义 setter
    var salary: Double = 0.0
        set(value) {
            field = maxOf(value, 0.0)
        }
    
    // 延迟初始化属性
    val lazyValue: String by lazy {
        println("只计算一次")
        "延迟计算的值"
    }
}
```

### 方法

```kotlin
class Calculator {
    // 普通方法
    fun add(a: Int, b: Int): Int = a + b
    
    // 带默认参数的方法
    fun greet(name: String, greeting: String = "Hello") = "$greeting, $name!"
    
    // 可变参数方法
    fun sum(vararg numbers: Int): Int {
        return numbers.sum()
    }
    
    // 中缀表示法
    infix fun Int.add(other: Int): Int = this + other
}

// 使用
val calc = Calculator()
println(calc.add(1, 2))
println(1 add 2) // 使用中缀表示法
```

### 可见性修饰符

| 修饰符 | 说明 | 适用范围 |
|---------|------|---------|
| `public` | 默认修饰符，随处可见 | 类、属性、方法 |
| `private` | 仅在类内部可见 | 类、属性、方法 |
| `protected` | 在类及其子类中可见 | 类、属性、方法 |
| `internal` | 在同一模块内可见 | 类、属性、方法 |

```kotlin
class Outer {
    private val privateProp = 1
    protected val protectedProp = 2
    internal val internalProp = 3
    val publicProp = 4 // 默认为 public
    
    private fun privateMethod() {}
    protected fun protectedMethod() {}
    internal fun internalMethod() {}
    fun publicMethod() {} // 默认为 public
}
```

## 接口（Interface）

### 基本定义

```kotlin
// 基本接口定义
interface Clickable {
    fun click()
}

// 带默认方法的接口
interface Clickable {
    fun click()
    
    // 默认方法实现
    fun doubleClick() {
        click()
        click()
    }
}

// 带属性的接口
interface Named {
    val name: String
    val description: String
        get() = "默认描述"
}
```

### 接口实现

```kotlin
// 实现单个接口
class Button : Clickable {
    override fun click() {
        println("按钮被点击")
    }
}

// 实现多个接口
class SmartButton : Clickable, Named {
    override fun click() {
        println("$name 被点击")
    }
    
    override val name: String = "智能按钮"
}
```

### 接口继承

```kotlin
interface Clickable {
    fun click()
}

interface Focusable {
    fun focus()
}

// 接口继承
interface ClickableAndFocusable : Clickable, Focusable {
    fun activate() {
        click()
        focus()
    }
}

// 实现继承的接口
class AdvancedButton : ClickableAndFocusable {
    override fun click() = println("点击")
    override fun focus() = println("聚焦")
    override fun activate() = println("激活")
}
```

### 接口中的属性

```kotlin
interface Configurable {
    // 抽象属性
    val config: Map<String, Any>
    
    // 带默认实现的属性
    val isEnabled: Boolean
        get() = config["enabled"] as? Boolean ?: false
    
    // 带自定义访问器的属性
    val timeout: Long
        get() = config["timeout"] as? Long ?: 30000
        set(value) {
            config["timeout"] = value
        }
}
```

### 接口中的函数式属性

```kotlin
interface Comparator<T> {
    fun compare(a: T, b: T): Int
    
    // 函数式属性
    companion object {
        fun <T> naturalOrder(): Comparator<T> = Comparator { a, b ->
            @Suppress("UNCHECKED_CAST")
            (a as Comparable<T>).compareTo(b)
        }
    }
}
```

## 继承（Inheritance）

### 基本继承

```kotlin
// 父类（使用 open 关键字）
open class Animal(val name: String) {
    open fun makeSound() {
        println("$name 发出声音")
    }
}

// 子类
class Dog(name: String) : Animal(name) {
    override fun makeSound() {
        println("$name 汪汪叫")
    }
}

// 使用
val dog = Dog("旺财")
dog.makeSound() // 输出: 旺财 汪汪叫
```

### 方法重写

```kotlin
open class Parent {
    open fun method() = println("父类方法")
}

class Child : Parent() {
    override fun method() = println("子类方法")
    
    // 调用父类方法
    fun callParentMethod() {
        super.method()
    }
}
```

### 属性重写

```kotlin
open class Parent {
    open val value: String = "父类值"
}

class Child : Parent() {
    override val value: String = "子类值"
    
    // 访问父类属性
    fun printParentValue() {
        println(super.value)
    }
}
```

### 继承与构造函数

```kotlin
open class Parent(val name: String) {
    init {
        println("父类初始化: $name")
    }
}

class Child(name: String, val age: Int) : Parent(name) {
    init {
        println("子类初始化: $name, $age")
    }
}

// 使用
val child = Child("Alice", 25)
// 输出:
// 父类初始化: Alice
// 子类初始化: Alice, 25
```

### 类型检查与转换

```kotlin
open class Animal
class Dog : Animal()

fun checkType(animal: Animal) {
    // 类型检查
    if (animal is Dog) {
        println("这是一只狗")
        // 智能转换
        val dog = animal as Dog
        println(dog)
    }
    
    // 安全转换
    val dog = animal as? Dog
    dog?.let { println(it) }
}
```

### Any 类型

```kotlin
// Any 是 Kotlin 中所有类的超类
fun printAny(value: Any) {
    when (value) {
        is String -> println("字符串: $value")
        is Int -> println("整数: $value")
        is List<*> -> println("列表: ${value.size} 个元素")
        else -> println("其他类型")
    }
}

// 使用
printAny("Hello")
printAny(42)
printAny(listOf(1, 2, 3))
```

## 抽象类

### 基本定义

```kotlin
// 抽象类
abstract class Shape {
    abstract fun area(): Double
    abstract fun perimeter(): Double
    
    fun printInfo() {
        println("面积: ${area()}, 周长: ${perimeter()}")
    }
}

// 具体子类
class Circle(val radius: Double) : Shape() {
    override fun area(): Double = Math.PI * radius * radius
    override fun perimeter(): Double = 2 * Math.PI * radius
}

class Rectangle(val width: Double, val height: Double) : Shape() {
    override fun area(): Double = width * height
    override fun perimeter(): Double = 2 * (width + height)
}
```

### 抽象属性

```kotlin
abstract class Animal {
    abstract val species: String
    abstract val sound: String
    
    fun makeSound() {
        println("$species: $sound")
    }
}

class Cat : Animal() {
    override val species: String = "猫"
    override val sound: String = "喵喵"
}

class Dog : Animal() {
    override val species: String = "狗"
    override val sound: String = "汪汪"
}
```

### 抽象类与接口对比

| 特性 | 抽象类 | 接口 |
|------|---------|------|
| 构造函数 | 可以有 | 不能有 |
| 状态存储 | 可以存储状态 | 不能存储状态（Kotlin 1.2+ 可以） |
| 方法实现 | 可以有部分实现 | 可以有默认实现 |
| 继承 | 单继承 | 多继承 |
| 使用场景 | 需要共享代码和状态 | 定义行为契约 |

## 数据类

### 基本定义

```kotlin
// 数据类定义
data class User(val id: Int, val name: String, val email: String)

// 自动生成的方法
val user = User(1, "Alice", "alice@example.com")

// copy() 方法
val updatedUser = user.copy(name = "Bob")

// componentN() 方法
val (id, name, email) = user

// equals() 和 hashCode()
val user2 = User(1, "Alice", "alice@example.com")
println(user == user2) // true

// toString()
println(user) // User(id=1, name=Alice, email=alice@example.com)
```

### 数据类要求

| 要求 | 说明 |
|------|------|
| 主构造函数至少有一个参数 | 必须定义属性 |
| 所有主构造函数参数必须是 val 或 var | 确保不可变性 |
| 不能是 abstract、open、sealed 或 inner | 保持简单性 |
| 可以实现接口 | 支持多态 |
| 可以继承其他类 | 但不能继承数据类 |

### 数据类的高级用法

```kotlin
// 带默认值的数据类
data class User(
    val id: Int,
    val name: String = "Unknown",
    val email: String = ""
)

// 带次构造函数的数据类
data class User(val id: Int, val name: String) {
    constructor(id: Int) : this(id, "Unknown")
}

// 数据类解构
val user = User(1, "Alice", "alice@example.com")
val (id, name, _) = user
println("ID: $id, Name: $name")
```

## 密封类

### 基本定义

```kotlin
// 密封类
sealed class Result

data class Success(val data: String) : Result()
data class Error(val message: String) : Result()
object Loading : Result()

// when 表达式完整覆盖
fun handleResult(result: Result): String {
    return when (result) {
        is Success -> "成功: ${result.data}"
        is Error -> "错误: ${result.message}"
        is Loading -> "加载中..."
    }
}
```

### 密封类的特性

| 特性 | 说明 |
|------|------|
| 限制子类 | 所有子类必须在同一文件中定义 |
| 完整覆盖 | when 表达式可以省略 else 分支 |
| 类型安全 | 编译器检查所有可能的情况 |

### 密封类继承

```kotlin
sealed class UIElement

class Button(val text: String) : UIElement()
class TextField(val placeholder: String) : UIElement()
class Label(val text: String) : UIElement()

// 完整的类型检查
fun render(element: UIElement): String {
    return when (element) {
        is Button -> "<button>${element.text}</button>"
        is TextField -> "<input placeholder='${element.placeholder}'>"
        is Label -> "<label>${element.text}</label>"
    }
}
```

## 嵌套类

### 静态嵌套类

```kotlin
class Outer {
    private val outerValue = 1
    
    // 静态嵌套类（不持有外部类引用）
    class Nested {
        fun accessOuter() {
            // 无法直接访问外部类的私有成员
            println("无法访问 outerValue")
        }
    }
}

// 使用
val nested = Outer.Nested()
nested.accessOuter()
```

### 内部类

```kotlin
class Outer {
    private val outerValue = 1
    
    // 内部类（持有外部类引用）
    inner class Inner {
        fun accessOuter() {
            // 可以访问外部类的私有成员
            println("访问外部类: $outerValue")
        }
    }
}

// 使用
val outer = Outer()
val inner = outer.Inner()
inner.accessOuter()
```

### 匿名内部类

```kotlin
class Container {
    private val items = mutableListOf<String>()
    
    fun process(action: (String) -> Unit) {
        items.forEach { action(it) }
    }
}

// 使用
val container = Container()
container.process { item ->
    // 匿名内部类
    println("处理: $item")
}
```

## 对象表达式与对象声明

### 对象表达式

```kotlin
// 对象表达式（匿名对象）
val listener = object : MouseAdapter() {
    override fun mouseClicked(e: MouseEvent) {
        println("鼠标点击: ${e.x}, ${e.y}")
    }
}

// 对象表达式可以继承多个接口
val adapter = object : Clickable, Focusable {
    override fun click() = println("点击")
    override fun focus() = println("聚焦")
}
```

### 对象声明

```kotlin
// 对象声明（单例模式）
object Database {
    private val connection = "数据库连接"
    
    fun connect() = println("连接: $connection")
    fun disconnect() = println("断开连接")
}

// 使用
Database.connect()
Database.disconnect()

// 对象声明可以实现接口
object Singleton : Clickable {
    override fun click() = println("单例点击")
}
```

### 伴生对象

```kotlin
class MyClass {
    companion object {
        private var count = 0
        
        fun increment() {
            count++
        }
        
        fun getCount(): Int = count
    }
}

// 使用
MyClass.increment()
println(MyClass.getCount())
```

### 伴生对象实现接口

```kotlin
interface Factory<T> {
    fun create(): T
}

class User {
    companion object : Factory<User> {
        override fun create(): User = User(0, "Guest", "")
    }
}

// 使用
val user = User.create()
```

## 最佳实践

### 类设计原则

1. **优先使用数据类**：对于主要存储数据的类，使用 data class
2. **合理使用密封类**：对于有限的类型层次结构，使用 sealed class
3. **谨慎使用继承**：优先使用组合而非继承
4. **明确可见性**：合理使用 private、protected、internal、public
5. **避免过度设计**：保持类简单，遵循 YAGNI 原则

### 接口设计原则

1. **接口隔离**：保持接口小而专注
2. **默认方法谨慎**：避免在接口中添加过多默认实现
3. **函数式接口**：对于单个方法的接口，考虑使用函数类型
4. **命名规范**：使用描述性名称，如 `-able`、`-ible` 后缀

### 继承设计原则

1. **Liskov 替换原则**：子类应该可以替换父类而不影响程序正确性
2. **开放继承谨慎**：使用 open 关键字明确标记可继承的类和方法
3. **避免深层继承**：继承层次不宜过深，通常不超过 3 层
4. **组合优于继承**：优先使用组合来复用代码

### 代码示例

```kotlin
// 好的设计：使用接口和组合
interface Clickable {
    fun click()
}

class Button(private val handler: ClickHandler) : Clickable {
    override fun click() {
        handler.handleClick()
    }
}

class ClickHandler {
    fun handleClick() {
        println("处理点击")
    }
}

// 使用
val handler = ClickHandler()
val button = Button(handler)
button.click()

// 不好的设计：过度继承
open class BaseButton
open class StyledButton : BaseButton()
open class AnimatedButton : StyledButton()
class MyButton : AnimatedButton() // 继承层次过深
```

## 总结

Kotlin 的类、接口与继承系统提供了强大的面向对象编程能力：

1. **类系统**：支持主构造函数、次构造函数、初始化块、属性和方法
2. **接口系统**：支持默认方法、属性继承、函数式接口
3. **继承机制**：使用 open 关键字控制继承，支持方法重写和属性重写
4. **特殊类**：数据类、密封类、对象声明等提供便捷的编程模式
5. **嵌套类**：支持静态嵌套类和内部类
6. **最佳实践**：遵循 SOLID 原则，优先使用组合而非继承

通过合理使用这些特性，可以编写出清晰、可维护、可扩展的 Kotlin 代码。