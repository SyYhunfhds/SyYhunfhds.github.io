---
title: 从零开始的RPC（三）：还在Protobuf
date: 2026-01-30
---
[[toc]]
***
## Protocol（三）：endless...
### 可数值类型 （Scalar Value Types）
> A scalar message field can have one of the following types – the table shows the type specified in the `.proto` file, and the corresponding type in the automatically generated class:

| Proto Type | Notes                                                                                                                                           |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| double     | Uses [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754) double-precision format.                                                                |
| float      | Uses [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754) single-precision format.                                                                |
| int32      | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint32 instead. |
| int64      | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint64 instead. |
| uint32     | Uses variable-length encoding.                                                                                                                  |
| uint64     | Uses variable-length encoding.                                                                                                                  |
| sint32     | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int32s.                            |
| sint64     | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int64s.                            |
| fixed32    | Always four bytes. More efficient than uint32 if values are often greater than 228.                                                             |
| fixed64    | Always eight bytes. More efficient than uint64 if values are often greater than 256.                                                            |
| sfixed32   | Always four bytes.                                                                                                                              |
| sfixed64   | Always eight bytes.                                                                                                                             |
| bool       |                                                                                                                                                 |
| string     | A string must always contain UTF-8 encoded or 7-bit ASCII text, and cannot be longer than 232.                                                  |
| bytes      | May contain any arbitrary sequence of bytes no longer than 232.                                                                                 |


| Proto Type | C++ Type    | Java/Kotlin Type[1] | Python Type[3]                   | Go Type | Ruby Type                      | C# Type    | PHP Type          | Dart Type | Rust Type   |
| ---------- | ----------- | ------------------- | -------------------------------- | ------- | ------------------------------ | ---------- | ----------------- | --------- | ----------- |
| double     | double      | double              | float                            | float64 | Float                          | double     | float             | double    | f64         |
| float      | float       | float               | float                            | float32 | Float                          | float      | float             | double    | f32         |
| int32      | int32_t     | int                 | int                              | int32   | Fixnum or Bignum (as required) | int        | integer           | int       | i32         |
| int64      | int64_t     | long                | int/long[4]                      | int64   | Bignum                         | long       | integer/string[6] | Int64     | i64         |
| uint32     | uint32_t    | int[2]              | int/long[4]                      | uint32  | Fixnum or Bignum (as required) | uint       | integer           | int       | u32         |
| uint64     | uint64_t    | long[2]             | int/long[4]                      | uint64  | Bignum                         | ulong      | integer/string[6] | Int64     | u64         |
| sint32     | int32_t     | int                 | int                              | int32   | Fixnum or Bignum (as required) | int        | integer           | int       | i32         |
| sint64     | int64_t     | long                | int/long[4]                      | int64   | Bignum                         | long       | integer/string[6] | Int64     | i64         |
| fixed32    | uint32_t    | int[2]              | int/long[4]                      | uint32  | Fixnum or Bignum (as required) | uint       | integer           | int       | u32         |
| fixed64    | uint64_t    | long[2]             | int/long[4]                      | uint64  | Bignum                         | ulong      | integer/string[6] | Int64     | u64         |
| sfixed32   | int32_t     | int                 | int                              | int32   | Fixnum or Bignum (as required) | int        | integer           | int       | i32         |
| sfixed64   | int64_t     | long                | int/long[4]                      | int64   | Bignum                         | long       | integer/string[6] | Int64     | i64         |
| bool       | bool        | boolean             | bool                             | bool    | TrueClass/FalseClass           | bool       | boolean           | bool      | bool        |
| string     | std::string | String              | str/unicode[5]                   | string  | String (UTF-8)                 | string     | string            | String    | ProtoString |
| bytes      | std::string | ByteString          | str (Python 2), bytes (Python 3) | []byte  | String (ASCII-8BIT)            | ByteString | string            | List      | ProtoBytes  |

[1] Kotlin uses the corresponding types from Java, even for unsigned types, to ensure compatibility in mixed Java/Kotlin codebases.

[2] In Java, unsigned 32-bit and 64-bit integers are represented using their signed counterparts, with the top bit simply being stored in the sign bit.

[3] In all cases, setting values to a field will perform type checking to make sure it is valid.

[4] 64-bit or unsigned 32-bit integers are always represented as long when decoded, but can be an int if an int is given when setting the field. In all cases, the value must fit in the type represented when set. See [2].

[5] Python strings are represented as unicode on decode but can be str if an ASCII string is given (this is subject to change).

[6] Integer is used on 64-bit machines and string is used on 32-bit machines.

You can find out more about how these types are encoded when you serialize your message in [Protocol Buffer Encoding](https://protobuf.dev/programming-guides/encoding).
### 默认值 （Default Field Values）
> When a message is parsed, if the encoded message bytes do not contain a particular field, accessing that field in the parsed object returns the default value for that field. The default values are type-specific:

- For strings, the default value is the empty string.
- For bytes, the default value is empty bytes.
- For bools, the default value is false.
- For numeric types, the default value is zero.
- For message fields, the field is not set. Its exact value is language-dependent. See the [generated code guide](https://protobuf.dev/reference/) for details.
- For enums, the default value is the **first defined enum value**, which must be 0. See [Enum Default Value](https://protobuf.dev/programming-guides/proto3/#enum-default).

> The default value for repeated fields is empty (generally an empty list in the appropriate language).

> The default value for map fields is empty (generally an empty map in the appropriate language).

> Note that for implicit-presence scalar fields, once a message is parsed there’s no way of telling whether that field was explicitly set to the default value (for example whether a boolean was set to `false`) or just not set at all: you should bear this in mind when defining your message types. For example, don’t have a boolean that switches on some behavior when set to `false` if you don’t want that behavior to also happen by default. Also note that if a scalar message field **is** set to its default, the value will not be serialized on the wire. If a float or double value is set to +0 it will not be serialized, but -0 is considered distinct and will be serialized.

> See the [generated code guide](https://protobuf.dev/reference/) for your chosen language for more details about how defaults work in generated code.

### 枚举 （Enumerations）
> When you’re defining a message type, you might want one of its fields to only have one of a predefined list of values. For example, let’s say you want to add a `corpus` field for each `SearchRequest`, where the corpus can be `UNIVERSAL`, `WEB`, `IMAGES`, `LOCAL`, `NEWS`, `PRODUCTS` or `VIDEO`. You can do this very simply by adding an `enum` to your message definition with a constant for each possible value.

> In the following example we’ve added an `enum` called `Corpus` with all the possible values, and a field of type `Corpus`:

```protobuf
enum Corpus {
  CORPUS_UNSPECIFIED = 0;
  CORPUS_UNIVERSAL = 1;
  CORPUS_WEB = 2;
  CORPUS_IMAGES = 3;
  CORPUS_LOCAL = 4;
  CORPUS_NEWS = 5;
  CORPUS_PRODUCTS = 6;
  CORPUS_VIDEO = 7;
}

message SearchRequest {
  string query = 1;
  int32 page_number = 2;
  int32 results_per_page = 3;
  Corpus corpus = 4;
}

```

#### 带前缀的枚举值 （Prefixing Enum Values）
> When prefixing enum values, the remainder of the name with the prefix stripped should still be a legal and style-conformant enum name. For example, avoid the following:

在为枚举值添加前缀时，要记住前缀和基本名的合体也应该是合法的、格式符合契约的。不要像下面这样做：

```protobuf
enum DeviceTier {
  DEVICE_TIER_UNKNOWN = 0;
  DEVICE_TIER_1 = 1;
  DEVICE_TIER_2 = 2;
}

```

> Instead, use a value name like `DEVICE_TIER_TIER1`, where the `DEVICE_TIER_` portion is viewed as scoping the enum value rather than as part of the individual enum value name. Some Protobuf implementations automatically strip the prefix that matches the containing enum name where it is safe to do so, but could not in this example since a bare `1` is not a legal enum value name.

不要`DEVICE_TIER_1`，要`DEVICE_TIER_TIER1`，因为`DEVICE_TIER_`部分会被视作对枚举值的作用域限定，而不是枚举值名称的一部分。一些Protobuf的实现会尽量不删除前缀，而是把前缀也视作名称的一部分，但在这个例子中，这些实现无法做出安全的行为，因为移除`DEVICE_TIER_`之后留下的`1`并不是合法的枚举值名称

> We plan for a future Edition to add support for scoped enums, which will eliminate the need to manually prefix each enum value and enable this to be written succinctly as `TIER1 = 1`.

我们计划在之后的版本中添加对局部枚举值（*scoped enums*）的支持，不再需要开发者手动添加前缀，开发者可以直接写`TIER1 = 1`
#### 默认枚举值 （Enum Default Value）
```protobuf
enum Corpus {
  CORPUS_UNSPECIFIED = 0;
  CORPUS_UNIVERSAL = 1;
  CORPUS_WEB = 2;
  CORPUS_IMAGES = 3;
  CORPUS_LOCAL = 4;
  CORPUS_NEWS = 5;
  CORPUS_PRODUCTS = 6;
  CORPUS_VIDEO = 7;
}
```

`SearchRequest.corpus`枚举变量的默认值是`CORPUS_UNSPECIFIED`

Proto3中枚举定义的第一个值必须持有零值，并且应该命名为`ENUM_TYPE_NAME_UNSPECIFIED`或`ENUM_TYPE_NAME_UNKNOWN`。这是因为：

- 必须有零值，这样我们就可以将`0`应用为[默认数值](https://protobuf.dev/programming-guides/proto3/#default)
- 零值必须为第一个元素，以便兼容Proto2的语义——除非指定其他值，否则第一个枚举值都会是默认值

也建议第一个枚举值的命名在语义上仅指 *这个值未指定* ，不要包含其他意思
#### 枚举值别名 （Enum Value Aliases）
> You can define aliases by assigning the same value to different enum constants. To do this you need to set the `allow_alias` option to `true`. Otherwise, the protocol buffer compiler generates a warning message when aliases are found. Though all alias values are valid for serialization, only the first value is used when deserializing.

```protobuf
enum EnumAllowingAlias {
  option allow_alias = true;
  EAA_UNSPECIFIED = 0;
  EAA_STARTED = 1;
  EAA_RUNNING = 1;
  EAA_FINISHED = 2;
}

enum EnumNotAllowingAlias {
  ENAA_UNSPECIFIED = 0;
  ENAA_STARTED = 1;
  // ENAA_RUNNING = 1;  // 取消这行的注释会在生成时抛出错误
  ENAA_FINISHED = 2;
}

```

> Enumerator constants must be in the range of a 32-bit integer. Since `enum` values use [varint encoding](https://protobuf.dev/programming-guides/encoding) on the wire, negative values are inefficient and thus not recommended. You can define `enum`s within a message definition, as in the earlier example, or outside – these `enum`s can be reused in any message definition in your `.proto` file. You can also use an `enum` type declared in one message as the type of a field in a different message, using the syntax `_MessageType_._EnumType_`.

> When you run the protocol buffer compiler on a `.proto` that uses an `enum`, the generated code will have a corresponding `enum` for Java, Kotlin, or C++, or a special `EnumDescriptor` class for Python that’s used to create a set of symbolic constants with integer values in the runtime-generated class.

:::important
The generated code may be subject to language-specific limitations on the number of enumerators (low thousands for one language). Review the limitations for the languages you plan to use.
:::
> During deserialization, unrecognized enum values will be preserved in the message, though how this is represented when the message is deserialized is language-dependent. In languages that support open enum types with values outside the range of specified symbols, such as C++ and Go, the unknown enum value is simply stored as its underlying integer representation. In languages with closed enum types such as Java, a case in the enum is used to represent an unrecognized value, and the underlying integer can be accessed with special accessors. In either case, if the message is serialized the unrecognized value will still be serialized with the message.

:::important
For information on how enums should work contrasted with how they currently work in different languages, see [Enum Behavior](https://protobuf.dev/programming-guides/enum).
:::

> For more information about how to work with message `enum`s in your applications, see the [generated code guide](https://protobuf.dev/reference/) for your chosen language.

#### 标记不再可用的枚举值 （Reserved Values）
> If you [update](https://protobuf.dev/programming-guides/proto3/#updating) an enum type by entirely removing an enum entry, or commenting it out, future users can reuse the numeric value when making their own updates to the type. This can cause severe issues if they later load old instances of the same `.proto`, including data corruption, privacy bugs, and so on. One way to make sure this doesn’t happen is to specify that the numeric values (and/or names, which can also cause issues for JSON serialization) of your deleted entries are `reserved`. The protocol buffer compiler will complain if any future users try to use these identifiers. You can specify that your reserved numeric value range goes up to the maximum possible value using the `max` keyword.

```protobuf
enum Foo {
  reserved 2, 15, 9 to 11, 40 to max;
  reserved "FOO", "BAR";
}

```
### 使用其他消息类型 （Using Other Message Types）
> You can use other message types as field types. For example, let’s say you wanted to include `Result` messages in each `SearchResponse` message – to do this, you can define a `Result` message type in the same `.proto` and then specify a field of type `Result` in `SearchResponse`:

你可以将消息类型用作字段类型：
```protobuf
message SearchResponse {
  repeated Result results = 1;
}

message Result {
  string url = 1;
  string title = 2;
  repeated string snippets = 3;
}

```

#### 导入其他消息类型 （Importing Definitions）
> In the earlier example, the `Result` message type is defined in the same file as `SearchResponse` – what if the message type you want to use as a field type is already defined in another `.proto` file?

在上一个例子中，`Result`消息类型和`SearchResponse`是定义在同一个文件中的。那如果你想使用的消息类型在另一个`.proto`中呢？

> You can use definitions from other `.proto` files by _importing_ them. To import another `.proto`’s definitions, you add an import statement to the top of your file:

你可以通过 *导入* 使用其他`.proto`中的消息类型。你需要在文件顶部加上这一行导入语句：
```protobuf
import "myproject/other_protos.proto";

```

> The protobuf compiler searches for imported files in a set of directories specified using the `-I`/`--proto_path` flag. The path given in an `import` statement is resolved relative to these directories. For more information on using the compiler, see [Generating Your Classes](https://protobuf.dev/programming-guides/proto3/#generating).

Protobuf编译器会在`-I`/`--proto_path`指定的路径下搜索可导入的文件。而`import`语句指定的路径会被解析到CLI参数所指定的目录下。详情请见[生成契约类](https://protobuf.dev/programming-guides/proto3/#generating)

> For example, consider the following directory structure:

以下面的文件结构为例：
```
my_project/
├── protos/
│   ├── main.proto
│   └── common/
│       └── timestamp.proto

```

> To use definitions from `timestamp.proto` within `main.proto`, you would run the compiler from the `my_project` directory and set `--proto_path=protos`. The `import` statement in `main.proto` would then be:

要想在`main.proto`中使用`timestamp.proto`，你需要在运行在`my_project`目录的终端中设置`--proto_path=protos`，`main.proto`中的`import`语句则为：
```protobuf
// Located in my_project/protos/main.proto
import "common/timestamp.proto";

```

> In general you should set the `--proto_path` flag to the highest-level directory that contains protos. This is often the root of the project, but in this example it’s in a separate `/protos` directory.

> By default, you can use definitions only from directly imported `.proto` files. However, sometimes you may need to move a `.proto` file to a new location. Instead of moving the `.proto` file directly and updating all the call sites in a single change, you can put a placeholder `.proto` file in the old location to forward all the imports to the new location using the `import public` notion.

:::note
The public import functionality available in Java is most effective when moving an entire .proto file or when using `java_multiple_files = true`. In these cases, generated names remain stable, avoiding the need to update references in your code. While technically functional when moving a subset of a .proto file without `java_multiple_files = true`, doing so requires simultaneous updates to many references, thus might not significantly ease migration. The functionality is not available in Kotlin, TypeScript, JavaScript, GCL, or with C++ targets that use protobuf static reflection.
:::

> `import public` dependencies can be transitively relied upon by any code importing the proto containing the `import public` statement. For example:

```protobuf
// new.proto
// All definitions are moved here

```

```protobuf
// old.proto
// This is the proto that all clients are importing.
import public "new.proto";
import "other.proto";

```

```protobuf
// client.proto
import "old.proto";
// You use definitions from old.proto and new.proto, but not other.proto

```
#### 使用Proto2的消息类型 （Using proto2 Message Types）
> It’s possible to import [proto2](https://protobuf.dev/programming-guides/proto2) message types and use them in your proto3 messages, and vice versa. However, proto2 enums cannot be used directly in proto3 syntax (it’s okay if an imported proto2 message uses them).

### 嵌套类型 （Nested Types）
> You can define and use message types inside other message types, as in the following example – here the `Result` message is defined inside the `SearchResponse` message:

你可以在一个消息类型里定义并使用其他消息类型：比如像下面这样，在`SearchResponse`消息中定义并使用`Result`消息
```protobuf
message SearchResponse {
  message Result {
    string url = 1;
    string title = 2;
    repeated string snippets = 3;
  }
  repeated Result results = 1;
}

```

> If you want to reuse this message type outside its parent message type, you refer to it as `_Parent_._Type_`:

如果你想在父级消息外部复用嵌套消息，你需要这样访问子级消息 `_Parent_._Type_`：
```protobuf
message SomeOtherMessage {
  SearchResponse.Result result = 1;
}

```

> You can nest messages as deeply as you like. In the example below, note that the two nested types named `Inner` are entirely independent, since they are defined within different messages:

你可以无限嵌套消息定义，也可以在不同的消息内部定义同样的子级消息

```protobuf
message Outer {       // Level 0
  message MiddleAA {  // Level 1
    message Inner {   // Level 2
      int64 ival = 1;
      bool  booly = 2;
    }
  }
  message MiddleBB {  // Level 1
    message Inner {   // Level 2
      int32 ival = 1;
      bool  booly = 2;
    }
  }
}

```
### 更新消息定义 （Updating A Message Type）
> If an existing message type no longer meets all your needs – for example, you’d like the message format to have an extra field – but you’d still like to use code created with the old format, don’t worry! It’s very simple to update message types without breaking any of your existing code when you use the binary wire format.

如果已有的消息格式不再满足你的全部需求——比如，你想给现有消息增加一个新的字段，但又想沿用旧的序列化配置，别担心，如果你用的是二进制流式编码（binary wire format），你可以轻松更新消息类型，而不丢失兼容性
:::note
If you use ProtoJSON or [proto text format](https://protobuf.dev/reference/protobuf/textformat-spec) to store your protocol buffer messages, the changes that you can make in your proto definition are different. The ProtoJSON wire format safe changes are described [here](https://protobuf.dev/programming-guides/json#json-wire-safety).
:::

> Check [Proto Best Practices](https://protobuf.dev/best-practices/dos-donts) and the following rules:

#### 不安全的二进制编码字段更改 （Binary Wire-unsafe Changes）
> Wire-unsafe changes are schema changes that will break if you use parse data that was serialized using the old schema with a parser that is using the new schema (or vice versa). Only make wire-unsafe changes if you know that all serializers and deserializers of the data are using the new schema.

？？？

- 修改已有字段的ID是不安全的
	- 修改已有字段的ID等效于删除这个字段并创建新的类型一样的字段。如果你真的想给字段换个ID，请查看[删除一个字段](https://protobuf.dev/programming-guides/proto3/#deleting)
- 将字段ID更改为已存在的`oneof`ID也是不安全的
	> Moving fields into an existing `oneof` is not safe.

#### 安全的二进制编码字段更新 （Binary Wire-safe Changes）
> Wire-safe changes are ones where it is fully safe to evolve the schema in this way without risk of data loss or new parse failures.

> Note that any wire-safe changes may be a breaking change to application code in a given language. For example, adding a value to a preexisting enum would be a compilation break for any code with an exhaustive switch on that enum. For that reason, Google may avoid making some of these types of changes on public messages: the AIPs contain guidance for which of these changes are safe to make there.

- 增加新字段是安全的
	Adding new fields is safe.
    - If you add new fields, any messages serialized by code using your “old” message format can still be parsed by your new generated code. You should keep in mind the [default values](https://protobuf.dev/programming-guides/proto3/#default) for these elements so that new code can properly interact with messages generated by old code. Similarly, messages created by your new code can be parsed by your old code: old binaries simply ignore the new field when parsing. See the [Unknown Fields](https://protobuf.dev/programming-guides/proto3/#unknowns) section for details.
- 删除字段是安全的
	Removing fields is safe.
    - The same field number must not used again in your updated message type. You may want to rename the field instead, perhaps adding the prefix “OBSOLETE_”, or make the field number [reserved](https://protobuf.dev/programming-guides/proto3/#fieldreserved), so that future users of your `.proto` can’t accidentally reuse the number.
- 给枚举添加新的值是安全的
	Adding additional values to an enum is safe.
- Changing a single explicit presence field or extension into a member of a **new** `oneof` is safe.
- Changing a `oneof` which contains only one field to an explicit presence field is safe.
- Changing a field into an extension of same number and type is safe.

#### 可能安全的二进制编码字段更改 （Binary Wire-compatible Changes (Conditionally Safe)）：那些相互兼容的字段类型
> Unlike Wire-safe changes, wire-compatible means that the same data can be parsed both before and after a given change. However, a parse of the data may be lossy under this shape of change. For example, changing an int32 to an int64 is a compatible change, but if a value larger than INT32_MAX is written, a client that reads it as an int32 will discard the high order bits of the number.

> You can make compatible changes to your schema only if you manage the roll out to your system carefully. For example, you may change an int32 to an int64 but ensure you continue to only write legal int32 values until the new schema is deployed to all endpoints, and then subsequently start writing larger values after that.

> If your schema is published outside of your organization, you should generally not make wire-compatible changes, as you cannot manage the deployment of the new schema to know when the different range of values may be safe to use.

- `int32`, `uint32`, `int64`, `uint64`, and `bool` are all compatible.
    - If a number is parsed from the wire which doesn’t fit in the corresponding type, you will get the same effect as if you had cast the number to that type in C++ (for example, if a 64-bit number is read as an int32, it will be truncated to 32 bits).
- `sint32` and `sint64` are compatible with each other but are _not_ compatible with the other integer types.
    - If the value written was between INT_MIN and INT_MAX inclusive it will parse as the same value with either type. If an sint64 value was written outside of that range and parsed as an sint32, the varint is truncated to 32 bits and then zigzag decoding occurs (which will cause a different value to be observed).
- `string` and `bytes` are compatible as long as the bytes are valid UTF-8.
- Embedded messages are compatible with `bytes` if the bytes contain an encoded instance of the message.
- `fixed32` is compatible with `sfixed32`, and `fixed64` with `sfixed64`.
- For `string`, `bytes`, and message fields, singular is compatible with `repeated`.
    - Given serialized data of a repeated field as input, clients that expect this field to be singular will take the last input value if it’s a primitive type field or merge all input elements if it’s a message type field. Note that this is **not** generally safe for numeric types, including bools and enums. Repeated fields of numeric types are serialized in the [packed](https://protobuf.dev/programming-guides/encoding#packed) format by default, which will not be parsed correctly when a singular field is expected.
- `enum` is compatible with `int32`, `uint32`, `int64`, and `uint64`
    - Be aware that client code may treat them differently when the message is deserialized: for example, unrecognized proto3 `enum` values will be preserved in the message, but how this is represented when the message is deserialized is language-dependent.
- Changing a field between a `map<K, V>` and the corresponding `repeated` message field is binary compatible (see [Maps](https://protobuf.dev/programming-guides/proto3/#maps), below, for the message layout and other restrictions).
    - However, the safety of the change is application-dependent: when deserializing and reserializing a message, clients using the `repeated` field definition will produce a semantically identical result; however, clients using the `map` field definition may reorder entries and drop entries with duplicate keys.

### 未知字段 （Unknown Fields）
> Unknown fields are well-formed protocol buffer serialized data representing fields that the parser does not recognize. For example, when an old binary parses data sent by a new binary with new fields, those new fields become unknown fields in the old binary.

> Proto3 messages preserve unknown fields and include them during parsing and in the serialized output, which matches proto2 behavior.

#### 避免丢失未知字段 （Retaining Unknown Fields）
> Some actions can cause unknown fields to be lost. For example, if you do one of the following, unknown fields are lost:

- Serialize a proto to JSON.
- Iterate over all of the fields in a message to populate a new message.

> To avoid losing unknown fields, do the following:

- Use binary; avoid using text formats for data exchange.
- Use message-oriented APIs, such as `CopyFrom()` and `MergeFrom()`, to copy data rather than copying field-by-field

> TextFormat is a bit of a special case. Serializing to TextFormat prints unknown fields using their field numbers. But parsing TextFormat data back into a binary proto fails if there are entries that use field numbers.

### Any
> The `Any` message type lets you use messages as embedded types without having their .proto definition. An `Any` contains an arbitrary serialized message as `bytes`, along with a URL that acts as a globally unique identifier for and resolves to that message’s type. To use the `Any` type, you need to [import](https://protobuf.dev/programming-guides/proto3/#other) `google/protobuf/any.proto`.

`Any`消息类型允许你在消息中嵌入类型，而不需要知道对应的`.proto`定义。`Any`中会包含`bytes`类型的任意已序列化数据，以及可解析到该消息类型的URL（统一资源定位符）。导入`google/protobuf/any.proto`以使用`Any`消息类型。

```protobuf
import "google/protobuf/any.proto";

message ErrorStatus {
  string message = 1;
  repeated google.protobuf.Any details = 2;
}

```

> The default type URL for a given message type is `type.googleapis.com/_packagename_._messagename_`.

> Different language implementations will support runtime library helpers to pack and unpack `Any` values in a typesafe manner – for example, in Java, the `Any` type will have special `pack()` and `unpack()` accessors, while in C++ there are `PackFrom()` and `UnpackTo()` methods:

```c++
// Storing an arbitrary message type in Any.
NetworkErrorDetails details = ...;
ErrorStatus status;
status.add_details()->PackFrom(details);

// Reading an arbitrary message from Any.
ErrorStatus status = ...;
for (const google::protobuf::Any& detail : status.details()) {
  if (detail.Is<NetworkErrorDetails>()) {
    NetworkErrorDetails network_error;
    detail.UnpackTo(&network_error);
    ... processing network_error ...
  }
}

```

### Oneof
> If you have a message with many singular fields and where at most one field will be set at the same time, you can enforce this behavior and save memory by using the oneof feature.

> Oneof fields are like optional fields except all the fields in a oneof share memory, and at most one field can be set at the same time. Setting any member of the oneof automatically clears all the other members. You can check which value in a oneof is set (if any) using a special `case()` or `WhichOneof()` method, depending on your chosen language.

> Note that if _multiple values are set, the last set value as determined by the order in the proto will overwrite all previous ones_.

> Field numbers for oneof fields must be unique within the enclosing message.

#### 使用Oneof功能 （Using Oneof）
```protobuf
message SampleMessage {
  oneof test_oneof {
    string name = 4;
    SubMessage sub_message = 9;
  }
}

```

> You then add your oneof fields to the oneof definition. You can add fields of any type, except `map` fields and `repeated` fields. If you need to add a repeated field to a oneof, you can use a message containing the repeated field.

> In your generated code, oneof fields have the same getters and setters as regular fields. You also get a special method for checking which value (if any) in the oneof is set. You can find out more about the oneof API for your chosen language in the relevant [API reference](https://protobuf.dev/reference/).

#### Oneof的特性 （Oneof Features）
- Setting a oneof field will automatically clear all other members of the oneof. So if you set several oneof fields, only the _last_ field you set will still have a value.
```protobuf
SampleMessage message;
message.set_name("name");
CHECK_EQ(message.name(), "name");
// Calling mutable_sub_message() will clear the name field and will set
// sub_message to a new instance of SubMessage with none of its fields set.
message.mutable_sub_message();
CHECK(message.name().empty());

```

- If the parser encounters multiple members of the same oneof on the wire, only the last member seen is used in the parsed message. When parsing data on the wire, starting at the beginning of the bytes, evaluate the next value, and apply the following parsing rules:
	
	- First, check if a _different_ field in the same oneof is currently set, and if so clear it.
	- Then apply the contents as though the field was not in a oneof:
	    - A primitive will overwrite any value already set
	    - A message will merge into any value already set

- A oneof cannot be `repeated`.
    
- Reflection APIs work for oneof fields.
    
- If you set a oneof field to the default value (such as setting an int32 oneof field to 0), the “case” of that oneof field will be set, and the value will be serialized on the wire.
    
- If you’re using C++, make sure your code doesn’t cause memory crashes. The following sample code will crash because `sub_message` was already deleted by calling the `set_name()` method.

```c++
SampleMessage message;
SubMessage* sub_message = message.mutable_sub_message();
message.set_name("name");      // Will delete sub_message
sub_message->set_...            // Crashes here

```

> Again in C++, if you `Swap()` two messages with oneofs, each message will end up with the other’s oneof case: in the example below, `msg1` will have a `sub_message` and `msg2` will have a `name`.

```c++
SampleMessage msg1;
msg1.set_name("name");
SampleMessage msg2;
msg2.mutable_sub_message();
msg1.swap(&msg2);
CHECK(msg1.has_sub_message());
CHECK_EQ(msg2.name(), "name");

```

#### 向后兼容的问题 （Backwards-compatibility issues）
> Be careful when adding or removing oneof fields. If checking the value of a oneof returns `None`/`NOT_SET`, it could mean that the oneof has not been set or it has been set to a field in a different version of the oneof. There is no way to tell the difference, since there’s no way to know if an unknown field on the wire is a member of the oneof.

##### 字段ID复用问题 （Tag Reuse Issues）
- **Move singular fields into or out of a oneof**: You may lose some of your information (some fields will be cleared) after the message is serialized and parsed. However, you can safely move a single field into a **new** oneof and may be able to move multiple fields if it is known that only one is ever set. See [Updating A Message Type](https://protobuf.dev/programming-guides/proto3/#updating) for further details.
- **Delete a oneof field and add it back**: This may clear your currently set oneof field after the message is serialized and parsed.
- **Split or merge oneof**: This has similar issues to moving singular fields.

### 键值对 （Maps）
> If you want to create an associative map as part of your data definition, protocol buffers provides a handy shortcut syntax:

```protobuf
map<key_type, value_type> map_field = N;

```

> …where the `key_type` can be any integral or string type (so, any [scalar](https://protobuf.dev/programming-guides/proto3/#scalar) type except for floating point types and `bytes`). Note that neither enum nor proto messages are valid for `key_type`. The `value_type` can be any type except another map.

> So, for example, if you wanted to create a map of projects where each `Project` message is associated with a string key, you could define it like this:

```protobuf
map<string, Project> projects = 3;

```

#### 特性 （Maps Features）
- Map fields cannot be `repeated`.
- Wire format ordering and map iteration ordering of map values is undefined, so you cannot rely on your map items being in a particular order.
- When generating text format for a `.proto`, maps are sorted by key. Numeric keys are sorted numerically.
- When parsing from the wire or when merging, if there are duplicate map keys the last key seen is used. When parsing a map from text format, parsing may fail if there are duplicate keys.
- If you provide a key but no value for a map field, the behavior when the field is serialized is language-dependent. In C++, Java, Kotlin, and Python the default value for the type is serialized, while in other languages nothing is serialized.
- No symbol `FooEntry` can exist in the same scope as a map `foo`, because `FooEntry` is already used by the implementation of the map.

The generated map API is currently available for all supported languages. You can find out more about the map API for your chosen language in the relevant [API reference](https://protobuf.dev/reference/).

#### 向后兼容性 （Backwards Compatibility） 
> The map syntax is equivalent to the following on the wire, so protocol buffers implementations that do not support maps can still handle your data:

```protobuf
message MapFieldEntry {
  key_type key = 1;
  value_type value = 2;
}

repeated MapFieldEntry map_field = N;

```

> Any protocol buffers implementation that supports maps must both produce and accept data that can be accepted by the earlier definition.

### 包管理 （Packages）
> You can add an optional `package` specifier to a `.proto` file to prevent name clashes between protocol message types.

```protobuf
package foo.bar;
message Open { ... }

```

> You can then use the package specifier when defining fields of your message type:

```protobuf
message Foo {
  ...
  foo.bar.Open open = 1;
  ...
}

```

> The way a package specifier affects the generated code depends on your chosen language:

- In **C++** the generated classes are wrapped inside a C++ namespace. For example, `Open` would be in the namespace `foo::bar`.
- In **Java** and **Kotlin**, the package is used as the Java package, unless you explicitly provide an `option java_package` in your `.proto` file.
- In **Python**, the `package` directive is ignored, since Python modules are organized according to their location in the file system.
- In **Go**, the `package` directive is ignored, and the generated `.pb.go` file is in the package named after the corresponding `go_proto_library` Bazel rule. For open source projects, you **must** provide either a `go_package` option or set the Bazel `-M` flag.
- In **Ruby**, the generated classes are wrapped inside nested Ruby namespaces, converted to the required Ruby capitalization style (first letter capitalized; if the first character is not a letter, `PB_` is prepended). For example, `Open` would be in the namespace `Foo::Bar`.
- In **PHP** the package is used as the namespace after converting to PascalCase, unless you explicitly provide an `option php_namespace` in your `.proto` file. For example, `Open` would be in the namespace `Foo\Bar`.
- In **C#** the package is used as the namespace after converting to PascalCase, unless you explicitly provide an `option csharp_namespace` in your `.proto` file. For example, `Open` would be in the namespace `Foo.Bar`.

> Note that even when the `package` directive does not directly affect the generated code, for example in Python, it is still strongly recommended to specify the package for the `.proto` file, as otherwise it may lead to naming conflicts in descriptors and make the proto not portable for other languages.

#### 包名解析 （Packages and Name Resolution）
> Type name resolution in the protocol buffer language works like C++: first the innermost scope is searched, then the next-innermost, and so on, with each package considered to be “inner” to its parent package. A leading ‘.’ (for example, `.foo.bar.Baz`) means to start from the outermost scope instead.

> The protocol buffer compiler resolves all type names by parsing the imported `.proto` files. The code generator for each language knows how to refer to each type in that language, even if it has different scoping rules.

***
# 页面底部