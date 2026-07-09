---
title: samber/do 调试与进阶特性
date: 2026-03-09
author: Deepseek V4 Flash (Trae SOLO Mode)
footer: Trae编辑
---

# samber/do 调试与进阶特性

本文覆盖 samber/do 框架的 **冷门/进阶特性**，包括调试工具链、Web UI 可视化、框架迁移指南以及已知限制。

::: tip 前置阅读
如果你还不熟悉 samber/do 的核心用法（注册、调用、生命周期），请先阅读 [samber_do 依赖注入框架核心指南](samber_do%20依赖注入框架核心指南.md)。
:::

---

## 一、调试工具链

samber/do 内置了依赖图解析和可视化工具，帮助你理解容器内的服务关系。

### 1.1 打印 Scope Tree

输出容器的分层结构，包括每层注册了哪些服务及其状态。

```go
injector := do.New()
// ... 注册服务 ...
injector.ExplainScopeTree()

// 输出示例：
// Scope ID: 35d18a30-...
//  Scope name: [root]
//  DAG:
//   |
//    \_ [root] (ID: 35d18a30-...)
//        * 😴 PostgreSQLClientService 🫀 🙅
//        * 😴 RedisClientService 🫀 🙅
//        * 🔁 Config
//        * 🔗 Logger
//        |
//        |\_ api (ID: dce6f365-...)
//        |    |
//        |    |\_ public-api (ID: b9cac0c2-...)
//        |    |    * 😴 PublicApiRouterService
//        |    |
//        |    \_ internal-api (ID: a9e3adfc-...)
//        |        * 😴 InternalApiRouterService
//        |
//        \_ jobs (ID: 53406825-...)
//            * 😴 StatisticsJobService
```

**Emoji 含义：**

| Emoji | 含义 |
|-------|------|
| 😴 | 懒加载服务（Lazy） |
| 🔁 | 预加载服务（Eager） |
| 🏭 | 瞬态服务（Transient） |
| 🔗 | 服务别名（Alias） |
| 🫀 | 实现了 Healthchecker |
| 🙅 | 实现了 Shutdowner |

### 1.2 打印 Service Dependencies

查看指定服务的完整依赖链。

```go
injector.ExplainService("*main.UserControllerService")

// 输出：
// UserControllerService
//   ├── UserService
//   │   ├── UserRepository
//   │   │   └── Config
//   │   └── Logger
//   └── Router
```

### 1.3 循环依赖检测

容器在运行时自动检测循环依赖。存在循环依赖时，`do.Invoke` 返回错误：

```go
// 假如 A → B → C → A 构成循环
_, err := do.Invoke[*ServiceA](injector)
// err: "DI: circular dependency detected: ServiceA → ServiceB → ServiceC → ServiceA"
```

---

## 二、Web UI 可视化

samber/do 提供了 Web UI 页面，以图形化方式展示 Scope Tree 和 Service Dependencies。

::: danger 安全警告
不要在生产环境中公开暴露调试 Web UI。它暴露了内部 DI 图信息（服务名、依赖关系等）。使用身份认证中间件和/或网络限制（IP 白名单、VPN）保护路由。
:::

### 2.1 标准库 net/http

```bash
go get github.com/samber/do/http/std/v2
```

```go
import "github.com/samber/do/http/std/v2"

injector := startProgram()
mux := http.NewServeMux()

// 挂载调试路由前先应用认证中间件
mux.Handle("/debug/do/", std.Use("/debug/do", injector))

http.ListenAndServe(":8080", mux)
```

### 2.2 Gin

```bash
go get github.com/samber/do/http/gin/v2
```

```go
import ginhttp "github.com/samber/do/http/gin/v2"

injector := startProgram()
router := gin.New()

// 先对路由组附加认证中间件，再挂载调试处理器
ginhttp.Use(router.Group("/debug/do"), injector)

router.Run(":8080")
```

### 2.3 Fiber

```bash
go get github.com/samber/do/http/fiber/v2
```

```go
import fiberhttp "github.com/samber/do/http/fiber/v2"

injector := startProgram()
router := fiber.New()

fiberhttp.Use(router.Group("/debug/do"), "/debug/do", injector)

router.Listen(":8080")
```

### 2.4 Echo

```bash
go get github.com/samber/do/http/echo/v2
```

```go
import echohttp "github.com/samber/do/http/echo/v2"

injector := startProgram()
router := echo.New()

echohttp.Use(router.Group("/debug/do"), "/debug/do", injector)

router.Start(":8080")
```

### 2.5 Chi

```bash
go get github.com/samber/do/http/chi/v2
```

```go
import chihttp "github.com/samber/do/http/chi/v2"

injector := startProgram()
router := chi.NewRouter()

chihttp.Use(router, "/debug/do", injector)

http.ListenAndServe(":8080", router)
```

---

## 三、框架对比与迁移指南

以下提供快速对比，完整的迁移步骤请参考官方文档。

### 3.1 samber/do vs Google Wire vs Uber Dig

| 维度 | samber/do | Google Wire | Uber Dig |
|------|-----------|-------------|----------|
| 原理 | 泛型（编译时类型安全） | 代码生成 | 反射 |
| 额外构建步骤 | 无 | 需要 `wire` 命令 | 无 |
| 生命周期管理 | 健康检查 + 优雅关闭 | 有限 | 有限 |
| 作用域 | 内建 Scope Tree | 无 | 无 |
| 调试工具 | Web UI + 打印 | 无 | 无 |
| Provider 签名 | `func(Injector) (T, error)` | `func(...) (T, error)` 无 Injector | `func(...) (T, error)` 无 Injector |

### 3.2 从 Google Wire 迁移

核心变化：
- 移除 `//go:build wireinject` 标记
- 将 Provider 签名改为 `func(do.Injector) (T, error)`
- 用 `do.Provide` + `do.MustInvoke` 替换 `wire.Build`

完整迁移指南：[官方文档 — 从 Google Wire 迁移](https://do.samber.dev/docs/migrating/migrating-from-wire)

### 3.3 从 Uber Dig 迁移

核心变化：
- 将 `container.Provide(func(...) (T, error))` 改为 `do.Provide(injector, func(do.Injector) (T, error))`
- 将 `container.Invoke(func(svc T))` 改为 `svc := do.MustInvoke[T](injector)`
- 用 `do.InvokeAs[T]()` 替换通过 interface 调用

完整迁移指南：[官方文档 — 从 Uber Dig 迁移](https://do.samber.dev/docs/migrating/migrating-from-dig)

### 3.4 从 v1.x 升级到 v2

| 变化项 | v1.x | v2 |
|--------|------|----|
| `do.Injector` | 结构体 | 接口 |
| 函数参数 | `*do.Injector` | `do.Injector` |
| `ShutdownOnSignals` | 返回 `error` | 返回 `(os.Signal, *ShutdownReport)` |
| `Shutdown()` | 阻塞，返回 `error` | 非阻塞，返回 `map[string]error` |
| 内部服务名 | 不含包路径 | 包含包路径（消除重名冲突） |
| Hooks | 单个回调 | 切片回调，可注册多个 |

完整升级指南：[官方文档 — 从 v1.x 升级到 v2](https://do.samber.dev/docs/upgrading/from-v1-x-to-v2)

---

## 四、已知限制与注意事项

### 4.1 InvokeStruct 反射性能

`do.InvokeStruct` 依赖 Go 的 `reflect` 包在运行时解析 struct tag，性能比手动注入低一个数量级。不推荐在以下场景使用：

- 性能关键路径
- Serverless 函数（冷启动时间敏感）
- 高频调用的瞬时服务

**建议替代方案**：在 Provider 中手动注入依赖。

```go
// ❌ 反射方式（InvokeStruct）
do.Provide(injector, do.InvokeStruct[MyService])

// ✅ 手动注入（性能更好）
do.Provide(injector, func(i do.Injector) (*MyService, error) {
    return &MyService{
        Logger: do.MustInvoke[*logrus.Logger](i),
        DB:     do.MustInvoke[*sql.DB](i),
    }, nil
})
```

### 4.2 循环依赖限制

samber/do 不支持循环依赖。服务依赖关系必须构成有向无环图（DAG）。

**解决方案：**

1. 重构设计，将循环依赖拆解为单向依赖
2. 引入中间层（如事件总线、回调接口）

### 4.3 隐式别名绑定歧义

当使用 `do.InvokeAs[T]()` 且接口签名过于通用（如 `interface{}`、`fmt.Stringer`）时，容器可能匹配到错误的服务。

**建议**：对于简单接口，优先使用显式名称或命名注册来消除歧义。

```go
// 可能匹配到多个服务，导致不确定行为
svc := do.MustInvokeAs[any](injector)

// ✅ 更明确的做法：使用命名服务或具体类型
svc := do.MustInvoke[*MySpecificService](injector)
```

### 4.4 其他注意事项

| 限制                                      | 说明                                                                                                                                          |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `do.Eager` 与 `do.Lazy` 参数类型不同           | `do.Lazy` 接受构造函数（Provider），`do.Eager` 接受已创建的值。在 Package 中混用时极易将构造函数误传入 Eager，导致容器注册 func 类型而非目标类型，Invoke 时收到 `(*T)(nil)` 或报错找不到服务           |
| `InvokeStruct` 不支持嵌套结构体                 | struct tag 只作用于直接字段，不会递归处理嵌套字段                                                                                                              |
| Override 不能处理已实例化的服务                    | 如果一个懒加载服务已经被调用过，Override 不会替换其已创建的实例                                                                                                        |
| 全局容器禁止生产使用                              | `do.Provide(nil, ...)` 违背依赖反转原则                                                                                                             |
| `Shutdown` 不等于释放 GC 引用                  | `Shutdown()` 调用的是服务上的清理方法（关闭连接、刷盘），但 injector 内部的 map 引用不会被清除。要真正让服务被 GC，必须让 injector 本身离开作用域。                                              |
| Transient Provider 内禁止调用 `i.Scope(...)` | Transient 内部使用 `virtualScope` 包裹真实 scope，`i.Scope(name)` 透传到底层真实 scope。第二次 Invoke 时同名子作用域已存在 → `DI: scope "name" has already been declared` |

::: danger Transient + Scope 组合陷阱

**根因分析**

samber/do 的 Transient 服务在每次 Invoke 时会创建一个 `virtualScope`（内部类型）来包裹真实的底层 scope，用于追踪依赖图。当 Provider 函数内调用 `i.Scope("name")` 时：

1. `virtualScope.Scope("name")` 透传到底层真实 scope
2. 真实 scope 创建名为 "name" 的子作用域
3. 第二次 Invoke Transient 服务时，**新的** `virtualScope` 被创建，但仍透传到**同一个**真实 scope
4. 真实 scope 检测到 "name" 子作用域已存在 → panic

**复现代码**

```go
type IMyService interface{}
type MyService struct{}

func NewMyServiceWithScope(i do.Injector) (IMyService, error) {
    // 第二次 Invoke 时这里会 panic:
    // "DI: scope `myservice` has already been declared"
    _ = i.Scope("myservice")
    return &MyService{}, nil
}

func TestTransientWithScope(t *testing.T) {
    injector := do.New(
        do.TransientNamed("service", NewMyServiceWithScope),
    )

    inst1 := do.MustInvokeNamed[IMyService](injector, "service") // ✓ 首次成功
    _ = inst1

    // ✗ 第二次 Invoke 触发 NewMyServiceWithScope → i.Scope("myservice")
    // → scope "myservice" 已存在 → panic
    _, err := do.InvokeNamed[IMyService](injector, "service")
    if err != nil {
        t.Logf("预期中的 panic 已捕获: %v", err)
    }
}
```

**修复方案**

| 方案 | 做法 | 适用场景 |
|------|------|---------|
| **优先避免** | 不在 Transient Provider 内部创建子作用域 | 所有 Transient 服务 |
| **父作用域预先创建** | 在父作用域中预先创建子作用域，Transient Provider 内直接注册服务 | 必须使用 Scope 隔离的场景 |
| **改用 Lazy** | 若必须使用 Scope，改用 Lazy 加载（单例），自行管理生命周期 | Provider 内部副作用少的场景 |
| **移除死代码** | 检查 Provider 内创建的 Scope 是否真的被使用（如 Leader.injector 从未被读），直接删除 | Legacy 代码清理 |
:::

---

### 4.5 GC 与容器生命周期

#### 为什么 Shutdown 后内存不释放？

samber/do 容器内部使用 `map[string]any` 存储所有已实例化的服务。`Shutdown()` 只调用每个服务上的 `Shutdown()` 方法做**资源清理**（关闭连接、刷盘等），不会从 map 中删除条目。

```go
injector := do.New()
do.Provide(injector, NewBigService)       // 注册 100MB 的服务
big := do.MustInvoke[*BigService](injector) // 实例化

injector.Shutdown()                        // 调用 BigService.Shutdown()
                                           // 但 injector 仍然持有 *BigService 的引用

// GC 无法回收 *BigService
// 只有在 injector 离开作用域时，整个 map 才会被回收
injector = nil // ← 此时 *BigService 不再被任何根引用持有，可被 GC
```

#### 三种注册方式的 GC 行为对比

| 注册方式 | 容器持有对象 | 实例是否被容器引用 | GC 可达性 |
|----------|-------------|-------------------|-----------|
| `Provide`（Lazy 懒加载） | Provider + **首次创建的实例**（单例） | **是** — 实例存入 `map[string]any` | 只要 injector 存活，实例永不被 GC |
| `ProvideValue`（Eager 预加载） | **直接存值** — 值本身就是实例 | **是** — 值存入 `map[string]any` | 只要 injector 存活，值永不被 GC |
| `ProvideTransient`（Transient 瞬态） | **仅 Provider（构造函数）** | **否** — 每次 Invoke 新建实例直接返回给调用方 | 调用方变量离开作用域后即可被 GC |

```go
// Transient：容器不做缓存，每次新建
func runBatch() {
    for i := 0; i < 100; i++ {
        svc := do.MustInvoke[*MyService](injector)
        svc.DoWork()
        // svc 在循环迭代结束后无引用 → 可被 GC
    }
}

// Lazy：容器缓存实例，函数返回后仍不可 GC
func runBatch() {
    svc := do.MustInvoke[*MyService](injector)
    svc.DoWork()
} // svc 变量消失，但 injector 内部仍持有引用 → 不可 GC
```

#### Shutdown 真正做了什么

| 操作 | 效果 |
|------|------|
| `do.Shutdown[T](i)` | 调用该服务的 Shutdown 方法，清理资源；懒加载服务可被重新 Invoke |
| `injector.Shutdown()` | 遍历所有 Shutdowner，按逆初始化顺序调用清理方法；容器标记为关闭，后续无法 Invoke |
| `injector.Clone()` | 创建新容器，共享注册表但服务实例独立。**原容器丢弃后，其内的服务可被 GC** |

#### 精准控制服务生命周期的推荐模式

```go
func ProcessBatch() {
    // 为每个批次创建独立 Scope
    batchScope := globalInjector.Scope("batch-xxx")
    defer batchScope.Shutdown() // 批次结束，清理 scope 内的资源

    // 在此 Scope 中注册一次性服务
    do.Provide(batchScope, NewTempConnection)
    conn := do.MustInvoke[*TempConnection](batchScope)
    // ...
    // defer batchScope.Shutdown() 触发时，TempConnection 被 Shutdown
    // 函数返回后，batchScope 离开作用域，GC 可回收
}
```

::: tip
使用 Scope 隔离生命周期，在 Scope 销毁时连带释放其管理的所有服务引用，是实现精细化 GC 控制的最佳模式。
:::

---

## 参考链接

- [官方文档 — About](https://do.samber.dev/docs/about)
- [官方文档 — Troubleshooting](https://do.samber.dev/docs/troubleshooting/scope-tree)
- [官方文档 — Web UI](https://do.samber.dev/docs/troubleshooting/web-ui)
- [官方文档 — Migrating from Wire](https://do.samber.dev/docs/migrating/migrating-from-wire)
- [官方文档 — Migrating from Dig](https://do.samber.dev/docs/migrating/migrating-from-dig)
- [官方文档 — Upgrading from v1.x to v2](https://do.samber.dev/docs/upgrading/from-v1-x-to-v2)
- [GitHub 仓库](https://github.com/samber/do)
