---
title: Zod与运行时数据校验
date: 2026-07-09
footer: Trae编辑
---

# Zod 与运行时数据校验

## Go 开发者已知

Go 通过 `struct tag` + `validator` 包或 `json.Unmarshal` 实现运行时数据校验。TS 类型只在编译期存在，**运行时需要 Zod 验证数据结构**。

```go
// Go 的结构体标签校验
import "github.com/go-playground/validator/v10"

type CreateUserRequest struct {
    Name     string `json:"name"     validate:"required,min=2,max=50"`
    Email    string `json:"email"    validate:"required,email"`
    Age      int    `json:"age"      validate:"gte=0,lte=150"`
    Password string `json:"password" validate:"required,min=8"`
    Role     string `json:"role"     validate:"oneof=admin user viewer"`
}

var validate = validator.New()

func CreateUserHandler(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "Invalid JSON", 400)
        return
    }

    if err := validate.Struct(req); err != nil {
        // 返回验证错误详情
        http.Error(w, err.Error(), 400)
        return
    }

    // req 已验证通过，可以安全使用
    fmt.Printf("Creating user: %s (%s)\n", req.Name, req.Email)
}

// Go 的 JSON struct tag 做类型转换
type ApiResponse struct {
    Code    int    `json:"code"`
    Message string `json:"message"`
    Data    any    `json:"data,omitempty"`
}
```

## TS 怎么做

### 为什么需要运行时校验

```ts
// TS 类型只在编译期存在 —— 运行时被完全擦除
interface UserInput {
    name: string;
    age: number;
    email: string;
}

// JSON.parse 返回 any —— 完全不安全！
const raw = JSON.parse(`{ "name": "Alice", "age": "not-a-number", "email": "invalid" }`);

// raw 被断言为 UserInput，但实际 age 是 string
const input = raw as UserInput;
console.log(input.age.toFixed(2)); // 运行时崩溃！age 是字符串
```

### Zod 基础

```bash
npm install zod
```

```ts
import { z } from "zod";

// 基础 schema
const StringSchema = z.string();
const NumberSchema = z.number();
const BooleanSchema = z.boolean();
const NullSchema = z.null();
const UndefinedSchema = z.undefined();
const AnySchema = z.any();
const UnknownSchema = z.unknown();

// 带约束的基础 schema
const UsernameSchema = z.string().min(2).max(50);
const AgeSchema = z.number().int().positive().max(150);
const EmailSchema = z.string().email();
const UrlSchema = z.string().url();

// 字面量
const RoleSchema = z.enum(["admin", "user", "viewer"]);

// 解析（parse 成功返回值，失败抛异常）
const username = UsernameSchema.parse("Alice"); // "Alice"
// UsernameSchema.parse(""); // ZodError: 至少 2 个字符

// safeParse —— 不抛异常，返回 Result 类型
const result = UsernameSchema.safeParse("");
if (!result.success) {
    console.error(result.error.issues);
    // [{ code: "too_small", minimum: 2, path: [], message: "至少 2 个字符" }]
} else {
    console.log(result.data);
}
```

### z.object —— 对象校验

```ts
// 定义对象 schema —— 类比 Go struct tag
const UserSchema = z.object({
    name: z.string().min(2).max(50),
    email: z.string().email(),
    age: z.number().int().positive().max(150),
    role: z.enum(["admin", "user", "viewer"]).default("user"),
    phone: z.string().regex(/^1[3-9]\d{9}$/).optional(),
    createdAt: z.date().default(() => new Date()),
});

// 从 schema 推断类型
type User = z.infer<typeof UserSchema>;
// 等价于:
// type User = {
//   name: string;
//   email: string;
//   age: number;
//   role: "admin" | "user" | "viewer";
//   phone?: string;
//   createdAt: Date;
// };

// 解析数据
const rawData = {
    name: "Alice",
    email: "alice@example.com",
    age: 25,
    role: "admin",
};

const parsed = UserSchema.parse(rawData);
console.log(parsed); // 所有字段已验证，类型安全

// 嵌套对象
const AddressSchema = z.object({
    city: z.string(),
    street: z.string(),
    zip: z.string().regex(/^\d{5}$/),
});

const UserWithAddressSchema = z.object({
    name: z.string(),
    address: AddressSchema,
    tags: z.array(z.string()).max(5),
});

type UserWithAddress = z.infer<typeof UserWithAddressSchema>;
```

### 高级校验

```ts
// 条件校验 —— refine
const PasswordSchema = z.string()
    .min(8)
    .refine(val => /[A-Z]/.test(val), "必须包含大写字母")
    .refine(val => /[0-9]/.test(val), "必须包含数字");

// 跨字段校验 —— superRefine
const RegisterSchema = z.object({
    password: z.string().min(8),
    confirmPassword: z.string(),
}).superRefine((data, ctx) => {
    if (data.password !== data.confirmPassword) {
        ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: "两次密码不一致",
            path: ["confirmPassword"],
        });
    }
});

// transform —— 数据转换清洗
const TrimmedString = z.string().transform(s => s.trim());
const NumberString = z.string().transform(Number);
const NormalizedEmail = z.string()
    .email()
    .transform(email => email.toLowerCase().trim());

// 组合 transform
const ApiUserSchema = z.object({
    id: z.number(),
    user_name: z.string(),
    user_email: z.string().email(),
}).transform(data => ({
    id: data.id,
    name: data.user_name,
    email: data.user_email,
}));
// 输出类型: { id: number; name: string; email: string }

// union —— 联合类型
const ResultSchema = z.union([
    z.object({ status: z.literal("success"), data: z.unknown() }),
    z.object({ status: z.literal("error"), message: z.string() }),
]);

type ApiResult = z.infer<typeof ResultSchema>;
// { status: "success"; data: unknown } | { status: "error"; message: string }
```

### 前后端共享 schema

```ts
// shared/schemas/user.ts —— 前后端共享
import { z } from "zod";

export const CreateUserSchema = z.object({
    name: z.string().min(2).max(50),
    email: z.string().email(),
    password: z.string().min(8),
    age: z.number().int().positive().optional(),
});

export const UserResponseSchema = z.object({
    id: z.number(),
    name: z.string(),
    email: z.string().email(),
    createdAt: z.date(),
});

export type CreateUserInput = z.infer<typeof CreateUserSchema>;
export type UserResponse = z.infer<typeof UserResponseSchema>;
```

::: code-tabs#lang

@tab TypeScript (Zod)

```ts
// 前端使用
import { CreateUserSchema, type CreateUserInput } from "@/shared/schemas/user";

async function submitUser(data: CreateUserInput) {
    const validated = CreateUserSchema.parse(data);
    const response = await fetch("/api/users", {
        method: "POST",
        body: JSON.stringify(validated),
    });
    return response.json();
}
```

@tab Go (struct tag)

```go
// Go 后端定义（不共享）—— 需要手写两次校验
type CreateUserRequest struct {
    Name     string `json:"name"     validate:"required,min=2,max=50"`
    Email    string `json:"email"    validate:"required,email"`
    Password string `json:"password" validate:"required,min=8"`
    Age      int    `json:"age"      validate:"omitempty,gte=0,lte=150"`
}
```

:::

## 差异分析

| 维度 | Go (struct tag + validator) | TypeScript (Zod) |
|------|---------------------------|-------------------|
| **类型系统** | 编译期 + 运行时（struct tag） | 仅编译期类型 + Zod 运行时 |
| **校验时机** | JSON 反序列化 + validator | 显式调用 `.parse()` / `.safeParse()` |
| **类型派生** | 手动定义 struct | `z.infer<typeof Schema>` 自动派生 |
| **前后端共享** | 需手写双重定义 | npm 包共享同一份 schema |
| **自定义校验** | `validator.RegisterValidation` | `.refine()` / `.superRefine()` |
| **数据转换** | 需额外 `transform` 逻辑 | `.transform()` 内置 |
| **错误信息** | validator 默认英文，自定义较繁 | 中文友好，可配置 |
| **零值问题** | Go 零值语义（int=0, string=""） | 明确区分 undefined/可选/默认值 |

## Bad Practice

### 1. 重复定义类型和 schema

```ts
// Bad: 分别定义类型和 schema
interface User {
    name: string;
    email: string;
    age: number;
}

const UserSchema = z.object({
    name: z.string(),
    email: z.string().email(),
    age: z.number().int().positive(),
});

// 修改时要同步两个地方，容易不一致

// Best: 用 z.infer 派生类型
const UserSchema = z.object({
    name: z.string(),
    email: z.string().email(),
    age: z.number().int().positive(),
});

type User = z.infer<typeof UserSchema>;
// 修改 schema 后类型自动更新
```

### 2. 仅用 parse 而忽略 safeParse

```ts
// Bad: 使用 parse 直接抛异常
try {
    const data = UserSchema.parse(input);
    // 如果失败，需要 try-catch 捕获
} catch (err) {
    // err 是 ZodError，但不是所有调用方都记得处理
}

// Best: 使用 safeParse 返回联合类型
const result = UserSchema.safeParse(input);
if (!result.success) {
    // 类型安全地处理错误
    console.error(result.error.issues);
    // 返回 400 响应
    return;
}
// result.data 类型安全
processUser(result.data);
```

### 3. schema 校验成功后不再校验

```ts
// Bad: parse 后没有缩小类型
function process(input: unknown) {
    const data = UserSchema.parse(input);
    // data 类型是 User，但后续代码可能类型污染
}

// Best: parse 后立即赋值给新变量
function process(input: unknown) {
    const user = UserSchema.parse(input);
    // 后续使用 user 而非 input，避免混用
}
```

### 4. 在 Zod schema 中放入业务逻辑

```ts
// Bad: schema 中做复杂业务校验
const OrderSchema = z.object({
    userId: z.number(),
    amount: z.number(),
    balance: z.number(),
}).refine(data => data.amount <= data.balance, "余额不足");
// 但"余额不足"是业务逻辑，不应该在 schema 中

// Best: schema 只做数据形状和格式校验
const OrderSchema = z.object({
    userId: z.number(),
    amount: z.number().positive(),
});

// 业务逻辑单独处理
async function createOrder(input: unknown) {
    const order = OrderSchema.parse(input);
    const user = await getUser(order.userId);
    if (order.amount > user.balance) {
        throw new BusinessError("余额不足");
    }
    // 继续处理...
}
```

## Best Practice

### 1. 分层校验 —— 输入/输出分开

```ts
// Best: API 层统一校验输入和输出
// api/schemas.ts
import { z } from "zod";

// 请求 schema
export const CreateUserRequestSchema = z.object({
    name: z.string().min(2).max(50).transform(s => s.trim()),
    email: z.string().email().transform(e => e.toLowerCase()),
    password: z.string().min(8),
});

// 响应 schema —— 确保返回给前端的数据格式正确
export const CreateUserResponseSchema = z.object({
    id: z.number(),
    name: z.string(),
    email: z.string().email(),
    createdAt: z.date(),
});

// api/handler.ts
import { CreateUserRequestSchema, CreateUserResponseSchema } from "./schemas";

async function handleCreateUser(rawInput: unknown) {
    // 校验输入
    const input = CreateUserRequestSchema.parse(rawInput);

    // 业务处理
    const user = await db.users.create({
        name: input.name,
        email: input.email,
        password_hash: await hashPassword(input.password),
    });

    // 校验输出 —— 确保不会泄漏敏感字段
    return CreateUserResponseSchema.parse(user);
}
```

### 2. 利用 transform 清洗数据

```ts
// Best: 用 transform 做数据清洗
const CleanUserSchema = z.object({
    name: z.string()
        .min(1)
        .transform(s => s.trim())
        .transform(s => s.replace(/\s+/g, " ")), // 合并多余空格

    email: z.string()
        .email()
        .transform(e => e.toLowerCase().trim()),

    phone: z.string()
        .optional()
        .transform(p => p?.replace(/[\s-]/g, "")), // 移除空格和连字符

    tags: z.array(z.string())
        .max(5)
        .transform(tags => [...new Set(tags.map(t => t.toLowerCase()))]), // 去重转小写
});

// 使用: 解析后数据已经清洗完毕，可直接使用
const clean = CleanUserSchema.parse(rawUser);
```

### 3. 自定义错误消息

```ts
// Best: 中文错误消息配置
const UserFormSchema = z.object({
    name: z.string({
        required_error: "用户名是必填项",
        invalid_type_error: "用户名必须是字符串",
    })
    .min(2, "用户名至少 2 个字符")
    .max(50, "用户名最多 50 个字符"),

    age: z.number({
        required_error: "年龄是必填项",
    })
    .int("年龄必须是整数")
    .positive("年龄必须大于 0")
    .max(150, "年龄不能超过 150"),

    email: z.string().email("邮箱格式不正确"),
});

// 统一提取错误消息
function formatZodErrors(error: z.ZodError): Record<string, string> {
    const errors: Record<string, string> = {};
    for (const issue of error.issues) {
        const path = issue.path.join(".");
        if (!errors[path]) {
            errors[path] = issue.message;
        }
    }
    return errors;
}

const result = UserFormSchema.safeParse(input);
if (!result.success) {
    const errors = formatZodErrors(result.error);
    // { name: "用户名至少 2 个字符", email: "邮箱格式不正确" }
}
```

::: tip 总结

1. Zod 弥补了 TS 类型只在编译期存在的缺陷，提供运行时校验
2. 使用 `safeParse` 而非 `parse` 避免 try-catch 传播
3. 用 `z.infer<typeof Schema>` 自动派生类型，避免重复定义
4. `.transform()` 是数据清洗的利器，在解析阶段完成格式化
5. 前后端共享 schema 确保类型一致性（Go 无法原生实现）
6. schema 只做数据形状校验，业务逻辑不要混入

:::
