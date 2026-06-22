# API 文档
## 配置
- host: `localhost`
- port: `8000`

## 通用DTO
### 响应DTO
- `code`: 返回码, 0表示成功, 其他表示失败
- `message`: 提示信息, 用于描述操作结果或错误信息
- `data`: `Object`类型, 包含返回的数据

- 后端大部分API都有中间件`group.Middleware(ghttp.MiddlewareHandlerResponse)`, 除了登录链路这种需要直接操作`*ghttp.Request`的API外, 其他API都通过这个中间件来封装响应内容(在`data`的基础上封装`code`和`message`)
- GoFrame后端API只要路由正确, 无论请求是否处理成功, 其HTTP响应码都为200
    - 请求路径出错时会返回404错误
    - 后端报错时则会返回500错误

## v1 API `/v1`
### 登录链路 `/auth`
#### 登录 `/login` | 完整路径(下同) `POST /v1/auth/login`
##### 请求DTO
```go
type LoginReq struct {
	g.Meta `method:"post" path:"/auth/login" tags:"Authorization" summary:"用户登录"`

	Username string `json:"username" form:"username" v:"length:3,24" dc:"用户名(可选)"`
	Email    string `json:"email" form:"email" dc:"邮箱 (可选)"`
	Password string `json:"password" form:"password" v:"required|ci|password2" dc:"密码(必填)"`
}
```
```json
{
	"username": "user123",
	"email": "user@example.com",
	"password": "123456abcABC"
}
```
- `username`: 用户名, 必填, 长度为3-24个字符
- `email`: 邮箱, 必填, 格式为 `username@example.com`
- `password`: 密码, 必填, 长度至多24个字符, 包含大小写字母、数字(`password2`), 大小写敏感(`ci`)

##### 响应DTO
```go
type LoginRes struct {
	Code    int    `json:"code" dc:"返回码"`
	Message string `json:"message" dc:"告知登录是否成功"`
}
```
```json
{
	"code": 0,
	"message": "登录成功"
}
```

##### 响应类型 (示例)
###### 后端数据库没开导致查表失败
```json
{
	"code": 61,
	"message": "无法登录, 请联系管理员"
}
```
- code: 61 -> gcode.CodeInternalError

###### 用户名/邮箱/密码 未通过参数校验
```json
{
	"code": 53,
	"message": "The username value `xxx` length must be between 3 and 24"
}
```
- code: 53 -> gcode.CodeInvalidRequest
- `xxx` -> 输入的用户名

###### 登录成功
```json
{
	"code": 0,
	"message": "登录成功"
}
```
- 后端通过`SetCookie`设置含有JWT的token
- 后端已开启`httpOnly`, 有效期为5分钟, JWT有效期也是5分钟, Cookie键名为`Authorization`
```yaml
server:
  # 略
  argon: # Argon2配置
    # 略
  cookie: # Cookie配置
    key: "authorization"
    domain: ""
    path: "/"
    # 86400秒 = 1天; 3600秒 = 1小时; 60秒 = 1分钟
    max_age: 300
    http_only: true # 仅通过HTTP访问，不允许通过JavaScript访问
    # jwt配置
    jwt_secret: # 略
    jwt_signing_method: "HS256"
```
###### 密码错误
```json
{
	"code": 61,
	"message": "密码错误"
}
```

###### 用户不存在
```json
{
	"code": 0,
	"message": "无法登录, 请联系管理员"
}
```
- WARNING: 这个响应分支可能会间接泄露用户信息
- 虽然Code为0, 但不会设置Cookie

#### 注册 `/register` | 完整路径 `POST /v1/user/register`
##### 请求DTO
```go
type CreateReq struct {
	g.Meta   `path:"/user" method:"post" tags:"User" summary:"Create user"`
	Username string `v:"required|length:3,24" json:"username" dc:"username"` // 3~24位长的用户名
	// Password
	//
	// ci: 默认严格区分大小写
	// password2: 二级密码强度, 需要包含大小写字母和数字
	Password string `v:"required|ci|password2" json:"password" dc:"midium password, required alphabets and digits"`
	Email    string `v:"required|email" json:"email" dc:"email"`
}
```
```json
{
	"username": "user123",
	"password": "123456abcABC",
	"email": "user@example.com"
}
```

##### 响应DTO
```go
type CreateRes struct {
	Id int64 `json:"id" dc:"user id"`
}
```
```json
{
	"code": 0,
	"message": "OK",
	"data": {
		"id": 8
	}
}
```
- 返回的Id是用户在`Employee`表中的主键ID, 仅作调试, 后面会删掉
- 这个API的中间件是`group.Middleware(ghttp.MiddlewareHandlerResponse)`, 会把API的响应包裹在:
```json
{
	"code": 123456,
	"message": "xxx",
	"data": {
		// API本身返回的数据
	}
}
```

##### 响应类型
###### 数据库没开导致查表失败
```json
{
	"code": 52,
	"message": "BEGIN: dial tcp 127.0.0.1:5432: connectex: No connection could be made because the target machine actively refused it.",
	"data": {
		"id": 0
	}
}
```
- WARNING: 这个响应分支会泄露后端基础设施信息
- ~~用户已知悉, 会自行修改~~

###### 注册成功
```json
{
	"code": 0,
	"message": "OK",
	"data": {
		"id": 123456
	}
}
```
###### 参数未通过校验
```json
{
	"code": 51,
	"message": "The username value `ab` length must be between 3 and 24",
	"data": null
}
```

#### 登出 `/logout` | 完整路径 `GET /v1/auth/logout`
##### 请求DTO
- 无, 不论用户是否携带Cookie, 访问这个API都会被`Remove` Cookie

---

## TODO: 待实现API

### 1. 用户管理 `/user`

#### 1.1 获取当前用户信息 `GET /v1/user/me`
##### 请求DTO
- 无, 需要携带Cookie

##### 响应DTO
**Go后端**:
```go
type GetUserRes struct {
    Id       int64  `json:"id" dc:"用户ID"`
    Username string `json:"username" dc:"用户名"`
    Email    string `json:"email" dc:"邮箱"`
}
```

**Dart前端**:
```dart
part 'user.g.dart';

@JsonSerializable()
class UserInfoResponse {
  final int id;
  @JsonKey(name: 'username')
  final String username;
  @JsonKey(name: 'email')
  final String email;

  UserInfoResponse({
    required this.id,
    required this.username,
    required this.email,
  });

  factory UserInfoResponse.fromJson(Map<String, dynamic> json) => 
      _$UserInfoResponseFromJson(json);
  Map<String, dynamic> toJson() => _$UserInfoResponseToJson(this);
}
```

##### 成功响应示例
```json
{
    "code": 0,
    "message": "OK",
    "data": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com"
    }
}
```

---

### 2. 份额管理 `/share`

#### 2.1 获取份额列表 `GET /v1/share/list`
##### 请求DTO
**Go后端**:
```go
type GetShareListReq struct {
    Page int `json:"page" form:"page" dc:"页码(从1开始)"`
    Size int `json:"size" form:"size" dc:"每页数量"`
}
```

**Dart前端**:
```dart
class GetShareListRequest {
  final int page;
  @JsonKey(name: 'size')
  final int pageSize;

  GetShareListRequest({
    this.page = 1,
    this.pageSize = 10,
  });

  Map<String, dynamic> toJson() {
    return {
      'page': page,
      'size': pageSize,
    };
  }
}
```

##### 响应DTO
**Go后端**:
```go
type Share struct {
    Id        int64     `json:"id" dc:"份额ID"`
    UserId    int64     `json:"user_id" dc:"用户ID"`
    Value     string    `json:"value" dc:"份额值(Base64)"`
    Version   int       `json:"version" dc:"版本号"`
    CreatedAt time.Time `json:"created_at" dc:"创建时间"`
}

type GetShareListRes struct {
    List  []Share `json:"list" dc:"份额列表"`
    Total int64   `json:"total" dc:"总数"`
}
```

**Dart前端**:
```dart
part 'share.g.dart';

@JsonSerializable()
class ShareItem {
  final int id;
  @JsonKey(name: 'user_id')
  final int userId;
  @JsonKey(name: 'value')
  final String value;
  @JsonKey(name: 'version')
  final int version;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  ShareItem({
    required this.id,
    required this.userId,
    required this.value,
    required this.version,
    required this.createdAt,
  });

  factory ShareItem.fromJson(Map<String, dynamic> json) => 
      _$ShareItemFromJson(json);
  Map<String, dynamic> toJson() => _$ShareItemToJson(this);
}

@JsonSerializable()
class GetShareListResponse {
  @JsonKey(name: 'list')
  final List<ShareItem> shares;
  @JsonKey(name: 'total')
  final int total;

  GetShareListResponse({
    required this.shares,
    required this.total,
  });

  factory GetShareListResponse.fromJson(Map<String, dynamic> json) => 
      _$GetShareListResponseFromJson(json);
}
```

---

#### 2.2 提交份额 `POST /v1/share/submit`
##### 请求DTO
**Go后端**:
```go
type SubmitShareReq struct {
    TaskId int64  `json:"task_id" v:"required" dc:"任务ID"`
    Value  string `json:"value" v:"required" dc:"份额值(Base64)"`
}
```

**Dart前端**:
```dart
class SubmitShareRequest {
  @JsonKey(name: 'task_id')
  final int taskId;
  @JsonKey(name: 'value')
  final String value;

  SubmitShareRequest({
    required this.taskId,
    required this.value,
  });

  Map<String, dynamic> toJson() {
    return {
      'task_id': taskId,
      'value': value,
    };
  }
}
```

##### 响应DTO
**Go后端**:
```go
type SubmitShareRes struct {
    Success bool `json:"success" dc:"是否成功"`
}
```

**Dart前端**:
```dart
part 'submit_share.g.dart';

@JsonSerializable()
class SubmitShareResponse {
  @JsonKey(name: 'success')
  final bool success;

  SubmitShareResponse({required this.success});

  factory SubmitShareResponse.fromJson(Map<String, dynamic> json) => 
      _$SubmitShareResponseFromJson(json);
}
```

---

### 3. 审计条目 `/item`

#### 3.1 获取审计条目列表 `GET /v1/item/list`
##### 请求DTO
**Go后端**:
```go
type GetItemListReq struct {
    Page int    `json:"page" form:"page" dc:"页码"`
    Size int    `json:"size" form:"size" dc:"每页数量"`
    Status string `json:"status" form:"status" dc:"状态筛选(可选)"`
}
```

**Dart前端**:
```dart
class GetItemListRequest {
  final int page;
  @JsonKey(name: 'size')
  final int pageSize;
  @JsonKey(name: 'status')
  final String? status;

  GetItemListRequest({
    this.page = 1,
    this.pageSize = 10,
    this.status,
  });

  Map<String, dynamic> toJson() {
    return {
      'page': page,
      'size': pageSize,
      if (status != null) 'status': status,
    };
  }
}
```

##### 响应DTO
**Go后端**:
```go
type AuditItem struct {
    Id        int64     `json:"id" dc:"条目ID"`
    Title     string    `json:"title" dc:"标题"`
    Status    string    `json:"status" dc:"状态(encrypted/decrypted/pending)"`
    CreatedAt time.Time `json:"created_at" dc:"创建时间"`
    UpdatedAt time.Time `json:"updated_at" dc:"更新时间"`
}

type GetItemListRes struct {
    List  []AuditItem `json:"list" dc:"条目列表"`
    Total int64       `json:"total" dc:"总数"`
}
```

**Dart前端**:
```dart
part 'audit_item.g.dart';

@JsonSerializable()
class AuditItem {
  final int id;
  @JsonKey(name: 'title')
  final String title;
  @JsonKey(name: 'status')
  final String status;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  AuditItem({
    required this.id,
    required this.title,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
  });

  factory AuditItem.fromJson(Map<String, dynamic> json) => 
      _$AuditItemFromJson(json);
  Map<String, dynamic> toJson() => _$AuditItemToJson(this);

  String get statusText {
    switch (status) {
      case 'encrypted': return '已加密';
      case 'decrypted': return '已解密';
      case 'pending': return '待处理';
      default: return status;
    }
  }
}

@JsonSerializable()
class GetItemListResponse {
  @JsonKey(name: 'list')
  final List<AuditItem> items;
  @JsonKey(name: 'total')
  final int total;

  GetItemListResponse({
    required this.items,
    required this.total,
  });

  factory GetItemListResponse.fromJson(Map<String, dynamic> json) => 
      _$GetItemListResponseFromJson(json);
}
```

---

#### 3.2 创建审计条目 `POST /v1/item`
##### 请求DTO
**Go后端**:
```go
type CreateItemReq struct {
    Title       string `json:"title" v:"required|length:1,255" dc:"标题"`
    Description string `json:"description" dc:"描述(可选)"`
}
```

**Dart前端**:
```dart
class CreateItemRequest {
  @JsonKey(name: 'title')
  final String title;
  @JsonKey(name: 'description')
  final String? description;

  CreateItemRequest({
    required this.title,
    this.description,
  });

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      if (description != null) 'description': description,
    };
  }
}
```

##### 响应DTO
**Go后端**:
```go
type CreateItemRes struct {
    Id int64 `json:"id" dc:"条目ID"`
}
```

**Dart前端**:
```dart
part 'create_item.g.dart';

@JsonSerializable()
class CreateItemResponse {
  final int id;

  CreateItemResponse({required this.id});

  factory CreateItemResponse.fromJson(Map<String, dynamic> json) => 
      _$CreateItemResponseFromJson(json);
}
```

---

#### 3.3 获取审计条目详情 `GET /v1/item/{id}`
##### 请求DTO
- 路径参数: `id` - 条目ID

##### 响应DTO
**Go后端**:
```go
type GetItemDetailRes struct {
    Id          int64     `json:"id" dc:"条目ID"`
    Title       string    `json:"title" dc:"标题"`
    Description string    `json:"description" dc:"描述"`
    Status      string    `json:"status" dc:"状态"`
    CreatedAt   time.Time `json:"created_at" dc:"创建时间"`
    UpdatedAt   time.Time `json:"updated_at" dc:"更新时间"`
}
```

**Dart前端**:
```dart
part 'get_item_detail.g.dart';

@JsonSerializable()
class GetItemDetailResponse {
  final int id;
  @JsonKey(name: 'title')
  final String title;
  @JsonKey(name: 'description')
  final String description;
  @JsonKey(name: 'status')
  final String status;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  GetItemDetailResponse({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
  });

  factory GetItemDetailResponse.fromJson(Map<String, dynamic> json) => 
      _$GetItemDetailResponseFromJson(json);
}
```

---

#### 3.4 加密审计条目 `POST /v1/item/{id}/encrypt`
##### 请求DTO
**Go后端**:
```go
type EncryptItemReq struct {
    ItemId int64  `json:"item_id" v:"required" dc:"条目ID"`
    KeyId  int64  `json:"key_id" v:"required" dc:"密钥ID"`
}
```

**Dart前端**:
```dart
class EncryptItemRequest {
  @JsonKey(name: 'item_id')
  final int itemId;
  @JsonKey(name: 'key_id')
  final int keyId;

  EncryptItemRequest({
    required this.itemId,
    required this.keyId,
  });

  Map<String, dynamic> toJson() {
    return {
      'item_id': itemId,
      'key_id': keyId,
    };
  }
}
```

---

### 4. 任务协调 `/task`

#### 4.1 创建份额收集任务 `POST /v1/task/share/init`
##### 请求DTO
**Go后端**:
```go
type InitShareTaskReq struct {
    ItemId    int64 `json:"item_id" v:"required" dc:"条目ID"`
    Threshold int   `json:"threshold" v:"required|min:2" dc:"阈值(需要的份额数量)"`
}
```

**Dart前端**:
```dart
class InitShareTaskRequest {
  @JsonKey(name: 'item_id')
  final int itemId;
  @JsonKey(name: 'threshold')
  final int threshold;

  InitShareTaskRequest({
    required this.itemId,
    required this.threshold,
  });

  Map<String, dynamic> toJson() {
    return {
      'item_id': itemId,
      'threshold': threshold,
    };
  }
}
```

##### 响应DTO
**Go后端**:
```go
type InitShareTaskRes struct {
    TaskId int64 `json:"task_id" dc:"任务ID"`
}
```

**Dart前端**:
```dart
part 'init_share_task.g.dart';

@JsonSerializable()
class InitShareTaskResponse {
  @JsonKey(name: 'task_id')
  final int taskId;

  InitShareTaskResponse({required this.taskId});

  factory InitShareTaskResponse.fromJson(Map<String, dynamic> json) => 
      _$InitShareTaskResponseFromJson(json);
}
```

---

#### 4.2 获取任务状态 `GET /v1/task/{taskId}/status`
##### 请求DTO
- 路径参数: `taskId` - 任务ID

##### 响应DTO
**Go后端**:
```go
type GetTaskStatusRes struct {
    TaskId      int64     `json:"task_id" dc:"任务ID"`
    Status      string    `json:"status" dc:"状态(waiting/ready/completed/failed)"`
    Threshold   int       `json:"threshold" dc:"阈值"`
    Collected   int       `json:"collected" dc:"已收集份额数"`
    CreatedAt   time.Time `json:"created_at" dc:"创建时间"`
    UpdatedAt   time.Time `json:"updated_at" dc:"更新时间"`
}
```

**Dart前端**:
```dart
part 'get_task_status.g.dart';

@JsonSerializable()
class GetTaskStatusResponse {
  @JsonKey(name: 'task_id')
  final int taskId;
  @JsonKey(name: 'status')
  final String status;
  @JsonKey(name: 'threshold')
  final int threshold;
  @JsonKey(name: 'collected')
  final int collected;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  GetTaskStatusResponse({
    required this.taskId,
    required this.status,
    required this.threshold,
    required this.collected,
    required this.createdAt,
    required this.updatedAt,
  });

  factory GetTaskStatusResponse.fromJson(Map<String, dynamic> json) => 
      _$GetTaskStatusResponseFromJson(json);

  double get progress => threshold > 0 ? collected / threshold : 0;
}
```

---

### 5. 扰动更新 `/delta`

#### 5.1 生成扰动向量 `POST /v1/delta/generate`
##### 请求DTO
**Go后端**:
```go
type GenerateDeltaReq struct {
    ItemId int64 `json:"item_id" v:"required" dc:"条目ID"`
}
```

**Dart前端**:
```dart
class GenerateDeltaRequest {
  @JsonKey(name: 'item_id')
  final int itemId;

  GenerateDeltaRequest({required this.itemId});

  Map<String, dynamic> toJson() {
    return {'item_id': itemId};
  }
}
```

##### 响应DTO
**Go后端**:
```go
type DeltaVector struct {
    UserId int64  `json:"user_id" dc:"用户ID"`
    Value  uint32 `json:"value" dc:"扰动值"`
}

type GenerateDeltaRes struct {
    DeltaId  int64        `json:"delta_id" dc:"扰动ID"`
    Version  int          `json:"version" dc:"新版本号"`
    Deltas   []DeltaVector `json:"deltas" dc:"扰动向量列表"`
}
```

**Dart前端**:
```dart
part 'delta.g.dart';

@JsonSerializable()
class DeltaVector {
  @JsonKey(name: 'user_id')
  final int userId;
  @JsonKey(name: 'value')
  final int value;

  DeltaVector({
    required this.userId,
    required this.value,
  });

  factory DeltaVector.fromJson(Map<String, dynamic> json) => 
      _$DeltaVectorFromJson(json);
  Map<String, dynamic> toJson() => _$DeltaVectorToJson(this);
}

@JsonSerializable()
class GenerateDeltaResponse {
  @JsonKey(name: 'delta_id')
  final int deltaId;
  @JsonKey(name: 'version')
  final int version;
  @JsonKey(name: 'deltas')
  final List<DeltaVector> deltas;

  GenerateDeltaResponse({
    required this.deltaId,
    required this.version,
    required this.deltas,
  });

  factory GenerateDeltaResponse.fromJson(Map<String, dynamic> json) => 
      _$GenerateDeltaResponseFromJson(json);
}
```

---

## Dart通用响应封装

```dart
part 'api_response.g.dart';

@JsonSerializable(genericArgumentFactories: true)
class ApiResponse<T> {
  @JsonKey(name: 'code')
  final int code;
  @JsonKey(name: 'message')
  final String message;
  @JsonKey(name: 'data')
  final T? data;

  ApiResponse({
    required this.code,
    required this.message,
    this.data,
  });

  factory ApiResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Object?) fromJsonT,
  ) =>
      _$ApiResponseFromJson(json, fromJsonT);

  Map<String, dynamic> toJson(Object Function(T?) toJsonT) => 
      _$ApiResponseToJson(this, toJsonT);

  bool get isSuccess => code == 0;
}
```

---

## API汇总表

| API路径 | HTTP方法 | 功能 | 认证 | 状态 |
|---------|----------|------|------|------|
| `/v1/auth/login` | POST | 用户登录 | 无需 | ✅ 已实现 |
| `/v1/user/register` | POST | 用户注册 | 无需 | ✅ 已实现 |
| `/v1/auth/logout` | GET | 用户登出 | Cookie | ✅ 已实现 |
| `/v1/user/me` | GET | 获取当前用户信息 | Cookie | TODO |
| `/v1/share/list` | GET | 获取份额列表 | Cookie | TODO |
| `/v1/share/submit` | POST | 提交份额 | Cookie | TODO |
| `/v1/item/list` | GET | 获取审计条目列表 | Cookie | TODO |
| `/v1/item` | POST | 创建审计条目 | Cookie | TODO |
| `/v1/item/{id}` | GET | 获取条目详情 | Cookie | TODO |
| `/v1/item/{id}/encrypt` | POST | 加密审计条目 | Cookie | TODO |
| `/v1/task/share/init` | POST | 初始化份额收集任务 | Cookie | TODO |
| `/v1/task/{taskId}/status` | GET | 获取任务状态 | Cookie | TODO |
| `/v1/delta/generate` | POST | 生成扰动向量 | Cookie | TODO |