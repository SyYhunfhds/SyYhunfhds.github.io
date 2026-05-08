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

## 最佳实践

### 1. 全局 Logger

```go
package logger

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

var Log *zap.Logger

func Init(level string) error {
    var config zap.Config
    if level == "debug" {
        config = zap.NewDevelopmentConfig()
        config.Level = zap.NewAtomicLevelAt(zapcore.DebugLevel)
    } else {
        config = zap.NewProductionConfig()
        config.Level = zap.NewAtomicLevelAt(zapcore.InfoLevel)
    }

    var err error
    Log, err = config.Build()
    if err != nil {
        return err
    }

    return nil
}

func Sync() {
    if Log != nil {
        _ = Log.Sync()
    }
}
```

使用示例:

```go
package main

import "your-app/logger"

func main() {
    if err := logger.Init("debug"); err != nil {
        panic(err)
    }
    defer logger.Sync()

    logger.Log.Info("application started")
}
```

### 2. 结构化错误日志

```go
func ProcessOrder(orderID string) error {
    logger.Info("processing order",
        zap.String("order_id", orderID),
        zap.String("stage", "validation"),
    )

    if err := validateOrder(orderID); err != nil {
        logger.Error("order validation failed",
            zap.String("order_id", orderID),
            zap.Error(err),
            zap.String("stage", "validation"),
        )
        return err
    }

    logger.Info("order processed successfully",
        zap.String("order_id", orderID),
    )
    return nil
}
```

### 3. 上下文日志传递

```go
func HandleRequest(ctx context.Context, req *Request) {
    logger := logger.Log.With(
        zap.String("request_id", req.ID),
        zap.String("user_id", req.UserID),
    )

    logger.Info("request received")

    if err := processRequest(ctx, req); err != nil {
        logger.Error("request processing failed",
            zap.Error(err),
            zap.String("method", req.Method),
        )
        return
    }

    logger.Info("request processed successfully")
}
```

### 4. 性能优化建议

::: caution 性能优化

1. **热点路径使用 Logger**: 在性能关键代码中使用 `zap.Logger` 而非 `SugaredLogger`
2. **避免 zap.Any**: 尽量使用具体类型的字段构造方法
3. **合理设置日志级别**: 生产环境避免使用 Debug 级别
4. **使用采样**: 高并发场景启用日志采样,避免日志泛滥
5. **及时 Sync**: 程序退出前调用 `logger.Sync()` 刷新缓冲区

:::

### 5. 日志采样配置

```go
config := zap.Config{
    Level:       zap.NewAtomicLevelAt(zapcore.InfoLevel),
    Development: false,
    Sampling: &zap.SamplingConfig{
        Initial:    100,
        Thereafter: 100,
    },
    Encoding:         "json",
    EncoderConfig:    zap.NewProductionEncoderConfig(),
    OutputPaths:      []string{"stdout"},
    ErrorOutputPaths: []string{"stderr"},
}
```

采样规则说明:
- 前 100 条日志全部记录
- 之后每 100 条日志记录 1 条

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
