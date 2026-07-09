---
title: tsconfig 配置详解
date: 2026-07-09
footer: Trae AI 创作
---

# tsconfig 配置详解

> **面向读者**：有 Go 后端经验的开发者。TypeScript 的 `tsconfig.json` 可以理解为 `go.mod` + 编译器选项的结合体——既声明项目元信息，又控制编译行为。理解和配置好它是高质量前端项目的起点。

---

## 一、tsconfig.json 的角色定位

```json
{
  "compilerOptions": {
    // 编译器选项（核心）
  },
  "include": [
    // 编译包含的文件
  ],
  "exclude": [
    // 编译排除的文件
  ]
}
```

| 概念              | TS `tsconfig.json`        | Go 类似概念              |
| ----------------- | ------------------------- | ------------------------ |
| 项目标识          | `compilerOptions`          | `go.mod`                 |
| 目标平台          | `target`                   | `GOOS` / `GOARCH`        |
| 严格模式          | `strict: true`             | `go vet` 内置检查         |
| 模块系统          | `module`                   | `GO111MODULE`            |
| 依赖路径          | `paths` + `baseUrl`        | `replace` / `module path` |
| 源文件范围        | `include` / `exclude`      | `*.go` 文件自动包含       |
| 输出目录          | `outDir`                   | `go build -o`             |
| Source Map        | `sourceMap: true`          | 非原生支持（需第三方）     |

::: tip

Go 的编译器选项相对固定（几乎没有可开关的），而 TS 提供了 100+ 编译选项——这是 JS 生态"没有官方工具链"的补偿，选择权完全交给开发者。

:::

---

## 二、严格模式（最核心）

严格模式是 TS 中最**重要**的选项组，类比 Go 的 `go vet` 但覆盖面更广：

```json
{
  "compilerOptions": {
    // === 一键开启所有严格检查 ===
    "strict": true

    // === strict: true 展开后包含以下所有 ===
    // "strictNullChecks": true,     // 不能把 null/undefined 赋值给其他类型
    // "noImplicitAny": true,       // 禁止隐式 any
    // "strictFunctionTypes": true,  // 函数参数逆变检查
    // "strictBindCallApply": true,  // bind/call/apply 类型检查
    // "strictPropertyInitialization": true, // 属性必须初始化
    // "noUnusedLocals": true,       // 未使用的局部变量（类似 Go unused 变量）
    // "noUnusedParameters": true,   // 未使用的参数
    // "noImplicitReturns": true,    // 所有路径必须有返回值
  }
}
```

### 2.1 strict 开启前后的对比

```ts
// ❸ strict: false（不推荐）
function greet(name) {
  // noImplicitAny 关闭 → name 是隐式 any
  return `Hello, ${name.toUpperCase()}`;
}

let x;
x = 42;
x = "hello"; // 任何类型都可以
```

```ts
// ❸ strict: true（推荐）
function greet(name: string): string {
  // 必须显式标注类型
  return `Hello, ${name.toUpperCase()}`;
}

let x: string | number;
x = 42;
x = "hello"; // OK（联合类型）
```

### 2.2 strictNullChecks 对比

```ts
// strictNullChecks: false
const el = document.getElementById('not-exists');
el.style.color = 'red'; // 运行时崩溃 ❌

// strictNullChecks: true
const el = document.getElementById('not-exists');
// el 的类型是 HTMLElement | null
if (el) {
  el.style.color = 'red'; // ✅ 类型收窄后安全
}
```

```go
// Go 中默认就是"不能 nil 赋值给非指针类型"
var s string  // "", 不是 nil
var p *string // nil，使用前必须检查
```

::: warning 永远不要关闭 strict

```json
{
  "compilerOptions": {
    "strict": false  // ❌ 不推荐——等于放弃了 TS 最大的价值
  }
}
```

关闭 `strict` 相当于 `go build` 时关闭了类型检查——这违背了使用 TypeScript 的根本目的。

:::

---

## 三、target — 编译目标

```json
{
  "compilerOptions": {
    "target": "ES2020"
    // 可选：ES5 | ES6/ES2015 | ES2016 | ... | ES2022 | ESNext
  }
}
```

| target       | 支持的特性                     | 类比 Go         |
| ------------ | ------------------------------ | --------------- |
| `ES5`        | 兼容 IE11 及以下（已淘汰）      | 交叉编译到旧架构 |
| `ES6/ES2015` | `class` `箭头函数` `Promise`   | Go 1.x 基线    |
| `ES2020`     | 可选链 `?.` 空值合并 `??`      | 当前主流版本    |
| `ESNext`     | 最新的提案特性                 | Go tip 版本      |

```json
// 当前推荐配置
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"]
  }
}
```

::: tip

`target` 决定的是**语法降级**（如箭头函数转普通函数），而 `lib` 决定的是**类型定义**（如 `Promise` `Map` `fetch` 是否需要类型声明）。

类比 Go：`GOOS=linux GOARCH=amd64` 决定目标平台，`target` 决定"最低运行时版本"。

:::

---

## 四、module — 模块系统

```json
{
  "compilerOptions": {
    "module": "ESNext",
    // 可选：CommonJS | AMD | UMD | System | ESNext | NodeNext
    "moduleResolution": "bundler"
    // 可选：node | classic | bundler | nodenext
  }
}
```

### 4.1 常见组合

| 场景                    | module           | moduleResolution   |
| ----------------------- | ---------------- | ------------------ |
| 浏览器（Vite 构建）     | `ESNext`         | `bundler`          |
| Node.js 服务端          | `CommonJS`       | `node`             |
| Node.js ESM             | `NodeNext`       | `NodeNext`         |
| 兼容环境                | `ESNext`         | `bundler`          |

```json
// 前端 Vite 项目的推荐配置
{
  "compilerOptions": {
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true
  }
}
```

### 4.2 类比 Go

```go
// Go 的模块系统相对简单——module path 决定导入路径
import "github.com/gin-gonic/gin"

// TS 需要区分：import 是"静态导入"还是"运行时 require"
import { ref } from 'vue';     // ESM 静态导入
const lodash = await import('lodash'); // 动态导入
```

::: info ESM vs CommonJS

| 特性           | ESM (`import`/`export`)     | CommonJS (`require`/`module.exports`) |
| -------------- | --------------------------- | ------------------------------------- |
| 加载方式       | 静态编译时                  | 动态运行时                            |
| 树摇（Tree Shaking） | 原生支持              | 不支持                                |
| 异步加载       | `import()`                  | `require()` 同步                      |
| 浏览器支持     | 原生                        | 需打包工具转换                        |
| Go 类比        | import 语句                 | 无直接类比                            |

:::

---

## 五、paths + baseUrl — 路径映射

```json
{
  "compilerOptions": {
    "baseUrl": ".",              // 路径解析的根目录
    "paths": {
      "@/*": ["src/*"],          // @/ 映射到 src/
      "@components/*": ["src/components/*"],
      "@utils/*": ["src/utils/*"]
    }
  }
}
```

```ts
// 使用路径别名
import { Button } from '@components/common/Button';
import { formatDate } from '@utils/format';

// 而不是深层相对引用
// import { Button } from '../../../components/common/Button';
```

### 5.1 类比 Go module path

```go
// go.mod
module github.com/myapp

// main.go
import "github.com/myapp/internal/utils"
```

| 概念        | Go                    | TS                         |
| ----------- | --------------------- | -------------------------- |
| 项目根路径 | `module` in `go.mod`  | `baseUrl`                  |
| 路径简写    | 完整 module path      | `paths` 别名               |
| 外部依赖    | `require` in `go.mod` | `dependencies` in `package.json` |
| 本地替换    | `replace`             | `paths` 或 workspace       |

::: warning paths 需要配合构建工具

`tsconfig.json` 中的 `paths` 只影响 TS 编译时的类型检查，不影响运行时模块解析。需要额外配置 Vite/Rollup/webpack 的 resolve alias：

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
});
```

否则编译通过了，运行时找不到模块。

:::

---

## 六、types / typeRoots — 类型声明

```json
{
  "compilerOptions": {
    "typeRoots": ["./node_modules/@types"],
    "types": ["node", "vite/client"]
  }
}
```

| 配置          | 作用             | 类比 Go                     |
| ------------- | ---------------- | --------------------------- |
| `typeRoots`   | 类型声明搜索路径 | `GOPATH` / `GOMODCACHE`    |
| `types`       | 自动加载哪种类型 | 类似 `//go:generate` 指令   |
| 不设置 `types` | 自动加载所有 `@types/*` | Go 自动解析所有 import |

```json
// node_modules/@types/ 目录结构
node_modules/
└── @types/
    ├── node/          # Node.js 类型
    ├── react/         # React 类型
    └── lodash/        # Lodash 类型

// 设置 types: ["node"] 后，只加载 @types/node
// 其他 @types/* 不会被自动加载，需要手动 import
```

::: tip

对于前端项目（Vue/React），推荐将 DOM 类型通过 `lib` 引入，而非 `types`：

```json
{
  "compilerOptions": {
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "types": ["vite/client"]
  }
}
```

`lib` 中的 `"DOM"` 提供了 `document` `window` `HTMLElement` 等类型。

:::

---

## 七、include / exclude — 文件范围

```json
{
  "include": ["src"],
  "exclude": ["node_modules", "dist", "**/*.spec.ts"]
}
```

| 配置 | 说明 | 类比 Go |
| --- | --- | ------- |
| `include` | 编译哪些文件 | 所有 `.go` 文件（无需配置） |
| `exclude` | 排除哪些文件 | `_test.go` 通过 `go test` 控制 |

```json
// 更精确的 include 写法
{
  "include": [
    "src/**/*.ts",
    "src/**/*.tsx",
    "src/**/*.vue",
    "env.d.ts"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "coverage",
    "**/*.test.ts",
    "**/*.spec.ts"
  ]
}
```

---

## 八、Source Map

```json
{
  "compilerOptions": {
    "sourceMap": true,
    // 或
    "inlineSourceMap": false
  }
}
```

| 配置                | 作用                 | 类比 Go               |
| ------------------- | -------------------- | --------------------- |
| `sourceMap: true`   | 生成 `.js.map` 文件 | Go 无原生支持          |
| `inlineSourceMap`   | 内嵌到 JS 文件中    | 调试线上代码时使用      |
| `inlineSources`     | 源代码也嵌入 map    | 配合 Sentry 等错误监控 |

::: info Source Map 的作用

```ts
// TS 源码 → 经过编译 → 混淆/压缩的 JS
// 浏览器运行的是 JS，但通过 Source Map 可以定位到 TS 源码的行号

// 开发环境必须开启，生产环境建议配合错误监控开启
{
  "compilerOptions": {
    "sourceMap": true
  }
}
```

Go 虽然没有 Source Map，但 `go tool pprof` + 二进制符号表提供了类似的"从运行态映射到源码"的能力。

:::

---

## 九、推荐模板

### 前端项目（Vue 3 + Vite）

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    },
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "types": ["vite/client"]
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
  "exclude": ["node_modules", "dist"]
}
```

### React 项目（React + Vite）

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "react-jsx",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    },
    "lib": ["ES2020", "DOM", "DOM.Iterable"]
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

---

## 十、Bad vs Best

### Bad：关闭严格模式

```json
{
  "compilerOptions": {
    "strict": false,          // ❌ 放弃了类型检查
    "noImplicitAny": false,   // ❌ 允许隐式 any
    "strictNullChecks": false // ❌ null 随意赋值
  }
}
```

```ts
// 这样写都不会报错
function process(data) {
  return data.name.toUpperCase();
}
process(undefined); // 运行时崩溃
```

### Best：始终开启 strict

```json
{
  "compilerOptions": {
    "strict": true,            // ✅ 严格模式全家桶
    "noUnusedLocals": true,    // ✅ 检查未使用的变量
    "noUnusedParameters": true, // ✅ 检查未使用的参数
    "noImplicitReturns": true  // ✅ 所有路径必须有返回值
  }
}
```

```ts
// strict: true 后，这些都会报错
function process(data: { name: string } | null): string {
  if (!data) return '';
  return data.name.toUpperCase();
}
```

::: warning 类比 Go

| 关闭 strict 的 TS 项目          | Go 项目                       |
| ------------------------------ | ----------------------------- |
| 等于用 `interface{}` 写所有函数 | 等于全部用 `interface{}`      |
| 放弃了编译时类型安全            | Go 编译器不会允许这样          |
| 最终变成"带类型的 JavaScript"   | 失去了 TypeScript 的核心价值   |

:::

---

## 总结

| 配置选项               | 用途                   | 推荐值              | 类比 Go               |
| ---------------------- | ---------------------- | ------------------- | --------------------- |
| `strict: true`         | 开启所有严格检查       | `true`              | `go vet`              |
| `target`               | 编译目标版本           | `ES2020`            | GOOS/GOARCH           |
| `module`               | 模块系统               | `ESNext`            | go.mod module         |
| `paths` + `baseUrl`    | 路径别名               | `@/*` → `src/*`    | go module path        |
| `sourceMap: true`      | 调试映射               | `true`              | 无原生支持             |
| `lib`                  | 运行时类型定义         | `ES2020` + `DOM`   | 标准库类型             |

下一站：[ESLint + Prettier 代码规范](./06-ESLint-Prettier代码规范.md)，学习如何形成规范化的代码风格。
