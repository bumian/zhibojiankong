#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'

from instar import *
from live_platform.Huajiao import Huajiao
from live_platform.Inke import Inke
from live_platform.Yizhibo import Yizhibo
import sys
import threading
import time

instar = Instar()
log = get_logger()
redis_ins = get_redis()
thread_limit = {
    "huajiao":10,
    "inke":6,
    "yizhibo":15
}
send_list = []


platforms = ["huajiao","inke","yizhibo"]

def save_feeds_log(log_data):
    instar.save2es("feeds_monitor","log",log_data)


def check_param(param):
    result = True
    if param not in platforms:
        log.error("unsupport platform")
        result = False
    return result

def add_live(uid,sent_uid,pf_ins):
    global send_list
    follow_list = pf_ins.get_follow_list(uid)
    pf = pf_ins.platform
    if not follow_list:
        return
    for feed in follow_list:
        if feed["status"] == 1:
            uid = feed["uid"]
            if pf+"-"+str(uid) not in sent_uid and uid not in send_list:
                live_id = feed["live_id"]
                instar.add_living(pf, live_id, uid)
                send_list.append(uid)
                log.info("sent new "+pf+" live " +str(uid)+"," +str(live_id))

def run(pf):
    sent_uid = redis_ins.smembers("passerby_living_rooms")
    limit = thread_limit.get(pf,3)
    global send_list
    send_list = []
    threads = []
    uid_list = instar.get_account_list(pf)
    pf_ins = eval(pf.capitalize() + '()')

    for uid in uid_list:
        t = threading.Thread(target=add_live,args=(uid,sent_uid,pf_ins))
        threads.append(t)

    start_time = int(time.time())
    log.info("bind "+pf+" user feeds monitor start,user:"+str(len(uid_list))+",thread limit:"+str(limit))

    for thread in threads:
        thread.start()
        while True:
             if threading.activeCount() < limit:
                 break
             time.sleep(0.01)

    log.info(pf+" monit task end,sent:"+str(len(send_list)))
    end_time = int(time.time())
    log_data = {
        "platform":pf,
        "time_stamp":end_time,
        "run_time": end_time - start_time,
        "sent":len(send_list)
    }
    save_feeds_log(log_data)


if __name__ == '__main__':
    platform = sys.argv[1]
    if check_param(platform):
        run(platform)
        time.sleep(10)
