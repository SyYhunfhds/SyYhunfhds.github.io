---
title: 价值47500美刀的Git已删除文件泄露漏洞
date: 2025-09-22
author: Ibtissam hammadi
footer: 版权及浏览收益为原作者所有。如侵犯版权，请通知译者尽快删除
---
:::important
**原作者**：[Ibtissam hammadi](https://medium.com/@ibtissamhammadi1?source=post_page---byline--e1f144981757---------------------------------------)
**原标题**：[My Bug In Deleted Files Made Me $47,500](https://medium.com/@ibtissamhammadi1/my-bug-in-deleted-files-made-me-47-500-e1f144981757)
**原始副标题**：[How a flaw in Git’s internals led to a $47,500 bug bount](https://medium.com/@ibtissamhammadi1/my-bug-in-deleted-files-made-me-47-500-e1f144981757)

**原文为Member-Only限制阅读**
:::
[[toc]]
# 正文
## 前言
忙碌了一天后，`git add`、`git commit`、`git push`，然后便是短暂的放松。代码看起来安全了，但真是如此吗？有没有可能，`git rm`并不会真正删除追踪的代码？你的API密钥仍然是暴露的呢？

这并非只是一个空想，这最终成为价值47500美元的Github仓库安全漏洞

这不会是一个舒心的问题。每天都有数不胜数的敏感文件被上传到git仓库中，与此同时还有N多个扫描bot对这些敏感文件虎视眈眈。对于想挖商业SRC（原文是*Bug Bounty*）的人来说，这些敏感文件无疑是一座座金矿
## 重新认识git
### `.git`目录暗藏玄坤
很多开发者都以为`.git`目录只是一个存档点——一个存储最新提交的地方罢了。但这就大错特错了。实际上，`.git`目录更像一个精妙的高效的数据库，尽职尽责地保存好你的每一次git活动

所以听好了：`git rm`不会删除文件，而只是从当前项目中删除了文件，而对文件的修改操作以及文件本身仍然保存在git的本地数据库中。文件此时变成了所谓的**悬垂对象**（**blob**，**Binary-Large-Object**，大型二进制对象）

这些悬垂对象就像遗落在图书馆储藏室的书，它们只是没有出现在主书架上，而不是被打成了纸浆。为了节省空间，Git会高效地将这些历史对象打包成`pack files`

这对于版本控制来说很正常，但在**Github仓库安全人员**看来，这是一个潜在的隐患。如果曾经有API密钥或凭据被提交到仓库中，它就会一直存在git数据库中，`git rm`是不能彻底删掉的。API密钥等敏感文件仍然存在数据库中，甚至是可以通过指令复原的（`git checkout <old-commit-hash> -- <file>`）

这不是BUG，这是特性（*机制* ），但安全人员必须知晓这个问题
## 开始挖洞
### 如何从数据以太中提取出敏感数据
#### 1. The Mistake
一个写有**API密钥**的配置文件被交了上去，后面又`git rm`掉了
“我不到啊？我还以为删掉了呢？”
#### 2. The Insight
**Git机制**告诉我们文件只是被打包成了悬垂blob，我们只需要找到它
#### 3. The Tool（`git fsck`）
`git fsck --full --unreachable --no-reflog`用于列出所有没有链接到当前git历史的对象
#### 4. 自动化
手动翻看每一个blob的话会很折磨人，因此必须上脚本。**TruffleHog**可用于搜索遍历所有不可达的对象
#### 5. 获得回报
**TruffleHog**会制裁每一个以为`git rm`了文件就不会泄露敏感数据的开发者
## 报酬 && 修复
平台评级为**严重**漏洞。厂商的安全团队十分感激。他们的敏感数据没有被其他别有用心的人利用，而我也获得了47500美刀的回报

很多开发团队都只关注活跃的代码仓库，但要想真正万无一失，我们还必须看得更深。下面我会教你如何保护你自己的仓库：
#### 1. 扫描整个代码仓库，而不只是最近几次提交
大多数**敏感数据扫描**都只针对要提交上去的代码，这没问题，但有点顾头不顾腚。你的**整个代码仓库**都可能暗藏玄坤
- **怎么办呢？**
	用工具扫描整个代码repo，比如用`trufflehog`：
	```sh
	trufflehog git https://github.com/your-org/your-repo --since-commit HEAD --max-depth 1000
	```
工具会扫描最近1000次提交，搜索悬垂blob中的敏感数据
#### 2. 移除所有敏感文件
（`git rm`是治标不治本的）我们必须重写整个提交历史来彻底清除历史敏感数据提交
- **怎么办呢？**
	推荐使用`git filter-repo`，强大，并且专为清楚历史提交中的特定文件而生
	```sh
	# Example: Remove a file containing a password from all history  
	git filter-repo --force --path passwords.txt --invert-paths
	```
	（直接用`git rebase`也行）
:::warning from 原作者
这将重写提交历史，仓库中的其他开发者需要重写克隆仓库来启用最新的提交历史
:::

#### 3. 在提交前删除对敏感文件的追踪
最好的解决办法就是防患于未然。预提交hook可以自动化扫描提交中的敏感信息，并阻止符合条件的敏感提交，就像一个安全网一样，防呆不防傻。

- **怎么办呢？**
	把Trufflehog这样的工具整合到代码仓库中
	```yaml
	# Example pre-commit hook configuration  
	# Install trufflehog and add this to your .pre-commit-config.yaml file  
	-   repo: https://github.com/trufflesecurity/truffleHog  
	    rev: main  
	    hooks:  
	    -   id: trufflehog
	```
	现在每次`git commit`后，工具都会自动扫描代码

在采取这些措施后，你不会再祈祷仓库失火，而是知道它们（理论上）不会再出事。你将**主动出击**，将隐患扼杀在摇篮中
## 反思 （*Takeaway*）
The **.git directory** is an engineering marvel with a shadow side. Understanding **Git internals** is a modern security superpower.

What’s hiding in your attic?

**P.S.** This isn’t just for **bug bounty** hunters. Every developer should scan old repos — you might find something scary or lucrative.
***
# 页面尾部