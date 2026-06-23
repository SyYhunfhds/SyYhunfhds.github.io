---
title: samber/do 依赖注入框架核心指南
date: 2026-06-23
author: Deepseek V4 Flash (Trae SOLO Mode)
footer: Trae编辑
---

# samber/do 依赖注入框架核心指南

## 概述

`samber/do` 是基于 Go 1.18+ 泛型的依赖注入（DI）工具包。设计目标是作为 `uber/dig` 和 `google/wire` 的现代替代品。

**核心优势：**

| 维度 | samber/do | uber/dig | google/wire |
|------|-----------|----------|-------------|
| 类型安全 | 泛型编译期安全 | 反射运行时安全 | 代码生成编译期安全 |
| 代码生成 | 不需要 | 不需要 | 需要 `wire` 命令 |
| 外部依赖 | 零依赖 | 依赖 `go.uber.org/dig` | 零依赖 |
| 生命周期管理 | 健康检查 + 优雅关闭 | 有限 | 有限 |
| 作用域 | 内建 Scope Tree | 无 | 无 |
| 调试工具 | Web UI + Scope Tree 打印 | 无 | 无 |

### 作者生态

`samber/do` 作者 Samuel Berthe 在 Go 社区以泛型工具库闻名：

- `samber/lo` — Go 版 Lodash 泛型工具库
- `samber/mo` — Go 版 Monads（Option、Result、Either）
- `samber/do` — 依赖注入框架

## 核心概念

```go
// Injector：DI 容器接口，所有操作的入口
type Injector interface { /* ... */ }

// Provider[T]：服务构造函数
type Provider[T any] func(Injector) (T, error)
```

**三个原则：**

1. 服务通过 `Provider[T]` 注册到容器
2. 服务通过 `do.Invoke[T]()` 按需加载（默认懒加载）
3. 服务间依赖在 Provider 中声明，由容器自动递归解析

## 安装

```bash
go get github.com/samber/do/v2
```

::: warning 版本说明
务必使用 v2 版本，v1 已不再维护。v2 将 `do.Injector` 改为接口类型，签名与 v1 不兼容。
:::

## 一、创建容器

### 默认容器

```go
import "github.com/samber/do/v2"

injector := do.New()
```

### 自定义选项

```go
injector := do.NewWithOpts(&do.InjectorOpts{
    HealthCheckParallelism:   10,
    HealthCheckGlobalTimeout: 5 * time.Second,
    HealthCheckTimeout:       500 * time.Millisecond,
    StructTagKey:             "di", // 默认 "do"
})
```

## 二、服务注册

### 2.1 懒加载（Lazy，默认）

服务在第一次被调用时才实例化，全局唯一单例。

```go
type MyService struct {
    Hello string
}

func NewMyService(i do.Injector) (*MyService, error) {
    return &MyService{Hello: "world"}, nil
}

do.Provide(injector, NewMyService)
```

### 2.2 预加载（Eager）

容器创建后立即实例化，适合需要在启动阶段完成初始化的服务（如数据库连接池预热）。

```go
do.Provide(injector, do.Eager[*MyService](NewMyService))
```

### 2.3 瞬态加载（Transient）

每次调用都创建新实例。

```go
do.ProvideTransient(injector, func(i do.Injector) (*Logger, error) {
    return &Logger{RequestID: uuid.New()}, nil
})
```

### 2.4 值注册（Value）

直接注册已创建好的值，省去构造步骤。

```go
do.ProvideValue(injector, &Config{
    Port: 8080,
    Env:  "production",
})
```

### 2.5 命名注册（Named）

注册同一类型的多个实例。

```go
do.ProvideNamed(injector, "front-left", NewWheel)
do.ProvideNamed(injector, "front-right", NewWheel)
do.ProvideNamed(injector, "back-left", NewWheel)
do.ProvideNamed(injector, "back-right", NewWheel)
```

### 2.6 覆盖注册（Override）

测试时替换真实服务为 Mock 实现。

```go
// Setup：注册真实服务
do.Provide(injector, NewRealDatabase)

// SetupTest：替换为 Mock
do.Override(injector, NewMockDatabase)
```

::: warning
`Override` 仅在测试场景推荐使用，生产环境请使用接口别名（Interface Aliasing）。
:::

### 2.7 包批量注册（Package）

将多个服务打包为一个 `do.Package`，在入口一次性导入。

```go
// pkg/car/package.go
var CarPackage = do.Package(
    do.Lazy(NewCar),
    do.Lazy(NewEngine),
    do.LazyNamed("front-left", NewWheel),
    do.LazyNamed("front-right", NewWheel),
    do.LazyNamed("back-left", NewWheel),
    do.LazyNamed("back-right", NewWheel),
)
```

```go
// cmd/main.go
injector := do.New(car.CarPackage)
do.ProvideValue(injector, &Config{Port: 4242})
```

## 三、服务调用

### 3.1 基本调用

```go
// 返回 error
svc, err := do.Invoke[*MyService](injector)

// 失败则 panic
svc := do.MustInvoke[*MyService](injector)
```

### 3.2 命名调用

```go
wheel := do.MustInvokeNamed[*Wheel](injector, "front-left")
```

### 3.3 自动结构体注入（InvokeStruct）

通过 struct tag 自动注入依赖字段。

```go
type MyService struct {
    Logger  *logrus.Logger `do:""`
    DB      *sql.DB        `do:""`
    Port    int            `do:"config.port"`
}

// 方式一：在 Provider 中调用
do.Provide(injector, func(i do.Injector) (*MyService, error) {
    return do.InvokeStruct[MyService](i)
})

// 方式二：直接用 InvokeStruct 作为 Provider
do.Provide(injector, do.InvokeStruct[MyService])
```

tag 规则：

| tag 值 | 行为 |
|--------|------|
| `` `do:""` `` | 按类型自动查找服务 |
| `` `do:"service.name"` `` | 按名称查找服务 |
| 无 tag | 不注入 |

::: warning
`InvokeStruct` 依赖反射，不推荐在性能敏感路径或 Serverless 环境中使用。
:::

## 四、接口别名绑定

### 4.1 隐式别名（推荐）

注册具体类型，调用时按接口自动匹配。

```go
type Metric interface {
    Inc()
}

type RequestPerSecond struct {
    counter int
}

func (r *RequestPerSecond) Inc() { r.counter++ }

// 注册具体类型
do.Provide(injector, func(i do.Injector) (*RequestPerSecond, error) {
    return &RequestPerSecond{}, nil
})

// 按接口调用（隐式匹配）
metric := do.MustInvokeAs[Metric](injector)
metric.Inc()
```

### 4.2 显式别名

适用于需要为同一实现绑定多个接口的遗留代码场景。

```go
do.Provide(injector, func(i do.Injector) (*RequestPerSecond, error) {
    return &RequestPerSecond{}, nil
})

err := do.As[*RequestPerSecond, Metric](injector)
```

::: danger
显式别名可能导致脆弱的设计，谨慎使用。
:::

## 五、作用域树（Scope Tree）

作用域将服务按模块分组，子作用域可访问父作用域的服务。

### 创建作用域

```go
root := do.New()
apiModule := root.Scope("api")
jobModule := root.Scope("jobs")
```

### 作用域隔离

```go
// 注册到根作用域
do.Provide(root, NewEngine)

// 注册到子作用域
do.Provide(apiModule, func(i do.Injector) (*SteeringWheel, error) {
    // 可以访问根作用域的 *Engine
    engine := do.MustInvoke[*Engine](i)
    return &SteeringWheel{Engine: engine}, nil
})

// 调用时从子作用域开始查找，逐级向上
wheel := do.MustInvoke[*SteeringWheel](apiModule)
```

::: tip 作用域嵌套
Scope 可以多层嵌套：`root.Scope("api").Scope("v1").Scope("public")`。查找顺序为当前 scope → 父 scope → 直到 root。
:::

## 六、服务生命周期

### 6.1 健康检查

服务实现 `Healthchecker` 接口即可被检测。

```go
var _ do.HealthcheckerWithContext = (*MyPostgreSQLConnection)(nil)

type MyPostgreSQLConnection struct {
    DB *sql.DB
}

func (pg *MyPostgreSQLConnection) HealthCheck(ctx context.Context) error {
    return pg.DB.PingContext(ctx)
}

// 全局检查
status := injector.HealthCheckWithContext(ctx)
for serviceName, err := range status {
    if err != nil {
        log.Printf("Service %s is unhealthy: %v", serviceName, err)
    }
}

// 单个服务检查
err := do.HealthCheck[*MyPostgreSQLConnection](injector)
```

支持接口：

| 接口 | 方法签名 |
|------|----------|
| `Healthchecker` | `HealthCheck() error` |
| `HealthcheckerWithContext` | `HealthCheck(context.Context) error` |

### 6.2 优雅关闭

服务实现 `Shutdowner` 接口即可在应用退出时清理资源。关闭顺序按逆初始化顺序执行。

```go
var _ do.ShutdownerWithContextAndError = (*MyPostgreSQLConnection)(nil)

func (pg *MyPostgreSQLConnection) Shutdown(ctx context.Context) error {
    return pg.DB.Close()
}

// 手动触发关闭
report := injector.ShutdownWithContext(ctx)

// 监听信号自动关闭
signal, report := injector.ShutdownOnSignals(syscall.SIGTERM, os.Interrupt)
```

支持接口：

| 接口 | 方法签名 |
|------|----------|
| `Shutdowner` | `Shutdown()` |
| `ShutdownerWithError` | `Shutdown() error` |
| `ShutdownerWithContext` | `Shutdown(context.Context)` |
| `ShutdownerWithContextAndError` | `Shutdown(context.Context) error` |

### 6.3 生命周期钩子

```go
injector := do.NewWithOpts(&do.InjectorOpts{
    HookAfterRegistration: []func(scope *do.Scope, serviceName string){
        func(scope *do.Scope, serviceName string) {
            slog.Debug("[DI] Registered " + serviceName)
        },
    },
    HookBeforeShutdown: []func(scope *do.Scope, serviceName string){
        func(scope *do.Scope, serviceName string) {
            slog.Debug("[DI] Shutting down " + serviceName)
        },
    },
})
```

也可以在运行时动态添加钩子：

```go
injector.AddBeforeShutdownHook(func(scope *do.Scope, serviceName string) {
    slog.Debug("[DI] Shutting down " + serviceName)
})
```

## 七、容器管理

### 7.1 容器克隆

克隆拥有相同的服务注册表，但不共享已实例化的状态。适合测试场景。

```go
injector = injector.Clone()
// 或替换部分服务
injector = injector.CloneWithOpts(&do.InjectorOpts{
    StructTagKey: "di",
})
do.Override(injector, NewMockEngine)
```

### 7.2 全局容器（不推荐）

```go
// 传递 nil 自动使用全局容器
do.Provide(nil, NewMyService)
svc := do.MustInvoke[*MyService](nil)
```

::: danger
全局容器违背 DI 原则，仅在快速原型中临时使用，生产环境禁止。
:::

## 八、完整实战：三层架构 Web 服务

```go
// ========================================
// 1. 定义领域类型与接口
// ========================================
type User struct {
    ID   int64
    Name string
}

type UserRepository interface {
    FindByID(id int64) (*User, error)
}

type UserService interface {
    GetUser(id int64) (*User, error)
}

// ========================================
// 2. 实现 Repository
// ========================================
type PostgresUserRepository struct {
    db *sql.DB
}

func NewPostgresUserRepository(i do.Injector) (*PostgresUserRepository, error) {
    cfg := do.MustInvoke[*Config](i)
    db, err := sql.Open("postgres", cfg.DatabaseURL)
    if err != nil {
        return nil, err
    }
    return &PostgresUserRepository{db: db}, nil
}

func (r *PostgresUserRepository) FindByID(id int64) (*User, error) {
    // ...
    return &User{ID: id, Name: "Alice"}, nil
}

// ========================================
// 3. 实现 Service
// ========================================
type userServiceImpl struct {
    repo UserRepository
}

func NewUserService(i do.Injector) (*userServiceImpl, error) {
    repo := do.MustInvoke[UserRepository](i)
    return &userServiceImpl{repo: repo}, nil
}

func (s *userServiceImpl) GetUser(id int64) (*User, error) {
    return s.repo.FindByID(id)
}

// ========================================
// 4. 实现 Controller（注册时绑定接口别名）
// ========================================
type UserController struct {
    svc UserService
}

func NewUserController(i do.Injector) (*UserController, error) {
    svc := do.MustInvoke[UserService](i)
    return &UserController{svc: svc}, nil
}

func (c *UserController) HandleGetUser(w http.ResponseWriter, r *http.Request) {
    // ...
}

// ========================================
// 5. 组合根（Composition Root）
// ========================================
func main() {
    injector := do.New()

    // Config
    do.ProvideValue(injector, &Config{
        Port:        8080,
        DatabaseURL: "postgres://localhost:5432/mydb",
    })

    // Repository（注册具体类型）
    do.Provide(injector, NewPostgresUserRepository)
    do.MustAs[*PostgresUserRepository, UserRepository](injector) // 绑定接口别名

    // Service（通过接口调用 Repository）
    do.Provide(injector, NewUserService)
    do.MustAs[*userServiceImpl, UserService](injector)

    // Controller
    do.Provide(injector, NewUserController)

    // 启动 HTTP 服务
    ctrl := do.MustInvoke[*UserController](injector)
    http.HandleFunc("/users/", ctrl.HandleGetUser)

    // 优雅退出
    injector.ShutdownOnSignals(syscall.SIGTERM, os.Interrupt)
}
```

## 参考链接

- [官方文档](https://do.samber.dev/)
- [GitHub 仓库](https://github.com/samber/do)
- [pkg.go.dev](https://pkg.go.dev/github.com/samber/do/v2)
