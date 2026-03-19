---
title: Go JWT v5 认证与鉴权
date: 2026-03-16
footer: Trae编辑
---

# Go JWT v5 认证与鉴权

本文详细介绍 `github.com/golang-jwt/jwt/v5` 库的 API 用法、Bad Practice 和最佳实践，包括完整的认证与鉴权系统设计。

## 目录

- [基础概念](#基础概念)
- [核心 API](#核心-api)
- [常用方法](#常用方法)
- [Bad Practice](#bad-practice)
- [最佳实践](#最佳实践)
- [认证与鉴权系统设计](#认证与鉴权系统设计)

## 基础概念

### 什么是 JWT

::: info JWT 定义
JWT（JSON Web Token）是一种开放标准（RFC 7519），用于在网络应用环境中安全地传输信息。JWT 是一个紧凑的、自包含的 JSON 对象，可以被验证和信任。
:::

JWT 由三部分组成：
- **Header**：声明类型和算法
- **Payload**：包含声明（Claims），如用户信息、过期时间等
- **Signature**：使用密钥对 Header 和 Payload 进行签名

### 安装依赖

```bash
go get -u github.com/golang-jwt/jwt/v5
```

## 核心 API

### 1. 创建和签名 Token

#### 标准 Claims - MapClaims

```go
package main

import (
    "fmt"
    "time"
    "github.com/golang-jwt/jwt/v5"
)

func main() {
    // 创建 Claims
    claims := jwt.MapClaims{
        "sub":   "user123",
        "name":  "张三",
        "iss":   "my-app",
        "exp":   time.Now().Add(time.Hour * 24).Unix(),
        "iat":   time.Now().Unix(),
    }

    // 创建 Token
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

    // 签名 Token
    tokenString, err := token.SignedString([]byte("your-secret-key"))
    if err != nil {
        panic(err)
    }

    fmt.Println("Token:", tokenString)
}
```

#### 自定义 Claims 结构体

```go
type CustomClaims struct {
    UserID   uint   `json:"user_id"`
    Username string `json:"username"`
    Role     string `json:"role"`
    jwt.RegisteredClaims
}

func main() {
    claims := CustomClaims{
        UserID:   123,
        Username: "zhangsan",
        Role:     "admin",
        RegisteredClaims: jwt.RegisteredClaims{
            Issuer:    "my-app",
            Subject:   "123",
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Hour * 24)),
            NotBefore: jwt.NewNumericDate(time.Now()),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            ID:        "token-unique-id",
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    tokenString, _ := token.SignedString([]byte("your-secret-key"))
    fmt.Println(tokenString)
}
```

### 2. 解析和验证 Token

#### 解析 MapClaims

```go
func parseToken(tokenString string) (jwt.MapClaims, error) {
    token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return []byte("your-secret-key"), nil
    })

    if err != nil {
        return nil, err
    }

    if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
        return claims, nil
    }

    return nil, fmt.Errorf("invalid token")
}
```

#### 解析自定义 Claims

```go
func parseCustomToken(tokenString string) (*CustomClaims, error) {
    token, err := jwt.ParseWithClaims(tokenString, &CustomClaims{}, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return []byte("your-secret-key"), nil
    })

    if err != nil {
        return nil, err
    }

    if claims, ok := token.Claims.(*CustomClaims); ok && token.Valid {
        return claims, nil
    }

    return nil, fmt.Errorf("invalid token")
}
```

### 3. 签名算法

#### HS256（对称加密）

```go
token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
tokenString, err := token.SignedString([]byte("your-secret-key"))
```

#### RS256（非对称加密）

```go
// 使用 RSA 私钥签名
privateKey, err := jwt.ParseRSAPrivateKeyFromPEM(privateKeyBytes)
if err != nil {
    panic(err)
}

token := jwt.NewWithClaims(jwt.SigningMethodRS256, claims)
tokenString, err := token.SignedString(privateKey)

// 使用 RSA 公钥验证
publicKey, err := jwt.ParseRSAPublicKeyFromPEM(publicKeyBytes)
token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
    return publicKey, nil
})
```

#### ES256（椭圆曲线加密）

```go
privateKey, err := jwt.ParseECPrivateKeyFromPEM(ecPrivateKeyBytes)
token := jwt.NewWithClaims(jwt.SigningMethodES256, claims)
tokenString, err := token.SignedString(privateKey)
```

### 4. 验证选项

```go
token, err := jwt.ParseWithClaims(tokenString, claims, keyFunc,
    jwt.WithValidMethods([]string{"HS256"}),
    jwt.WithLeeway(time.Second*30),
    jwt.WithExpirationRequired(),
)
```

### 5. Claims 类型

#### MapClaims

```go
claims := jwt.MapClaims{
    "user_id":  123,
    "username": "zhangsan",
    "role":     "admin",
}
```

#### RegisteredClaims

```go
claims := jwt.RegisteredClaims{
    Issuer:    "my-app",
    Subject:   "123",
    Audience:  []string{"client1", "client2"},
    ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Hour)),
    NotBefore: jwt.NewNumericDate(time.Now()),
    IssuedAt:  jwt.NewNumericDate(time.Now()),
    ID:        "token-id",
}
```

## 常用方法

### 1. 生成 Token 工具函数

```go
package main

import (
    "time"
    "github.com/golang-jwt/jwt/v5"
)

var jwtSecret = []byte("your-secret-key")

type UserClaims struct {
    UserID   uint   `json:"user_id"`
    Username string `json:"username"`
    Role     string `json:"role"`
    jwt.RegisteredClaims
}

func GenerateToken(userID uint, username, role string) (string, error) {
    claims := UserClaims{
        UserID:   userID,
        Username: username,
        Role:     role,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Hour * 24)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            NotBefore: jwt.NewNumericDate(time.Now()),
            Issuer:    "my-app",
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(jwtSecret)
}

func ParseToken(tokenString string) (*UserClaims, error) {
    token, err := jwt.ParseWithClaims(tokenString, &UserClaims{}, func(token *jwt.Token) (interface{}, error) {
        return jwtSecret, nil
    })

    if err != nil {
        return nil, err
    }

    if claims, ok := token.Claims.(*UserClaims); ok && token.Valid {
        return claims, nil
    }

    return nil, fmt.Errorf("invalid token")
}
```

### 2. Gin 中间件示例

```go
package main

import (
    "net/http"
    "strings"
    "github.com/gin-gonic/gin"
    "github.com/golang-jwt/jwt/v5"
)

func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
            c.Abort()
            return
        }

        parts := strings.Split(authHeader, " ")
        if len(parts) != 2 || parts[0] != "Bearer" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid authorization format"})
            c.Abort()
            return
        }

        claims, err := ParseToken(parts[1])
        if err != nil {
            c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
            c.Abort()
            return
        }

        c.Set("user_id", claims.UserID)
        c.Set("username", claims.Username)
        c.Set("role", claims.Role)
        c.Next()
    }
}

func RoleMiddleware(requiredRole string) gin.HandlerFunc {
    return func(c *gin.Context) {
        role, exists := c.Get("role")
        if !exists || role != requiredRole {
            c.JSON(http.StatusForbidden, gin.H{"error": "Insufficient permissions"})
            c.Abort()
            return
        }
        c.Next()
    }
}
```

### 3. Refresh Token 实现

```go
type TokenPair struct {
    AccessToken  string `json:"access_token"`
    RefreshToken string `json:"refresh_token"`
}

func GenerateTokenPair(userID uint, username, role string) (*TokenPair, error) {
    accessToken, err := GenerateToken(userID, username, role)
    if err != nil {
        return nil, err
    }

    refreshClaims := UserClaims{
        UserID:   userID,
        Username: username,
        Role:     role,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Hour * 24 * 7)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            Issuer:    "my-app",
        },
    }

    refreshToken := jwt.NewWithClaims(jwt.SigningMethodHS256, refreshClaims)
    refreshTokenString, err := refreshToken.SignedString(jwtSecret)
    if err != nil {
        return nil, err
    }

    return &TokenPair{
        AccessToken:  accessToken,
        RefreshToken: refreshTokenString,
    }, nil
}
```

### 4. 使用 Redis 存储 Token 黑名单

```go
import "github.com/go-redis/redis/v8"

var ctx = context.Background()

func RevokeToken(tokenString string, ttl time.Duration) error {
    claims, err := ParseToken(tokenString)
    if err != nil {
        return err
    }

    remainingTTL := time.Until(claims.ExpiresAt.Time)
    if remainingTTL <= 0 {
        return nil
    }

    return rdb.Set(ctx, "token:blacklist:"+tokenString, "1", remainingTTL).Err()
}

func IsTokenRevoked(tokenString string) bool {
    result, err := rdb.Get(ctx, "token:blacklist:"+tokenString).Result()
    return err == nil && result == "1"
}
```

## Bad Practice

### 1. 使用弱密钥或硬编码密钥

::: danger 严重安全问题
使用弱密钥或硬编码密钥会导致严重的安全漏洞。
:::

```go
// ❌ Bad Practice
var jwtSecret = []byte("secret") // 太弱了

// ❌ Bad Practice - 硬编码
token.SignedString([]byte("hardcoded-secret"))

// ✅ Good Practice
var jwtSecret = []byte(os.Getenv("JWT_SECRET"))

// ✅ Good Practice - 使用强密钥生成
// openssl rand -base64 64
```

### 2. 使用 None 算法

```go
// ❌ Bad Practice - 极度危险
token := jwt.NewWithClaims(jwt.SigningMethodNone, claims)

// ✅ Good Practice - 强制使用签名算法
token, err := jwt.ParseWithClaims(tokenString, claims, keyFunc,
    jwt.WithValidMethods([]string{"HS256", "RS256"}),
)
```

### 3. Token 过期时间过长

```go
// ❌ Bad Practice - 30 天过期，非常危险
ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Hour * 24 * 30)),

// ✅ Good Practice - 短期过期 + Refresh Token
ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Hour * 2)),
```

### 4. 在 Token 中存储敏感信息

```go
// ❌ Bad Practice - 存储密码
claims := jwt.MapClaims{
    "password": "secret123", // Token 可以被解码看到
}

// ❌ Bad Practice - 存储完整用户信息
claims := jwt.MapClaims{
    "user": userObject, // Token 会变得很大
}

// ✅ Good Practice - 只存储必要信息
claims := jwt.MapClaims{
    "user_id": 123,
    "username": "zhangsan",
    "role": "user",
}
```

### 5. 不验证签名算法

```go
// ❌ Bad Practice
token, _ := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
    return jwtSecret, nil
})

// ✅ Good Practice
token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
    if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
        return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
    }
    return jwtSecret, nil
})
```

### 6. 忽略错误处理

```go
// ❌ Bad Practice
token, _ := jwt.Parse(tokenString, keyFunc)
claims, _ := token.Claims.(jwt.MapClaims)

// ✅ Good Practice
token, err := jwt.Parse(tokenString, keyFunc)
if err != nil {
    return nil, err
}

if !token.Valid {
    return nil, fmt.Errorf("invalid token")
}

claims, ok := token.Claims.(jwt.MapClaims)
if !ok {
    return nil, fmt.Errorf("invalid claims")
}
```

### 7. 在循环中重复解析 Token

```go
// ❌ Bad Practice
for _, item := range items {
    claims, _ := ParseToken(tokenString) // 重复解析
    processItem(item, claims)
}

// ✅ Good Practice
claims, err := ParseToken(tokenString)
if err != nil {
    return err
}
for _, item := range items {
    processItem(item, claims)
}
```

## 最佳实践

### 1. 密钥管理

::: tip 密钥安全
密钥应该：
- 使用强随机生成的密钥
- 从环境变量或密钥管理服务读取
- 定期轮换密钥
:::

```go
package config

import (
    "os"
    "crypto/rsa"
    "github.com/golang-jwt/jwt/v5"
)

type JWTConfig struct {
    Secret     []byte
    PrivateKey *rsa.PrivateKey
    PublicKey  *rsa.PublicKey
}

func LoadJWTConfig() (*JWTConfig, error) {
    secret := os.Getenv("JWT_SECRET")
    if secret == "" {
        return nil, fmt.Errorf("JWT_SECRET not set")
    }

    return &JWTConfig{
        Secret: []byte(secret),
    }, nil
}
```

### 2. 使用 Refresh Token 机制

::: info 双 Token 策略
- Access Token：短期（15分钟-2小时），用于 API 访问
- Refresh Token：长期（7天-30天），用于刷新 Access Token
:::

```go
type TokenService struct {
    config *JWTConfig
    store  TokenStore
}

func (s *TokenService) GenerateTokens(userID uint, username, role string) (*TokenPair, error) {
    accessToken, err := s.generateAccessToken(userID, username, role)
    if err != nil {
        return nil, err
    }

    refreshToken, err := s.generateRefreshToken(userID)
    if err != nil {
        return nil, err
    }

    if err := s.store.SaveRefreshToken(userID, refreshToken); err != nil {
        return nil, err
    }

    return &TokenPair{
        AccessToken:  accessToken,
        RefreshToken: refreshToken,
    }, nil
}

func (s *TokenService) RefreshAccessToken(refreshToken string) (string, error) {
    claims, err := s.parseRefreshToken(refreshToken)
    if err != nil {
        return "", err
    }

    if !s.store.IsRefreshTokenValid(claims.UserID, refreshToken) {
        return "", fmt.Errorf("invalid refresh token")
    }

    user, err := s.getUser(claims.UserID)
    if err != nil {
        return "", err
    }

    return s.generateAccessToken(user.ID, user.Username, user.Role)
}
```

### 3. 实现 Token 黑名单

::: warning 登出处理
JWT 本身无法撤销，需要通过黑名单机制实现登出。
:::

```go
type TokenBlacklist struct {
    redis *redis.Client
}

func NewTokenBlacklist(redis *redis.Client) *TokenBlacklist {
    return &TokenBlacklist{redis: redis}
}

func (t *TokenBlacklist) Add(tokenString string, expiresAt time.Time) error {
    key := "token:blacklist:" + tokenString
    ttl := time.Until(expiresAt)
    
    if ttl <= 0 {
        return nil
    }

    return t.redis.Set(context.Background(), key, "1", ttl).Err()
}

func (t *TokenBlacklist) Contains(tokenString string) bool {
    key := "token:blacklist:" + tokenString
    result, err := t.redis.Get(context.Background(), key).Result()
    return err == nil && result == "1"
}
```

### 4. 使用非对称加密（RS256）

::: tip RS256 优势
- 私钥签名，公钥验证
- 密钥分发更安全
- 适合微服务架构
:::

```go
func LoadRSAPrivateKey(path string) (*rsa.PrivateKey, error) {
    keyBytes, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }
    return jwt.ParseRSAPrivateKeyFromPEM(keyBytes)
}

func LoadRSAPublicKey(path string) (*rsa.PublicKey, error) {
    keyBytes, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }
    return jwt.ParseRSAPublicKeyFromPEM(keyBytes)
}

func SignWithRSA(claims jwt.Claims, privateKey *rsa.PrivateKey) (string, error) {
    token := jwt.NewWithClaims(jwt.SigningMethodRS256, claims)
    return token.SignedString(privateKey)
}

func VerifyWithRSA(tokenString string, publicKey *rsa.PublicKey) (jwt.Claims, error) {
    token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
            return nil, fmt.Errorf("unexpected signing method")
        }
        return publicKey, nil
    })

    if err != nil {
        return nil, err
    }

    return token.Claims, nil
}
```

### 5. Claims 验证中间件

```go
type AuthConfig struct {
    ValidMethods []string
    Leeway       time.Duration
}

func NewAuthMiddleware(config *AuthConfig, secret []byte, blacklist *TokenBlacklist) gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "missing authorization header"})
            c.Abort()
            return
        }

        parts := strings.Split(authHeader, " ")
        if len(parts) != 2 || strings.ToLower(parts[0]) != "bearer" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid authorization format"})
            c.Abort()
            return
        }

        tokenString := parts[1]

        if blacklist.Contains(tokenString) {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "token has been revoked"})
            c.Abort()
            return
        }

        token, err := jwt.ParseWithClaims(tokenString, &UserClaims{}, func(token *jwt.Token) (interface{}, error) {
            return secret, nil
        },
            jwt.WithValidMethods(config.ValidMethods),
            jwt.WithLeeway(config.Leeway),
        )

        if err != nil {
            c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
            c.Abort()
            return
        }

        if !token.Valid {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid token"})
            c.Abort()
            return
        }

        claims, ok := token.Claims.(*UserClaims)
        if !ok {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid claims"})
            c.Abort()
            return
        }

        c.Set("claims", claims)
        c.Set("user_id", claims.UserID)
        c.Set("username", claims.Username)
        c.Set("role", claims.Role)
        c.Next()
    }
}
```

### 6. 速率限制和安全头

```go
func SecurityHeadersMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("X-Content-Type-Options", "nosniff")
        c.Header("X-Frame-Options", "DENY")
        c.Header("X-XSS-Protection", "1; mode=block")
        c.Header("Content-Security-Policy", "default-src 'self'")
        c.Next()
    }
}

func RateLimitMiddleware(limiter *rate.Limiter) gin.HandlerFunc {
    return func(c *gin.Context) {
        if !limiter.Allow() {
            c.JSON(http.StatusTooManyRequests, gin.H{"error": "rate limit exceeded"})
            c.Abort()
            return
        }
        c.Next()
    }
}
```

## 认证与鉴权系统设计

### 1. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Client (Web/Mobile)                    │
└────────────────────┬────────────────────────────────────────┘
                     │ 1. Login (username/password)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway / Load Balancer                  │
└────────────────────┬────────────────────────────────────────┘
                     │ 2. Forward to Auth Service
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                      Auth Service                               │
│  - User Authentication                                          │
│  - Token Generation (Access + Refresh)                        │
│  - Token Validation                                             │
│  - Token Revocation                                             │
└────────┬──────────────────┬──────────────────────────────────┘
         │ 3. Return Tokens │
         │                  │ 4. Validate Token
         ↓                  ↓
┌──────────┐         ┌──────────────────────────────────────────┐
│  Client  │         │         Resource Services                 │
└──────────┘         │  - User Service                           │
                     │  - Order Service                          │
                     │  - Payment Service                        │
                     └──────────────────────────────────────────┘
```

### 2. 目录结构

```
auth/
├── api/
│   ├── handler/
│   │   ├── auth_handler.go
│   │   └── token_handler.go
│   └── middleware/
│       ├── auth_middleware.go
│       └── role_middleware.go
├── config/
│   └── jwt_config.go
├── internal/
│   ├── model/
│   │   ├── user.go
│   │   └── token.go
│   ├── repository/
│   │   ├── user_repository.go
│   │   └── token_repository.go
│   └── service/
│       ├── auth_service.go
│       └── token_service.go
├── pkg/
│   └── jwt/
│       ├── generator.go
│       └── validator.go
└── main.go
```

### 3. 核心接口设计

#### Auth Service 接口

```go
package service

import (
    "context"
)

type AuthService interface {
    Login(ctx context.Context, username, password string) (*TokenPair, error)
    Logout(ctx context.Context, userID uint, accessToken string) error
    RefreshToken(ctx context.Context, refreshToken string) (*TokenPair, error)
    ChangePassword(ctx context.Context, userID uint, oldPassword, newPassword string) error
    ResetPassword(ctx context.Context, email string) error
}

type TokenPair struct {
    AccessToken  string `json:"access_token"`
    RefreshToken string `json:"refresh_token"`
    TokenType    string `json:"token_type"`
    ExpiresIn    int64  `json:"expires_in"`
}
```

#### Token Service 接口

```go
type TokenService interface {
    GenerateAccessToken(ctx context.Context, user *User) (string, error)
    GenerateRefreshToken(ctx context.Context, user *User) (string, error)
    ValidateAccessToken(ctx context.Context, token string) (*UserClaims, error)
    ValidateRefreshToken(ctx context.Context, token string) (*RefreshClaims, error)
    RevokeAccessToken(ctx context.Context, token string) error
    RevokeRefreshToken(ctx context.Context, userID uint, token string) error
}
```

### 4. 完整的登录流程

```go
func (h *AuthHandler) Login(c *gin.Context) {
    var req LoginRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    user, err := h.userRepo.FindByUsername(req.Username)
    if err != nil {
        c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
        return
    }

    if !user.CheckPassword(req.Password) {
        c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
        return
    }

    tokenPair, err := h.authService.Login(c.Request.Context(), user)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to generate tokens"})
        return
    }

    c.SetCookie("refresh_token", tokenPair.RefreshToken,
        int(time.Hour*24*7), "/", "", true, true)

    c.JSON(http.StatusOK, gin.H{
        "access_token": tokenPair.AccessToken,
        "token_type":   "Bearer",
        "expires_in":   tokenPair.ExpiresIn,
    })
}
```

### 5. 权限控制设计

#### RBAC 模型

```go
type Permission string

const (
    PermissionRead   Permission = "read"
    PermissionWrite  Permission = "write"
    PermissionDelete Permission = "delete"
    PermissionAdmin  Permission = "admin"
)

type Role string

const (
    RoleGuest Role = "guest"
    RoleUser  Role = "user"
    RoleAdmin Role = "admin"
)

var rolePermissions = map[Role][]Permission{
    RoleGuest: {PermissionRead},
    RoleUser:  {PermissionRead, PermissionWrite},
    RoleAdmin: {PermissionRead, PermissionWrite, PermissionDelete, PermissionAdmin},
}

func (r Role) HasPermission(permission Permission) bool {
    permissions, ok := rolePermissions[r]
    if !ok {
        return false
    }
    for _, p := range permissions {
        if p == permission {
            return true
        }
    }
    return false
}
```

#### 权限中间件

```go
func RequirePermission(permission Permission) gin.HandlerFunc {
    return func(c *gin.Context) {
        role, exists := c.Get("role")
        if !exists {
            c.JSON(http.StatusForbidden, gin.H{"error": "role not found"})
            c.Abort()
            return
        }

        if !role.(Role).HasPermission(permission) {
            c.JSON(http.StatusForbidden, gin.H{"error": "insufficient permissions"})
            c.Abort()
            return
        }

        c.Next()
    }
}

func RequireRole(roles ...Role) gin.HandlerFunc {
    return func(c *gin.Context) {
        role, exists := c.Get("role")
        if !exists {
            c.JSON(http.StatusForbidden, gin.H{"error": "role not found"})
            c.Abort()
            return
        }

        userRole := role.(Role)
        for _, allowedRole := range roles {
            if userRole == allowedRole {
                c.Next()
                return
            }
        }

        c.JSON(http.StatusForbidden, gin.H{"error": "insufficient permissions"})
        c.Abort()
    }
}
```

### 6. 审计日志

```go
type AuditLog struct {
    ID        uint      `gorm:"primaryKey"`
    UserID    uint      `gorm:"index"`
    Action    string    `gorm:"index"`
    Resource  string
    IP        string
    UserAgent string
    Success   bool
    Error     string
    CreatedAt time.Time
}

func AuditMiddleware(logger AuditLogger) gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        
        c.Next()
        
        userID, _ := c.Get("user_id")
        action := c.Request.Method + " " + c.Request.URL.Path
        
        log := AuditLog{
            UserID:    userID.(uint),
            Action:    action,
            IP:        c.ClientIP(),
            UserAgent: c.GetHeader("User-Agent"),
            Success:   c.Writer.Status() < 400,
            CreatedAt: start,
        }
        
        logger.Log(log)
    }
}
```

## 总结

::: tip 关键要点
1. **密钥安全**：使用强密钥，从环境变量读取，定期轮换
2. **短期 Token**：Access Token 短期过期（15分钟-2小时），配合 Refresh Token
3. **签名算法**：优先使用 RS256 非对称加密，微服务架构更安全
4. **Token 黑名单**：实现登出功能，使用 Redis 存储黑名单
5. **算法验证**：强制验证签名算法，防止算法切换攻击
6. **Claims 最小化**：只存储必要信息，不存储敏感数据
7. **错误处理**：不要忽略任何错误，正确处理各种异常情况
8. **RBAC 权限**：实现基于角色的访问控制
9. **审计日志**：记录所有认证和授权操作
10. **安全头**：使用安全响应头，防止常见 Web 攻击
:::

通过遵循这些最佳实践，您可以构建一个安全、可靠、可扩展的 JWT 认证与鉴权系统。
