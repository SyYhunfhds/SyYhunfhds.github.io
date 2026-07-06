---
title: go/ast、go/parser、go/types 与 reflect 库详解
date: 2026-03-09
footer: Trae编辑
---

# go/ast、go/parser、go/types 与 reflect 库详解

## 概述

Go 标准库提供两套代码扫描工具链：

| 扫描方式 | 时机 | 核心包 | 能力 |
|----------|------|--------|------|
| **静态扫描** | 编译时（无需运行） | `go/ast`, `go/parser`, `go/token`, `go/types` | 解析源码为抽象语法树（AST），获取类型信息 |
| **动态扫描** | 运行时 | `reflect` | 检查程序运行时的类型和值，动态调用方法 |

两种方式互补：静态扫描能分析未执行的代码路径，动态扫描能看到运行时的实际数据。

---

## 第一部分：静态扫描

## 核心包关系

```
Go 源码文件 (*.go)
      │
      ▼
go/parser.ParseFile()          ← 词法/语法分析
      │
      ▼
go/ast.File                    ← 抽象语法树（AST）
      │
      ├──▶ ast.Inspect() / ast.Walk()   ← 遍历 AST 节点
      │
      └──▶ go/types.Check()             ← 类型检查
              │
              ▼
         go/types.Info                  ← 类型信息（标识符、类型推断等）
```

辅助包 `go/token` 贯穿全程，记录每个节点在源码中的位置（文件、行号、列号）。

### go/token — 位置与令牌

`go/token` 提供源代码位置信息和词法令牌。

```go
import "go/token"

// FileSet 管理一组源文件的位置信息
// 所有解析和类型检查操作共享同一个 FileSet
fset := token.NewFileSet()

// 核心类型
type Pos  int          // 字节偏移位置
type Position struct { // 可读位置
    Filename string
    Offset   int
    Line     int
    Column   int
}

// FileSet 方法
func (s *FileSet) Position(p Pos) Position  // Pos → Position
func (s *FileSet) AddFile(filename, base, size) *File
```

## 一、go/ast — 抽象语法树

`go/ast` 定义了 Go 源码的树形结构。每个语法元素对应一个节点类型，所有节点实现 `ast.Node` 接口。

### Node 接口

```go
type Node interface {
    Pos() token.Pos // 起始位置
    End() token.Pos // 结束位置
}
```

### 关键节点类型

| 结构体 | 对应代码 | 关键字段 |
|--------|----------|----------|
| `*ast.File` | 整个 `.go` 文件 | `Name`（包名）、`Decls`（声明列表）、`Imports`（导入） |
| `*ast.Package` | 一个包（多个文件） | `Name`、`Files` |
| `*ast.Ident` | 标识符 | `Name`（名字）、`Obj`（绑定的对象） |
| `*ast.FuncDecl` | 函数/方法声明 | `Recv`（接收者）、`Name`、`Type`、`Body` |
| `*ast.GenDecl` | 通用声明（var/const/type/import） | `Tok`（关键字）、`Specs`（规格列表） |
| `*ast.ValueSpec` | 值声明 | `Names`、`Type`、`Values` |
| `*ast.TypeSpec` | 类型声明 | `Name`、`Type` |
| `*ast.CallExpr` | 函数调用 | `Fun`（函数表达式）、`Args`（参数） |
| `*ast.BinaryExpr` | 二元表达式 | `X`（左）、`Op`（运算符）、`Y`（右） |
| `*ast.AssignStmt` | 赋值语句 | `Lhs`（左值）、`Tok`（运算符）、`Rhs`（右值） |
| `*ast.ReturnStmt` | return 语句 | `Results`（返回值） |
| `*ast.BlockStmt` | 花括号代码块 | `List`（语句列表） |
| `*ast.ImportSpec` | 导入声明 | `Path`（路径）、`Name`（别名） |
| `*ast.SelectorExpr` | 选择表达式（x.Sel） | `X`（对象）、`Sel`（选择器） |
| `*ast.BasicLit` | 基础字面量 | `Kind`（类型）、`Value`（值） |

### 遍历 AST

Go 提供两种遍历方式：

#### ast.Inspect（简洁方式）

```go
func Inspect(node Node, f func(Node) bool)

// f 返回 false 时跳过当前节点的子节点
ast.Inspect(f, func(n ast.Node) bool {
    if n == nil {
        return false
    }
    // 处理节点...
    return true
})
```

#### ast.Walk（自定义 Visitor）

```go
type Visitor interface {
    Visit(node Node) Visitor // 返回 nil 停止遍历
}

type MyVisitor struct{}

func (v MyVisitor) Visit(n ast.Node) ast.Visitor {
    if n != nil {
        // 处理节点
    }
    return v // 继续遍历子节点
}

ast.Walk(MyVisitor{}, f)
```

#### 实战：提取所有函数声明

```go
func ExtractFunctions(fset *token.FileSet, f *ast.File) {
    ast.Inspect(f, func(n ast.Node) bool {
        fn, ok := n.(*ast.FuncDecl)
        if !ok {
            return true
        }
        pos := fset.Position(fn.Pos())
        fmt.Printf("%s:%d: func %s\n", pos.Filename, pos.Line, fn.Name.Name)
        return true
    })
}
```

#### 实战：查找所有函数调用

```go
func FindCalls(f *ast.File) {
    ast.Inspect(f, func(n ast.Node) bool {
        call, ok := n.(*ast.CallExpr)
        if !ok {
            return true
        }
        switch fun := call.Fun.(type) {
        case *ast.Ident:
            fmt.Printf("调用函数: %s\n", fun.Name)
        case *ast.SelectorExpr:
            fmt.Printf("调用方法: %s.%s\n", fun.X, fun.Sel.Name)
        }
        return true
    })
}
```

## 二、go/parser — 语法解析器

`go/parser` 将 Go 源码解析为 `ast.File`。

### 核心函数

```go
import "go/parser"

// 解析单个文件
func ParseFile(fset *token.FileSet, filename string, src any, mode Mode) (*ast.File, error)
// - filename: 文件名（仅用于位置信息）
// - src: 源码（nil 时读取文件，也可以是 string/[]byte/io.Reader）
// - mode: 解析模式

// 解析表达式（适用于解析单个表达式）
func ParseExpr(x string) (ast.Expr, error)
func ParseExprFrom(fset *token.FileSet, filename string, src any, mode Mode) (ast.Expr, error)

// 解析目录（已废弃，推荐 golang.org/x/tools/go/packages）
func ParseDir(fset *token.FileSet, path string, filter func(os.FileInfo) bool, mode Mode) (map[string]*ast.Package, error)
```

### 解析模式

```go
const (
    PackageClauseOnly Mode = 1 << iota // 只解析 package 子句
    ImportsOnly                        // 只解析导入声明
    ParseComments                      // 解析注释并关联到 AST 节点
    Trace                              // 打印解析过程跟踪
    DeclarationErrors                  // 报告声明错误
    SpuriousErrors                     // 报告所有非致命错误
    SkipObjectResolution               // 跳过对象解析（Go 1.22+）
)
```

### 三种解析方式

```go
// 方式1：解析字符串
src := `package main
func Add(a, b int) int { return a + b }`
f, err := parser.ParseFile(fset, "calc.go", src, parser.ParseComments)

// 方式2：解析文件
f, err := parser.ParseFile(fset, "main.go", nil, parser.ParseComments)

// 方式3：解析表达式（动态求值、类型检查场景）
expr, err := parser.ParseExpr(`a + b*2`)
```

### 完整示例

```go
package main

import (
    "fmt"
    "go/ast"
    "go/parser"
    "go/token"
)

func main() {
    fset := token.NewFileSet()
    src := `
package main

import "fmt"

type User struct {
    Name string
    Age  int
}

func (u User) Greet() string {
    return "Hello, " + u.Name
}
`
    f, err := parser.ParseFile(fset, "example.go", src, parser.ParseComments)
    if err != nil {
        panic(err)
    }

    // 遍历所有声明
    for _, decl := range f.Decls {
        switch d := decl.(type) {
        case *ast.GenDecl:
            fmt.Printf("通用声明: %s\n", d.Tok)
            for _, spec := range d.Specs {
                switch s := spec.(type) {
                case *ast.TypeSpec:
                    fmt.Printf("  类型: %s\n", s.Name.Name)
                case *ast.ImportSpec:
                    fmt.Printf("  导入: %s\n", s.Path.Value)
                }
            }
        case *ast.FuncDecl:
            fmt.Printf("函数: %s\n", d.Name.Name)
            if d.Recv != nil {
                fmt.Printf("  接收者: %s\n", d.Recv.List[0].Type)
            }
        }
    }
}
```

## 三、go/types — 类型检查

`go/types` 在 AST 基础上执行语义分析，解析类型信息。AST 只描述代码的样子，`go/types` 告诉你每个标识符的类型。

### 核心 API

```go
import "go/types"

// 配置
type Config struct {
    GoVersion      string      // Go 版本
    Importer       Importer    // 导入器
    Error          func(error) // 错误处理
    Sizes          Sizes       // 类型大小
    FakeImportC    bool        // 模拟 import "C"
}

// 类型检查入口
func (conf *Config) Check(path string, fset *token.FileSet,
    files []*ast.File, info *Info) (*Package, error)

// 类型信息收集
type Info struct {
    Types      map[ast.Expr]TypeAndValue  // 表达式的类型
    Defs       map[*ast.Ident]Object      // 标识符的定义
    Uses       map[*ast.Ident]Object      // 标识符的使用
    Implicits  map[ast.Node]Object        // 隐式声明
    Selections map[*ast.SelectorExpr]*Selection // 选择器
    Scopes     map[ast.Node]*Scope        // 作用域
    InitOrder  []*Initializer             // 初始化顺序
}

// 类型断言
func (info *Info) TypeOf(e ast.Expr) TypeAndValue
```

### 类型检查流程

```go
func TypeCheck(f *ast.File, fset *token.FileSet) (*types.Package, *types.Info, error) {
    conf := types.Config{
        Importer: &importer{},    // 自定义/默认导入器
        Error:    func(err error) {},
    }
    info := &types.Info{
        Types: make(map[ast.Expr]types.TypeAndValue),
        Defs:  make(map[*ast.Ident]types.Object),
        Uses:  make(map[*ast.Ident]types.Object),
    }
    pkg, err := conf.Check("main", fset, []*ast.File{f}, info)
    return pkg, info, err
}
```

### 类型断言类别

```go
// info.Types 中包含每个表达式的类型
for expr, tv := range info.Types {
    fmt.Printf("表达式: %s, 类型: %s, 值: %v\n",
        expr, tv.Type, tv.Value)

    // tv.IsValue(): 是否是值表达式
    // tv.IsType():  是否是类型表达式
    // tv.IsNil():   是否是 nil
    // tv.IsBuiltin(): 是否是内置函数
    // tv.Addressable(): 是否可取地址
}
```

### 实战：类型检查并打印变量类型

```go
package main

import (
    "fmt"
    "go/ast"
    "go/importer"
    "go/parser"
    "go/token"
    "go/types"
)

func main() {
    fset := token.NewFileSet()
    src := `package main
var x int
const y = "hello"
func add(a, b int) int { return a + b }`
    f, _ := parser.ParseFile(fset, "main.go", src, 0)

    conf := types.Config{Importer: importer.Default()}
    info := &types.Info{
        Defs: make(map[*ast.Ident]types.Object),
        Uses: make(map[*ast.Ident]types.Object),
    }
    pkg, _ := conf.Check("main", fset, []*ast.File{f}, info)
    fmt.Printf("包: %s\n", pkg)

    // 打印所有定义的类型
    for id, obj := range info.Defs {
        if obj != nil {
            fmt.Printf("%s: %s (类型: %s)\n", id.Name, obj, obj.Type())
        }
    }
}
```

### 使用 `golang.org/x/tools/go/packages` 加载包

手动调用 `parser.ParseFile` + `types.Config.Check` 繁琐。推荐使用 `go/packages` 一次加载整个包及其依赖：

```go
import "golang.org/x/tools/go/packages"

cfg := &packages.Config{
    Mode: packages.NeedFiles | packages.NeedSyntax | packages.NeedTypesInfo,
}
pkgs, _ := packages.Load(cfg, "./...")

for _, pkg := range pkgs {
    for _, f := range pkg.Syntax {
        // f 是 *ast.File
        // pkg.TypesInfo 是 *types.Info
        ast.Inspect(f, func(n ast.Node) bool {
            // 静态分析逻辑
            return true
        })
    }
}
```

---

## 第二部分：动态扫描

## 四、reflect — 运行时反射

`reflect` 包在程序运行时检查类型和值。静态扫描看源码，动态扫描看实际运行的数据。

### 核心概念

```go
import "reflect"

// 两个基础入口
func TypeOf(i any) Type    // 获取类型信息
func ValueOf(i any) Value  // 获取值信息
```

### Type — 类型信息

```go
type Type interface {
    // 基础信息
    Name() string       // 类型名（如 "int", "User"）
    PkgPath() string    // 包路径
    Kind() Kind         // 底层类型类别
    String() string     // 类型字符串表示
    Size() uintptr      // 内存大小
    Align() int         // 对齐要求

    // 结构体
    NumField() int               // 字段数
    Field(i int) StructField     // 第 i 个字段
    FieldByName(name string) (StructField, bool)
    NumMethod() int              // 方法数
    Method(i int) Method         // 第 i 个方法

    // 指针/切片/map/通道
    Elem() Type                 // 元素类型
    Key() Type                  // map 的键类型（仅 map 可用）

    // 函数
    NumIn() int                 // 参数个数
    In(i int) Type              // 第 i 个参数类型
    NumOut() int                // 返回值个数
    Out(i int) Type             // 第 i 个返回值类型

    // 可赋值/可比较判断
    AssignableTo(u Type) bool
    Comparable() bool
    Implements(u Type) bool
}
```

### Kind — 类型类别

```go
const (
    Bool Kind = iota + 1
    Int, Int8, Int16, Int32, Int64
    Uint, Uint8, Uint16, Uint32, Uint64
    Float32, Float64
    Complex64, Complex128
    String, UnsafePointer

    Array, Chan, Func, Interface, Map
    Ptr, Slice, Struct

    // 未导出字段常被视为该类型
    Invalid = iota
)
```

### Value — 值操作

```go
type Value struct{ /* 未导出 */ }

func ValueOf(i any) Value

// 读取值
func (v Value) Bool() bool
func (v Value) Int() int64
func (v Value) Float() float64
func (v Value) String() string
func (v Value) Bytes() []byte
func (v Value) Interface() any

// 设置值（要求值可寻址、可设置）
func (v Value) Set(x Value)
func (v Value) SetBool(x bool)
func (v Value) SetInt(x int64)
func (v Value) SetString(x string)

// 结构体操作
func (v Value) NumField() int
func (v Value) Field(i int) Value
func (v Value) FieldByName(name string) Value

// 调用
func (v Value) Call(in []Value) []Value

// 判断
func (v Value) IsValid() bool      // 是否有效
func (v Value) IsNil() bool        // 是否为 nil
func (v Value) IsZero() bool       // 是否为零值
func (v Value) CanSet() bool       // 是否可设置
func (v Value) CanAddr() bool      // 是否可取地址
func (v Value) Elem() Value        // 指针解引用或接口解包
```

### 三大反射定律

```go
// 1. 从接口值到反射对象
t := reflect.TypeOf(42)       // TypeOf 从 interface{} 获取类型
v := reflect.ValueOf(42)      // ValueOf 从 interface{} 获取值

// 2. 从反射对象到接口值
i := v.Interface()            // Value → interface{}
fmt.Println(i.(int))          // 断言使用

// 3. 修改反射对象需要可设置
// 错误：v := reflect.ValueOf(x); v.Set(...)
// 正确：v := reflect.ValueOf(&x); v.Elem().Set(...)
```

### 实战：遍历结构体字段并读取标签

```go
type Config struct {
    Host    string `json:"host" env:"CONFIG_HOST"`
    Port    int    `json:"port" env:"CONFIG_PORT"`
    Verbose bool   `json:"verbose" env:"CONFIG_VERBOSE"`
}

func ReadStructTags(v any) {
    t := reflect.TypeOf(v)
    if t.Kind() == reflect.Ptr {
        t = t.Elem()
    }
    if t.Kind() != reflect.Struct {
        fmt.Println("不是结构体")
        return
    }

    val := reflect.ValueOf(v)
    if val.Kind() == reflect.Ptr {
        val = val.Elem()
    }

    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        fval := val.Field(i)

        fmt.Printf("字段: %-10s 类型: %-10s 值: %-10v json: %-15s env: %s\n",
            field.Name,
            field.Type,
            fval.Interface(),
            field.Tag.Get("json"),
            field.Tag.Get("env"),
        )
    }
}

// 使用
cfg := Config{Host: "localhost", Port: 8080, Verbose: true}
ReadStructTags(&cfg)
```

### 实战：动态调用方法

```go
type Calculator struct{}

func (c Calculator) Add(a, b int) int { return a + b }
func (c Calculator) Greet(name string) string { return "Hi, " + name }

func CallMethod(obj any, methodName string, args ...any) []reflect.Value {
    v := reflect.ValueOf(obj)
    method := v.MethodByName(methodName)
    if !method.IsValid() {
        panic("方法不存在: " + methodName)
    }

    in := make([]reflect.Value, len(args))
    for i, arg := range args {
        in[i] = reflect.ValueOf(arg)
    }
    return method.Call(in)
}

// 使用
calc := Calculator{}
result := CallMethod(calc, "Add", 3, 4)
fmt.Println(result[0].Int()) // 7

msg := CallMethod(calc, "Greet", "World")
fmt.Println(msg[0].String()) // "Hi, World"
```

### 实战：动态创建类型实例

```go
func CreateInstance[T any]() T {
    t := reflect.TypeOf((*T)(nil)).Elem()
    v := reflect.New(t) // *T
    return v.Elem().Interface().(T)
}

// 动态设置字段
func SetField(obj any, name string, value any) {
    v := reflect.ValueOf(obj)
    if v.Kind() == reflect.Ptr {
        v = v.Elem()
    }
    f := v.FieldByName(name)
    if f.IsValid() && f.CanSet() {
        f.Set(reflect.ValueOf(value))
    }
}
```

### 性能注意事项

- 反射操作比静态类型慢 10–100 倍
- 尽量避免在热路径中使用反射
- 使用缓存（如 `sync.Map` 缓存解析结果）减少反射次数
- 优先使用 `reflect.TypeFor[T]()`（Go 1.22+）替代 `reflect.TypeOf((*T)(nil)).Elem()`

```go
// Go 1.22+ 简洁写法
t := reflect.TypeFor[Config]()
```

---

## 第三部分：静态扫描 vs 动态扫描

## 对比

| 维度 | 静态扫描（ast/types） | 动态扫描（reflect） |
|------|----------------------|---------------------|
| 时机 | 编译时 | 运行时 |
| 输入 | 源码文件 | 运行时的值 |
| 覆盖范围 | 所有代码路径（包括未执行的） | 仅实际执行到的代码 |
| 类型信息 | 完整的类型声明和关系 | 运行时类型和具体值 |
| 修改能力 | 可生成/修改代码 | 可修改运行时的值 |
| 性能影响 | 无运行时开销 | 有运行时开销 |
| 典型场景 | 代码生成、lint 检查、自动重构 | 序列化、ORM、DI 容器 |

## 场景选择

**选择静态扫描（ast/parser/types）：**

- 编写自定义 linter 或代码规范检查
- 代码生成（如 `stringer`、protobuf 插件）
- 统计代码指标（函数数、复杂度、依赖关系）
- 重构工具（重命名、提取函数）

**选择动态扫描（reflect）：**

- `encoding/json` / `encoding/xml` 序列化
- ORM 对象关系映射（如 GORM）
- 依赖注入框架
- 通用类型比较（`reflect.DeepEqual`）
- 结构体验证

## 两种方式协调使用

某些场景需要结合两种方式。例如，一个代码生成工具先用 AST 扫描源码，生成运行时需要的元数据结构，再在运行时用 reflect 读取：

```go
// 阶段1：静态扫描（代码生成时）
// ast → 遍历结构体 → 生成 Register() 函数

// 阶段2：动态扫描（运行时）
// reflect → 读取结构体字段 → 设置值
```

---

## 第四部分：完整实战

## 实战 1：用 AST 统计 Go 文件指标

```go
func AnalyzeFile(filename string, src string) {
    fset := token.NewFileSet()
    f, err := parser.ParseFile(fset, filename, src, parser.ParseComments)
    if err != nil {
        panic(err)
    }

    var (
        funcCount   int
        typeCount   int
        varCount    int
        importCount = len(f.Imports)
    )

    ast.Inspect(f, func(n ast.Node) bool {
        switch n.(type) {
        case *ast.FuncDecl:
            funcCount++
        case *ast.TypeSpec:
            typeCount++
        case *ast.ValueSpec:
            // 检查是否是 var 声明
            if parent, ok := n.(*ast.ValueSpec); ok {
                _ = parent
                varCount++
            }
        }
        return true
    })

    fmt.Printf("文件: %s\n", filename)
    fmt.Printf("  导入: %d, 函数: %d, 类型: %d, 变量: %d\n",
        importCount, funcCount, typeCount, varCount)
}
```

## 实战 2：用 reflect 实现通用 JSON 扁平化

```go
func FlattenStruct(v any, prefix string) map[string]any {
    result := make(map[string]any)
    flatten(reflect.ValueOf(v), prefix, result)
    return result
}

func flatten(val reflect.Value, prefix string, result map[string]any) {
    if val.Kind() == reflect.Ptr {
        if val.IsNil() {
            return
        }
        val = val.Elem()
    }
    if val.Kind() != reflect.Struct {
        return
    }

    t := val.Type()
    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        fval := val.Field(i)

        // 跳过未导出字段
        if !field.IsExported() {
            continue
        }

        key := prefix + field.Name
        if tag := field.Tag.Get("json"); tag != "" {
            key = prefix + tag
        }

        if fval.Kind() == reflect.Struct {
            flatten(fval, key+".", result)
        } else {
            result[key] = fval.Interface()
        }
    }
}

// 使用
type Address struct {
    City  string `json:"city"`
    Street string `json:"street"`
}
type Person struct {
    Name    string  `json:"name"`
    Age     int     `json:"age"`
    Address Address `json:"address"`
}

p := Person{Name: "Alice", Age: 30, Address: Address{City: "Beijing", Street: "Main St"}}
flat := FlattenStruct(p, "")
// {"name": "Alice", "age": 30, "address.city": "Beijing", "address.street": "Main St"}
```

## 实战 3：自定义 linter（静态扫描）

```go
package main

import (
    "go/ast"
    "go/parser"
    "go/token"
    "os"
    "path/filepath"
    "strings"
)

// 检查是否有未处理的错误返回值
type Linter struct {
    errors []string
}

func (l *Linter) LintFile(filename string) {
    fset := token.NewFileSet()
    f, err := parser.ParseFile(fset, filename, nil, parser.ParseComments)
    if err != nil {
        return
    }

    ast.Inspect(f, func(n ast.Node) bool {
        // 检查 if err != nil { return } 模式
        if stmt, ok := n.(*ast.RangeStmt); ok {
            // 检查 range 循环中是否存在不必要的内存复制
            if len(stmt.Value) == 1 {
                l.error(fset, stmt.Pos(), "遍历大结构体时可能发生不必要的复制")
            }
        }
        return true
    })
}

func (l *Linter) error(fset *token.FileSet, pos token.Pos, msg string) {
    p := fset.Position(pos)
    l.errors = append(l.errors, fmt.Sprintf("%s:%d:%d: %s", p.Filename, p.Line, p.Column, msg))
}
```

## 参考链接

### 标准库文档

- [go/ast](https://pkg.go.dev/go/ast) — 抽象语法树类型定义
- [go/parser](https://pkg.go.dev/go/parser) — Go 源码解析器
- [go/token](https://pkg.go.dev/go/token) — 令牌与位置信息
- [go/types](https://pkg.go.dev/go/types) — Go 类型检查器
- [reflect](https://pkg.go.dev/reflect) — 运行时反射

### 工具库

- [golang.org/x/tools/go/packages](https://pkg.go.dev/golang.org/x/tools/go/packages) — 包加载（替代 ParseDir）
- [golang.org/x/tools/go/analysis](https://pkg.go.dev/golang.org/x/tools/go/analysis) — 静态分析框架
- [go/format](https://pkg.go.dev/go/format) — AST 格式化输出
