### 抖音直播间保险助手

#### 弹幕抓取使用
##### 实现原理
1. 利用工具抓取得到定向直播间的弹幕数据
2. 在本地或浏览器新建web socket客户端，与该工具建立web socket连接，实现数据通信
3. iframe内嵌html，通过click事件触发html加载渲染
##### 实践步骤
1. 根据提示下载[抖音弹幕抓取数据推送](https://gitee.com/apebyte/dy-barrage-grab#/apebyte/dy-barrage-grab/blob/master/./BarrageGrab/Modles/JsonEntity/Command.cs)**发行版**或者直接下载使用本项目中的Release_v2.7.5文件夹
2. 同时打开要爬取的抖音直播间和该软件exe可执行文件
3. 在本项目目根目录 python main.py
##### 测试
<img src="./test/Q&A/img1.png" alt="测试img1" width="300" height="200">
<img src="./test/Q&A/img2.png" alt="测试img2" width="300" height="200">

##### 不足
1. 在js代码中建立的web socket客户端无法及时close，目前不影响展示
