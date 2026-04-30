---
title: mbt 前端速成笔记（一）
date: 2026-04-26
---
[[toc]]
***
### wasm构建和运行简述
:::note 参考资料
- [官方 - Moonbit与JS交互](https://www.moonbitlang.cn/pearls/moonbit-jsffi)
:::
#### 预先准备
为了让 MoonBit 工具链知晓我们的目标平台是 JavaScript，我们需要在项目根目录的 `moon.mod.json` 文件中添加以下内容：
```json
{
  "preferred-target": "js"
}
```
此项配置会告知编译器，在执行 `moon build` 或 `moon check` 等命令时，默认使用 JavaScript 后端。 当然，如果你希望在命令行中临时指定，也可以通过 `--target=js` 参数达到同样的效果

#### 构建wasm目标文件
MoonBit 编译器通过 `moon build` 命令进行编译。由于我们要运行在浏览器，需要指定目标为 `wasm` 或 `js`

**针对 Web 端，我们通常直接使用 `js` 后缀的目标**（因为它会自动帮你生成 `wasm` 以及配套的加载逻辑）：
```sh
moon build --target js
```
命令执行成功后，由于我们的项目默认包含一个可执行入口，你可以在 `target/js/debug/build/` 目录下找到编译产物。MoonBit 非常贴心地为我们生成了三个文件：
- `.js` 文件：编译后的 JavaScript 源码。
- `.js.map` 文件：用于调试的 Source Map 文件。
- `.d.ts` 文件：TypeScript 类型声明文件，便于在 TypeScript 项目中集成。
```
│  .moon-lock
│  packages.json
│
├─js
│  └─debug
│      └─build
│          │  all_pkgs.json
│          │  build.moon_db
│          │
│          └─cmd
│              └─main
│                      main.core
│                      main.d.ts
│                      main.js
│                      main.js.map
│                      main.mi
│                      moonbit.d.ts
```

#### HTML页面挂载
你需要一个 HTML 文件来加载生成的 `.js` 文件。

在你的项目根目录下创建一个 `index.html`：
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>MoonBit Go-Style Test</title>
</head>
<body>
  <div id="app"></div>

  <script type="module">
    // 注意：路径需根据你 build 出来的实际位置调整
    import "./target/js/release/build/cmd/main/main.js"; // 导入的时候默认自动执行main函数
    
    // 启动 MoonBit 程序
    main();
  </script>
</body>
</html>
```

#### 运行本地服务器
:::warning
你不能直接双击 `index.html` 打开。因为浏览器出于安全考虑，禁止通过 `file://` 协议加载 Wasm 模块（CORS 策略）
:::
你需要一个本地 Web 服务器。你可以用任何你熟悉的工具，比如 Go 程序员最常用的一行命令：
```sh
# 如果你有 Go 环境
go run github.com/schollz/serve@latest .

# 或者简单的 Python 服务器
python3 -m http.server 8080
```

### 一、 浏览器互操作 (FFI 基础)
:::note 参考资料
- [官方 - FFI文档](https://docs.moonbitlang.cn/language/ffi.html)
:::
#### 1.1 `extern` 关键字与外部函数声明
MoonBit 的 FFI 设计在原则上保持了一致性。与调用 C 或其他语言类似，我们通过一个带有 `extern` 关键字的函数声明来定义一个外部调用
```js
// 语法结构：extern "协议" fn 函数名(参数) -> 返回类型 = "JS中的真实路径"
extern "js" fn consoleLog(msg : String) -> Unit = "(msg) => console.log(msg)"
```
- `extern "js"`：声明这是一个指向 JavaScript 环境的外部函数。
- `fn consoleLog(msg : String) -> Unit`：这是该函数在 MoonBit 中的类型签名，它接受一个 `String` 类型的参数，并且返回一个单位值 (`Unit`)。
- `"(msg) => console.log(msg)"`：等号右侧的字符串字面量是这段 FFI 的“灵魂”，其中需要包含一段原生 JavaScript 函数。
    在这里，我们使用了一个简洁的箭头函数。 MoonBit 编译器会按原样将这段代码嵌入到最终生成的 `.js` 文件中，从而实现从 MoonBit 到 JavaScript 的调用。
:::tip
如果你的 JavaScript 代码片段比较复杂，可以使用 `#|` 语法来定义多行字符串，以提高可读性。
:::

```js
extern "js" fn alert(msg: String) -> Unit = "alert"
extern "js" fn alert_raw(msg : String) -> Unit = 
  #|(msg) => { window.alert(msg); }
extern "js" fn console_log(msg: String) -> Unit = "(s) => console.log(s)"

fn main {
  alert_raw("Hello World")
  console_log("Hello World")  
}
```
:::warning 
仅供参考，根本跑不起来
![](assets/Pasted%20image%2020260426214716.png)
`alert`会丢失内容，而`console.log`则是跑都跑不起来

更别说LSP还处处和我作对，只要有一个`extern "js"`在文件里面就会导致语法高亮和代码补全无法再使用
:::
:::warning
直接在闭包函数里写逻辑都没用
![](assets/Pasted%20image%2020260426220743.png)

mbt你牛大了
:::


##### 参考资料：以JS为后端时的外部函数声明
![](assets/Pasted%20image%2020260426213642.png)

:::warning
FFI调用的JS函数只在JS运行时里有效，在浏览器环境中无效；如果需要操作界面，必须FFI调用DOM操作函数

```js
extern "js" fn dead_simple_call() -> Unit = "() => { const el = document.createElement('div'); el.innerText='WASM 确实动了'; document.body.appendChild(el); }"

fn main {
  dead_simple_call()
}
```
:::

#### 1.2 基础类型映射（Int, Float, String, JsPtr）
|**MoonBit 类型**|**JavaScript 对应**|**说明**|
|---|---|---|
|`Int`|`Number`|对应 JS 的整数部分|
|`Float`|`Number`|对应 JS 的浮点数|
|`String`|`String`|**注意**：底层会自动处理编码转换|
|`Bool`|`Boolean`|直接映射|
|**`JsPtr`**|**`Object`**|**重点**：代表一个 JS 对象的引用（句柄）|

:::tip **什么是 `JsPtr`？** 
由于 Wasm 不能直接把一个巨大的 JS 对象（比如整个 DOM 树）塞进自己的内存，它只能通过一个“指针”或者“编号”来代表这个对象。在 MoonBit 里，我们通常用 `JsPtr` 来持有浏览器的 `window`, `document` 或某个 `button`。
:::

#### 1.3 `pub` 与 `pub(all)` 在 FFI 中的导出规则
如果你写的 MoonBit 函数要被 JS 调用（比如 JS 里的一个定时器触发了 MoonBit 的逻辑），你就得**导出**它

- **`pub fn`**: 导出函数，外部（其他 MoonBit 包或 JS）可见。
- **`pub(all) struct`**: 在 FFI 场景下，如果你希望 JS 能完整看到结构体的所有字段，需要使用 `pub(all)`


#### 1.4 内存模型预警：Wasm 与 JS 的边界

### 二、 声明式 UI 核心概念 (Declarative UI)

#### 2.1 状态驱动视图 (State -> View) 模型

#### 2.2 虚拟 DOM (V-DOM) 与 Diff 算法简介

#### 2.3 信号 (Signal) 与 细粒度更新 * (取决于具体框架)



### 三、 UI 框架实战：核心组件库

#### 3.1 定义组件结构 (Component Struct)

#### 3.2 属性传递 (Props) 与 默认值处理

#### 3.3 事件处理 (Event Handling) 与 闭包陷阱

#### 3.4 列表渲染与 Key 值的重要性

### 四、 高级特性与样式

#### 4.1 样式绑定 (Style & CSS-in-JS)

#### 4.2 生命周期钩子 (Lifecycle Hooks)

#### 4.3 异步数据加载 (Async/Await in UI)

### 五、 云原生与边缘集成

#### 5.1 Wasm 模块体积优化

#### 5.2 在 Serverless 环境下渲染 UI (SSR)


***
# 页面底部