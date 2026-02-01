---
title: 从零开始的Business Form插件探索
date: 2026-01-24
---
[[toc]]
***
## 表单
### `Update Request`：更新数据
1. 在**Add Visualization**的右侧插件列表里找到**Business Form**
	![](assets/Pasted%20image%2020260125110411.png)
2. **设置elem属性**
	如下可以创建一个文本输入框
	![](assets/Pasted%20image%2020260125110728.png)
	如法炮制创建一个`Select`下拉列表，ID为`priority`，Label为`优先级`；并在`Options`菜单中添加`Low`、`Medium`和`High`选项。
	![](assets/Pasted%20image%2020260125111007.png)
3. **添加API接口**
	找到**Update Request**选项卡，先选择REST系列请求方法
	(由于请求是由浏览器发起的，所以应该直接用`localhost`作为域名)
	
	![](assets/Pasted%20image%2020260125111554.png)
	**Update Request Payload**中默认选择**All Elements**，即自动打包整个Panel的字段，例如打包成这样：
	```json
		{
	  "announcement": "用户输入的内容",
	  "priority": "High"
	}
	```
	![](assets/Pasted%20image%2020260125111837.png)
4. 写一个后端服务去对接看看
	```go
		func initAPI(rg *gin.RouterGroup) {
			rg.POST("/submit-announcement", func(ctx *gin.Context) {
				var req announcementDTO
				if err := ctx.ShouldBindJSON(&req); err != nil {
					if errors.Is(err, io.ErrUnexpectedEOF) {
						ctx.JSON(400, gin.H{
							"msg": "empty json body",
						})
						return
					}
					ctx.JSON(400, gin.H{
						"msg": err.Error(),
					})
					return
				}
		
				log.Printf("req: %+v", req)
				ctx.JSON(200, gin.H{
					"msg": "success",
				})
			})
	}
	```
	![](assets/Pasted%20image%2020260125113554.png)
5. **API响应处理** 
	在这里自定义响应逻辑![](assets/Pasted%20image%2020260125130013.png)
	```go
	resp = context.panel.response
	console.log(resp)
	if (resp && resp.status === 200) {
	  context.grafana.notifySuccess(['Update', 'Values updated successfully.']);
	  context.grafana.refresh();
	} else {
	  context.grafana.notifyError(['Update', 'An error occurred updating values.']);
	}
	```
	![](assets/Pasted%20image%2020260125164248.png)
	记得启用CORS
6. 如果解不开response的话……
	```js
	// 1. 获取响应对象
	const response = context.panel.response;
	
	// 检查 response 是否有效并包含 json 方法
	if (response && typeof response.json === 'function') {
	
	  // 2. 手动解析流（Promise 方式）
	  response.json().then(function (result) {
	    console.log('后端返回的数据解析成功:', result);
	
	    // 3. 根据你后端的 JSON 结构进行判断
	    // 你后端的回显是 {"status":200,"message":"success",...}
	    if (result.status === 200 || result.message === "success") {
	      context.grafana.notifySuccess(['提交成功', `后端已收到消息并回显: ${result.message}`]);
	      context.grafana.refresh(); // 刷新数据源
	    } else {
	      context.grafana.notifyError(['业务报错', result.message || '未知错误']);
	    }
	
	  }).catch(function (err) {
	    console.error('JSON 解析失败:', err);
	    context.grafana.notifyError(['解析错误', '后端返回的不是标准 JSON 格式']);
	  });
	
	} else {
	  // 如果走到这里，说明请求根本没发出去，或者返回的对象不是 Fetch Response
	  console.error('无效的响应对象:', response);
	  context.grafana.notifyError(['请求异常', '未获取到后端响应，请检查网络或 CORS']);
	}
	```

:::note
在标准的后端开发中，库（如 axios 或 requests）会自动帮你把 Body 解析好。但在 Grafana 面板的这个特定钩子函数里：

- 它是基于浏览器原生的 fetch 实现的。
    
- fetch 的特性就是：`response` 返回时，Body 还是一个流（`Stream`），必须显式调用 `.json()` 或 `.text()` 才能拿到内容。
    
- 由于插件的沙盒环境限制，不支持顶层 `await`，所以必须用` .then()`。
:::
### `Initial Request`：在页面初始化后加载数据
![](assets/Pasted%20image%2020260125172434.png)
数据来源通常有三种做法：
- **REST API**: 直接调用后端接口。
- **Data Source**: 调用 Grafana 配置好的数据源（如 MySQL 里的某行记录）。
- **Query**: 直接绑定到左侧面板里写的 Query 查询结果。
对于这样的响应：
```json
{
  "announcement": "欢迎来到监控系统",
  "priority": "High"
}
```
- **只要 Element ID 和 JSON 里的 Key 完全一致**，插件会自动把 `欢迎来到监控系统 `填入 ID 为 `announcement` 的输入框中。
- 无需写一行代码，这是“约定大于配置”。

![](assets/Pasted%20image%2020260125173409.png)
不过Grafana的这个插件默认只会在根部搜索json key。本着能用就行的心态，我不得不放弃多包一层业务状态码的想法

:::note 动态初始化（结合 Dashboard 变量）

作为后端，你肯定会遇到：**“我要根据不同的服务器 ID 显示不同的配置”**。

1. 在 Grafana 顶部创建一个变量 `server_id`。
    
2. 在 Initial Request 的 URL 里使用它：  
    `http://your-backend/config?id=${server_id}`
    
3. 当你切换顶部的变量时，表单会自动重新发起 GET 请求，刷新显示的内容。
:::


## 草稿

### 第一阶段：环境搭建与“只写”基础 (基础篇)
**目标：** 让 Grafana 能够向你的后端发送数据。

1.  **环境准备**：
    *   安装 Grafana 环境。
    *   安装 `volkovlabs-form-panel` (Business Forms) 和 `volkovlabs-text-panel` (Business Text)。
2.  **创建第一个表单**：
    *   学习添加 `Input` (String)、`Textarea` 和 `Button`。
    *   **重点学习**：`Update Request` 配置。
    *   **后端练习**：写一个简单的 API (Node.js/Python/Go)，接收表单的 POST 请求并打印 JSON 日志。
3.  **理解变量绑定**：
    *   学习如何将 Grafana 的 `Dashboard Variables` (变量) 作为表单的默认值。

### 第二阶段：数据闭环与状态同步 (进阶篇)
**目标：** 实现“提交 -> 后端处理 -> 页面自动更新”的闭环。

1.  **初始化请求 (Initial Request)**：
    *   学习如何从后端 API 获取数据并自动填充到表单中。
2.  **Post-processing 脚本**：
    *   学习在表单提交成功后编写 JavaScript。
    *   **核心技能**：使用 `context.grafana.refresh()` 触发数据源刷新。
    *   **核心技能**：使用 `context.grafana.notify('success', ...)` 弹出操作提示。
3.  **多面板联动**：
    *   练习：在 A 面板提交表单修改数据库，让 B 面板（普通表格）自动更新显示新数据。

### 第三阶段：动态 UI 与高级逻辑 (逻辑篇)
**目标：** 让表单具备逻辑判断能力，不再是静态表单。

1.  **条件渲染 (Disable/Hide)**：
    *   学习编写简单的 JS 逻辑：例如当 `Select` 下拉框选择“高级”时，才显示某些输入框。
2.  **数据转换 (Payload Transformation)**：
    *   学习在发送 API 之前，用 JavaScript 重新格式化 JSON Payload。
3.  **文件处理**：
    *   学习使用 Business Forms 的 `File` 元素，尝试通过 Grafana 向后端上传配置文件。

### 第四阶段：大模型对话窗口实战 (实战篇)
**目标：** 也就是你最终想要的目标，在 Grafana 里做一个聊天窗口。

1.  **Business Text 的渲染力**：
    *   学习使用 Handlebars 语法渲染数据库里的对话记录。
    *   练习：如何让不同的角色（User/Assistant）显示不同的气泡样式。
2.  **模拟流式体验**：
    *   虽然 Grafana 本质是拉取数据，但你可以通过设置较低的刷新频率（或手动刷新）来模拟对话感。
3.  **Context (上下文) 管理**：
    *   学习如何把 `SessionID` 存在 Grafana 变量里，确保每次发给后端的 Prompt 都带上当前会话 ID。

### 第五阶段：安全性与生产化 (架构篇)
**目标：** 让你的“另类前端”能够上线给别人用。

1.  **权限控制**：
    *   学习根据 Grafana 的用户角色（Admin/Editor/Viewer）动态禁用提交按钮。
2.  **API 认证**：
    *   学习在 Form Panel 的请求头中注入 Authorization 令牌。
3.  **部署优化**：
    *   学习如何利用 Grafana 的容器化特性，将你的后端服务与 Grafana 一起打包。

---


***
# 页面底部