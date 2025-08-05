---
title: 我只用浏览器就发现了五十多个XSS漏洞 谷歌浏览器的一些技巧如何用于漏洞挖掘
category:
  - 搬运
  - 红队
  - 脚本小子
  - AI+
  - Medium
  - Bug-Bounty
tags:
  - 搬运
  - 红队
date: 2025-08-05
author: Ibtissam hammadi
footer: 版权及浏览收益为原作者所有。如侵犯版权，请通知译者尽快删除
---
:::info
- **原作者**：**Ibtissam hammadi**
- **原作者个人主页**：[https://medium.com/@ibtissamhammadi1](https://medium.com/@ibtissamhammadi1)
- **原文标题**：**I Found 50+ XSS Flaws Using Just My Browser**
- **原文链接**：[https://medium.com/@ibtissamhammadi1/i-found-50-xss-flaws-using-just-my-browser-a00caba76c48](https://medium.com/@ibtissamhammadi1/i-found-50-xss-flaws-using-just-my-browser-a00caba76c48)
:::
:::important
原文为**Member Only**会员制博文
:::
[[toc]]
## 参考资料
- **原文的参考资料**
	- 无
- **译者翻译时参考的资料**
	- [RecordedFuture - 什么是Google Dorking](https://www.recordedfuture.com/threat-intelligence-101/threat-analysis-techniques/google-dorks)
## 相关工具
- [**KNOXSS**](https://knoxss.pro/) 订阅制的*自动化XSS测试* 平台
- [**Dalfox**](https://github.com/hahwul/dalfox) 使用Go语言打造的 *超快的XSS扫描器*
- **Burp Suite 社区版** *拦截和修改请求
- [**Gauplus**](https://github.com/bp0lr/gauplus?tab=readme-ov-file) *抓取URL用于测试*
	- **Gau**是一款从`AlienVaults`、时光机和威胁情报交易网站抓取URL的工具；而**GauPlus**则是Gau的社区加强版
***
## 引言
上个月，我向一家科技巨头提交了一个XSS漏洞，无他，只使用了**Chrome浏览器 开发者工具**

三天前，我的Paypal账户收到了5000美元的漏洞赏金。不使用BP，也不使用花里胡哨的工具，只用了我的浏览器和一点小小的技巧
如果你认为挖掘XSS漏洞需要用到各种各样琳琅满目的工具，那你还是想少了。
**脚本再强大那也是假的，只使用浏览器挖掘XSS漏洞才是真的**。下面我将手把手教你如何手工挖洞。

## 60秒XSS漏洞速记：为什么只用浏览器就足够了
**XSS (*Cross-Site Scripting*)漏洞**简单来说就是诱导网站运行你注入的脚本而不是它自己的脚本

打个比方，就是把一张假的菜单偷偷塞到厨师的烹饪表里——而厨师（*浏览器*）没有发现菜单是假的、

XSS漏洞主要有以下三种类型：
- **存储型XSS**：Payload会被服务器持久化到缓存或数据库中（常出现在评论情景中）
- **反射型XSS**：即使反射的，不持久的（可能出现在URL中：`example.com/search?q=<script>alert(1)</script>`
- **DOM XSS**：无需服务器交互的，影响整个浏览器范围内的攻击

### 为什么你的浏览器就足够强大了
- **开发者工具(*DevTools*)** 允许你修改页面以测试Payload
- **控制台/网络请求监控(*Console/Network Tab*)** 揭示隐藏输入和API调用
- **无需安装额外工具或插件(*No Setup is needed*)** —— 只需要`Ctrl + Shift + I`快捷键，便可开始日站

## 行之有效的赏金技巧
### 存储型XSS：静默杀手
上传一个SVG Payload `<svg onload=alert(1)>`，如果站点把Payload渲染出来了，那就对了

**应该在什么地方尝试注入**：
- **用户个人主页**（比如 *生物资料页* ）
- **文件上传接口** （比如 *SVG、PDF等的上传页面* ）
- **评论区**

**高级技巧**：
```html
<!-- 绕过空格过滤 -->
<svg/onload=alert(document.domain)>
```
很多网站都**允许上传SVG图像但没有配置有效的过滤措施**
### 反射型XSS：速战速决
使用**Google Dorks**发现可注入的参数：
```
inurl:search?q= inurl:redirect?url= site:example.com
```
然后发送下面的Payload：
```html
"><script>alert(1)</script>
```

:::tip
**Google Dorking**是一种**高级信息搜集技巧**，旨在使用Google搜索引擎提供的搜索语法，来搜索互联网上隐藏的站点或页面（可用于发现一些历史遗留站点）。**Exploit-DB**提供了一个收集了很多Dork Payload的仓库——[**Google Hacking Database (GHDB)**](https://www.exploit-db.com/google-hacking-database)

Google Dorks的威力，来自于将这些高级搜索操作符进行组合，像搭积木一样，构建出极其精准的查询语句。
- **site:**
    - **作用**: 将搜索范围限定在**某个特定的网站**或**某个顶级域名**内。
    - **示例**:
        - site:example.com (只搜索example.com及其所有子域名)
        - site:.gov (只搜索所有政府网站)
- **inurl:**
    - **作用**: 寻找**URL路径中包含特定关键词**的网页。
    - **示例**: inurl:login.php (寻找所有登录页面)
- **intitle:**
    - **作用**: 寻找**网页标题中包含特定关键词**的网页。
    - **示例**: intitle:"index of" (寻找那些显示为“index of /”的、未设防的目录列表)
- **intext:**
    - **作用**: 寻找**网页正文中包含特定关键词**的网页。
    - **示例**: intext:"password" (寻找正文中出现“password”这个词的页面)
- **filetype:**
    - **作用**: 寻找**特定文件类型**的文件。
    - **示例**: filetype:sql (寻找被意外暴露在公网的SQL数据库备份文件)
- **ext:**
    - 与filetype:类似，按文件扩展名搜索。
- **"" (双引号)**
    - **作用**: 进行**精确匹配**搜索。
    - **示例**: "admin login"
- **- (减号)**
    - **作用**: **排除**某个关键词。
    - **示例**: -site:github.com (排除来自GitHub的结果)

以下是常用的20个搜索关键字：
1. **Site:** Finds results on a specific website or domain.
2. **Inurl:** Searches for a keyword within a URL.
3. **Intitle:** Finds a keyword within a webpage's title.
4. **Filetype:** Locates specific file types like PDF or XLS.
5. **Link:** Finds web pages linking to a specific URL.
6. **Intext:** Searches for keywords within the body text of a webpage.
7. **Allintitle:** Finds pages with multiple keywords in the title.
8. **Cache:** Shows the cached version of a webpage.
9. **Related:** Displays pages related to a specific URL.
10. **Info:** Provides details about a website, including cache and similar pages.
11. **Ext:** Finds a specific file extension.
12. **Define:** Displays the definition of a word or phrase.
13. **Phonebook:** Searches for phone numbers and contact information for a person or business.
14. **Map:** Shows a map of a location or address.
15. **Allinurl:** Finds pages with multiple keywords in the URL.
16. **Before:** Finds content indexed before a specific date.
17. **After:** Finds content indexed after a specific date.
18. **Numrange:** Searches for numbers within a specified range.
19. **AROUND(X):** Finds pages where two terms are within a specified number of words from each other.
20. **Inanchor:** Searches for keywords within the anchor text of links on a webpage.

:::

#### 工具推荐
- `gauplus` （抓取URL用于测试）
	```shell
	gauplus -random-agent -subs example.com | grep "search?q="
  ```

### DOM XSS：无形的威胁
**常见sink点（*危险函数*）**
- `innerHTML`
- `eval()`
- `location.hash`

**例如**：
如果一个网站使用了下面的代码：
```html
document.getElementById("error").innerHTML = location.hash.substring(1) ;
```

那么便可尝试下面的Payload：
```html
example.com/#<img src=x onerror=alert(1)>
```

### 悄无声息绕过WAF
**WAF (*Web Application Firewall*)** 会拦截比较露骨的Payload，但对于下面的“奇行种“就无能为力了：
```html
javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/"/+/onmouseover=1/+/[*/[]/+alert(1)//'>
```

**绕过技巧**
- **Case-swapping**: `<ScRipT>alert(1)</sCRipT>`
- **Hex encoding**: `\x3cscript\x3ealert(1)\x3c/script\x3e`
- **SVG/PDF polyglots**: [GitHub repo links] （这里原文就是个空链接）
### 从`alert(1)`到价值一万美元的赏金漏洞：撰写一份报告
##### 报告示例
```plain
Vulnerable Parameter: Search query (/?q=payload)
Payload: <img src=x onerror=alert(document.cookie)>
Impact: Session hijacking (stealing admin cookies)
```

##### 现在就可以使用的免费工具
- **KNOXSS** *自动化XSS测试*
- **Dalfox** *超快的Payload生成工具*
- **Burp Suite 社区版** *拦截和修改请求*

> 记好这些工具 ——让你的第一次XSS漏洞挖掘如虎添翼

# 现在该你了
**试试这个：**
1. 访问任何有**评论区**的站点
2. 发送下面的Payload
	```html
	<svg onload=alert(1)>
	```
3. 如果出现了一个弹窗，那么这便是一个**XSS漏洞**

# 肺腑之言
挖掘XSS漏洞并不需要靶场演练。你的浏览器就是你的趁手工具。动动脑子，专注于**实战情形下的XSS渗透**，做好**笔记归档**

***下一个价值五千美刀的赏金漏洞没准就是你的 —— `Ctrl + Shift + I` 便是你最好的伙伴***
