---
title: 从零开始的Fyne（三）
date: 2026-01-12
---
[[toc]]
## 布局列表
### 标准布局
#### 水平容器/Horizontal Box/HBox
> Horizontal Box arranges items in a horizontal row. Every element will have the same height (the height of the tallest item in the container) and objects will be left-aligned at their minimum width.
![](assets/Pasted%20image%2020260112005345.png)
#### 垂直容器/Vertical Box/VBox
> Vertical Box arranges items in a vertical column. Every element will have the same width (the width of the widest item in the container) and objects will be top-aligned at their minimum height.
![](assets/Pasted%20image%2020260112005424.png)
#### 东西南北布局/Border
> Border layout supports positioning of items at the outside of available space. The border is passed pointers to the objects for (top, left, bottom, right). All items in the container that are not positioned on a border will fill the remaining space.
![](assets/Pasted%20image%2020260112005513.png)
#### 居中布局/Center
> Center layout positions all container elements in the center of the container. Every object will be set to its minimum size.
![](assets/Pasted%20image%2020260112005549.png)
#### 表单布局/等宽横栏布局/Form
> Form layout arranges items in pairs where the first column is at minimum width. This is normally useful for labelling elements in a form, where the label is in the first column and the item it describes is in the second. You should always add an even number of elements to a form layout.
![](assets/Pasted%20image%2020260112005622.png)
#### 网格布局/Grid
> Grid layout arranges items equally in the available space. A number of columns is specified, with objects being positioned horizontally until the number of columns is reached at which point a new row is started. All objects have the same size, that is width divided by column total and the height will be total height divided by the number of rows required. Minus padding.
![](assets/Pasted%20image%2020260112005644.png)

#### 宽度可变的网格布局/GridWrap
> GridWrap layout arranges all items to flow along a row, wrapping to a new row if there is insufficient space. All objects will be set to the same size, which is the size passed to the layout. This layout may not respect item MinSize to manage this uniform layout. Often used in file managers or image thumbnail lists.
![](assets/Pasted%20image%2020260112005737.png)
#### 留白布局/Padded
> Padded layout positions all container elements to fill the available space but with a small padding around the outside. The size of the padding is theme specific. The objects will all be drawn in the order they were added to the container (last-most is on top).
![](assets/Pasted%20image%2020260112005818.png)
> You can also specify each site separately using `CustomPadded` layout.
![](assets/Pasted%20image%2020260112005840.png)
#### 高度可变的行列式布局/RowWrap
> RowWrap layout arranges a set of different items to flow along a row, wrapping to a new row if there is insufficient space. All objects will be set to their minimum size, and will be bottom aligned to a consistent position leaving space for the tallest item.
![](assets/Pasted%20image%2020260112005922.png)
#### 栈布局（曾经是最好的）/Stack(was Max)
> Stack layout positions all container elements to fill the available space. The objects will all be full-sized and drawn in the order they were added to the container (last-most is on top).
![](assets/Pasted%20image%2020260112010009.png)
### 联合布局
> It is possible to build up more complex application structures by using multiple layouts. Multiple containers that each have their own layout can be nested to create complete user interface arrangements using only the standard layouts listed above. For example a horizontal box for a header, a vertical box for a left side file panel and a grid wrap layout in the content area - all inside a container using a border layout can build the result illustrated below.
![](assets/Pasted%20image%2020260112010048.png)
***
# 页面底部