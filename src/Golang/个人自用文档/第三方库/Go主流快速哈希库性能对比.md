---
title: Go主流快速哈希库性能对比
date: 2026-05-22
footer: AI创作内容
---

# Go主流快速哈希库性能对比

本文详细介绍Golang社区中主流的快速非加密哈希库，包括xxHash、MurmurHash、CityHash、FarmHash等，并从生成速度、随机性、哈希值空间三个维度进行对比分析。

## 目录

- [概述](#概述)
- [主流哈希库介绍](#主流哈希库介绍)
- [性能对比](#性能对比)
- [随机性分析](#随机性分析)
- [哈希值空间](#哈希值空间)
- [使用示例](#使用示例)
- [最佳实践](#最佳实践)
- [总结](#总结)

## 概述

非加密哈希算法（又称快速哈希）主要用于：
- 哈希表/字典的键计算
- 数据分片/负载均衡
- 布隆过滤器
- 数据校验和
- 唯一标识符生成

与加密哈希（如SHA-256）相比，快速哈希牺牲了抗碰撞性换取极致性能。

### 核心指标

| 指标 | 说明 |
|------|------|
| **生成速度** | 每秒处理数据量（MB/s）或每次操作耗时（ns/op） |
| **随机性** | 哈希值分布均匀度、雪崩效应、扩散性 |
| **哈希值空间** | 输出位数（32位/64位/128位） |
| **抗碰撞性** | 不同输入产生相同哈希的概率 |

## 主流哈希库介绍

### 1. xxHash

**官方网站**：https://github.com/cespare/xxhash

xxHash是目前最快的非加密哈希算法之一，由Yann Collet开发。

#### 特性
- **XXH32**：32位输出，使用32位算术
- **XXH64**：64位输出，使用64位算术
- **XXH3**：最新版本，支持64位和128位输出，使用SIMD优化

#### 性能亮点
- 小数据速度极快（7-8 ns/op for 8 bytes）
- 大数据接近RAM速度（31.5 GB/s）
- 通过SMHasher测试套件

#### Go实现
```go
import "github.com/cespare/xxhash/v2"

// XXH64
hash := xxhash.Sum64([]byte("hello"))

// XXH3
hash := xxhash.Sum64String("hello")
```

### 2. MurmurHash3

**官方网站**：https://github.com/twmb/murmur3

MurmurHash是一种广泛使用的非加密哈希算法，由Austin Appleby开发。

#### 特性
- **Murmur3-32**：32位输出
- **Murmur3-128**：128位输出（适合64位系统）

#### 性能亮点
- 良好的分布性和雪崩效应
- 广泛应用于缓存系统（如Redis）
- 跨平台一致性

#### Go实现
```go
import "github.com/twmb/murmur3"

// 32位哈希
hash32 := murmur3.Sum32([]byte("hello"))

// 128位哈希
hash128 := murmur3.Sum128([]byte("hello"))
```

### 3. CityHash

**官方网站**：https://github.com/google/cityhash

CityHash是Google开发的哈希算法，专门针对长字符串优化。

#### 特性
- **CityHash64**：64位输出
- **CityHash128**：128位输出

#### 性能亮点
- 对长键（1KB+）性能出色
- 良好的碰撞抵抗性
- 适合分布式系统中的一致性哈希

#### Go实现
```go
import "github.com/google/cityhash"

hash64 := cityhash.CityHash64([]byte("hello"))
hash128 := cityhash.CityHash128([]byte("hello"))
```

### 4. FarmHash

**官方网站**：https://github.com/dgryski/go-farm

FarmHash是Google开发的另一组哈希函数，基于CityHash改进。

#### 特性
- **Fingerprint64**：64位指纹
- **Fingerprint128**：128位指纹
- **Hash32/64**：常规哈希

#### 性能亮点
- 小数据速度优秀
- 良好的统计特性
- 适合内存密集型应用

#### Go实现
```go
import "github.com/dgryski/go-farm"

hash64 := farm.Fingerprint64([]byte("hello"))
```

### 5. HighwayHash

**官方网站**：https://github.com/google/highwayhash

HighwayHash是Google开发的高速消息认证码算法，也可用作哈希函数。

#### 特性
- 64位和128位输出
- 需要16字节密钥
- 声称具有加密级别的安全性

#### 性能亮点
- 大数据速度极快（接近RAM速度）
- 强碰撞抵抗性
- 适合需要认证的场景

#### Go实现
```go
import "github.com/google/highwayhash"

key := make([]byte, 16) // 16字节密钥
hash := highwayhash.Sum64([]byte("hello"), key)
```

### 6. SeaHash

**官方网站**：https://github.com/dgryski/go-seahash

SeaHash是一种注重随机性的哈希算法。

#### 特性
- 64位输出
- 基于AES-NI指令集
- 强统计特性

#### 性能亮点
- 优秀的分布性
- 适合需要高质量哈希的场景

## 性能对比

### 基准测试数据

根据社区基准测试（Intel Xeon E3-1505M v6 @ 3.00GHz）：

| 算法 | 8字节 | 8KB | 1MB | 吞吐量(8KB) |
|------|-------|-----|-----|-------------|
| **xxHash64** | 7.7 ns/op | 551 ns/op | 77972 ns/op | ~14.5 GB/s |
| **FarmHash** | 10.7 ns/op | 686 ns/op | 95575 ns/op | ~11.7 GB/s |
| **SeaHash** | 16.0 ns/op | 3683 ns/op | 470030 ns/op | ~2.2 GB/s |
| **HighwayHash** | 53.2 ns/op | 581 ns/op | 80398 ns/op | ~13.8 GB/s |
| **Murmur3** | 25.6 ns/op | 1205 ns/op | 155219 ns/op | ~6.7 GB/s |

### 速度排名

#### 小数据（< 1KB）
1. **xxHash64** - 最快
2. **FarmHash** - 优秀
3. **Murmur3** - 中等
4. **SeaHash** - 较慢
5. **HighwayHash** - 最慢（初始化开销大）

#### 大数据（> 1KB）
1. **xxHash64/XXH3** - 最快，接近RAM速度
2. **HighwayHash** - 非常快
3. **FarmHash** - 优秀
4. **Murmur3** - 中等
5. **SeaHash** - 较慢

## 随机性分析

### 随机性指标

| 指标 | 说明 | 测试方法 |
|------|------|----------|
| **雪崩效应** | 输入一位变化，输出至少一半位变化 | SMHasher测试 |
| **分布均匀性** | 哈希值在输出空间均匀分布 | 直方图测试 |
| **差分分布** | 输入微小变化导致输出显著变化 | 差分测试 |
| **碰撞抵抗** | 不同输入产生相同哈希的概率 | 生日攻击测试 |

### 算法随机性评级

| 算法 | 雪崩效应 | 分布均匀性 | 碰撞抵抗 | 综合评分 |
|------|----------|------------|----------|----------|
| **XXH3** | 优秀 | 优秀 | 优秀 | 10/10 |
| **HighwayHash** | 优秀 | 优秀 | 优秀 | 10/10 |
| **Murmur3** | 良好 | 良好 | 良好 | 8/10 |
| **CityHash** | 良好 | 优秀 | 良好 | 8/10 |
| **FarmHash** | 良好 | 良好 | 良好 | 7/10 |
| **SeaHash** | 优秀 | 优秀 | 良好 | 9/10 |
| **CRC32** | 较差 | 较差 | 较差 | 4/10 |

### 实际测试示例

```go
package main

import (
    "fmt"
    "github.com/cespare/xxhash/v2"
    "github.com/twmb/murmur3"
)

func main() {
    // 测试雪崩效应
    s1 := "hello"
    s2 := "hellp" // 最后一位不同
    
    h1 := xxhash.Sum64([]byte(s1))
    h2 := xxhash.Sum64([]byte(s2))
    
    // 计算汉明距离
    diff := countSetBits(h1 ^ h2)
    fmt.Printf("xxHash64 汉明距离: %d/64\n", diff)
    
    m1 := murmur3.Sum64([]byte(s1))
    m2 := murmur3.Sum64([]byte(s2))
    diff = countSetBits(m1 ^ m2)
    fmt.Printf("Murmur3 汉明距离: %d/64\n", diff)
}

func countSetBits(n uint64) int {
    count := 0
    for n > 0 {
        count += int(n & 1)
        n >>= 1
    }
    return count
}
```

## 哈希值空间

### 输出位数对比

| 算法 | 输出位数 | 输出空间大小 | 碰撞概率（生日攻击） |
|------|----------|--------------|---------------------|
| **XXH32** | 32位 | 4.3×10^9 | 约77,163次操作后50%概率 |
| **XXH64** | 64位 | 1.8×10^19 | 约5.1×10^9次操作后50%概率 |
| **XXH3-128** | 128位 | 3.4×10^38 | 约1.8×10^19次操作后50%概率 |
| **Murmur3-32** | 32位 | 4.3×10^9 | 约77,163次操作后50%概率 |
| **Murmur3-128** | 128位 | 3.4×10^38 | 约1.8×10^19次操作后50%概率 |
| **CityHash64** | 64位 | 1.8×10^19 | 约5.1×10^9次操作后50%概率 |
| **CityHash128** | 128位 | 3.4×10^38 | 约1.8×10^19次操作后50%概率 |
| **FarmHash64** | 64位 | 1.8×10^19 | 约5.1×10^9次操作后50%概率 |
| **HighwayHash** | 64/128位 | 1.8×10^19 / 3.4×10^38 | 取决于输出位数 |

### 空间选择建议

```go
// 根据场景选择哈希位数

// 场景1：小数据量哈希表（< 100万条目）
// 使用32位足够
hash := xxhash.Sum64([]byte(key)) % uint64(tableSize)

// 场景2：大数据量哈希表或分布式系统
// 使用64位
hash := xxhash.Sum64([]byte(key))

// 场景3：极高数据量或安全性要求高
// 使用128位
hash := murmur3.Sum128([]byte(key))
```

## 使用示例

### 基础使用

```go
package main

import (
    "fmt"
    "github.com/cespare/xxhash/v2"
    "github.com/twmb/murmur3"
    "github.com/google/cityhash"
)

func main() {
    data := []byte("Hello, World!")
    
    // xxHash64
    xxh := xxhash.Sum64(data)
    fmt.Printf("xxHash64: %d\n", xxh)
    
    // Murmur3-32
    mur32 := murmur3.Sum32(data)
    fmt.Printf("Murmur3-32: %d\n", mur32)
    
    // Murmur3-128
    mur128 := murmur3.Sum128(data)
    fmt.Printf("Murmur3-128: %d\n", mur128)
    
    // CityHash64
    city := cityhash.CityHash64(data)
    fmt.Printf("CityHash64: %d\n", city)
}
```

### 流式哈希

```go
import "github.com/cespare/xxhash/v2"

// 流式计算哈希
h := xxhash.New()
h.Write([]byte("Hello"))
h.Write([]byte(", "))
h.Write([]byte("World!"))
result := h.Sum64()
```

### 带种子哈希

```go
// 使用不同种子生成不同哈希值
seed := uint64(12345)
hash1 := xxhash.Sum64WithSeed([]byte("hello"), seed)
hash2 := xxhash.Sum64WithSeed([]byte("hello"), seed+1)
```

### 哈希表应用

```go
type HashTable struct {
    buckets [][]kv
}

type kv struct {
    key   string
    value interface{}
}

func (t *HashTable) Put(key string, value interface{}) {
    // 使用xxHash计算桶索引
    hash := xxhash.Sum64String(key)
    idx := hash % uint64(len(t.buckets))
    
    // 添加到对应桶
    t.buckets[idx] = append(t.buckets[idx], kv{key, value})
}

func (t *HashTable) Get(key string) (interface{}, bool) {
    hash := xxhash.Sum64String(key)
    idx := hash % uint64(len(t.buckets))
    
    for _, kv := range t.buckets[idx] {
        if kv.key == key {
            return kv.value, true
        }
    }
    return nil, false
}
```

### 一致性哈希

```go
import (
    "github.com/buraksezer/consistent"
    "github.com/cespare/xxhash/v2"
)

// 使用xxHash作为一致性哈希的哈希函数
type xxhashHasher struct{}

func (h xxhashHasher) Sum64(data []byte) uint64 {
    return xxhash.Sum64(data)
}

func main() {
    cfg := consistent.Config{
        PartitionCount:    7,
        ReplicationFactor: 20,
        Load:              1.25,
        Hasher:            xxhashHasher{},
    }
    
    c := consistent.New(nil, cfg)
    
    // 添加节点
    c.Add("node1", "node2", "node3")
    
    // 获取key对应的节点
    key := "user:123"
    node, _ := c.LocateKey([]byte(key))
    fmt.Printf("Key %s belongs to node %s\n", key, node)
}
```

## 最佳实践

### 1. 选择合适的哈希算法

```go
// 根据场景选择
func ChooseHashAlgorithm(dataSize int, securityLevel string) string {
    if dataSize < 1024 && securityLevel == "low" {
        return "xxhash64" // 最快
    }
    if dataSize > 1024*1024 && securityLevel == "high" {
        return "highwayhash" // 大数据+高安全性
    }
    return "xxhash64" // 默认选择
}
```

### 2. 避免哈希碰撞攻击

```go
// 使用带密钥的哈希防止哈希碰撞攻击
func SafeHash(data []byte, secretKey []byte) uint64 {
    // 将密钥和数据组合
    combined := append(secretKey, data...)
    return xxhash.Sum64(combined)
}
```

### 3. 处理哈希值分布

```go
// 使用双重哈希减少冲突
func DoubleHash(key string) uint64 {
    h1 := xxhash.Sum64String(key)
    h2 := murmur3.Sum64([]byte(key))
    // 组合两个哈希
    return h1 ^ (h2 << 1)
}
```

### 4. 性能优化技巧

```go
// 预分配哈希对象避免重复创建
type HashPool struct {
    pool sync.Pool
}

func NewHashPool() *HashPool {
    return &HashPool{
        pool: sync.Pool{
            New: func() interface{} {
                return xxhash.New()
            },
        },
    }
}

func (p *HashPool) Hash(data []byte) uint64 {
    h := p.pool.Get().(*xxhash.Digest)
    defer func() {
        h.Reset()
        p.pool.Put(h)
    }()
    h.Write(data)
    return h.Sum64()
}
```

### 5. 测试哈希质量

```go
func TestHashDistribution() {
    const sampleCount = 1000000
    const bucketCount = 1000
    
    distribution := make([]int, bucketCount)
    
    for i := 0; i < sampleCount; i++ {
        key := fmt.Sprintf("key_%d", i)
        hash := xxhash.Sum64String(key)
        bucket := hash % uint64(bucketCount)
        distribution[bucket]++
    }
    
    // 计算标准差评估分布均匀性
    mean := float64(sampleCount) / float64(bucketCount)
    variance := 0.0
    for _, count := range distribution {
        variance += math.Pow(float64(count)-mean, 2)
    }
    variance /= float64(bucketCount)
    stdDev := math.Sqrt(variance)
    
    fmt.Printf("均值: %.2f, 标准差: %.2f\n", mean, stdDev)
    fmt.Printf("变异系数: %.2f%%\n", stdDev/mean*100)
}
```

## 总结

### 算法选择建议

| 场景 | 推荐算法 | 理由 |
|------|----------|------|
| **通用场景** | **xxHash64** | 速度最快，随机性优秀 |
| **小数据高频** | **xxHash64** | 初始化开销小 |
| **大数据处理** | **XXH3** | 接近RAM速度 |
| **高安全性需求** | **HighwayHash** | 加密级别安全性 |
| **分布式系统** | **CityHash128** | 良好的分布性 |
| **缓存系统** | **Murmur3** | 广泛应用，兼容性好 |

### 性能对比表

| 算法 | 小数据速度 | 大数据速度 | 随机性 | 输出空间 | 推荐度 |
|------|------------|------------|--------|----------|--------|
| **xxHash64** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 64位 | ⭐⭐⭐⭐⭐ |
| **XXH3** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 64/128位 | ⭐⭐⭐⭐⭐ |
| **Murmur3** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 32/128位 | ⭐⭐⭐⭐ |
| **CityHash** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 64/128位 | ⭐⭐⭐⭐ |
| **FarmHash** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 64位 | ⭐⭐⭐ |
| **HighwayHash** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 64/128位 | ⭐⭐⭐⭐ |
| **SeaHash** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | 64位 | ⭐⭐⭐ |

### 最终建议

1. **默认选择xxHash64**：在大多数场景下提供最佳的性能/质量平衡
2. **需要更高安全性选择XXH3或HighwayHash**
3. **处理极大量数据选择XXH3**
4. **分布式系统考虑128位输出**
5. **始终测试哈希质量**：特别是在高负载生产环境中

参考资料：
- https://github.com/yasushi-saito/go-hash-shootout
- https://github.com/kelindar/hashbench
- https://github.com/Cyan4973/xxHash
