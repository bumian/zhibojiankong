#instar_scrapy 花椒爬虫

##环境
需要先运行setup.sh来安装oneapm监控程序和其他python库

##启动

###web接口
入口文件：`web_service.py`
提供爬取直播平台的代理接口
包括用户基本信息、直播基本信息、直播间详细数据
两种启动方式：
1. 运行`restart.sh`
2. 用pm2管理： `pm2 start web_service.py -x --interpreter python --name 'spider_api'`

###榜单轮询爬虫
入口文件: `get_living.py`
启动方式：
1. 通过crontab, 设置一分钟执行一次
2. 通过crontab.sh 可实现几秒执行一次


###用户直播列表轮询爬虫
入口文件: `feeds_monitor.py`
设置crontab: `* * * * * cd dir && python feeds_monitor.py`