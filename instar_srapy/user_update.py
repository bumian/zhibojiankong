#!/usr/bin/env python
# coding: utf-8
__author__ = 'Danny'

from instar import *
from live_platform.Huajiao import Huajiao

if __name__ == "__main__":
    pf_ins = Huajiao()
    redis_ins = get_redis()
    mysql_ins = get_mysql()
    new_user = mysql_ins.get_all("SELECT uid FROM instar.user_huajiao WHERE avatar=''")
    if not new_user:
        print("now need update user")
        exit()
    for user in new_user:
        uid = user["uid"]
        print("starting deal uid " + str(uid))
        user_data = pf_ins.get_user_info(uid)
        user_data["uid"] = int(user_data["uid"])
        user_data["praises"] = int(user_data["praises"])
        user_data["followers"] = int(user_data["followers"])
        user_data["followings"] = int(user_data["followings"])
        user_data["feeds"] = int(user_data["feeds"])
        try:
            mysql_ins.update("user_huajiao", "uid", uid, user_data)
        except Exception as e:
            print "update error"
            print e
        mysql_ins.commit()
