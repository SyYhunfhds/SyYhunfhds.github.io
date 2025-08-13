---
title: OTP Bypass：又一个不使用任何工具便发现的漏洞
category:
  - 搬运
  - Medium
  - Bypass
  - Bug-Bounty
tags:
  - 搬运
  - Medium
  - OTP
  - Infosec
  - Bug-Bounty
  - OTP-Bypass
  - Bug-Bounty-Tips
author: StrangeRwhite
footer: 版权及浏览收益为原作者所有，已获得转载和翻译授权。如侵犯版权，请通知译者尽快删除
date: 2025-05-15
---
:::important 版权信息
- **原作者**：StrangeRwhite
- [**原作者的Medium主页**](https://strangerwhite.medium.com/?source=post_page---byline--8b2c1013c3e7---------------------------------------)：[https://strangerwhite.medium.com/?source=post_page---byline--8b2c1013c3e7---------------------------------------](https://strangerwhite.medium.com/?source=post_page---byline--8b2c1013c3e7---------------------------------------)
- **原作者的Twitter主页**：[https://x.com/StrangeRwhite9?t=xdbpVbjrkxEW1TQSfK94jQ&s=09](https://x.com/StrangeRwhite9?t=xdbpVbjrkxEW1TQSfK94jQ&s=09)
- **原文标题及链接**：[Bypassing OTP Verification: Another Bug Found Without Any Tools!](https://strangerwhite.medium.com/bypassing-otp-verification-another-bug-found-without-any-tools-8b2c1013c3e7)
:::
:::important 转载授权 && 译文改动
本译文当前为第三版译文。已向原作者取得转载和翻译授权。

第三版译文相较第一版译文有如下改动：
- 移除了第一版译文中引用的来自Medium原文的图片
- 手动将link从授权部分的文本中移出，单独作为一个超链接
- 添加`date`属性，同步至原文发布时间
- 同步`tags`属性
:::
[[toc]]
## 前言
**欢迎来到我的漏洞赏金系列！** 🚀
**Welcome Back to My Bug Hunting Series!** 🚀
*我手测得越多，我越发现**挖掘漏洞并不需要那些花里胡哨的工具**。有时，你缺少的只是一双慧眼*
_The more I test manually, the more I realize that_ **_finding bugs doesn’t always require fancy tools_**_. Sometimes, all it takes is a_ **_careful look_** _at how things work._
如果你是白帽黑客新手，或者只是对漏洞挖掘有点好奇，这篇帖子将会带你领略一个冰冷的错误如何变成温暖的刀乐。让我们现在开始吧！
If you’re new to bug hunting or just curious about how these things work, this post will show you that even simple mistakes can lead to big vulnerabilities. Let’s get into the details!
这是我的***不使用任何工具挖掘漏洞***系列中的第二个漏洞。这一次，我意外发现了一个**OTP绕过漏洞** —— 但是这不重要，重要的是……**我拿到了赏金！** 💰🎉
This is the second bug in my series on **_finding bugs without using any tools._** This time, I accidentally discovered an **OTP bypass** — but hey, that doesn’t matter! What really matters is… **I got a bounty for it!** 💰🎉

:::tip 译者注 Gemini生成
根据**生成和传递方式**的不同，OTP主要可以分为以下几类：
1. **基于时间同步的OTP (TOTP - Time-based One-Time Password)**
    - **如何工作**: 客户端（如Google Authenticator App, Authy）和服务器共享一个**密钥（Secret Key）**和一个**时间戳**。它们使用同一个算法（通常是HMAC-SHA1），将密钥和当前时间（通常以30秒为一个窗口）进行计算，生成一个**相同的6位数字**。
    - **常见情景**:
        - **双因素认证 (2FA)**: 登录网站、VPN、服务器SSH时，在输入密码后，需要再输入App上显示的这个动态验证码。这是**最安全**的OTP形式。
        - **交易确认**: 在进行敏感操作（如大额转账）时，需要输入动态口令进行最终确认。
    - **优点**: 不依赖外部通信，即使手机没有信号也能生成。
2. **基于短信/邮件的OTP (SMS/Email-based OTP)**
    - **如何工作**: 服务器生成一个随机的、有有效期的验证码，然后通过短信或邮件，发送到用户预先绑定的手机或邮箱里。
    - **常见情景**:
        - **用户注册/身份验证**: 验证用户是否是这个手机号/邮箱的真实主人。
        - **密码重置**: 验证身份，允许用户重置忘记的密码。
        - **快捷登录**: 在不输入密码的情况下，仅通过手机验证码登录。
        - **支付确认**: 电商网站在支付时发送的确认码。
    - **优点**: 用户体验极其方便，几乎没有使用门槛。
    - **缺点**: 安全性相对较低，可能被短信劫持、SIM卡交换攻击等方式拦截。
3. **基于事件/计数器的OTP (HOTP - HMAC-based One-Time Password)**
    - **如何工作**: 客户端和服务器共享一个密钥和一个**计数器**。每当用户请求一个新的验证码时，计数器加一，然后用密钥和新的计数值生成一个OTP。
    - **常见情景**: 比较少见，主要用于一些硬件令牌（Hardware Token）中。
    - **优点**: 不受时间同步问题的影响。

这篇文章里的漏洞，即是**第二类（基于短信/邮件的OTP）**中最典型的一种逻辑缺陷**
:::
## 正文

### 网站功能杂谈
这个网站看上去和其他网站没什么两样，注册时都需要**校验OTP**以确认邮箱。但有一点不一样的是，我注意到**OTP只在注册期间使用**，而“忘记密码”功能则是直接返回**重置链接**的
This website works just like any other site that requires **OTP verification** for signup to confirm your email. This one does too — but with a twist. I noticed that **OTP is only used during registration**, while the “Forgot Password” feature sends a **reset link instead**.
如果这个网站在重置密码时也用到了OTP，那么这个漏洞会**更严重**。但尽管如此，这个漏洞目前就足够严重了！🚨
If the website also used an OTP for password resets, this bug would be **way more critical**. But even as it is, it’s still a pretty serious issue! 🚨
### 漏洞🐞复现

1. **Go to the Sign-Up Page:**  
	1.**前往注册页面**
	注册页面位于 👉 `hxxps://website.com/signup/.`
    Visit the registration page at 👉 hxxps://website.com/signup/.
2. **Enter Your Details:**  
	2. **输入你的详细个人信息：**
	填写你的邮箱（比如`myemail@gmail.com`）然后点击**Sign Up**按钮
    Fill in the form with your email (e.g., `myemail@gmail.com`) and click the **Sign Up** button.
3. **OTP Verification Page Appears:**  
	3. **出现邮箱验证码校验页面：**
	你的邮箱会受到一个验证码。**但不要立即使用这个验证码！** 请点击**Back**按钮
    A code will be sent to your email. **Do not use this code!** Instead, press the **Back** button.
4.  **Re-enter Details with Victim’s Email:**  
	4. **这一次输入受害者的邮箱：**
    返回注册页面并再次填写信息，但这一次使用受害者的邮箱（比如`victim@gmail.com`）
	Go back to the Sign-Up page and fill in the form again, but this time use the victim’s email (e.g., `victim@gmail.com`).
5. **Click Sign Up Again:**  
    5. **再次点击Sign Up按钮**
    要求输入邮箱验证码时，把你刚才收到的你自己邮箱（比如`myemail@gmail.com`）的验证码输入进去
    When prompted for the OTP, enter the code sent to your email (`myemail@gmail.com`).
6. **Account Created Successfully:**  
    6. **成功创建账户**
    网站确认了验证码，使用受害者的邮箱成功创建了一个账户
    The website accepts the code, and the account is successfully created using the victim’s email (`victim@gmail.com`).

### BUG是如何工作的
这一问题究其根源在于网站是如何校验邮箱的。网站并非强制绑定邮箱验证码和对应的邮箱，而是会接受**任意有效的验证码** —— 即使是不同邮箱收到的验证码！这一错误配置导致了邮箱认证Bypass
The issue lies in how the website verifies email addresses. Instead of tying the OTP to the specific email entered during registration, the system accepts **any valid OTP** — even one from a different email! This misconfiguration makes it possible to bypass email verification.

## 结语
这是我**不使用任何工具**发现的第二个漏洞 —— 只需要细致的手动测试！挖掘安全漏洞并不总是需要哪些花里胡哨的工具；有时，细心的观察便足以揭示严重的漏洞。
This was another bug I found **without using any tools** — just careful manual testing! Finding security flaws doesn’t always require fancy software; sometimes, simply observing how a system behaves can reveal critical vulnerabilities.
更阴的地方是，我还得到了**赏金**！💰🎉
And the best part? I got a **bounty** for this! 💰🎉
👀请关注我的**无工具漏洞挖掘** WP
👀 Stay tuned for more **“No-Tool Bug Bounty”** write-ups!  
有问题想问？请联系我的邮箱：`strangerwhite9@gmail.com`或者直接在评论区留下你的回复
Got questions? Email me: `strangerwhite9@gmail.com` or drop a comment below
***StrangeRwhite*撰写 | 系列：*不使用工具挖掘漏洞***
**by _StrangeRwhite_ | Series: _Finding Bugs Without Tools_**