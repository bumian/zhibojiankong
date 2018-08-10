#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'

from instar import *
from live_platform.Meipai import Meipai

if __name__ == '__main__':
    db = get_mysql()
    log = get_logger()
    redis_ins = get_redis()
    instar = Instar()
    platform = ["meipai"]
    for pf in platform:
        # 动态产生平台实例
        pf_ins = eval(pf.capitalize() + '()')
        # 获取当前榜单数据保存到redis
        lives_all = pf_ins.traverse_living("live")  # 当前热门榜

        all_plat_users = instar.get_all_platform_users(pf)  # 平台所有用户id
        log.info("total crawled platform user in mysql: " + str(len(all_plat_users)))
        saved_users=[]
        for live in lives_all:
            uid = int(live["live"]["user"]["id"])
            if uid not in all_plat_users and uid not in saved_users:
                #data = pf_ins.get_user_info(uid)
                #db.insert("user_" + pf,data)
                log.info("new user meipai " + str(uid))
                # 新用户加到redis队列，异步处理
                redis_ins.sadd("new_user_" + pf, uid)
                saved_users.append(uid)
        log.info(pf + " hot live deal completed，total:"+str(len(saved_users)))
