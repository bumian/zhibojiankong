#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'

from instar import *
from live_platform.Huajiao import Huajiao
from live_platform.Inke import Inke
from live_platform.Yizhibo import Yizhibo
import threading
import time


instar = Instar()
log = get_logger()
redis_ins = get_redis()
cf = get_conf()
limit = 10

def monit(index,uid,sent_uid,pf_ins):
        live_id = pf_ins.is_user_living(uid)
        pf_name = pf_ins.platform
        if live_id:
            if pf_name+"-"+str(uid) not in sent_uid:
                instar.add_living(pf_name, live_id, uid)
                log.info("sent new "+pf_name+" live " +str(uid)+"," +str(live_id))
            else:
                #log.info("live already sent to room monitor " + str(live_id))
                pass
        else:
            return

def run():
    sent_uid = redis_ins.smembers("passerby_living_rooms")
    platforms = ["huajiao","inke","yizhibo"]
    for pf in platforms:
        threads = []
        pf_ins = eval(pf.capitalize() + '()')
        redis_key = cf.get("redis","vip_"+pf)
        monit_list = list(redis_ins.smembers(redis_key))
        log.info("register user of "+pf+" num : " + str(len(monit_list)))
        for index,uid in enumerate(monit_list):
            t = threading.Thread(target=monit,args=(index,uid,sent_uid,pf_ins))
            threads.append(t)
        log.info("bind "+pf+" user feeds monitor start")
        for thread in threads:
            thread.start()
            while True:
                 if threading.activeCount() < limit:
                     break
                 time.sleep(0.01)
        log.info("bind "+pf+" user feeds monitor end")

if __name__ == '__main__':
    while True:
        run()
        time.sleep(10)
