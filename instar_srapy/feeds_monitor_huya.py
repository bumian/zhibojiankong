#!/usr/bin/env python
# coding: utf-8
__author__ = 'Danny'

from instar import *
from live_platform.Huya import Huya
import time
from Util.func import get_host_name

host_name = get_host_name()
log = get_logger()
redis_ins = get_redis()


def get_monit_list(platform):
    redis_key = host_name + "_" + platform
    log.info("get task list from " + redis_key)
    monit_list = list(redis_ins.smembers(redis_key))
    return monit_list

def run():
    huya = Huya()
    instar = Instar()
    cf = get_conf()
    sent_uid = redis_ins.smembers("passerby_living_rooms")
    follow_list = huya.traverse_living("live",30000)
    send_list = []
    pf = "huya"
    monoit_list = get_monit_list(pf)
    if not follow_list:
        return
    for live in follow_list:
        feed = live
        if True:
            uid = str(feed["uid"])
            if str(feed["privateHost"]) not in monoit_list:
                continue
            if pf+"-"+str(uid) not in sent_uid and uid not in send_list:
                live_id = feed["privateHost"]
                instar.add_living(pf, live_id, uid)
                send_list.append(uid)
                log.info("sent new "+pf+" live " +str(uid)+"," +str(live_id))
    log.info("sent new "+pf+" live total:"+str(len(send_list)))

if __name__ == '__main__':
    run()
    time.sleep(30)
