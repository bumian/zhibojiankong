#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'

import requests
from instar import *
import time
import threading

proxy = {"http":"proxy2.instarx.net:8080"}
limit = 5
log = get_logger()

def get_cookie():
    cookie = ""
    url = 'http://www.yizhibo.com/live/h5api/change_one'
    try:
        cookie = dict(requests.get(url).cookies)
    except:
        pass
    return cookie

def gen_random_uid(cookie):
    uid = ""
    url = 'http://www.yizhibo.com/live/h5api/change_one'
    try:
        res = requests.get(url,proxies=proxy,timeout=3,cookies=cookie).text
        live_id = res.split('/')[2].split('.')[0]
    except:
        return uid
    url = "http://www.yizhibo.com/live/h5api/get_basic_live_info"
    param = {
        "scid":live_id
    }
    try:
        res = requests.get(url,params=param,proxies=proxy,timeout=5).json()
        uid = int(res["data"]["memberid"])
    except:
        pass
    return uid

def add_user(all_plat_users,redis_ins,cookie):
    uid = gen_random_uid(cookie)
    if not uid:
        return
    if uid not in all_plat_users:
        log.info("new user " + str(uid))
        redis_ins.sadd("new_user_yizhibo", uid)

def run():
    db = get_mysql()
    redis_ins = get_redis()
    instar = Instar()
    all_plat_users = instar.get_all_platform_users("yizhibo")
    log.info("total crawled platform user in mysql: " + str(len(all_plat_users)))
    threads = []
    cookie = get_cookie()
    if not cookie:
        return
    for i in range(1,1000):
        t = threading.Thread(target=add_user,args=(all_plat_users,redis_ins,cookie))
        threads.append(t)

    for thread in threads:
        thread.start()
        while True:
             if threading.activeCount() < limit:
                 break
             time.sleep(0.01)

if __name__ == "__main__":
    run()
