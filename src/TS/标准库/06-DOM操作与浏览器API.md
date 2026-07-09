---
title: DOM操作与浏览器API
date: 2026-07-09
footer: Trae编辑
---

# DOM 操作与浏览器 API

## Go 开发者已知

Go 主要运行在服务端，没有浏览器 DOM。但 Go 通过 `syscall/js` 可以在 WebAssembly 中操作 DOM。

```go
// Go WASM 中的 DOM 操作（syscall/js）
import "syscall/js"

func main() {
    doc := js.Global().Get("document")

    // 查询元素
    element := doc.Call("querySelector", "#app")

    // 修改内容
    element.Set("textContent", "Hello from Go WASM!")

    // 添加事件监听
    button := doc.Call("querySelector", "#btn")
    button.Call("addEventListener", "click", js.FuncOf(func(this js.Value, args []js.Value) any {
        println("Button clicked!")
        return nil
    }))

    // 创建新元素
    div := doc.Call("createElement", "div")
    div.Set("className", "container")
    div.Set("innerHTML", "<p>New content</p>")
    doc.Get("body").Call("appendChild", div)

    // 阻塞主 goroutine 防止程序退出
    select {}
}
```

## TS 怎么做

### Document / Element / HTMLElement 类型层级

```ts
// DOM 类型层级 —— 类似继承关系
// EventTarget → Node → Element → HTMLElement → HTMLDivElement / HTMLInputElement 等

// EventTarget: addEventListener, removeEventListener, dispatchEvent
// Node: parentNode, childNodes, appendChild, removeChild
// Element: classList, attributes, querySelector
// HTMLElement: style, hidden, click, focus
// HTMLInputElement: value, checked, files
// HTMLFormElement: submit, reset, elements

// 类型安全的查询
const div = document.querySelector<HTMLDivElement>("#app");
// div 的类型是 HTMLDivElement | null

const input = document.querySelector<HTMLInputElement>('input[name="email"]');
// input 的类型是 HTMLInputElement | null

// 如果不指定泛型，返回类型不够精确
const el = document.querySelector("#app");
// el 的类型是 Element | null（缺少 HTMLDivElement 的特定属性）
```

### addEventListener 类型推断

```ts
// addEventListener 根据事件名称自动推断事件对象类型
const button = document.querySelector<HTMLButtonElement>("#submit-btn");

button?.addEventListener("click", (e) => {
    // e 自动推断为 MouseEvent
    console.log(e.clientX, e.clientY);
});

button?.addEventListener("keydown", (e) => {
    // e 自动推断为 KeyboardEvent
    if (e.key === "Enter") console.log("Pressed Enter!");
});

const input = document.querySelector<HTMLInputElement>("#username");
input?.addEventListener("input", (e) => {
    // e 自动推断为 Event
    const target = e.target as HTMLInputElement;
    console.log(target.value);
});

// 自定义事件 —— 使用泛型指定具体类型
type UserEvent = CustomEvent<{ userId: number; name: string }>;
document.addEventListener("user-login", ((e: UserEvent) => {
    console.log(e.detail.userId, e.detail.name);
}) as EventListener);
```

### Fetch API —— 类型安全封装

```ts
// Fetch API —— 现代浏览器内置 HTTP 请求（类比 Go net/http）
interface ApiResponse<T> {
    data: T;
    status: number;
    message: string;
}

// 基础用法
const response = await fetch("/api/users");
const users = await response.json() as User[];

// 类型安全的封装
async function fetchApi<T>(
    url: string,
    options?: RequestInit
): Promise<ApiResponse<T>> {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...options?.headers,
        },
        ...options,
    });

    if (!response.ok) {
        throw new ApiError(
            `HTTP ${response.status}: ${response.statusText}`,
            response.status
        );
    }

    return {
        data: (await response.json()) as T,
        status: response.status,
        message: response.statusText,
    };
}

// 使用
interface User {
    id: number;
    name: string;
    email: string;
}

const result = await fetchApi<User[]>("/api/users");
console.log(result.data); // User[]
```

### localStorage / sessionStorage

```ts
// localStorage —— 持久化存储（类比 Go 的文件存储）
// sessionStorage —— 会话级存储（关闭标签页即清除）
// 两者 API 完全相同

// 基础操作
localStorage.setItem("theme", "dark");
const theme = localStorage.getItem("theme"); // "dark"
localStorage.removeItem("theme");
localStorage.clear();

// 存储对象需要 JSON 序列化
interface UserPreferences {
    theme: "light" | "dark";
    fontSize: number;
    language: string;
}

function savePreferences(prefs: UserPreferences): void {
    localStorage.setItem("preferences", JSON.stringify(prefs));
}

function loadPreferences(): UserPreferences | null {
    const raw = localStorage.getItem("preferences");
    if (!raw) return null;
    try {
        return JSON.parse(raw) as UserPreferences;
    } catch {
        return null;
    }
}

// 监听 storage 事件（其他标签页修改时触发）
window.addEventListener("storage", (e) => {
    if (e.key === "preferences") {
        console.log("Preferences changed in another tab:", e.newValue);
    }
});
```

### IntersectionObserver / ResizeObserver

```ts
// IntersectionObserver —— 检测元素是否在视口中（类比 Go 无对应，浏览器特有）
// 用途：无限滚动、懒加载、广告曝光统计

const observer = new IntersectionObserver(
    (entries) => {
        for (const entry of entries) {
            if (entry.isIntersecting) {
                console.log("Element is visible:", entry.target);
                // 加载图片
                const img = entry.target as HTMLImageElement;
                img.src = img.dataset.src ?? "";
                // 加载后停止观察
                observer.unobserve(entry.target);
            }
        }
    },
    { threshold: 0.1 } // 10% 可见时触发
);

// 观察所有懒加载图片
document.querySelectorAll<HTMLImageElement>("img[data-src]")
    .forEach(img => observer.observe(img));

// ResizeObserver —— 监听元素尺寸变化
const resizeObserver = new ResizeObserver((entries) => {
    for (const entry of entries) {
        const { width, height } = entry.contentRect;
        console.log(`Element resized: ${width}x${height}`);
    }
});

resizeObserver.observe(document.querySelector("#sidebar")!);
```

## 差异分析

| 维度 | Go (syscall/js) | TypeScript (原生 DOM) |
|------|----------------|---------------------|
| **类型系统** | 无类型安全，`js.Value` + `Call` 方法 | 完整 DOM 类型层级（2000+ 类型） |
| **查询选择器** | `doc.Call("querySelector", "#id")` | `document.querySelector<T>("selector")` |
| **事件处理** | `Call("addEventListener", ...)` | 原生 `addEventListener` + 类型推断 |
| **HTTP 请求** | `net/http` 或 `js.Global().Call("fetch")` | `fetch()` 内置，类型需封装 |
| **本地存储** | `js.Global().Get("localStorage")` | `localStorage` 原生 API |
| **观察者 API** | 需手动轮询或 js 桥接 | IntersectionObserver / ResizeObserver 内置 |
| **null 检查** | 调用可能 panic | 类型系统强制 null 检查（strict 模式） |

## Bad Practice

### 1. 忽略 null 检查

```ts
// Bad: 假设元素一定存在
const el = document.querySelector("#app")!; // 非空断言 —— 如果不存在则运行时崩溃
el.innerHTML = "content"; // 可能 Cannot read properties of null

// Bad: 使用非空断言链式调用
document.querySelector("#btn")!.addEventListener("click", handler);

// Best: 使用可选链和空值合并
const app = document.querySelector<HTMLDivElement>("#app");
if (app) {
    app.innerHTML = "content";
}

// 或者
document.querySelector("#btn")?.addEventListener("click", handler);

// 或者使用断言函数
function assertElement<T extends Element>(
    selector: string,
    type?: new (...args: any[]) => T
): T {
    const el = document.querySelector<T>(selector);
    if (!el) throw new Error(`Element "${selector}" not found`);
    return el;
}

const button = assertElement("#submit-btn", HTMLButtonElement);
button.disabled = true; // 类型安全且无需 null 检查
```

### 2. 直接操作 innerHTML 导致 XSS

```ts
// Bad: innerHTML 插入用户内容 —— XSS 漏洞
const userInput = "<script>alert('xss')</script>";
document.querySelector("#content")!.innerHTML = userInput; // 执行了恶意脚本！

// Best: 使用 textContent 或 createTextNode
document.querySelector("#content")!.textContent = userInput; // 安全

// 如果需要 HTML（且信任来源），使用 insertAdjacentHTML
// 或者 DOMPurify 库
function sanitizeHTML(str: string): string {
    const div = document.createElement("div");
    div.textContent = str; // 先转义
    return div.innerHTML;
}
```

### 3. 频繁操作 DOM 导致性能问题

```ts
// Bad: 循环中反复操作 DOM
const list = document.querySelector("#list")!;
for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li); // 每次 append 都触发重排
}

// Best: 使用 DocumentFragment 或一次更新
const fragment = document.createDocumentFragment();
for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    fragment.appendChild(li);
}
list.appendChild(fragment); // 一次重排

// 或使用 innerHTML 批量写入
list.innerHTML = items.map(item => `<li>${escapeHtml(item)}</li>`).join("");
```

### 4. 未移除事件监听导致内存泄漏

```ts
// Bad: 事件监听器导致 DOM 元素无法被 GC
class Widget {
    private element: HTMLElement;

    constructor() {
        this.element = document.createElement("div");
        document.body.appendChild(this.element);
        // 箭头函数匿名引用，无法移除
        window.addEventListener("resize", () => {
            this.element.style.width = `${window.innerWidth}px`;
        });
    }

    destroy() {
        document.body.removeChild(this.element);
        // 但是 resize 监听器仍然存在！this.element 无法被 GC
    }
}

// Best: 保存引用以便移除
class WidgetBetter {
    private element: HTMLElement;
    private boundHandler: () => void;

    constructor() {
        this.element = document.createElement("div");
        document.body.appendChild(this.element);
        this.boundHandler = () => {
            this.element.style.width = `${window.innerWidth}px`;
        };
        window.addEventListener("resize", this.boundHandler);
    }

    destroy() {
        window.removeEventListener("resize", this.boundHandler);
        document.body.removeChild(this.element);
    }
}
```

## Best Practice

### 1. 类型安全的 DOM 工具函数

```ts
// Best: 封装常用 DOM 操作
class DOM {
    static select<T extends Element = HTMLElement>(
        selector: string
    ): T | null {
        return document.querySelector<T>(selector);
    }

    static selectAll<T extends Element = HTMLElement>(
        selector: string
    ): T[] {
        return [...document.querySelectorAll<T>(selector)];
    }

    static create<K extends keyof HTMLElementTagNameMap>(
        tag: K,
        attrs?: Partial<HTMLElementTagNameMap[K]>,
        children?: (string | Node)[]
    ): HTMLElementTagNameMap[K] {
        const el = document.createElement(tag);
        if (attrs) Object.assign(el, attrs);
        if (children) el.append(...children);
        return el;
    }

    static on<K extends keyof HTMLElementEventMap>(
        el: HTMLElement,
        event: K,
        handler: (e: HTMLElementEventMap[K]) => void,
        options?: AddEventListenerOptions
    ): () => void {
        el.addEventListener(event, handler as EventListener, options);
        // 返回取消函数
        return () => el.removeEventListener(event, handler as EventListener);
    }
}

// 使用
const btn = DOM.select<HTMLButtonElement>("#submit");
DOM.on(btn!, "click", (e) => {
    e.preventDefault();
    console.log("Submitted!");
});
```

### 2. 封装类型安全的 Fetch 客户端

```ts
// Best: 统一的 HTTP 客户端
class HttpClient {
    private baseURL: string;

    constructor(baseURL: string, private defaultHeaders: Record<string, string> = {}) {
        this.baseURL = baseURL.replace(/\/+$/, "");
    }

    private async request<T>(
        method: string,
        path: string,
        body?: unknown
    ): Promise<T> {
        const url = `${this.baseURL}${path}`;

        const headers = new Headers({
            "Content-Type": "application/json",
            ...this.defaultHeaders,
        });

        const config: RequestInit = {
            method,
            headers,
            body: body ? JSON.stringify(body) : undefined,
        };

        const response = await fetch(url, config);

        if (!response.ok) {
            const errorBody = await response.text().catch(() => "");
            throw new HttpError(response.status, response.statusText, errorBody);
        }

        // 处理 No-Content 响应
        if (response.status === 204) return undefined as T;

        return response.json() as Promise<T>;
    }

    get<T>(path: string): Promise<T> {
        return this.request<T>("GET", path);
    }

    post<T>(path: string, body: unknown): Promise<T> {
        return this.request<T>("POST", path, body);
    }

    put<T>(path: string, body: unknown): Promise<T> {
        return this.request<T>("PUT", path, body);
    }

    delete<T>(path: string): Promise<T> {
        return this.request<T>("DELETE", path);
    }
}

class HttpError extends Error {
    constructor(
        public status: number,
        public statusText: string,
        public body: string
    ) {
        super(`HTTP ${status}: ${statusText}`);
        this.name = "HttpError";
    }
}

// 使用
const api = new HttpClient("https://api.example.com/v1");
const users = await api.get<User[]>("/users");
const newUser = await api.post<User>("/users", { name: "Alice" });
```

### 3. 使用 Observer API 优化性能

```ts
// Best: IntersectionObserver 实现虚拟列表/懒加载
class LazyLoader {
    private observer: IntersectionObserver;

    constructor(
        private options: { rootMargin?: string; threshold?: number } = {}
    ) {
        this.observer = new IntersectionObserver(
            (entries) => {
                for (const entry of entries) {
                    if (entry.isIntersecting) {
                        const target = entry.target;
                        this.load(target);
                        this.observer.unobserve(target);
                    }
                }
            },
            { rootMargin: "200px", ...options }
        );
    }

    observe(element: HTMLElement): void {
        this.observer.observe(element);
    }

    private load(element: HTMLElement): void {
        // 加载实际内容
        if (element instanceof HTMLImageElement) {
            const src = element.dataset.src;
            if (src) element.src = src;
        }
        // 触发自定义事件
        element.dispatchEvent(new CustomEvent("loaded", { detail: element }));
    }

    destroy(): void {
        this.observer.disconnect();
    }
}

// 使用
const lazyLoader = new LazyLoader({ rootMargin: "100px" });
document.querySelectorAll<HTMLImageElement>("img[data-src]")
    .forEach(img => lazyLoader.observe(img));
```

::: tip 总结

1. 用泛型 `querySelector<T>` 获取类型安全的元素引用
2. 始终处理 null 检查（可选链、类型守卫、断言函数）
3. 避免 innerHTML 插入不可信内容，防止 XSS
4. 使用 DocumentFragment 批量更新 DOM 减少重排
5. Observer API（IntersectionObserver/ResizeObserver）比事件监听更高效
6. 及时移除事件监听防止内存泄漏

:::