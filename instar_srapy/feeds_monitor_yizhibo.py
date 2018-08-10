#!/usr/bin/env python
# coding: utf-8
__author__ = 'Danny'

from instar import *
from live_platform.Yizhibo import Yizhibo
import time

def run():
    plat = Yizhibo()
    instar = Instar()
    log = get_logger()
    redis_ins = get_redis()
    cf = get_conf()
    #page_num = cf.getint("local","task_page")
    #page_count = cf.getint("local","task_count")

    monit_list = list(redis_ins.smembers("vip_yizhibo"))
    # 已经添加过的直播id
    sent_uid = redis_ins.smembers("passerby_living_rooms")
    log.info("monit user num : " + str(len(monit_list)))
    # 查看每一个用户的直播列表
    for i in range(0,len(monit_list)):
        #if i % page_count != page_num:
        #    continue
        uid = monit_list[i]
        log.info("get user live info " + str(uid))
        live_id = plat.is_user_living(uid)
        if live_id:
            if "yizhibo-"+str(uid) not in sent_uid:
                instar.add_living("yizhibo", repr(str(live_id)), uid)
                log.info("sent new yizhibo live " + str(live_id))
            else:
                log.info("live already sent to room monitor " + str(live_id))
        else:
            log.info("not living " + str(uid))
            continue
    log.info("bind user feeds monitor end")

if __name__ == '__main__':
    while True:
        run()
        time.sleep(5)
