---
title: OpenTelemetry Go 完全指南（四）：高级特性与最佳实践
date: 2026-03-18
footer: Trae编辑
---

# OpenTelemetry Go 完全指南（四）：高级特性与最佳实践

:::note 参考资料
- [OpenTelemetry Go Propagation API](https://pkg.go.dev/go.opentelemetry.io/otel/propagation)
- [OpenTelemetry Go Baggage API](https://pkg.go.dev/go.opentelemetry.io/otel/baggage)
:::

[[toc]]

## Context Propagation（上下文传播）

Context Propagation 是分布式追踪的核心机制，用于在服务间传递追踪上下文。

### TraceContext 传播

TraceContext 是 W3C 标准的追踪上下文传播格式，用于在服务间传递追踪信息。它通过两个 HTTP 头部来实现：

- `traceparent`：携带核心追踪信息，包括 TraceID、SpanID、父 SpanID 和采样标志
- `tracestate`：可选的扩展字段，用于传递厂商特定的信息

#### TraceContext 格式详解

`traceparent` 头部格式：
```
00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

各部分含义：
- `00`：版本号
- `4bf92f3577b34da6a3ce929d0e0e4736`：TraceID（16字节，32个十六进制字符）
- `00f067aa0ba902b7`：SpanID（8字节，16个十六进制字符）
- `01`：Trace Flags（最低位表示采样状态）

#### 全局 Propagator 配置

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/propagation"
)

func init() {
    // 设置全局 Propagator
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{},
        propagation.Baggage{},
    ))
}
```

#### 服务间上下文传递方法

##### 1. HTTP 服务间传递

```go
// 服务端提取上下文
func httpHandler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()
    
    tracer := otel.Tracer("http-server")
    ctx, span := tracer.Start(ctx, "handleRequest")
    defer span.End()
    
    // 处理请求...
}

// 客户端注入上下文
func callService(ctx context.Context, url string) error {
    tracer := otel.Tracer("http-client")
    ctx, span := tracer.Start(ctx, "callService")
    defer span.End()
    
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return err
    }
    
    // 自动注入 TraceContext
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    return nil
}
```

##### 2. Redis 服务间传递

对于 Redis 等缓存服务，需要手动传递上下文：

```go
import (
    "context"
    "fmt"
    "github.com/redis/go-redis/v9"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/propagation"
    "net/http"
)

// Redis 客户端包装
func withTraceContext(ctx context.Context, cmd string, keys ...string) context.Context {
    tracer := otel.Tracer("redis-client")
    ctx, span := tracer.Start(ctx, fmt.Sprintf("redis.%s", cmd))
    
    // 注入 TraceContext 到 Redis 命令中（通过 key 前缀或自定义字段）
    carrier := make(http.Header)
    otel.GetTextMapPropagator().Inject(ctx, propagation.HeaderCarrier(carrier))
    
    // 可以将 TraceContext 存储在 Redis 键或值中
    // 例如：使用 key 前缀或在哈希字段中存储
    
    return ctx
}

func redisGet(ctx context.Context, client *redis.Client, key string) (string, error) {
    ctx = withTraceContext(ctx, "GET", key)
    
    val, err := client.Get(ctx, key).Result()
    if err != nil {
        return "", err
    }
    
    return val, nil
}

func redisSet(ctx context.Context, client *redis.Client, key, value string) error {
    ctx = withTraceContext(ctx, "SET", key)
    
    err := client.Set(ctx, key, value, 0).Err()
    if err != nil {
        return err
    }
    
    return nil
}
```

##### 3. gRPC 服务间传递

```go
import (
    "context"
    "google.golang.org/grpc"
    "google.golang.org/grpc/stats/opentelemetry"
)

// 服务端配置
func setupGRPCServer() *grpc.Server {
    opts := []grpc.ServerOption{
        grpc.StatsHandler(opentelemetry.NewServerHandler()),
    }
    
    server := grpc.NewServer(opts...)
    return server
}

// 客户端配置
func setupGRPCClient() *grpc.ClientConn {
    opts := []grpc.DialOption{
        grpc.WithStatsHandler(opentelemetry.NewClientHandler()),
    }
    
    conn, err := grpc.Dial("localhost:50051", opts...)
    if err != nil {
        panic(err)
    }
    return conn
}

// 调用 gRPC 服务
func callGRPCService(ctx context.Context, client pb.UserServiceClient) error {
    tracer := otel.Tracer("grpc-client")
    ctx, span := tracer.Start(ctx, "callUserService")
    defer span.End()
    
    _, err := client.GetUser(ctx, &pb.GetUserRequest{UserId: "123"})
    return err
}
```

##### 4. 消息队列传递

对于 Kafka、RabbitMQ 等消息队列，需要在消息头中传递 TraceContext：

```go
import (
    "context"
    "github.com/segmentio/kafka-go"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/propagation"
    "net/http"
)

// 发送消息时注入 TraceContext
func sendMessage(ctx context.Context, writer *kafka.Writer, topic string, message []byte) error {
    tracer := otel.Tracer("kafka-producer")
    ctx, span := tracer.Start(ctx, "sendMessage")
    defer span.End()
    
    // 注入 TraceContext 到消息头
    headers := make(http.Header)
    otel.GetTextMapPropagator().Inject(ctx, propagation.HeaderCarrier(headers))
    
    kafkaHeaders := make([]kafka.Header, 0, len(headers))
    for k, v := range headers {
        kafkaHeaders = append(kafkaHeaders, kafka.Header{
            Key:   k,
            Value: []byte(v[0]),
        })
    }
    
    err := writer.WriteMessages(ctx, kafka.Message{
        Topic:   topic,
        Value:   message,
        Headers: kafkaHeaders,
    })
    return err
}

// 消费消息时提取 TraceContext
func consumeMessage(ctx context.Context, msg kafka.Message) (context.Context, error) {
    // 从消息头提取 TraceContext
    headers := make(http.Header)
    for _, h := range msg.Headers {
        headers.Add(h.Key, string(h.Value))
    }
    
    ctx = otel.GetTextMapPropagator().Extract(ctx, propagation.HeaderCarrier(headers))
    
    tracer := otel.Tracer("kafka-consumer")
    ctx, span := tracer.Start(ctx, "consumeMessage")
    defer span.End()
    
    // 处理消息...
    
    return ctx, nil
}
```

#### 手动上下文传递

在没有自动 instrumentation 的情况下，需要手动处理上下文传递：

```go
import (
    "context"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/propagation"
    "net/http"
)

// 手动注入上下文
func injectContext(ctx context.Context, headers map[string]string) {
    carrier := make(http.Header)
    for k, v := range headers {
        carrier.Add(k, v)
    }
    
    otel.GetTextMapPropagator().Inject(ctx, propagation.HeaderCarrier(carrier))
    
    for k, v := range carrier {
        headers[k] = v[0]
    }
}

// 手动提取上下文
func extractContext(ctx context.Context, headers map[string]string) context.Context {
    carrier := make(http.Header)
    for k, v := range headers {
        carrier.Add(k, v)
    }
    
    return otel.GetTextMapPropagator().Extract(ctx, propagation.HeaderCarrier(carrier))
}
```

#### 最佳实践

1. **统一配置**：在应用启动时设置全局 Propagator
2. **优先使用自动 instrumentation**：对于 HTTP、gRPC 等常见协议，使用官方提供的中间件
3. **手动传递**：对于 Redis、消息队列等需要手动处理的场景，实现专门的上下文传递逻辑
4. **错误处理**：在传递上下文时处理可能的错误
5. **性能考虑**：避免在高频操作中过度创建 Span
6. **安全考虑**：在处理来自外部的上下文时进行适当验证

#### 常见问题与解决方案

| 问题 | 解决方案 |
|------|----------|
| 上下文传递中断 | 确保所有服务都正确配置了 Propagator |
| 性能开销 | 使用采样策略减少追踪数据量 |
| 跨语言传递 | 确保所有语言都使用 W3C TraceContext 标准 |
| 消息队列传递 | 在消息头中正确存储和提取上下文 |

通过正确实现 TraceContext 传播，可以确保分布式系统中的追踪链路完整，从而更好地理解系统行为和排查问题。

### HTTP 服务端传播

```go
import (
    "net/http"
    
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/trace"
)

func httpHandler(w http.ResponseWriter, r *http.Request) {
    // 从请求头中提取上下文
    ctx := otel.GetTextMapPropagator().Extract(
        r.Context(),
        propagation.HeaderCarrier(r.Header),
    )

    // 创建 Span
    tracer := otel.Tracer("my-service")
    ctx, span := tracer.Start(ctx, "http-request",
        trace.WithSpanKind(trace.SpanKindServer),
    )
    defer span.End()

    // 处理请求
    processRequest(ctx, w, r)
}
```

### HTTP 客户端传播

```go
import (
    "net/http"
    
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/trace"
)

func httpClient(ctx context.Context, url string) (*http.Response, error) {
    tracer := otel.Tracer("my-service")

    // 创建 Span
    ctx, span := tracer.Start(ctx, "http-request",
        trace.WithSpanKind(trace.SpanKindClient),
    )
    defer span.End()

    // 创建 HTTP 请求
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, err
    }

    // 注入上下文到请求头
    otel.GetTextMapPropagator().Inject(ctx, propagation.HeaderCarrier(req.Header))

    // 发送请求
    client := &http.Client{}
    return client.Do(req)
}
```

### gRPC 传播

```go
import (
    "google.golang.org/grpc"
    "google.golang.org/grpc/metadata"
    
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/propagation"
)

// gRPC 客户端拦截器
func grpcClientInterceptor(ctx context.Context, method string, req, reply interface{}, 
    cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {
    
    // 创建 Span
    tracer := otel.Tracer("my-service")
    ctx, span := tracer.Start(ctx, method,
        trace.WithSpanKind(trace.SpanKindClient),
    )
    defer span.End()

    // 注入上下文到 gRPC metadata
    md := metadata.New(nil)
    otel.GetTextMapPropagator().Inject(ctx, propagation.HeaderCarrier(md))
    ctx = metadata.NewOutgoingContext(ctx, md)

    // 调用 RPC
    return invoker(ctx, method, req, reply, cc, opts...)
}

// gRPC 服务端拦截器
func grpcServerInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, 
    handler grpc.UnaryHandler) (interface{}, error) {
    
    // 从 gRPC metadata 中提取上下文
    md, ok := metadata.FromIncomingContext(ctx)
    if ok {
        ctx = otel.GetTextMapPropagator().Extract(ctx, propagation.HeaderCarrier(md))
    }

    // 创建 Span
    tracer := otel.Tracer("my-service")
    ctx, span := tracer.Start(ctx, info.FullMethod,
        trace.WithSpanKind(trace.SpanKindServer),
    )
    defer span.End()

    // 处理请求
    return handler(ctx, req)
}
```

## Baggage（行李）

Baggage 用于在服务间传递业务数据，与 TraceContext 一起传播。

### 设置和获取 Baggage

```go
import (
    "go.opentelemetry.io/otel/baggage"
)

func setBaggage(ctx context.Context) context.Context {
    // 创建 Baggage 成员
    member1, _ := baggage.NewMember("user.id", "12345")
    member2, _ := baggage.NewMember("tenant.id", "tenant-001")

    // 创建 Baggage
    bag, _ := baggage.New(member1, member2)

    // 设置到 Context
    ctx = baggage.ContextWithBaggage(ctx, bag)
    return ctx
}

func getBaggage(ctx context.Context) {
    // 从 Context 获取 Baggage
    bag := baggage.FromContext(ctx)

    // 获取成员值
    userID := bag.Member("user.id").Value()
    tenantID := bag.Member("tenant.id").Value()

    fmt.Printf("User ID: %s, Tenant ID: %s\n", userID, tenantID)
}
```

### 在 Span 中使用 Baggage

```go
func processWithBaggage(ctx context.Context) {
    // 获取 Baggage
    bag := baggage.FromContext(ctx)
    userID := bag.Member("user.id").Value()

    // 创建 Span 并添加属性
    tracer := otel.Tracer("my-service")
    ctx, span := tracer.Start(ctx, "process-request")
    defer span.End()

    span.SetAttributes(
        attribute.String("user.id", userID),
    )
}
```

## 自动插桩

OpenTelemetry 提供了丰富的自动插桩库，减少手动埋点的工作。

### Gin 框架集成

```go
import (
    "github.com/gin-gonic/gin"
    "go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"
)

func main() {
    // 初始化 OpenTelemetry
    initTracerProvider()

    // 创建 Gin 引擎
    r := gin.New()

    // 添加 OpenTelemetry 中间件
    r.Use(otelgin.Middleware("my-service"))

    // 定义路由
    r.GET("/api/users", userHandler)

    r.Run(":8080")
}
```

### gRPC 集成

```go
import (
    "google.golang.org/grpc"
    "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
)

func main() {
    // 初始化 OpenTelemetry
    initTracerProvider()

    // 创建 gRPC 服务器
    server := grpc.NewServer(
        grpc.UnaryInterceptor(otelgrpc.UnaryServerInterceptor()),
        grpc.StreamInterceptor(otelgrpc.StreamServerInterceptor()),
    )

    // 注册服务
    pb.RegisterUserServiceServer(server, &userService{})

    // 启动服务器
    listener, _ := net.Listen("tcp", ":50051")
    server.Serve(listener)
}
```

### 数据库集成

```go
import (
    "database/sql"
    "go.opentelemetry.io/contrib/instrumentation/github.com/go-sql-driver/mysql/otelsql"
)

func main() {
    // 初始化 OpenTelemetry
    initTracerProvider()

    // 使用 OpenTelemetry 包装的数据库驱动
    db, err := otelsql.Open("mysql", "user:password@tcp(localhost:3306)/db")
    if err != nil {
        panic(err)
    }
    defer db.Close()

    // 使用数据库
    rows, _ := db.Query("SELECT * FROM users")
    defer rows.Close()
}
```

### HTTP 客户端集成

```go
import (
    "net/http"
    "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

func main() {
    // 初始化 OpenTelemetry
    initTracerProvider()

    // 创建带追踪的 HTTP 客户端
    client := &http.Client{
        Transport: otelhttp.NewTransport(http.DefaultTransport),
    }

    // 发送请求
    resp, err := client.Get("http://example.com/api/users")
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()
}
```

## 与框架集成

### Gin 中间件完整示例

```go
package middleware

import (
    "github.com/gin-gonic/gin"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/codes"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/trace"
)

func TracingMiddleware(serviceName string) gin.HandlerFunc {
    tracer := otel.Tracer(serviceName)
    propagator := otel.GetTextMapPropagator()

    return func(c *gin.Context) {
        // 从请求头提取上下文
        ctx := propagator.Extract(c.Request.Context(), propagation.HeaderCarrier(c.Request.Header))

        // 创建 Span
        spanName := c.Request.Method + " " + c.FullPath()
        if spanName == " " {
            spanName = c.Request.Method + " " + c.Request.URL.Path
        }

        ctx, span := tracer.Start(ctx, spanName,
            trace.WithSpanKind(trace.SpanKindServer),
            trace.WithAttributes(
                attribute.String("http.method", c.Request.Method),
                attribute.String("http.url", c.Request.URL.String()),
                attribute.String("http.route", c.FullPath()),
                attribute.String("http.host", c.Request.Host),
            ),
        )
        defer span.End()

        // 设置 Context
        c.Request = c.Request.WithContext(ctx)

        // 处理请求
        c.Next()

        // 设置状态
        status := c.Writer.Status()
        span.SetAttributes(
            attribute.Int("http.status_code", status),
        )

        if status >= 400 {
            span.SetStatus(codes.Error, http.StatusText(status))
        } else {
            span.SetStatus(codes.Ok, "")
        }

        // 记录错误
        if len(c.Errors) > 0 {
            span.RecordError(c.Errors.Last())
        }
    }
}
```

### Metrics 中间件

```go
package middleware

import (
    "time"

    "github.com/gin-gonic/gin"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/metric"
)

func MetricsMiddleware(serviceName string) gin.HandlerFunc {
    meter := otel.Meter(serviceName)

    // 创建指标
    requestCounter, _ := meter.Int64Counter(
        "http.requests.total",
        metric.WithDescription("Total number of HTTP requests"),
    )

    requestDuration, _ := meter.Float64Histogram(
        "http.request.duration",
        metric.WithDescription("HTTP request duration in milliseconds"),
    )

    activeRequests, _ := meter.Int64UpDownCounter(
        "http.requests.active",
        metric.WithDescription("Number of active HTTP requests"),
    )

    return func(c *gin.Context) {
        start := time.Now()
        ctx := c.Request.Context()

        // 增加活跃请求数
        activeRequests.Add(ctx, 1)
        defer activeRequests.Add(ctx, -1)

        // 处理请求
        c.Next()

        // 记录指标
        duration := float64(time.Since(start).Milliseconds())
        attrs := []attribute.KeyValue{
            attribute.String("method", c.Request.Method),
            attribute.String("route", c.FullPath()),
            attribute.Int("status", c.Writer.Status()),
        }

        requestCounter.Add(ctx, 1, metric.WithAttributes(attrs...))
        requestDuration.Record(ctx, duration, metric.WithAttributes(attrs...))
    }
}
```

## 最佳实践

### 1. 初始化顺序

::: tip 初始化顺序
正确的初始化顺序对于 OpenTelemetry 至关重要。
:::

```go
func main() {
    // 1. 创建 Resource
    res := createResource()

    // 2. 创建 Exporter
    exporter := createExporter()

    // 3. 创建 TracerProvider 和 MeterProvider
    tp := createTracerProvider(res, exporter)
    mp := createMeterProvider(res, exporter)

    // 4. 设置全局 Provider
    otel.SetTracerProvider(tp)
    otel.SetMeterProvider(mp)

    // 5. 设置 Propagator
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{},
        propagation.Baggage{},
    ))

    // 6. 确保在程序退出时关闭
    defer tp.Shutdown(context.Background())
    defer mp.Shutdown(context.Background())

    // 7. 启动应用
    runApplication()
}
```

### 2. 采样策略

```go
// 生产环境推荐配置
func createProductionSampler() sdktrace.Sampler {
    return sdktrace.ParentBased(
        sdktrace.TraceIDRatioBased(0.1), // 根采样率 10%
        sdktrace.WithLocalParentSampled(sdktrace.AlwaysSample()),
        sdktrace.WithRemoteParentSampled(sdktrace.AlwaysSample()),
    )
}

// 开发环境推荐配置
func createDevelopmentSampler() sdktrace.Sampler {
    return sdktrace.AlwaysSample()
}
```

### 3. 错误处理

```go
func handleRequest(ctx context.Context) error {
    ctx, span := tracer.Start(ctx, "handle-request")
    defer span.End()

    err := doSomething()
    if err != nil {
        // 记录错误
        span.RecordError(err, trace.WithAttributes(
            attribute.String("error.type", fmt.Sprintf("%T", err)),
        ))
        // 设置状态
        span.SetStatus(codes.Error, err.Error())
        return err
    }

    span.SetStatus(codes.Ok, "")
    return nil
}
```

### 4. 性能优化

```go
// 使用批处理导出
tp := sdktrace.NewTracerProvider(
    sdktrace.WithBatcher(exporter,
        sdktrace.WithBatchTimeout(5*time.Second),
        sdktrace.WithMaxExportBatchSize(512),
        sdktrace.WithMaxQueueSize(2048),
    ),
)

// 使用合理的采样率
tp := sdktrace.NewTracerProvider(
    sdktrace.WithSampler(sdktrace.ParentBased(
        sdktrace.TraceIDRatioBased(0.1),
    )),
)

// 避免过度埋点
// ❌ Bad
for i := 0; i < 1000; i++ {
    ctx, span := tracer.Start(ctx, "process-item")
    processItem(i)
    span.End()
}

// ✅ Good
ctx, span := tracer.Start(ctx, "process-items")
for i := 0; i < 1000; i++ {
    processItem(i)
}
span.End()
```

### 5. 资源管理

```go
func createResource() *resource.Resource {
    // 自动检测资源
    res, err := resource.New(
        context.Background(),
        resource.WithAttributes(
            semconv.ServiceName("my-service"),
            semconv.ServiceVersion("1.0.0"),
        ),
        resource.WithHost(),
        resource.WithOS(),
        resource.WithProcess(),
        resource.WithContainer(),
    )
    if err != nil {
        panic(err)
    }
    return res
}
```

### 6. 测试支持

```go
import (
    "go.opentelemetry.io/otel/sdk/trace/tracetest"
)

func TestWithTracing(t *testing.T) {
    // 创建内存导出器
    exporter := tracetest.NewInMemoryExporter()

    // 创建 TracerProvider
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithSyncer(exporter),
        sdktrace.WithSampler(sdktrace.AlwaysSample()),
    )
    defer tp.Shutdown(context.Background())

    otel.SetTracerProvider(tp)

    // 执行测试
    ctx := context.Background()
    doSomething(ctx)

    // 验证 Span
    spans := exporter.GetSpans()
    assert.Equal(t, 1, len(spans))
    assert.Equal(t, "do-something", spans[0].Name)
}
```

## 总结

::: tip 关键要点
1. **Context Propagation**：确保追踪上下文在服务间正确传播
2. **Baggage**：用于传递业务数据，与 TraceContext 一起传播
3. **自动插桩**：使用官方提供的插桩库，减少手动埋点
4. **框架集成**：与 Gin、gRPC、数据库等框架无缝集成
5. **最佳实践**：正确的初始化顺序、合理的采样策略、错误处理、性能优化
:::

本系列笔记完整介绍了 OpenTelemetry Go 的所有核心 API 和最佳实践。通过掌握这些内容，你可以在 Go 应用中构建强大的可观测性系统，实现对 Tracing、Metrics、Logs 三大信号的统一采集和管理。

## 附录：常用包列表

| **包名** | **用途** |
| -------- | -------- |
| `go.opentelemetry.io/otel` | 核心包 |
| `go.opentelemetry.io/otel/trace` | Tracing API |
| `go.opentelemetry.io/otel/metric` | Metrics API |
| `go.opentelemetry.io/otel/baggage` | Baggage API |
| `go.opentelemetry.io/otel/propagation` | 上下文传播 |
| `go.opentelemetry.io/otel/sdk/trace` | Tracing SDK |
| `go.opentelemetry.io/otel/sdk/metric` | Metrics SDK |
| `go.opentelemetry.io/otel/sdk/resource` | 资源管理 |
| `go.opentelemetry.io/otel/exporters/otlp/otlptrace` | OTLP Trace Exporter |
| `go.opentelemetry.io/otel/exporters/otlp/otlpmetric` | OTLP Metric Exporter |
| `go.opentelemetry.io/otel/exporters/jaeger` | Jaeger Exporter |
| `go.opentelemetry.io/otel/exporters/prometheus` | Prometheus Exporter |
| `go.opentelemetry.io/contrib/instrumentation/...` | 自动插桩库 |
