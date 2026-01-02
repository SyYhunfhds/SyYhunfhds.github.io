---
title: 从零开始的Fyne（二）
date: 2026-01-02
---
[[toc]]
***
## 探索Fyne
### `Canvas`与`CanvasObject`
> In Fyne, a `Canvas` is the area within which an application is drawn. Each window has a canvas, which you can access with `Window.Canvas()`, but usually, you will find functions on `Window` that avoid directly accessing the canvas.

在Fyne中，`Canvas`就是一块用来绘制APP的区域。每个窗口都会有一个`canvas`，可以用`Window.Canvas()`访问，但一般来说，你应该调用`Window`的方法，而不是直接操作`Canvas`

> Everything that can be drawn in Fyne is a type of `CanvasObject`. The example here opens a new window and then shows different types of primitive graphical elements by setting the content of the window canvas. There are many ways that each type of object can be customised, as shown with the text and circle examples.

`CanvasObject`就是Fyne中用来绘制一切的实例。下面的例子演示了如何打开一个新窗口并通过设置Window canvas来显示两个不同形状的元素。我们可以自定义很多组件/`CanvasObject`，下面所演示的是文本组件和圆圈组件

> As well as changing the content shown using `Canvas.SetContent()`, it is possible to change the properties of existing canvas objects. For example, you can change the `FillColor` of a rectangle and then call `rect.Refresh()` to update its appearance. When performing such updates from a goroutine, you should use the `fyne.Do` function to queue the updates safely on the main goroutine, ensuring thread safety as required since Fyne v2.6.0.

我们可以使用`Canvas.SetContent()`修改显示出来的组件内容，也可以直接修改已存在的canvas对象的属性。比如我们可以直接修改矩形元素的`FillColor`属性，然后调用`rect.Refresh()`更新它的外观。如果是在协程里执行这种更新，你应该使用`fyne.Do`函数，将更新事件放入队列中，并确保你的fyne版本高于2.6.0，因为fyne 2.6.0之后更新了其协程机制，带来了更好的线程安全

```go
package main  
  
import (  
    "image/color"  
    "log"    "time"  
    "fyne.io/fyne/v2"    "fyne.io/fyne/v2/app"    "fyne.io/fyne/v2/canvas")  
  
func main() {  
    // _ = os.Setenv("FYNE_THEME", "light")  
  
    myApp := app.New()  
    myWindow := myApp.NewWindow("Canvas")  
    myCanvas := myWindow.Canvas()  
  
    blue := color.NRGBA{R: 0, G: 0, B: 255, A: 255}  
    rect := canvas.NewRectangle(blue)  
    myCanvas.SetContent(rect)  
  
    go func() {  
       time.Sleep(time.Second)  
       green := color.NRGBA{R: 0, G: 255, B: 0, A: 255}  
       fyne.Do(func() {  
          rect.FillColor = green  
          rect.Refresh()  
       })  
    }()  
  
    myWindow.Resize(fyne.NewSize(300, 300))  
    myWindow.Show()  
    myApp.Run()  
  
    log.Printf("程序退出")  
}
```

![](assets/PixPin_2026-01-02_23-19-50.mp4)

我们还可以以同样方式绘制很多不同的元素，比如画个圆和一个文本：
```go
func setContentToText(c fyne.Canvas) {  
    green := color.NRGBA{R: 0, G: 255, B: 0, A: 255}  
    text := canvas.NewText("Hello World", green)  
    text.TextStyle.Bold = true  
    c.SetContent(text)  
}  
func setContentToCircle(c fyne.Canvas) {  
    red := color.NRGBA{R: 255, G: 0, B: 0, A: 255}  
    circle := canvas.NewCircle(color.White)  
    circle.StrokeWidth = 4  
    circle.StrokeColor = red  
    c.SetContent(circle)  
}
```
![](assets/PixPin_2026-01-02_23-26-31.mp4)

#### `Widget` 工具组件
> A `fyne.Widget` is a special type of canvas object that has interactive elements associated with it. In widgets, the logic is separate from the way that it looks (also called the `WidgetRenderer`).

`fyne.Widget`是一种特殊的Canvas对象，拥有可交互元素。wigets的渲染（`WidgetRender`）和事件逻辑是分离的

> Widgets are also types of `CanvasObject`, so we can set the content of our window to a single widget. See how we create a new `widget.Entry` and set it as the content of the window in this example.

Widgets也是一种`CanvasObject`，所以我们可以把窗口内容设置成单独一个Widget。下面的例子演示了如何创建一个新的文本输入框`Widget.Entry`并将其设为窗口的内容：
```go
package main  
  
import (  
    "log"  
  
    "fyne.io/fyne/v2"    "fyne.io/fyne/v2/app"    "fyne.io/fyne/v2/widget")  
  
func main() {  
    // _ = os.Setenv("FYNE_THEME", "light")  
  
    myApp := app.New()  
    myWindow := myApp.NewWindow("Demo")  
  
    myWindow.SetContent(widget.NewEntry())  
  
    myWindow.Resize(fyne.NewSize(300, 300))  
    myWindow.Show()  
    myApp.Run()  
  
    log.Printf("程序退出")  
}
```
![](assets/Pasted%20image%2020260102233517.png)

### 容器与布局
> In the previous example we saw how to set a `CanvasObject` to the content of a `Canvas`, but it is not very useful to only show one visual element. To show more than one item we use the `Container` type.

在前面的例子中我们了解到了如何将一个`CanvasObject`设置为画布区域`Canvas`的内容，但仅仅只显示一个可见元素是不够的。为了渲染更多元素，我们需要使用`Container`/容器 类型

> As the `fyne.Container` also is a `fyne.CanvasObject`, we can set it to be the content of a `fyne.Canvas`. In this example we create 3 text objects and then place them in a container using the `container.NewWithoutLayout()` function. As there is no layout set we can move the elements around like you see with `text2.Move()`.


***
# 页面底部