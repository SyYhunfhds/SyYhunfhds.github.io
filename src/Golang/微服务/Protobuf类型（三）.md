---
title: 从零开始的RPC（五）：Protobuf消息类型（三）
date: 2026-02-01
---
[[toc]]
***
## Protobuf类型 （三）
### 定义服务 （Defining Services）
> If you want to use your message types with an RPC (Remote Procedure Call) system, you can define an RPC service interface in a `.proto` file and the protocol buffer compiler will generate service interface code and stubs in your chosen language. So, for example, if you want to define an RPC service with a method that takes your `SearchRequest` and returns a `SearchResponse`, you can define it in your `.proto` file as follows:

```protobuf
service SearchService {
  rpc Search(SearchRequest) returns (SearchResponse);
}

```

> The most straightforward RPC system to use with protocol buffers is [gRPC](https://grpc.io): a language- and platform-neutral open source RPC system developed at Google. gRPC works particularly well with protocol buffers and lets you generate the relevant RPC code directly from your `.proto` files using a special protocol buffer compiler plugin.

> If you don’t want to use gRPC, it’s also possible to use protocol buffers with your own RPC implementation. You can find out more about this in the [Proto2 Language Guide](https://protobuf.dev/programming-guides/proto2#services).

> There are also a number of ongoing third-party projects to develop RPC implementations for Protocol Buffers. For a list of links to projects we know about, see the [third-party add-ons wiki page](https://github.com/protocolbuffers/protobuf/blob/master/docs/third_party.md).

### JSON映射 （JSON Mapping）
> The standard protobuf binary wire format is the preferred serialization format for communication between two systems that use protobufs. For communicating with systems that use JSON rather than protobuf wire format, Protobuf supports a canonical encoding in [JSON](https://protobuf.dev/programming-guides/json).

### 可选`option`配置 （Options）
> Individual declarations in a `.proto` file can be annotated with a number of _options_. Options do not change the overall meaning of a declaration, but may affect the way it is handled in a particular context. The complete list of available options is defined in [`/google/protobuf/descriptor.proto`](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/descriptor.proto).

> Some options are file-level options, meaning they should be written at the top-level scope, not inside any message, enum, or service definition. Some options are message-level options, meaning they should be written inside message definitions. Some options are field-level options, meaning they should be written inside field definitions. Options can also be written on enum types, enum values, oneof fields, service types, and service methods; however, no useful options currently exist for any of these.

> Here are a few of the most commonly used options:

- `java_package` (file option)
- `java_outer_classname` (file option)
- `java_multiple_files` (file option)
- `optimize_for` (file option)：只影响C++和Java的代码生成行为
- `cc_generic_services`, `java_generic_services`, `py_generic_services` (file options)：**泛型服务已被废弃**
- `cc_enable_arenas` (file option)：在生成的C++代码中启用一次性分配一次性释放的内存分配方式
- `objc_class_prefix` (file option)：Ojective C的
- `packed` (field option)：默认对列表和基本数值类型为`true`
- `deprecated` (field option): If set to `true`, indicates that the field is deprecated and should not be used by new code. In most languages this has no actual effect. In Java, this becomes a `@Deprecated` annotation. For C++, clang-tidy will generate warnings whenever deprecated fields are used. In the future, other language-specific code generators may generate deprecation annotations on the field’s accessors, which will in turn cause a warning to be emitted when compiling code which attempts to use the field. If the field is not used by anyone and you want to prevent new users from using it, consider replacing the field declaration with a [reserved](https://protobuf.dev/programming-guides/proto3/#fieldreserved) statement.
```protobuf
int32 old_field = 6 [deprecated = true];

```

#### 枚举值配置项 （Enum Value Options）
> Enum value options are supported. You can use the `deprecated` option to indicate that a value shouldn’t be used anymore. You can also create custom options using extensions.

```protobuf
import "google/protobuf/descriptor.proto";

extend google.protobuf.EnumValueOptions {
  optional string string_name = 123456789;
}

enum Data {
  DATA_UNSPECIFIED = 0;
  DATA_SEARCH = 1 [deprecated = true];
  DATA_DISPLAY = 2 [
    (string_name) = "display_value"
  ];
}

```

> The C++ code to read the `string_name` option might look something like this:

```c++
const absl::string_view foo = proto2::GetEnumDescriptor<Data>()
    ->FindValueByName("DATA_DISPLAY")->options().GetExtension(string_name);

```

> See [Custom Options](https://protobuf.dev/programming-guides/proto3/#customoptions) to see how to apply custom options to enum values and to fields.

#### 自定义配置项 （Custom Options）
> Protocol Buffers also allows you to define and use your own options. Note that this is an **advanced feature** which most people don’t need. If you do think you need to create your own options, see the [Proto2 Language Guide](https://protobuf.dev/programming-guides/proto2#customoptions) for details. Note that creating custom options uses [extensions](https://protobuf.dev/programming-guides/proto2#extensions), which are permitted only for custom options in proto3.

#### 配置维持 （Option Retention）

### 编译`.proto`
To generate the Java, Kotlin, Python, C++, Go, Ruby, Objective-C, or C# code that you need to work with the message types defined in a `.proto` file, you need to run the protocol buffer compiler `protoc` on the `.proto` file. If you haven’t installed the compiler, [download the package](https://protobuf.dev/downloads) and follow the instructions in the README. For Go, you also need to install a special code generator plugin for the compiler; you can find this and installation instructions in the [golang/protobuf](https://github.com/golang/protobuf/) repository on GitHub.

The protobuf compiler is invoked as follows:

```sh
protoc --proto_path=IMPORT_PATH --cpp_out=DST_DIR --java_out=DST_DIR --python_out=DST_DIR --go_out=DST_DIR --ruby_out=DST_DIR --objc_out=DST_DIR --csharp_out=DST_DIR path/to/file.proto
```

- `IMPORT_PATH` specifies a directory in which to look for `.proto` files when resolving `import` directives. If omitted, the current directory is used. Multiple import directories can be specified by passing the `--proto_path` option multiple times. `-I=_IMPORT_PATH_` can be used as a short form of `--proto_path`.

**Note:** File paths relative to their `proto_path` must be globally unique in a given binary. For example, if you have `proto/lib1/data.proto` and `proto/lib2/data.proto`, those two files cannot be used together with `-I=proto/lib1 -I=proto/lib2` because it would be ambiguous which file `import "data.proto"` will mean. Instead `-Iproto/` should be used and the global names will be `lib1/data.proto` and `lib2/data.proto`.

If you are publishing a library and other users may use your messages directly, you should include a unique library name in the path that they are expected to be used under to avoid file name collisions. If you have multiple directories in one project, it is best practice to prefer setting one `-I` to a top level directory of the project.

- You can provide one or more _output directives_:
    
    - `--cpp_out` generates C++ code in `DST_DIR`. See the [C++ generated code reference](https://protobuf.dev/reference/cpp/cpp-generated) for more.
    - `--java_out` generates Java code in `DST_DIR`. See the [Java generated code reference](https://protobuf.dev/reference/java/java-generated) for more.
    - `--kotlin_out` generates additional Kotlin code in `DST_DIR`. See the [Kotlin generated code reference](https://protobuf.dev/reference/kotlin/kotlin-generated) for more.
    - `--python_out` generates Python code in `DST_DIR`. See the [Python generated code reference](https://protobuf.dev/reference/python/python-generated) for more.
    - `--go_out` generates Go code in `DST_DIR`. See the [Go generated code reference](https://protobuf.dev/reference/go/go-generated-opaque) for more.
    - `--ruby_out` generates Ruby code in `DST_DIR`. See the [Ruby generated code reference](https://protobuf.dev/reference/ruby/ruby-generated) for more.
    - `--objc_out` generates Objective-C code in `DST_DIR`. See the [Objective-C generated code reference](https://protobuf.dev/reference/objective-c/objective-c-generated) for more.
    - `--csharp_out` generates C# code in `DST_DIR`. See the [C# generated code reference](https://protobuf.dev/reference/csharp/csharp-generated) for more.
    - `--php_out` generates PHP code in `DST_DIR`. See the [PHP generated code reference](https://protobuf.dev/reference/php/php-generated) for more.
    
    As an extra convenience, if the `DST_DIR` ends in `.zip` or `.jar`, the compiler will write the output to a single ZIP-format archive file with the given name. `.jar` outputs will also be given a manifest file as required by the Java JAR specification. Note that if the output archive already exists, it will be overwritten.
    
- You must provide one or more `.proto` files as input. Multiple `.proto` files can be specified at once. Although the files are named relative to the current directory, each file must reside in one of the `IMPORT_PATH`s so that the compiler can determine its canonical name.
    

## File location
***
# 页面底部