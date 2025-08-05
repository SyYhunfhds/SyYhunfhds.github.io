---
title: 挖掘巴基斯坦电商平台bykea漏洞
category:
  - 红队
  - 脚本小子
  - AI+
tags:
  - 红队
  - 脚本小子
  - AI-Powered
date: 2025-08-05
---
## 资产范围
```cs
|identifier|asset_type|
|*.bykea.net|WILDCARD|
|com.bykea.pk|GOOGLE_PLAY_APP_ID|
|com.bykea.pk.partner|GOOGLE_PLAY_APP_ID|
|1351179184|APPLE_STORE_APP_ID|
|bykea.com|URL|
|https://maps.bykea.net|URL|
|https://leaflet-map.bykea.net|URL|
|https://nominatim.bykea.net|URL|
|https://googleplace*.bykea.net|WILDCARD|
|https://geocode-beta.bykea.net|URL|
|www.tilismtechservices.com|URL|
|https://api.bykea.net|URL|
|https://kronos*.bykea.net|WILDCARD|
|https://loadboard*.bykea.net/|WILDCARD|
|https://raptor*.bykea.net|WILDCARD|
|https://*test*.bykea.net|WILDCARD|
```

## 尝试子域名挖掘和探活
```shell
subfinder.exe -d *.bykea.net

--- 2025年8月5日 02:42:40
sandbox.bykea.net 503
jaalitalos.bykea.net 503
googleplaces.bykea.net 403 *
```

不得劲，换ksubdomain
```
api.bykea.net => 172.67.70.114 => 104.26.4.35 => 104.26.5.35
sp.bykea.net => 104.26.5.35 => 172.67.70.114 => 104.26.4.35
track.bykea.net => 104.26.4.35 => 172.67.70.114 => 104.26.5.35
raptor.bykea.net => 104.26.5.35 => 172.67.70.114 => 104.26.4.35
```
处理一下：
```plain
api.bykea.net
sp.bykea.net
track.bykea.net
raptor.bykea.net
```

### 尝试403 bypass `googleplaces.bykea.net`
```shell
python dirsearch.py -u "https://googleplaces.bykea.net/" -j yes -b yes
```
使用403Bypasser尝试目录扫描和403绕过
确认后台确实没有暴露的敏感文件

### 尝试扫描 `api.bykea.net`
```shell
python dirsearch.py -u "https://api.bykea.net/" -j yes -b yes
```
也没有暴露的敏感文件

### 尝试子域名接管漏洞 
```shell
F:\CodeDev\nuclei.exe -u api.bykea.net -u sp.bykea.net -u track.bykea.net -u raptor.bykea.net -t F:\CodeDev\全自动漏洞挖掘\9.4WPOC\subdomain_takeover\subdomain-takeover.yaml
```
![](assets/Pasted%20image%2020250805063859.png)
告辞
## 扫描各个站点
### 首页 `bykea.com`
没有暴露的敏感URL、没有暴露的参数

## Nuclei，启动！
