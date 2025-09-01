---
title: HackerOne 101 CTF 解题合集（其实是挖洞挖到没自信了）
category:
  - 脚本小子
tags:
  - CTF
  - HackerOne
  - H101
---
https://ctf.hacker101.com/ctf
## [Trivial](https://ctf.hacker101.com/ctf/start/1): A little something to get you started
### EXP && PAYLOAD
```HTML

```
### FLAG
```plain text
flag{ee6172793bc23dc43fc76ec267d182cca615f8164ae1c553b725d686798f8789}
^FLAG^ee6172793bc23dc43fc76ec267d182cca615f8164ae1c553b725d686798f8789$FLAG$
```
### 参考资料
### 解题思路
查看页面源代码，访问`body`文本的图像
### 解题过程
dirmap扫不出来，等一下arjun扫扫参数![](assets/Pasted%20image%2020250813202417.png)
谢谢……
![](assets/Pasted%20image%2020250813204116.png)
再看一眼源代码，有一个被视作文本的`body`属性，加载一下……
![](assets/Pasted%20image%2020250813204147.png)
原来如此

但是……唉……这怎么交呢？噢，顶部导航栏有个`submit flag`，校验通过的话页面不会有提示也不会立即刷新题目列表，就挺坑的
***
## [\[Easy\] Micro-CMS v1](https://ctf.hacker101.com/ctf/start/2)
### EXP && PAYLOAD
```HTML

```
### FLAG
```plain text
FLAG03: ^FLAG^401ca02397156b32ac7a6f7ebfc2b93c9d4c8c2baa2e39e30c3b27deb4eca4fc$FLAG$
FLAG02: ^FLAG^f04046c9e82e997d5ef0babf2ca4a816dd85f2b6cc08c3cc6bada62682cc2de6$FLAG$
^FLAG^ba9e8fd1739acb3226ec35f844bd8366b76bc0f17d89d1fb445d4ae15a12dcb6$FLAG$
^FLAG^55ff7f3c43ee806e0700d5100400c1d31a0fd00b4a77469e71f7535f7819d89e$FLAG$
```
### 参考资料
- [Medium - Ternera的WP](https://medium.com/@ternera/hacker101-ctf-micro-cms-v1-e230c5239126)
### 解题思路
1. 注意到Markdown编辑已有页面可以加载HTML元素，于是注入XSS Payload（使用EasyXSS插件获取`<img` Payload）
2. `/create/page`路由可以创建页面，但是不能直接往标题里注入XSS（会被自动HTML实体化），要爆破请求，这样等到ID来到`38`之后后台判机就会给页面标题注入flag
3. `/page/edit/{int}`路由可以绕过某些页面的403限制
4. `/page/{int}`路由模拟了SQL注入漏洞，在后面加上单引号就能拿到flag
### 解题过程
![](assets/Pasted%20image%2020250813204926.png)
一个可以编辑和预览Markdown文档的超简易博客，并且这个Markdown是拓展了HTML语法的
![](assets/Pasted%20image%2020250813205152.png)
确实能弹东西出来
![](assets/Pasted%20image%2020250813205621.png)
但是拿到flag的方法有点反常，似乎是匹配到XSS Payload就会向其中注入flag的
这里拿到第一个flag

扫了一波目录没结果
![](assets/Pasted%20image%2020250814120855.png)
根据提示，爆破了`create/page`路由，炸出来第二个flag
![](assets/Pasted%20image%2020250814121034.png)
太阴了

![](assets/Pasted%20image%2020250814123222.png)
注意到第3~7篇文章没有被列出来，对着`page/{int}`路由爆破了一下，注意到第5篇文章返回了403状态码![](assets/Pasted%20image%2020250814123506.png)
使用`OPTIONS`请求方法时返回了`200`，但是没有内容
路径穿越的方法也不太行，也没有针对openresty/1.27.1.2的SSRF vector
![](assets/Pasted%20image%2020250814124917.png)
`/page/edit`路由能编辑到，但是会是一次性的……直接覆盖了……
![](assets/Pasted%20image%2020250814125415.png)
重开了一下容器然后手动测试，发现从`/page/edit`可以访问403页面……旁路攻击
![](assets/Pasted%20image%2020250814125806.png)
继续测试，确认前八篇文章只有第5篇文章是可以进行403Bypass的

最后一个flag……
现在尝试了编辑Markdown内容注入XSS、爆破创建Markdown页面、侧信道攻击绕过403限制，
还有什么呢
![](assets/Pasted%20image%2020250814132001.png)
……666有这么做题目的吗？？合着你这路径匹配是仿SQL的不是直接匹配文件路径的
***
## \[Moderate\] Micro-CMS V2
### EXP && PAYLOAD
```HTML

```
### FLAG
```plain text

```
### 参考资料
### 解题思路
### 解题过程
现在不论是修改还是创建页面都需要登录……
```shell
sqlmap -u "https://1f4ebc0a41aba4f3c30696e64362916b.ctf.hacker101.com/login" --data "username=admin&password=12345"
```

***
## 题目名称
### EXP && PAYLOAD
```HTML

```
### FLAG
```plain text

```
### 参考资料
### 解题思路
### 解题过程

***
## 题目名称
### EXP && PAYLOAD
```HTML

```
### FLAG
```plain text

```
### 参考资料
### 解题思路
### 解题过程

***
## 题目名称
### EXP && PAYLOAD
```HTML

```
### FLAG
```plain text

```
### 参考资料
### 解题思路
### 解题过程

***
## 题目名称
### EXP && PAYLOAD
```HTML

```
### FLAG
```plain text

```
### 参考资料
### 解题思路
### 解题过程

***
## 题目名称
### EXP && PAYLOAD
```HTML

```
### FLAG
```plain text

```
### 参考资料
### 解题思路
### 解题过程

***
## 题目名称
### EXP && PAYLOAD
```HTML

```
### FLAG
```plain text

```
### 参考资料
### 解题思路
### 解题过程

***
## 题目名称
### EXP && PAYLOAD
```HTML

```
### FLAG
```plain text

```
### 参考资料
### 解题思路
### 解题过程

***
## 题目名称
### EXP && PAYLOAD
```HTML

```
### FLAG
```plain text

```
### 参考资料
### 解题思路
### 解题过程

***
## 题目名称
### EXP && PAYLOAD
```HTML

```
### FLAG
```plain text

```
### 参考资料
### 解题思路
### 解题过程

***
