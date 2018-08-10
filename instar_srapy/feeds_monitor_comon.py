#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'

from instar import *
from Util.func import get_host_name
from live_platform.Huajiao import Huajiao
from live_platform.Inke import Inke
from live_platform.Yizhibo import Yizhibo
from live_platform.Bilibili import Bilibili
import threading
import time
import sys

cf = get_conf()
instar = Instar()
log = get_logger()
redis_ins = get_redis()
host_name = get_host_name()

platforms = {
    "huajiao":10,
    "inke":6,
    "yizhibo":10,
    "bilibili":6
}

def check_param(param):
    result = True
    if param not in platforms.keys():
        log.error("unsupport platform")
        result = False
    return result

def get_monit_list(platform):
    redis_key = host_name + "_" + platform
    log.info("get task list from " + redis_key)
    monit_list = list(redis_ins.smembers(redis_key))
    return monit_list

def monit(index,uid,sent_uid,pf_ins):
        live_id = pf_ins.is_user_living(uid)
        pf_name = pf_ins.platform
        if live_id:
            if pf_name+"-"+str(uid) not in sent_uid:
                instar.add_living(pf_name, live_id, uid)
                log.info("sent new "+pf_name+" live " +str(uid)+"," +str(live_id))

def run(platform):
        threads = []
        sent_uid = redis_ins.smembers("passerby_living_rooms")
        limit = platforms[platform]
        pf_ins = eval(platform.capitalize() + '()')
        monit_list = get_monit_list(platform)

        log.info("register user of "+platform+" num : " + str(len(monit_list)))
        for index,uid in enumerate(monit_list):
            t = threading.Thread(target=monit,args=(index,uid,sent_uid,pf_ins))
            threads.append(t)

        log.info("bind "+platform+" user feeds monitor start,thread limit:"+str(limit))

        for thread in threads:
            thread.start()
            while True:
                 if threading.activeCount() < limit:
                     break
                 time.sleep(0.01)

        log.info("bind "+platform+" user feeds monitor end")

if __name__ == '__main__':
    platform = sys.argv[1]
    if check_param(platform):
        while True:
            run(platform)
            time.sleep(10)
