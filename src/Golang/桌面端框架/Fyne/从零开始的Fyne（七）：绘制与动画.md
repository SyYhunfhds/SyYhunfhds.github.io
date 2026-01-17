---
title: 从零开始的Fyne（七）：绘制与动画、容器、组件、收纳样式（没意思）
date: 2026-01-13
---
[[toc]]
## 绘制与动画
### 矩形/Rectangle
> `canvas.Rectangle` is the simplest canvas object in Fyne. It displays a block of the specified colour. You can also set the colour using the `FillColor` field.

> In this example the rectangle fills the window as it is the only content element.

```go
package main

import (
	"image/color"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
)

func main() {
	myApp := app.New()
	w := myApp.NewWindow("Rectangle")

	rect := canvas.NewRectangle(color.White)
	w.SetContent(rect)

	w.Resize(fyne.NewSize(150, 100))
	w.ShowAndRun()
}
```

> Other `fyne.CanvasObject` types have more configuration, let us look [next](https://docs.fyne.io/canvas/text/) at `canvas.Text`.
### 文本/Text
> `canvas.Text` is used for all text rendering within Fyne. It is created by specifying the text and colour for the text. Text is rendered using the default font, specified by the current theme.

> The text object allows certain configuration like the `Alignment` and `TextStyle` field. as illustrated in the example here. To use a monospaced font instead you can specify `fyne.TextStyle{Monospace: true}`.

```go
package main

import (
	"image/color"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
)

func main() {
	myApp := app.New()
	w := myApp.NewWindow("Text")

	text := canvas.NewText("Text Object", color.White)
	text.Alignment = fyne.TextAlignTrailing
	text.TextStyle = fyne.TextStyle{Italic: true}
	w.SetContent(text)

	w.ShowAndRun()
}
```

> It is possible to use an alternative font by specifying a `FYNE_FONT` environment variable. Use this to set a `.ttf` file to use instead of the one provided in the Fyne toolkit or the current theme.


***
#  页面底部