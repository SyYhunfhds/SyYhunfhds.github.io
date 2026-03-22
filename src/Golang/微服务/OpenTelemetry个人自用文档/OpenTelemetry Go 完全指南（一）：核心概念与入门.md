---
title: OpenTelemetry Go 完全指南（一）：核心概念与入门
date: 2026-03-22
footer: Trae编辑
---

# OpenTelemetry Go 完全指南（一）：核心概念与入门

:::note 参考资料
- [OpenTelemetry Go 官方入门教程](https://opentelemetry.io/docs/languages/go/getting-started/)
- [OpenTelemetry Go API 文档](https://pkg.go.dev/go.opentelemetry.io/otel)
:::

[[toc]]

## 什么是 OpenTelemetry

OpenTelemetry（简称 OTel）是一个开源的可观测性框架，由 CNCF（云原生计算基金会）维护。它提供了一套厂商中立的 API、SDK 和工具集，用于收集、生成和导出遥测数据（Telemetry Data）。

::: info 核心价值
OpenTelemetry 的核心价值在于：
- **统一标准**：整合了 Tracing、Metrics、Logs 三大可观测性信号
- **厂商中立**：避免供应商锁定，可自由切换后端
- **跨语言支持**：支持 Go、Java、Python、JavaScript 等主流语言
- **自动插桩**：提供丰富的自动插桩库，减少代码侵入
:::

## 三大可观测性信号

OpenTelemetry 支持三种类型的遥测数据：

### 1. Tracing（追踪）

追踪记录了请求在分布式系统中的完整路径，包括：
- 请求经过的所有服务
- 每个服务的处理时间
- 服务间的调用关系
- 错误和异常信息

**核心概念**：
- **Trace**：一个完整的请求链路，由多个 Span 组成
- **Span**：一个工作单元，代表一个操作（如 HTTP 请求、数据库查询）
- **SpanContext**：Span 的上下文信息，包括 TraceID、SpanID 等

### 2. Metrics（指标）

指标是可聚合的数值数据，用于监控系统状态：

| **指标类型** | **描述** | **示例** |
| ------------ | -------- | -------- |
| **Counter** | 单调递增的计数器 | 请求数、错误数 |
| **Gauge** | 可增可减的瞬时值 | CPU 使用率、内存使用量 |
| **Histogram** | 值的分布统计 | 响应时间分布、请求大小分布 |
| **Observable Counter** | 可观察的计数器 | 异步采集的计数器 |
| **Observable Gauge** | 可观察的测量值 | 异步采集的测量值 |
| **Observable UpDownCounter** | 可观察的增减计数器 | 异步采集的增减计数器 |

### 3. Logs（日志）

日志是离散的事件记录，包含程序执行的详细信息。OpenTelemetry 正在将日志整合到统一框架中。

::: tip 三者的关联
通过 TraceID 可以将 Tracing、Metrics、Logs 三者关联起来，提供完整的可观测性视图：
- **Metrics** 用于告警和发现异常
- **Tracing** 用于定位问题的具体位置
- **Logs** 用于查看详细的错误信息
:::

## OpenTelemetry 架构

OpenTelemetry 的架构分为三层：

### 1. API 层

定义了遥测数据的接口，不包含具体实现：
- `go.opentelemetry.io/otel/trace` - 追踪 API
- `go.opentelemetry.io/otel/metric` - 指标 API
- `go.opentelemetry.io/otel/baggage` - Baggage API
- `go.opentelemetry.io/otel/propagation` - 上下文传播 API

### 2. SDK 层

实现了 API 层的接口，提供具体功能：
- `go.opentelemetry.io/otel/sdk/trace` - 追踪 SDK
- `go.opentelemetry.io/otel/sdk/metric` - 指标 SDK
- `go.opentelemetry.io/otel/sdk/resource` - 资源管理

### 3. Exporter 层

负责将遥测数据导出到后端系统：
- `go.opentelemetry.io/otel/exporters/jaeger` - Jaeger 导出器
- `go.opentelemetry.io/otel/exporters/otlp/otlptrace` - OTLP 导出器
- `go.opentelemetry.io/otel/exporters/prometheus` - Prometheus 导出器

## 核心组件

### TracerProvider

TracerProvider 是追踪系统的入口，负责：
- 创建和管理 Tracer 实例
- 配置 SpanProcessor 和 Sampler
- 管理 Resource 和 Exporter

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/sdk/trace"
)

// 创建 TracerProvider
tp := trace.NewTracerProvider(
    trace.WithSampler(trace.AlwaysSample()),
    trace.WithBatcher(exporter),
)

// 设置为全局 TracerProvider
otel.SetTracerProvider(tp)
```

### Tracer

Tracer 用于创建 Span，是应用程序与追踪系统交互的主要接口：

```go
// 获取 Tracer
tracer := otel.Tracer("my-service")

// 创建 Span
ctx, span := tracer.Start(ctx, "operation-name")
defer span.End()
```

### MeterProvider

MeterProvider 是指标系统的入口，负责：
- 创建和管理 Meter 实例
- 配置 MetricReader 和 Exporter
- 管理指标的聚合和导出

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/sdk/metric"
)

// 创建 MeterProvider
mp := metric.NewMeterProvider(
    metric.WithReader(reader),
)

// 设置为全局 MeterProvider
otel.SetMeterProvider(mp)
```

### Meter

Meter 用于创建指标，是应用程序与指标系统交互的主要接口：

```go
// 获取 Meter
meter := otel.Meter("my-service")

// 创建 Counter
counter, _ := meter.Int64Counter(
    "request.count",
    metric.WithDescription("Total number of requests"),
)

// 记录指标
counter.Add(ctx, 1)
```

### Resource

Resource 描述了产生遥测数据的实体，通常包含：
- 服务名称
- 服务版本
- 主机名
- 进程 ID
- 环境信息

```go
import (
    "go.opentelemetry.io/otel/sdk/resource"
    semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
)

res := resource.NewWithAttributes(
    semconv.SchemaURL,
    semconv.ServiceName("my-service"),
    semconv.ServiceVersion("1.0.0"),
    semconv.DeploymentEnvironment("production"),
)
```

## 快速开始

### 安装依赖

```bash
# 核心依赖
go get go.opentelemetry.io/otel
go get go.opentelemetry.io/otel/sdk
go get go.opentelemetry.io/otel/exporters/stdout/stdouttrace

# 可选：OTLP 导出器
go get go.opentelemetry.io/otel/exporters/otlp/otlptrace
go get go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc

# 可选：Jaeger 导出器
go get go.opentelemetry.io/otel/exporters/jaeger
```

### 第一个追踪示例

```go
package main

import (
    "context"
    "fmt"
    "log"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/stdout/stdouttrace"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
)

func main() {
    // 创建 stdout 导出器（用于演示）
    exporter, err := stdouttrace.New(stdouttrace.WithPrettyPrint())
    if err != nil {
        log.Fatalf("failed to create exporter: %v", err)
    }

    // 创建 Resource
    res, err := resource.New(
        context.Background(),
        resource.WithAttributes(
            semconv.ServiceName("demo-service"),
        ),
    )
    if err != nil {
        log.Fatalf("failed to create resource: %v", err)
    }

    // 创建 TracerProvider
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(res),
        sdktrace.WithSampler(sdktrace.AlwaysSample()),
    )
    defer tp.Shutdown(context.Background())

    // 设置全局 TracerProvider
    otel.SetTracerProvider(tp)

    // 获取 Tracer
    tracer := otel.Tracer("demo-service")

    // 创建 Span
    ctx, span := tracer.Start(context.Background(), "main-operation")
    defer span.End()

    // 执行业务逻辑
    doWork(ctx, tracer)

    fmt.Println("Trace data exported to stdout")
}

func doWork(ctx context.Context, tracer trace.Tracer) {
    // 创建子 Span
    _, span := tracer.Start(ctx, "do-work")
    defer span.End()

    // 模拟工作
    fmt.Println("Doing work...")
}
```

### 第一个指标示例

```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/stdout/stdoutmetric"
    "go.opentelemetry.io/otel/sdk/metric"
)

func main() {
    // 创建 stdout 导出器（用于演示）
    exporter, err := stdoutmetric.New(stdoutmetric.WithPrettyPrint())
    if err != nil {
        log.Fatalf("failed to create exporter: %v", err)
    }

    // 创建 MeterProvider
    mp := metric.NewMeterProvider(
        metric.WithReader(exporter),
    )
    defer mp.Shutdown(context.Background())

    // 设置全局 MeterProvider
    otel.SetMeterProvider(mp)

    // 获取 Meter
    meter := otel.Meter("demo-service")

    // 创建 Counter
    counter, err := meter.Int64Counter(
        "request.count",
        metric.WithDescription("Total number of requests"),
        metric.WithUnit("{request}"),
    )
    if err != nil {
        log.Fatalf("failed to create counter: %v", err)
    }

    // 创建 Histogram
    histogram, err := meter.Float64Histogram(
        "request.duration",
        metric.WithDescription("Request duration in milliseconds"),
        metric.WithUnit("ms"),
    )
    if err != nil {
        log.Fatalf("failed to create histogram: %v", err)
    }

    // 记录指标
    for i := 0; i < 5; i++ {
        counter.Add(context.Background(), 1)
        histogram.Record(context.Background(), float64(i*100))
        time.Sleep(100 * time.Millisecond)
    }

    fmt.Println("Metric data exported to stdout")
}
```

## 目录结构建议

对于完整的 OpenTelemetry Go 项目，建议的目录结构：

```
my-service/
├── cmd/
│   └── main.go
├── internal/
│   ├── telemetry/
│   │   ├── tracer.go      # Tracer 初始化
│   │   ├── meter.go       # Meter 初始化
│   │   └── config.go      # 配置管理
│   └── handler/
│       └── handler.go
├── pkg/
│   └── middleware/
│       └── tracing.go     # 追踪中间件
├── go.mod
└── go.sum
```

## 本系列笔记规划

本系列将分为以下几部分：

1. **基础篇（本文）**：核心概念与入门
   - OpenTelemetry 简介
   - 三大可观测性信号
   - 架构和核心组件
   - 快速开始示例

2. **Tracing 篇**：追踪 API 详解
   - TracerProvider 配置
   - Span 创建和管理
   - SpanProcessor 和 Sampler
   - Exporter 配置
   - 属性和事件

3. **Metrics 篇**：指标 API 详解
   - MeterProvider 配置
   - Counter、Gauge、Histogram 使用
   - Observable 指标
   - MetricReader 和 Exporter
   - 视图和聚合

4. **高级篇**：Context Propagation 和最佳实践
   - Context 传播机制
   - Baggage 使用
   - 自动插桩
   - 与框架集成（Gin、gRPC 等）
   - 最佳实践和性能优化

## 总结

::: tip 关键要点
1. **统一标准**：OpenTelemetry 提供了 Tracing、Metrics、Logs 三大信号的统一采集
2. **厂商中立**：避免供应商锁定，可自由切换后端
3. **分层架构**：API 层定义接口，SDK 层提供实现，Exporter 层负责导出
4. **核心组件**：TracerProvider、Tracer、MeterProvider、Meter、Resource
5. **快速开始**：通过简单的配置即可开始使用 OpenTelemetry
:::

OpenTelemetry 是现代云原生应用可观测性的基石。通过本系列笔记，你将掌握如何在 Go 应用中完整地使用 OpenTelemetry，构建强大的可观测性系统。

下一篇文章将详细介绍 Tracing API 的使用方法和最佳实践。
