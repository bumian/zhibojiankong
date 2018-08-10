#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'
import urllib
from Util.func import *
from Platform import Platform
import requests
import time
import json
import re

class Meipai(Platform):
    def __init__(self):
        Platform.__init__(self)
        self.platform = "meipai"
        pass
    param_common = {"lc": "3000000000006495", "cv": "IK2.9.60_Android", "cc": "TG36415", "ua": "htcHTCT329t", "uid": "53438311", "sid": "211aHEWUIJe6E95Cq4KI6Ji2NBwc2i0c4aGko2Rgi2HjIxkv7V1aG",
                    "devi": "55895025256510", "imsi": "370270000000000", "imei": "867895025256510", "icc": "89514103211118510721", "conn": "WIFI", "vv": "1.0.3-2016060211417.android",
                    "aid": "66ff6d923d499104", "osversion": "android_17", "proto": "4", "smid": "DuzvvftLIdB0GRrFsBY2OaaaazGxLfnLE2vPS0mxzSoKNWbzoRIvS531y6avt3bHAiRP7gGHedExL96Q616rsqkr"}
    api = {
        "live_list": "https://newapi.meipai.com/live_channels/programs.json",
        "live_info": "https://newapi.meipai.com/lives/show.json",
        "user_info": "https://newapi.meipai.com/users/show.json",
        "user_feeds":"https://newapi.meipai.com/share_lives/user_feeds.json",
        "gift_info":"https://www.meipai.com/fans_rank/user",
        "feed_list":"http://www.meipai.com/lives/get_channels_program"
    }
    accounts = []
    def set_account(self):
        """
        设置账号
        :return:
        """
        pass
    def get_user_info(self, uid):
        """
        获取用户信息
        :param uid: user id
        :return:
        """
        time.sleep(self.sleep_time)
        param = {
            "id": uid
        }
        param = dic_merge(self.param_common, param)

        data = []
        api_name = "get_user_info"
        error,res = s_request(self.api["user_info"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        try:
            d = res
            data = {
                "uid": uid,
                "followers": s_int(s_get(d,"followers_count")),
                "verified": s_get(d,"verified"),
                "nickname": d["screen_name"],
                "level": d["level"],
                "gender": "M" if d["gender"] == "m" else "F",
                "followings":s_int(s_get(d,"friends_count")),
                "avatar": s_get(d,"avatar"),
                "signature": s_get(d,"description"),
                "city":get_city(d["city"]),
                "province":get_city(d["province"])
            }
        except:
            self.error("meipai get_user_info, " + str(uid) + "," + json.dumps(res))
        return data

    def get_live_list(self):
        param = {
            "page" : 1,
            "count" : 100
        }
        param = dic_merge(self.param_common, param)

        data = []
        api_name = "get_feed_list"
        while True:
            error,res = s_request(self.api["feed_list"], params=param)
            res = s_check(error,res,self.platform,api_name,self.log)
            if not res:
                break
            param["page"] = param["page"] +1
            data.extend(res)

        self.log.info("meipai get live list:"+str(len(data)))
        return data


    def traverse_living(self, live_type="live",limit=200):
        """
        遍历获取当前所有直播，保存到redis
        :param  $live_type string 榜单类型
        :return:
        """
        param = {
            "page" : 1
        }
        param = dic_merge(self.param_common, param)

        data = []
        #api_name = "get_hot_list"
        #error,res = s_request(self.api["live_list"], params=param)
        #res = s_check(error,res,self.platform,api_name,self.log)
        # if not res:
        #     return data
        while len(data) < limit:
            res = requests.get(self.api["live_list"], params=param)
            try:
                res = res.json()
                param["page"] = param["page"] +1
            except:
                continue
            if not res:
                break
            data.extend(res)
            time.sleep(1)
        self.log.info("meipai get host list:"+str(len(data)))
        return data

    def get_live_info(self, live_id, uid):
        """
        获取直播信息, 同时包含直播的状态以判断直播是否结束
        :param live_id: 直播 id
        :param uid: 用户id
        :return:
        """
        time.sleep(self.sleep_time)
        param = {
            "id": live_id
        }

        data = []
        api_name = "get_live_info"
        error,res = s_request(self.api["live_info"],'GET',2,params=param)

        if "400" in error:
            return data

        res = s_check(error,res,self.platform,api_name,self.log)



        if not res:
            return self.UNKNOWN_ERROR

        try:
            d = res
            data = {
                "live_id": live_id,
                "uid": uid,
                "title": s_get(d,"caption"),
                "praises": d.get("likes_count",0),
                "watches": d.get("plays_count",0),
                "image": s_get(d,"cover_pic"),
                "duration": int(s_get(d,"time")),
                "location": "",
                "is_end": 0 if d["is_live"] else 1
            }
        except:
            self.error("meipai get_live_info error," + str(live_id) + " ," + json.dumps(res))
            return self.UNKNOWN_ERROR
        return data
    def get_user_gift_info(self, uid):
        """
        获取用户收礼物信息
        :param uid: 用户id
        :return:
        """
        time.sleep(self.sleep_time)
        param = {
            "id": uid
        }
        header = {
            "User-Agent":'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
        }

        data = []
        api_name = "get_user_gift_info"
        error,res = s_request(self.api["gift_info"], params=param, headers=header)

        if not res:
            return data

        try:
            meibean = re.findall('receive_info":{"beans":"<b>'+r"(\d+)",res.content)[0]
            data = {
                "send":0,
                "get":int(meibean)
            }
        except Exception,e:
            self.error("meipai get_gift_info, " + str(uid) + "," + str(e))
        return data

    def get_user_feeds(self, uid):
        """
        获取用户直播列表
        :param uid:
        :return: 整理后的数据
        """
        time.sleep(self.sleep_time)
        param = {
            "uid": uid
        }
        data = []
        api_name = "get_user_feeds"
        error,res = s_request(self.api["user_feeds"],headers=self.headers, params=param)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return data

        d = res
        if s_get(d,"lives"):
            data = s_get(d,"lives")
        return data

    def is_user_living(self, uid):
        """
        判断是否正在直播
        :param uid:
        :return: array
        """
        time.sleep(self.sleep_time)
        live_id = ""
        feeds = self.get_user_feeds(uid)
        if not feeds:
            return live_id
        try:
            status = feeds[0]["is_live"]
            live_id = feeds[0]["id"] if status else ""
        except:
            self.error("meipai is_user_living error, " + str(uid) + "," + str(feeds))
        return live_id

    def host_list_format(self,time_stamp,lives_hot):
        """
        热门榜单列表格式化，用于存es
        :param time_stamp
        :param lives_hot
        :return json
        """
        data = {}
        es_data = []
        pos = 1
        for item in lives_hot:
            uid = int(item["live"]["user"]["id"])
            data = {
                    "time_stamp":time_stamp,
                    "uid":uid,
                    "pos":pos
                }
            es_data.append(data)
            pos = pos + 1
        return es_data

if __name__ == '__main__':
    meipai = Meipai()
    print meipai.get_user_info(1080072512)
