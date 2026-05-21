---
title: Dart JSON序列化完全指南（2024+）
date: 2026-05-20
footer: Trae编辑·AI创作
---

# Dart JSON序列化完全指南（2024+）

::: info 简介
本文详细介绍 Dart 现代化的 JSON 序列化生态，包括手动序列化、json_serializable、freezed、built_value 等方案，并提供最佳实践建议。
:::

## 1. JSON序列化概述

### 1.1 什么是JSON序列化

JSON序列化是将 Dart 对象转换为 JSON 字符串（序列化），以及将 JSON 字符串转换为 Dart 对象（反序列化）的过程。

### 1.2 Dart中的JSON方案对比

| 方案 | 类型 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|----------|
| **dart:convert** | 手动 | 零依赖、简单 | 样板代码多、类型不安全 | 小型项目/快速原型 |
| **json_serializable** | 代码生成 | 类型安全、灵活 | 需要配置 | 中型到大型项目 |
| **freezed** | 代码生成 | 不可变对象、联合类型 | 学习曲线较陡 | 需要不可变状态的项目 |
| **built_value** | 代码生成 | 强类型、高性能 | 配置复杂 | 大型企业级项目 |

## 2. 手动序列化（dart:convert）

### 2.1 基础用法

```dart
import 'dart:convert';

void main() {
  // JSON字符串转Map
  String jsonString = '{"name": "John", "age": 30}';
  Map<String, dynamic> jsonMap = jsonDecode(jsonString);
  print(jsonMap['name']); // John
  
  // Map转JSON字符串
  Map<String, dynamic> user = {'name': 'John', 'age': 30};
  String json = jsonEncode(user);
  print(json); // {"name":"John","age":30}
}
```

### 2.2 手动实现模型类

```dart
class User {
  final String name;
  final int age;
  final DateTime? createdAt;

  User({
    required this.name,
    required this.age,
    this.createdAt,
  });

  // 从JSON解析
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      name: json['name'] as String,
      age: json['age'] as int,
      createdAt: json['createdAt'] != null 
          ? DateTime.parse(json['createdAt'] as String) 
          : null,
    );
  }

  // 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'age': age,
      'createdAt': createdAt?.toIso8601String(),
    };
  }
}
```

### 2.3 处理嵌套对象

```dart
class Address {
  final String street;
  final String city;

  Address({required this.street, required this.city});

  factory Address.fromJson(Map<String, dynamic> json) {
    return Address(
      street: json['street'] as String,
      city: json['city'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {'street': street, 'city': city};
  }
}

class User {
  final String name;
  final Address address;

  User({required this.name, required this.address});

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      name: json['name'] as String,
      address: Address.fromJson(json['address'] as Map<String, dynamic>),
    );
  }

  Map<String, dynamic> toJson() {
    return {'name': name, 'address': address.toJson()};
  }
}
```

## 3. json_serializable方案

### 3.1 安装依赖

```yaml
dependencies:
  json_annotation: ^4.9.0

dev_dependencies:
  build_runner: ^2.4.0
  json_serializable: ^6.8.0
```

### 3.2 基本用法

```dart
import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final String name;
  final int age;
  final DateTime? createdAt;

  User({
    required this.name,
    required this.age,
    this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
```

### 3.3 运行代码生成

```bash
# 一次性生成
dart run build_runner build

# 开发时监听变化
dart run build_runner watch
```

### 3.4 JsonKey注解

`JsonKey` 注解用于精细控制字段的序列化行为，以下是所有可用参数的完整示例：

```dart
@JsonSerializable()
class User {
  // 1. name: JSON字段名映射
  @JsonKey(name: 'user_name') 
  final String name;

  // 2. defaultValue: 默认值（当JSON中无此字段或值为null时使用）
  @JsonKey(defaultValue: 18) 
  final int age;

  // 3. includeIfNull: 序列化时是否包含null值（默认true）
  @JsonKey(includeIfNull: false) 
  final String? email;

  // 4. disallowNullValue: 禁止null值，若为null则抛出DisallowedNullValueException
  @JsonKey(disallowNullValue: true) 
  final String username;

  // 5. fromJson/toJson: 自定义序列化/反序列化函数
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson) 
  final DateTime createdAt;

  // 6. includeFromJson: 是否参与反序列化（默认true）
  @JsonKey(includeFromJson: true) 
  final String? token;

  // 7. includeToJson: 是否参与序列化（默认true）
  @JsonKey(includeToJson: false) 
  final String? internalId;

  // 8. readValue: 自定义从JSON读取值的方式
  @JsonKey(readValue: _readNestedValue) 
  final String? nestedValue;

  // 9. required: 是否必需字段（默认false）
  @JsonKey(required: true) 
  final String id;

  // 10. unknownEnumValue: 枚举的未知值处理
  @JsonKey(unknownEnumValue: UserRole.user) 
  final UserRole role;

  // 11. ignore: 完全忽略此字段（已废弃，推荐使用includeFromJson/includeToJson）
  @JsonKey(ignore: true) 
  final int? tempData;

  User({
    required this.name,
    required this.age,
    this.email,
    required this.username,
    required this.createdAt,
    this.token,
    this.internalId,
    this.nestedValue,
    required this.id,
    required this.role,
    this.tempData,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}

// 自定义DateTime转换器
DateTime _dateTimeFromJson(String json) => DateTime.parse(json);
String _dateTimeToJson(DateTime date) => date.toIso8601String();

// 自定义嵌套值读取
String? _readNestedValue(Map json, String key) {
  return (json['nested'] as Map)[key] as String?;
}

// 枚举定义
enum UserRole { admin, user, guest }
```

#### JsonKey参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `String?` | null | JSON中的字段名，默认使用Dart字段名 |
| `defaultValue` | `Object?` | null | JSON中无此字段或值为null时使用的默认值 |
| `disallowNullValue` | `bool?` | null | 若为true，字段值为null时抛出异常 |
| `fromJson` | `Function?` | null | 自定义反序列化函数 |
| `toJson` | `Function?` | null | 自定义序列化函数 |
| `includeFromJson` | `bool?` | null | 是否参与反序列化（true=包含，false=排除） |
| `includeToJson` | `bool?` | null | 是否参与序列化（true=包含，false=排除） |
| `includeIfNull` | `bool?` | null | 序列化时是否包含null值（默认true） |
| `readValue` | `Function?` | null | 自定义从JSON读取值的方式 |
| `required` | `bool?` | null | 标记字段是否必需 |
| `unknownEnumValue` | `Enum?` | null | 枚举遇到未知值时使用的默认值 |
| `ignore` | `bool?` | null | 完全忽略此字段（已废弃） |

#### 常用场景示例

**场景1：处理嵌套JSON结构**

```dart
@JsonKey(readValue: _extractUserId)
final String userId;

String _extractUserId(Map json, String key) {
  return (json['user'] as Map)['id'] as String;
}
```

**场景2：处理服务器返回的时间戳**

```dart
@JsonKey(fromJson: _timestampToDateTime, toJson: _dateTimeToTimestamp)
final DateTime createdAt;

DateTime _timestampToDateTime(int timestamp) {
  return DateTime.fromMillisecondsSinceEpoch(timestamp);
}

int _dateTimeToTimestamp(DateTime date) {
  return date.millisecondsSinceEpoch;
}
```

**场景3：处理枚举类型**

```dart
enum Status { active, inactive, suspended }

@JsonKey(
  fromJson: _statusFromJson, 
  toJson: _statusToJson,
  unknownEnumValue: Status.inactive,
)
final Status status;

Status _statusFromJson(String json) {
  return Status.values.firstWhere(
    (e) => e.name.toLowerCase() == json.toLowerCase(),
    orElse: () => Status.inactive,
  );
}

String _statusToJson(Status status) => status.name.toLowerCase();
```

**场景4：排除敏感字段**

```dart
@JsonKey(includeToJson: false) // 序列化时排除
final String? password;

@JsonKey(includeFromJson: false) // 反序列化时排除
final String? serverSideData;
```

### 3.5 生成的代码示例

```dart
// user.g.dart (自动生成)
part of 'user.dart';

User _$UserFromJson(Map<String, dynamic> json) => User(
      name: json['user_name'] as String,
      age: json['age'] as int? ?? 18,
      email: json['email'] as String?,
      createdAt: _dateTimeFromJson(json['createdAt'] as String),
    );

Map<String, dynamic> _$UserToJson(User instance) => <String, dynamic>{
      'user_name': instance.name,
      'age': instance.age,
      if (instance.email != null) 'email': instance.email,
      'createdAt': _dateTimeToJson(instance.createdAt),
    };
```

### 3.6 配置build.yaml

```yaml
targets:
  $default:
    builders:
      json_serializable:
        options:
          # 生成JSON Schema
          create_json_schema: true
          # 字段名风格 (snake_case, kebab_case, pascal_case)
          field_rename: snake_case
          # 是否生成fromJson/toJson
          generate_from_json_when_null: false
```

## 4. freezed方案

### 4.1 安装依赖

```yaml
dependencies:
  freezed_annotation: ^2.4.0
  json_annotation: ^4.9.0

dev_dependencies:
  build_runner: ^2.4.0
  freezed: ^2.4.0
  json_serializable: ^6.8.0
```

### 4.2 基本用法

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

@freezed
class User with _$User {
  const factory User({
    required String name,
    required int age,
    String? email,
    @JsonKey(name: 'created_at') DateTime? createdAt,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
```

### 4.3 copyWith方法

```dart
final user = User(name: 'John', age: 30);

// 使用copyWith创建修改后的副本
final updatedUser = user.copyWith(
  name: 'Jane',
  age: 28,
);

// 原对象不变
print(user.name);      // John
print(updatedUser.name); // Jane
```

### 4.4 默认值 @Default

```dart
@freezed
class User with _$User {
  const factory User({
    required String name,
    @Default(18) int age,
    @Default([]) List<String> tags,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

// 使用时可以省略带默认值的字段
final user = User(name: 'John');
print(user.age);  // 18
print(user.tags);  // []
```

### 4.5 联合类型 (Union/Sealed Class)

```dart
@freezed
sealed class Result<T> with _$Result<T> {
  const factory Result.success(T data) = Success<T>;
  const factory Result.error(String message) = Error<T>;
  const factory Result.loading() = Loading<T>;
}

// 使用
Result<String> result = const Result.loading();

result.when(
  success: (data) => print('Success: $data'),
  error: (message) => print('Error: $message'),
  loading: () => print('Loading...'),
);
```

### 4.6 自定义方法和getter

```dart
@freezed
class User with _$User {
  const User._(); // 私有构造函数

  const factory User({
    required String firstName,
    required String lastName,
    required int age,
  }) = _User;

  // 自定义getter
  String get fullName => '$firstName $lastName';

  // 自定义方法
  bool get isAdult => age >= 18;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
```

## 5. built_value方案

### 5.1 安装依赖

```yaml
dependencies:
  built_value: ^8.8.0
  built_collection: ^5.1.1

dev_dependencies:
  build_runner: ^2.4.0
  built_value_generator: ^8.8.0
```

### 5.2 基本用法

```dart
import 'package:built_value/built_value.dart';
import 'package:built_value/serializer.dart';

part 'user.g.dart';

abstract class User implements Built<User, UserBuilder> {
  String get name;
  int get age;
  String? get email;
  DateTime? get createdAt;

  User._();
  factory User([void Function(UserBuilder) updates]) = _$User;

  static Serializer<User> get serializer => _$userSerializer;
}
```

### 5.3 序列化配置

```dart
import 'package:built_value/serializer.dart';

part 'serializers.g.dart';

@SerializersFor([
  User,
])
final Serializers serializers = _$serializers;

// 使用
final user = User((b) => b
  ..name = 'John'
  ..age = 30
);

// 序列化
String json = jsonEncode(serializers.serialize(user));

// 反序列化
User user = serializers.deserialize(jsonDecode(json)) as User;
```

### 5.4 自定义序列化器

```dart
import 'package:built_value/serializer.dart';

class CustomDateTimeSerializer implements PrimitiveSerializer<DateTime> {
  @override
  DateTime deserialize(Serializers serializers, Object? serialized, {FullType specifiedType = FullType.unspecified}) {
    return DateTime.parse(serialized as String);
  }

  @override
  Object serialize(Serializers serializers, DateTime object, {FullType specifiedType = FullType.unspecified}) {
    return object.toIso8601String();
  }

  @override
  Iterable<Type> get types => [DateTime];

  @override
  String get wireName => 'DateTime';
}
```

## 6. 自定义转换器

### 6.1 JsonConverter（json_serializable）

```dart
class DateTimeConverter implements JsonConverter<DateTime, String> {
  const DateTimeConverter();

  @override
  DateTime fromJson(String json) => DateTime.parse(json);

  @override
  String toJson(DateTime object) => object.toIso8601String();
}

@JsonSerializable()
class User {
  @DateTimeConverter()
  final DateTime createdAt;

  User({required this.createdAt});

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
```

### 6.2 JsonKey自定义转换

```dart
enum UserRole { admin, user, guest }

UserRole _roleFromJson(String json) {
  return UserRole.values.firstWhere(
    (e) => e.name.toLowerCase() == json.toLowerCase(),
    orElse: () => UserRole.user,
  );
}

String _roleToJson(UserRole role) => role.name.toLowerCase();

@JsonSerializable()
class User {
  @JsonKey(fromJson: _roleFromJson, toJson: _roleToJson)
  final UserRole role;

  User({required this.role});

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
```

## 7. 处理多态JSON

### 7.1 使用freezed处理多态

```dart
@freezed
sealed class Shape with _$Shape {
  const factory Shape.circle({required double radius}) = Circle;
  const factory Shape.rectangle({required double width, required double height}) = Rectangle;
  const factory Shape.triangle({required double base, required double height}) = Triangle;

  factory Shape.fromJson(Map<String, dynamic> json) {
    final type = json['type'] as String;
    switch (type) {
      case 'circle':
        return Circle.fromJson(json);
      case 'rectangle':
        return Rectangle.fromJson(json);
      case 'triangle':
        return Triangle.fromJson(json);
      default:
        throw Exception('Unknown shape type: $type');
    }
  }
}
```

### 7.2 使用@freezed的union功能

```dart
@freezed
class Shape with _$Shape {
  const factory Shape.circle({required double radius}) = Circle;
  const factory Shape.rectangle({required double width, required double height}) = Rectangle;
  const factory Shape.triangle({required double base, required double height}) = Triangle;

  factory Shape.fromJson(Map<String, dynamic> json) => _$ShapeFromJson(json);
}

// 配置build.yaml添加类型鉴别器
targets:
  $default:
    builders:
      json_serializable:
        options:
          discriminator: type
```

## 8. 性能优化

### 8.1 使用compute隔离解析

```dart
import 'dart:async';
import 'dart:convert';

Future<User> parseUser(String jsonString) async {
  return await compute(_parseUser, jsonString);
}

User _parseUser(String jsonString) {
  final jsonMap = jsonDecode(jsonString) as Map<String, dynamic>;
  return User.fromJson(jsonMap);
}
```

### 8.2 缓存解析结果

```dart
final _cache = <String, User>{};

Future<User> getUser(String id) async {
  if (_cache.containsKey(id)) {
    return _cache[id]!;
  }
  
  final response = await http.get(Uri.parse('https://api.example.com/users/$id'));
  final user = User.fromJson(jsonDecode(response.body));
  _cache[id] = user;
  return user;
}
```

### 8.3 使用lazy_static缓存Serializer

```dart
import 'package:built_value/serializer.dart';
import 'package:lazy_static/lazy_static.dart';

part 'serializers.g.dart';

lazy static final Serializers serializers = _$serializers;
```

## 9. 测试策略

### 9.1 测试序列化和反序列化

```dart
void main() {
  test('User serialization round trip', () {
    final user = User(
      name: 'John',
      age: 30,
      createdAt: DateTime(2024, 1, 1),
    );

    // 序列化
    final json = user.toJson();
    
    // 反序列化
    final restoredUser = User.fromJson(json);

    // 验证
    expect(restoredUser.name, equals(user.name));
    expect(restoredUser.age, equals(user.age));
    expect(restoredUser.createdAt, equals(user.createdAt));
  });

  test('User.fromJson handles missing optional fields', () {
    final json = {'name': 'John', 'age': 30};
    final user = User.fromJson(json);
    
    expect(user.name, equals('John'));
    expect(user.email, isNull);
  });
}
```

### 9.2 测试边缘情况

```dart
test('User.fromJson handles null values', () {
  final json = {
    'name': null,
    'age': null,
    'createdAt': 'invalid-date',
  };
  
  expect(() => User.fromJson(json), throwsA(isA<FormatException>()));
});
```

## 10. 最佳实践

### 10.1 选择合适的方案

```
小型项目 / 快速原型
    ↓
dart:convert (手动序列化)

中型项目 / 需要类型安全
    ↓
json_serializable

需要不可变状态 / 复杂状态管理
    ↓
freezed

大型企业级项目 / 需要高性能
    ↓
built_value
```

### 10.2 使用final和const

```dart
// 推荐
@freezed
class User with _$User {
  const factory User({
    required final String name,
    required final int age,
  }) = _User;
}

// 避免：可变字段
class User {
  String name; // 可变字段，不推荐
  int age;
  
  User({required this.name, required this.age});
}
```

### 10.3 处理DateTime

```dart
// 推荐：使用ISO8601格式
@JsonKey(name: 'created_at')
final DateTime? createdAt;

// 序列化
createdAt?.toIso8601String()

// 反序列化
DateTime.parse(json['created_at'])
```

### 10.4 使用枚举时提供默认值

```dart
enum UserRole { admin, user, guest }

UserRole _roleFromJson(String json) {
  return UserRole.values.firstWhere(
    (e) => e.name.toLowerCase() == json.toLowerCase(),
    orElse: () => UserRole.user, // 提供默认值
  );
}
```

### 10.5 组织模型文件

```
lib/
├── models/
│   ├── user.dart
│   ├── post.dart
│   ├── comment.dart
│   └── serializers.dart
```

### 10.6 使用build.yaml统一配置

```yaml
targets:
  $default:
    builders:
      json_serializable:
        options:
          field_rename: snake_case
          create_json_schema: true
          generate_from_json_when_null: false
```

## 11. 常见问题

### 11.1 代码生成失败

**问题**：运行build_runner时出现错误

**解决方案**：
```bash
# 清理缓存
dart run build_runner clean

# 重新生成（删除冲突文件）
dart run build_runner build --delete-conflicting-outputs
```

### 11.2 DateTime解析失败

**问题**：JSON中的日期格式不兼容

**解决方案**：使用自定义转换器

```dart
@JsonKey(fromJson: _parseDateTime)
final DateTime createdAt;

DateTime _parseDateTime(dynamic json) {
  if (json is String) {
    return DateTime.parse(json);
  }
  return DateTime.fromMillisecondsSinceEpoch(json as int);
}
```

### 11.3 字段名不匹配

**问题**：JSON字段名与Dart字段名不同

**解决方案**：使用@JsonKey注解

```dart
@JsonKey(name: 'user_name')
final String name;
```

### 11.4 空安全问题

**问题**：JSON字段可能为null但Dart字段是非空的

**解决方案**：

```dart
@JsonSerializable()
class User {
  // 使用required确保非空
  @JsonKey(defaultValue: '')
  final String name;

  User({required this.name});
}
```

## 12. 总结

| 方案 | 推荐场景 | 特点 |
|------|----------|------|
| **dart:convert** | 小型项目 | 简单、零依赖 |
| **json_serializable** | 中型项目 | 类型安全、灵活 |
| **freezed** | 需要不可变状态 | 联合类型、copyWith |
| **built_value** | 大型项目 | 高性能、强类型 |

### 推荐学习路径

1. **基础**：掌握 `dart:convert` 的 `jsonEncode/jsonDecode`
2. **进阶**：学习 `json_serializable` 进行类型安全的序列化
3. **高级**：掌握 `freezed` 处理不可变状态和联合类型
4. **专业**：了解 `built_value` 用于高性能场景

### 关键要点

- **类型安全**：使用代码生成方案避免运行时错误
- **不可变性**：优先使用不可变对象（freezed/built_value）
- **测试**：测试序列化往返转换确保正确性
- **性能**：大型JSON使用compute隔离解析
- **文档**：使用JSON Schema生成API文档
