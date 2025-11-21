---
title: Golang Pongo2模板库自用文档（不全）
date: 2025-11-10
---
## 参考文档 && 引用资料
- [ZetCode文档](https://zetcode.com/golang/pongo2/)
- [Pongo2Gin的Gitlab仓库](https://gitlab.com/go-box/pongo2gin)
	- 实现了一个HTML渲染实例，可以把Gin默认的渲染实例替换掉
- [Pongo2本体](https://github.com/flosch/pongo2?tab=readme-ov-file)
- [Github-Pongo2官方手册](https://github.com/flosch/pongo2/blob/master/docs/)
- [Github-Pongo2 过滤器文档](https://github.com/flosch/pongo2/blob/master/docs/filters.md)

***
[[toc]]
## 须知
###  模板语句包裹符
- `{% %}` - 语句
- `{{ }}` - 会被打印到模板中的表达式
- `{# #}` - 注释
- `# ##` - 内联语句
## 模板管理
### 模板加载
#### 从字符串中加载模板：`pongo2.FromString`
```go
package main

import (
    "fmt"
    "log"

    "github.com/flosch/pongo2/v5"
)

func main() {

    tpl, err := pongo2.FromString("Hello {{ name }}!")

    if err != nil {
        log.Fatal(err)
    }

    res, err := tpl.Execute(pongo2.Context{"name": "John Doe"})

    if err != nil {
        log.Fatal(err)
    }

    fmt.Println(res)
}

```
#### 从文件中加载模板：`pongo2.FromFile`
```tpl
{{ name }} is a {{ occupation }}
```

```go
package main

import (
    "fmt"
    "log"

    "github.com/flosch/pongo2/v5"
)

func main() {

    tpl, err := pongo2.FromFile("message.tpl")

    if err != nil {
        log.Fatal(err)
    }

    name, occupation := "John Doe", "gardener"
    ctx := pongo2.Context{"name": name, "occupation": occupation}

    res, err := tpl.Execute(ctx)

    if err != nil {
        log.Fatal(err)
    }

    fmt.Println(res)
}

```
#### 从字节序列中加载模板：`pongo2.FromBytes`
#### 从缓存中加载模板：`pongo2.FromCache`
:::info
Pongo2Gin仓库文档的一句原文：
“Caching is implemented by the Pongo2 library itself.”
:::

### 模板渲染
*下面这些函数都接受`pongo.Context`参数作为模板上下文*
- `Execute`
- `ExecuteWriter`
- `ExecuteBytes`
## 语法
### 运算操作
```go
var (

	// Available symbols in pongo2 (within filters/tag)
	TokenSymbols = []string{

		"{{-", "-}}", "{%-", "-%}",

		"==", ">=", "<=", "&&", "||", "{{", "}}", "{%", "%}", "!=", "<>",

		"(", ")", "+", "-", "*", "<", ">", "/", "^", ",", ".", "!", "|", ":", "=", "%",
	}

	// Available keywords in pongo2
	TokenKeywords = []string{"in", "and", "or", "not", "true", "false", "as", "export"}
)
```
你知道我要说什么
#### 数学运算
#### 布尔运算
#### 逻辑连接符号

### 控制结构
#### `if-else`结构
```html
{% for todo in todos -%}
    {% if todo.Done %}
        {{- todo.Title -}}
    {% endif %}
{% endfor %}

```
#### `for`结构
```html
{% for word in words -%}
    {{ word }}
{% endfor %}
```
### 函数/过滤器：[传送门](https://github.com/flosch/pongo2/blob/master/docs/filters.md)
#### `length`：返回数组、切片、字符串和Map的长度
```go
func (v *Value) Len() int
```
> Len returns the length for an array, chan, map, slice or string. Otherwise it will return 0.


```html
{% for word in words -%}
    {{ word }} has {{ word | length }} characters
{% endfor %}

```
#### 自定义函数/过滤器：[传送门](https://github.com/flosch/pongo2/blob/0d938eb266f3/filters.go#L29)
##### 自定义过滤器
```go
func RegisterFilter(name string, fn FilterFunction) error
```
> RegisterFilter registers a new filter. If there's already a filter with the same name, RegisterFilter will panic. You usually want to call this function in the filter's init() function: [http://golang.org/doc/effective_go.html#init](http://golang.org/doc/effective_go.html#init)

##### 替换过滤器
```go
func ReplaceFilter(name string, fn FilterFunction) error
```
> ReplaceFilter replaces an already registered filter with a new implementation. Use this function with caution since it allows you to change existing filter behaviour.



## 示例
#### 在`net/http`服务器中使用模板
```go
package main

import (
    "net/http"

    "github.com/flosch/pongo2/v5"
)

type User struct {
    Name       string
    Occupation string
}

var tpl = pongo2.Must(pongo2.FromFile("users.html"))

func usersHandler(w http.ResponseWriter, r *http.Request) {

    users := []User{
        {Name: "John Doe", Occupation: "gardener"},
        {Name: "Roger Roe", Occupation: "driver"},
        {Name: "Peter Smith", Occupation: "teacher"},
    }

    err := tpl.ExecuteWriter(pongo2.Context{"users": users}, w)

    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
    }
}

func main() {

    http.HandleFunc("/users", usersHandler)
    http.ListenAndServe(":8080", nil)
}

```

## 在Gin中使用Pongo2
**可以看看[Pongo2Gin](https://gitlab.com/go-box/pongo2gin)**


***

# 页面尾部