---
title: Go Zap 日志库使用指南
date: 2026-05-08
footer: Trae编辑
---

# Go Zap 日志库使用指南

## 概述

`go.uber.org/zap` 是 Uber 开源的一款高性能结构化日志库,专为对性能和可靠性有严苛要求的 Golang 应用设计。与标准库 `log` 及其他日志库相比,zap 通过预分配内存、避免反射、优化字段编码等方式,实现了极致的性能表现,同时提供丰富的结构化日志能力。

::: info 核心优势

- **极致高性能**:在吞吐率和延迟上远超同类库,无反射开销,适合高并发、低延迟场景
- **结构化日志**:原生支持 JSON 等结构化格式,便于日志分析工具解析
- **灵活可配置**:支持自定义日志级别、输出路径、编码格式、采样策略
- **分级日志**:提供完整的日志级别支持,支持按级别过滤日志
- **安全可靠**:避免并发写冲突,崩溃时可保证日志不丢失

:::

## 核心特性

### 性能优势

Zap 采用了独特的设计理念来实现极致性能:

- **零分配 JSON 编码器**:避免反射,使用预定义的类型编码器
- **内存池技术**:减少内存分配次数,降低 GC 压力
- **并发安全**:所有方法都是并发安全的,无需额外同步
- **类型安全**:强类型字段系统,编译时检查类型错误

### 两种 Logger 类型

Zap 提供两种 Logger 以满足不同场景需求:

#### 1. Logger (高性能、强类型)

适用于性能关键路径,需要显式指定字段类型:

```go
logger, _ := zap.NewProduction()
defer logger.Sync()

logger.Info("failed to fetch URL",
    zap.String("url", "http://example.org"),
    zap.Int("attempt", 3),
    zap.Duration("backoff", time.Second),
)
```

#### 2. SugaredLogger (易用性、弱类型)

适用于非热点代码,语法更简洁:

```go
logger, _ := zap.NewProduction()
defer logger.Sync()
sugar := logger.Sugar()

sugar.Infow("failed to fetch URL",
    "url", "http://example.org",
    "attempt", 3,
    "backoff", time.Second,
)

sugar.Infof("Failed to fetch URL: %s", "http://example.org")
```

::: tip 性能对比

- `Logger`: 性能最优,零分配,适合热点路径
- `SugaredLogger`: 性能比 Logger 低约 50%,但仍比其他日志库快 4-10 倍

:::

## 安装

使用 `go get` 安装最新版本:

```bash
go get -u go.uber.org/zap
```

验证安装:

```bash
grep "go.uber.org/zap" go.mod
```

## 快速开始

### 预设配置

Zap 提供三种预设配置,开箱即用:

#### 1. 生产环境配置

```go
package main

import (
    "go.uber.org/zap"
)

func main() {
    logger, err := zap.NewProduction()
    if err != nil {
        panic(err)
    }
    defer logger.Sync()

    logger.Info("production log demo",
        zap.String("service", "user-service"),
        zap.Int("port", 8080),
        zap.Bool("enable_tls", true),
    )
}
```

输出示例(JSON 格式):

```json
{
  "level": "info",
  "ts": 1715123456.789,
  "caller": "main.go:13",
  "msg": "production log demo",
  "service": "user-service",
  "port": 8080,
  "enable_tls": true
}
```

#### 2. 开发环境配置

```go
package main

import (
    "go.uber.org/zap"
)

func main() {
    logger, err := zap.NewDevelopment()
    if err != nil {
        panic(err)
    }
    defer logger.Sync()

    logger.Debug("development log demo",
        zap.String("env", "dev"),
        zap.Int("debug_port", 6060),
    )
}
```

输出示例(控制台格式):

```
2026-05-08T10:30:45.123+0800	DEBUG	main.go:13	development log demo	{"env": "dev", "debug_port": 6060}
```

#### 3. 示例配置

```go
logger := zap.NewExample()
logger.Info("example log")
```

::: warning 配置选择

- **NewProduction**: 生产环境,JSON 格式,Info 级别及以上
- **NewDevelopment**: 开发环境,Console 格式,Debug 级别及以上,带颜色高亮
- **NewExample**: 测试示例,JSON 格式,Debug 级别,省略时间戳

:::

## 日志级别

Zap 支持以下日志级别(从低到高):

| 级别 | 数值 | 用途 |
|------|------|------|
| Debug | -1 | 调试信息,仅在开发环境启用 |
| Info | 0 | 常规信息,记录关键事件 |
| Warn | 1 | 警告信息,潜在问题 |
| Error | 2 | 错误信息,需要关注的错误 |
| DPanic | 3 | 开发环境 panic,生产环境当作 Error |
| Panic | 4 | 记录后 panic |
| Fatal | 5 | 记录后调用 os.Exit(1) |

### 动态调整日志级别

```go
package main

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func main() {
    atomicLevel := zap.NewAtomicLevelAt(zapcore.InfoLevel)

    config := zap.Config{
        Level:            atomicLevel,
        Development:      false,
        Encoding:         "json",
        EncoderConfig:    zap.NewProductionEncoderConfig(),
        OutputPaths:      []string{"stdout"},
        ErrorOutputPaths: []string{"stderr"},
    }

    logger, err := config.Build()
    if err != nil {
        panic(err)
    }
    defer logger.Sync()

    logger.Debug("this won't be logged")
    logger.Info("this will be logged")

    atomicLevel.SetLevel(zapcore.DebugLevel)
    logger.Debug("now debug logs are visible")
}
```

## 字段类型

Zap 为 Go 语言的所有基本类型和常见类型提供了字段构造方法:

### 基本类型

```go
logger.Info("user action",
    zap.Bool("is_admin", true),
    zap.Int("user_id", 12345),
    zap.Int64("timestamp", 1715123456),
    zap.Float64("score", 98.5),
    zap.String("username", "john_doe"),
)
```

### 指针类型

```go
userID := 12345
logger.Info("pointer fields",
    zap.Intp("user_id", &userID),
    zap.Stringp("nickname", nil),
)
```

### 切片类型

```go
tags := []string{"golang", "zap", "logging"}
ids := []int{1, 2, 3, 4, 5}
logger.Info("slice fields",
    zap.Strings("tags", tags),
    zap.Ints("ids", ids),
)
```

### 复杂类型

```go
logger.Info("complex fields",
    zap.Time("created_at", time.Now()),
    zap.Duration("elapsed", 2*time.Second),
    zap.Error(errors.New("connection timeout")),
    zap.Any("metadata", map[string]interface{}{
        "region": "us-west",
        "version": "1.0.0",
    }),
)
```

::: details 字段命名规则

- `zap.Type()`: 基本类型字段
- `zap.Typep()`: 指针类型字段
- `zap.Types()`: 切片类型字段
- `zap.Any()`: 任意类型字段(使用反射,性能较低)

:::

## 高级配置

### 自定义配置

```go
package main

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func main() {
    config := zap.Config{
        Level:       zap.NewAtomicLevelAt(zapcore.InfoLevel),
        Development: false,
        Sampling: &zap.SamplingConfig{
            Initial:    100,
            Thereafter: 100,
        },
        Encoding: "json",
        EncoderConfig: zapcore.EncoderConfig{
            TimeKey:        "ts",
            LevelKey:       "level",
            NameKey:        "logger",
            CallerKey:      "caller",
            MessageKey:     "msg",
            StacktraceKey:  "stacktrace",
            LineEnding:     zapcore.DefaultLineEnding,
            EncodeLevel:    zapcore.LowercaseLevelEncoder,
            EncodeTime:     zapcore.ISO8601TimeEncoder,
            EncodeDuration: zapcore.SecondsDurationEncoder,
            EncodeCaller:   zapcore.ShortCallerEncoder,
        },
        OutputPaths:      []string{"stdout", "/var/log/app.log"},
        ErrorOutputPaths: []string{"stderr"},
        InitialFields: map[string]interface{}{
            "service": "my-app",
            "version": "1.0.0",
        },
    }

    logger, err := config.Build()
    if err != nil {
        panic(err)
    }
    defer logger.Sync()

    logger.Info("custom logger configured")
}
```

### 日志轮转

使用 `lumberjack` 实现日志轮转:

```bash
go get gopkg.in/natefinch/lumberjack.v2
```

```go
package main

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
    "gopkg.in/natefinch/lumberjack.v2"
)

func main() {
    writer := &lumberjack.Logger{
        Filename:   "/var/log/myapp/app.log",
        MaxSize:    100,
        MaxBackups: 3,
        MaxAge:     28,
        Compress:   true,
    }

    core := zapcore.NewCore(
        zapcore.NewJSONEncoder(zap.NewProductionEncoderConfig()),
        zapcore.AddSync(writer),
        zapcore.InfoLevel,
    )

    logger := zap.New(core, zap.AddCaller())
    defer logger.Sync()

    logger.Info("log rotation configured")
}
```

### 多输出目标

```go
package main

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
    "os"
)

func main() {
    consoleEncoder := zapcore.NewConsoleEncoder(zap.NewDevelopmentEncoderConfig())
    jsonEncoder := zapcore.NewJSONEncoder(zap.NewProductionEncoderConfig())

    core := zapcore.NewTee(
        zapcore.NewCore(consoleEncoder, zapcore.AddSync(os.Stdout), zapcore.DebugLevel),
        zapcore.NewCore(jsonEncoder, zapcore.AddSync(os.Stderr), zapcore.InfoLevel),
    )

    logger := zap.New(core)
    defer logger.Sync()

    logger.Debug("only to console")
    logger.Info("to both console and stderr")
}
```

## 配置参数详解

Zap 的 `Config` 结构体提供了完整的配置能力,以下是所有配置参数的详细说明:

### Config 结构体完整字段

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `Level` | `AtomicLevel` | 最小启用日志级别,支持运行时动态修改 | `InfoLevel` |
| `Development` | `bool` | 开发模式,影响 DPanic 级别行为和栈追踪 | `false` |
| `DisableCaller` | `bool` | 禁用调用者信息(文件名和行号) | `false` |
| `DisableStacktrace` | `bool` | 完全禁用自动栈追踪捕获 | `false` |
| `Sampling` | `*SamplingConfig` | 采样策略配置,nil 表示禁用采样 | `nil` |
| `Encoding` | `string` | 编码格式,"json" 或 "console" | `"json"` |
| `EncoderConfig` | `EncoderConfig` | 编码器详细配置 | 见下文 |
| `OutputPaths` | `[]string` | 日志输出路径列表(文件路径或 URL) | `["stderr"]` |
| `ErrorOutputPaths` | `[]string` | 内部错误输出路径列表 | `["stderr"]` |
| `InitialFields` | `map[string]interface{}` | 初始字段,会添加到所有日志中 | `nil` |

### EncoderConfig 配置

`EncoderConfig` 是编码器的核心配置:

| 参数 | 类型 | 说明 | 默认值(生产环境) |
|------|------|------|-----------------|
| `MessageKey` | `string` | 消息字段的 key 名称 | `"msg"` |
| `LevelKey` | `string` | 日志级别字段的 key 名称 | `"level"` |
| `TimeKey` | `string` | 时间戳字段的 key 名称 | `"ts"` |
| `NameKey` | `string` | Logger 名称字段的 key 名称 | `"logger"` |
| `CallerKey` | `string` | 调用者信息字段的 key 名称 | `"caller"` |
| `FunctionKey` | `string` | 函数名字段 key(已废弃) | 空 |
| `StacktraceKey` | `string` | 栈追踪字段的 key 名称 | `"stacktrace"` |
| `LineEnding` | `string` | 行结束符 | `"\n"` |
| `EncodeLevel` | `LevelEncoder` | 级别编码器函数 | `LowercaseLevelEncoder` |
| `EncodeTime` | `TimeEncoder` | 时间编码器函数 | `EpochTimeEncoder` |
| `EncodeDuration` | `DurationEncoder` | 时长编码器函数 | `SecondsDurationEncoder` |
| `EncodeCaller` | `CallerEncoder` | 调用者编码器函数 | `ShortCallerEncoder` |

### SamplingConfig 采样配置

| 参数 | 类型 | 说明 |
|------|------|------|
| `Initial` | `int` | 每秒初始采样数量,之后进入节流 |
| `Thereafter` | `int` | 采样间隔,每 N 条日志采样 1 条 |
| `Hook` | `func(Entry, SamplingDecision)` | 采样决策回调函数 |

### 编码器函数详解

#### LevelEncoder 级别编码器

```go
zapcore.LowercaseLevelEncoder    // 小写: "info", "debug", "error"
zapcore.LowercaseColorLevelEncoder // 小写带颜色(开发环境)
zapcore.CapitalLevelEncoder      // 大写: "INFO", "DEBUG", "ERROR"
zapcore.CapitalColorLevelEncoder // 大写带颜色
```

#### TimeEncoder 时间编码器

```go
zapcore.EpochTimeEncoder        // Unix 时间戳(秒)
zapcore.EpochMillisTimeEncoder  // Unix 时间戳(毫秒)
zapcore.EpochNanosTimeEncoder  // Unix 时间戳(纳秒)
zapcore.ISO8601TimeEncoder     // ISO8601 格式
zapcore.RFC3339TimeEncoder      // RFC3339 格式
zapcore.RFC3339NanoTimeEncoder  // RFC3339 纳秒格式
```

#### DurationEncoder 时长编码器

```go
zapcore.SecondsDurationEncoder  // 秒为单位:"1.5s"
zapcore.NanosDurationEncoder    // 纳秒为单位
zapcore.MillisDurationEncoder   // 毫秒为单位
zapcore.StringDurationEncoder   // 字符串格式:"1.5s"
```

#### CallerEncoder 调用者编码器

```go
zapcore.ShortCallerEncoder  // 简短格式:"main.go:12"
zapcore.FullCallerEncoder   // 完整格式:"/path/to/file/main.go:12"
```

### 配置示例:完整生产环境配置

```go
package main

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func main() {
    config := zap.Config{
        Level:       zap.NewAtomicLevelAt(zapcore.InfoLevel),
        Development: false,
        DisableCaller: false,
        DisableStacktrace: false,
        Sampling: &zap.SamplingConfig{
            Initial:    100,
            Thereafter: 100,
        },
        Encoding: "json",
        EncoderConfig: zapcore.EncoderConfig{
            MessageKey:     "msg",
            LevelKey:       "level",
            TimeKey:        "ts",
            NameKey:        "logger",
            CallerKey:      "caller",
            StacktraceKey:  "stacktrace",
            LineEnding:     zapcore.DefaultLineEnding,
            EncodeLevel:    zapcore.LowercaseLevelEncoder,
            EncodeTime:     zapcore.ISO8601TimeEncoder,
            EncodeDuration: zapcore.StringDurationEncoder,
            EncodeCaller:   zapcore.ShortCallerEncoder,
        },
        OutputPaths:      []string{"stdout", "/var/log/app.log"},
        ErrorOutputPaths: []string{"stderr"},
        InitialFields: map[string]interface{}{
            "service": "my-app",
            "version":  "1.0.0",
            "env":      "production",
        },
    }

    logger, err := config.Build()
    if err != nil {
        panic(err)
    }
    defer logger.Sync()

    logger.Info("logger configured successfully")
}
```

### 配置示例:完整开发环境配置

```go
package main

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func main() {
    config := zap.Config{
        Level:       zap.NewAtomicLevelAt(zapcore.DebugLevel),
        Development: true,
        DisableCaller: false,
        DisableStacktrace: false,
        Sampling: nil,
        Encoding: "console",
        EncoderConfig: zapcore.EncoderConfig{
            MessageKey:     "msg",
            LevelKey:       "level",
            TimeKey:        "T",
            NameKey:        "name",
            CallerKey:      "C",
            StacktraceKey:  "S",
            LineEnding:     zapcore.DefaultLineEnding,
            EncodeLevel:    zapcore.CapitalColorLevelEncoder,
            EncodeTime:     zapcore.ISO8601TimeEncoder,
            EncodeDuration: zapcore.StringDurationEncoder,
            EncodeCaller:   zapcore.ShortCallerEncoder,
        },
        OutputPaths:      []string{"stdout"},
        ErrorOutputPaths: []string{"stderr"},
        InitialFields:   nil,
    }

    logger, err := config.Build()
    if err != nil {
        panic(err)
    }
    defer logger.Sync()

    logger.Debug("debug message")
    logger.Info("info message")
}
```

### 选项式配置(Options)

除了 Config 结构体,zap 还支持通过 Options 进行配置:

```go
logger := zap.New(core,
    zap.AddCaller(),                    // 添加调用者信息
    zap.AddStacktrace(ErrorLevel),     // Error 及以上级别添加栈追踪
    zap.WrapCore(wrapCoreFunc),        // 包装 Core
    zap.WithCaller(false),             // 禁用调用者
    zap.WithOptions(opts...),          // 嵌套选项
)
```

### AtomicLevel 运行时级别控制

`AtomicLevel` 支持运行时动态调整日志级别:

```go
atomicLevel := zap.NewAtomicLevel()

config := zap.Config{
    Level: atomicLevel,
    // ...
}

logger, _ := config.Build()

// 运行时修改级别
atomicLevel.SetLevel(zapcore.DebugLevel)
logger.Debug("now visible")

atomicLevel.SetLevel(zapcore.ErrorLevel)
logger.Info("now hidden")
```

::: info 配置建议

- 生产环境使用 `NewProductionConfig()`,基于 `zap.NewProduction()`
- 开发环境使用 `NewDevelopmentConfig()`,基于 `zap.NewDevelopment()`
- 需要完全自定义时使用 `Config{}` 结构体

:::

## Good Practice

### 1. 环境感知的 Logger 初始化

```go
package logger

import (
    "os"
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

var Log *zap.Logger

func Init() error {
    env := os.Getenv("APP_ENV")

    var cfg zap.Config
    if env == "development" {
        cfg = zap.NewDevelopmentConfig()
        cfg.Level = zap.NewAtomicLevelAt(zapcore.DebugLevel)
        cfg.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
    } else {
        cfg = zap.NewProductionConfig()
        cfg.Level = zap.NewAtomicLevelAt(zapcore.InfoLevel)
    }

    var err error
    Log, err = cfg.Build()
    return err
}

func Sync() {
    if Log != nil {
        _ = Log.Sync()
    }
}
```

### 2. 分层 Logger 设计

```go
type Logger struct {
    *zap.Logger
}

func NewLogger(serviceName string) *Logger {
    baseLogger, _ := zap.NewProduction()

    return &Logger{
        Logger: baseLogger.With(
            zap.String("service", serviceName),
        ),
    }
}

func (l *Logger) WithRequestID(requestID string) *zap.Logger {
    return l.Logger.With(zap.String("request_id", requestID))
}

func (l *Logger) WithUser(userID string) *zap.Logger {
    return l.Logger.With(zap.String("user_id", userID))
}
```

### 3. 错误处理的最佳实践

```go
func safeSync(logger *zap.Logger) {
    if logger != nil {
        if err := logger.Sync(); err != nil {
            fmt.Fprintf(os.Stderr, "failed to sync logger: %v\n", err)
        }
    }
}

func main() {
    logger, err := zap.NewProduction()
    if err != nil {
        panic(err)
    }
    defer safeSync(logger)

    logger.Info("application started")
}
```

### 4. 结构化日志字段规范

```go
// 遵循统一的字段命名规范
logger.Info("user action",
    zap.String("event_type", "user_login"),
    zap.String("user_id", "12345"),
    zap.String("ip_address", "192.168.1.1"),
    zap.String("user_agent", "Mozilla/5.0..."),
    zap.Time("timestamp", time.Now()),
)

// 避免混合风格
logger.Info("order created",
    zap.String("order_id", "ORD-12345"),  // 统一使用下划线
    zap.Int("amount", 1000),                 // 统一使用基本类型
    zap.Strings("items", []string{"item1", "item2"}),
)
```

### 5. HTTP 请求日志中间件

```go
func LoggingMiddleware(logger *zap.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()

            wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}
            next.ServeHTTP(wrapped, r)

            logger.Info("http request",
                zap.String("method", r.Method),
                zap.String("path", r.URL.Path),
                zap.Int("status", wrapped.statusCode),
                zap.Duration("latency", time.Since(start)),
                zap.String("client_ip", r.RemoteAddr),
            )
        })
    }
}

type responseWriter struct {
    http.ResponseWriter
    statusCode int
}

func (rw *responseWriter) WriteHeader(code int) {
    rw.statusCode = code
    rw.ResponseWriter.WriteHeader(code)
}
```

### 6. 日志级别使用规范

::: caution 日志级别规范

- **Debug**: 仅在开发/调试时使用,生产环境禁用
- **Info**: 记录正常的业务操作流程
- **Warn**: 记录潜在问题,如超时、重试
- **Error**: 记录错误,但不影响服务继续运行
- **DPanic**: 仅开发环境使用,帮助发现严重 bug
- **Panic**: 记录后 panic,用于不可恢复错误
- **Fatal**: 记录后 os.Exit(1),仅用于程序必须终止的情况

:::

### 7. 性能关键路径优化

```go
// 热点路径:使用 Logger 而非 SugaredLogger
func ProcessHotPath(data []byte) error {
    logger.Info("processing hot path",
        zap.Int("data_size", len(data)),
        zap.String("operation", "process"),
    )
    // 处理逻辑...
    return nil
}

// 非热点路径:可使用 SugaredLogger
func ProcessNonHotPath(data []byte) error {
    sugar := logger.Sugar()
    sugar.Infow("processing non-hot path",
        "data_size", len(data),
        "operation", "process",
    )
    // 处理逻辑...
    return nil
}
```

### 8. 集成日志采样

```go
config := zap.Config{
    Level: zap.NewAtomicLevelAt(zapcore.InfoLevel),
    Sampling: &zap.SamplingConfig{
        Initial:    100,    // 第一秒内最多 100 条
        Thereafter: 100,    // 之后每 100 条采样 1 条
    },
    // ...
}
```

### 9. 多环境输出配置

```go
func buildLoggerConfig(env string) zap.Config {
    switch env {
    case "production":
        return zap.Config{
            Level:       zap.NewAtomicLevelAt(zapcore.InfoLevel),
            Development: false,
            Encoding:   "json",
            Sampling: &zap.SamplingConfig{
                Initial:    100,
                Thereafter: 100,
            },
            OutputPaths:      []string{"stdout"},
            ErrorOutputPaths: []string{"stderr"},
            EncoderConfig:    zap.NewProductionEncoderConfig(),
        }
    case "staging":
        return zap.Config{
            Level:       zap.NewAtomicLevelAt(zapcore.DebugLevel),
            Development: false,
            Encoding:   "json",
            OutputPaths:      []string{"stdout", "/var/log/app-staging.log"},
            ErrorOutputPaths: []string{"stderr"},
            EncoderConfig:    zap.NewProductionEncoderConfig(),
        }
    default: // development
        return zap.Config{
            Level:       zap.NewAtomicLevelAt(zapcore.DebugLevel),
            Development: true,
            Encoding:   "console",
            OutputPaths:      []string{"stdout"},
            ErrorOutputPaths: []string{"stderr"},
            EncoderConfig:    zap.NewDevelopmentEncoderConfig(),
        }
    }
}
```

### 10. 与标准库 log 集成

```go
func redirectStdLog() {
    logger, _ := zap.NewDevelopment()

    zap.RedirectStdLog(logger)

    log.Println("this will be logged via zap")
}

func newStdLog() {
    logger, _ := zap.NewProduction()
    stdLog := zap.NewStdLog(logger)

    stdLog.Println("standard library log via zap")
}
```

:::tip Good Practice 总结

1. **始终调用 Sync()**: 确保缓冲区数据写入
2. **使用结构化字段**: 避免字符串拼接
3. **合理选择日志级别**: 生产环境禁用 Debug
4. **性能关键路径用 Logger**: 其他路径可用 SugaredLogger
5. **统一字段命名**: 保持日志可分析性
6. **使用采样**: 高并发场景防止日志泛滥
7. **分离错误输出**: 内部错误可单独处理

:::

## 常见问题

### 1. 如何添加调用者信息?

```go
logger, _ := zap.NewProduction(zap.AddCaller())
logger.Info("with caller info")
```

输出:

```json
{
  "level": "info",
  "ts": 1715123456.789,
  "caller": "main.go:10",
  "msg": "with caller info"
}
```

### 2. 如何添加调用栈?

```go
logger, _ := zap.NewProduction(zap.AddStacktrace(zapcore.ErrorLevel))
logger.Error("error with stacktrace")
```

### 3. 如何自定义字段名称?

```go
encoderConfig := zapcore.EncoderConfig{
    TimeKey:        "timestamp",
    LevelKey:       "severity",
    MessageKey:     "message",
    CallerKey:      "caller",
    StacktraceKey:  "stack",
    EncodeLevel:    zapcore.LowercaseLevelEncoder,
    EncodeTime:     zapcore.ISO8601TimeEncoder,
}
```

### 4. 如何输出到文件?

```go
file, err := os.OpenFile("/var/log/app.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
if err != nil {
    panic(err)
}

logger := zap.New(
    zapcore.NewCore(
        zapcore.NewJSONEncoder(zap.NewProductionEncoderConfig()),
        zapcore.AddSync(file),
        zapcore.InfoLevel,
    ),
)
```

## 参考资源

- [官方 GitHub 仓库](https://github.com/uber-go/zap)
- [官方文档](https://pkg.go.dev/go.uber.org/zap)
- [性能基准测试](https://github.com/uber-go/zap#performance)
- [FAQ](https://github.com/uber-go/zap/blob/master/FAQ.md)

::: info 总结

Zap 是一款性能卓越、功能强大的结构化日志库,特别适合对性能有严苛要求的 Go 应用。通过合理配置和使用,可以显著提升应用的可观测性和运维效率。

:::
