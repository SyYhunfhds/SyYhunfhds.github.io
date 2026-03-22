---
title: OpenTelemetry Go 完全指南（二）：Tracing API 详解
date: 2026-03-18
footer: Trae编辑
---

# OpenTelemetry Go 完全指南（二）：Tracing API 详解

:::note 参考资料
- [OpenTelemetry Go Trace API](https://pkg.go.dev/go.opentelemetry.io/otel/trace)
- [OpenTelemetry Go Trace SDK](https://pkg.go.dev/go.opentelemetry.io/otel/sdk/trace)
:::

[[toc]]

## TracerProvider 配置

TracerProvider 是追踪系统的核心，负责创建和管理 Tracer 实例。

### 创建 TracerProvider

```go
import (
    "context"
    
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
)

func initTracerProvider() (*sdktrace.TracerProvider, error) {
    // 创建 Resource
    res, err := resource.New(
        context.Background(),
        resource.WithAttributes(
            semconv.ServiceName("my-service"),
            semconv.ServiceVersion("1.0.0"),
            semconv.DeploymentEnvironment("production"),
        ),
    )
    if err != nil {
        return nil, err
    }

    // 创建 TracerProvider
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithResource(res),
        sdktrace.WithSampler(sdktrace.AlwaysSample()),
        sdktrace.WithBatcher(exporter),
    )

    // 设置为全局 TracerProvider
    otel.SetTracerProvider(tp)

    return tp, nil
}
```

### TracerProvider 配置选项

| **选项** | **描述** | **默认值** |
| --------- | -------- | ---------- |
| `WithResource` | 设置资源信息 | 空资源 |
| `WithSampler` | 设置采样器 | AlwaysSample |
| `WithBatcher` | 使用批处理导出器 | - |
| `WithSyncer` | 使用同步导出器 | - |
| `WithSpanProcessor` | 添加 SpanProcessor | - |
| `WithIDGenerator` | 设置 ID 生成器 | 随机 ID |
| `WithSpanLimits` | 设置 Span 限制 | 默认限制 |

## Span 创建和管理

### 创建 Span

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/trace"
)

func createSpan(ctx context.Context) {
    // 获取 Tracer
    tracer := otel.Tracer("my-service")

    // 创建 Span
    ctx, span := tracer.Start(ctx, "operation-name")
    defer span.End()

    // 执行业务逻辑
    doWork(ctx)
}
```

### Span 启动选项

```go
// 带属性的 Span
ctx, span := tracer.Start(ctx, "operation-name",
    trace.WithAttributes(
        attribute.String("key", "value"),
        attribute.Int("count", 42),
    ),
)

// 带时间戳的 Span
startTime := time.Now()
ctx, span := tracer.Start(ctx, "operation-name",
    trace.WithTimestamp(startTime),
)

// 带链接的 Span
ctx, span := tracer.Start(ctx, "operation-name",
    trace.WithLinks(trace.Link{
        SpanContext: linkedSpanContext,
        Attributes: []attribute.KeyValue{
            attribute.String("link.type", "parent"),
        },
    }),
)

// 指定 SpanKind
ctx, span := tracer.Start(ctx, "http-request",
    trace.WithSpanKind(trace.SpanKindClient),
)
```

### SpanKind 类型

::: info SpanKind 说明
SpanKind 用于标识 Span 的类型，帮助理解调用关系。
:::

| **SpanKind** | **描述** | **示例** |
| ------------ | -------- | -------- |
| `SpanKindInternal` | 内部操作 | 内部函数调用 |
| `SpanKindServer` | 服务端处理请求 | HTTP 服务端 |
| `SpanKindClient` | 客户端发起请求 | HTTP 客户端 |
| `SpanKindProducer` | 生产者发送消息 | Kafka 生产者 |
| `SpanKindConsumer` | 消费者接收消息 | Kafka 消费者 |

```go
// HTTP 服务端
ctx, span := tracer.Start(ctx, "GET /api/users",
    trace.WithSpanKind(trace.SpanKindServer),
)

// HTTP 客户端
ctx, span := tracer.Start(ctx, "GET http://api.example.com/users",
    trace.WithSpanKind(trace.SpanKindClient),
)

// 消息生产者
ctx, span := tracer.Start(ctx, "publish to orders-topic",
    trace.WithSpanKind(trace.SpanKindProducer),
)

// 消息消费者
ctx, span := tracer.Start(ctx, "consume from orders-topic",
    trace.WithSpanKind(trace.SpanKindConsumer),
)
```

### 创建嵌套 Span

```go
func parentOperation(ctx context.Context) {
    tracer := otel.Tracer("my-service")
    
    // 创建父 Span
    ctx, parentSpan := tracer.Start(ctx, "parent-operation")
    defer parentSpan.End()

    // 调用子操作
    childOperation(ctx)
}

func childOperation(ctx context.Context) {
    tracer := otel.Tracer("my-service")
    
    // 创建子 Span（自动继承父 Span 的上下文）
    ctx, childSpan := tracer.Start(ctx, "child-operation")
    defer childSpan.End()

    // 执行业务逻辑
}
```

## Span 属性和事件

### 添加属性

属性是键值对形式的元数据，用于描述 Span 的特征：

```go
import (
    "go.opentelemetry.io/otel/attribute"
)

func addAttributes(span trace.Span) {
    // 添加单个属性
    span.SetAttributes(
        attribute.String("user.id", "12345"),
        attribute.String("user.name", "张三"),
        attribute.Int("user.age", 30),
        attribute.Bool("user.vip", true),
        attribute.Float64("order.amount", 99.99),
    )

    // 添加数组属性
    span.SetAttributes(
        attribute.StringSlice("tags", []string{"premium", "verified"}),
        attribute.IntSlice("ids", []int{1, 2, 3}),
    )
}
```

### 常用语义属性

OpenTelemetry 定义了标准的语义属性，位于 `go.opentelemetry.io/otel/semconv/v1.24.0` 包中：

```go
import (
    semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
)

func addSemanticAttributes(span trace.Span) {
    // HTTP 相关
    span.SetAttributes(
        semconv.HTTPMethod("GET"),
        semconv.HTTPURL("/api/users"),
        semconv.HTTPStatusCode(200),
        semconv.HTTPRoute("/api/users/:id"),
    )

    // 数据库相关
    span.SetAttributes(
        semconv.DBSystemPostgreSQL,
        semconv.DBStatement("SELECT * FROM users WHERE id = $1"),
        semconv.DBOperation("SELECT"),
        semconv.DBSQLTable("users"),
    )

    // 服务相关
    span.SetAttributes(
        semconv.ServiceName("user-service"),
        semconv.ServiceVersion("1.0.0"),
    )
}
```

### 添加事件

事件是带时间戳的日志记录，用于标记 Span 生命周期中的重要时刻：

```go
func addEvents(span trace.Span) {
    // 添加简单事件
    span.AddEvent("operation-started")

    // 添加带属性的事件
    span.AddEvent("cache-hit",
        trace.WithAttributes(
            attribute.String("cache.key", "user:12345"),
            attribute.Int("cache.ttl", 3600),
        ),
    )

    // 添加带时间戳的事件
    span.AddEvent("request-received",
        trace.WithTimestamp(time.Now()),
    )
}
```

### 记录异常

```go
func recordError(span trace.Span, err error) {
    // 记录错误
    span.RecordError(err)

    // 记录错误并设置状态
    span.RecordError(err, trace.WithAttributes(
        attribute.String("error.type", "DatabaseError"),
        attribute.String("error.code", "E1234"),
    ))
    span.SetStatus(codes.Error, err.Error())
}
```

## Span 状态

Span 状态用于表示操作的结果：

```go
import (
    "go.opentelemetry.io/otel/codes"
)

func setSpanStatus(span trace.Span, err error) {
    if err != nil {
        // 设置错误状态
        span.SetStatus(codes.Error, err.Error())
    } else {
        // 设置成功状态
        span.SetStatus(codes.Ok, "")
    }
}
```

### 状态类型

| **状态** | **描述** | **使用场景** |
| -------- | -------- | ------------ |
| `Unset` | 未设置（默认） | 操作未完成或状态未知 |
| `Ok` | 成功 | 操作成功完成 |
| `Error` | 失败 | 操作失败 |

## SpanProcessor 和 Sampler

### SpanProcessor

SpanProcessor 负责处理 Span 的生命周期事件：

#### BatchSpanProcessor（推荐）

批处理导出，性能最优：

```go
import (
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

func createBatchSpanProcessor() (sdktrace.SpanProcessor, error) {
    // 创建 OTLP 导出器
    exporter, err := otlptracegrpc.New(context.Background(),
        otlptracegrpc.WithEndpoint("localhost:4317"),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }

    // 创建批处理 SpanProcessor
    processor := sdktrace.NewBatchSpanProcessor(exporter,
        sdktrace.WithBatchTimeout(5*time.Second),
        sdktrace.WithMaxExportBatchSize(512),
        sdktrace.WithMaxQueueSize(2048),
    )

    return processor, nil
}
```

#### SimpleSpanProcessor

同步导出，适合调试：

```go
func createSimpleSpanProcessor(exporter sdktrace.SpanExporter) sdktrace.SpanProcessor {
    return sdktrace.NewSimpleSpanProcessor(exporter)
}
```

#### 自定义 SpanProcessor

```go
type CustomSpanProcessor struct{}

func (p *CustomSpanProcessor) OnStart(ctx context.Context, span sdktrace.ReadWriteSpan) {
    // Span 开始时调用
}

func (p *CustomSpanProcessor) OnEnd(span sdktrace.ReadOnlySpan) {
    // Span 结束时调用
}

func (p *CustomSpanProcessor) ForceFlush(ctx context.Context) error {
    // 强制刷新
    return nil
}

func (p *CustomSpanProcessor) Shutdown(ctx context.Context) error {
    // 关闭处理器
    return nil
}
```

### Sampler（采样器）

采样器决定哪些 Span 应该被记录：

#### AlwaysSample

记录所有 Span：

```go
tp := sdktrace.NewTracerProvider(
    sdktrace.WithSampler(sdktrace.AlwaysSample()),
)
```

#### NeverSample

不记录任何 Span：

```go
tp := sdktrace.NewTracerProvider(
    sdktrace.WithSampler(sdktrace.NeverSample()),
)
```

#### TraceIDRatioBased

基于 TraceID 的概率采样：

```go
// 采样 10% 的请求
tp := sdktrace.NewTracerProvider(
    sdktrace.WithSampler(sdktrace.TraceIDRatioBased(0.1)),
)
```

#### ParentBased

基于父 Span 的采样决策：

```go
tp := sdktrace.NewTracerProvider(
    sdktrace.WithSampler(sdktrace.ParentBased(
        sdktrace.TraceIDRatioBased(0.1), // 根采样器
        sdktrace.WithLocalParentSampled(sdktrace.AlwaysSample()),  // 父 Span 已采样
        sdktrace.WithLocalParentNotSampled(sdktrace.NeverSample()), // 父 Span 未采样
        sdktrace.WithRemoteParentSampled(sdktrace.AlwaysSample()),  // 远程父 Span 已采样
        sdktrace.WithRemoteParentNotSampled(sdktrace.NeverSample()), // 远程父 Span 未采样
    )),
)
```

## Exporter 配置

### OTLP Exporter（推荐）

使用 OpenTelemetry 协议导出：

```go
import (
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
)

// gRPC 方式
func createOTLPgRPCExporter() (sdktrace.SpanExporter, error) {
    return otlptracegrpc.New(context.Background(),
        otlptracegrpc.WithEndpoint("localhost:4317"),
        otlptracegrpc.WithInsecure(),
        otlptracegrpc.WithTimeout(10*time.Second),
    )
}

// HTTP 方式
func createOTLPHTTPExporter() (sdktrace.SpanExporter, error) {
    return otlptracehttp.New(context.Background(),
        otlptracehttp.WithEndpoint("localhost:4318"),
        otlptracehttp.WithInsecure(),
    )
}
```

### Jaeger Exporter

```go
import (
    "go.opentelemetry.io/otel/exporters/jaeger"
)

func createJaegerExporter() (sdktrace.SpanExporter, error) {
    return jaeger.New(jaeger.WithCollectorEndpoint(
        jaeger.WithEndpoint("http://localhost:14268/api/traces"),
    ))
}
```

### Stdout Exporter（调试用）

```go
import (
    "go.opentelemetry.io/otel/exporters/stdout/stdouttrace"
)

func createStdoutExporter() (sdktrace.SpanExporter, error) {
    return stdouttrace.New(stdouttrace.WithPrettyPrint())
}
```

## 完整示例

### HTTP 服务追踪

```go
package main

import (
    "context"
    "log"
    "net/http"
    "time"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/codes"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
    "go.opentelemetry.io/otel/trace"
)

func main() {
    // 初始化 TracerProvider
    tp, err := initTracerProvider()
    if err != nil {
        log.Fatalf("failed to initialize tracer provider: %v", err)
    }
    defer tp.Shutdown(context.Background())

    // 设置全局 Propagator
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{},
        propagation.Baggage{},
    ))

    // 创建 HTTP 服务
    http.HandleFunc("/api/users", userHandler)
    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}

func initTracerProvider() (*sdktrace.TracerProvider, error) {
    // 创建 OTLP 导出器
    exporter, err := otlptracegrpc.New(context.Background(),
        otlptracegrpc.WithEndpoint("localhost:4317"),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }

    // 创建 Resource
    res, err := resource.New(
        context.Background(),
        resource.WithAttributes(
            semconv.ServiceName("user-service"),
            semconv.ServiceVersion("1.0.0"),
        ),
    )
    if err != nil {
        return nil, err
    }

    // 创建 TracerProvider
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(res),
        sdktrace.WithSampler(sdktrace.ParentBased(
            sdktrace.TraceIDRatioBased(0.1),
        )),
    )

    otel.SetTracerProvider(tp)
    return tp, nil
}

func userHandler(w http.ResponseWriter, r *http.Request) {
    tracer := otel.Tracer("user-service")

    // 从请求中提取上下文
    ctx := otel.GetTextMapPropagator().Extract(
        r.Context(),
        propagation.HeaderCarrier(r.Header),
    )

    // 创建 Span
    ctx, span := tracer.Start(ctx, "GET /api/users",
        trace.WithSpanKind(trace.SpanKindServer),
        trace.WithAttributes(
            semconv.HTTPMethod(r.Method),
            semconv.HTTPRoute("/api/users"),
        ),
    )
    defer span.End()

    // 模拟业务逻辑
    err := processUser(ctx, tracer)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    span.SetStatus(codes.Ok, "")
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("OK"))
}

func processUser(ctx context.Context, tracer trace.Tracer) error {
    // 创建子 Span
    ctx, span := tracer.Start(ctx, "process-user")
    defer span.End()

    // 添加事件
    span.AddEvent("processing-started")

    // 模拟数据库查询
    err := queryDatabase(ctx, tracer)
    if err != nil {
        return err
    }

    span.AddEvent("processing-completed")
    return nil
}

func queryDatabase(ctx context.Context, tracer trace.Tracer) error {
    // 创建子 Span
    ctx, span := tracer.Start(ctx, "query-database",
        trace.WithSpanKind(trace.SpanKindClient),
        trace.WithAttributes(
            semconv.DBSystemPostgreSQL,
            semconv.DBOperation("SELECT"),
            semconv.DBSQLTable("users"),
        ),
    )
    defer span.End()

    // 模拟查询
    time.Sleep(10 * time.Millisecond)

    span.SetAttributes(
        semconv.DBStatement("SELECT * FROM users WHERE active = true"),
        attribute.Int("db.rows_affected", 10),
    )

    return nil
}
```

## 最佳实践

### 1. 合理命名 Span

::: tip 命名规范
Span 名称应该简洁明了，能够清楚地描述操作。
:::

```go
// ❌ Bad Practice
tracer.Start(ctx, "doSomething")
tracer.Start(ctx, "func1")

// ✅ Good Practice
tracer.Start(ctx, "GET /api/users")
tracer.Start(ctx, "query-database")
tracer.Start(ctx, "send-email")
```

### 2. 使用语义属性

```go
// ❌ Bad Practice
span.SetAttributes(
    attribute.String("method", "GET"),
    attribute.String("url", "/api/users"),
)

// ✅ Good Practice
span.SetAttributes(
    semconv.HTTPMethod("GET"),
    semconv.HTTPURL("/api/users"),
)
```

### 3. 正确处理错误

```go
func handleRequest(ctx context.Context) error {
    ctx, span := tracer.Start(ctx, "handle-request")
    defer span.End()

    err := doSomething()
    if err != nil {
        // 记录错误
        span.RecordError(err)
        // 设置状态
        span.SetStatus(codes.Error, err.Error())
        return err
    }

    span.SetStatus(codes.Ok, "")
    return nil
}
```

### 4. 避免过度追踪

```go
// ❌ Bad Practice - 在循环中创建 Span
for _, item := range items {
    ctx, span := tracer.Start(ctx, "process-item")
    processItem(item)
    span.End()
}

// ✅ Good Practice - 批量处理
ctx, span := tracer.Start(ctx, "process-items",
    trace.WithAttributes(
        attribute.Int("item.count", len(items)),
    ),
)
defer span.End()

for _, item := range items {
    processItem(item)
}
```

### 5. 使用 Context 传递

```go
// ❌ Bad Practice - 不传递 Context
func processUser(userID string) {
    ctx, span := tracer.Start(context.Background(), "process-user")
    defer span.End()
    // 无法关联到父 Span
}

// ✅ Good Practice - 传递 Context
func processUser(ctx context.Context, userID string) {
    ctx, span := tracer.Start(ctx, "process-user")
    defer span.End()
    // 可以正确关联到父 Span
}
```

## 总结

::: tip 关键要点
1. **TracerProvider**：追踪系统的核心，负责创建和管理 Tracer
2. **Span**：追踪的基本单元，包含属性、事件、状态等信息
3. **SpanProcessor**：处理 Span 的生命周期事件，推荐使用 BatchSpanProcessor
4. **Sampler**：控制采样率，推荐使用 ParentBased + TraceIDRatioBased
5. **Exporter**：导出追踪数据，推荐使用 OTLP Exporter
6. **最佳实践**：合理命名、使用语义属性、正确处理错误、避免过度追踪
:::

本篇文章详细介绍了 OpenTelemetry Go 的 Tracing API，包括 TracerProvider 配置、Span 创建和管理、属性和事件、SpanProcessor 和 Sampler、Exporter 配置等内容。下一篇文章将介绍 Metrics API 的使用方法。
