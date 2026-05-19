---
title: Flutter MaterialApp Components 完全指南
date: 2026-05-14
footer: Trae编辑·AI创作
---

# Flutter MaterialApp Components 完全指南

::: info 简介
本文详细介绍 MaterialApp 及其相关的所有 Material Design 组件，涵盖 Actions、Communication、Containment、Navigation、Selection、Text Inputs 等六大类组件。
:::

## 1. MaterialApp 概述

### 1.1 什么是 MaterialApp

`MaterialApp` 是 Flutter 中用于构建 Material Design 风格应用的顶层 Widget，它封装了路由管理、主题配置、本地化等核心功能。

```dart
MaterialApp(
  title: 'My App',
  theme: ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
  ),
  home: const HomeScreen(),
)
```

### 1.2 MaterialApp 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `navigatorKey` | `GlobalKey<NavigatorState>?` | 控制 Navigator 的全局键 |
| `scaffoldMessengerKey` | `GlobalKey<ScaffoldMessengerState>?` | 控制 ScaffoldMessenger 的全局键 |
| `home` | `Widget?` | 应用的主页面 |
| `routes` | `Map<String, WidgetBuilder>?` | 命名路由表 |
| `initialRoute` | `String?` | 初始路由 |
| `onGenerateRoute` | `RouteFactory?` | 动态路由生成 |
| `theme` | `ThemeData?` | 亮色主题 |
| `darkTheme` | `ThemeData?` | 暗色主题 |
| `themeMode` | `ThemeMode` | 主题模式 |
| `locale` | `Locale?` | 语言设置 |
| `supportedLocales` | `Iterable<Locale>` | 支持的语言列表 |
| `localizationsDelegates` | `Iterable<LocalizationsDelegate>?` | 本地化代理 |

## 2. 布局组件 (Layout)

### 2.1 Scaffold

Scaffold 是 Material Design 布局的基本结构类，提供 app bar、drawer、bottom navigation 等。

```dart
Scaffold(
  appBar: AppBar(title: const Text('Title')),
  drawer: const Drawer(child: DrawerContent()),
  body: const Center(child: Text('Content')),
  bottomNavigationBar: BottomNavigationBar(
    items: const [
      BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
      BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'Settings'),
    ],
  ),
  floatingActionButton: FloatingActionButton(
    onPressed: () {},
    child: const Icon(Icons.add),
  ),
)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `appBar` | `PreferredSizeWidget?` | 顶部应用栏 |
| `body` | `Widget?` | 主内容区域 |
| `floatingActionButton` | `Widget?` | 浮动操作按钮 |
| `floatingActionButtonLocation` | `FloatingActionButtonLocation?` | FAB 位置 |
| `drawer` | `Widget?` | 左侧抽屉 |
| `endDrawer` | `Widget?` | 右侧抽屉 |
| `bottomNavigationBar` | `Widget?` | 底部导航栏 |
| `bottomSheet` | `Widget?` | 底部弹窗 |
| `persistentFooterButtons` | `List<Widget>?` | 持久性底部按钮 |

### 2.2 AppBar

Material Design 应用栏，通常放在 Scaffold 的 appBar 位置。

```dart
AppBar(
  title: const Text('App Title'),
  leading: IconButton(icon: const Icon(Icons.menu), onPressed: () {}),
  actions: [
    IconButton(icon: const Icon(Icons.search), onPressed: () {}),
    IconButton(icon: const Icon(Icons.more_vert), onPressed: () {}),
  ],
  flexibleSpace: const FlexibleSpaceBar(title: Text('Flexible')),
  backgroundColor: Colors.blue,
  elevation: 4,
  centerTitle: true,
)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `title` | `Widget?` | 标题 |
| `leading` | `Widget?` | 左侧部件 |
| `actions` | `List<Widget>?` | 右侧操作按钮 |
| `flexibleSpace` | `Widget?` | 弹性空间 |
| `backgroundColor` | `Color?` | 背景颜色 |
| `elevation` | `double` | 阴影高度 |
| `centerTitle` | `bool?` | 标题居中 |
| `bottom` | `PreferredSizeWidget?` | 底部部件 |
| `automaticallyImplyLeading` | `bool` | 自动推断 leading |

### 2.3 BottomNavigationBar

底部导航栏，用于在多个屏幕之间切换。

```dart
BottomNavigationBar(
  currentIndex: _selectedIndex,
  onTap: (index) => setState(() => _selectedIndex = index),
  type: BottomNavigationBarType.fixed,
  items: const [
    BottomNavigationBarItem(
      icon: Icon(Icons.home),
      label: 'Home',
      backgroundColor: Colors.blue,
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.search),
      label: 'Search',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.person),
      label: 'Profile',
    ),
  ],
)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `items` | `List<BottomNavigationBarItem>` | 导航项 |
| `currentIndex` | `int` | 当前选中索引 |
| `onTap` | `ValueChanged<int>?` | 点击回调 |
| `type` | `BottomNavigationBarType` | 类型（fixed/shifting） |
| `elevation` | `double` | 阴影高度 |
| `backgroundColor` | `Color?` | 背景颜色 |
| `selectedItemColor` | `Color?` | 选中颜色 |
| `unselectedItemColor` | `Color?` | 未选中颜色 |
| `showUnselectedLabels` | `bool?` | 显示未选中标签 |

### 2.4 NavigationBar (Material 3)

Material 3 新的底部导航组件。

```dart
NavigationBar(
  selectedIndex: _selectedIndex,
  onTap: (index) => setState(() => _selectedIndex = index),
  destinations: const [
    NavigationDestination(
      icon: Icon(Icons.home_outlined),
      selectedIcon: Icon(Icons.home),
      label: 'Home',
    ),
    NavigationDestination(
      icon: Icon(Icons.search_outlined),
      selectedIcon: Icon(Icons.search),
      label: 'Search',
    ),
    NavigationDestination(
      icon: Icon(Icons.person_outlined),
      selectedIcon: Icon(Icons.person),
      label: 'Profile',
    ),
  ],
)
```

### 2.5 NavigationRail

侧边导航轨道，适合平板设备。

```dart
NavigationRail(
  selectedIndex: _selectedIndex,
  onTap: (index) => setState(() => _selectedIndex = index),
  labelType: NavigationRailLabelType.all,
  destinations: const [
    NavigationRailDestination(
      icon: Icon(Icons.home_outlined),
      selectedIcon: Icon(Icons.home),
      label: Text('Home'),
    ),
    NavigationRailDestination(
      icon: Icon(Icons.search_outlined),
      selectedIcon: Icon(Icons.search),
      label: Text('Search'),
    ),
  ],
)
```

### 2.6 Drawer

侧边抽屉组件。

```dart
Drawer(
  child: ListView(
    padding: EdgeInsets.zero,
    children: [
      const DrawerHeader(
        decoration: BoxDecoration(color: Colors.blue),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            CircleAvatar(
              radius: 30,
              backgroundImage: NetworkImage('https://example.com/avatar.jpg'),
            ),
            SizedBox(height: 10),
            Text('John Doe', style: TextStyle(color: Colors.white)),
            Text('john@example.com', style: TextStyle(color: Colors.white70)),
          ],
        ),
      ),
      ListTile(
        leading: const Icon(Icons.home),
        title: const Text('Home'),
        onTap: () => Navigator.pop(context),
      ),
      ListTile(
        leading: const Icon(Icons.settings),
        title: const Text('Settings'),
        onTap: () => Navigator.pop(context),
      ),
    ],
  ),
)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `child` | `Widget?` | 抽屉内容 |
| `elevation` | `double` | 阴影高度 |
| `shape` | `ShapeBorder?` | 形状 |

### 2.7 BottomSheet

底部弹窗组件。

```dart
showModalBottomSheet(
  context: context,
  builder: (context) => Container(
    height: 200,
    padding: const EdgeInsets.all(16),
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Text('Title', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        ListTile(
          leading: const Icon(Icons.share),
          title: const Text('Share'),
          onTap: () => Navigator.pop(context),
        ),
        ListTile(
          leading: const Icon(Icons.link),
          title: const Text('Copy Link'),
          onTap: () => Navigator.pop(context),
        ),
      ],
    ),
  ),
);
```

## 3. 按钮组件 (Actions)

### 3.1 ElevatedButton

凸起的按钮，默认带有阴影。

```dart
ElevatedButton(
  onPressed: () {},
  style: ElevatedButton.styleFrom(
    backgroundColor: Colors.blue,
    foregroundColor: Colors.white,
    elevation: 4,
    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
  ),
  child: const Text('Elevated Button'),
)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `onPressed` | `VoidCallback?` | 点击回调 |
| `onLongPress` | `VoidCallback?` | 长按回调 |
| `style` | `ButtonStyle?` | 按钮样式 |
| `child` | `Widget?` | 按钮内容 |

### 3.2 TextButton

文本按钮，无背景色和阴影。

```dart
TextButton(
  onPressed: () {},
  style: TextButton.styleFrom(
    foregroundColor: Colors.blue,
    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
  ),
  child: const Text('Text Button'),
)
```

### 3.3 OutlinedButton

带边框的按钮。

```dart
OutlinedButton(
  onPressed: () {},
  style: OutlinedButton.styleFrom(
    foregroundColor: Colors.blue,
    side: const BorderSide(color: Colors.blue, width: 2),
    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
  ),
  child: const Text('Outlined Button'),
)
```

### 3.4 FloatingActionButton

浮动操作按钮，通常放在右下角。

```dart
FloatingActionButton(
  onPressed: () {},
  tooltip: 'Add',
  backgroundColor: Colors.blue,
  foregroundColor: Colors.white,
  elevation: 6,
  child: const Icon(Icons.add),
)

// Extended FAB
FloatingActionButton.extended(
  onPressed: () {},
  icon: const Icon(Icons.add),
  label: const Text('Add Item'),
)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `onPressed` | `VoidCallback?` | 点击回调 |
| `tooltip` | `String?` | 提示文本 |
| `backgroundColor` | `Color?` | 背景颜色 |
| `foregroundColor` | `Color?` | 前景颜色 |
| `elevation` | `double` | 阴影高度 |
| `child` | `Widget?` | 按钮内容 |

### 3.5 IconButton

图标按钮。

```dart
IconButton(
  onPressed: () {},
  icon: const Icon(Icons.settings),
  tooltip: 'Settings',
  iconSize: 24,
  color: Colors.grey,
  splashRadius: 20,
)
```

### 3.6 SegmentedButton

分段按钮，单选或多选。

```dart
SegmentedButton<int>(
  segments: const [
    ButtonSegment(value: 1, label: Text('One'), icon: Icon(Icons.looks_one)),
    ButtonSegment(value: 2, label: Text('Two'), icon: Icon(Icons.looks_two)),
    ButtonSegment(value: 3, label: Text('Three'), icon: Icon(Icons.looks_3)),
  ],
  selected: {_selected},
  onSelectionChanged: (Set<int> newSelection) {
    setState(() => _selected = newSelection.first);
  },
)
```

### 3.7 PopupMenuButton

弹出菜单按钮。

```dart
PopupMenuButton<String>(
  onSelected: (value) => print('Selected: $value'),
  itemBuilder: (context) => [
    const PopupMenuItem(value: 'item1', child: Text('Item 1')),
    const PopupMenuItem(value: 'item2', child: Text('Item 2')),
    const PopupMenuDivider(),
    const PopupMenuItem(value: 'item3', child: Text('Item 3')),
  ],
  child: const Text('Menu'),
)
```

## 4. 输入组件 (Text Inputs)

### 4.1 TextField

单行文本输入框。

```dart
TextField(
  decoration: const InputDecoration(
    labelText: 'Name',
    hintText: 'Enter your name',
    prefixIcon: Icon(Icons.person),
    suffixIcon: Icon(Icons.clear),
    border: OutlineInputBorder(),
  ),
  controller: _controller,
  keyboardType: TextInputType.text,
  textInputAction: TextInputAction.done,
  obscureText: false,
  maxLength: 50,
  onChanged: (value) => print('Changed: $value'),
  onSubmitted: (value) => print('Submitted: $value'),
)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `decoration` | `InputDecoration?` | 输入装饰 |
| `controller` | `TextEditingController?` | 文本控制器 |
| `keyboardType` | `TextInputType?` | 键盘类型 |
| `textInputAction` | `TextInputAction?` | 键盘动作按钮 |
| `obscureText` | `bool` | 密码模式 |
| `maxLength` | `int?` | 最大长度 |
| `onChanged` | `ValueChanged<String>?` | 变化回调 |
| `onSubmitted` | `ValueChanged<String>?` | 提交回调 |
| `enabled` | `bool` | 是否启用 |

### 4.2 TextFormField

配合 Form 使用的表单文本框。

```dart
TextFormField(
  decoration: const InputDecoration(
    labelText: 'Email',
    hintText: 'Enter your email',
    prefixIcon: Icon(Icons.email),
    border: OutlineInputBorder(),
  ),
  keyboardType: TextInputType.emailAddress,
  validator: (value) {
    if (value == null || value.isEmpty) {
      return 'Please enter your email';
    }
    if (!value.contains('@')) {
      return 'Please enter a valid email';
    }
    return null;
  },
  onSaved: (value) => _email = value,
)
```

### 4.3 InputDecoration

输入框装饰器。

```dart
InputDecoration(
  labelText: 'Username',
  hintText: 'Enter username',
  errorText: 'Invalid username',
  prefixIcon: const Icon(Icons.person),
  suffixIcon: IconButton(icon: const Icon(Icons.clear), onPressed: () {}),
  filled: true,
  fillColor: Colors.grey[100],
  border: OutlineInputBorder(
    borderRadius: BorderRadius.circular(8),
    borderSide: BorderSide(color: Colors.grey),
  ),
  enabledBorder: OutlineInputBorder(
    borderRadius: BorderRadius.circular(8),
    borderSide: BorderSide(color: Colors.grey[300]!),
  ),
  focusedBorder: OutlineInputBorder(
    borderRadius: BorderRadius.circular(8),
    borderSide: const BorderSide(color: Colors.blue, width: 2),
  ),
  errorBorder: OutlineInputBorder(
    borderRadius: BorderRadius.circular(8),
    borderSide: const BorderSide(color: Colors.red, width: 2),
  ),
  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
)
```

### 4.4 DropdownButtonFormField

下拉表单选择框。

```dart
DropdownButtonFormField<String>(
  decoration: const InputDecoration(
    labelText: 'Country',
    border: OutlineInputBorder(),
  ),
  value: _selectedCountry,
  items: const [
    DropdownMenuItem(value: 'us', child: Text('United States')),
    DropdownMenuItem(value: 'uk', child: Text('United Kingdom')),
    DropdownMenuItem(value: 'cn', child: Text('China')),
    DropdownMenuItem(value: 'jp', child: Text('Japan')),
  ],
  onChanged: (value) => setState(() => _selectedCountry = value),
)
```

## 5. 显示组件 (Containment)

### 5.1 Card

卡片容器，用于展示相关内容的集合。

```dart
Card(
  elevation: 4,
  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
  clipBehavior: Clip.antiAlias,
  child: Column(
    mainAxisSize: MainAxisSize.min,
    children: [
      const ListTile(
        leading: CircleAvatar(child: Icon(Icons.person)),
        title: Text('John Doe'),
        subtitle: Text('Software Engineer'),
      ),
      const Padding(
        padding: EdgeInsets.symmetric(horizontal: 16),
        child: Text('A passionate developer who loves coding.'),
      ),
      ButtonBar(
        children: [
          TextButton(onPressed: () {}, child: const Text('VIEW')),
          TextButton(onPressed: () {}, child: const Text('SHARE')),
        ],
      ),
    ],
  ),
)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `elevation` | `double` | 阴影高度 |
| `color` | `Color?` | 背景颜色 |
| `shape` | `ShapeBorder?` | 形状 |
| `clipBehavior` | `Clip` | 裁剪行为 |
| `child` | `Widget?` | 卡片内容 |

### 5.2 ListTile

固定高度的列表项。

```dart
ListTile(
  leading: const CircleAvatar(child: Icon(Icons.person)),
  title: const Text('John Doe'),
  subtitle: const Text('john@example.com'),
  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
  onTap: () {},
  selected: true,
  selectedTileColor: Colors.blue.withOpacity(0.1),
)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `leading` | `Widget?` | 左侧部件 |
| `title` | `Widget?` | 标题 |
| `subtitle` | `Widget?` | 副标题 |
| `trailing` | `Widget?` | 右侧部件 |
| `onTap` | `VoidCallback?` | 点击回调 |
| `selected` | `bool` | 是否选中 |

### 5.3 Chip

标签/碎片组件。

```dart
Chip(
  avatar: const CircleAvatar(child: Text('A')),
  label: const Text('Apple'),
  deleteIcon: const Icon(Icons.close, size: 18),
  onDeleted: () => print('Deleted'),
  onPressed: () => print('Pressed'),
  backgroundColor: Colors.green[100],
  deleteIconColor: Colors.green,
)
```

### 5.4 Divider

分隔线。

```dart
const Divider(
  height: 1,
  thickness: 1,
  color: Colors.grey,
  indent: 16,
  endIndent: 16,
)
```

### 5.5 Badge

徽章组件，显示数量或状态。

```dart
Badge(
  label: const Text('3'),
  child: IconButton(icon: const Icon(Icons.notifications), onPressed: () {}),
)
```

### 5.6 Tooltip

提示气泡。

```dart
const Tooltip(
  message: 'This is a tooltip',
  child: Icon(Icons.help_outline),
)
```

## 6. 通信组件 (Communication)

### 6.1 SnackBar

底部简短消息提示。

```dart
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: const Text('Item deleted'),
    action: SnackBarAction(
      label: 'UNDO',
      onPressed: () => print('Undo'),
    ),
    behavior: SnackBarBehavior.floating,
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    duration: const Duration(seconds: 3),
    backgroundColor: Colors.grey[800],
  ),
)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `content` | `Widget` | 消息内容 |
| `backgroundColor` | `Color?` | 背景颜色 |
| `action` | `SnackBarAction?` | 操作按钮 |
| `duration` | `Duration` | 显示时长 |
| `behavior` | `SnackBarBehavior` | 行为样式 |
| `shape` | `ShapeBorder?` | 形状 |
| `dismissDirection` | `DismissDirection` | 滑动关闭方向 |

### 6.2 AlertDialog

警告对话框。

```dart
showDialog(
  context: context,
  builder: (context) => AlertDialog(
    title: const Text('Confirm'),
    content: const Text('Are you sure you want to delete this item?'),
    actions: [
      TextButton(
        onPressed: () => Navigator.pop(context),
        child: const Text('CANCEL'),
      ),
      TextButton(
        onPressed: () {
          Navigator.pop(context);
          print('Deleted');
        },
        child: const Text('DELETE'),
      ),
    ],
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
  ),
)
```

### 6.3 SimpleDialog

简单对话框。

```dart
showDialog(
  context: context,
  builder: (context) => SimpleDialog(
    title: const Text('Select Option'),
    children: [
      SimpleDialogOption(
        onPressed: () => Navigator.pop(context, 'option1'),
        child: const Row(
          children: [
            Icon(Icons.person),
            SizedBox(width: 16),
            Text('Option 1'),
          ],
        ),
      ),
      SimpleDialogOption(
        onPressed: () => Navigator.pop(context, 'option2'),
        child: const Row(
          children: [
            Icon(Icons.group),
            SizedBox(width: 16),
            Text('Option 2'),
          ],
        ),
      ),
    ],
  ),
)
```

### 6.4 AboutDialog

关于对话框。

```dart
showAboutDialog(
  context: context,
  applicationName: 'My App',
  applicationVersion: '1.0.0',
  applicationIcon: const FlutterLogo(size: 48),
  applicationLegalese: '© 2024 My Company',
  children: [
    const SizedBox(height: 16),
    const Text('A great app for everyone.'),
  ],
)
```

## 7. 选择组件 (Selection)

### 7.1 Checkbox

复选框。

```dart
Checkbox(
  value: _isChecked,
  onChanged: (value) => setState(() => _isChecked = value!),
  activeColor: Colors.blue,
  checkColor: Colors.white,
  tristate: false,
)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `value` | `bool?` | 选中状态 |
| `onChanged` | `ValueChanged<bool?>?` | 变化回调 |
| `activeColor` | `Color?` | 选中颜色 |
| `checkColor` | `Color?` | 勾选颜色 |
| `tristate` | `bool` | 三态模式 |

### 7.2 Switch

开关。

```dart
Switch(
  value: _isEnabled,
  onChanged: (value) => setState(() => _isEnabled = value),
  activeColor: Colors.blue,
  activeTrackColor: Colors.blue[200],
  inactiveThumbColor: Colors.grey,
  inactiveTrackColor: Colors.grey[300],
)
```

### 7.3 Radio

单选按钮。

```dart
RadioListTile<String>(
  value: 'option1',
  groupValue: _selectedOption,
  onChanged: (value) => setState(() => _selectedOption = value!),
  title: const Text('Option 1'),
  subtitle: const Text('Description for option 1'),
  secondary: const Icon(Icons.label),
)
```

### 7.4 Slider

滑块。

```dart
Slider(
  value: _sliderValue,
  onChanged: (value) => setState(() => _sliderValue = value),
  min: 0,
  max: 100,
  divisions: 10,
  label: '${_sliderValue.round()}',
  activeColor: Colors.blue,
  inactiveColor: Colors.blue[200],
)
```

### 7.5 RangeSlider

范围滑块。

```dart
RangeSlider(
  values: _rangeValues,
  onChanged: (values) => setState(() => _rangeValues = values),
  min: 0,
  max: 100,
  divisions: 10,
  labels: RangeLabels('${_rangeValues.start.round()}', '${_rangeValues.end.round()}'),
)
```

## 8. 进度组件 (Progress)

### 8.1 LinearProgressIndicator

线性进度指示器。

```dart
LinearProgressIndicator(
  value: 0.7,
  backgroundColor: Colors.grey[300],
  valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
  minHeight: 8,
  borderRadius: BorderRadius.circular(4),
)
```

### 8.2 CircularProgressIndicator

圆形进度指示器。

```dart
CircularProgressIndicator(
  value: 0.7,
  backgroundColor: Colors.grey[300],
  valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
  strokeWidth: 4,
)
```

### 8.3 RefreshProgressIndicator

刷新进度指示器。

```dart
RefreshProgressIndicator(
  valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
  backgroundColor: Colors.grey[300],
)
```

## 9. 表格组件 (Data Table)

### 9.1 DataTable

数据表格。

```dart
DataTable(
  sortColumnIndex: _sortColumnIndex,
  sortAscending: _sortAscending,
  columns: [
    DataColumn(
      label: const Text('Name'),
      onSort: (columnIndex, ascending) {
        setState(() {
          _sortColumnIndex = columnIndex;
          _sortAscending = ascending;
        });
      },
    ),
    const DataColumn(label: Text('Age'), numeric: true),
    const DataColumn(label: Text('Role')),
  ],
  rows: [
    DataRow(
      cells: [
        const DataCell(Text('John')),
        const DataCell(Text('30')),
        const DataCell(Text('Engineer')),
      ],
    ),
    DataRow(
      cells: [
        const DataCell(Text('Jane')),
        const DataCell(Text('25')),
        const DataCell(Text('Designer')),
      ],
    ),
  ],
)
```

### 9.2 PaginatedDataTable

分页数据表格。

```dart
PaginatedDataTable(
  header: const Text('Employees'),
  columns: const [
    DataColumn(label: Text('Name')),
    DataColumn(label: Text('Age'), numeric: true),
    DataColumn(label: Text('Role')),
  ],
  source: _dataSource,
  rowsPerPage: 10,
  availableRowsPerPage: const [5, 10, 20],
  onRowsPerPageChanged: (value) => setState(() => _rowsPerPage = value!),
)
```

## 10. 导航组件 (Navigation)

### 10.1 TabBar

标签栏。

```dart
DefaultTabController(
  length: 3,
  child: Scaffold(
    appBar: AppBar(
      bottom: const TabBar(
        tabs: [
          Tab(icon: Icon(Icons.home), text: 'Home'),
          Tab(icon: Icon(Icons.search), text: 'Search'),
          Tab(icon: Icon(Icons.person), text: 'Profile'),
        ],
        isScrollable: true,
        indicatorColor: Colors.white,
        labelColor: Colors.white,
        unselectedLabelColor: Colors.white70,
      ),
      title: const Text('TabBar Demo'),
    ),
    body: const TabBarView(
      children: [
        Center(child: Text('Home Page')),
        Center(child: Text('Search Page')),
        Center(child: Text('Profile Page')),
      ],
    ),
  ),
)
```

### 10.2 TabBarView

标签页视图。

```dart
TabBarView(
  controller: _tabController,
  physics: const BouncingScrollPhysics(),
  children: const [
    Center(child: Text('Page 1')),
    Center(child: Text('Page 2')),
    Center(child: Text('Page 3')),
  ],
)
```

## 11. 综合示例

```dart
class MaterialComponentsDemo extends StatelessWidget {
  const MaterialComponentsDemo({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Material Components'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => _showSearchDialog(context),
          ),
          PopupMenuButton<String>(
            onSelected: (value) => print('Selected: $value'),
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'settings', child: Text('Settings')),
              const PopupMenuItem(value: 'about', child: Text('About')),
            ],
          ),
        ],
      ),
      drawer: Drawer(
        child: ListView(
          children: [
            const DrawerHeader(
              decoration: BoxDecoration(color: Colors.blue),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  CircleAvatar(radius: 30, child: Icon(Icons.person, size: 40)),
                  SizedBox(height: 10),
                  Text('User Name', style: TextStyle(color: Colors.white, fontSize: 18)),
                  Text('user@example.com', style: TextStyle(color: Colors.white70)),
                ],
              ),
            ),
            const ListTile(leading: Icon(Icons.home), title: Text('Home')),
            const ListTile(leading: Icon(Icons.settings), title: Text('Settings')),
          ],
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Card(
            child: ListTile(
              leading: CircleAvatar(child: Icon(Icons.person)),
              title: Text('John Doe'),
              subtitle: Text('Software Engineer'),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            decoration: InputDecoration(
              labelText: 'Email',
              prefixIcon: const Icon(Icons.email),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(child: ElevatedButton(onPressed: () {}, child: const Text('Primary'))),
              const SizedBox(width: 8),
              Expanded(child: OutlinedButton(onPressed: () {}, child: const Text('Secondary'))),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Checkbox(value: true, onChanged: (v) {}),
              const Text('Accept terms'),
              const Spacer(),
              Switch(value: true, onChanged: (v) {}),
            ],
          ),
          const SizedBox(height: 16),
          const LinearProgressIndicator(value: 0.7),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showBottomSheet(context),
        icon: const Icon(Icons.add),
        label: const Text('Add'),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.search), label: 'Search'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }

  void _showSearchDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Search'),
        content: const TextField(decoration: InputDecoration(hintText: 'Enter search term')),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('CANCEL')),
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('SEARCH')),
        ],
      ),
    );
  }

  void _showBottomSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Add New Item', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.photo),
              title: const Text('From Gallery'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.camera),
              title: const Text('From Camera'),
              onTap: () => Navigator.pop(context),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 12. 组件分类速查表

| 类别 | 组件 |
|------|------|
| **布局** | Scaffold, AppBar, Drawer, BottomNavigationBar, NavigationBar, NavigationRail, BottomSheet |
| **按钮** | ElevatedButton, TextButton, OutlinedButton, FloatingActionButton, IconButton, SegmentedButton, PopupMenuButton |
| **输入** | TextField, TextFormField, InputDecoration, DropdownButtonFormField |
| **显示** | Card, ListTile, Chip, Divider, Badge, Tooltip |
| **通信** | SnackBar, AlertDialog, SimpleDialog, AboutDialog |
| **选择** | Checkbox, Switch, Radio, RadioListTile, Slider, RangeSlider |
| **进度** | LinearProgressIndicator, CircularProgressIndicator, RefreshProgressIndicator |
| **表格** | DataTable, PaginatedDataTable |
| **导航** | TabBar, TabBarView |

::: tip 最佳实践
1. 使用 Material 3 的 `useMaterial3: true` 启用最新设计语言
2. 优先使用 `NavigationBar` 替代 `BottomNavigationBar`
3. 表单验证使用 `TextFormField` 配合 `Form` 和 `GlobalKey<FormState>`
4. 列表使用 `ListTile` 保持一致性
5. 使用 `Chip` 显示标签和筛选条件
6. 进度指示器使用 `LinearProgressIndicator`（水平）和 `CircularProgressIndicator`（圆形）
:::

::: warning 注意事项
- `Scaffold` 需要在 `MaterialApp` 内部使用
- `AppBar` 必须放在 `Scaffold.appBar` 位置，不能单独使用
- `BottomNavigationBar` 的 items 不能为空
- `TextField` 必须配合 `ScaffoldMessenger` 显示 SnackBar
- 所有输入组件的 `onChanged` 回调可能在每次输入变化时触发，需注意性能
:::
