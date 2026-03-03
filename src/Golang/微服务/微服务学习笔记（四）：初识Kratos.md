---
title: 从零开始的RPC（七）：初识Kratos
date: 2026-02-07
---
[[toc]]
:::tip 参考资料来源
- 《Go语言高并发与微服务实战》书籍
	实体书成书于20年之前，可能是在18年左右开始编写的
	彼时Go的版本为1.12.x，尚未添加泛型，PRC和Protobuf协议的一些细节也与现在不同，因此理论部分仅供参考
- B站开源Kratos微服务框架 [官方文档](https://go-kratos.dev/zh-cn/docs)
:::
***
## Kratos 快速开始
#### 环境准备
**安装依赖工具**：
- [go](https://golang.org/dl/)
- [protoc](https://github.com/protocolbuffers/protobuf)
- [protoc-gen-go](https://github.com/protocolbuffers/protobuf-go)
**建议**开启`GO111MODULE`：
```sh
go env -w GO111MODULE=on
```

**安装Kratos配套CLI工具**：
```sh
go install github.com/go-kratos/kratos/cmd/kratos/v2@latest
```

#### 创建项目
```sh
kratos new helloworld

# 国内拉取失败可使用gitee源
kratos new helloworld -r https://gitee.com/go-kratos/kratos-layout.git
# 亦可使用自定义的模板
kratos new helloworld -r xxx-layout.git
# 同时也可以通过环境变量指定源
KRATOS_LAYOUT_REPO=xxx-layout.git
# -b 指定分支 
kratos new helloworld -b main

cd helloworld
go mod download
```

```sh
# 使用--nomod添加服务，共用go.mod，大仓模式
kratos new helloworld
cd helloworld
kratos new app/user --nomod
```

### 添加Proto项目
#### 添加Proto文件
```sh
kratos proto add api/helloworld/v1/demo.proto
```

生成`api/helloworld/v1/demo.proto`文件：
```protobuf
syntax = "proto3";

package api.helloworld.v1;

option go_package = "helloworld/api/helloworld/v1;v1";
option java_multiple_files = true;
option java_package = "api.helloworld.v1";

service Demo {
    rpc CreateDemo (CreateDemoRequest) returns (CreateDemoReply);
    rpc UpdateDemo (UpdateDemoRequest) returns (UpdateDemoReply);
    rpc DeleteDemo (DeleteDemoRequest) returns (DeleteDemoReply);
    rpc GetDemo (GetDemoRequest) returns (GetDemoReply);
    rpc ListDemo (ListDemoRequest) returns (ListDemoReply);
}

message CreateDemoRequest {}
message CreateDemoReply {}

message UpdateDemoRequest {}
message UpdateDemoReply {}

message DeleteDemoRequest {}
message DeleteDemoReply {}

message GetDemoRequest {}
message GetDemoReply {}

message ListDemoRequest {}
message ListDemoReply {}
```
#### 生成Proto代码
```sh
# 可以直接通过 make 命令生成
make api

# 或使用 kratos cli 进行生成
kratos proto client api/helloworld/v1/demo.proto
```
在`proto`同目录下生成：
```sh
api/helloworld/v1/demo.pb.go
api/helloworld/v1/demo_grpc.pb.go
# 注意 http 代码只会在 proto 文件中声明了 http 时才会生成
api/helloworld/v1/demo_http.pb.go
```

#### 生成Service代码
通过 proto 文件，可以直接生成对应的 Service 实现代码：
- 使用 `-t` 指定生成目录
```sh
kratos proto server api/helloworld/v1/demo.proto -t internal/service
```

输出`internal/service/demo.go`文件
```go
package service

import (
    "context"

    pb "helloworld/api/helloworld"
)

type DemoService struct {
    pb.UnimplementedDemoServer
}

func NewDemoService() *DemoService {
    return &DemoService{}
}

func (s *DemoService) CreateDemo(ctx context.Context, req *pb.CreateDemoRequest) (*pb.CreateDemoReply, error) {
    return &pb.CreateDemoReply{}, nil
}
func (s *DemoService) UpdateDemo(ctx context.Context, req *pb.UpdateDemoRequest) (*pb.UpdateDemoReply, error) {
    return &pb.UpdateDemoReply{}, nil
}
func (s *DemoService) DeleteDemo(ctx context.Context, req *pb.DeleteDemoRequest) (*pb.DeleteDemoReply, error) {
    return &pb.DeleteDemoReply{}, nil
}
func (s *DemoService) GetDemo(ctx context.Context, req *pb.GetDemoRequest) (*pb.GetDemoReply, error) {
    return &pb.GetDemoReply{}, nil
}
func (s *DemoService) ListDemo(ctx context.Context, req *pb.ListDemoRequest) (*pb.ListDemoReply, error) {
    return &pb.ListDemoReply{}, nil
}
```

### 运行项目
- 如子目录下有多个项目则出现选择菜单
```
kratos run
```
### 查看版本
```sh
kratos -v
```
### 更新工具
```sh
kratos upgrade
```
### 更新日志
```sh
# 等同于打印 https://github.com/go-kratos/kratos/releases/latest 的版本更新日志
kratos changelog

# 打印指定版本更新日志
kratos changelog v2.1.4

#  查看从 latest 版本发布后至今的更新日志
kratos changelog dev
```
### 查看帮助
任何命令下加 `-h` 查看帮助
```sh
kratos -h
kratos new -h
```
## Kratos 简单配置
### 配置使用Goland开发
- [来源](https://go-kratos.dev/zh-cn/docs/intro/faq/#3%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8-goland-%E8%BF%9B%E8%A1%8C%E5%BC%80%E5%8F%91)
在 goland 中，可以添加构建配置如下图
![](assets/Pasted%20image%2020260209190023.png)
### 配置gorm+SQLite数据源
![](assets/Pasted%20image%2020260209213807.png)
Kratos默认不提供数据库初始化逻辑，也就是不强制使用Ent（图数据库框架）、gORM亦或是原生SQL连接：（`internal/data/data.go`）（`/data`目录是Kratos封装db、cache等组件的地方）
```go
// ProviderSet is data providers.
var ProviderSet = wire.NewSet(NewData, NewGreeterRepo)

// Data .
type Data struct {
	// TODO wrapped database client
}

// NewData .
func NewData(c *conf.Data) (*Data, func(), error) {
	cleanup := func() {
		log.Info("closing the data resources")
	}
	return &Data{}, cleanup, nil
}
```

记得引入依赖，Kratos默认没有：
```sh
go get gorm.io/gorm
go get gorm.io/driver/sqlite
go get modernc.org/sqlite
```
然后写连接方式：
```go
// Data .
type Data struct {
	// 更换为Sqlite
	DB *gorm.DB // 记得封装数据库实例
}

// 新建Sqlite连接
func newSqliteData(c *conf.Data) (data *Data, err error) {
	var db *gorm.DB
	db, err = gorm.Open(sqlite.Open(c.Database.GetSource()), &gorm.Config{})
	if err != nil {
		return nil, err
	}
	data = &Data{DB: db}

	return
}

// NewData .
func NewData(c *conf.Data) (data *Data, cleanup func(), err error) {
	switch strings.ToLower(c.Database.GetDriver()) {
	case "sqlite":
		data, err = newSqliteData(c)
		if err != nil {
			return nil, nil, err
		}
	default:
		err = errors.New(fmt.Sprintf("database driver %s not supported", c.Database.GetDriver()))
		return
	}

	cleanup = func() {
		log.Info("closing the data resources")

		sqlDB, _ := data.DB.DB()
		if err := sqlDB.Close(); err != nil {
			log.Errorf("failed to close sqlite3 connection pool: %v", err)
		}
		log.Info("successfully closed the data resources")
	}
	return data, cleanup, nil // 这里的Data实例原本是&Data{}, 也要记得改
}
```

### 配置Ent+(Pure Go)Sqlite数据源
- [来源](https://go-kratos.dev/zh-cn/docs/guide/ent/)

:::tip
Ent 是 Facebook（现 Meta）开源的一个**实体（Entity）框架**。它的核心思想不是让开发者写 SQL，也不是让开发者定义结构体，而是让开发者**定义一张“图”**。
- **所有的表都是“节点（Node）”**。
- **所有的关联（外键）都是“边（Edge）”**。
:::

:::important
Ent默认支持Mysql、PostgreSQL和Sqlite（CGO）驱动：
```go
// Dialect names for external usage.  
const (  
    MySQL    = "mysql"  
    SQLite   = "sqlite3"  
    Postgres = "postgres"
    )

// Open opens a database/sql.DB specified by the driver name and
// the data source name, and returns a new client attached to it.
// Optional parameters can be added for configuring the client.
func Open(driverName, dataSourceName string, options ...Option) (*Client, error) {
	switch driverName {
	case dialect.MySQL, dialect.Postgres, dialect.SQLite:
		drv, err := sql.Open(driverName, dataSourceName)
		if err != nil {
			return nil, err
		}
		return NewClient(append(options, Driver(drv))...), nil
	default:
		return nil, fmt.Errorf("unsupported driver: %q", driverName)
	}
}
```

这里的`sqlite3`注册名对应CGO版Sqlite驱动，在Kratos文档中给出的是：`github.com/mattn/go-sqlite3`
:::

对`modernc.org/sqlite`等非标准SQLite驱动，需要手动建立数据库实例：
```go
db, err := sql.Open("sqlite", (*conf.Data)GetSource())
```
然后创建数据库驱动：
```go
drv := entsql.OpenDB(dialect.SQLite, db) // 这一步得用回Ent指定的数据库方言，不然可能无法生成表结构
```
最后创建数据库客户端实例，并封装到`Data`中：
```go
// Data .
type Data struct {
	// wrapped database client
	// DB
	//
	// gorm数据库实例
	DB *gorm.DB
	/*
		Client

		Ent创建的数据库客户端连接, 与DB互相独立
	*/
	Client *ent.Client
}

func createSqliteClient(c *conf.Data) (data *Data, err error) {
	// 省略其他逻辑
	client := ent.NewClient(ent.Driver(drv))  
  
	if err = client.Schema.Create(context.Background()); err != nil {  
	    return nil, fmt.Errorf("failed creating schema resources: %v", err)  
	}
	
	return &Data{Client: client}, nil
}
```

:::important
- 给PureGO版Sqlite驱动应用CGO的驱动方言可能发生意外情况
:::

个人实现如下：
```go
func newSqliteDataWithEnt(c *conf.Data) (data *Data, err error) {
	switch strings.ToLower(c.Database.GetDriver()) {
	case "sqlite3", "sqlite":
		// 使用标准库sql.Open创建数据库连接，添加_pragma参数启用外键
		connStr := c.Database.GetSource()
		if !strings.Contains(connStr, "_pragma=foreign_keys") {
			// 如果连接字符串中没有外键设置，则添加默认配置
			if strings.Contains(connStr, "?") {
				connStr += "&_pragma=foreign_keys(1)&_pragma=journal_mode(WAL)&_pragma=synchronous(NORMAL)"
			} else {
				connStr += "?_pragma=foreign_keys(1)&_pragma=journal_mode(WAL)&_pragma=synchronous(NORMAL)"
			}
		}

		db, err := sql.Open("sqlite", connStr)
		if err != nil {
			return nil, fmt.Errorf("failed to open sqlite connection: %v", err)
		}

		// 验证外键是否启用
		var fkEnabled int
		err = db.QueryRow("PRAGMA foreign_keys;").Scan(&fkEnabled)
		if err != nil {
			log.Errorf("查询外键状态失败: %v", err)
		} else {
			// log.Infof("外键启用状态: %d", fkEnabled)
		}

		drv := entsql.OpenDB(dialect.SQLite, db)
		client := ent.NewClient(ent.Driver(drv))

		if err = client.Schema.Create(context.Background()); err != nil {
			return nil, fmt.Errorf("failed creating schema resources: %v", err)
		}

		return &Data{Client: client}, nil
	}

	return nil, err
}
```

## Kratos 设计哲学
### 错误处理
- [来源](https://go-kratos.dev/zh-cn/docs/intro/design/#%E9%94%99%E8%AF%AF%E5%A4%84%E7%90%86)
Kratos的错误类型包含下面四个*逻辑* 字段：
1. `code` ：状态码
2. `reason` 业务的具体错误码，为可读的字符串，能够表明，在同一个服务中应该唯一。
3. `message` 用户可读的信息，可以在客户端（App、浏览器等）进行相应的展示给用户看。
4. `metadata` 为一些附加信息，可以作为补充信息使用。

:::note gRPC的**富错误类型**
包含下面三个*逻辑* 字段：
1. **Code**: 整数状态码。
2. **Message**: 错误描述字符串。
3. **Details**: 一个 Any 类型的数组。可以携带任何序列化后的 Protobuf 消息。

:::

示例错误消息如下：
```json
{
    // 错误码，跟 http-status 一致，并且在 grpc 中可以转换成 grpc-status
    "code": 500,
    // 错误原因，定义为业务判定错误码
    "reason": "USER_NOT_FOUND",
    // 错误信息，为用户可读的信息，可作为用户提示内容
    "message": "invalid argument error",
    // 错误元信息，为错误添加附加可扩展信息
    "metadata": {"some-key": "some-value"}
}
```

在Kratos中可以使用proto文件定义业务错误，并通过工具生成对应的处理逻辑和方法（如使用layout中提供的`make errors`指令）

#### 错误定义
```protobuf
syntax = "proto3";

package api.blog.v1;
import "errors/errors.proto";

option go_package = "github.com/go-kratos/examples/blog/api/v1;v1";

enum ErrorReason {
  // 设置缺省错误码
  option (errors.default_code) = 500;

  // 为某个枚举单独设置错误码
  USER_NOT_FOUND = 0 [(errors.code) = 404];
  CONTENT_MISSING = 1 [(errors.code) = 400];;
}
```
#### 错误创建
- 项目里的`errors`包默认用的是Kratos的
```go
// 通过 errors.New() 响应错误
errors.New(500, "USER_NAME_EMPTY", "user name is empty")

// 通过 proto 生成的代码响应错误，并且包名应替换为自己生成代码后的 package name
api.ErrorUserNotFound("user %s not found", "kratos")

// 传递metadata
err := errors.New(500, "USER_NAME_EMPTY", "user name is empty")
err = err.WithMetadata(map[string]string{
    "foo": "bar",
})
```

#### 错误断言
```go
err := wrong()

// 通过 errors.Is() 断言
if errors.Is(err,errors.BadRequest("USER_NAME_EMPTY","")) {
  // do something
}

// 通过判断 *Error.Reason 和 *Error.Code
e := errors.FromError(err)
if  e.Reason == "USER_NAME_EMPTY" && e.Code == 500 {
  // do something
}

// 通过 proto 生成的代码断言错误，并且包名应替换为自己生成代码后的 package name
if api.IsUserNotFound(err) {
  // do something
}
```
## Kratos启动流程
### `cmd/`目录下的项目目录
- `main.go`
- `wire.go`和`wire_gen.go`由Wire自动生成，暂时不做讨论


## Kratos练习
### 在Kratos中注册consul实例并通过HTTP方式与Consul交互
#### 使用默认方式注册consul实例
- 客户端（也就是Kratos项目）的Service Name（也就是代码中的`.Name()`方法和`Name`变量）不能为空
- consul库默认使用HTTP客户端，默认使用`127.0.0.1:8500`作为服务地址
```go
import (
    consul "github.com/go-kratos/kratos/contrib/registry/consul/v2"
    "github.com/hashicorp/consul/api"
)

func init() {  
    flag.StringVar(&Name, "name", "helloworld-srv", "客户端服务名, 使用方法: -name YOUR-SERVICE-NAME")  
    flag.StringVar(&flagconf, "conf", "../../configs", "config path, eg: -conf config.yaml")  
}  
  
func newApp(logger log.Logger, gs *grpc.Server, hs *http.Server) *kratos.App {  
    // 注册consul实例  
    consulConfig := api.DefaultConfig()  
    consulConfig.Address = "192.168.100.133:8500"  
    // consulConfig.Scheme = "http"  
    // consulConfig.Token = "YOUR-ACL-TOKEN"    // consulConfig.WaitTime = 5 * time.Second  
    client, err := api.NewClient(consulConfig)  
    // 设置连接参数, 包括代理、请求超时时间和是否启用HTTP2等  
    if err != nil {  
       panic(err)  
    }  
    reg := consul.New(client)  
  
    app := kratos.New(  
       kratos.ID(id),  
       kratos.Name(Name),  
       kratos.Version(Version),  
       kratos.Metadata(map[string]string{}),  
       kratos.Logger(logger),  
       kratos.Server(  
          gs,  
          hs,  
       ),  
  
       // 添加注册器  
       kratos.Registrar(reg),  
    )  
  
    return app  
}
```

`api.DefaultConfig`的实现：
```go
// github.com\hashicorp\consul\api@v1.33.2\api.go

// DefaultConfig returns a default configuration for the client. By default this
// will pool and reuse idle connections to Consul. If you have a long-lived  
// client object, this is the desired behavior and should make the most efficient  
// use of the connections to Consul. If you don't reuse a client object, which  
// is not recommended, then you may notice idle connections building up over  
// time. To avoid this, use the DefaultNonPooledConfig() instead.  
func DefaultConfig() *Config {  
    return defaultConfig(nil, cleanhttp.DefaultPooledTransport)  
}

// DefaultNonPooledConfig returns a default configuration for the client which
// does not pool connections. This isn't a recommended configuration because it
// will reconnect to Consul on every request, but this is useful to avoid the
// accumulation of idle connections if you make many client objects during the
// lifetime of your application.
func DefaultNonPooledConfig() *Config {
	return defaultConfig(nil, cleanhttp.DefaultTransport)
}

// defaultConfig returns the default configuration for the client, using the
// given function to make the transport.
func defaultConfig(logger hclog.Logger, transportFn func() *http.Transport) *Config {
	if logger == nil {
		logger = hclog.New(&hclog.LoggerOptions{
			Name: "consul-api",
		})
	}

	config := &Config{
		Address:   "localhost:8500",
		Scheme:    "http",
		Transport: transportFn(),
	}

	if addr := os.Getenv(HTTPAddrEnvName); addr != "" {
		config.Address = addr
	}

	if tokenFile := os.Getenv(HTTPTokenFileEnvName); tokenFile != "" {
		config.TokenFile = tokenFile
	}

	if token := os.Getenv(HTTPTokenEnvName); token != "" {
		config.Token = token
	}

	if auth := os.Getenv(HTTPAuthEnvName); auth != "" {
		var username, password string
		if strings.Contains(auth, ":") {
			split := strings.SplitN(auth, ":", 2)
			username = split[0]
			password = split[1]
		} else {
			username = auth
		}

		config.HttpAuth = &HttpBasicAuth{
			Username: username,
			Password: password,
		}
	}

	if ssl := os.Getenv(HTTPSSLEnvName); ssl != "" {
		enabled, err := strconv.ParseBool(ssl)
		if err != nil {
			logger.Warn(fmt.Sprintf("could not parse %s", HTTPSSLEnvName), "error", err)
		}

		if enabled {
			config.Scheme = "https"
		}
	}

	if v := os.Getenv(HTTPTLSServerName); v != "" {
		config.TLSConfig.Address = v
	}
	if v := os.Getenv(HTTPCAFile); v != "" {
		config.TLSConfig.CAFile = v
	}
	if v := os.Getenv(HTTPCAPath); v != "" {
		config.TLSConfig.CAPath = v
	}
	if v := os.Getenv(HTTPClientCert); v != "" {
		config.TLSConfig.CertFile = v
	}
	if v := os.Getenv(HTTPClientKey); v != "" {
		config.TLSConfig.KeyFile = v
	}
	if v := os.Getenv(HTTPSSLVerifyEnvName); v != "" {
		doVerify, err := strconv.ParseBool(v)
		if err != nil {
			logger.Warn(fmt.Sprintf("could not parse %s", HTTPSSLVerifyEnvName), "error", err)
		}
		if !doVerify {
			config.TLSConfig.InsecureSkipVerify = true
		}
	}

	if v := os.Getenv(HTTPNamespaceEnvName); v != "" {
		config.Namespace = v
	}

	if v := os.Getenv(HTTPPartitionEnvName); v != "" {
		config.Partition = v
	}

	return config
}
```

#### consul注册与反注册流程（程序流）
*由 调用方 到 实现方*
1. `cmd/<PROJECT>/main.go`/Kratos服务
	1. 【开发者】创建配置，再用配置创建consul实例
	2. Kratos逐个启动所有服务，包括默认http服务和默认grpc服务（标号①）
		![](assets/Pasted%20image%2020260211210632.png)
	3. 待自身服务启动后，Kratos调用consul实例的`Register`接口进行**服务注册**（标号②）
		这是**单实例单注册**模式，即一个Kratos程序在其整个生命周期内只向一个服务注册一次
		1. `kratos\contrib\registry\consul\v2@v2.0.0-20260105075216-c7a58ff59f80\registry.go`
			-  调用来自`client.go`的`Register(ctx context.Context, svc *registry.ServiceInstance, enableHealthCheck bool) error`和`Deregister(ctx context.Context, serviceID string) error`方法
				这里只是套个壳传递一下ctx，没什么好说的
		2. `kratos\contrib\registry\consul\v2@v2.0.0-20260105075216-c7a58ff59f80\client.go`
			- 实现`Register(ctx context.Context, svc *registry.ServiceInstance, enableHealthCheck bool) error`方法
				1. 遍历服务实例信息中的`Endpoints`端点，取出域名协议、域名地址和端口，构建切片；检查当前客户端是否启用`enableHealthCheck`，如果启用，就在`AgentServiceRegistration`实例的`Checks`切片中追加要进行健康信息上传的服务信息（包括自身地址、轮询间隔、自身终止前的回收方法和请求超时时间）
				2. 给`Client`实例的map上锁，为当前服务创建协程上下文和`cancel()`；检查是否开启心跳检测，如果设置开启，就创建协程轮询探测服务，一旦心跳中断，就关闭协程上下文，并从map中移除服务实例
				3. 调用`c.cli.Agent().ServiceRegisterOpts`方法正式向consul注册当前服务信息
					`c.cli.Agent().ServiceRegisterOpts`是对`agent.go`中的`serviceRegister(service *AgentServiceRegistration, opts ServiceRegisterOpts) error`的套壳，以下是该方法的流程：
					1. 向`<consul_schema>://<consul_ip>:<consul_port>/v1/agent/service/register`发起`PUT`请求；如果是要更换心跳检查，就设置`replace-existing-checks`（GET参数）为`true`；如果设置了Token，就用Token的值作为`X-Consul-Token`的值
					2. 如果请求响应为`200 Status OK`，就返回`nil`错误；如果不是就返回`err`
					- hashicorp在这里使用了他们自己封装的带`ctx`的http客户端，并手动close掉请求响应缓冲区，以承载consul所需的高频请求，并避免可能的fd泄露
			- 实现`Deregister(ctx context.Context, serviceID string) error`方法
				- `agent.go`在这里的实现与上面类似，只是少了很多配置项的检查逻辑
				1. `PUT`请求`"<consul_schema>://<consul_ip>:<consul_port>/v1/agent/service/deregister/%s", serviceID`
					![](assets/Pasted%20image%2020260211214635.png)
				2. 请求前会先设置一下参数；不太优雅，但好歹也是编译器确定的，并且每一个参数都代表着一个很重要的分布式系统功能
					![](assets/Pasted%20image%2020260211214712.png)
		3. `github.com\hashicorp\consul\api@v1.33.2\agent.go`
	4. Kratos服务的`chan os.Signal`有缓冲通道接收到任何信号后，调用`app.Stop`方法；`app.Stop`方法首先在完全终止前循环遍历调用`beforeStop`方法，然后**反注册**服务，最后取消app实例所派生的协程的上下文
	5. 所有协程全部关闭后，`app.Run`方法所在协程的才可以退出，进而退出`main`方法所在的协程，程序退出

:::note Endpoints 是哪来的？
- **自动探测**：如果你在配置里没写死 IP，Kratos 会在 `Register` 前调用其内部的 `endpoint.go`。
    
- **逻辑**：它会扫描本地网卡，排除 `127.0.0.1`，找到第一个合法的内网 IP，并结合 Server 监听的端口，自动拼凑出 `grpc://192.168.1.5:9000` 这样的字符串。
:::

:::note `Endpoints`如何生成
1. `main`函数中由`config.New(config.WithSource(file.NewSource(flagconf)))`读取配置文件并生成`endpoints`切片

2. 而在启动`app`实例前会调用`buildInstance()`生成实例，其中先读取配置值，然后遍历注册的服务，使用自身服务监听的IP地址或域名生成相应的consul（或其他服务）端点
```go
func (a *App) buildInstance() (*registry.ServiceInstance, error) {
	endpoints := make([]string, 0, len(a.opts.endpoints))
	for _, e := range a.opts.endpoints {
		endpoints = append(endpoints, e.String())
	}
	if len(endpoints) == 0 {
		for _, srv := range a.opts.servers {
			if r, ok := srv.(transport.Endpointer); ok {
				e, err := r.Endpoint()
				if err != nil {
					return nil, err
				}
				endpoints = append(endpoints, e.String())
			}
		}
	}
	return &registry.ServiceInstance{
		ID:        a.opts.id,
		Name:      a.opts.name,
		Version:   a.opts.version,
		Metadata:  a.opts.metadata,
		Endpoints: endpoints,
	}, nil
}
```
:::


`consul`库的`client.go`中`Register`和`Deregister`方法实现：
```go
// Register register service instance to consul
func (c *Client) Register(ctx context.Context, svc *registry.ServiceInstance, enableHealthCheck bool) error {
	addresses := make(map[string]api.ServiceAddress, len(svc.Endpoints))
	checkAddresses := make([]string, 0, len(svc.Endpoints))
	for _, endpoint := range svc.Endpoints {
		raw, err := url.Parse(endpoint)
		if err != nil {
			return err
		}
		addr := raw.Hostname()
		port, _ := strconv.ParseUint(raw.Port(), 10, 16)

		checkAddresses = append(checkAddresses, net.JoinHostPort(addr, strconv.FormatUint(port, 10)))
		addresses[raw.Scheme] = api.ServiceAddress{Address: endpoint, Port: int(port)}
	}
	tags := []string{fmt.Sprintf("version=%s", svc.Version)}
	if len(c.tags) > 0 {
		tags = append(tags, c.tags...)
	}
	asr := &api.AgentServiceRegistration{
		ID:              svc.ID,
		Name:            svc.Name,
		Meta:            svc.Metadata,
		Tags:            tags,
		TaggedAddresses: addresses,
	}
	if len(checkAddresses) > 0 {
		host, portRaw, _ := net.SplitHostPort(checkAddresses[0])
		port, _ := strconv.ParseInt(portRaw, 10, 32)
		asr.Address = host
		asr.Port = int(port)
	}
	if enableHealthCheck {
		for _, address := range checkAddresses {
			asr.Checks = append(asr.Checks, &api.AgentServiceCheck{
				TCP:                            address,
				Interval:                       fmt.Sprintf("%ds", c.healthcheckInterval),
				DeregisterCriticalServiceAfter: fmt.Sprintf("%ds", c.deregisterCriticalServiceAfter),
				Timeout:                        "5s",
			})
		}
		// custom checks
		asr.Checks = append(asr.Checks, c.serviceChecks...)
	}
	if c.heartbeat {
		asr.Checks = append(asr.Checks, &api.AgentServiceCheck{
			CheckID:                        "service:" + svc.ID,
			TTL:                            fmt.Sprintf("%ds", c.healthcheckInterval*2),
			DeregisterCriticalServiceAfter: fmt.Sprintf("%ds", c.deregisterCriticalServiceAfter),
		})
	}

	c.lock.Lock()
	if cc, ok := c.cancelers[svc.ID]; ok {
		cc.cancel()
		<-cc.done
	}
	var cc *canceler
	if c.heartbeat {
		cancelCtx, cancel := context.WithCancel(context.Background())
		cc = &canceler{
			ctx:    cancelCtx,
			cancel: cancel,
			done:   make(chan struct{}),
		}
		c.cancelers[svc.ID] = cc
		go func() {
			<-cc.done
			cc.cancel()
			c.lock.Lock()
			if c.cancelers[svc.ID] == cc {
				delete(c.cancelers, svc.ID)
			}
			c.lock.Unlock()
		}()
	}
	c.lock.Unlock()

	err := c.cli.Agent().ServiceRegisterOpts(asr, api.ServiceRegisterOpts{}.WithContext(ctx))
	if err != nil {
		if c.heartbeat {
			close(cc.done)
		}
		return err
	}

	if c.heartbeat {
		go func() {
			defer close(cc.done)
			err = c.cli.Agent().UpdateTTL("service:"+svc.ID, "pass", "pass")
			if err != nil {
				log.Errorf("[Consul]update ttl heartbeat to consul failed!err:=%v", err)
			}
			ticker := time.NewTicker(time.Second * time.Duration(c.healthcheckInterval))
			defer ticker.Stop()
			for {
				select {
				case <-cc.ctx.Done():
					_ = c.cli.Agent().ServiceDeregister(svc.ID)
					return
				case <-ticker.C:
					err = c.cli.Agent().UpdateTTLOpts("service:"+svc.ID, "pass", "pass", new(api.QueryOptions).WithContext(cc.ctx))
					if errors.Is(err, context.Canceled) || errors.Is(err, context.DeadlineExceeded) {
						_ = c.cli.Agent().ServiceDeregister(svc.ID)
						return
					}
					if err != nil {
						log.Errorf("[Consul] update ttl heartbeat to consul failed! err=%v", err)
						// when the previous report fails, try to re register the service
						if err := sleepCtx(cc.ctx, time.Duration(rand.IntN(5))*time.Second); err != nil {
							_ = c.cli.Agent().ServiceDeregister(svc.ID)
							return
						}
						if err := c.cli.Agent().ServiceRegisterOpts(asr, api.ServiceRegisterOpts{}.WithContext(cc.ctx)); err != nil {
							log.Errorf("[Consul] re registry service failed!, err=%v", err)
						} else {
							log.Warn("[Consul] re registry of service occurred success")
						}
					}
				}
			}
		}()
	}
	return nil
}


// Deregister service by service ID
func (c *Client) Deregister(ctx context.Context, serviceID string) error {
	c.lock.RLock()
	cc, ok := c.cancelers[serviceID]
	c.lock.RUnlock()
	if ok {
		cc.cancel()
		<-cc.done
	}

	err := c.cli.Agent().ServiceDeregisterOpts(serviceID, new(api.QueryOptions).WithContext(ctx))
	var se api.StatusError
	if errors.As(err, &se) && se.Code == 404 {
		// not found
		err = nil
	}
	return err
}
```
### 在Kratos中尝试服务发现
#### 使用gRPC通过consul实例发现其他服务
:::note Kratos自定义服务发现URL
一个标准的 Kratos 服务发现 URL 遵循 RFC 3986 规范，通常分为三个部分：
`协议`://`节点身份`/`端点`
- **Scheme (`discovery`)/协议**: 这是一个“信号灯”。它告诉 gRPC 客户端：不要用标准的 DNS 去解析这个地址，而是去调用一个名为 `discovery` 的自定义解析器（Resolver）。
- **Authority (通常为空/节点身份**: 在 `discovery:///` 中，三个斜杠意味着 Authority 部分被跳过了。如果填写，通常用于指定特定的注册中心集群，但 Kratos 默认通过代码注入 `Discovery` 实例，所以这里通常为空。
- **Endpoint (`helloworld`)/端点**: 这是目标服务的**唯一标识名**（Service Name）。Resolver 会拿着这个名字去 Consul 或 Etcd 的“通讯录”里翻找对应的 IP 列表。

:::

```kotlin
package main

import (
	"context"
	v1 "helloworld/api/helloworld/v1"
	"os"
	"os/signal"
	"syscall"

	"github.com/go-kratos/kratos/contrib/registry/consul/v2"
	"github.com/go-kratos/kratos/v2/transport/grpc"
	"github.com/hashicorp/consul/api"
)

func main() {
	// os.Signal Context
	ctx, cancel := signal.NotifyContext(context.Background(),
		os.Interrupt, syscall.SIGINT, syscall.SIGTERM)
	defer cancel()

	cli, _ := api.NewClient(api.DefaultConfig())
	// 使用服务发现的consul库: "github.com/go-kratos/kratos/contrib/registry/consul/v2"
	discoveryCenter := consul.New(cli)

	conn, err := grpc.DialInsecure(
		ctx,
		// /<SERVICE_NAME> 最前面得有一个斜杠
		grpc.WithEndpoint("discovery:///helloworld-srv"),
		grpc.WithDiscovery(discoveryCenter),
	)
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	// 调用greeter.SayHello方法
	c := v1.NewGreeterClient(conn)
	if res, err := c.SayHello(ctx, &v1.HelloRequest{Name: "kratos"}); err != nil {
		panic(err)
	} else {
		println(res.Message)
	}
	// INFO msg=[resolver] update instances: [{"id":"DESKTOP-82POIPF","name":"helloworld-srv","version":"","metadata":null,"endpoints":["grpc://192.168.100.1:9000","http://192.168.100.1:8000"]}]
	// Hello kratos
}
```
## Kratos心得
### 加一个服务有多费劲
> 在 Kratos 里加一个服务需要动 6-7 个模块

#### 1. **API 定义层**（1 个模块）
```sh
# 生成proto文件
kratos proto add api/<PROJECT_NAME>/v1/xxx.proto

# 编译生成客户端文件
make api
kratos proto client api/<PROJECT_NAME>/v1/xxx.proto
```

| 文件 | 操作 | 说明 |
|------|------|------|
| `api/xxx/v1/xxx.proto` | 新建 | 定义 proto 服务和消息 |
| `api/xxx/v1/xxx.pb.go` | 自动生成 | proto 消息代码 |
| `api/xxx/v1/xxx_grpc.pb.go` | 自动生成 | gRPC 服务代码 |

---

#### 2. **服务实现层**（1 个模块）
```sh
# 编译生成服务端文件(默认不包括http_rpc)
kratos proto server api/<PROJECT_NAME>/v1/xxx.proto -t internal/service
```

| 文件 | 操作 | 说明 |
|------|------|------|
| `internal/service/xxx.go` | 新建 | 实现服务逻辑 |
| `internal/service/service.go` | **显式注册** | 添加到 `service.ProviderSet` |

```go
// internal/service/service.go
var ProviderSet = wire.NewSet(
    NewGreeterService,
    NewCallItselfService,  // ← 新增
)
```

---

#### 3. **数据访问层**（可选，1 个模块）

如果服务依赖其他 gRPC 服务：

| 文件 | 操作 | 说明 |
|------|------|------|
| `internal/data/xxxClient.go` | 新建 | 创建 gRPC 客户端 |
| `internal/data/data.go` | **显式注册** | 添加到 `data.ProviderSet` |

```go
// internal/data/data.go
var ProviderSet = wire.NewSet(
    NewData,
    NewGreeterRepo,
    NewGreeterRPCClient,  // ← 新增
)
```

---

#### 4. **传输层**（1 个模块）

| 文件 | 操作 | 说明 |
|------|------|------|
| `internal/server/grpc.go` | **显式注册** | 注册到 gRPC 服务器 |

```go
// internal/server/grpc.go
func NewGRPCServer(..., callItself *service.CallItselfService, ...) *grpc.Server {
    srv := grpc.NewServer(opts...)
    v1.RegisterGreeterServer(srv, greeter)
    v1.RegisterCallItselfServer(srv, callItself)  // ← 新增
    return srv
}
```

---

#### 5. **服务发现层**（可选，1 个模块）

如果需要服务发现：

| 文件 | 操作 | 说明 |
|------|------|------|
| `internal/server/registry.go` | 新建/修改 | 创建 Discovery/Registrar |
| `internal/server/server.go` | **显式注册** | 添加到 `server.ProviderSet` |

```go
// internal/server/server.go
var ProviderSet = wire.NewSet(
    NewGRPCServer,
    NewHTTPServer,
    NewConsulRegistrar,
    NewConsulDiscovery,  // ← 新增
)
```

---

#### 6. **依赖注入层**（1 个模块）

| 文件                           | 操作     | 说明           |
| ---------------------------- | ------ | ------------ |
| `cmd/helloworld/wire.go`     | 通常不需要改 | Wire 自动解析依赖  |
| `cmd/helloworld/wire_gen.go` | 自动生成   | 运行 `wire` 命令 |

---

#### 总结

##### 需要显式注册的地方（4-5 处）

1. **`internal/service/service.go`** - 注册到 `service.ProviderSet`
2. **`internal/server/grpc.go`** - 注册到 gRPC 服务器
3. **`internal/server/server.go`** - 注册到 `server.ProviderSet`
4. **`internal/data/data.go`** - 如果有依赖，注册到 `data.ProviderSet`
5. **`internal/server/registry.go`** - 如果需要服务发现，注册到 `server.ProviderSet`

##### 完整流程

```
1. 定义 proto
   ↓
2. 生成 pb.go 和 _grpc.pb.go
   ↓
3. 实现服务逻辑
   ↓
4. 注册到 service.ProviderSet
   ↓
5. 注册到 gRPC Server
   ↓
6. 运行 wire 生成依赖注入代码
   ↓
7. 启动服务
```

##### 最小化场景（无服务发现）

只需动 3 个模块：
1. `api/` - 定义 proto
2. `internal/service/` - 实现并注册服务
3. `internal/server/grpc.go` - 注册到 gRPC 服务器
***
# 页面底部