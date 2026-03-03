---
title: Kotlin与Spring Boot（一）
date: 2026-02-27
---
[[toc]]
:::note 参考文档
- https://kotlinlang.org/docs/jvm-get-started-spring-boot.html
:::
***
## 环境配置
#### 参数配置
**官方教程配置**

| 参数名称     | 参数配置                           |
| -------- | ------------------------------ |
| **项目名称** | demo                           |
| **项目语言** | Kotlin                         |
| **打包方式** | Gradle - Kotlin                |
| **JDK**  | Java JDK (Amazon Corretto v23) |
| **Java** | 17+                            |

| 依赖名称    | 依赖选项             |
| ------- | ---------------- |
| **Web** | Spring Web       |
| **SQL** | Spring Data JDBC |
| **SQL** | H2 Database      |


**本人配置**
![](assets/Pasted%20image%2020260301125249.png)
*习惯yaml了，所以配置文件也用`yaml`的*

:::tip H2 Database
_H2数据库是轻量级、高性能的Java嵌入式数据库_，具有如下优点：
- **零配置（Zero Config）**：Spring Boot 只要发现路径下有 H2 的包，就会自动帮你配置好 `DataSource`。你甚至不需要在 `application.properties` 里写连接字符串。
    
- **兼容性强**：它支持 **"MySQL Mode"** 或 **"PostgreSQL Mode"**。这意味着你在练习时写的是 H2，但未来换成生产环境的 MySQL 时，代码几乎不用改。
    
- **可视化**：它自带一个网页版的控制台。你只需要访问 `localhost:8080/h2-console`，就能直接查表，体验和 Navicat 差不多。
:::

#### `build.gradle.kts`构建脚本内容简述
**插件板块 (The `plugins` block)**
插件就像是给编译器安装的“增强模组”。
- **`kotlin("jvm")`**： 这是基础。它告诉 Gradle 这是一个 Kotlin 项目，并指定了编译器版本，确保你的代码能被编译成运行在 Java 虚拟机（JVM）上的字节码。
- **`kotlin("plugin.spring")` (All-open 插件)**： **这是最关键的一环。** 在 Kotlin 中，类默认是 `final` 的（不可被继承）。但 Spring 的很多核心功能（如 `@Transactional` 或 AOP）需要通过创建子类代理来实现。 这个插件会自动为标注了 Spring 注解的类添加 `open` 修饰符，让你不需要手动在每个类前面写 `open`。
```kotlin
plugins {  
    kotlin("jvm") version "2.2.21"  
    kotlin("plugin.spring") version "2.2.21"  
    id("org.springframework.boot") version "4.0.3"  
    id("io.spring.dependency-management") version "1.1.7"  
}  
  
group = "org.example"  
version = "0.0.1-SNAPSHOT"  
description = "spring-demo"  
  
java {  
    toolchain {  
        languageVersion = JavaLanguageVersion.of(17)  
    }  
}  
  
repositories {  
    mavenCentral()  
}  
  
dependencies {  
    implementation("org.springframework.boot:spring-boot-h2console")  
    implementation("org.springframework.boot:spring-boot-starter-data-jdbc")  
    implementation("org.springframework.boot:spring-boot-starter-webmvc")  
    implementation("org.jetbrains.kotlin:kotlin-reflect")  
    implementation("tools.jackson.module:jackson-module-kotlin")  
    runtimeOnly("com.h2database:h2")  
    testImplementation("org.springframework.boot:spring-boot-starter-data-jdbc-test")  
    testImplementation("org.springframework.boot:spring-boot-starter-webmvc-test")  
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit5")  
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")  
}  
  
kotlin {  
    compilerOptions {  
        freeCompilerArgs.addAll("-Xjsr305=strict", "-Xannotation-default-target=param-property")  
    }  
}  
  
tasks.withType<Test> {  
    useJUnitPlatform()  
}
```
**依赖板块 (The `dependencies` block)**
这里列出了你的项目所依赖的外部库。
- **`jackson-module-kotlin`**： Jackson 是 Spring 默认的 JSON 解析器。由于 Kotlin 的数据类（Data Classes）和构造函数与 Java 不同，这个模块能让 Jackson 完美识别 Kotlin 的非空类型和默认参数。
- **`kotlin-reflect`**： 反射允许程序在运行时检查自己的结构。Spring 框架极度依赖反射来发现 `@Service`、`@RestController` 等组件。这个库为 Kotlin 的高级特性（如可空性属性和扩展函数）提供了完整的反射支持。

**配置块 (The `kotlin` block)**
在这里你可以对编译器进行“微调”。例如，你可以开启之前提到的 **Opt-in** 功能，而不必在每个文件里写注解：
```kotlin
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-opt-in=kotlin.time.ExperimentalTime")
    }
}
```
## 前言
#### 项目自动生成的Spring Boot Application
```kotlin
package org.example.demo  
  
import org.springframework.boot.autoconfigure.SpringBootApplication  
import org.springframework.boot.runApplication  
  
@SpringBootApplication  
class SpringDemoApplication  
  
fun main(args: Array<String>) {  
    runApplication<SpringDemoApplication>(*args)  
}
```
1. 声明`SpringDemoApplication`类
	在Kotlin中，如果一个类没有任何成员（字段或方法），那么可以省略`{}` class body
2. 使用[`@SpringBootApplication`注解](https://docs.spring.io/spring-boot/reference/using/using-the-springbootapplication-annotation.html#using.using-the-springbootapplication-annotation)
	在Spring Boot中，`@SpringBootApplication`注解用于开启[自动配置](https://docs.spring.io/spring-boot/reference/using/auto-configuration.html#using.auto-configuration)、[组件扫描](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/ComponentScan.html)，甚至可以在application class上自定义额外配置
3. 程序入口`fun main()`
	`main`函数是程序的入口。[顶级/top level](https://kotlinlang.org/docs/functions.html#function-scope)`main`函数被声明在`SpringDemoApplication`的外部、`org.example.demo`包的级别；`main`函数封装了Spring的`runApplication`，用于启动Spring Framework application
4. `main`函数的参数`Array<String>`
	这意味着你可以通过CLI向Spring传递一系列参数
5. 数组展开符号 `*args`
	`main`函数参数`args`的类型是字符串数组。既然它是字符串数组，而你想将它的内容传递给`runApplication`函数，你可以使用*展开操作符* （在数组变量前面加上`*`号）
## Hello World
### 创建一个Controller
在Spring框架中，Controller是用来处理web请求的。在`com.example.demo`（和`Main.kt`一个层级）下创建`MessageController.kt`：
```kotlin
import org.springframework.web.bind.annotation.GetMapping  
import org.springframework.web.bind.annotation.RequestParam  
import org.springframework.web.bind.annotation.RestController  
  
@RestController  
class MessageController {  
    @GetMapping("/")  
    fun index (  
        @RequestParam("name")  
        name: String  
    ) = "Hello, $name"  
}
```
1. `@RestController `注解
	指定所装饰的类为**Spring Controller类**；这个注解意味着该组件将能被Spring扫描出来，因为它和`Main.kt`就是一个包级别的
	Kotlin的普通类（不是抽象类）默认是`final`的，不可被继承的——而Spring的机制就是要继承Controller类之后实现一个新的子类，并调用这个子类处理请求，所以原生Kotlin + Spring在使用`@RestController `注解后还需要加上`open`关键字，修饰当前类为可继承的。`kotlin-allopen`插件可以自动处理这个流程
	![](assets/Pasted%20image%2020260301171041.png)
2. `@GetMapping`注解
	标记给定函数为实现了HTTP GET接口的方法
	```kotlin
	fun index (  
        @RequestParam("name")  
        name: String  
    ) = "Hello, $name" 
	```
3. `@RequestParam`注解
	标记给定变量应当与哪个名称的参数绑定
4. 单行函数`index()`
	Kotlin语法糖，当函数体只有一行时，可以省略`{}`函数体，改为在函数类型后面写上` = single-line expression`；Kotlin同时会推导函数返回值类型，这里推导为`String`，因为写上去的是字符串，字符串本身就能`evaluate`，Kotlin将此作为函数返回值
5. Kotlin字符串模板语法 `Hello, $name`
	- `$name`：引用变量
	- `${...}`：引用表达式（函数、表达式）的求值，例如`${user?.name: "unknown"}`

![](assets/Pasted%20image%2020260301171913.png)
*0秒猜出默认端口*
#### Data Class在Spring中的应用
还是在`Main.kt`同目录下，创建一个`Message.kt`文件：
```kotlin
package org.example.demo  
  
data class Message (val id: String?, val text: String)
```
`Message`类将被用于传递一系列序列化为JSON文档后的`Message`对象，用于`MessageControll`的API

1. **数据类**
	`data class xxx`创建一个**数据类**，数据类相比普通类自带`toString`、`copy`和`equals`等方法
2. `val`和`var`关键字
	前者用于声明引用固定的变量，后者用于声明引用可变的变量；引用可变不可变与变量本身能否变化无关，比如`val ml = mutableListOf("A", "B", "C")`创建出来的`MutableList`就是能使用`add`和`remove`方法的，和`val`不`val`的无关
3. **可空类型** `String?`
	变量可以为`null`，后面对变量的访问和方法调用都必须显式处理`null`值情况，即使业务逻辑里那些可空属性一直都不可空
***
在`MessageController.kt`中，移除`index()`函数，改为：
```kotlin
import org.springframework.web.bind.annotation.GetMapping  
import org.springframework.web.bind.annotation.RequestMapping  
import org.springframework.web.bind.annotation.RestController  
  
@RestController  
@RequestMapping("/")  
class MessageController {  
    @GetMapping  
    fun listMessages() = listOf(  
        Message("1", "Hello!"),  
        Message("1", "Bonjour!"),  
        Message("3", "Private!"),  
    )  
}
```
1. `listOf`函数
	接受可变长度参数列表，创建**不可变列表**变量

![](assets/Pasted%20image%2020260301173503.png)
:::tip
在 Spring 应用程序中，如果类路径（classpath）中存在 **Jackson** 库，任何控制器（controller）默认都会渲染 JSON 响应。由于你在 `build.gradle.kts` 文件中指定了 `spring-boot-starter-webmvc` 依赖，Jackson 已作为**传递性依赖**（transitive dependency）被引入。因此，如果端点（endpoint）返回的是一个可以被序列化为 JSON 的数据结构，应用程序就会以 JSON 文档的形式进行响应。
:::
:::note 术语补充
- **传递性依赖 (Transitive Dependency)**： 你不需要手动添加 `jackson-databind`。当你引入 `spring-boot-starter-webmvc` 时，它内部已经包含了 Jackson。这就像你买了一套“西装套餐”，衬衫和领带是自动包含在里面的。
    
- **内容协商与序列化**： Spring 探测到 Jackson 后，会自动配置 `MappingJackson2HttpMessageConverter`。当你让一个函数返回一个 Kotlin **数据类 (Data Class)** 时，Jackson 会通过反射读取属性，并将其转换为 `{"key": "value"}` 格式。
    
- **默认行为**： 这就是 Spring Boot “约定优于配置”的体现。只要库在那里，它就假设你想要 JSON。
:::
### 添加数据库支持
在基于 Spring 框架的应用程序中，通用的做法是在所谓的**服务层（Service Layer）** 内实现数据库访问逻辑——这里是业务逻辑所在的地方。在 Spring 中，你应该使用 `@Service` 注解来标记类，以暗示该类属于应用程序的服务层。在本章节中，你将为此创建一个 `MessageService` 类。

还是在`Main.kt`同目录下，创建`MessageService.kt`文件：
```kotlin
import org.springframework.jdbc.core.JdbcTemplate  
import org.springframework.stereotype.Service  
import java.util.UUID
 
@Service  
class MessageService(private val db: JdbcTemplate) {  
    fun findMessage() = db.query("select * from messages") {  
        resp, _ ->  
        Message(resp.getString("id"), resp.getString("text"))  
    }  
  
	fun save(message: Message): Message {  
	    val id = message.id?: UUID.randomUUID().toString()  
	    db.update (  
	        "insert into messages values (?, ?)",  
	        id, message.text  
	    )  
	    return message.copy(id = id)  
	}
}
```
1. `db.query`第二个参数对应`rowMapper`，是一个回调函数——这里因为回调函数同时是函数的`db.query`的最后一个参数，因此看上去是挂在`db.query()`外面的lambda函数，也就是**trailing lambda**特性
	![](assets/Pasted%20image%2020260301175316.png)
#### 更新`MessageController`类
```kotlin
import org.springframework.http.ResponseEntity  
import org.springframework.web.bind.annotation.*  
import java.net.URI  
  
@RestController  
@RequestMapping("/")  
class MessageController(private val service: MessageService) {  
    @GetMapping  
    fun listMessages() = service.findMessage()  
  
    @PostMapping  
    fun post(@RequestBody message: Message): ResponseEntity<Message> {  
        val savedMessage = service.save(message)  
        return ResponseEntity.created(  
            URI("/${savedMessage.id?: "unknown-id"}")  
        ).body(savedMessage)  
    }  
}
```
1. **`@PostMapping`注解**
	The method responsible for handling HTTP POST requests needs to be annotated with `@PostMapping` annotation. To be able to convert the JSON sent as HTTP Body content into an object, you need to use the `@RequestBody` annotation for the method argument. Thanks to having the Jackson library in the classpath of the application, the conversion happens automatically.
	 标记用于处理HTTP POST请求的方法。为了将JSON格式的消息体数据转换为对象，你需要给方法参数加上`@RequestBody`注解。多亏了类路径里的Jackson，这一转换过程是自动发生
2. `ResponseEntity`
	`ResponseEntity` represents the whole HTTP response: status code, headers, and body.
	Using the `created()` method you configure the response status code (201) and set the location header indicating the context path for the created resource.
	`ResponseEntity`可以存储整一个HTTP返回值：状态码、响应头和消息体
	使用`created()`方法，你可以配置状态码（[201 Created](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Reference/Status/201)），并设置重定向路径
#### 配置数据库
1. 在`src/main/resources/`目录下创建`schema.sql`文件。`.sql`文件用于存储数据库对象定义
	![](assets/Pasted%20image%2020260301193450.png)
2. 更新`schema.sql`文件：
	```sql
	create table if not exists messages (  
    id varchar(60) primary key,  
    text varchar not null  
);
	```
3. 打开`src/main/resources`目录下的`application.properties`，添加如下配置：
	```yaml
	spring:  
	  application:  
	    name: spring-demo  
	  datasource:  
	    driver-class-name: org.h2.Driver  
	    url: jdbc:h2:file:./data/testdb  
	    username: name  
	    password: password  
	  sql:  
	    init:  
	      schema-locations: classpath:schema.sql  
	      mode: always
	```

这些设置会启用Spring程序的数据库。[详情请见](https://docs.spring.io/spring-boot/appendix/application-properties/index.html)
#### 通过HTTP请求添加Message数据到数据库
在根目录下创建`requests.http`文件并添加下面的HTTP请求：
```
### Post "Hello!"
POST http://localhost:8080/
Content-Type: application/json

{
  "text": "Hello!"
}

### Post "Bonjour!"

POST http://localhost:8080/
Content-Type: application/json

{
  "text": "Bonjour!"
}

### Post "Privet!"

POST http://localhost:8080/
Content-Type: application/json

{
  "text": "Privet!"
}

### Get all the messages
GET http://localhost:8080/
```

![](assets/Pasted%20image%2020260301195152.png)
#### 通过ID获得消息
拓展业务逻辑，实现`findMessageById`
1. 在`MessageService`类中添加`findMessageById(id: String)`
	```kotlin
	 import org.springframework.jdbc.core.JdbcTemplate  
	import org.springframework.jdbc.core.query  
	import org.springframework.stereotype.Service  
	import java.util.UUID  
	  
	@Service  
	class MessageService(private val db: JdbcTemplate) {  
	    fun findMessage() = db.query("select * from messages") {  
	        resp, _ ->  
	        Message(resp.getString("id"), resp.getString("text"))  
	    }  
	    fun findMessageById(id: String): Message? = db.query("select * from messages where id = ?", id) {  
	        resp, _ ->  
	        Message(resp.getString("id"), resp.getString("text"))  
	    }.singleOrNull()  
	  
	    fun save(message: Message): Message {  
	        val id = message.id?: UUID.randomUUID().toString()  
	        db.update (  
	            "insert into messages values (?, ?)",  
	            id, message.text  
	        )  
	        return message.copy(id = id)  
	    }  
	}
	```
	- `singleOrNull`：列表的方法，仅当列表中只有一个对象且该对象不为`null`时有返回值，否则，若列表中没有元素或有多个元素时返回`null`
	- `Message?`：`Message`的可空类型，这里显式标出来方便理解
	- `findMessageById`用到的`query`函数需要额外的依赖导入`import org.springframework.jdbc.core.query`，是由Spring提供的Kotlin拓展
2. 在`MessageController`中添加新的`index`路由：
	```kotlin
	    @GetMapping("/{id}")  
		fun get(@PathVariable id: String) = service.findMessageById(id).toResponseEntity()  
		  
		private fun Message?.toResponseEntity() = this?.let {  
		    ResponseEntity.ok(it)  
		}?: ResponseEntity.notFound().build<Message>()
	```
	- `@PathVariable`：标记给定字段为动态路径参数
	- `?.let`：Message返回值不为空时执行`let`块中的函数
	- `?.let`后面的`?:`：返回值为空就走这个分支，构造 404 响应块
		- 不使用拓展函数，而是直接在`service.findMessageById(id)`后面写`?: ResponseEntity.notFound()`的话，在搜索不到数据的时候会给个200 空消息体响应，不知道为什么
		![](assets/Pasted%20image%2020260301201513.png)
	- **可空类型**的拓展函数
		拓展函数的所有者可以为**可空类型**
![](assets/Pasted%20image%2020260301200728.png)
![](assets/Pasted%20image%2020260301201524.png)
使用拓展私有函数拓展Controller之后，才修复蜜汁空消息体的问题

### 使用Spring Data CrudRepository
在这一节中，你将把服务层（service layer）进行迁移，使用 **Spring Data `CrudRepository`** 代替 `JdbcTemplate` 来进行数据库访问。`CrudRepository` 是一个 Spring Data 接口，用于对特定类型的仓库（repository）执行通用的 **CRUD**（增、删、改、查）操作。它提供了一系列开箱即用的方法，用于与数据库进行交互。

:::note `JdbcTemplate` vs `CrudRepository`

- **`JdbcTemplate`**：你需要自己编写 SQL 语句（如 `SELECT * FROM messages`），手动处理结果集（ResultSet）并将其映射到对象。虽然灵活，但代码冗余量大。
    
- **`CrudRepository`**：你只需定义一个接口并继承它。Spring Data 会在运行时自动为你生成实现逻辑。你不需要写一行 SQL 就能实现基础功能。
:::
:::note Spring Data 的魔力：方法名派生

除了标准方法，`CrudRepository` 还支持通过方法名自动生成查询。例如，在 Kotlin 接口中定义 `fun findByText(text: String): List<Message>`，Spring 会自动解析并生成对应的 SQL，无需手动配置。
:::
#### 更新程序
首先需要修改`Message`类以适应`CrudRepository`API：
1. 给`Message`类加上`@Table`注解，将`Message`映射到数据表上；并给`id`字段加上`@Id`注解：
	这些注解都需要额外的导入语句
	```kotlin
	import org.springframework.data.annotation.Id  
	import org.springframework.data.relational.core.mapping.Table  
	  
	@Table("MESSAGES")  
	data class Message (@Id val id: String? = null, val text: String)
	```
	- `id: String ?= null`：显式加上默认值`null`，提高可读性
1. 创建`MessageRepository.kt`文件，声明`MessageRepository`接口（管理`Message`表相关的CRUD逻辑）并实现`CrudRepository`接口：
	```kotlin
	import org.springframework.data.repository.CrudRepository  
  
	interface MessageRepository: CrudRepository<Message, String>
	```
	- `CrudRepository`需要两个泛型参数：`<DataObject> T`和`<ID> ID`
1. 更新`MessageService`类，使用`MessageRepository`而非执行原生SQL语句：
	```kotlin
	import org.springframework.data.repository.findByIdOrNull  
	import org.springframework.stereotype.Service  
	import java.util.UUID  
	  
	@Service  
	class MessageService(private val db: MessageRepository) {  
	    fun findMessage(): List<Message> = db.findAll().toList()  
	    fun findMessageById(id: String): Message? = db.findByIdOrNull(id)  
	  
	    fun save(message: Message): Message = db.save(message)  
	}
	```
	- `findByIdOrNull`：给Spring Data JDBC的`CrudRepository`的扩展函数
	- `CrudRepositor<T>.save()`函数：
		[This function works](https://docs.spring.io/spring-data/relational/reference/#jdbc.entity-persistence) with an assumption that the new object doesn't have an id in the database. Hence, the id **should be null** for insertion.
		If the id isn't _null_, `CrudRepository` assumes that the object already exists in the database and this is an _update_ operation as opposed to an _insert_ operation. After the insert operation, the `id` will be generated by the data store and assigned back to the `Message` instance.
		函数默认新对象在数据库中没有记录。因此，对象插入时**不应该携带**id
		如果id不为空，`CrudRepository`会假定数据库中已经存在给定对象，并将**插入操作**更换为**更新操作**，数据库会顺便取出`id`，并将其赋回给`Message`实例
1. 更新`schemq.sql`中的数据表定义；鉴于`id`是字符串类型，所以可以使用`RANDOM_UUID()`函数来生成ID
	```sql
	create table if not exists messages (  
	    id varchar(60) default RANDOM_UUID() primary key,  
	    text varchar not null  
	);
	```
2. 最后更新`application.properties`：
	![](assets/Pasted%20image%2020260301205319.png)

![](assets/Pasted%20image%2020260301205349.png)
***
# 页面底部
