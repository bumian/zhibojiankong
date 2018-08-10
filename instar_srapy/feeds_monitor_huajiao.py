#!/usr/bin/env python
# coding: utf-8
__author__ = 'Danny'

from instar import *
from live_platform.Huajiao import Huajiao
import threading
import time

plat = Huajiao()
instar = Instar()
log = get_logger()
redis_ins = get_redis()
limit = 10

def monit(uid,sent_uid):
    log.info("get user feed list " + str(uid))
    feeds = plat.get_user_feeds(uid)
    if feeds:
        res = {
            "errno":0,
            "data":feeds
        }
    else:
        return
    if res and res["errno"] == 0:
        if  len(res["data"]) == 0:
            log.info("no feeds " + str(uid))
            return
        if res["data"][0]["status"] != 1:
            log.info("not living " + str(uid))
            return
        # 主播正在直播，判断是否已经添加
        live_id = res["data"][0]["live_id"]
        if "huajiao-"+str(uid) not in sent_uid:
            instar.add_living("huajiao", live_id, uid)
            # TODO: 一直添加，需要有个方式删除旧数据
            #redis_ins.sadd("sent_huajiao", live_id)
            log.info("sent new live " + str(live_id))
        else:
            log.info("live already sent to room monitor " + str(live_id))
    else:
        log.error("get user feed list error")

def run():
    # 已绑定用户的平台id
    bind_uid_list = redis_ins.smembers("bind_huajiao")
    # 经常上热门的用户
    hot_uid_list = redis_ins.smembers("hot_huajiao")
    monit_list = list(bind_uid_list | hot_uid_list)
    # 已经添加过的直播id
    sent_uid = redis_ins.smembers("passerby_living_rooms")
    log.info("register user num : " + str(len(bind_uid_list)))
    # 查看每一个用户的直播列表
    threads = []
    for i in range(0,len(monit_list)):
        #if i % page_count != page_num:
        #    continue
        uid = monit_list[i]
        t = threading.Thread(target=monit,args=(uid,sent_uid))
        threads.append(t)
    for thread in threads:
        thread.start()
        while True:
             if activeCount() < limit:
                 break
    log.info("bind user feeds monitor end")

if __name__ == '__main__':
    while True:
        run()
        time.sleep(10)
