---
title: Flutter UI导引 （下）
date: 2026-05-13
---
[[toc]]
***
## 环境配置
由于教程开发的是IOS应用，而本人没有IOS设备，也不想捣鼓adb，所以就想在Windows上直接开发

在Windows上开发需要C++工具链和Windows 10/11 SDK（包括DirectX SDK），如果因为某些组件的注册表缓存污染而无法完成安装，可以尝试用[微软疑难解答程序](https://support.microsoft.com/en-us/topic/fix-problems-that-block-programs-from-being-installed-or-removed-cca7d1b6-65a9-3d98-426b-e9f927e1eb4d)卸载有问题的组件，然后回Visual Studio Installer安装
## 高级UI特性
### 引言 Introduction
> In this third installment of the Flutter tutorial series, you'll use Flutter's Cupertino library to build a partial clone of the iOS Contacts app.

在Flutter教程系列第三部分里，你将使用Flutter Cupertino库构建一个IOS通讯录APP

![](assets/Pasted%20image%2020260513212304.png)

> By the end of this tutorial, you'll have learned how to create adaptive layouts, implement comprehensive theming, build navigation patterns, and use advanced scrolling techniques.

通过本教程，你会学会如何创建自适应布局、实现复杂的主题、构建导航模式（*Navigation pattern* ），以及掌握高级滚动组件技巧

#### 你将学到 What you'll learn
> This tutorial explores the following topics:

教程包含以下主题：
- Building responsive layouts with `LayoutBuilder`.  
    使用 `LayoutBuilder` 构建**响应式布局**
- Using advanced scrolling with slivers and search.  
    使用具有 slivers 和搜索的**高级滚动功能**。
- Implementing stack-based navigation patterns.  
    实现**基于栈的导航模式**。
- Creating comprehensive themes with `CupertinoThemeData`.  
    使用 `CupertinoThemeData` 创建全面的主题。
- Supporting both light and dark themes.  
    支持亮色和暗色主题。
- Creating an iOS-style UI using Cupertino widgets.  
    使用 Cupertino 组件创建 iOS 风格的 UI。

> This tutorial assumes that you've completed the previous Flutter tutorials and are comfortable with basic widget composition, state management, and the Flutter project structure.

本教程假设您已完成之前的 Flutter 教程，并且熟悉基本的组件组合、状态管理和 Flutter 项目结构。
### 创建新项目 Create a new Flutter project
```bash
flutter create rolodex --empty
cd rolodex

```

### 设置项目结构 Set up the structure
> First, create the basic directory structure for your app. In your project's `lib` directory, create the following folders:

首先，为您的应用程序创建基本目录结构。在您的项目的 `lib` 目录下，创建以下文件夹：
```bash
mkdir lib/data lib/screens lib/theme

```

> This command creates folders to organize your code into logical sections: data models, screen widgets, and theme configuration.

该命令会创建文件夹以将您的代码组织成逻辑部分： 数据模型、屏幕组件和主题配置

***
# 页面底部