---
title: OpenTelemetry Go 完全指南（三）：Metrics API 详解
date: 2026-03-18
footer: Trae编辑
---

# OpenTelemetry Go 完全指南（三）：Metrics API 详解

:::note 参考资料
- [OpenTelemetry Go Metric API](https://pkg.go.dev/go.opentelemetry.io/otel/metric)
- [OpenTelemetry Go Metric SDK](https://pkg.go.dev/go.opentelemetry.io/otel/sdk/metric)
:::

[[toc]]

## MeterProvider 配置

MeterProvider 是指标系统的核心，负责创建和管理 Meter 实例。

### 创建 MeterProvider

```go
import (
    "context"
    
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"
    "go.opentelemetry.io/otel/sdk/metric"
    "go.opentelemetry.io/otel/sdk/resource"
    semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
)

func initMeterProvider() (*metric.MeterProvider, error) {
    // 创建 Resource
    res, err := resource.New(
        context.Background(),
        resource.WithAttributes(
            semconv.ServiceName("my-service"),
            semconv.ServiceVersion("1.0.0"),
        ),
    )
    if err != nil {
        return nil, err
    }

    // 创建 OTLP 导出器
    exporter, err := otlpmetricgrpc.New(context.Background(),
        otlpmetricgrpc.WithEndpoint("localhost:4317"),
        otlpmetricgrpc.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }

    // 创建 MeterProvider
    mp := metric.NewMeterProvider(
        metric.WithResource(res),
        metric.WithReader(metric.NewPeriodicReader(exporter,
            metric.WithInterval(30*time.Second),
        )),
    )

    // 设置为全局 MeterProvider
    otel.SetMeterProvider(mp)

    return mp, nil
}
```

### MeterProvider 配置选项

| **选项** | **描述** | **默认值** |
| --------- | -------- | ---------- |
| `WithResource` | 设置资源信息 | 空资源 |
| `WithReader` | 添加 MetricReader | - |
| `WithView` | 添加视图配置 | - |
| `WithExemplarFilter` | 设置 Exemplar 过滤器 | - |

## 指标类型详解

### 1. Counter（计数器）

Counter 是单调递增的计数器，只能增加，不能减少。

::: info 使用场景
- 请求数统计
- 错误数统计
- 任务完成数
:::

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/metric"
)

func createCounter() {
    meter := otel.Meter("my-service")

    // 创建 Int64 Counter
    requestCounter, err := meter.Int64Counter(
        "request.count",
        metric.WithDescription("Total number of requests"),
        metric.WithUnit("{request}"),
    )
    if err != nil {
        panic(err)
    }

    // 创建 Float64 Counter
    bytesCounter, err := meter.Float64Counter(
        "bytes.transmitted",
        metric.WithDescription("Total bytes transmitted"),
        metric.WithUnit("By"),
    )
    if err != nil {
        panic(err)
    }

    // 使用 Counter
    ctx := context.Background()
    requestCounter.Add(ctx, 1)
    bytesCounter.Add(ctx, 1024.5)
}
```

### 2. UpDownCounter（增减计数器）

UpDownCounter 可以增加或减少，用于跟踪可增可减的值。

::: info 使用场景
- 活跃连接数
- 队列大小
- 并发请求数
:::

```go
func createUpDownCounter() {
    meter := otel.Meter("my-service")

    // 创建 Int64 UpDownCounter
    activeConnections, err := meter.Int64UpDownCounter(
        "active.connections",
        metric.WithDescription("Number of active connections"),
        metric.WithUnit("{connection}"),
    )
    if err != nil {
        panic(err)
    }

    // 使用 UpDownCounter
    ctx := context.Background()
    activeConnections.Add(ctx, 1)   // 连接增加
    activeConnections.Add(ctx, -1)  // 连接减少
}
```

### 3. Histogram（直方图）

Histogram 用于统计值的分布情况，自动计算分位数。

::: info 使用场景
- 响应时间分布
- 请求大小分布
- 队列等待时间
:::

```go
func createHistogram() {
    meter := otel.Meter("my-service")

    // 创建 Float64 Histogram
    durationHistogram, err := meter.Float64Histogram(
        "request.duration",
        metric.WithDescription("Request duration in milliseconds"),
        metric.WithUnit("ms"),
    )
    if err != nil {
        panic(err)
    }

    // 创建 Int64 Histogram
    sizeHistogram, err := meter.Int64Histogram(
        "request.size",
        metric.WithDescription("Request size in bytes"),
        metric.WithUnit("By"),
    )
    if err != nil {
        panic(err)
    }

    // 使用 Histogram
    ctx := context.Background()
    durationHistogram.Record(ctx, 123.45)
    sizeHistogram.Record(ctx, 1024)
}
```

### 4. Gauge（测量值）

Gauge 用于记录瞬时值，可以增加或减少。

::: info 使用场景
- CPU 使用率
- 内存使用量
- 温度
:::

```go
import (
    "go.opentelemetry.io/otel/metric/instrument"
)

func createGauge() {
    meter := otel.Meter("my-service")

    // 创建 Float64 Observable Gauge
    _, err := meter.Float64ObservableGauge(
        "cpu.usage",
        metric.WithDescription("CPU usage percentage"),
        metric.WithUnit("%"),
        metric.WithFloat64Callback(func(ctx context.Context, obs metric.Float64Observer) error {
            // 获取 CPU 使用率
            usage := getCPUUsage()
            obs.Observe(usage)
            return nil
        }),
    )
    if err != nil {
        panic(err)
    }
}
```

### 5. Observable Counter（可观察计数器）

Observable Counter 是异步采集的计数器，由 SDK 定期调用回调函数获取值。

```go
func createObservableCounter() {
    meter := otel.Meter("my-service")

    // 创建 Int64 Observable Counter
    _, err := meter.Int64ObservableCounter(
        "process.cpu.seconds",
        metric.WithDescription("Total CPU seconds"),
        metric.WithUnit("s"),
        metric.WithInt64Callback(func(ctx context.Context, obs metric.Int64Observer) error {
            // 获取进程 CPU 时间
            cpuSeconds := getProcessCPUTime()
            obs.Observe(cpuSeconds)
            return nil
        }),
    )
    if err != nil {
        panic(err)
    }
}
```

### 6. Observable UpDownCounter（可观察增减计数器）

```go
func createObservableUpDownCounter() {
    meter := otel.Meter("my-service")

    // 创建 Int64 Observable UpDownCounter
    _, err := meter.Int64ObservableUpDownCounter(
        "queue.size",
        metric.WithDescription("Current queue size"),
        metric.WithUnit("{item}"),
        metric.WithInt64Callback(func(ctx context.Context, obs metric.Int64Observer) error {
            // 获取队列大小
            size := getQueueSize()
            obs.Observe(size)
            return nil
        }),
    )
    if err != nil {
        panic(err)
    }
}
```

## 带属性的指标

指标可以添加属性（标签），用于区分不同的维度：

```go
import (
    "go.opentelemetry.io/otel/attribute"
)

func recordMetricsWithAttributes() {
    meter := otel.Meter("my-service")

    counter, _ := meter.Int64Counter(
        "http.requests",
        metric.WithDescription("Total HTTP requests"),
    )

    ctx := context.Background()

    // 记录不同方法的请求数
    counter.Add(ctx, 1, metric.WithAttributes(
        attribute.String("method", "GET"),
        attribute.String("status", "200"),
        attribute.String("route", "/api/users"),
    ))

    counter.Add(ctx, 1, metric.WithAttributes(
        attribute.String("method", "POST"),
        attribute.String("status", "201"),
        attribute.String("route", "/api/users"),
    ))
}
```

## MetricReader 和 Exporter

### PeriodicReader（周期性读取）

定期从 SDK 读取指标并导出：

```go
import (
    "go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"
    "go.opentelemetry.io/otel/sdk/metric"
)

func createPeriodicReader() (metric.Reader, error) {
    // 创建 OTLP 导出器
    exporter, err := otlpmetricgrpc.New(context.Background(),
        otlpmetricgrpc.WithEndpoint("localhost:4317"),
        otlpmetricgrpc.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }

    // 创建 PeriodicReader
    reader := metric.NewPeriodicReader(exporter,
        metric.WithInterval(30*time.Second),
    )

    return reader, nil
}
```

### ManualReader（手动读取）

手动触发指标导出，适合自定义导出逻辑：

```go
func createManualReader() metric.Reader {
    return metric.NewManualReader()
}

// 手动导出指标
func exportMetrics(reader metric.Reader, exporter metric.Exporter) {
    ctx := context.Background()
    
    // 收集指标
    rm, err := reader.Collect(ctx)
    if err != nil {
        panic(err)
    }

    // 导出指标
    if err := exporter.Export(ctx, rm); err != nil {
        panic(err)
    }
}
```

### Prometheus Exporter

直接暴露 Prometheus 格式的指标：

```go
import (
    "go.opentelemetry.io/otel/exporters/prometheus"
    "go.opentelemetry.io/otel/sdk/metric"
)

func initPrometheusExporter() (metric.Reader, error) {
    // 创建 Prometheus 导出器
    exporter, err := prometheus.New()
    if err != nil {
        return nil, err
    }

    // 创建 MeterProvider
    mp := metric.NewMeterProvider(metric.WithReader(exporter))
    otel.SetMeterProvider(mp)

    return exporter, nil
}

// 暴露指标端点
func exposeMetrics() {
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":2222", nil)
}
```

## 视图和聚合

视图用于自定义指标的聚合方式和属性过滤。

### 自定义聚合

```go
import (
    "go.opentelemetry.io/otel/sdk/metric"
)

func createView() metric.View {
    return metric.NewView(
        metric.Instrument{
            Name: "request.duration",
        },
        metric.Stream{
            Aggregation: metric.AggregationExplicitBucketHistogram{
                Boundaries: []float64{0.1, 0.5, 1.0, 2.0, 5.0, 10.0},
            },
        },
    )
}

// 使用视图
mp := metric.NewMeterProvider(
    metric.WithReader(reader),
    metric.WithView(createView()),
)
```

### 属性过滤

```go
func createAttributeFilterView() metric.View {
    return metric.NewView(
        metric.Instrument{
            Name: "http.requests",
        },
        metric.Stream{
            AttributeFilter: attribute.NewDenyKeysFilter(
                "sensitive.data",
                "user.password",
            ),
        },
    )
}
```

### 重命名指标

```go
func createRenameView() metric.View {
    return metric.NewView(
        metric.Instrument{
            Name: "old.metric.name",
        },
        metric.Stream{
            Name: "new.metric.name",
        },
    )
}
```

## 完整示例

### HTTP 服务指标监控

```go
package main

import (
    "context"
    "log"
    "net/http"
    "time"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/exporters/prometheus"
    "go.opentelemetry.io/otel/metric"
    "go.opentelemetry.io/otel/sdk/metric"
)

var (
    meter           metric.Meter
    requestCounter  metric.Int64Counter
    requestDuration metric.Float64Histogram
    activeRequests  metric.Int64UpDownCounter
)

func main() {
    // 初始化 Prometheus 导出器
    exporter, err := prometheus.New()
    if err != nil {
        log.Fatalf("failed to create prometheus exporter: %v", err)
    }

    // 创建 MeterProvider
    mp := metric.NewMeterProvider(metric.WithReader(exporter))
    otel.SetMeterProvider(mp)

    // 创建 Meter
    meter = otel.Meter("http-service")

    // 创建指标
    requestCounter, err = meter.Int64Counter(
        "http.requests.total",
        metric.WithDescription("Total number of HTTP requests"),
        metric.WithUnit("{request}"),
    )
    if err != nil {
        log.Fatalf("failed to create counter: %v", err)
    }

    requestDuration, err = meter.Float64Histogram(
        "http.request.duration",
        metric.WithDescription("HTTP request duration in milliseconds"),
        metric.WithUnit("ms"),
    )
    if err != nil {
        log.Fatalf("failed to create histogram: %v", err)
    }

    activeRequests, err = meter.Int64UpDownCounter(
        "http.requests.active",
        metric.WithDescription("Number of active HTTP requests"),
        metric.WithUnit("{request}"),
    )
    if err != nil {
        log.Fatalf("failed to create updown counter: %v", err)
    }

    // 创建 HTTP 服务
    http.HandleFunc("/api/users", metricsMiddleware(userHandler))
    http.Handle("/metrics", exporter)

    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}

func metricsMiddleware(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        ctx := context.Background()

        // 增加活跃请求数
        activeRequests.Add(ctx, 1)
        defer activeRequests.Add(ctx, -1)

        // 调用处理函数
        next(w, r)

        // 记录请求计数和持续时间
        duration := float64(time.Since(start).Milliseconds())
        attrs := []attribute.KeyValue{
            attribute.String("method", r.Method),
            attribute.String("route", r.URL.Path),
            attribute.Int("status", 200),
        }

        requestCounter.Add(ctx, 1, metric.WithAttributes(attrs...))
        requestDuration.Record(ctx, duration, metric.WithAttributes(attrs...))
    }
}

func userHandler(w http.ResponseWriter, r *http.Request) {
    time.Sleep(10 * time.Millisecond) // 模拟处理时间
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("OK"))
}
```

### 系统资源监控

```go
package main

import (
    "context"
    "log"
    "runtime"
    "time"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"
    "go.opentelemetry.io/otel/metric"
    "go.opentelemetry.io/otel/sdk/metric"
)

func main() {
    // 初始化 OTLP 导出器
    exporter, err := otlpmetricgrpc.New(context.Background(),
        otlpmetricgrpc.WithEndpoint("localhost:4317"),
        otlpmetricgrpc.WithInsecure(),
    )
    if err != nil {
        log.Fatalf("failed to create exporter: %v", err)
    }

    // 创建 MeterProvider
    mp := metric.NewMeterProvider(
        metric.WithReader(metric.NewPeriodicReader(exporter,
            metric.WithInterval(10*time.Second),
        )),
    )
    otel.SetMeterProvider(mp)

    // 创建 Meter
    meter := otel.Meter("system-monitor")

    // 创建 Observable Gauge 监控内存
    _, err = meter.Int64ObservableGauge(
        "process.memory.heap",
        metric.WithDescription("Process heap memory usage in bytes"),
        metric.WithUnit("By"),
        metric.WithInt64Callback(func(ctx context.Context, obs metric.Int64Observer) error {
            var m runtime.MemStats
            runtime.ReadMemStats(&m)
            obs.Observe(int64(m.HeapAlloc))
            return nil
        }),
    )
    if err != nil {
        log.Fatalf("failed to create gauge: %v", err)
    }

    // 创建 Observable Gauge 监控 Goroutine
    _, err = meter.Int64ObservableGauge(
        "process.goroutines",
        metric.WithDescription("Number of goroutines"),
        metric.WithUnit("{goroutine}"),
        metric.WithInt64Callback(func(ctx context.Context, obs metric.Int64Observer) error {
            obs.Observe(int64(runtime.NumGoroutine()))
            return nil
        }),
    )
    if err != nil {
        log.Fatalf("failed to create gauge: %v", err)
    }

    // 保持运行
    select {}
}
```

## 最佳实践

### 1. 合理命名指标

::: tip 命名规范
指标名称应该清晰、简洁，使用小写和下划线。
:::

```go
// ❌ Bad Practice
meter.Int64Counter("RequestCount")
meter.Int64Counter("req_cnt")

// ✅ Good Practice
meter.Int64Counter("http.requests.total")
meter.Int64Counter("db.queries.count")
```

### 2. 使用语义单位

```go
// ❌ Bad Practice
meter.Int64Counter("request.count", metric.WithUnit("1"))

// ✅ Good Practice
meter.Int64Counter("request.count", metric.WithUnit("{request}"))
meter.Float64Histogram("request.duration", metric.WithUnit("ms"))
meter.Int64Counter("bytes.transmitted", metric.WithUnit("By"))
```

### 3. 合理使用属性

```go
// ❌ Bad Practice - 属性值过多
counter.Add(ctx, 1, metric.WithAttributes(
    attribute.String("user.id", userID), // 用户 ID 值太多
))

// ✅ Good Practice - 使用有限的属性值
counter.Add(ctx, 1, metric.WithAttributes(
    attribute.String("method", "GET"),
    attribute.String("status", "200"),
    attribute.String("route", "/api/users"),
))
```

### 4. 选择合适的指标类型

| **场景** | **推荐类型** |
| -------- | ------------ |
| 请求数、错误数 | Counter |
| 响应时间、请求大小 | Histogram |
| 活跃连接数、队列大小 | UpDownCounter |
| CPU 使用率、内存使用量 | Observable Gauge |

### 5. 避免高频更新

```go
// ❌ Bad Practice - 高频更新
for i := 0; i < 1000000; i++ {
    counter.Add(ctx, 1)
}

// ✅ Good Practice - 批量更新
counter.Add(ctx, 1000000)
```

## 总结

::: tip 关键要点
1. **MeterProvider**：指标系统的核心，负责创建和管理 Meter
2. **指标类型**：Counter、UpDownCounter、Histogram、Gauge、Observable Counter/Gauge
3. **MetricReader**：PeriodicReader（自动）、ManualReader（手动）
4. **Exporter**：OTLP、Prometheus、Stdout 等
5. **视图**：自定义聚合、属性过滤、重命名指标
6. **最佳实践**：合理命名、使用语义单位、合理使用属性、选择合适的类型
:::

本篇文章详细介绍了 OpenTelemetry Go 的 Metrics API，包括 MeterProvider 配置、指标类型、MetricReader 和 Exporter、视图和聚合等内容。下一篇文章将介绍 Context Propagation 和最佳实践。
