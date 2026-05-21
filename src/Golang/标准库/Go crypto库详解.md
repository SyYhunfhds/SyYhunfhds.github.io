---
title: Go crypto库详解
date: 2026-05-20
footer: AI创作内容
---

# Go crypto库详解

Go语言的`crypto`包系列提供了完整的加密功能，包括哈希函数、对称加密、非对称加密、数字签名、TLS等。本文详细介绍crypto库的核心组件和使用方法。

## 目录

- [概述](#概述)
- [哈希函数](#哈希函数)
- [对称加密](#对称加密)
- [非对称加密](#非对称加密)
- [数字签名](#数字签名)
- [随机数生成](#随机数生成)
- [TLS/SSL](#tls-ssl)
- [密钥派生](#密钥派生)
- [最佳实践](#最佳实践)

## 概述

Go的crypto库是一个模块化的加密工具集，主要包含以下子包：

| 子包 | 功能 | 主要用途 |
|------|------|----------|
| `crypto` | 通用接口和常量 | 定义哈希接口等 |
| `crypto/aes` | AES对称加密 | 数据加密 |
| `crypto/des` | DES对称加密 | 遗留系统兼容 |
| `crypto/rsa` | RSA非对称加密 | 密钥交换、签名 |
| `crypto/ecdsa` | ECDSA数字签名 | 高效签名 |
| `crypto/ed25519` | Ed25519签名 | 现代签名算法 |
| `crypto/sha256` | SHA-256哈希 | 数据完整性校验 |
| `crypto/sha512` | SHA-512哈希 | 高安全性哈希 |
| `crypto/md5` | MD5哈希 | 校验和（非安全场景） |
| `crypto/rand` | 密码学安全随机数 | 密钥生成 |
| `crypto/tls` | TLS协议实现 | 安全通信 |
| `crypto/cipher` | 加密模式 | CBC、GCM等 |
| `crypto/subtle` | 常量时间比较 | 防止时序攻击 |
| `crypto/hmac` | HMAC消息认证 | 消息完整性 |

## 哈希函数

### SHA-256

SHA-256是目前最常用的安全哈希算法，输出256位（32字节）哈希值。

```go
package main

import (
    "crypto/sha256"
    "fmt"
    "encoding/hex"
)

func main() {
    data := []byte("Hello, Crypto!")
    
    // 方法1：一次性计算
    hash := sha256.Sum256(data)
    fmt.Printf("SHA-256: %x\n", hash)
    
    // 方法2：流式计算
    h := sha256.New()
    h.Write(data)
    hash2 := h.Sum(nil)
    fmt.Printf("SHA-256 (stream): %x\n", hex.EncodeToString(hash2))
}
```

### SHA-512

SHA-512输出512位（64字节）哈希值，安全性更高。

```go
import "crypto/sha512"

func sha512Example() {
    data := []byte("sensitive data")
    hash := sha512.Sum512(data)
    fmt.Printf("SHA-512: %x\n", hash)
}
```

### MD5（不推荐用于安全场景）

```go
import "crypto/md5"

func md5Example() {
    data := []byte("checksum data")
    hash := md5.Sum(data)
    fmt.Printf("MD5: %x\n", hash)
}
```

### HMAC消息认证

```go
import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/hex"
)

func hmacExample() {
    secret := []byte("my-secret-key")
    message := []byte("hello world")
    
    h := hmac.New(sha256.New, secret)
    h.Write(message)
    signature := h.Sum(nil)
    
    fmt.Printf("HMAC-SHA256: %s\n", hex.EncodeToString(signature))
}
```

## 对称加密

### AES-GCM模式（推荐）

AES-GCM提供认证加密，同时保证机密性和完整性。

```go
package main

import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "fmt"
)

func encryptGCM(plaintext, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }
    
    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }
    
    nonce := make([]byte, gcm.NonceSize())
    if _, err := rand.Read(nonce); err != nil {
        return nil, err
    }
    
    return gcm.Seal(nonce, nonce, plaintext, nil), nil
}

func decryptGCM(ciphertext, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }
    
    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }
    
    nonceSize := gcm.NonceSize()
    if len(ciphertext) < nonceSize {
        return nil, fmt.Errorf("ciphertext too short")
    }
    
    nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]
    return gcm.Open(nil, nonce, ciphertext, nil)
}

func main() {
    // 256-bit key (32 bytes)
    key := make([]byte, 32)
    rand.Read(key)
    
    plaintext := []byte("secret message")
    
    ciphertext, _ := encryptGCM(plaintext, key)
    fmt.Printf("Ciphertext: %x\n", ciphertext)
    
    decrypted, _ := decryptGCM(ciphertext, key)
    fmt.Printf("Decrypted: %s\n", decrypted)
}
```

### AES-CBC模式

```go
import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "io"
    "bytes"
)

func pkcs7Pad(data []byte, blockSize int) []byte {
    padding := blockSize - len(data)%blockSize
    return append(data, bytes.Repeat([]byte{byte(padding)}, padding)...)
}

func pkcs7Unpad(data []byte) []byte {
    padding := int(data[len(data)-1])
    return data[:len(data)-padding]
}

func encryptCBC(plaintext, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }
    
    plaintext = pkcs7Pad(plaintext, aes.BlockSize)
    ciphertext := make([]byte, aes.BlockSize+len(plaintext))
    iv := ciphertext[:aes.BlockSize]
    
    if _, err := io.ReadFull(rand.Reader, iv); err != nil {
        return nil, err
    }
    
    mode := cipher.NewCBCEncrypter(block, iv)
    mode.CryptBlocks(ciphertext[aes.BlockSize:], plaintext)
    
    return ciphertext, nil
}

func decryptCBC(ciphertext, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }
    
    if len(ciphertext) < aes.BlockSize {
        return nil, fmt.Errorf("ciphertext too short")
    }
    
    iv := ciphertext[:aes.BlockSize]
    ciphertext = ciphertext[aes.BlockSize:]
    
    mode := cipher.NewCBCDecrypter(block, iv)
    mode.CryptBlocks(ciphertext, ciphertext)
    
    return pkcs7Unpad(ciphertext)
}
```

## 非对称加密

### RSA加密

```go
package main

import (
    "crypto/rand"
    "crypto/rsa"
    "crypto/sha256"
    "fmt"
)

func main() {
    // 生成RSA密钥对
    privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
    if err != nil {
        panic(err)
    }
    
    publicKey := &privateKey.PublicKey
    
    // 加密
    plaintext := []byte("secret message for RSA")
    ciphertext, err := rsa.EncryptOAEP(sha256.New(), rand.Reader, publicKey, plaintext, nil)
    if err != nil {
        panic(err)
    }
    
    fmt.Printf("Encrypted: %x\n", ciphertext)
    
    // 解密
    decrypted, err := rsa.DecryptOAEP(sha256.New(), rand.Reader, privateKey, ciphertext, nil)
    if err != nil {
        panic(err)
    }
    
    fmt.Printf("Decrypted: %s\n", decrypted)
}
```

### RSA签名与验证

```go
func rsaSignExample() {
    privateKey, _ := rsa.GenerateKey(rand.Reader, 2048)
    publicKey := &privateKey.PublicKey
    
    message := []byte("message to sign")
    
    // 签名
    hash := sha256.Sum256(message)
    signature, _ := rsa.SignPKCS1v15(rand.Reader, privateKey, crypto.SHA256, hash[:])
    
    fmt.Printf("Signature: %x\n", signature)
    
    // 验证
    err := rsa.VerifyPKCS1v15(publicKey, crypto.SHA256, hash[:], signature)
    if err != nil {
        fmt.Println("Verification failed:", err)
    } else {
        fmt.Println("Verification succeeded")
    }
}
```

### ECDSA签名

```go
import (
    "crypto/ecdsa"
    "crypto/elliptic"
    "crypto/rand"
    "crypto/sha256"
    "fmt"
)

func ecdsaExample() {
    // 生成ECDSA密钥对
    privateKey, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
    if err != nil {
        panic(err)
    }
    
    message := []byte("message for ECDSA")
    hash := sha256.Sum256(message)
    
    // 签名
    r, s, err := ecdsa.Sign(rand.Reader, privateKey, hash[:])
    if err != nil {
        panic(err)
    }
    
    fmt.Printf("Signature: r=%x, s=%x\n", r, s)
    
    // 验证
    valid := ecdsa.Verify(&privateKey.PublicKey, hash[:], r, s)
    fmt.Printf("Valid: %v\n", valid)
}
```

### Ed25519签名（推荐）

Ed25519是现代签名算法，安全性高且性能好。

```go
import (
    "crypto/ed25519"
    "crypto/rand"
    "fmt"
)

func ed25519Example() {
    // 生成密钥对
    publicKey, privateKey, err := ed25519.GenerateKey(rand.Reader)
    if err != nil {
        panic(err)
    }
    
    message := []byte("message for Ed25519")
    
    // 签名
    signature := ed25519.Sign(privateKey, message)
    fmt.Printf("Signature: %x\n", signature)
    
    // 验证
    valid := ed25519.Verify(publicKey, message, signature)
    fmt.Printf("Valid: %v\n", valid)
}
```

## 数字签名

### 签名最佳实践

```go
import (
    "crypto"
    "crypto/rand"
    "crypto/rsa"
    "crypto/sha256"
)

func signData(privateKey *rsa.PrivateKey, data []byte) ([]byte, error) {
    hash := sha256.Sum256(data)
    return rsa.SignPKCS1v15(rand.Reader, privateKey, crypto.SHA256, hash[:])
}

func verifyData(publicKey *rsa.PublicKey, data, signature []byte) error {
    hash := sha256.Sum256(data)
    return rsa.VerifyPKCS1v15(publicKey, crypto.SHA256, hash[:], signature)
}
```

## 随机数生成

### 安全随机数

```go
import (
    "crypto/rand"
    "fmt"
)

func generateRandomBytes(n int) ([]byte, error) {
    b := make([]byte, n)
    _, err := rand.Read(b)
    if err != nil {
        return nil, err
    }
    return b, nil
}

func main() {
    // 生成32字节随机密钥
    key, _ := generateRandomBytes(32)
    fmt.Printf("Random key: %x\n", key)
    
    // 生成随机整数
    var randomInt int64
    rand.Read([]byte(fmt.Sprintf("%d", randomInt)))
}
```

## TLS/SSL

### 服务端配置

```go
package main

import (
    "crypto/tls"
    "net/http"
)

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("Hello, TLS!"))
    })
    
    // 加载证书
    cert, err := tls.LoadX509KeyPair("cert.pem", "key.pem")
    if err != nil {
        panic(err)
    }
    
    config := &tls.Config{
        Certificates: []tls.Certificate{cert},
        MinVersion:   tls.VersionTLS12,
        CipherSuites: []uint16{
            tls.TLS_AES_128_GCM_SHA256,
            tls.TLS_AES_256_GCM_SHA384,
        },
    }
    
    server := &http.Server{
        Addr:      ":443",
        TLSConfig: config,
        Handler:   mux,
    }
    
    server.ListenAndServeTLS("", "")
}
```

### 客户端配置

```go
func tlsClientExample() {
    config := &tls.Config{
        MinVersion: tls.VersionTLS12,
        // 禁用不安全的套件
        CipherSuites: []uint16{
            tls.TLS_AES_128_GCM_SHA256,
            tls.TLS_AES_256_GCM_SHA384,
        },
    }
    
    client := &http.Client{
        Transport: &http.Transport{
            TLSClientConfig: config,
        },
    }
    
    resp, err := client.Get("https://example.com")
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()
}
```

## 密钥派生

### PBKDF2

```go
import (
    "crypto/rand"
    "crypto/sha256"
    "crypto/subtle"
    "golang.org/x/crypto/pbkdf2"
)

func deriveKey(password, salt []byte) []byte {
    // 使用PBKDF2派生密钥
    return pbkdf2.Key(password, salt, 4096, 32, sha256.New)
}

func comparePasswords(hashed, password, salt []byte) bool {
    derived := deriveKey(password, salt)
    return subtle.ConstantTimeCompare(hashed, derived) == 1
}
```

### Scrypt

```go
import "golang.org/x/crypto/scrypt"

func scryptExample(password, salt []byte) ([]byte, error) {
    // N: CPU/内存成本参数
    // r: 块大小
    // p: 并行度
    return scrypt.Key(password, salt, 1<<15, 8, 1, 32)
}
```

## 最佳实践

### 1. 使用安全的随机数生成器

```go
// 正确：使用crypto/rand
import "crypto/rand"

key := make([]byte, 32)
rand.Read(key)

// 错误：不要使用math/rand
// import "math/rand"
// rand.Seed(time.Now().UnixNano())
// rand.Read(key) // 不安全！
```

### 2. 选择合适的密钥长度

| 算法 | 推荐密钥长度 | 安全级别 |
|------|-------------|----------|
| AES | 256位 | 高 |
| RSA | 2048位以上 | 中-高 |
| ECDSA | P-256 | 高 |
| Ed25519 | 固定 | 高 |

### 3. 使用认证加密模式

```go
// 推荐：使用GCM模式
gcm, _ := cipher.NewGCM(block)
ciphertext := gcm.Seal(nonce, nonce, plaintext, nil)

// 避免：单独使用CBC模式（容易受到padding oracle攻击）
// mode := cipher.NewCBCEncrypter(block, iv)
// mode.CryptBlocks(ciphertext, plaintext)
```

### 4. 定期轮换密钥

```go
type KeyManager struct {
    currentKey []byte
    keyVersion int
}

func (km *KeyManager) RotateKey() error {
    newKey := make([]byte, 32)
    _, err := rand.Read(newKey)
    if err != nil {
        return err
    }
    km.currentKey = newKey
    km.keyVersion++
    return nil
}
```

### 5. 避免硬编码密钥

```go
// 正确：从环境变量或密钥管理服务读取
key := []byte(os.Getenv("ENCRYPTION_KEY"))

// 错误：硬编码密钥
// key := []byte("my-secret-key-12345")
```

### 6. 使用常量时间比较

```go
// 正确：防止时序攻击
if subtle.ConstantTimeCompare(a, b) == 1 {
    // 相等
}

// 错误：普通比较可能泄露信息
// if bytes.Equal(a, b) { ... }
```

### 7. TLS最佳实践

```go
config := &tls.Config{
    // 禁用SSLv3和TLSv1.0/1.1
    MinVersion: tls.VersionTLS12,
    
    // 只使用安全的套件
    CipherSuites: []uint16{
        tls.TLS_AES_128_GCM_SHA256,
        tls.TLS_AES_256_GCM_SHA384,
        tls.TLS_CHACHA20_POLY1305_SHA256,
    },
    
    // 禁用会话恢复（防止会话劫持）
    SessionTicketsDisabled: true,
    
    // 使用现代曲线
    CurvePreferences: []tls.CurveID{
        tls.CurveP256,
        tls.X25519,
    },
}
```

## 总结

Go的crypto库提供了完整的加密工具集，涵盖：

1. **哈希函数**：SHA-256、SHA-512、MD5
2. **对称加密**：AES（GCM模式推荐）
3. **非对称加密**：RSA、ECDSA、Ed25519
4. **数字签名**：支持多种算法
5. **TLS/SSL**：安全通信
6. **密钥派生**：PBKDF2、Scrypt

遵循最佳实践，选择合适的算法和参数，可以构建安全可靠的加密系统。
