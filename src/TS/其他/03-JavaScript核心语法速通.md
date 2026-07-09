---
title: JavaScript 核心语法速通
date: 2026-07-09
footer: Trae AI 创作
---

# JavaScript 核心语法速通

> **面向读者**：有 Go 后端经验的开发者。JavaScript 的语法乍看起来很熟悉（C 风格），但"神"完全不同——它是一种**动态、弱类型、基于原型**的脚本语言。本文会不断对比 Go，帮你划清界限。

---

## 一、JS vs TS：先搞清楚关系

TypeScript 是 JavaScript 的**超集**——在 JS 基础上增加了**类型系统**。类比 Go 是带类型的语言，TypeScript 就是把"动态"的 JS 加上类型约束：

```
JavaScript = 动态类型 + 解释执行
TypeScript = JS + 类型注解 + 编译时检查
Go        = 静态类型 + 编译执行
```

```ts
// TypeScript 补上类型
function greet(name: string): string {
  return `Hello, ${name}`;
}
```

::: tip 学习路径建议

对于 Go 开发者，**建议直接学习 TypeScript**，跳过纯 JavaScript 的"动态自由"阶段。因为你已经习惯了编译时类型检查，学会 TS 后可以直接上手 Vue/React。

但本篇文章仍然以 JS 讲解核心概念，因为 TS 不会改变 JS 的运行时行为（如 `this` 动态绑定、原型链）。

:::

---

## 二、变量声明与提升（Hoisting）

### 2.1 `var` / `let` / `const`

```js
// Go: name := "Alice"        // 编译时确定类型
// Go: var name string = "Alice"

// JS 三种声明方式
var  name1 = "Alice";   // 函数作用域，有提升（不推荐）
let  name2 = "Bob";     // 块作用域，推荐
const name3 = "Charlie"; // 块作用域，常量（绑定不可变）

// const 是"引用不可变"，而非值不可变
const arr = [1, 2, 3];
arr.push(4);       // OK
// arr = [5, 6, 7]; // Error: Assignment to constant variable
```

### 2.2 变量提升（Hoisting）

```js
console.log(a); // undefined（不报错！）
var a = 10;

// 以上代码等价于：
var a;
console.log(a); // undefined
a = 10;
```

```go
// Go 中不存在提升
fmt.Println(a) // 编译错误：undefined: a
a := 10
```

::: warning 提升陷阱

```js
// let 和 const 不会提升到赋值前可用（暂时性死区）
console.log(b); // ReferenceError: Cannot access 'b' before initialization
let b = 20;
```

类比 Go 中在变量声明之前引用变量，编译器直接报错——但 JS 的 `var` 不会报错，只返回 `undefined`，这是**语言缺陷**，所以总是用 `let` / `const`。

:::

---

## 三、`==` vs `===`（Go 只有 `==`）

这是 JS 中**最容易踩的坑之一**：

```js
// == 会做类型转换（Type Coercion）
5 == "5"     // true（字符串 "5" 转数字 5）
0 == false   // true（false 转 0）
"" == false  // true
null == undefined // true
[] == false  // true

// === 严格相等，不做类型转换（推荐）
5 === "5"    // false
0 === false  // false
null === undefined // false
```

```go
// Go 只有 ==，且不同类型不能直接比较
// 5 == "5"  // 编译错误：mismatched types int and string
```

::: caution 永远使用 `===`

```js
// 推荐的判等写法
if (x === null)    { /* ... */ }
if (x === undefined) { /* ... */ }
if (x === true)    { /* ... */ }

// 检查是否为 null/undefined 的简洁写法
if (x == null) { /* x === null || x === undefined */ }
```

:::

---

## 四、对象字面量 vs Go struct

```js
// JS 对象字面量——类似 Go 的 map + struct 的混合体
const user = {
  name: "Alice",
  age: 30,
  "is-admin": true,    // 带特殊字符的键需要引号
  greet() {            // 方法简写
    return `Hi, I'm ${this.name}`;
  }
};

// 动态增删属性（Go 做不到）
user.email = "alice@example.com";  // 新增
delete user.age;                   // 删除
```

```go
// Go 结构体——字段固定，编译时确定
type User struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}
user := User{Name: "Alice", Age: 30}
```

::: info 关键区别

| 特性         | JS 对象            | Go struct           |
| ------------ | ------------------ | ------------------- |
| 字段固定     | 否（可动态增减）    | 是（编译时确定）     |
| 方法定义     | 函数属性            | 绑定到类型           |
| 访问不存在字段 | 返回 `undefined`  | 编译错误             |
| JSON 转换    | `JSON.stringify`   | `json.Marshal`       |
| 空值判断     | `=== undefined`    | `field == "" / 0`等  |

:::

---

## 五、`this` 动态绑定（核心难点）

**Go 的接收者是静态绑定**，函数定义时确定；**JS 的 `this` 是动态绑定**，调用时确定——这是前端开发中**最易混淆的概念**。

```js
// Go 写法思维：this 绑定到调用者
const obj = {
  name: "Alice",
  greet() {
    console.log(`Hi, I'm ${this.name}`);
  }
};

obj.greet(); // "Hi, I'm Alice"  ✅

// 但是：
const fn = obj.greet;
fn(); // "Hi, I'm undefined" ❌ this 指向全局（或 undefined 严格模式）
```

```go
// Go 中永远不会出现这种情况——接收者是静态确定的
type User struct { Name string }
func (u User) Greet() { fmt.Printf("Hi, I'm %s", u.Name) }

u := User{Name: "Alice"}
fn := u.Greet
fn() // "Hi, I'm Alice" ✅ 始终正确
```

### 5.1 修复 `this` 丢失

```js
// 方式一：箭头函数（不绑定自己的 this）
const obj = {
  name: "Alice",
  greet: () => {
    console.log(`Hi, I'm ${this.name}`); // this 指向外层作用域
  }
};

// 方式二：bind
const fn = obj.greet.bind(obj);

// 方式三：Vue/React 中常用
const onClick = () => {
  console.log(this.name); // 箭头函数继承外层 this
};
```

::: caution `this` 是 JS 中最容易混淆的概念

```js
// React 类组件（旧式）中的典型问题
class Button {
  constructor() {
    this.text = "Click me";
  }

  handleClick() {
    console.log(this.text); // this 会丢失！
  }
}

const btn = new Button();
document.querySelector('button')
  .addEventListener('click', btn.handleClick); // undefined ❌

// 解决：箭头函数
document.querySelector('button')
  .addEventListener('click', () => btn.handleClick()); // ✅
```

记得：谁调用函数，`this` 就指向谁。

:::

---

## 六、原型链（Prototype Chain）vs Go 嵌入

JS 的继承通过原型链实现，类似于 Go 的结构体嵌入（composition），但机制完全不同：

```js
// JS 原型链
function Animal(name) {
  this.name = name;
}
Animal.prototype.speak = function() {
  console.log(`${this.name} makes a sound`);
};

function Dog(name, breed) {
  Animal.call(this, name); // 调用父构造函数
  this.breed = breed;
}
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;

// 覆盖方法
Dog.prototype.speak = function() {
  console.log(`${this.name} barks`);
};

const dog = new Dog("Buddy", "Golden");
dog.speak(); // "Buddy barks"
```

```go
// Go 结构体嵌入（更简洁）
type Animal struct { Name string }
func (a Animal) Speak() {
    fmt.Printf("%s makes a sound\n", a.Name)
}

type Dog struct {
    Animal         // 嵌入
    Breed string
}

func (d Dog) Speak() {
    fmt.Printf("%s barks\n", d.Name)
}

dog := Dog{Animal: Animal{Name: "Buddy"}, Breed: "Golden"}
dog.Speak() // "Buddy barks"
```

::: info 原型链 vs 嵌入的本质区别

| 特性           | JS 原型链         | Go 嵌入                |
| -------------- | ----------------- | ---------------------- |
| 语言类型       | 动态             | 静态                   |
| 查找方式       | 运行时沿链查找    | 编译时确定             |
| 属性覆盖       | 自有属性遮盖原型  | 外层方法提升            |
| 多继承         | 链式（单链）      | 可嵌入多个结构体        |
| ES6 class 语法 | 语法糖，仍是原型  | 不是 class，是 composition |

:::

---

## 七、闭包（Closure）

Go 也支持闭包，但 JS 中闭包使用更频繁，尤其是在事件处理和 React Hooks 中：

```js
// JS 闭包
function createCounter() {
  let count = 0;          // 外部函数的 "私有变量"
  return function() {
    count++;              // 内部函数 "记住" 了 count
    return count;
  };
}

const counter = createCounter();
console.log(counter()); // 1
console.log(counter()); // 2
console.log(counter()); // 3
```

```go
// Go 闭包
func createCounter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}

counter := createCounter()
fmt.Println(counter()) // 1
fmt.Println(counter()) // 2
fmt.Println(counter()) // 3
```

::: tip 前端闭包的典型场景

```js
// React Hooks 中的闭包
function Timer() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    // 这里的 setInterval 通过闭包捕获了 count
    const id = setInterval(() => {
      setCount(c => c + 1); // 使用回调形式避免闭包陷阱
    }, 1000);
    return () => clearInterval(id);
  }, []);

  return <div>{count}</div>;
}
```

闭包陷阱（Closure Trap）：在 useEffect 中直接使用 `count` 而不是 `setCount(c => c + 1)`，会捕获旧值。

:::

---

## 八、JSON 序列化与反序列化

```js
// JS 序列化（类比 Go json.Marshal）
const obj = { name: "Alice", age: 30, role: null };
const jsonStr = JSON.stringify(obj);
// '{"name":"Alice","age":30,"role":null}'

// 美化输出
JSON.stringify(obj, null, 2);

// 反序列化（类比 Go json.Unmarshal）
const parsed = JSON.parse(jsonStr);
console.log(parsed.name); // "Alice"

// 注意：JSON 不支持 undefined、函数、Symbol
JSON.stringify({ a: undefined, b: function(){} }); // '{}'
```

```go
// Go 中的对应
type User struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}
user := User{Name: "Alice", Age: 30}
data, _ := json.Marshal(user)
var parsed User
json.Unmarshal(data, &parsed)
```

::: warning JSON.parse 的安全性

```js
try {
  const data = JSON.parse(userInput);
} catch (e) {
  console.error('Invalid JSON', e);
}
```

类比 Go 中 `json.Unmarshal` 返回 error，JS 的 `JSON.parse` 抛出异常，需要用 `try/catch` 捕获。

:::

---

## 九、严格模式（Strict Mode）

```js
"use strict"; // 写在文件或函数顶部

// 严格模式下的变化：
x = 10;        // ReferenceError（非严格模式下会创建全局变量）
delete x;      // SyntaxError（不能删除变量）

function fn() {
  console.log(this); // undefined（非严格模式下是 window）
}
fn();
```

::: tip 类比 Go

Go 的变量声明后必须使用（编译错误），JS 严格模式禁用了很多"允许但不合适"的行为——都在推动代码更安全、更可预测。

:::

---

## 总结

| JS 概念         | Go 类比                             |
| --------------- | ----------------------------------- |
| `let` / `const` | `:=` / `const`                      |
| 变量提升         | 不存在（编译错误）                    |
| `===`           | `==`（Go 无类型转换比较）            |
| 对象字面量       | struct + map 混合体                  |
| `this` 动态绑定  | 接收者静态绑定（完全不同）            |
| 原型链           | 结构体嵌入（目的相似，机制不同）       |
| 闭包             | 同样支持                              |
| `JSON.parse`    | `json.Unmarshal`（需要 error 处理）   |
| 严格模式         | 编译时约束（Go 的编译器作用类似）      |

下一站：[TS 推荐项目结构规范](./04-TS推荐项目结构规范.md)，学习如何组织一个可维护的前端项目。
