#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'

from instar import *
from live_platform.Taobao import Taobao

if __name__ == '__main__':
    db = get_mysql()
    log = get_logger()
    redis_ins = get_redis()
    instar = Instar()
    platform = ["taobao"]
    for pf in platform:
        # 动态产生平台实例
        pf_ins = eval(pf.capitalize() + '()')
        # 获取当前榜单数据保存到redis
        lives_all = pf_ins.traverse_living("live")  # 当前热门榜
        #lives_new = pf_ins.traverse_living("latest")  # 当前最新榜单
        #lives_all = lives_hot + lives_new

        all_plat_users = instar.get_all_platform_users(pf)  # 平台所有用户id
        log.info("total crawled platform user in mysql: " + str(len(all_plat_users)))
        saved_users=[]
        for live in lives_all["dataList"]:
            uid = int(live["data"]["accountId"])
            if uid not in all_plat_users and uid not in saved_users:
                #data = pf_ins.get_user_info(uid)
                #db.insert("user_" + pf,data)
                log.info("new user " + str(uid))
                # 新用户加到redis队列，异步处理
                redis_ins.sadd("new_user_" + pf, uid)
                saved_users.append(uid)
        log.info(pf + " hot live deal completed")
    #db.commit()
    log.info("all platform hot live deal completed")
