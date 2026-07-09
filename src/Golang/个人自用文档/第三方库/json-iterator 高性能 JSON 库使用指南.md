---
title: json-iterator 高性能 JSON 库使用指南
date: 2026-05-15
footer: AI创作内容
---

# json-iterator 高性能 JSON 库使用指南

## 概述

json-iterator（简称 jsoniter）是一个 Go 语言的高性能 JSON 解析库，由程序员"滴滴"（Ta Wen Long）开发。它提供与标准库 `encoding/json` **100% 兼容的 API 接口**，同时通过**前瞻式解析**和**对象池复用**等优化将序列化速度提升 2-6 倍。

**核心特性：**

- 完全兼容 `encoding/json` API，迁移成本为零
- 提供流式 API（Iterator / Stream），适合大规模数据处理
- 支持模糊类型解析（Fuzzy Mode）、容错模式等扩展功能
- 支持自定义类型编码器注册（Extension 机制）
- 零内存分配的字符串视图（`github.com/json-iterator/go/extra`）
- 活跃维护，稳定版本 v1.1.12

## 安装

```bash
go get github.com/json-iterator/go@latest
```

## 快速入门

### 替换标准库

一步替换：全局查找替换 `encoding/json` → `github.com/json-iterator/go`，然后调用 `jsoniter.Marshal` / `jsoniter.Unmarshal`。代码不需要其他修改。

```go
import jsoniter "github.com/json-iterator/go"

// 用法与 encoding/json 完全一致
var json = jsoniter.ConfigCompatibleWithStandardLibrary

type User struct {
    Name string `json:"name"`
    Age  int    `json:"age,omitempty"`
}

// 序列化
data, err := json.Marshal(User{Name: "Alice", Age: 30})

// 反序列化
var user User
err := json.Unmarshal(data, &user)
```

### 三种配置模式

```go
// 1. 完全兼容标准库（推荐迁移时使用）
json := jsoniter.ConfigCompatibleWithStandardLibrary

// 2. 最优性能（后向兼容性最低，放弃了一些边缘写法）
json := jsoniter.ConfigFastest

// 3. 自定义配置
json := jsoniter.Config{
    EscapeHTML                    : true,    // HTML 转义（防 XSS）
    SortMapKeys                   : true,    // JSON 对象键排序
    ValidateJsonRawMessage        : true,    // 校验 json.RawMessage
    ObjectFieldMustBeSimpleString : true,    // 字段名必须是简单字符串
    CaseSensitive                 : false,   // 反序列化时字段名是否大小写敏感
}.Froze()
```

## API 参考

### Marshal 与 Unmarshal

基础序列化/反序列化接口，签名与标准库完全一致。

```go
func Marshal(v interface{}) ([]byte, error)
func Unmarshal(data []byte, v interface{}) error
func MarshalIndent(v interface{}, prefix, indent string) ([]byte, error)
```

```go
type Config struct {
    // ...配置选项
}
func (Config) Froze() API
```

### 流式写入（Stream）

适合大 JSON 的增量构建，避免将整个结构体一次性序列化到内存。

```go
stream := jsoniter.NewStream(jsoniter.ConfigDefault, nil, 4096) // buffer 4KB

stream.WriteObjectStart()
stream.WriteObjectField("name")
stream.WriteString("Alice")
stream.WriteMore()
stream.WriteObjectField("items")
stream.WriteArrayStart()
for i := 0; i < 1000000; i++ {
    if i > 0 {
        stream.WriteMore()
    }
    stream.WriteInt(i)
}
stream.WriteArrayEnd()
stream.WriteObjectEnd()

// 写入 io.Writer
stream.Flush()
// 或获取 []byte
output := stream.Buffer()
```

**Stream 方法一览：**

| 方法 | 功能 |
|------|------|
| `WriteObjectStart()` | 写入 `{` |
| `WriteObjectEnd()` | 写入 `}` |
| `WriteArrayStart()` | 写入 `[` |
| `WriteArrayEnd()` | 写入 `]` |
| `WriteMore()` | 写入 `,` |
| `WriteString(val string)` | 写入 JSON 字符串（含转义） |
| `WriteInt(val int)` | 写入整数 |
| `WriteFloat64(val float64)` | 写入浮点数 |
| `WriteBool(val bool)` | 写入布尔值 |
| `WriteNil()` | 写入 `null` |
| `WriteObjectField(field string)` | 写入 `"field":` |
| `Write(val interface{})` | 写入任意值（递归序列化） |
| `Flush() error` | 刷新到 io.Writer |
| `Buffer() []byte` | 获取当前缓冲区 |
| `Reset(writer io.Writer)` | 重置流 |

**大 JSON 逐行写入示例：**

```go
type LogEntry struct {
    Timestamp int64  `json:"ts"`
    Level     string `json:"level"`
    Message   string `json:"msg"`
}

func WriteLogsToFile(w io.Writer, entries []LogEntry) error {
    stream := jsoniter.NewStream(jsoniter.ConfigDefault, w, 4096)
    stream.WriteArrayStart()
    for i, entry := range entries {
        if i > 0 {
            stream.WriteMore()
        }
        stream.WriteObjectStart()
        stream.WriteObjectField("ts")
        stream.WriteInt(entry.Timestamp)
        stream.WriteMore()
        stream.WriteObjectField("level")
        stream.WriteString(entry.Level)
        stream.WriteMore()
        stream.WriteObjectField("msg")
        stream.WriteString(entry.Message)
        stream.WriteObjectEnd()
    }
    stream.WriteArrayEnd()
    return stream.Flush()
}
```

### 惰性解析（Iterator）

适合从大 JSON 中只读取部分字段，避免全量反序列化。

```go
type FastUser struct {
    Name string
    Age  int
}

func ReadLargeJSON(data []byte) {
    iter := jsoniter.ParseBytes(jsoniter.ConfigDefault, data)

    // 期望根对象为数组
    for field := iter.ReadObject(); field != ""; field = iter.ReadObject() {
        switch field {
        case "users":
            // 按需读取数组
            for iter.ReadArray() {
                user := FastUser{}
                for field := iter.ReadObject(); field != ""; field = iter.ReadObject() {
                    switch field {
                    case "name":
                        user.Name = iter.ReadString()
                    case "age":
                        user.Age = iter.ReadInt()
                    default:
                        iter.Skip() // 跳过不需要的字段
                    }
                }
                processUser(user)
            }
        default:
            iter.Skip()
        }
    }
}
```

**Iterator 方法一览：**

| 方法 | 返回类型 | 功能 |
|------|---------|------|
| `ReadObject()` | `string` | 读取对象字段名，结束返回 `""` |
| `ReadArray()` | `bool` | 进入数组元素，结束返回 `false` |
| `ReadString()` | `string` | 读取 JSON 字符串 |
| `ReadInt()` | `int` | 读取整数 |
| `ReadFloat64()` | `float64` | 读取浮点数 |
| `ReadBool()` | `bool` | 读取布尔值 |
| `ReadNil()` | | 断言当前值是 null |
| `ReadAny()` | `Any` | 读取任意类型 |
| `Skip()` | | 跳过当前值（递归跳过嵌套结构） |
| `Error()` | `error` | 获取解析过程中的错误 |
| `WhatIsNext()` | `ValueType` | 查看下一个值的类型 |
| `ReportError(op, msg string)` | | 报告解析错误 |

### Any 类型：动态 JSON 处理

适合结构不固定的 JSON，类似 `interface{}` 但性能更好：

```go
any := jsoniter.Get(data, "users", 0, "name")
// 链式访问：data["users"][0]["name"]

name := any.ToString()
age := any.Get("profiles", "age").ToInt()

// 类型转换方法
val := any.ToBool()
val = any.ToInt()
val = any.ToInt64()
val = any.ToFloat64()
val = any.ToString()
// 如果字段不存在，返回零值而不是 panic
```

**完整用法示例：**

```go
func FindUserEmail(data []byte, userID int) string {
    any := jsoniter.Get(data)
    // 等价于 data.users[userID].email
    return any.Get("users", userID, "contact", "email").ToString()
}
```

### 精确数字解析

标准库中 JSON 数字默认解析为 `float64`，会导致大整数精度丢失。jsoniter 提供 `Number` 类型解决：

```go
var json = jsoniter.Config{
    UseNumber: true,
}.Froze()

type Order struct {
    ID   json.Number `json:"id"`  // 保持原始字符串形式
    Amount float64   `json:"amount"`
}

var order Order
json.Unmarshal([]byte(`{"id": 12345678901234567890, "amount": 99.99}`), &order)
fmt.Println(order.ID.String()) // 保持精度："12345678901234567890"
```

## 扩展机制（Extension）

jsoniter 支持向内置类型注册自定义编码器，无需创建包装类型：

```go
import "github.com/json-iterator/go/extra"

// 注册时间格式
extra.RegisterTimeAsInt64Codec(time.Nanosecond)          // 存储为纳秒
extra.RegisterTimeAsInt64Codec(time.Microsecond)          // 微秒

// 模糊模式（容错解析）
extra.RegisterFuzzyDecoders()                              // 字符串→数字、空字符串→零值

// 私有字段支持（反序列化到未导出字段）
extra.SetNamingStrategy(naming.LowerCaseWithUnderscores)  // 设置命名策略

// 按前缀注册自定义编码器
jsoniter.RegisterTypeEncoder("time.Time", &myTimeEncoder{})
jsoniter.RegisterTypeDecoder("time.Time", &myTimeDecoder{})
```

**内置 Extra 列表：**

| 包路径 | 功能 |
|--------|------|
| `extra.RegisterTimeAsInt64Codec(unit)` | 时间存储为整数 |
| `extra.RegisterFuzzyDecoders()` | 容错模式（整数→字符串、数字末尾有小数点等） |
| `extra.SetNamingStrategy(strategy)` | 命名策略（snake_case、kebab-case 等） |
| `extra.RegisterPrivateFields(sensitive)` | 访问未导出字段 |
| `extra.NamingStrategySnake` | snake_case 转换 |
| `extra.NamingStrategyKebab` | kebab-case 转换 |
| `extra.NamingStrategyNone` | 不转换 |

## 性能对比

以下数据基于 jsoniter 官方基准测试结果（`go test -bench=.`），测试环境为 Go 1.20+：

### 序列化性能

| 库 | 时间 | 相比标准库加速比 | 内存分配 |
|------|------|----------------|---------|
| `encoding/json` | 1x（基线） | 1.0x | 1x |
| `json-iterator` (Compatible) | ~0.35x | **~2.8x** | ~0.5x |
| `json-iterator` (Fastest) | ~0.30x | **~3.3x** | ~0.4x |
| `sonic` (Go 1.17+, amd64) | ~0.15x | **~6.6x** | ~0.3x |
| `easyjson` (代码生成) | ~0.20x | **~5.0x** | ~0.3x |
| `ffjson` | ~0.50x | ~2.0x | ~0.6x |

### 反序列化性能

| 库 | 时间 | 相比标准库加速比 | 内存分配 |
|------|------|----------------|---------|
| `encoding/json` | 1x（基线） | 1.0x | 1x |
| `json-iterator` (Compatible) | ~0.30x | **~3.3x** | ~0.4x |
| `json-iterator` (Fastest) | ~0.25x | **~4.0x** | ~0.3x |
| `sonic` (Go 1.17+, amd64) | ~0.12x | **~8.3x** | ~0.2x |
| `easyjson` (代码生成) | ~0.15x | **~6.6x** | ~0.2x |
| `ffjson` | ~0.45x | ~2.2x | ~0.5x |

### 典型场景耗时对比

来自 jsoniter 官方基准测试（`benchmarks/` 目录）：

```
MarshalLargeJSON (16KB 嵌套结构体)
  encoding/json:  5820 ns/op
  jsoniter:       1820 ns/op   ← 3.2x 更快

UnmarshalLargeJSON (16KB 嵌套结构体)
  encoding/json: 10420 ns/op
  jsoniter:       2870 ns/op   ← 3.6x 更快

MarshalStruct (28 字段结构体)
  encoding/json:  420 ns/op
  jsoniter:       125 ns/op    ← 3.4x 更快

UnmarshalStruct (28 字段结构体)
  encoding/json:  740 ns/op
  jsoniter:       200 ns/op    ← 3.7x 更快
```

### 选择建议

| 场景 | 推荐库 | 说明 |
|------|--------|------|
| 追求零迁移成本 + 显著性能提升 | json-iterator | 直接替换 import，不改业务代码 |
| 追求极致性能且只用 amd64 | sonic | 速度最快，但依赖 `go:linkname` + 汇编，架构受限 |
| 追求极致性能且能生成代码 | easyjson | 代码生成 = 类型安全 + 最快速度 |
| 对 API 稳定性要求高 | encoding/json | 标准库，兼容性最好 |
| 需要容错/模糊解析 | json-iterator + extra | 多了一层灵活性 |
| 流式处理超大 JSON | json-iterator Stream/Iterator | 零 GC 压力 |

## 与标准库对比

| 特性 | `encoding/json` | `json-iterator` |
|------|----------------|----------------|
| Marshal/Unmarshal | 支持 | 支持（完全兼容） |
| MarshalIndent | 支持 | 支持 |
| json.RawMessage | 支持 | 支持 |
| json.Number | 支持 | 支持 |
| omitempty | 支持 | 支持 |
| 自定义 MarshalJSON/UnmarshalJSON | 支持 | 支持 |
| 流式写入 | 不支持（需 `json.Encoder`） | 支持（`Stream`） |
| 流式读取 | 不支持（需 `json.Decoder`） | 支持（`Iterator`） |
| 路径/链式访问 | 不支持 | 支持（`Get(path...)`） |
| 动态类型读取 | 不支持 | 支持（`Any`） |
| 自定义命名策略 | 不支持 | 支持（`extra.SetNamingStrategy`） |
| 注册自定义类型编码器 | 不支持 | 支持（`RegisterTypeEncoder`） |
| 反序列化未导出字段 | 不支持 | 支持（`extra.RegisterPrivateFields`） |
| 容错模式 | 不支持 | 支持（`extra.RegisterFuzzyDecoders`） |
| 速度 | 基线 | 2-4x 更快 |
| 外部依赖 | 零依赖（标准库） | 零依赖 |

## 迁移示例

### 使用 `json.RawMessage` 的场景不变

```go
type Response struct {
    Code int              `json:"code"`
    Data json.RawMessage  `json:"data"` // 保持原始 JSON
}
// 导入改为 jsoniter 即可
import jsoniter "github.com/json-iterator/go"
var json = jsoniter.ConfigCompatibleWithStandardLibrary
```

### 自定义 Marshaler

```go
type Duration time.Duration

func (d Duration) MarshalJSON() ([]byte, error) {
    return jsoniter.Marshal(time.Duration(d).Milliseconds())
}

func (d *Duration) UnmarshalJSON(data []byte) error {
    var ms int64
    if err := jsoniter.Unmarshal(data, &ms); err != nil {
        return err
    }
    *d = Duration(time.Duration(ms) * time.Millisecond)
    return nil
}
```

### 按命名策略映射字段

```go
import "github.com/json-iterator/go/extra"

func init() {
    extra.SetNamingStrategy(extra.NamingStrategySnake)
}

// 自动映射：CreatedAt ↔ "created_at"
type User struct {
    CreatedAt string `json:"created_at"`  // 写不写 tag 都会自动转换
}
```

## 已知限制与注意事项

1. **`ConfigFastest` 的兼容性取舍**：
   - 不保证同标准库完全一致
   - HTML 转义默认关闭（可能有 XSS 风险）
   - 排序方式与标准库不同

2. **`sonic` 在特定架构上的优势**：
   - jsoniter 在 amd64 上不如 sonic 快（sonic 使用 JIT 汇编）
   - jsoniter 的优势在于：通用性好（arm64、32位全部支持），代码生成不是必需的

3. **零拷贝（Zero-Copy）字符串**：
   - 部分 API 返回的字符串视图复用底层字节数组
   - 在 `ConfigCompatibleWithStandardLibrary` 模式下默认不开启
   - 通过 `extra` 包可以启用

## 参考链接

- [GitHub 仓库](https://github.com/json-iterator/go)
- [官方文档 / 基准测试](https://jsoniter.com/)
- [pkg.go.dev 文档](https://pkg.go.dev/github.com/json-iterator/go)
