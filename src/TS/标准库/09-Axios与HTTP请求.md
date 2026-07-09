---
title: Axios与HTTP请求
date: 2026-07-09
footer: Trae编辑
---

# Axios 与 HTTP 请求

## Go 开发者已知

Go 使用 `net/http` 标准库发送 HTTP 请求，可自定义 Transport 实现拦截器逻辑。

```go
// Go 基础 HTTP 请求
import (
    "bytes"
    "encoding/json"
    "net/http"
)

type User struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

func GetUser(id int) (*User, error) {
    resp, err := http.Get(fmt.Sprintf("https://api.example.com/users/%d", id))
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("unexpected status: %d", resp.StatusCode)
    }

    var user User
    if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
        return nil, err
    }
    return &user, nil
}

// Go 的 Transport 实现拦截器
type LoggingTransport struct {
    Transport http.RoundTripper
}

func (t *LoggingTransport) RoundTrip(req *http.Request) (*http.Response, error) {
    fmt.Printf("[%s] %s\n", req.Method, req.URL)
    resp, err := t.Transport.RoundTrip(req)
    if err != nil {
        fmt.Printf("[ERROR] %v\n", err)
    }
    return resp, err
}

// 使用
client := &http.Client{
    Transport: &LoggingTransport{
        Transport: http.DefaultTransport,
    },
    Timeout: 30 * time.Second,
}
```

## TS 怎么做

### 安装与基础用法

```bash
npm install axios
# TS 类型已内置，无需额外安装
```

```ts
import axios from "axios";

// 基础 GET 请求
const response = await axios.get("https://api.example.com/users");
console.log(response.data); // 响应体
console.log(response.status); // 状态码 200
console.log(response.headers); // 响应头

// POST 请求
const newUser = await axios.post("https://api.example.com/users", {
    name: "Alice",
    email: "alice@example.com",
});

// 请求配置
const resp = await axios({
    method: "GET",
    url: "https://api.example.com/users",
    params: { page: 1, limit: 10 },    // URL 查询参数
    headers: { Authorization: "Bearer token123" },
    timeout: 5000,                       // 超时
});
```

### 泛型约束 —— axios.get\<T\>()

```ts
// 泛型 —— 指定响应数据类型
interface User {
    id: number;
    name: string;
    email: string;
    createdAt: string;
}

interface PaginatedResponse<T> {
    data: T[];
    total: number;
    page: number;
    limit: number;
}

// 单个对象
const { data: user } = await axios.get<User>("/api/users/1");
// user 类型: User
console.log(user.name);

// 分页响应
const { data: page } = await axios.get<PaginatedResponse<User>>("/api/users", {
    params: { page: 1, limit: 20 },
});
// page.data: User[]
// page.total: number

// 注意：axios.get<T>() 只影响 TS 类型推断，不保证运行时类型安全
// 运行时数据仍需 Zod 校验（见第8篇）
```

### 拦截器 —— 类比 Go Transport

```ts
import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from "axios";

// 创建实例
const api: AxiosInstance = axios.create({
    baseURL: "https://api.example.com/v1",
    timeout: 10000,
    headers: { "Content-Type": "application/json" },
});

// 请求拦截器 —— 添加 Token、日志等
api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // 添加认证头
        const token = localStorage.getItem("token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        // 请求日志
        console.log(`[${config.method?.toUpperCase()}] ${config.url}`);

        return config;
    },
    (error) => {
        // 请求错误处理
        return Promise.reject(error);
    }
);

// 响应拦截器 —— 统一错误处理、数据提取
api.interceptors.response.use(
    (response: AxiosResponse) => {
        // 提取 data 字段
        return response.data;
    },
    (error) => {
        if (error.response) {
            // 服务器返回了错误状态码
            const { status, data } = error.response;
            switch (status) {
                case 401:
                    // 未授权 —— 跳转登录
                    localStorage.removeItem("token");
                    window.location.href = "/login";
                    break;
                case 403:
                    console.error("权限不足");
                    break;
                case 404:
                    console.error("资源不存在");
                    break;
                case 500:
                    console.error("服务器错误");
                    break;
            }
        } else if (error.request) {
            // 请求已发出但没有收到响应
            console.error("网络错误：无法连接到服务器");
        } else {
            // 请求配置出错
            console.error("请求配置错误:", error.message);
        }
        return Promise.reject(error);
    }
);

// 使用实例
const user = await api.get<User>("/users/1"); // 直接返回 data，而非 response.data
```

::: code-tabs#lang

@tab TypeScript (Axios)

```ts
// Axios 请求拦截器
api.interceptors.request.use((config) => {
    config.headers.Authorization = `Bearer ${getToken()}`;
    return config;
});
```

@tab Go (net/http Transport)

```go
// Go Transport 拦截器
type AuthTransport struct {
    Transport http.RoundTripper
}

func (t *AuthTransport) RoundTrip(req *http.Request) (*http.Response, error) {
    req.Header.Set("Authorization", "Bearer "+getToken())
    return t.Transport.RoundTrip(req)
}
```

:::

### AbortController —— 请求取消

```ts
// 使用 AbortController 取消 Axios 请求
import axios, { CancelTokenSource } from "axios";

// 方式1: AbortController（推荐，浏览器标准）
const controller = new AbortController();

// 发送请求
const request = axios.get("/api/heavy-task", {
    signal: controller.signal,
});

// 取消请求
controller.abort();

// 处理取消
try {
    await request;
} catch (err) {
    if (axios.isCancel(err)) {
        console.log("请求被取消:", err.message);
    } else {
        console.error("其他错误:", err);
    }
}

// 方式2: Axios 的 CancelToken（旧 API，已弃用）
const source = axios.CancelToken.source();
axios.get("/api/data", { cancelToken: source.token });
source.cancel("用户取消了操作");

// 实际场景：搜索框取消前一次请求
class SearchService {
    private controller: AbortController | null = null;

    async search(query: string): Promise<SearchResult[]> {
        // 取消前一次未完成的请求
        this.controller?.abort();
        this.controller = new AbortController();

        try {
            const { data } = await axios.get<SearchResult[]>("/api/search", {
                params: { q: query },
                signal: this.controller.signal,
            });
            return data;
        } catch (err) {
            if (axios.isCancel(err)) return [];
            throw err;
        }
    }
}
```

### 错误处理类型守卫

```ts
import axios, { AxiosError } from "axios";

// Axios 错误类型
interface ApiErrorResponse {
    message: string;
    code: string;
    details?: Record<string, string[]>;
}

// 类型守卫 —— 判断是否为 Axios 错误
function isAxiosError<T = ApiErrorResponse>(
    error: unknown
): error is AxiosError<T> {
    return axios.isAxiosError(error);
}

// 统一错误处理
async function safeRequest<T>(url: string): Promise<T | null> {
    try {
        const { data } = await axios.get<T>(url);
        return data;
    } catch (err) {
        if (isAxiosError<ApiErrorResponse>(err)) {
            if (err.response) {
                // 服务器返回了错误
                const apiError = err.response.data;
                console.error(`[${apiError.code}] ${apiError.message}`);
                if (apiError.details) {
                    for (const [field, msgs] of Object.entries(apiError.details)) {
                        console.error(`  ${field}: ${msgs.join(", ")}`);
                    }
                }
            } else if (err.request) {
                // 网络层错误
                console.error("网络不可用，请检查连接");
            }
        } else if (err instanceof Error) {
            console.error("非 HTTP 错误:", err.message);
        }
        return null;
    }
}
```

### 封装类型安全 API Client

```ts
// Best: 完整的 API Client 封装
import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from "axios";

// 通用 API 响应
interface ApiResponse<T> {
    code: number;
    message: string;
    data: T;
}

class ApiClient {
    private client: AxiosInstance;

    constructor(baseURL: string) {
        this.client = axios.create({
            baseURL,
            timeout: 15000,
            headers: { "Content-Type": "application/json" },
        });

        this.setupInterceptors();
    }

    private setupInterceptors(): void {
        // 请求拦截
        this.client.interceptors.request.use((config) => {
            const token = this.getToken();
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });

        // 响应拦截
        this.client.interceptors.response.use(
            (response) => response.data,
            (error: AxiosError<ApiResponse<unknown>>) => {
                if (error.response?.status === 401) {
                    this.handleUnauthorized();
                }
                return Promise.reject(this.normalizeError(error));
            }
        );
    }

    private getToken(): string | null {
        return localStorage.getItem("access_token");
    }

    private handleUnauthorized(): void {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
    }

    private normalizeError(error: AxiosError<ApiResponse<unknown>>): AppError {
        if (error.response) {
            const { status, data } = error.response;
            return new AppError(
                data?.message || `HTTP ${status}`,
                status,
                data?.code
            );
        }
        if (error.request) {
            return new AppError("网络连接失败", 0, "NETWORK_ERROR");
        }
        return new AppError(error.message, -1, "UNKNOWN_ERROR");
    }

    // 类型安全的请求方法
    async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
        return this.client.get<any, T>(url, config);
    }

    async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
        return this.client.post<any, T>(url, data, config);
    }

    async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
        return this.client.put<any, T>(url, data, config);
    }

    async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
        return this.client.delete<any, T>(url, config);
    }
}

class AppError extends Error {
    constructor(
        message: string,
        public statusCode: number,
        public code?: string
    ) {
        super(message);
        this.name = "AppError";
    }
}

// 使用
const apiClient = new ApiClient("https://api.example.com/v1");
const users = await apiClient.get<User[]>("/users");
// users 类型: User[]（不含 response.data 包装）
```

## 差异分析

| 维度 | Go (net/http) | TypeScript (Axios) |
|------|--------------|-------------------|
| **请求构造** | `http.NewRequest` + `client.Do` | `axios.get/post/put/delete` 直接调用 |
| **请求体序列化** | `json.NewDecoder/Encoder` | 自动 JSON 序列化/反序列化 |
| **泛型响应** | 手动类型断言 `json.Decode` | `axios.get<T>()` 编译期泛型 |
| **拦截器** | `Transport.RoundTrip` 接口 | `interceptors.request/response.use` |
| **请求取消** | `context.Context` | `AbortController` / `CancelToken` |
| **超时** | `client.Timeout` | `config.timeout` |
| **错误类型** | 手动判断 `!= nil` | `AxiosError` + `isAxiosError()` 类型守卫 |
| **并发请求** | `sync.WaitGroup` + goroutine | `axios.all` / `Promise.all` |

## Bad Practice

### 1. 不处理网络错误

```ts
// Bad: 假设请求总是成功的
const { data } = await axios.get("/api/users");
// 如果网络断开、服务器 500、超时等，直接抛出未处理异常

// Bad: 只在 catch 中打印
try {
    const { data } = await axios.get("/api/users");
} catch (err) {
    console.log(err); // 用户看不到友好的错误提示
}

// Best: 统一错误处理
try {
    const { data } = await axios.get("/api/users");
    // 处理数据
} catch (err) {
    if (axios.isAxiosError(err)) {
        if (err.response) {
            // HTTP 错误（4xx/5xx）
            showToast(`请求失败: ${err.response.status}`);
        } else {
            // 网络错误
            showToast("网络连接失败，请检查网络");
        }
    } else {
        showToast("发生未知错误");
    }
}
```

### 2. 重复创建 Axios 实例

```ts
// Bad: 每次调用都创建新实例
async function fetchUsers() {
    const api = axios.create({ baseURL: "https://api.example.com" });
    return api.get("/users");
}

async function fetchPosts() {
    const api = axios.create({ baseURL: "https://api.example.com" });
    return api.get("/posts");
}
// 拦截器、默认配置等都重复创建

// Best: 单例模式
const api = axios.create({ baseURL: "https://api.example.com" });
api.interceptors.request.use(/* ... */);

async function fetchUsers() { return api.get("/users"); }
async function fetchPosts() { return api.get("/posts"); }
```

### 3. 忘记处理响应拦截器的返回值

```ts
// Bad: 响应拦截器没有 return
api.interceptors.response.use(
    (response) => {
        // 没 return！后面的调用拿不到数据
        console.log("Response received");
    },
    (error) => Promise.reject(error)
);

// 调用处 data 是 undefined
const data = await api.get("/users");
console.log(data); // undefined

// Best: 始终 return 处理后的值
api.interceptors.response.use(
    (response) => response.data,
    (error) => Promise.reject(error)
);
```

### 4. 不取消已离开页面的请求

```ts
// Bad: 组件卸载后请求继续执行
class UserList extends React.Component {
    async componentDidMount() {
        const users = await axios.get("/api/users");
        // 如果组件已卸载，setState 会报错
        this.setState({ users });
    }
}

// Best: 组件卸载时取消请求
class UserListBetter extends React.Component {
    private controller = new AbortController();

    async componentDidMount() {
        try {
            const { data } = await axios.get("/api/users", {
                signal: this.controller.signal,
            });
            this.setState({ users: data });
        } catch (err) {
            if (!axios.isCancel(err)) {
                console.error(err);
            }
        }
    }

    componentWillUnmount() {
        this.controller.abort();
    }
}
```

## Best Practice

### 1. 统一封装拦截器

```ts
// Best: 模块化拦截器
// interceptors/auth.ts
export function authInterceptor(config: InternalAxiosRequestConfig) {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}

// interceptors/logging.ts
export function loggingInterceptor(config: InternalAxiosRequestConfig) {
    console.log(`[${new Date().toISOString()}] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
}

// interceptors/error.ts
export function errorInterceptor(error: AxiosError) {
    if (error.response) {
        switch (error.response.status) {
            case 401: window.dispatchEvent(new CustomEvent("auth:unauthorized")); break;
            case 429: /* rate limited */ break;
        }
    }
    return Promise.reject(error);
}

// api.ts —— 组装
import { authInterceptor, loggingInterceptor, errorInterceptor } from "./interceptors";

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL });
api.interceptors.request.use(authInterceptor);
api.interceptors.request.use(loggingInterceptor);
api.interceptors.response.use((r) => r.data, errorInterceptor);
```

### 2. 类型安全的 retry 封装

```ts
// Best: 带重试的请求
async function withRetry<T>(
    fn: () => Promise<T>,
    maxRetries = 3,
    baseDelay = 1000
): Promise<T> {
    let lastError: unknown;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (err) {
            lastError = err;
            if (attempt === maxRetries) break;

            // 只对特定错误重试
            if (axios.isAxiosError(err)) {
                const status = err.response?.status;
                if (status && status < 500) {
                    // 4xx 错误不重试
                    throw err;
                }
            }

            // 指数退避
            const delay = baseDelay * Math.pow(2, attempt - 1);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }

    throw lastError;
}

// 使用
const user = await withRetry(() =>
    axios.get<User>("/api/users/1").then(r => r.data)
);
```

### 3. 请求失败队列（离线重试）

```ts
// Best: 请求队列 —— 断网时缓存请求，恢复后自动重试
class RequestQueue {
    private queue: Array<() => Promise<unknown>> = [];
    private isOnline = navigator.onLine;

    constructor() {
        window.addEventListener("online", () => this.replay());
        window.addEventListener("offline", () => { this.isOnline = false; });
    }

    async enqueue<T>(request: () => Promise<T>): Promise<T> {
        if (this.isOnline) return request();

        return new Promise((resolve, reject) => {
            this.queue.push(async () => {
                try {
                    resolve(await request());
                } catch (err) {
                    reject(err);
                }
            });
        });
    }

    private async replay(): Promise<void> {
        this.isOnline = true;
        const pending = [...this.queue];
        this.queue = [];
        for (const request of pending) {
            await request().catch(console.error);
        }
    }
}
```

::: tip 总结

1. 用单例 `axios.create()` 替代每个组件单独创建实例
2. 拦截器实现认证/日志/错误处理的统一管理（类比 Go Transport）
3. `AbortController` 取消请求避免内存泄漏和竞态
4. 使用 `isAxiosError()` 类型守卫精准捕获 HTTP 错误
5. 响应拦截器中 `return response.data` 简化调用方代码
6. 封装 `ApiClient` 类提供类型安全的请求接口

:::
