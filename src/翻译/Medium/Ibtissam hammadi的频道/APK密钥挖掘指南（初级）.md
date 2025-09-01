---
title: 我使用grep字符串提取指令挖到了一个价值3330美元的漏洞
category:
  - 搬运
  - Bug-Bounty
  - Medium
tags:
  - 搬运
  - Medium
  - APK反编译
  - API泄露
author: Ibtissam hammadi
footer: 版权及浏览收益为原作者所有。如侵犯版权，请通知译者尽快删除
---
:::info
- **原作者**：**Ibtissam hammadi**
- **原作者个人主页**：[https://medium.com/@ibtissamhammadi1](https://medium.com/@ibtissamhammadi1)
- **原文标题**：**I Found a $3,330 Bug Using Extract Grep Curl**
- **原文副标题**：A step-by-step guide to uncovering hidden vulnerabilities (ethically!) with common command-line tools.
- **原文链接**：[https://medium.com/@ibtissamhammadi1/i-found-50-xss-flaws-using-just-my-browser-a00caba76c48](https://medium.com/@ibtissamhammadi1/i-found-50-xss-flaws-using-just-my-browser-a00caba76c48)
:::
:::important
原文为**Member Only**会员制博文
:::
[[toc]]
## 前言
这原本只是一次例行测试。某公司提交了一个安卓客户端APP用于安全审计，对方也没什么要求——只想要赶紧进行一次快速扫描然后签出

然后，**三行命令**下来，一切都变了

APP反编译代码中出现了一个突兀的**API Key**。不只是一个密钥，而是一个以最高权限访问云存储桶中所有敏感用户信息的密钥。赏金漏洞平台给出了**3330美元**的赏金

最疯狂的地方在于，**我没有使用昂贵的工具**，只用了**三个指令**：`Extract`、`Grep`和`cURL`

如果你也有过从事要求深度挖掘或misc技巧的赏金挖掘的想法，这篇指南会证明你是正确的

## 步骤
### 第一步：`Extract` —— 深入探寻APP的密钥
移动应用程序（ *Mobile apps*）（ 安卓、IOS乃至是Electron架构的桌面程序）通常将**Secrets**藏在它们附带的文件中。开发者有时在发布release之前忘了删除API密钥、数据库凭据，乃至是云存储桶的token

#### 这是怎么做到的
对于安卓系统，其应用程序（APK）可使用`apktool`这款免费的反编译工具提取出`jar`包和XML资源文件

```shell
apktool d target_app.apk -o output_folder
```

`apktool`会解包APK，提取XML文件和已编译的字节码——最重要的是——其中的源代码文件有时可能暗藏玄坤（密钥）

对于IOS或Electorn APP，请使用`class-dump`（IOS）或`asar`（ Electron架构）进行反编译和资源文件提取

#### 关键点
大多数APP都不会合理加密内部字符串。如果一个开发者硬编码了一串密码或一个API密钥，你肯定会在明文里看到它

### 第二步：解锁3330美元的正则匹配模式
提取出APK的内容后，下一步便是搜索高价值的字符串，这时候就该`grep`，一个CLI搜索工具出场了

执行下面这样一个简单的扫描：
```
grep -rE 'api_key|AKIA|ghp_|Bearer' output_folder/
```
- `-r`：正则匹配模式
- `-E`：拓展正则语法
用于提取APK资源文件中的**AWS密钥(`AKIA`)**、**Github Tokens(`ghp_`)**  和**通用API密钥**

#### 请签收您的密钥
一个名为`config.json`的文件出现了下面的字符串：
```json
{    
  "database_url": "mongodb://user:password@cluster0.example.com",    
  "aws_key": "AKIAXXXXXXXXXXXXXXXX"    
}
```
明晃晃一个`AWS key`

#### 为什么这个方法如此有效
开发者常常会忘记或忽略下面这些风险：
- 配置文件中**硬编码的凭据**
- **不小心提交到代码仓库**的密钥
- 生产环境打包时带上的**调试用token**
简简单单一个`grep`指令就可以把它们全部找出来

### 第三步 `Curl` —— 证明这是一个有效的BUG
找到密钥是一回事，证明密钥能用是另一回事。这时候就需要`curl`上场了
Finding a key is one thing. Proving it’s a real vulnerability? That’s where `curl` came in.
让我们快速测试一下这个AWS密钥能不能用
A quick test was run to see if the AWS key was valid:

```shell
curl -H "Authorization: AWS AKIAXXXXXXXXXXXXXXXX" https://s3.amazonaws.com/mybucket/
```

`cURL`收到了**一个长长的文件列表**，这意味着这个AWS密钥**可以读取S3桶中的所有数据**
The server **responded with a full list of files**, meaning the key had **full read access** to an S3 bucket.

#### **道德困境 (如何避免纠纷)**
到这一步，我们已经证明了这是一个**严重漏洞**。但从白帽黑客的角度来看，**密钥有用不等于有渗透价值**
At this point, **serious damage could have been done.** But in ethical hacking, **verification ≠ and exploitation.**
不要将文件应用于非法用途，但你可以通过下面的步骤进行进一步校验：
Instead of accessing files, the next steps were:

1. **Checking permissions** (Was the key read-only or full admin?)
	**检查密钥的权限**（是只能读取还是说有管理员权限）
2. **Documenting the issue** (Screenshots, minimal proof)
	**整理你的发现**（截图，最小化验证）
3. **Reporting responsibly** (No data stolen, no unnecessary access)
	**负责任地报告**（不要窃取数据，不要进行不必要的访问）

最终，客户收到了报告，撤销了密钥，并支付了漏洞赏金
The client was notified, the key was revoked, and the bounty was paid.

## 学到的教训（以及如何避免犯错）

**1. 差点与BUG擦肩而过 Almost Missing the Bug**
第一次扫描由于匹配模式有限，因此几乎是失败的。将Slack令牌、Firebase链接和Azure密钥也囊括到`grep`的正则匹配模式中，也许会带来些惊喜
The first scan almost failed because only default patterns were used. Expanding the `grep` search to include Slack tokens, Firebase URLs, and Azure keys made all the difference.

**2. 为什么有些BUG看起来不太好发现呢 Why Some Bugs Go Unnoticed**
很多黑壳都**只关注SQL注入漏洞或XSS漏洞**，而忽视了**低垂的果实**（比如暴露的密钥）。**趁手的工具 + 持之以恒 = 值当的回报**
Many hackers **only look for SQLi or XSS**, ignoring **low-hanging fruit** like exposed keys. **Simple tools + persistence = high rewards.**

**3. 白帽黑客的责任 The Ethical Responsibility**

- **Never access real user data** (even if the key allows it).
	- **不要访问真实用户的数据**（即使密钥有这样的权限）
- **Report through proper channels** ([**HackerOne**](https://www.hackerone.com/), [**Bugcrowd**](http://bugcrowd.com/), or direct contact).
	- **向合法平台提交报告**（[**HackerOne**](https://www.hackerone.com/), [**Bugcrowd**](http://bugcrowd.com/), 或是直接与开发商沟通）
- **Don’t demand payment** — some companies reward honesty without negotiation.
	- **不要坐地起价** —— 一些公司会诚实地给予报酬，不需要专门协商

## 你也来试试吧！（安全地）
你也想自己试试吗？下面一个**安全的挑战**：
Want to test this yourself? Here’s a **safe challenge**:

1. **Download an open-source app** (e.g., from GitHub).
	**下载一个开源的app**（比如从Github上下一个）
2. Run `apktool` and `grep` to see if any test keys are left inside.
	运行`apktool`并`grep`提取出可能的密钥

**如果这篇博文能够帮到你，那么请给我一个赞!** 每周我都会更新赏金漏洞挖掘分析 —— **关注我跟踪实战漏洞挖掘**
**Clap if this helped you!** More bug bounty breakdowns drop weekly — **follow for real-world case studies.**