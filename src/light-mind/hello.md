---
excalidraw-plugin: parsed
tags:
  - excalidraw
title: Hello World!
icon: pen-to-square
category:
  - Markdown样式测试
tag:
  - Obsidian
  - Admonition
  - Markdown-It
---


***
# Markdown样式测试
[[toc]]
*只能读取二级和三级标题*
## 二级标题

### 三级标题

#### 四级标题

##### 五级标题
###### 六级标题

***
## 代码格式
单行代码 `<?php phpinfo();?>`
多行代码 `Python`
```Python
import requests
print(requests.get("http://example.com").text)
```
不显示行号的多行代码 `Python:no-line-numbers`
```Python:no-line-numbers
import requests
print(requests.get("http://example.com").text)
```

VuePress默认不编译代码 `md`
```md
<!-- 默认情况下，这里会被保持原样 -->

1 + 2 + 3 = {{ 1 + 2 + 3 }}
```
使用`no-v-pre`来允许Vue编译代码 `md:no-v-pre` （生产环境中这个配置似乎是锁死不能打开的）
```md:no-v-pre
<!-- 这里会被 Vue 编译 -->

1 + 2 + 3 = {{ 1 + 2 + 3 }}
```

```js:no-v-pre
// 由于 JS 代码高亮，这里不会被正确编译
const onePlusTwoPlusThree = {{ 1 + 2 + 3 }}
```

***
##  字体测试
*斜体*
**粗体**
~~波浪线~~
$\frac{1}{2}$ **当前未启用LateX插件**
***
![](../static-assets/Pasted%20image%2020250705214847.png)

***

- 无序列表
	- 次级无序列表
		- 次次级无序列表

1. 有序列表
	1. 1.1
		1. 1.1.1
	2. 1.2
2. 2
3. 3
	1. 3.1
		1. 3.1.1
		2. 3.1.2
***
## 在Markdown中使用Vue语法
一加一等于： {{ 1 + 1 }}

<span v-for="i in 3"> span: {{ i }} </span>
**效果如下所示：**
![](../static-assets/Pasted%20image%2020250705221913.png)
***
## VuePress的内置组件
```
- VuePress - <Badge type="tip" text="v2" vertical="top" />
- VuePress - <Badge type="warning" text="v2" vertical="middle" />
- VuePress - <Badge type="danger" text="v2" vertical="bottom" />
- VuePress - <Badge type="important" text="v2" vertical="middle" />
- VuePress - <Badge type="info" text="v2" vertical="middle" />
- VuePress - <Badge type="note" text="v2" vertical="middle" />
```

- VuePress - <Badge type="tip" text="提示" vertical="top" />
- VuePress - <Badge type="warning" text="警告" vertical="middle" />
- VuePress - <Badge type="danger" text="危险" vertical="bottom" />
- VuePress - <Badge type="important" text="重要" vertical="middle" />
- VuePress - <Badge type="info" text="信息" vertical="middle" />
- VuePress - <Badge type="note" text="备注" vertical="middle" />

***
## VuePress拓展：提示容器
::: tip
这是一个提示容器，下面是一段代码
```Python
if __name__ == '__main__':
	print("Hello World")
```
:::

:::note 注意看，这是一个自定义标题
这是一个备注容器
:::

:::warning 警告消息
[!important]
好像无法启用GFM警告
:::
***
## Markdown官方拓展语法
### 脚注
### 任务列表
```md
- 使用 `- [ ] 一些文字` 渲染一个未勾选的任务项 (中括号间要有空格)
- 使用 `- [x] 一些文字` 渲染一个勾选了的任务项 (我们也支持大写的 `X`)
```

- [ ]  未完成的计划
- [x]  已完成的计划

*Obisidian里可以正确渲染，但在VuePress里却无法渲染*
:::tip
该语法需要在`config.ts`中启用该插件的`gfm`或`tasklist`配置
:::
### 组件

可以使用 component 代码块来在 Markdown 中添加组件。YAML 和 JSON 的数据格式均受支持。
```component Badge
text: SyYhunfhds
type: note
```

:::tip
该语法需要在`config.ts`中启用该插件的`component`配置
:::

***
## Markdown数学公式支持
### 单行数学公式

```
Euler's identity $e^{i\pi}+1=0$ is a beautiful formula in $\mathbb{R}^2$.
```

Euler's identity $e^{i\pi}+1=0$ is a beautiful formula in $\mathbb{R}^2$.
### 多行数学公式
```
$$
\frac {\partial^r} {\partial \omega^r} \left(\frac {y^{\omega}} {\omega}\right)
= \left(\frac {y^{\omega}} {\omega}\right) \left\{(\log y)^r + \sum_{i=1}^r \frac {(-1)^ Ir \cdots (r-i+1) (\log y)^{ri}} {\omega^i} \right\}
$$
```

$$
\frac {\partial^r} {\partial \omega^r} \left(\frac {y^{\omega}} {\omega}\right)
= \left(\frac {y^{\omega}} {\omega}\right) \left\{(\log y)^r + \sum_{i=1}^r \frac {(-1)^ Ir \cdots (r-i+1) (\log y)^{ri}} {\omega^i} \right\}
$$

***
## VuePress组件拓展
### 媒体组件
#### Bilibili
<BiliBili bvid="BV1kt411o7C3" />
*也是蜜汁渲染不出来*

### 工具组件
#### share
**全部组件（灰色）**
<Share />
**全部组件（彩色）**
<Share colorful/>
**自定义分享服务**
<Share :services="['qq','weibo']" />

配置存档，*好像这么存不太对*
```javascript
plugins: {
    components: {
       components: ["Badge", "VPCard"],
       componentOptions: {
        share: {
          services: [
            "douban", "email", "qq", "linkedin", "pinterest"
            // 这里还有其他关键字，详情请查阅https://plugin-components.vuejs.press/zh/guide/utilities/share.html#%E8%AE%BE%E7%BD%AE%E7%BB%84%E4%BB%B6
          ],
        },
       },
       
     },
  },
```
