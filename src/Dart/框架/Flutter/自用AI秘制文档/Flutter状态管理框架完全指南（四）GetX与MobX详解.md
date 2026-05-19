---
title: Flutter状态管理框架完全指南（四）GetX与MobX详解
date: 2026-05-14
footer: Trae编辑·AI创作
---

# Flutter状态管理框架完全指南（四）GetX与MobX详解

::: info 简介
本文详细介绍GetX和MobX的核心概念、API、配置方式和最佳实践。GetX是全能框架，MobX是响应式状态管理。
:::

## 1. GetX 基础

### 1.1 安装依赖

```yaml
dependencies:
  get: ^4.6.0
```

### 1.2 核心特性

GetX是一个全能框架，包含：
- **状态管理**
- **路由管理**
- **依赖注入**
- **国际化**
- **主题管理**

### 1.3 基本用法

```dart
import 'package:get/get.dart';

// Controller
class CounterController extends GetxController {
  var count = 0.obs;

  void increment() => count++;
  void decrement() => count--;
}

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text('GetX Demo')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // 使用Obx监听状态
              Obx(() => Text('Count: ${Get.find<CounterController>().count}')),
            ],
          ),
        ),
        floatingActionButton: Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            FloatingActionButton(
              onPressed: () => Get.find<CounterController>().decrement(),
              child: const Icon(Icons.remove),
            ),
            const SizedBox(width: 10),
            FloatingActionButton(
              onPressed: () => Get.find<CounterController>().increment(),
              child: const Icon(Icons.add),
            ),
          ],
        ),
      ),
    );
  }
}

// 在main或第一个widget中初始化
void main() {
  Get.put(CounterController());
  runApp(const MyApp());
}
```

### 1.4 响应式数据类型

| 类型 | 说明 |
|------|------|
| `RxInt` | 响应式整数 |
| `RxDouble` | 响应式浮点数 |
| `RxString` | 响应式字符串 |
| `RxBool` | 响应式布尔值 |
| `RxList<T>` | 响应式列表 |
| `RxMap<K, V>` | 响应式映射 |
| `Rx<T>` | 响应式泛型 |

```dart
class MyController extends GetxController {
  var name = ''.obs;
  var age = 0.obs;
  var isLogged = false.obs;
  var items = <String>[].obs;
  var user = User().obs;

  void updateUser() {
    user.update((user) {
      user?.name = 'New Name';
      user?.age = 30;
    });
  }
}
```

### 1.5 状态监听

```dart
class MyController extends GetxController {
  var count = 0.obs;

  @override
  void onInit() {
    super.onInit();
    // 监听单个值
    ever(count, (value) => print('Count changed: $value'));
    
    // 监听多个值
    everAll([count, name], (_) => print('Something changed'));
    
    // 只监听一次
    once(count, (_) => print('First change'));
    
    // 防抖
    debounce(count, (value) => print('Debounced: $value'), time: const Duration(seconds: 1));
    
    // 节流
    interval(count, (value) => print('Interval: $value'), time: const Duration(seconds: 1));
  }
}
```

### 1.6 依赖注入

```dart
// 注册依赖
Get.put(ApiService());
Get.put(UserController());

// 获取依赖
final api = Get.find<ApiService>();
final controller = Get.find<UserController>();

// 懒加载
Get.lazyPut(() => ApiService());

// 永久依赖（不会被销毁）
Get.create(() => GlobalService());

// 参数注入
Get.putWithParams<UserController>(
  () => UserController(),
  parameters: {'id': '123'},
);
```

### 1.7 路由管理

```dart
// 导航到新页面
Get.to(const SecondScreen());

// 导航并传递参数
Get.to(const SecondScreen(), arguments: {'id': 1});

// 接收参数
final args = Get.arguments;

// 替换当前页面
Get.off(const SecondScreen());

// 返回到上一页
Get.back();

// 返回到首页
Get.offAll(const HomeScreen());

// 路由别名
GetMaterialApp(
  getPages: [
    GetPage(name: '/', page: () => const HomeScreen()),
    GetPage(name: '/details', page: () => const DetailsScreen()),
  ],
);

// 使用别名导航
Get.toNamed('/details');
Get.toNamed('/details?id=123');
```

### 1.8 对话框与SnackBar

```dart
// 显示对话框
Get.dialog(
  AlertDialog(
    title: const Text('Dialog'),
    content: const Text('This is a dialog'),
    actions: [
      TextButton(onPressed: Get.back, child: const Text('OK')),
    ],
  ),
);

// 显示SnackBar
Get.snackbar(
  'Title',
  'Message',
  snackPosition: SnackPosition.BOTTOM,
);

// 显示底部弹窗
Get.bottomSheet(
  Container(
    height: 200,
    child: const Center(child: Text('Bottom Sheet')),
  ),
);
```

## 2. MobX 基础

### 2.1 安装依赖

```yaml
dependencies:
  mobx: ^2.0.0
  flutter_mobx: ^2.0.0

dev_dependencies:
  build_runner: ^2.0.0
  mobx_codegen: ^2.0.0
```

### 2.2 基本用法

```dart
import 'package:mobx/mobx.dart';
import 'package:flutter_mobx/flutter_mobx.dart';

part 'counter.g.dart';

class Counter = CounterBase with _$Counter;

abstract class CounterBase with Store {
  @observable
  int count = 0;

  @action
  void increment() => count++;

  @action
  void decrement() => count--;
}

// 使用
class CounterWidget extends StatelessWidget {
  final Counter counter;

  const CounterWidget({super.key, required this.counter});

  @override
  Widget build(BuildContext context) {
    return Observer(
      builder: (_) => Column(
        children: [
          Text('Count: ${counter.count}'),
          ElevatedButton(
            onPressed: counter.increment,
            child: const Text('Increment'),
          ),
        ],
      ),
    );
  }
}
```

### 2.3 运行代码生成

```bash
dart run build_runner watch
```

### 2.4 核心注解

| 注解 | 说明 |
|------|------|
| `@observable` | 标记可观察状态 |
| `@computed` | 计算属性 |
| `@action` | 标记修改状态的方法 |
| `@reaction` | 响应状态变化 |

### 2.5 Computed

```dart
abstract class Cart with Store {
  @observable
  List<Item> items = [];

  @computed
  double get total => items.fold(0, (sum, item) => sum + item.price);

  @computed
  int get itemCount => items.length;
}
```

### 2.6 Reaction

```dart
abstract class FormStore with Store {
  @observable
  String email = '';

  @observable
  String password = '';

  @computed
  bool get isValid => email.isNotEmpty && password.length >= 6;

  ReactionDisposer? _disposer;

  void setupValidators() {
    _disposer = reaction(
      (_) => isValid,
      (isValid) {
        print('Form valid: $isValid');
      },
    );
  }

  void dispose() {
    _disposer?.();
  }
}
```

### 2.7 异步操作

```dart
abstract class UserStore with Store {
  @observable
  User? user;

  @observable
  bool isLoading = false;

  @observable
  String? error;

  @action
  Future<void> fetchUser(String id) async {
    isLoading = true;
    error = null;
    try {
      user = await api.fetchUser(id);
    } catch (e) {
      error = e.toString();
    } finally {
      isLoading = false;
    }
  }
}
```

### 2.8 ObservableList 和 ObservableMap

```dart
abstract class TodoStore with Store {
  @observable
  final todos = ObservableList<Todo>();

  @observable
  final completed = ObservableMap<String, bool>();

  @action
  void addTodo(Todo todo) {
    todos.add(todo);
    completed[todo.id] = false;
  }

  @action
  void toggleTodo(String id) {
    completed[id] = !completed[id]!;
  }
}
```

## 3. GetX vs MobX

| 特性 | GetX | MobX |
|------|------|------|
| 类型 | 全能框架 | 纯状态管理 |
| 响应式 | 手动(.obs) | 自动追踪 |
| 代码生成 | 不需要 | 需要 |
| 路由管理 | ✅ | ❌ |
| 依赖注入 | ✅ | ⚠️ |
| 学习曲线 | 低 | 中 |

## 4. 最佳实践

### 4.1 GetX 项目结构

```
lib/
├── controllers/
│   ├── counter_controller.dart
│   └── user_controller.dart
├── views/
│   ├── home_view.dart
│   └── profile_view.dart
├── models/
│   └── user_model.dart
├── services/
│   └── api_service.dart
└── main.dart
```

### 4.2 MobX 项目结构

```
lib/
├── stores/
│   ├── counter_store.dart
│   └── user_store.dart
├── views/
│   ├── home_view.dart
│   └── profile_view.dart
├── models/
│   └── user_model.dart
├── services/
│   └── api_service.dart
└── main.dart
```

### 4.3 性能优化

```dart
// GetX: 使用SmartManagement
void main() {
  Get.put(CounterController(), permanent: true);
}

// MobX: 使用Observer包裹最小widget
Observer(
  builder: (_) => Text('${counter.count}'),
)
```

### 4.4 测试

```dart
// GetX测试
void main() {
  setUp(() {
    Get.put(CounterController());
  });

  tearDown(() {
    Get.reset();
  });

  test('counter increments', () {
    final controller = Get.find<CounterController>();
    expect(controller.count.value, 0);
    controller.increment();
    expect(controller.count.value, 1);
  });
}

// MobX测试
void main() {
  test('counter increments', () {
    final counter = Counter();
    expect(counter.count, 0);
    counter.increment();
    expect(counter.count, 1);
  });
}
```

## 5. 常见问题

### 5.1 GetX状态不更新

**问题**：使用普通变量而不是`.obs`

**解决方案**：确保使用响应式变量

```dart
// 错误
var count = 0; // 不会触发更新

// 正确
var count = 0.obs; // 响应式变量
```

### 5.2 MobX代码生成错误

**问题**：忘记运行build_runner

**解决方案**：

```bash
dart run build_runner build
```

### 5.3 GetX依赖找不到

**问题**：在MaterialApp之前使用Get.find()

**解决方案**：使用GetMaterialApp或延迟初始化

```dart
GetMaterialApp(
  home: Builder(
    builder: (context) {
      final controller = Get.find<CounterController>();
      return HomeScreen();
    },
  ),
)
```

---

**下一章**：[五、Redux与ChangeNotifier详解](Flutter状态管理框架完全指南（五）Redux与ChangeNotifier详解.md)
