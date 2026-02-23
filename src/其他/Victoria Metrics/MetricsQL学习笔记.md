---
title: MetricsQL学习笔记
date: 2026-02-16
footer: 版权及浏览收益为原作者所有。如侵犯版权，请通知译者尽快删除
---
[[toc]]
:::note 参考资料
- [官方文档](https://docs.victoriametrics.com/victoriametrics/metricsql/)
- [Medium - PromQL速成](https://valyala.medium.com/promql-tutorial-for-beginners-9ab455142085)
:::
***
### 快速开始
#### 使用golang prometheus SDK库创建一个客户端
```go
package main

import (
	"context"
	"fmt"
	"time"

	"github.com/prometheus/client_golang/api"
	v1 "github.com/prometheus/client_golang/api/prometheus/v1"
	"github.com/prometheus/common/model"
)

func main() {
	// 1. 创建客户端配置（VM 默认端口 8428）
	client, err := api.NewClient(api.Config{
		Address: "http://localhost:8428", 
	})
	if err != nil {
		panic(err)
	}

	v1api := v1.NewAPI(client)
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// 2. 执行 MetricsQL 查询 (即 Prometheus 瞬时查询)
	query := "up{job='node-exporter'}"
	result, warnings, err := v1api.Query(ctx, query, time.Now())
	
	if err != nil {
		fmt.Printf("查询出错: %v\n", err)
		return
	}
	if len(warnings) > 0 {
		fmt.Printf("警告: %v\n", warnings)
	}

	// 3. 处理结果
	switch v := result.(type) {
	case model.Vector:
		for _, sample := range v {
			fmt.Printf("指标: %s, 值: %v, 时间: %v\n", 
				sample.Metric, sample.Value, sample.Timestamp)
		}
	}
}
```

## 语法、操作符与示例
### 基本语法
```promql

```

#### 查询时间序列数据 （指标选择器）
返回所有以`node_network_receive_bytes_total`命名的时间序列数据
```
node_network_receive_bytes_total
```

**演示：查询`snmp_requests_total`时间序列**
![](assets/Pasted%20image%2020260216121635.png)
#### 过滤标签名
查询带有`eth1`标签名的时间序列：
```
node_network_receive_bytes_total{device="eth1"}
```
- `=`（等于）
- `!=`（不等于）
- `=~`（正则匹配）
	**示例**：
	- `node_network_receive_bytes_total{device=~"eth1|eth2"}`
	- `node_network_receive_bytes_total{device=~"eth.+"}`（过滤包含以`eth`开头的`device`标签的时间序列数据）
	[语法参见RE2文档](https://golang.org/pkg/regexp/)
- `!~`（正则排除）

![](assets/Pasted%20image%2020260216155533.png)

#### 过滤多个标签名
只在`instance`为`node42:9100`的Time Series上查询以`eth`开头的网络接口数据：
```
node_network_receive_bytes_total{instance="node42:9100", device=~"eth.+"}
```
上述过滤条件被视为`and`与条件；PromQL不支持`or`或条件，但大多数时候都可以用正则表达式来模拟类似的效果：比如要过滤`eth1`和`lo`的数据
```
node_network_receive_bytes_total{device=~"eth1|lo"}
```

:::note
MetricsQL支持`or`操作符：
```
node_network_receive_bytes_total{device="eth1" or instance="node42:9100"}
```
[详情点此查看](https://docs.victoriametrics.com/keyConcepts.html#filtering-by-multiple-or-filters)
:::
#### 正则匹配指标名
```
node_network_receive_bytes_total{__name__=~"node_network_(receive|transmit)_bytes_total"}
```
### 数据分析
#### 比对当前数据与历史数据
- `offset xxx`：查询指定时间之前的数据
```
node_network_receive_bytes_total offset 7d
```
- 返回一周以前的数据

- **示例**：查询当前GC占用是一小时前GC占用的1.5倍的部分：
```
go_memstats_gc_cpu_fraction > 1.5 * (go_memstats_gc_cpu_fraction offset 1h)
```

#### 计算斜率
计算近`5分钟`内`node_network_receive_bytes_total`指标的斜率：
```
rate(node_network_receive_bytes_total[5m])
```

计算前：
![](assets/Pasted%20image%2020260216163632.png)
计算后：
![](assets/Pasted%20image%2020260216163644.png)

##### 注意事项
- Rate strips metric name while leaving all the labels for the inner time series.

- Do not apply `rate` to time series, which may go up and down. Such time series are called [Gauges](https://prometheus.io/docs/concepts/metric_types/#gauge). `Rate` must be applied only to [Counters](https://prometheus.io/docs/concepts/metric_types/#counter), which always go up, but sometimes may be reset to zero (for instance, on service restart).

- Do not use `irate` instead of `rate`, since [it doesn’t capture spikes](https://medium.com/@valyala/why-irate-from-prometheus-doesnt-capture-spikes-45f9896d7832) and it isn’t much faster than the `rate`.
### 算术操作符
PromQL支持所有基础[算术操作符](https://prometheus.io/docs/prometheus/latest/querying/operators/#arithmetic-binary-operators)：
- `+`
- `-`
- `*`：乘法
- `/`：除法
- `%`：求模
- `^`：指数运算
### 布尔运算符
PromQL支持下列布尔运算符：
- `==`
- `!=`
- `>`和`>=`
- `<`和`<=`
## 组件函数
### 聚合与分组函数
PromQL allows [aggregating and grouping time series](https://prometheus.io/docs/prometheus/latest/querying/operators/#aggregation-operators). Time series are grouped by the given set of labels and then the given aggregation function is applied for each group. For instance, the following query would return summary ingress traffic across all the network interfaces grouped by instances (nodes with installed `node_exporter`):

```
sum(rate(node_network_receive_bytes_total[5m])) by (instance)
```
### 仪表盘(Gauge)函数
Gauges are time series that may go up and down at any time. For instance, memory usage, temperature or pressure. When drawing graphs for gauges it is expected to see min, max, avg and/or quantile values for each point on the graph. PromQL allows doing this with the [following functions](https://prometheus.io/docs/prometheus/latest/querying/functions/#aggregation_over_time):

- [min_over_time](https://docs.victoriametrics.com/MetricsQL.html#min_over_time)
- [max_over_time](https://docs.victoriametrics.com/MetricsQL.html#max_over_time)
- [avg_over_time](https://docs.victoriametrics.com/MetricsQL.html#avg_over_time)
- [quantile_over_time](https://docs.victoriametrics.com/MetricsQL.html#quantile_over_time)

For example, the following query would graph minimum value for free memory for each point on the graph:

```
min_over_time(node_memory_MemFree_bytes[5m])
```

VictoriaMetrics adds [`rollup_*`](https://docs.victoriametrics.com/MetricsQL.html#rollup)functions to PromQL, which automatically return `min`, `max` and `avg` value when applied to Gagues. For instance:

```
rollup(node_memory_MemFree_bytes)
```

### 操作Labels
PromQL provides two functions for labels’ modification, prettifying, deletion or creation:

- [label_replace](https://docs.victoriametrics.com/MetricsQL.html#label_replace)
- [label_join](https://docs.victoriametrics.com/MetricsQL.html#label_join)

Though these functions are awkward to use, they allow powerful dynamic manipulations for labels on the selected time series. The primary use case for `label_` functions is converting labels to the desired view.

VictoriaMetrics extends these functions with [more convenient label manipulation functions](https://docs.victoriametrics.com/MetricsQL.html#label-manipulation-functions):

- [`label_set`](https://docs.victoriametrics.com/MetricsQL.html#label_set) — sets additional labels to time series
- [`label_del`](https://docs.victoriametrics.com/MetricsQL.html#label_del) — deletes the given labels from time series
- [`label_keep`](https://docs.victoriametrics.com/MetricsQL.html#label_keep) — deletes all the labels from time series except the given labels
- [`label_copy`](https://docs.victoriametrics.com/MetricsQL.html#label_copy) — copies label values to another labels
- [`label_move`](https://docs.victoriametrics.com/MetricsQL.html#label_move) — renames labels
- [`label_transform`](https://docs.victoriametrics.com/MetricsQL.html#label_transform) — replaces all the substrings matching the given regex to template replacement
- [`label_value`](https://docs.victoriametrics.com/MetricsQL.html#label_value) — returns numeric value from the given label
### 一次查询，多个返回值
Sometimes it is necessary to return multiple results from a single PromQL query. This may be achieved with `[or](https://prometheus.io/docs/prometheus/latest/querying/operators/#logical-set-binary-operators)` [operator](https://prometheus.io/docs/prometheus/latest/querying/operators/#logical-set-binary-operators). For instance, the following query would return all the time series with names `metric1`, `metric2` and `metric3`:

```
metric1 or metric2 or metric3
```

VictoriaMetrics [simplifies](https://docs.victoriametrics.com/MetricsQL.html#union) returning multiple results — just enumerate them inside `()`:

```
(metric1, metric2, metric3)
```

Note that arbitrary PromQL expressions may be put instead of metric names there.

There is a common trap when combining expression results: results with duplicate set of labels are skipped. For instance, the following query would skip `sum(b)`, since both `sum(a)` and `sum(b)` have identical label set — they have no labels at all:

```
sum(a) or sum(b)
```

***
# 页面底部