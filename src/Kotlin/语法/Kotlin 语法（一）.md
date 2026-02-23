---
title: Kotlin 语法（一）：单元测试
date: 2026-02-15
---
[[toc]]
:::note 参考资料
- [官方文档]()
:::
***
### 快速开始
#### 单元测试
##### 补全依赖
打开`build.gradle.(kts)`文件并检查`testImplementation`依赖是否存在。这个依赖允许你使用`kotlin.test`和`JUnit`进行单元测试：
```kotlin
   dependencies {
       // Other dependencies.
       testImplementation(kotlin("test"))
   }
```

![](assets/Pasted%20image%2020260217220839.png)
*IDEA创建的项目默认就带有这个依赖*

然后将`test`任务加入到`build.gradle.(kts)`中：
```kotlin
   tasks.test {
       useJUnitPlatform()
   }
```

完整示例`build.gradle.(kts)`内容如下：
```kotlin
plugins {
    kotlin("jvm") version "2.1.21"
}

group = "org.example"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    testImplementation(kotlin("test"))
}

tasks.test {
    useJUnitPlatform()
}
```
##### 添加测试样例
在`Main.kt`中添加`Sample`类，`Sample`实例有一个`add`方法，实现两数相加：
```kotlin
class Sample() {  
    fun sum(a: Int, b: Int): Int {  
        return a + b  
    }  
}
```
然后用IDEA右键菜单快速生成**Test Stub**
![](assets/Pasted%20image%2020260217222950.png)

![](assets/Pasted%20image%2020260217223137.png)

:::note
也可以在`src/test/kotlin`下创建一个`*.kt`文件
![](assets/Pasted%20image%2020260218203351.png)
:::
##### 编写测试代码
编写测试代码：
1. 定义`testSum()`函数并使用`@Test`注解
2. 使用`assertEquals()`函数检查`sum`函数的返回值
```kotlin
import org.example.Sample  
import org.junit.jupiter.api.Assertions.*  
import org.junit.jupiter.api.Test  
  
class SampleTest {  
    private val sample = Sample()  
  
    @Test  
    fun testSum() {  
        val expected = 3  
        assertEquals(expected, sample.sum(1, 2))  
    }  
}
```

##### 运行测试
![](assets/Pasted%20image%2020260218205223.png)

:::note
也可以通过运行`./gradlew check`来执行所有指令
:::

![](assets/Pasted%20image%2020260218211406.png)

##### 神金Kotlin
![](assets/Pasted%20image%2020260218211045.png)
`Sample`的定义被导航到了`SampleTest.kt`里——我定义了谁，谁又定义了我？？？
![](assets/Pasted%20image%2020260218211209.png)
好家伙？？？

## 基本语法
### Hello World
#### 关键字
```kotlin
val 变量名称 : 变量类型 = 值
var 变量名称 : 变量类型 = 值
```
- `val`：声明**不可变变量**
	![](assets/Pasted%20image%2020260222232058.png)
- `var`：声明**可变变量**

- 变量类型标注可选；编译器会自动进行类型推导
#### 字符串模板
- `val str = "$变量"`
- `val str = "${表达式}"`

```kotlin
val customers = 10
println("There are $customers customers")
// There are 10 customers

println("There are ${customers + 1} customers")
// There are 11 customers
```

[详情请见](https://kotlinlang.org/docs/strings.html#string-templates)
:::note
- Kotlin会自动调用对象的`toString()`方法，所以字符串模板中可以任意嵌入非`String`类型变量
- 如果要调用对象的属性或方法，需要显式使用`{}`包裹：
```kotlin
val s = "abc"
println("$s.length is ${s.length}") 
// abc.length is 3
```
- 在单行字符串中要想保留`$`符号可以使用`\`，但在多行字符串中只能这样：
```kotlin
val price = """
${'$'}_9.99
"""
```

:::

##### 【实验性】多行模板字符串
```kotlin
val productName = "carrot"
val requestedData =
    $$$"""{
      "currency": "$",
      "enteredAmount": "42.45 $$",
      "$$serviceField": "none",
      "product": "$$$productName"
    }
    """

println(requestedData)
//{
//    "currency": "$",
//    "enteredAmount": "42.45 $$",
//    "$$serviceField": "none",
//    "product": "carrot"
//}
```
- 字符串前面的`$$$`用于指定引用符号为`$$$`，而`$`和`$$`都会被保留，不会用于变量引用
##### 字符串格式化
```kotlin
// Formats an integer, adding leading zeroes to reach a length of seven characters
val integerNumber = String.format("%07d", 31416)
println(integerNumber)
// 0031416

// Formats a floating-point number to display with a + sign and four decimal places
val floatNumber = String.format("%+.4f", 3.141592)
println(floatNumber)
// +3.1416

// Formats two strings to uppercase, each taking one placeholder
val helloString = String.format("%S %S", "hello", "world")
println(helloString)
// HELLO WORLD

// Formats a negative number to be enclosed in parentheses, then repeats the same number in a different format (without parentheses) using `argument_index$`.
val negativeNumberInParentheses = String.format("%(d means %1\$d", -31416)
println(negativeNumberInParentheses)
//(31416) means -31416
```

### 基本类型
| Category | Basic types                        | Example code                                                  |
| -------- | ---------------------------------- | ------------------------------------------------------------- |
| 整型       | `Byte`, `Short`, `Int`, `Long`     | `val year: Int = 2020`                                        |
| 无符号整型    | `UByte`, `UShort`, `UInt`, `ULong` | `val score: UInt = 100u`                                      |
| 浮点型      | `Float`, `Double`                  | `val currentTemp: Float = 24.5f`, `val price: Double = 19.99` |
| 布尔型      | `Boolean`                          | `val isEnabled: Boolean = true`                               |
| 字符       | `Char`                             | `val separator: Char = ','`                                   |
| 字符串      | `String`                           | `val message: String = "Hello, world!"`                       |

**基本类型**的属性和其他信息[详情请见](https://kotlinlang.org/docs/types-overview.html)

要想声明变量而不赋值，请提前指定类型：
```kotlin
// Variable declared without initialization
val d: Int
// Variable initialized
d = 3

// Variable explicitly typed and initialized
val e: String = "hello"

// Variables can be read because they have been initialized
println(d) // 3
println(e) // hello
```

如果声明变量而不赋值，那么会被视为语法错误：
![](assets/Pasted%20image%2020260222233843.png)
### 集合/Collection

|Collection type|Description|
|---|---|
|Lists|Ordered collections of items|
|Sets|Unique unordered collections of items|
|Maps|Sets of key-value pairs where keys are unique and map to only one value|
每一个集合类型都可为 **引用不可变** 与 **引用可变** 的（简单来说就是能否重新赋值）
#### 【初学可以跳过】须知
:::important 集合是否可变与`val`、`var`关键字的语义无关
可变集合（mutable collection）并不一定要赋值给 var。即使将可变集合赋值给 val，仍然可以对其进行写操作。

将可变集合赋值给 val 的好处在于，你可以保护指向该集合的*引用* 不被修改。随着代码量增加和逻辑复杂化，防止引用的意外篡改变得至关重要。为了代码的安全性和健壮性，请尽可能多地使用 val。如果你尝试对一个用 val 声明的集合进行重新赋值，将会产生编译错误
```kotlin
val numbers = mutableListOf("one", "two", "three", "four")
numbers.add("five")   // this is OK
println(numbers)
//numbers = mutableListOf("six", "seven")      // compilation error
```
:::
**引用不可变集合类型**是**协变的（covariant）**。这意味着，如果 Rectangle 类继承自 Shape，你可以在任何需要` List<Shape>` 的地方使用 `List<Rectangle>`。换句话说，集合类型具有与元素类型相同的子类型化关系（subtyping relationship）。Map 在其**值（Value）** 类型上是协变的，但在**键（Key）** 类型上不是。

相对地，**引用可变集合类型**不是协变的；否则，这将导致运行时错误。如果 `MutableList<Rectangle>` 是 `MutableList<Shape>` 的子类型，你就可以向其中插入 Shape 的其他继承者（例如 Circle），因此违反了其 Rectangle 的类型参数约束。

![](assets/Pasted%20image%2020260223123723.png)
*Kotlin集合类型继承关系*
#### 集合本集/Collection与引用可变集合/MutableCollection



#### 列表/List
- `listOf`：创建**不可变列表** `List`
- `mutableListOf`：创建**可变列表** `MutableList`

创建列表时Kotlin会自动推导元素类型，也可以使用`List<ItemT>`语法显式指定元素类型：
```kotlin
// Read only list
val readOnlyShapes = listOf("triangle", "square", "circle")
println(readOnlyShapes)
// [triangle, square, circle]

// Mutable list with explicit type declaration
val shapes: MutableList<String> = mutableListOf("triangle", "square", "circle")
println(shapes)
// [triangle, square, circle]
```

:::note 将`MutableList`转换为不可变的`List`
将`MutableList`赋值给一个`List`类型的变量
```kotlin
val shapes: MutableList<String> = mutableListOf("triangle", "square", "circle")
val shapesLocked: List<String> = shapes
```
:::

列表是有序的，所以可以用`[]`取出指定索引的元素
```kotlin
val readOnlyShapes = listOf("triangle", "square", "circle")
println("The first item in the list is: ${readOnlyShapes[0]}")
// The first item in the list is: triangle
```
特别地，可以用`.first()`和`.last()`方法取出列表头部和尾部的元素
```kotlin
val readOnlyShapes = listOf("triangle", "square", "circle")
println("The first item in the list is: ${readOnlyShapes.first()}")
// The first item in the list is: triangle
```

:::tip 
`.first()`和`.last()`被称作**扩展函数**，[详情请见](https://kotlinlang.org/docs/kotlin-tour-intermediate-extension-functions.html#extension-functions)
:::

使用`.count()`方法获取列表中的元素个数
```kotlin
val readOnlyShapes = listOf("triangle", "square", "circle")
println("This list has ${readOnlyShapes.count()} items")
// This list has 3 items
```

使用`in`操作符判断列表中是否存在某个元素
```kotlin
val readOnlyShapes = listOf("triangle", "square", "circle")
println("circle" in readOnlyShapes)
// true
```

使用`.add()`方法和`.remove()`方法分别向列表中添加元素和移除某个元素
```kotlin
val shapes: MutableList<String> = mutableListOf("triangle", "square", "circle")
// Add "pentagon" to the list
shapes.add("pentagon") 
println(shapes)  
// [triangle, square, circle, pentagon]

// Remove the first "pentagon" from the list
shapes.remove("pentagon") 
println(shapes)  
// [triangle, square, circle]
```
#### 集合/Set
对比列表是**有序**的且允许**元素重复**的类型，集合是**无序**的且**元素唯一**的类型

- `setOf(...)`: 创建**不可变集合** `Set`
- `mutableSetOf(...)`: 创建**可变集合** `MutableSet`
要想显式指定类型请使用`<T>`
```kotlin
// Read-only set
val readOnlyFruit = setOf("apple", "banana", "cherry", "cherry")
// Mutable set with explicit type declaration
val fruit: MutableSet<String> = mutableSetOf("apple", "banana", "cherry", "cherry")

println(readOnlyFruit)
// [apple, banana, cherry]
```

:::note 将`MutableSet`转换为不可变的`Set`
将`MutableSet`赋值给一个`Set`类型的变量
```kotlin
val fruit: MutableSet<String> = mutableSetOf("apple", "banana", "cherry", "cherry")
val fruitLocked: Set<String> = fruit
```
:::

- 由于集合是**无序**的，所以不能使用`[]`索引操作符
- 使用`.count()`方法获取集合中的元素个数
- 使用`in`操作符判断指定元素是否存在于集合中
- 使用`.add()`和`.remove()`增加或删除元素

#### 键值对/Map
Map将元素存储为键值对

:::tip
- Map的key必须是唯一的，这样Kotlin才能知道你想获取哪个值
- Map的value可以重复
:::

- 使用`mapOf`创建不可变的`Map`类型变量
- 使用`mutableMapOf`创建可变的`MutableMap`类型变量
还是一样的，编译器会自动推导类型；也可以使用`<keyType, valueType>`显式指定类型
```kotlin
// Read-only map
val readOnlyJuiceMenu = mapOf("apple" to 100, "kiwi" to 190, "orange" to 100)
println(readOnlyJuiceMenu)
// {apple=100, kiwi=190, orange=100}

// Mutable map with explicit type declaration
val juiceMenu: MutableMap<String, Int> = mutableMapOf("apple" to 100, "kiwi" to 190, "orange" to 100)
println(juiceMenu)
// {apple=100, kiwi=190, orange=100}
```

:::note 将`MutableMap`转换为不可变的`Map`
将`MutableMap`赋值给一个`Map`类型的变量
```kotlin
val juiceMenu: MutableMap<String, Int> = mutableMapOf("apple" to 100, "kiwi" to 190, "orange" to 100)
val juiceMenuLocked: Map<String, Int> = juiceMenu
```
:::

- 使用`[key: String]`访问Map中的元素
```kotlin
// Read-only map
val readOnlyJuiceMenu = mapOf("apple" to 100, "kiwi" to 190, "orange" to 100)
println("The value of apple juice is: ${readOnlyJuiceMenu["apple"]}")
// The value of apple juice is: 100
```
:::note
如果指定key在Map中不存在，会得到一个`null`：
```kotlin
// Read-only map
val readOnlyJuiceMenu = mapOf("apple" to 100, "kiwi" to 190, "orange" to 100)
println("The value of pineapple juice is: ${readOnlyJuiceMenu["pineapple"]}")
// The value of pineapple juice is: null
```
- **空类型安全**[详情请见](https://kotlinlang.org/docs/kotlin-tour-null-safety.html)
:::
- 也可以通过`[key] = value`来给可变Map添加一个键值对
- `.remove()`方法用于删除一个键值对
```kotlin
val juiceMenu: MutableMap<String, Int> = mutableMapOf("apple" to 100, "kiwi" to 190, "orange" to 100)
juiceMenu.remove("orange")    // Remove key "orange" from the map
println(juiceMenu)
// {apple=100, kiwi=190}
```
- `.count()`获取元素个数
```kotlin
// Read-only map
val readOnlyJuiceMenu = mapOf("apple" to 100, "kiwi" to 190, "orange" to 100)
println("This map has ${readOnlyJuiceMenu.count()} key-value pairs")
// This map has 3 key-value pairs
```
- 使用`.containKey()`判断指定key在Map中是否存在
```kotlin
val readOnlyJuiceMenu = mapOf("apple" to 100, "kiwi" to 190, "orange" to 100)
println(readOnlyJuiceMenu.containsKey("kiwi"))
// true
```
- 使用`.keys`和`.values`获取Map键列表和值列表
```kotlin
val readOnlyJuiceMenu = mapOf("apple" to 100, "kiwi" to 190, "orange" to 100)
println(readOnlyJuiceMenu.keys)
// [apple, kiwi, orange]
println(readOnlyJuiceMenu.values)
// [100, 190, 100]
```
:::tip
`.keys`和`.values`被称作对象上的**成员属性**，[详情请见](https://kotlinlang.org/docs/kotlin-tour-classes.html)
:::
- 使用`in`操作符判断给定key或**给定值**是否存在于Map中
```kotlin
val readOnlyJuiceMenu = mapOf("apple" to 100, "kiwi" to 190, "orange" to 100)
println("orange" in readOnlyJuiceMenu.keys)
// true

// Alternatively, you don't need to use the keys property
println("orange" in readOnlyJuiceMenu)
// true

println(200 in readOnlyJuiceMenu.values)
// false
```
#### 双向数组队列/ArrayDeque
`ArrayDeque<T>` 是双端队列（double-ended queue）的一种实现，它允许你在队列的头部或尾部添加或删除元素。因此，在 Kotlin 中，ArrayDeque 同时也充当了栈（Stack）和队列（Queue）这两种数据结构的角色。在底层实现上，ArrayDeque 是通过一个“可调大小的数组”实现的，该数组会在需要时自动调整其容量。

```kotlin
fun main() {
    val deque = ArrayDeque(listOf(1, 2, 3))

    deque.addFirst(0)
    deque.addLast(4)
    println(deque) // [0, 1, 2, 3, 4]

    println(deque.first()) // 0
    println(deque.last()) // 4

    deque.removeFirst()
    deque.removeLast()
    println(deque) // [1, 2, 3]
}
```

#### 数组/Arrays
数组不是`Collection`包的一员，[详情请见](https://kotlinlang.org/docs/arrays.html)

在某些方面，列表（List）与数组（Array）非常相似。然而，它们之间有一个重要的区别：数组的大小在初始化时就已经确定且无法更改；相应地，列表没有预定义的大小；列表的大小可以通过写操作（如添加、更新或删除元素）来改变

在 Kotlin 中，`MutableList` 的默认实现是 `ArrayList`，你可以将其理解为一种 *长度可变的数组* 

#### 详情请见
[详情请见](https://kotlinlang.org/docs/collections-overview.html)
### 控制流
#### 条件表达式/Conditional Expressions
#####  If
```kotlin
val d: Int
val check = true

if (check) {
    d = 1
} else {
    d = 2
}

println(d)
// 1
```

Kotlin中没有所谓的三目表达式 `condition ? then : else`，但当`if`代码块只有一行时，可以省略掉花括号`{}`：
```kotlin
val a = 1
val b = 2

println(if (a > b) a else b) // Returns a value: 2
```
##### When（多分支结构）
- 将`when`用于`statement`，此时没有返回值：
```kotlin
val obj = "Hello"

when (obj) {
    // Checks whether obj equals to "1"
    "1" -> println("One")
    // Checks whether obj equals to "Hello"
    "Hello" -> println("Greeting")
    // Default statement
    else -> println("Unknown")     
}
// Greeting
```
:::note
Kotlin会从上往下判断要走的分支，所以只有第一个分支会被触发
:::

- 将`when`用作表达式，此时有返回值：
```kotlin
val obj = "Hello"    

val result = when (obj) {
    // If obj equals "1", sets result to "one"
    "1" -> "One"
    // If obj equals "Hello", sets result to "Greeting"
    "Hello" -> "Greeting"
    // Sets result to "Unknown" if no previous condition is satisfied
    else -> "Unknown"
}
println(result)
// Greeting
```

上面的例子中`when`都在对`obj`进行判断，但`when`也可以用来纯粹地写多分支判断结构
```kotlin
fun main() {
    val trafficLightState = "Red" // This can be "Green", "Yellow", or "Red"

    val trafficAction = when {
        trafficLightState == "Green" -> "Go"
        trafficLightState == "Yellow" -> "Slow down"
        trafficLightState == "Red" -> "Stop"
        else -> "Malfunction"
    }

    println(trafficAction)
    // Stop
}
```

***
# 页面尾部