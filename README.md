# OpenAlien
![version](https://img.shields.io/badge/version-1.0.0-blue)
![license](https://img.shields.io/badge/license-MIT-brightgreen)
![python_version](https://img.shields.io/badge/python-%3E%3D%203.6-brightgreen)
![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
[![](https://img.shields.io/badge/blog-@encoderlee-red)](https://encoderlee.blog.csdn.net)
### 一个免费开源的外星世界(Alien Worlds)自动化挂机合约脚本
![](https://raw.githubusercontent.com/encoderlee/OpenAlien/main/doc/demo1.png)
## 说明
外星世界（Alien Worlds）官网： [https://alienworlds.io](https://alienworlds.io)

之前我们推出过免费开源的农民世界（FarmersWorld）合约脚本:
[https://github.com/encoderlee/OpenFarmer](https://github.com/encoderlee/OpenFarmer)

本次推出外星世界（Alien Worlds）的合约脚本：
[https://github.com/encoderlee/OpenAlien](https://github.com/encoderlee/OpenAlien)

老用户都懂，无需多言

和之前的 OpenFarmer 相比，本次开源的 OpenAlien 彻底脱离了Chrome浏览器运行 

底层的 EOSIO SDK 由原来的 [【eospy】](https://github.com/eosnewyork/eospy) 换成了我们自己开发的 [【eosapi】](https://github.com/encoderlee/eosapi) ，
提高了稳定性和单台电脑的多开数量

欢迎关注我的博客：[https://encoderlee.blog.csdn.net](https://encoderlee.blog.csdn.net)

### 欢迎加入我们的链游QQ群交流讨论：858505473

# 用法

### 使用方法一：

直接点下面链接下载最新版打包版本（或在github页面右侧的【Releases】里找），打包版本只支持Win10或更高版本的操作系统。

[【点我下载】](https://github.com/encoderlee/OpenAlien/releases/download/1.0.0/OpenAlien_1.0.0.zip)

把压缩包里的文件解压出来，先修改配置文件【user.yml】，再双击运行【user.bat】

多开第二个账号，复制【user.yml】为【user2.yml】，复制【user.bat】为【user2.bat】

修改配置文件【user2.yml】为第二个账户的信息，修改【user2.bat】文件，把里面的字符串“user.yml”改为“user2.yml”，然后双击运行【user2.bat】

多开更多账号，以此类推

### 使用方法二：

1.从源码运行，先安装 Python 环境，推荐安装 Python 3.9.13 版本，因为这是我们测试过的版本

下载地址：[https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe](https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe)

安装时记得勾选“Add Python 3.9 to PATH”

2.下载源码，在 github 项目页面上点击绿色按钮【Code】,【Download ZIP】,下载后解压出来

3.双击运行【install_dependencies.bat】安装依赖包，这个步骤每台电脑只需做一次

【注意】安装依赖包前请关闭梯子之类的代理，以免下载出错

4.先修改配置文件【user.yml】，再双击运行【user.bat】

5.多开方法和上面一样，就是复制这两个文件，修改后运行

### 配置文件说明

```yaml
#注意，每个参数名的冒号后面，都有一个空格，修改参数不要丢了空格

# wax节点地址，使用公共节点，有时候会网络不通，或者访问太频繁被限制，出现429错误，可以换节点，或者搭建私有节点
# 公共节点列表：https://wax.eosio.online/endpoints

rpc_domain: https://wax.pink.gg

# cpu代付号,cpu_key填写该代付号私钥，不需要代付则留空
cpu_account:
cpu_key:

# 即使可挖时间到了，也延迟30-90秒再挖
delay1: 30
delay2: 90

# http代理（比如127.0.0.1:10808)
# 给脚本设置HTTP代理，这样可以在一定程度上解决公共节点限制访问的问题，不需要则留空
proxy:
proxy_username:
proxy_password:

# 下面三项改为你的账号信息
# account是wax云钱包账号名
# token是什么，先在chrome浏览器中手工登录WAX云钱包  https://wallet.wax.io/dashboard
# 然后在chrome浏览器中输入地址导航到： https://all-access.wax.io/api/session
# 把token复制出来填到下面
# charge_time是采矿间隔，单位秒，登录alienworlds官网，打开工具页面，就可以看到，按实际情况填写

account: gts3c.c.wam
token: EHuyFHPcLpSNUJ4BLSUnPxxxxxxxxxxxx
charge_time: 336

```

公共节点列表：[https://wax.eosio.online/endpoints](https://wax.eosio.online/endpoints)

注意，从 Chrome 浏览器中复制出 token 后，浏览器可以点右上角叉叉关闭，但不要点退出登录该账号，也不要直接重新登录另外一个账号，不然之前的账号会掉线。

如果需要在 Chrome 中登录第二个账号，请使用 Chrome 的多用户功能登录

Chrome 多用户相关文章：[https://www.chensnotes.com/chrome-profile.html](https://www.chensnotes.com/chrome-profile.html)

### 常用工具

【nodepad++】[https://notepad-plus-plus.org/downloads/v8.4.2](https://notepad-plus-plus.org/downloads/v8.4.2)

文本编辑器，编辑修改【user.yml】配置文件更愉快

【cmder】[https://cmder.net](https://cmder.net)

替代 windows 自带的 cmd 命令行工具，防止脚本假死

系统自带的 cmd 命令行工具，默认开启快速编辑模式，有时候因为鼠标键盘意外操作，

日志会留在一个地方，处于假死状态，导致脚本不能持续运行，换用【cmder】解决该问题

### 常见错误
1.交易错误

交易错误的原因有很多种，比如智能合约报错，CPU不足，秘钥不对，WAX节点限制等

连续出现5次交易出错，脚本将停止，此时需要手工检查问题或更换节点

为什么不一直继续反复重试？因为反复提交错误的交易，公共节点就会把你拉黑，需要24小时之后才能使用该节点了

自行架设 WAX 私有节点，会在一定程度上改善此问题

2.节点错误

节点错误，尤其是 429 错误，主要是因为你一个IP下面同时跑的号太多了，请求频繁，被节点拉黑

公共节点毕竟是面向全球的免费服务，为了防止滥用，做了很多限制

每N个号设置一个代理IP，或者自行架设 WAX 私有节点，会在一定程度上改善此问题

### 欢迎打赏

wax钱包地址：

m45yy.wam

