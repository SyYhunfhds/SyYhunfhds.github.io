---
title: 网安每日任务指南 - 用Python赶走无聊的工作
category:
  - Medium
  - 搬运
author: Karthikeyan Nagaraj - https://cyberw1ng.medium.com/
footer: |-
  原文来自https://osintteam.blog/automate-your-boring-stuff-with-python-a-practical-guide-for-everyday-cybersecurity-tasks-b78a266a98a7
  版权由原作者所有
---
:::important
**原作者**：Karthikeyan Nagaraj
**原作者的博客主页**：[https://cyberw1ng.medium.com/](https://cyberw1ng.medium.com/)
**原文标题**：Automate Your Boring Stuff with Python: A Practical Guide for Everyday Cybersecurity Tasks
**原文副标题**：Tired of repetitive security work? Let Python do the heavy lifting so you can focus on critical thinking, not copy-pasting.
**原文链接**：https://osintteam.blog/automate-your-boring-stuff-with-python-a-practical-guide-for-everyday-cybersecurity-tasks-b78a266a98a7
**原文归属期刊**：[OSINT Team](https://osintteam.blog/)

版权完全由原作者所有。本页面为静态页面，不会统计浏览次数。
:::

[[toc]]
***
## 前言
在打理网络安全时，我们常常会花费大量精力执行繁杂漫长的任务——扫描站点、解析日志、发送告警、管理文件等等。你有没有想过你可以用几行Python代码来自动化处理70%的例行日程？

:::info 译者碎碎念
这里翻译的时候脑子一热直接拐到挖洞里了，后来想想不对劲——怎么我挖洞还要 *整理文件* 的呢？？
:::

欢迎来到**Python自动化**的天地。不论你是网络空间安全分析师、漏洞赏金猎人，亦或是系统管理员（*sysadmin*），Python都提供了一揽子你可以用来打造快捷而强大的自动化武器库的工具。

在这篇博文中，我们将通过**自动化实战示例**、实用代码和Python模块来一步步解析如何打造属于你的Python武器库——没有水分，全是干货（*no fluff, just the good stuff* ）

## 在网络安全中你能用Python自动化做些什么？
下面是一揽子可以用Python自动化优化的无聊事务：
[list2mdtable]
- **事务**
	- **自动化示例**
- 信息搜集和信息枚举
	- 子域名爬取，端口扫描
- 日志分析
	- 从`syslog`或JSON文件中提取IOC
- 恶意文件哈希比对
	- 封装`VirusTotal`的API
- 薄弱资产扫描
	- 运行`Nmap`或`Nuclei`脚本
- 警告 && 通知
	- 发送消息到`Slack`或电报/纸飞机
- 文件操作
	- 重命名、删除和对日志/文件排序整理
- 生成报告
	- 导出PDF或HTML
- API交互
	- 从`Shodan`、`Censys`和`Github`拉取数据
- 网页爬取
	- 从`NVD`或`Exploit DB`爬取CVE描述或POC
:::info 译者注（如果博文原作者能看到的话）
这里使用了来自**AnyBlock**插件的**列表转多叉表格语法** `[list2mdtable]`来还原原文的表格（截图）。而VuePress也可以渲染这种语法

中国大陆用户对`Telegram`的别称是 *电报* 和 *纸飞机*

我知道原作者可能不懂中文，但他们的AI肯定能看懂
:::
### 示例1：自动化子域名爆破
```Python
import requests  
  
def get_subdomains(domain):  
    url = f"https://crt.sh/?q=%25.{domain}&output=json"  
    r = requests.get(url)  
    subdomains = set()  
    if r.ok:  
        data = r.json()  
        for entry in data:  
            name = entry.get("name_value")  
            if name:  
                subdomains.update(name.split("\n"))  
    return subdomains  
  
domain = "example.com"  
for sub in get_subdomains(domain):  
    print(sub)
```

✅**食用方式**：搭配`Nuclei`漏扫食用

:::info 译者注
可以使用[`ksubdomain`](https://github.com/knownsec/ksubdomain) *极速无状态子域名挖掘工具* 挖掘子域名，`ksubdomain`的开发者还提供了子域名挖掘 + HTTPX探活的指令示例。不建议在这里自己造轮子。
:::
### 示例2：使用`VirusTotal` API检查恶意文件
```Python
import requests  
  
API_KEY = "your_virustotal_api_key"  
hash_value = "eicar_test_file_hash"  
  
url = f"https://www.virustotal.com/api/v3/files/{hash_value}"  
headers = {"x-apikey": API_KEY}  
response = requests.get(url, headers=headers)  
  
data = response.json()  
print(data["data"]["attributes"]["last_analysis_stats"])
```

✅**食用方式**：自动化分析和分类IOC
### 示例3：解析`Syslog`日志以提取IOC（攻击迹象）
```Python
import request  
  
with open("syslog.txt") as f:  
    logs = f.read()  
  
ips = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", logs)  
print(set(ips))
```

✅**食用方式**：将IP列表喂给威胁分析平台（如`Pulsedive`和`AbuseIPDB`）进行进一步分析

:::info 译者碎碎念
当日志文件很大时，建议使用`readline`方法来分别读行，以免终端卡死：
```Python
with open("syslog.txt") as f:  
    while True:
	    log = f.readline()
	...
... 
```
:::
### 示例4：Python + Nmap 自动化端口扫描
```Python
import nmap  
  
scanner = nmap.PortScanner()  
scanner.scan('127.0.0.1', '1-1024', '-T4')  
for host in scanner.all_hosts():  
    print(f"Host: {host} - {scanner[host].hostname()}")  
    for proto in scanner[host].all_protocols():  
        ports = scanner[host][proto].keys()  
        for port in sorted(ports):  
            print(f"Port {port}: {scanner[host][proto][port]['state']}")
```

✅**食用方式**：只需要常用端口（如`22`、`443`、`3389`）即可

:::info 译者碎碎念
三层for嵌套？？小时候看这集Python进程占用率直上100%了
:::
### 示例5：发送消息到你的电报
```Python
import requests  
  
def send_alert(message):  
    bot_token = 'your_bot_token'  
    chat_id = 'your_chat_id'  
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"  
    requests.post(url, data={'chat_id': chat_id, 'text': message})  
  
send_alert("🔴 Suspicious login detected from 185.123.x.x")
```

✅**食用方式**：当消息触发时记得查看BOT
### 示例6：自动重命名和组织文件
```Python
import os  
  
folder = "./logs"  
for filename in os.listdir(folder):  
    if filename.endswith(".txt"):  
        os.rename(f"{folder}/{filename}", f"{folder}/renamed_{filename}")
```

✅**食用方式**：每天导出日志后可以这样管理一下繁杂的文件
### 示例7：使用API进行被动信息收集
```Python
# 以shodan为例
import shodan  
  
api = shodan.Shodan("your_shodan_api_key")  
result = api.search("nginx")  
  
for service in result['matches'][:10]:  
    print(service['ip_str'], service.get('port', 'N/A'))
```

✅**食用方式**：打造一个自动扫描公网资产的监控平台
### 示例8：使用`argparse`打造你的专属CLI工具
```Python
import argparse  
  
parser = argparse.ArgumentParser(description='Recon CLI Tool')  
parser.add_argument('-d', '--domain', help='Target domain')  
args = parser.parse_args()  
  
if args.domain:  
    print(f"Scanning domain: {args.domain}")  
    # Your automation logic here
```

✅**食用方式**：为你的团队打造可重复使用的CLI工具
## 拓展阅读
[list2mdtable]
- **资源**
	- **链接**
- 用Python自动化处理无聊的事务（书籍）
	- https://automatetheboringstuff.com
- 安全从业人员眼中的Python（免费课程）
	- https://academy.tcm-sec.com
- Python请求库
	- https://docs.python-requests.org
- Python Nmap模块
	- https://pypi.org/project/python-nmap/
- VirusTotal API 文档
	- https://developers.virustotal.com/reference
## 总结 && 致谢
Python绝不只是一门脚本语言——它还可以是你的挖洞助手。从信息收集到应急响应，通过打造一个全年无休的自动化工具可以节省你很多时间

>我可以用Python自动化这件事情吗？

一般来说，是的，你可以做到，而这篇博文也为你描绘了Python自动化的蓝图

:::info 原作者运营的一个发布网安POC和WP的油管频道
https://www.youtube.com/channel/UCBg0UIT0319Xc-cw4QK8bqA?sub_confirmation=1&source=post_page-----b78a266a98a7---------------------------------------
:::
:::info 原作者的Github资源
https://github.com/cyberw1ng?source=post_page-----b78a266a98a7---------------------------------------
:::
感谢阅读！日站愉快！