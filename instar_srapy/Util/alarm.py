#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'


import redis
import sys
import time
import json
import socket, fcntl, struct


desc = {
    "get_hot_list":"存热门位置变化到es，每30秒拉一次热门",
    "add_hot_user_huajiao":"为花椒添加新用户，周期10分钟",
    "add_hot_user_inke":"为映客添加新用户，周期10分钟",
    "add_hot_user_yizhibo":"为一直播添加新用户，周期10分钟",
    "add_hot_user_meipai":"为美拍添加新用户，周期3分钟",
    "spider_health_monitor":"监控spider各个接口的健康状况，周期5分钟",
    "taobao_shop_manager":"淘宝刷每日店铺信息，每日3点执行,周期24小时86400",
    "taobao_midway_sess":"为淘宝刷热门列表提供MIDWAY_SESS，周期4小时"
}

def get_local_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))
    ret = socket.inet_ntoa(inet[20:24])
    return ret

def getRedis():
    redis_config = {
        "host": "redis3.instarx.net",
        "port": 6379,
        "password": "qGNF2V6dhBr7OQcsl8j9iw"
    }
    redis_instance = redis.Redis(redis_config["host"], redis_config["port"], 0, redis_config["password"])
    return redis_instance

def saveInfo(service,cron):
    local_ip = get_local_ip("eth0")
    last_time = int(time.time())
    filed = '-'.join([service,local_ip])
    data = {
        "service": service,
        "host": local_ip,
        "desc": desc.get(service,"暂无描述"),
        "cron": int(cron),
        "last": last_time,
        "author": "chenyong@bitflow.cn"
    }
    redis_instance = getRedis()
    redis_instance.hset("service_health",filed,json.dumps(data))



if __name__ == "__main__":
    service,cron = sys.argv[1:3]
    saveInfo(service, cron)
