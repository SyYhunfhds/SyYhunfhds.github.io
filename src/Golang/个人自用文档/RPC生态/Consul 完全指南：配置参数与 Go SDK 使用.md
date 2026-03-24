---
title: Consul 完全指南：配置参数与 Go SDK 使用
date: 2026-03-24
footer: Trae编辑
---

# Consul 完全指南：配置参数与 Go SDK 使用

:::note 参考资料
- [Consul 官方文档](https://www.consul.io/docs)
- [Consul Go SDK 文档](https://pkg.go.dev/github.com/hashicorp/consul/api)
:::

[[toc]]

## 1. Consul 概述

Consul 是 HashiCorp 公司开发的开源服务网格解决方案，提供服务发现、健康检查、配置管理和服务分割等功能。

### 1.1 核心特性

:::info 核心功能
- **服务发现**：自动检测和注册服务，支持 DNS 和 HTTP 接口
- **健康检查**：监控服务健康状态，自动剔除不健康的服务
- **配置管理**：基于 Key/Value 存储的配置中心
- **多数据中心**：原生支持多数据中心部署
- **服务网格**：通过 Connect 功能提供服务间的安全通信
:::

### 1.2 架构组成

| **组件** | **描述** | **职责** |
| -------- | -------- | -------- |
| Agent | 运行在每个节点上的守护进程 | 服务注册、健康检查、维护成员关系 |
| Server | 特殊的 Agent，参与共识 | 存储数据、处理查询请求、选举领导者 |
| Client | 普通的 Agent | 转发请求到 Server，执行健康检查 |
| Leader | 从 Server 中选举出的领导者 | 处理所有写操作，维护集群状态 |

## 2. 安装与配置

### 2.1 安装 Consul

```bash
# Linux
sudo apt-get install consul  # Ubuntu/Debian
sudo yum install consul      # CentOS/RHEL

# macOS
brew install consul

# Windows
# 从官网下载安装包并解压

# Docker
docker pull hashicorp/consul
docker run -d --name consul -p 8500:8500 -p 8300:8300 -p 8301:8301 -p 8302:8302 -p 8600:8600/udp hashicorp/consul agent -dev -client=0.0.0.0
```

### 2.2 基本配置

#### 2.2.1 开发模式启动

```bash
# 开发模式（仅用于测试）
consul agent -dev

# 访问 Web UI
# http://localhost:8500
```

#### 2.2.2 生产模式配置

创建配置文件 `consul.hcl`：

```hcl
# 基本配置
datacenter = "dc1"
data_dir = "/opt/consul/data"

# 服务器配置
server = true
bootstrap_expect = 3  # 集群节点数

# 网络配置
bind_addr = "192.168.1.100"
advertise_addr = "192.168.1.100"

# 端口配置
ports {
  http = 8500
  https = -1  # 禁用 HTTPS
  grpc = 8502
  serf_lan = 8301
  serf_wan = 8302
  server = 8300
}

# 日志配置
log_level = "INFO"

# 健康检查配置
telemetry {
  prometheus_retention_time = "24h"
  disable_hostname = true
}

# 自动加密
auto_encrypt {
  allow_tls = true
}

# ACL 配置
acl {
  enabled = true
  default_policy = "deny"
  enable_token_persistence = true
}
```

启动命令：

```bash
consul agent -config-file=consul.hcl
```

#### 2.2.3 Docker 环境配置

**开发模式**：

```bash
docker run -d \
  --name consul-dev \
  -p 8500:8500 \
  -p 8300:8300 \
  -p 8301:8301 \
  -p 8302:8302 \
  -p 8600:8600/udp \
  hashicorp/consul agent -dev -client=0.0.0.0
```

**生产模式**：

1. 创建 Docker Compose 文件 `docker-compose.yml`：

```yaml
version: '3'
services:
  consul-server-1:
    image: hashicorp/consul
    container_name: consul-server-1
    ports:
      - "8500:8500"
      - "8300:8300"
      - "8301:8301"
      - "8302:8302"
      - "8600:8600/udp"
    volumes:
      - ./consul-data/server1:/consul/data
    command: >
      agent -server -bootstrap-expect=3 -data-dir=/consul/data 
      -node=consul-server-1 -bind=0.0.0.0 -client=0.0.0.0

  consul-server-2:
    image: hashicorp/consul
    container_name: consul-server-2
    ports:
      - "8501:8500"
    volumes:
      - ./consul-data/server2:/consul/data
    command: >
      agent -server -bootstrap-expect=3 -data-dir=/consul/data 
      -node=consul-server-2 -bind=0.0.0.0 -client=0.0.0.0 
      -retry-join=consul-server-1

  consul-server-3:
    image: hashicorp/consul
    container_name: consul-server-3
    ports:
      - "8502:8500"
    volumes:
      - ./consul-data/server3:/consul/data
    command: >
      agent -server -bootstrap-expect=3 -data-dir=/consul/data 
      -node=consul-server-3 -bind=0.0.0.0 -client=0.0.0.0 
      -retry-join=consul-server-1

  consul-client:
    image: hashicorp/consul
    container_name: consul-client
    ports:
      - "8503:8500"
    volumes:
      - ./consul-data/client:/consul/data
    command: >
      agent -data-dir=/consul/data 
      -node=consul-client -bind=0.0.0.0 -client=0.0.0.0 
      -retry-join=consul-server-1
```

2. 启动集群：

```bash
# 创建数据目录
mkdir -p consul-data/server1 consul-data/server2 consul-data/server3 consul-data/client

# 启动容器
docker-compose up -d

# 查看集群状态
docker exec consul-server-1 consul members
```

**Docker 环境下的 KV 数据持久化**：

- 通过 `volumes` 挂载本地目录到容器的 `/consul/data` 目录
- 确保本地目录有正确的权限
- 这样即使容器重启，KV 数据也会保存在本地挂载的目录中

**注意事项**：

- 在 Docker 环境中，`data_dir` 默认为 `/consul/data`
- 需要通过 `volumes` 挂载持久化存储
- 集群模式下，所有服务器节点都需要挂载数据卷
- 生产环境中建议使用外部存储卷（如 NFS、EBS 等）

## 3. 核心配置参数

### 3.1 基本配置

| **参数** | **类型** | **默认值** | **描述** |
| -------- | -------- | ---------- | -------- |
| `datacenter` | string | "dc1" | 数据中心名称 |
| `data_dir` | string | - | 数据存储目录 |
| `log_level` | string | "INFO" | 日志级别（TRACE, DEBUG, INFO, WARN, ERROR） |
| `node_name` | string | 主机名 | 节点名称 |
| `bind_addr` | string | "0.0.0.0" | 绑定地址 |
| `advertise_addr` | string | - | 广播地址 |

### 3.2 服务器配置

| **参数** | **类型** | **默认值** | **描述** |
| -------- | -------- | ---------- | -------- |
| `server` | bool | false | 是否为服务器节点 |
| `bootstrap_expect` | int | 0 | 期望的服务器节点数 |
| `bootstrap` | bool | false | 是否为引导节点 |
| `retry_join` | []string | [] | 加入集群的节点地址 |
| `retry_interval` | string | "30s" | 重试加入的间隔 |
| `retry_max` | int | 0 | 最大重试次数（0 表示无限） |

### 3.3 网络配置

| **参数** | **类型** | **默认值** | **描述** |
| -------- | -------- | ---------- | -------- |
| `ports.http` | int | 8500 | HTTP API 端口 |
| `ports.https` | int | -1 | HTTPS API 端口（-1 表示禁用） |
| `ports.grpc` | int | 8502 | gRPC API 端口 |
| `ports.serf_lan` | int | 8301 | LAN 段 Serf 端口 |
| `ports.serf_wan` | int | 8302 | WAN 段 Serf 端口 |
| `ports.server` | int | 8300 | 服务器 RPC 端口 |

### 3.4 健康检查配置

| **参数** | **类型** | **默认值** | **描述** |
| -------- | -------- | ---------- | -------- |
| `checks` | []Check | [] | 健康检查配置 |
| `check_interval` | string | "10s" | 健康检查间隔 |
| `check_timeout` | string | "1s" | 健康检查超时 |
| `check_deregister_critical_service_after` | string | "30m" | 服务被注销前的临界时间 |

### 3.5 ACL 配置

| **参数** | **类型** | **默认值** | **描述** |
| -------- | -------- | ---------- | -------- |
| `acl.enabled` | bool | false | 是否启用 ACL |
| `acl.default_policy` | string | "allow" | 默认策略（allow/deny） |
| `acl.enable_token_persistence` | bool | false | 是否持久化 token |
| `acl.tokens.master` | string | - | 主 token |
| `acl.tokens.agent` | string | - | Agent token |
| `acl.tokens.default` | string | - | 默认 token |

## 4. Go SDK 使用

### 4.1 安装 SDK

```bash
go get github.com/hashicorp/consul/api
```

### 4.2 初始化客户端

```go
import (
    "github.com/hashicorp/consul/api"
)

func NewConsulClient() (*api.Client, error) {
    // 创建配置
    config := api.DefaultConfig()
    config.Address = "localhost:8500"  // Consul 服务地址
    
    // 可选：设置 ACL token
    // config.Token = "your-acl-token"
    
    // 创建客户端
    client, err := api.NewClient(config)
    if err != nil {
        return nil, err
    }
    
    return client, nil
}
```

### 4.3 服务注册

```go
func RegisterService(client *api.Client) error {
    // 定义服务
    registration := &api.AgentServiceRegistration{
        ID:      "my-service-1",         // 服务 ID
        Name:    "my-service",           // 服务名称
        Tags:    []string{"go", "api"},  // 服务标签
        Port:    8080,                    // 服务端口
        Address: "192.168.1.10",         // 服务地址
        
        // 健康检查
        Check: &api.AgentServiceCheck{
            HTTP:                           "http://192.168.1.10:8080/health",
            Interval:                       "10s",
            Timeout:                        "1s",
            DeregisterCriticalServiceAfter: "30s",
        },
    }
    
    // 注册服务
    return client.Agent().ServiceRegister(registration)
}
```

### 4.4 服务发现

```go
func DiscoverService(client *api.Client, serviceName string) ([]*api.AgentService, error) {
    // 查找服务
    services, _, err := client.Health().Service(serviceName, "", true, nil)
    if err != nil {
        return nil, err
    }
    
    // 提取服务实例
    var instances []*api.AgentService
    for _, service := range services {
        instances = append(instances, service.Service)
    }
    
    return instances, nil
}
```

### 4.5 健康检查

```go
func CheckServiceHealth(client *api.Client, serviceName string) ([]*api.ServiceEntry, error) {
    // 检查服务健康状态
    checks, _, err := client.Health().Service(serviceName, "", true, nil)
    if err != nil {
        return nil, err
    }
    
    return checks, nil
}
```

### 4.6 Key/Value 存储

```go
func SetKV(client *api.Client, key, value string) error {
    // 设置键值对
    _, err := client.KV().Put(&api.KVPair{
        Key:   key,
        Value: []byte(value),
    }, nil)
    return err
}

func GetKV(client *api.Client, key string) (string, error) {
    // 获取键值对
    pair, _, err := client.KV().Get(key, nil)
    if err != nil {
        return "", err
    }
    if pair == nil {
        return "", fmt.Errorf("key not found")
    }
    return string(pair.Value), nil
}

func DeleteKV(client *api.Client, key string) error {
    // 删除键值对
    _, err := client.KV().Delete(key, nil)
    return err
}
```

#### 4.6.1 KV 数据持久化

Consul KV 数据会持久化存储在配置的 `data_dir` 目录中。具体来说：

- **存储位置**：所有 KV 数据都会写入 `data_dir` 目录下的 Raft 日志和状态文件中
- **持久化机制**：Consul 使用 Raft 共识协议，所有写操作都会先写入 Raft 日志，然后持久化到磁盘
- **数据安全**：即使 Consul 服务重启，KV 数据也会从 `data_dir` 中恢复，不会丢失
- **备份恢复**：可以使用 `consul snapshot save` 和 `consul snapshot restore` 命令备份和恢复包括 KV 数据在内的所有 Consul 数据

### 4.7 服务注销

```go
func DeregisterService(client *api.Client, serviceID string) error {
    // 注销服务
    return client.Agent().ServiceDeregister(serviceID)
}
```

## 5. 高级功能

### 5.1 服务网格（Connect）

```go
func RegisterServiceWithConnect(client *api.Client) error {
    registration := &api.AgentServiceRegistration{
        ID:      "my-service-1",
        Name:    "my-service",
        Port:    8080,
        
        // 启用 Connect
        Connect: &api.AgentServiceConnect{
            Native: true,
        },
        
        // Connect 健康检查
        Checks: []*api.AgentServiceCheck{
            {
                Name:     "Connect Sidecar",
                Type:     "connect",
                Interval: "10s",
                Timeout:  "1s",
            },
        },
    }
    
    return client.Agent().ServiceRegister(registration)
}
```

### 5.2 多数据中心

```go
func GetServicesFromOtherDC(client *api.Client, serviceName, datacenter string) ([]*api.CatalogService, error) {
    // 从其他数据中心获取服务
    services, _, err := client.Catalog().Service(serviceName, "", &api.QueryOptions{
        Datacenter: datacenter,
    })
    return services, err
}
```

### 5.3 会话管理

```go
func CreateSession(client *api.Client) (string, error) {
    // 创建会话
    session := &api.SessionEntry{
        Name:     "my-session",
        Behavior: "delete",  // 会话过期时删除持有锁的键
        TTL:      "10s",     // 会话 TTL
    }
    
    sessionID, _, err := client.Session().Create(session, nil)
    return sessionID, err
}

func AcquireLock(client *api.Client, sessionID, key string) (bool, error) {
    // 获取锁
    pair := &api.KVPair{
        Key:     key,
        Value:   []byte("locked"),
        Session: sessionID,
    }
    
    acquired, _, err := client.KV().Acquire(pair, nil)
    return acquired, err
}

func ReleaseLock(client *api.Client, sessionID, key string) (bool, error) {
    // 释放锁
    pair := &api.KVPair{
        Key:     key,
        Session: sessionID,
    }
    
    released, _, err := client.KV().Release(pair, nil)
    return released, err
}
```

## 6. 完整示例

### 6.1 服务注册与发现

```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/hashicorp/consul/api"
)

const (
    serviceName = "my-api-service"
    serviceID   = "my-api-service-1"
    servicePort = 8080
)

var client *api.Client

func main() {
    var err error
    
    // 初始化 Consul 客户端
    client, err = api.NewClient(api.DefaultConfig())
    if err != nil {
        log.Fatalf("Failed to create Consul client: %v", err)
    }
    
    // 注册服务
    if err := registerService(); err != nil {
        log.Fatalf("Failed to register service: %v", err)
    }
    log.Println("Service registered successfully")
    
    // 启动 HTTP 服务
    http.HandleFunc("/health", healthHandler)
    http.HandleFunc("/", helloHandler)
    go func() {
        log.Printf("Starting server on port %d", servicePort)
        if err := http.ListenAndServe(fmt.Sprintf(":%d", servicePort), nil); err != nil {
            log.Fatalf("Failed to start server: %v", err)
        }
    }()
    
    // 模拟服务发现
    go func() {
        for {
            if err := discoverServices(); err != nil {
                log.Printf("Failed to discover services: %v", err)
            }
            time.Sleep(30 * time.Second)
        }
    }()
    
    // 等待中断信号
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit
    
    // 注销服务
    if err := client.Agent().ServiceDeregister(serviceID); err != nil {
        log.Printf("Failed to deregister service: %v", err)
    }
    log.Println("Service deregistered successfully")
}

func registerService() error {
    registration := &api.AgentServiceRegistration{
        ID:      serviceID,
        Name:    serviceName,
        Port:    servicePort,
        Address: "localhost",
        Tags:    []string{"go", "api"},
        Check: &api.AgentServiceCheck{
            HTTP:                           fmt.Sprintf("http://localhost:%d/health", servicePort),
            Interval:                       "10s",
            Timeout:                        "1s",
            DeregisterCriticalServiceAfter: "30s",
        },
    }
    return client.Agent().ServiceRegister(registration)
}

func discoverServices() error {
    services, _, err := client.Health().Service(serviceName, "", true, nil)
    if err != nil {
        return err
    }
    
    log.Printf("Found %d instances of %s", len(services), serviceName)
    for i, service := range services {
        log.Printf("Instance %d: %s:%d", i+1, service.Service.Address, service.Service.Port)
    }
    
    return nil
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("OK"))
}

func helloHandler(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("Hello from Consul service!"))
}
```

### 6.2 配置管理

```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "time"

    "github.com/hashicorp/consul/api"
)

const configKey = "my-service/config"

type Config struct {
    ServerPort int    `json:"server_port"`
    DatabaseURL string `json:"database_url"`
    LogLevel   string `json:"log_level"`
}

var client *api.Client

func main() {
    var err error
    
    // 初始化 Consul 客户端
    client, err = api.NewClient(api.DefaultConfig())
    if err != nil {
        log.Fatalf("Failed to create Consul client: %v", err)
    }
    
    // 设置配置
    config := Config{
        ServerPort: 8080,
        DatabaseURL: "postgres://user:pass@localhost:5432/db",
        LogLevel:   "info",
    }
    
    if err := setConfig(config); err != nil {
        log.Fatalf("Failed to set config: %v", err)
    }
    log.Println("Config set successfully")
    
    // 获取配置
    if err := getConfig(); err != nil {
        log.Fatalf("Failed to get config: %v", err)
    }
    
    // 监控配置变化
    go monitorConfigChanges()
    
    // 保持运行
    select {}
}

func setConfig(config Config) error {
    data, err := json.MarshalIndent(config, "", "  ")
    if err != nil {
        return err
    }
    
    _, err = client.KV().Put(&api.KVPair{
        Key:   configKey,
        Value: data,
    }, nil)
    return err
}

func getConfig() error {
    pair, _, err := client.KV().Get(configKey, nil)
    if err != nil {
        return err
    }
    if pair == nil {
        return fmt.Errorf("config not found")
    }
    
    var config Config
    if err := json.Unmarshal(pair.Value, &config); err != nil {
        return err
    }
    
    log.Printf("Current config: %+v", config)
    return nil
}

func monitorConfigChanges() {
    var lastIndex uint64
    
    for {
        options := &api.QueryOptions{
            WaitIndex: lastIndex,
        }
        
        pair, meta, err := client.KV().Get(configKey, options)
        if err != nil {
            log.Printf("Error monitoring config: %v", err)
            time.Sleep(5 * time.Second)
            continue
        }
        
        lastIndex = meta.LastIndex
        
        if pair != nil {
            var config Config
            if err := json.Unmarshal(pair.Value, &config); err != nil {
                log.Printf("Error unmarshaling config: %v", err)
                continue
            }
            
            log.Printf("Config changed: %+v", config)
            // 这里可以添加配置更新的逻辑
        }
    }
}
```

## 7. 最佳实践

### 7.1 服务注册

::: tip 服务注册最佳实践
- **唯一的服务 ID**：使用包含主机名或实例 ID 的唯一 ID
- **详细的健康检查**：包含多个健康检查维度（HTTP、TCP、gRPC 等）
- **合理的检查间隔**：根据服务特性设置合适的检查间隔
- **正确的服务地址**：确保服务地址可被其他服务访问
:::

### 7.2 服务发现

```go
// ✅ 推荐：使用健康检查过滤不健康的服务
func getHealthyServices(client *api.Client, serviceName string) ([]*api.AgentService, error) {
    services, _, err := client.Health().Service(serviceName, "", true, nil)
    if err != nil {
        return nil, err
    }
    
    var healthyServices []*api.AgentService
    for _, service := range services {
        healthyServices = append(healthyServices, service.Service)
    }
    
    return healthyServices, nil
}

// ❌ 不推荐：不检查健康状态
func getServices(client *api.Client, serviceName string) ([]*api.AgentService, error) {
    catalogServices, _, err := client.Catalog().Service(serviceName, "", nil)
    if err != nil {
        return nil, err
    }
    
    var services []*api.AgentService
    for _, service := range catalogServices {
        services = append(services, &api.AgentService{
            ID:      service.ServiceID,
            Name:    service.ServiceName,
            Address: service.Address,
            Port:    service.ServicePort,
        })
    }
    
    return services, nil
}
```

### 7.3 配置管理

::: tip 配置管理最佳实践
- **分层配置**：使用命名空间和路径分隔符组织配置（如 `service/env/config`）
- **配置版本控制**：在配置键中包含版本信息
- **配置验证**：在应用启动时验证配置有效性
- **配置监控**：监控配置变化并自动更新
:::

### 7.4 高可用部署

```hcl
# 生产环境推荐配置
server = true
bootstrap_expect = 3

retry_join = [
  "192.168.1.101",
  "192.168.1.102",
  "192.168.1.103"
]

# 启用自动加密
auto_encrypt {
  allow_tls = true
}

# 启用 ACL
acl {
  enabled = true
  default_policy = "deny"
  enable_token_persistence = true
}
```

### 7.5 安全配置

::: tip 安全最佳实践
- **启用 ACL**：限制对 Consul API 的访问
- **使用 TLS**：加密所有 Consul 通信
- **设置防火墙**：限制 Consul 端口的访问
- **定期轮换 token**：定期更新 ACL token
- **最小权限原则**：为不同服务分配最小必要的权限
:::

## 8. 常见问题

### 8.1 服务注册失败

**症状**：服务无法注册到 Consul

**解决方案**：
- 检查 Consul 服务是否运行
- 验证服务地址和端口是否正确
- 检查健康检查配置是否正确
- 查看 Consul 日志了解详细错误信息

### 8.2 服务发现找不到服务

**症状**：通过 Consul 无法发现服务

**解决方案**：
- 检查服务是否成功注册
- 验证服务健康状态
- 检查服务标签是否正确
- 确认 Consul 集群状态正常

### 8.3 健康检查失败

**症状**：服务被标记为不健康

**解决方案**：
- 检查健康检查端点是否可访问
- 验证健康检查超时设置是否合理
- 检查服务是否正常运行
- 查看服务日志了解详细错误信息

### 8.4 Consul 集群 leader 选举失败

**症状**：Consul 集群无法选举 leader

**解决方案**：
- 确保集群节点间网络通信正常
- 检查 `bootstrap_expect` 设置是否正确
- 验证集群节点数是否达到法定数量
- 查看 Consul 日志了解详细错误信息

### 8.5 配置更新不生效

**症状**：修改 Consul KV 存储的配置后，应用未更新

**解决方案**：
- 检查应用是否监控配置变化
- 验证配置键路径是否正确
- 确认应用有读取配置的权限
- 重启应用验证配置是否正确

## 9. 总结

Consul 是一个功能强大的服务网格解决方案，为微服务架构提供了：

- **服务发现**：自动注册和发现服务，简化服务间通信
- **健康检查**：监控服务健康状态，确保只将流量路由到健康的服务
- **配置管理**：集中管理配置，支持动态更新
- **多数据中心**：原生支持跨数据中心部署
- **服务网格**：提供服务间的安全通信

通过 Go SDK，我们可以：
- 轻松集成 Consul 到 Go 应用中
- 实现服务的自动注册和发现
- 利用 Key/Value 存储管理配置
- 监控服务健康状态
- 实现分布式锁和领导者选举

Consul 是构建可靠、可扩展的微服务架构的重要工具，它不仅提供了服务发现和配置管理的核心功能，还通过其丰富的 API 和 SDK 为开发者提供了灵活的集成方式。

## 10. 附录

### 10.1 常用命令

```bash
# 启动开发模式
consul agent -dev

# 启动服务器节点
consul agent -server -bootstrap-expect=3 -data-dir=/opt/consul/data -bind=192.168.1.100

# 启动客户端节点
consul agent -data-dir=/opt/consul/data -bind=192.168.1.101 -retry-join=192.168.1.100

# 查看集群成员
consul members

# 查看服务状态
consul catalog services

# 查看服务详情
consul catalog service my-service

# 备份 Consul 数据
consul snapshot save backup.snap

# 恢复 Consul 数据
consul snapshot restore backup.snap
```

### 10.2 环境变量

| **环境变量** | **描述** | **默认值** |
| ------------ | -------- | ---------- |
| `CONSUL_HTTP_ADDR` | Consul HTTP 地址 | "127.0.0.1:8500" |
| `CONSUL_HTTP_TOKEN` | Consul ACL token | "" |
| `CONSUL_HTTP_SSL` | 是否使用 HTTPS | false |
| `CONSUL_CACERT` | CA 证书路径 | "" |
| `CONSUL_CLIENT_CERT` | 客户端证书路径 | "" |
| `CONSUL_CLIENT_KEY` | 客户端密钥路径 | "" |

### 10.3 Go SDK 版本兼容性

| **Consul 版本** | **推荐 Go SDK 版本** |
| --------------- | -------------------- |
| 1.10.x | v1.11.x |
| 1.11.x | v1.12.x |
| 1.12.x | v1.13.x |
| 1.13.x | v1.14.x |
| 1.14.x | v1.15.x |

### 10.4 相关工具

- **consul-template**：基于 Consul KV 存储的配置模板工具
- **envconsul**：从 Consul KV 存储加载环境变量
- **consul-exporter**：Prometheus 导出器，用于监控 Consul
- **vault**：HashiCorp 的密钥管理工具，与 Consul 集成
