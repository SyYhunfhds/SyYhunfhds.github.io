---
title: 我挖到了一个价值3500美金的Git目录泄露漏洞 - 五分钟的渗透测试如何促成我目前以来赏金最高的漏洞
author: Ibtissam hammadi
footer: 版权及浏览收益为原作者所有。如侵犯版权，请通知译者尽快删除
date: 2025-08-11
category:
  - 搬运
  - Bug-Bounty
  - Medium
tags:
  - Medium
  - 搬运
  - Bug-Bounty
  - Git目录泄露
---
:::info
- **原作者**：**Ibtissam hammadi**
- **原作者个人主页**：[https://medium.com/@ibtissamhammadi1](https://medium.com/@ibtissamhammadi1)
- **原文标题**：**I Found $3,500 in a Public Git Config**
- **原文副标题**：Here’s how a 5-minute check turned into my biggest bug bounty yet.
- **原文链接**：[https://medium.com/@ibtissamhammadi1/i-found-3-500-in-a-public-git-config-3b9fc5e47c4b](https://medium.com/@ibtissamhammadi1/i-found-3-500-in-a-public-git-config-3b9fc5e47c4b)
:::
:::important
原文为**Member Only**会员制博文
:::
[[toc]]
## 前言
这原本不是一次渗透测试，甚至不是计划好的。但一点小小的习惯还是促成了我发现暴露的`/.git/config`文件
It wasn’t a hack. It wasn’t even planned. But when a simple habit led me to an exposed `/.git/config` file.
48小时后，**我的Paypal账户收到了3500美元的赏金**。这一切都源自一个本不应该被访问的**暴露在公网上的Git配置**
48 hours later, **$3,500 landed in my PayPal**. All because of a **public Git config** that shouldn’t have been accessible.
本贴将详细介绍漏洞挖掘过程 —— 以及你可以如何发现同样的**金矿**（当然，别干坏事）
Here’s exactly how it happened — and how you could spot the same **goldmine** (ethically, of course).

## 正文
### 一个意外的发现
在测试一个网站时（ 归属于*合法的* 漏洞赏金项目），对`/.git/config`的例行扫描得到了一条意料之外的响应：页面弹出了一个文件下载窗口
While testing a website (_legally_, under a bug bounty program), a routine check for `/.git/config` returned something unexpected: the file downloaded instantly.

> **如果`config`都暴露了，那么还有什么会暴露出来呢？**
> **“If this is exposed, what else is?”**

一个**暴露在公网的`/.git/config`** 通常意味着这**整个仓库**都是可以访问的 —— **源代码**，**API密钥**，**口令**，**亦或是内部工具**。这不只是一个**Git不安全配置的失误**；这还是一个任何人可以查看的**藏宝箱**
A **public Git config** often means the **entire repository** is accessible — **source code, API keys, passwords, even internal tools**. This wasn’t just a **Git security mistake**; it was a **treasure chest** for anyone who looked.

### 连点成线
使用`git-dumper`工具在几分钟内将整个仓库都dump了下拉：
With one tool (`git-dumper`), the entire repository was pulled in minutes:

```shell
git-dumper https://example.com/.git/ ./leaked-code
```

文件列表中，明晃晃地露出了很多**敏感数据**
Inside, **sensitive data** was sitting in plain sight:

- **Database credentials** (yes, _production_ ones).
	- *生产环境* 的**数据库凭据**
- **Cloud API keys** (full access).
	- **云服务API密钥** （全权限）
- **Internal admin dashboards** (no authentication required).
	- **内部admin面板** （不需要身份验证）

这绝非一次**简单的泄露** —— 这是一次**重大信息泄露**。这家公司的整个后端都有可能受到损害
This wasn’t just a **minor leak** — it was a **critical exposure**. The company’s entire backend could’ve been compromised.

### 白帽黑客漏洞报告：从漏洞发现到赏金支付
我是在**HackerOne**（支付信誉有良好保障）上提交的报告。漏洞提交和验证流程是这样的：
The report was submitted through **HackerOne** (name-dropping for credibility). Here’s why it worked:

1. **Evidence-packed**: Screenshots, commands used, and impact explained _without fluff_.
	1. **打包漏洞证据**：截图，用到的指令，以及*不拖泥带水的* 漏洞危害分析
2. **Fast triage**: Submitted at 2 PM, acknowledged by 5 PM.
	2. **超快回复**：报告是下午两点提交的，确认回复是下午五点前收到的
3. **Swift reward**: Paid **$3,500** the next morning — **one of the easiest bug bounty rewards** I’d ever earned.
	3. **豪爽的报酬**：第二天早上我便收到了**3500美元**的赏金 —— 我迄今为止得到的**最不费力气的漏洞赏金之一**

报告的核心在于**明晰漏洞细节和修复紧迫程度**。没有一个公司想看到它的`Git`仓库满天飞
The key? **Clarity and urgency**. No company wants its **exposed Git repo** floating around.

### 漏洞修复：如何赶走这个梦魇

#### 对于开发者：

- Never deploy `.git/` to production. Use `--dissociate` or `git archive` for deployments.
	- 切记不要将`.git/`提交到生产分支，使用`--dissociate`或`git archive`进行部署
- Audit `.gitignore`—ensure sensitive files (_configs, keys, envs_) are excluded.
	- 监听 `.gitignore` —— 确保敏感文件（*配置文件，密钥文件，环境变量配置*）没有被Git追踪修改
- Scan with `git-secrets` (AWS’s tool) to prevent accidental commits.
	- 使用AWS的工具`git-secret`拦截意外提交

#### 对于渗透测试人员

- Always check `/.git/config` during recon—low effort, high reward.
	- 在信息搜集阶段切记要检查`/.git/config` —— 低成本高回报
- Use `git-dumper` or `GoBuster` to confirm exposure.
	- 使用 `git-dumper`或`GoBuster`确认Git目录泄露漏洞
**耗时5分钟的检查**可以为一家公司省下数百万美元的安全成本 —— 亦或是变成**你手中温暖的美刀**
A **5-minute check** could save a company millions — or put **thousands in your pocket**.

### 事件后续 && 你可以如何复制我的成功
我的PayPal账户收到了**3500美元的赏金**，我不禁思考起来：
The moment the **$3,500 payout** hit my PayPal, two thoughts crossed my mind:

1. _“This was way too easy.”_
	1. *"这实在是太容易了"*
2. _“Why aren’t more people checking for this?”_
	2. *"为什么这么多人都没有注意到这个问题"*
显然，**Git目录泄露漏洞**远比你想得要常见得多。**你甚至不需要先成为一位专业的渗透测试人员才能发现这一漏洞**
Turns out, **exposed Git repos** are more common than you’d think. And the best part? **You don’t need to be a cybersecurity expert to find them.**
## 思考
### 为什么这种漏洞随处可见 && 如何修复Git目录泄露漏洞
很多开发者都不会意识到他们把`.git`文件夹部署到了生产环境中。以下是两种可能导致这一现象的因素：
Most developers don’t realize they’ve deployed their `.git` folder to production. It happens in two ways:

1. Manual Deployment Mistakes — Someone zips the project folder and uploads it, forgetting `.git` contains sensitive history.
	1. 手动部署时的失误 —— 有时开发者是直接打包压缩项目文件夹并上传的，从而忽略了`.git`会包含敏感历史的事实
2. Misconfigured Servers — The server isn’t blocking access to `.git`, so anyone can download it.
	2. 服务器错误配置 —— 服务器没有拦截对`.git`的访问，于是所有人都可以下载它

#### 如何在60秒内测试这一漏洞
你只需要一个浏览器或者`cURL`指令，然后尝试下面的渗透方式
All you need is a browser or `curl`. Try this:

**浏览器打开或使用`curl`访问：**
```plain
https://example.com/.git/config  
```
如果浏览器弹出了下载窗口（而不是返回404页面），**那么这便是Git目录泄露漏洞了**
If it downloads (instead of a 404), **you’ve hit gold**.

**自动化测试**
```shell
git-dumper https://example.com/.git/ output-folder  
```
如果这样能行，那么你会在输出文件夹看到下载好的**整个Git仓库**
If it works, **the entire repo is exposed**.

### 你会发现什么 && 受害公司在害怕什么
**泄露的Git仓库**不仅仅只有一堆源代码 —— 同时也存着**一揽子商业机密**
An **exposed Git repo** isn’t just about source code — it’s a **treasure trove of secrets**:

- `.env` files – Database passwords, API keys, encryption secrets.
	- `.env`文件 —— 数据库口令，API密钥，加密数据
- `config/` directories – Server credentials, third-party integrations.
	- `config/` 目录 —— 服务器凭据，第三方插件
- **Internal documentation** — Sometimes, even **employee emails** and **admin panel links**.
	- **内部文档** —— 有时，甚至还会有**员工邮箱**和**管理面板链接**
*等会儿？*，你可能会问，*这不是违法收集数据吗？*
_“But wait,”_ you might think, _“isn’t this illegal?”_
**只要你好好写报告，当然不会违法**
**Not if you report it ethically.**

### 如何正确地撰写报告 && 怎么样做能更快收到酬金

**第一步：整理漏洞证据**

- Screenshots of the exposed `.git/config`.
	- 暴露的`.git/config`的截图
- Proof of data leakage (e.g., `db_password = xyz` from dumped files).
	- 数据泄露的生证据（比如从导出的文件中得到的`db_password = xyz`）
- **Impact explanation** — _“An attacker could have taken full control of the database.”_
	- **漏洞危害分析** —— *"攻击者可以借此获得对数据库的全权控制 "*

**第二步：在漏洞赏金平台上提交你的报告**

- [**HackerOne**](https://www.hackerone.com/) / [**Bugcrowd**](https://www.bugcrowd.com/) (用于赏金支付).

**第三步：礼貌地要求回复**
很多公司都会**火急火燎**地迅速着手修复漏洞。如果目标公司没有在48小时内回应，请礼貌地询问他们 *"我就想知道漏洞报告有没有得到确认"*，这样能让情况好很多
Most companies **freak out** and fix this fast. If they don’t respond in 48 hours, a polite _“Just checking if this was reviewed?”_ works wonders.

### 接下来可能会发生什么
在搜索信息的同时，我还发现**其他三家公司**也存在同样的问题，其中一家甚至泄露出：
While researching, I found **three other companies** with the same issue. One had:

- **AWS keys** with full admin access.
	- 管理员权限的**AWS密钥**
- **Stripe API keys** (meaning attackers could steal payments).
	- **Stripe API密钥**（意味着攻击者可以窃取支付信息）
- **Employee VPN credentials** (full internal network access).
	- **员工的VPN账号** （可以完全访问内部网络）
这一切都与一个错误配置的`.git`目录脱不了干系
All because of one misconfigured `.git` folder.
这家公司支付了**5000美元**作为报酬
The company paid **$5,000** for that report.

### 开发者应该如何避免这一漏洞
如果你是开发者，**请立刻做下面的事情**：
If you’re a developer, **do this NOW**:

1. Never deploy `.git/` – Use `git archive` or CI/CD tools that exclude it.
	1. 永远不要上传`.git/`目录 —— 使用`git archive`（只导出不含`.git`目录的干净代码）或使用能够排除`.git/`目录的CI/CD工具（CI/CD流程中明确地删除`.git`目录）
2. Add `.git` to server blacklists – In Nginx/Apache, block access to `.git`.
	1. 将`.git`添加至服务器黑名单 —— 在Nginx/Apache中拦截对`.git`的访问
3. **Scan before deploying** — Run:
	1. **部署项目前扫描一下** —— 运行：
	```
	grep -r "password" .git/  
	```
（没错，确实会有人**在提交代码时硬编码口令**）
(Yes, some people **hardcode passwords in commits**.)
## 鼓励
### 为什么你应该现在就开始检查
这不只是为了赚取**漏洞赏金** —— 也是为了**让互联网更安全**
This isn’t just about **bug bounty rewards** — it’s about **making the web safer**.

- **For testers**: A **5-minute check** could be your next payout.
	- **对于渗透测试人员**：一次**5分钟的检查**就能成为你的下一份赏金
- **For devs**: A **10-second config change** could save your company.
	- **对于开发者**：一次**10秒钟的配置更改**能为你省下一大笔钱
*你会现在就开始对`.git/config`的检查吗？* （是的 / 才怪 / 也许吧）
_Would you check a site’s_ `_.git/config_` _right now?_ (Yes / No / Maybe)
**收下这篇指南吧 **。下次当你在浏览网站时就请试试吧 —— 你可能距离丰厚的赏金只有**一步之遥**
**Bookmark this guide.** The next time you’re browsing, try it — you might be **one URL away** from a big payout.