#!/usr/bin/env python
# coding: utf-8
__author__ = 'Danny'

import json
import time
from Util.func import md5, current_time
from config import *
import requests


class Instar:
    def __init__(self):
        self.db = get_mysql()
        self.redis = get_redis()
        self.log = get_logger()
        self.es = get_conf().get("es","url")
        pass

    @staticmethod
    def notify(action, platform, uid, message):
        """
        发送服务端通知
        :param action: 通知类型
        :param uid: 用户在平台的id
        :param platform: 平台名
        :param message: 附加消息
        :return:
        """
        param = {
            "action": action,
            "uid": uid,
            "platform": platform,
            "message": message
        }
        url = "http://notify.instarx.net/live/start"
        res = requests.get(url, params=param)
        res = res.json()
        if res["errno"] != 0:
            print("notify error: " + param)

    def get_bind_platform_user(self, plat_name="huajiao"):
        """
        获取某个平台已经绑定的平台用户id
        :param plat_name: 平台名称
        :return:
        """
        platforms = {"huajiao": 1, "inke": 2}  # 各平台编号，变化很少，这里写死减少数据库查询
        users = []
        all_users_res = self.db.get_all("SELECT uid FROM instar.user_account WHERE pid= %d" % platforms[plat_name])
        for u in all_users_res:
            users.append(int(u["uid"]))
        return users

    def get_all_platform_users(self, plat_name="huajiao", source="mysql"):
        """
        获取某个平台的所有用户id
        :param plat_name:
        :param source:
        :return:
        """
        if source == "mysql":
            _all_users = []
            all_users_res = self.db.get_all("SELECT uid FROM instar.user_" + plat_name)
            for u in all_users_res:
                if plat_name in ["huya"]:
                    _all_users.append(u["uid"])
                else:
                    _all_users.append(int(u["uid"]))
        else:
            _all_users = self.redis.smembers("user_" + plat_name)
        return _all_users


    def get_account(self,pf,uid):
        db = get_mysql()
        sql = "SELECT uid,token FROM instar.spider_account WHERE pf=\"" + pf + "\" and uid=" + uid
        account = db.get_all(sql)
        return account[0]

    def get_account_list(self,pf):
        account_list = []
        db = get_mysql()
        sql = "SELECT uid FROM instar.spider_account WHERE pf=\"" + pf + "\" and status in (0,1)"
        account = db.get_all(sql)
        for item in account:
            account_list.append(str(item["uid"]))
        return account_list

    def update_status(self,pf,uid,value):
        db = get_mysql()
        sql = "update instar.spider_account set status=" + str(value) + " WHERE pf=\"" + pf + "\" and uid="+uid
        db.query(sql)
        db.commit()

    @staticmethod
    def sign(timestamp):
        return md5(str(timestamp) + "InstarX2016")

    def save_live(self, plat, info, data):
        """
        保存直播信息到数据库
        :param plat: 直播平台
        :param info: 直播数据
        :param data: 榜单数据
        :return:
        """
        d = info["feed"]
        # 计算instar指数
        t_s = int(time.mktime(time.strptime(d["publishtime"], "%Y-%m-%d %H:%M:%S")))
        t_e = int(time.mktime(time.localtime()))
        _live_data = {
            "platform": plat,
            "live_id": d["relateid"],
            "uid": info["author"]["uid"],
            "start_time": d["publishtime"],
            "title": d["title"],
            "praises": d["praises"],
            "watches": d["watches"],
            "image": d["image"],
            "location": d["location"],
            "duration": t_e - t_s,
            "source": "rank_spider",
            "timestamp": int(time.time()),
            "tf": data["tf"]
        }
        _live_data["sign"] = self.sign(_live_data["timestamp"])
        res = requests.get("http://notify.instarx.net/live/stop/?", params=_live_data)
        if res.status_code == 200:
            res = res.json()
            if res["errno"] != 0:
                self.log.warn("save live info through our api, error: " + res["message"])
        else:
            self.log.warn("save live info api 500 error")

    def add_living(self, plat, _id, uid):
        """
        添加直播间监控
        :param plat:
        :param _id:
        :return:
        """
        d = {
            "platform": plat,
            "live_id": _id,
            "time": current_time()
        }
        cmd = {
                "cmd": "start "+plat+" "+str(uid)+" "+str(_id)
        }
        #self.redis.sadd("to_living", json.dumps(d))
        #self.redis.lpush("living_rooms_cmds", json.dumps(cmd))
        self.redis.sadd("passerby_living_rooms_cmds", json.dumps(cmd))

    def save2es(self,index,type,es_data):
        url = "".join([self.es,index,'/',type])
        es_data = json.dumps(es_data)
        requests.post(url, data=es_data.replace("\'","\""))
