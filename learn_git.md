# 糊里糊不记得改动在哪儿？确定不试试Git吗？

上个月对某个功能的修改，这个月还能记得怎么改的吗？
想退回到上一次稳定的版本，但是当时的版本忘了保存？
或者对着v1.0、 v1.1、v1.2的后缀，但是里面什么内容就很迷糊？
  
不管是团队协作，还是自己的软件管理，都可以试试Git。

## 1 什么是版本控制？

版本控制系统是帮助软件团队管理源代码的软件工具。随着开发环境的加速，版本控制系统可以帮助软件团队高效地工作，减少开发时间。

版本控制软件在一种特殊的数据库中记录了对代码的每一次修改。如果出现了错误，开发人员可以回溯，与代码的早期版本进行比较，帮助修复错误，同时尽量减少对其它团队成员的干扰。

### 版本控制的优势

版本控制可以帮助开发人员加快进度，并允许软件团队在团队扩大时保持效率和敏捷性。

版本控制系统（Version Control Systems, VCS）有时也被称为源代码管理（Source Code Management, SCM）或修订控制系统（Revision Control System）。今天最流行的VCS工具之一是Git，一个分布式的VCS（Distributed VCS, DVVS）。其主要优势包括：

1. 有完整的修订历史记录。包括文件的创建、删除以及对其内容的编辑，还包括作者、日期和每次改动的目的说明。有了完整的历史记录就可以回溯到以前的版本，方便bug修复。

2. 分支和合并（Branching and merging）。（1）通过在VCS中创建一个“分支”（branch），可以使多个工作流相互独立；（2）将工作合并（merge）到一起，使开发人员能验证每个分支上的修改有没有冲突。可以为每个功能建立分支，也可以为每个版本建立分支，或两者兼具。

3. 可追溯性。能够追踪对代码所做的每一个改动，并与项目管理和错误跟踪软件（如Jira）连接起来；能对每一次改动的目的进行清晰的注释，不仅有助于根本原因分析，也有助于别人理解代码，符合系统的长期设计意图。

## 2 源代码管理

源代码管理（SCM）用于跟踪源代码库的修改。SCM记录了代码库的修改历史，有助于在合并多个贡献者的更新时解决冲突。

随着软件项目的代码量和贡献者数量的增加，沟通和管理的复杂性也在增加。SCM可以减轻开发成本增长带来的组织压力。

### 源代码管理的推荐做法

1. 经常提交（commit）
    - 每次提交都是一个snapshot，频繁的提交可以提供很多机会恢复或撤销改动。一组提交可以通过rebase合并成一个提交，以澄清开发日志。
2. 确保是在最新版本上进行的改动
    - SCM允许多个开发者快速更新，很容易出现代码库的本地副本落后于全局副本的情况。因此，在进行更新之前，git pull获取最新的代码，有助于避免合并时的冲突。
3. 清晰的注释
    - 每次提交都有一个相应的log entry。提交的日志信息应该对提交内容是“为了什么”和“做了什么”进行描述。这些日志信息会成为项目发展的重要记录，可供未来的贡献者review。
4. commit之前进行审查
    - SCM提供了一个"暂存区"。在提交之前，暂存区可以用来管理和review所进行的改动。
5. 利用分支
    - 分支允许开发者创建一个独立的开发线。这些开发线通常是不同的产品功能。当一个分支的开发完成后，可以被合并到主开发线中。
6. 商定一个工作流
    - 如果没有就工作流程达成一致，在合并分支的时候就会导致低效的沟通。

## 2 Git是什么？

Git是一个成熟的的开源项目，由Linux操作系统内核的著名创造者Linus Torvalds于2005年开发。Git用户广泛，它在各种操作系统和IDE（集成开发环境）上都能很好地工作。

Git采用了分布式架构，是DVCS（分布式版本控制系统）的一个范例。在Git中，每个开发者的工作副本也是一个仓库，可以包含所有的修改历史，而不是像曾经流行的版本控制系统那样，只有一个地方可以保存软件的完整版本历史。

**除了分布式外，git还有以下几个特征：**
1. **性能**

    - Git的原始性能非常强大。提交新的修改、分支、合并和比较过去的版本都进行了性能优化。

    - Git在确定文件树的存储和版本历史时不会被文件名所迷惑（源代码文件经常被重命名、分割），**Git关注的是文件内容本身**。

    - 分布式的设计也能带来显著的性能优势。

2. **安全**

    - Git仓库中，文件的内容以及文件、目录、版本、标签和提交之间的关系，所有这些对象都用一种叫做SHA1的加密安全散列算法来保证。这可以保护代码和变更历史不受意外和恶意变更的影响，确保更改历史的可追溯性。有了Git，你可以确信你的源代码有一个真实的历史记录。

3. **灵活**

    - Git的灵活性体现在对各种非线性开发工作流程的支持、小型和大型项目的开发效率以及对许多现有系统和协议的兼容性上。

## 3 Git使用

### 3.1 安装和初次配置

git安装参见这个[教程](https://www.atlassian.com/git/tutorials/install-git)。

对于windows系统，下载安装exe即可。

对于Linux系统，操作如下：

1. 使用apt-get安装git

```
sudo apt-get install git
```

2. 查询是否安装成功

```
git --version
```

输出：```git version 2.30.1```
3. 配置Git用户名和邮箱。

```
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱"
```

### 3.2 导入一个新的项目

1. 进入到一个项目目录下，使用git init进行初始化。

```
cd project
git init
```

git会回复：```Initialized empty Git repository in .git/```

现在你已经初始化了工作目录--一个新的目录被创建，名为".git"，可以通过```ls -ah```查看。

2. 用git add告诉Git对当前目录下所有文件的内容进行快照，"."表示所有内容。

```
git add .
```

这个快照现在被保存在了一个**临时的暂存区域**，Git称之为 "索引（**index**）"。

3. 用git commit将索引的内容永久保存在仓库里。

```
git commit
```

### 3.3 做一些修改

对某些文件（file1 file2 file3）进行修改，然后把更新的内容添加到暂存区（index）中：

```
git add file1 file2 file3
```

提交前，可以用带有--cached选项的git diff命令来查看即将提交的内容。

```
git diff --cached
```

如果没有"--cached"，git diff会显示您已经做的但尚未添加到index中的任何修改。也可以用git status得到一个简短的情况说明:

```
$ git status
On branch master
Changes to be committed:
Your branch is up to date with 'origin/master'.
  (use "git restore --staged <file>..." to unstage)

 modified:   file1
 modified:   file2
 modified:   file3
```

如果还要做其它改动，也可以继续修改，把改动的文件也存到缓存区然后提交：

```
git commit -m "your message"
```

它将提示您输入描述该变更的信息（简单描述一下做了什么即可），然后会生成40位的哈希值，用作id，并把刚刚用git add添加到提交缓存区里的文件提交到本地仓库中，便于回溯。如果觉得message写得不好，还可以通过```git commit --amend```进行修改。

另外，你也可以不先运行git add再提交，而是使用

```
git commit -a
```

这样会将自动将任何修改过的（但不是新的）文件添加到缓存区中，然后提交（所有这些都在这一个命令中完成）。

### 3.4 查看项目历史

任何时候都可以通过用以下命令查看修改历史：

```
$ git log
commit 8b34695d8b1b4a13cf2fd5ef87bff876b937848f (HEAD -> master)
Author: Haiqin Chen <40618231+lovelyweather@users.noreply.github.com>
Date:   Sun Oct 23 16:10:08 2022 +0800

    Update learn_git.md
```

Git的历史表现为一系列commit，上述```git log```命令可以列出这些commit信息。第一行的commit是哈希算法算出的id。

可以```git show```这个id，以查看细节。
```
$ git show 8b34695d8b1b4a13cf2fd5ef87bff876b937848f
```
其实用前面几位数也就足够了，如```$ git show 8b34695d8b1b```。

可以使用git log -p查看每一处的详细信息:
```
git log -p
```
也可以使用如下命令查看版本修改的概述:
```
git log --stat --summary
```

可以给自己的提交命名：
```
$ git tag v2.5 8b34695d8b1b
```
用"v2.5"来命名8b34695d8b1b这个版本。如果你打算与其他人分享这个名字（例如，作为一个发布版本），你应该创建一个"tag"对象，也许还需要签名。

一些git log命令：
```
$ git log v2.5..v2.6            # commits between v2.5 and v2.6
$ git log v2.5..                # commits since v2.5
$ git log --since="2 weeks ago" # commits from the last 2 weeks
$ git log v2.5.. Makefile       # commits since v2.5 which modify Makefile
```
### 3.5 管理分支

Git仓库可以维护多个分支。要创建一个名为"experimental"的新分支：

```
git branch experimental
```

如果现在运行```$ git branch```，会得到一个所有现有分支的列表：

```
  experimental
* master
```

"experimental"分支是刚刚创建的，"master"分支是自动创建的默认分支。星号标志着你当前所在的分支；
输入```$ git switch experimental```可以切换到experimental分支。
现在编辑一个文件，提交修改，然后切换回主分支:

```
(edit file)
$ git commit -a
$ git switch master
```

这时不能检查experimental上所做的修改了，因为已经回到了主分支。

可以在主干分支上做一个不同的修改，然后commit：

```
(edit file)
$ git commit -a
```

现在两个分支有差别了。要将experimental分支的修改合并到main分支，请运行：
```
$ git merge experimental
```
如果这些修改没有冲突，就完成了。如有冲突，会在有问题的文件中有冲突的地方留下标记。
```$ git diff```可以显示冲突。

当你解决了冲突之后，使用```$ git commit -a```提交。

这时，可以用```$ git branch -d experimental```删除experimental分支，-d可以确保experimental分支中的改动已经在当前分支中了。

如果你在crazy-idea分支上开发，然后后悔了，你可以随时用```$ git branch -D crazy-idea```命令删除该分支。

### 3.6 使用Git进行协作

假设Alice启动了一个新项目，其Git仓库位于/home/alice/project；在同一台机器上，Bob也想贡献自己的力量。

Bob先用```bob$ git clone /home/alice/project myrepo```创建一个新的目录"myrepo"，该克隆版本与原始项目处于平等地位，拥有原始项目历史的副本。

Bob做了一些修改并提交了：
```
(edit files)
bob$ git commit -a
(repeat as necessary)
```
Bob告诉Alice拉取位于/home/bob/myrepo的仓库。Alice执行如下命令：
```
alice$ cd /home/alice/project
alice$ git pull /home/bob/myrepo master
```
这将把Bob的“master”分支的修改合并到Alice的当前分支。如果Alice在这期间做了自己的修改，那么她可能需要手动修复出现的冲突。

这里，"pull"命令执行了两项操作：它从远程分支获取修改，然后将它们合并到当前分支中。

注意：一般来说，Alice会在启动这个"拉取"命令之前，先提交她的本地修改。如果Bob的工作与Alice在他们的历史分叉后所做的工作有冲突，Aliceq将使用她的工作树和缓存区来解决冲突。

Alice可以先使用"fetch"命令大致查看一下Bob所做的事情，使用"FETCH_HEAD"，以确定他是否有值得拉取的东西，而不用先合并。像这样:
```
alice$ git fetch /home/bob/myrepo master
alice$ git log -p HEAD..FETCH_HEAD
```
即使Alice有未提交的本地修改，这个操作也是安全的。范围符号"HEAD...FETCH_HEAD"的意思是：显示从HEAD到FETCH_HEAD的一切修改内容。因为Alice已经知道了直到她当前状态（HEAD）的所有内容，只需要审查Bob在他的状态（FETCH_HEAD）中有哪些是她没有看到的。

在检查了Bob的修改后，如果没有什么紧急的事情，Alice可以决定继续工作而不从Bob那里拉取。如果Bob的历史中确实有一些Alice马上需要的东西，Alice可以选择先把她的工作藏起来，执行一个"pull"，再把她的工作置于新的版本之上。

当你在一个紧密的团体中工作时，反复与同一个版本库交互是很正常的。通过定义远程版本库的缩写，你可以让它变得更容易：
```
alice$ git remote add bob /home/bob/myrepo
```
这样，Alice就可以使用git fetch命令单独执行"pull"的第一部分操作，而不需要将它们与自己的分支合并，使用：
```
alice$ git fetch bob
```
当Alice使用git remote设置的远程仓库时，从Bob那里获取的内容会被保存在远程跟踪的分支中，在这里是bob/master。在这之后执行：
```
alice$ git log -p master...bob/master
```
可以显示Bob从Alice的master分支分出后所做的修改。

检查完这些改动后，Alice可以将这些改动合并到她的主干分支中:
```
alice$ git merge bob/master
```
这个合并也可以通过从她自己的远程跟踪分支拉取来完成（这与上述操作是一样的）:
```
alice$ git pull . remotes/bob/master
```
注意，git pull总是合并到当前的分支。

之后，Bob可以更新他的仓库到Alice的最新版本，方法是：
```
bob$ git pull
```
他不需要给出Alice仓库的路径；当Bob克隆Alice的仓库时，Git在仓库配置中存储了她的仓库位置，这个位置会被用于拉取：
```
bob$ git config --get remote.origin.url
/home/alice/project
```
Git 也会在"origin/master"下保留Alice主分支的原始副本。
```
bob$ git branch -r
  origin/master
```
**如果Bob在不同的机器上工作，他仍然可以使用ssh协议执行clone和pull。**
```
bob$ git clone alice.org:/home/alice/project myrepo
```
另外，Git也可以使用http，git pull详情点[这里](https://git-scm.com/docs/git-pull)。

## 4 SSH Key
SSH密钥是SSH（secure shell）网络协议的一个访问凭证。这个经过认证和加密的安全网络协议用于在不安全的开放网络上的机器之间进行远程通信。SSH被用于远程文件传输、网络管理和远程访问。所以，不管是在github还是其它服务器上，如果需要进行远程通信，都需要SSH密钥。

SSH使用一对密钥来启动远程各方之间的安全握手。该密钥对包含一个公钥和一个私钥。私钥与公钥都被称为key，公钥可以看作一把“锁”，私钥看作是“钥匙”。把公开的“锁”交给远程各方，以加密或“锁定”数据。持有的“私人密钥”可以打开这些数据。

### 4.1 [创建key](https://www.atlassian.com/git/tutorials/git-ssh)
SSH密钥是通过公钥加密算法产生的，最常见的是RSA或DSA。SSH密钥通过一个数学公式产生，它需要2个质数和一个随机种子变量来生成公钥和私钥。这是一个单向的公式，确保公钥可以从私钥中导出，但私钥不能从公钥中导出（非对称加密）。

SSH命令行工具包含一个密钥生成（keygen）工具：
```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```
-t 指定密钥类型，默认是rsa ，可以省略;

-C 设置注释文字，比如邮箱。
- 首先会弹出“"Enter a file in which to save the key"，不填直接回车就默认生成在~/.ssh文件夹下。
- 然后会弹出“Enter passphrase”，输入密码，作为额外的一层防护。
出现如下提示，key就生成好了：
```
Your identification has been saved in /Users/xiaowu/.ssh/id_rsa.
Your public key has been saved in /Users/xiaowu/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:4b5VLgcR1F3R9FxVel/DkJTbNhtx4zsP9DaFFauEx1Y pfchenhaiqin@163.com
The key's randomart image is:
+---[RSA 3072]----+
|         .o..+oE%|
|           .+o==B|
|        . .. ==*O|
|       . . .+.+B=|
|        S . .o..B|
|       .   +  .=o|
|        . o o  o+|
|         o o    .|
|        .        |
+----[SHA256]-----+
```
其中，id_rsa是私匙，id_rsa.pub是公匙，id_rsa不能告诉任何人，只有公钥可以。
## 5 github相关
github可以理解为一个远程服务器，利用git建立本地仓库和远程仓库的通信，所以这部分内容其实不仅限于github，其它远程机器也是一样的，内容和“3.6 使用Git进行协作”也多有重复。

不管是从github上克隆仓库还是从本地上传仓库，都需要在github上传本地机器的公钥：在github的setting下的SSH and GPG keys里粘贴id_rsa.pub里的内容。

### 5.1 把本地仓库关联到远程仓库
1. github上创建一个空的仓库
2. 使用```git remote add <name> <url>```连接到一个远程仓库

    - 我的示例为：```git remote add xiaowu_md git@github.com:lovelyweather/MeteoDataFusion.git```
  添加了这个远程仓库后，后续命令中可以使用\<name>作为\<url>的简写。
3. 使用```git push -u <remote> <branch>```推送到远程
   - 示例：```git push -u xiaowu_md master```，   将master这个分支推送到xiaowu_md对应的仓库url。远程如果没有这个分支会自动创建。我这里本地一半默认是master。
   ```-u```表示把本地仓库master的分支也提交上去，否则只提交当前的master与远程合并，其它的分支则不会。第一次加上```-u```即可，因为本地可能有其它分支可以一起传上去；以后提交新代码就不需要了。
4. 到github仓库上就可以看到刚才提交的代码了，注意需要切换到master分支（因为github上默认的分支是main）。
   - 可以到仓库的setting下的branches里面将default branch设置为master，这样以后就不用切换了。
### 5.2 把远程仓库克隆到本地

通过```git clone <repo>```，克隆位于\<repo>的仓库到本地机器上。原始仓库可以位于本地文件系统上，也可以是在远程机器上。接下来的操作就跟前面一样了，git add, git commit, git push这些。

---
参考资料：
1. [git官方教程](https://www.git-scm.com/docs/gittutorial)
2. [git初学者教程](https://www.atlassian.com/git/tutorials/what-is-version-control)（推荐）
3. [git基础命令pdf](https://github.com/lovelyweather/MeteoDataFusion/blob/master/SWTM-2088_Atlassian-Git-Cheatsheet.pdf)
4. [关于Git这一篇就够了](https://blog.csdn.net/bjbz_cxy/article/details/116703787?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522166633139016800182765413%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=166633139016800182765413&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-116703787-null-null.142^v59^pc_rank_34_1,201^v3^control_2&utm_term=git&spm=1018.2226.3001.4187)