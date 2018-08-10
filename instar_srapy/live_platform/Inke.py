#!/usr/bin/env python
# coding: utf-8

__author__ = 'Danny'
import urllib
from Util.func import *
from Platform import Platform
import requests
import time
import json

class Inke(Platform):
    def __init__(self):
        Platform.__init__(self)
        self.platform = "inke"
        self.cache_key = cache_key()
        self.live_type = ""
        self.sleep_time = 0.5
        pass

    param_common = {"lc": "3000000000006495", "cv": "IK2.9.60_Android", "cc": "TG36415", "ua": "htcHTCT329t", "uid": "53438311", "sid": "211aHEWUIJe6E95Cq4KI6Ji2NBwc2i0c4aGko2Rgi2HjIxkv7V1aG",
                    "devi": "55895025256510", "imsi": "370270000000000", "imei": "867895025256510", "icc": "89514103211118510721", "conn": "WIFI", "vv": "1.0.3-2016060211417.android",
                    "aid": "66ff6d923d499104", "osversion": "android_17", "proto": "4", "smid": "DuzvvftLIdB0GRrFsBY2OaaaazGxLfnLE2vPS0mxzSoKNWbzoRIvS531y6avt3bHAiRP7gGHedExL96Q616rsqkr"}

    api = {
        "live_list": "http://service.inke.com/api/live/simpleall",
        "theme_list":"http://service.inke.com/api/live/themesearch",#2F1AC028945B9BA9-xingqing|AFCC0BC263924F20-caiyi
        "near_recommend":"http://service.inke.com/api/live/near_recommend?uid=10",
        #"live_info": "http://webapi.busi.inke.cn/web/live_share_pc",
        "live_info":"http://service.inke.com/api/live/info",
        "user_info": "http://service.inke.com/api/user/info",
        "follow_info":"http://service.inke.com/api/user/relation/numrelations",
        "user_gift_info": "http://service.inke.com/api/statistic/inout",
        "user_feeds": "http://service.inke.com/api/record/list",
        "is_user_living": "http://service.inke.com/api/live/now_publish",
        #"add_follow":"http://service.inke.com/api/user/relation/follow",
        "add_follow":"http://webapi.busi.inke.cn/web/live_follow_pc",
        "get_follow_list":"http://service.inke.com/api/live/homepage",
        "user_tags":"http://service.inke.com/user/label/TopLabels",
        "view_num":"http://service.inke.com/api/live/statistic"

    }

    accounts = []

    def set_account(self):
        """
        设置账号
        :return:
        """
        pass
    def get_user_tags(self, uid):
        """
        获取用户标签
        :param uid: user id
        :return:
        """
        param = {
            "host_uid": uid
        }
        param = dic_merge(self.param_common, param)
        data = []
        api_name = "get_user_info-user_tags"
        error,s_res = s_request(self.api["user_tags"],params=param)
        res = s_check(error,s_res,self.platform,api_name,self.log)
        if not res:
            return data
        if res["dm_error"] == 0:
            data = res.get("label_list","")
        else:
            self.error("inke get_user_tags, " + str(uid) + "," + res["error_msg"])
        return data


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

        data = {}
        api_name = "get_user_info-user_info"
        error,s_res = s_request(self.api["user_info"],params=param)
        res = s_check(error,s_res,self.platform,api_name,self.log)

        if not res:
            return data

        api_name = "get_user_info-follow_info"
        error,s_res = s_request(self.api["follow_info"],params=param)
        res2 = s_check(error,s_res,self.platform,api_name,self.log)

        if not res2:
            return data
        if res["dm_error"] == 0:
            d = res["user"]
            nick = d["nick"]
            if not nick:
                return data
            avatar = s_get(d,"portrait")
            prefix = "http://img.meelive.cn/"
            tags = self.get_user_tags(uid)
            data = {
                "uid": uid,
                "signature": d["description"],
                "nickname": nick,
                "gender": "F" if d["gender"] == 0 else "M",
                "city": d["location"],
                "level": d["level"],
                "avatar": avatar if "http" in avatar else prefix+avatar,
                "followings": res2["num_followings"],
                "followers": res2["num_followers"],
                "tags": json.dumps(tags) if tags else ""
            }
            # TODO: 粉丝关注数
        else:
            self.error("inke get_user_info, " + str(uid) + "," + res["error_msg"])
        return data

    def traverse_living(self, live_type="live"):
        """
        遍历获取当前所有直播，保存到redis
        :param  $live_type string 榜单类型
        :return:
        """
        data = []
        api_name = "hot_list"
        error,res = s_request(self.api["live_list"])
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return data

        if res["dm_error"] == 0:
            data = res["lives"]
        return data

    def near_recommend(self):
        """
        获取附近的人信息
        :param  $live_type string 榜单类型
        :return:
        """
        data = []
        api_name = "near_recommend"
        error,res = s_request(self.api["near_recommend"])
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return data

        if res["dm_error"] == 0:
            data = res["lives"]

        return data
    def get_view_num(self,live_id,uid):
        """
        获取直播观看人数
        :param live_id: 直播 id
        :return:
        """
        time.sleep(self.sleep_time)
        param = {
            "id": live_id
        }
        data = []
        api_name = "get_view_num"
        error,s_res = s_request(self.api["view_num"],'GET',2,params=param)
        res = s_check(error,s_res,self.platform,api_name,self.log)

        if not res:
            return self.UNKNOWN_ERROR

        if res["dm_error"] == 0:
            data = {
                "live_id": live_id,
                "view_num": res.get("viewd_num",0)
                }
        else:
            self.error("inke get_view_num error, " + str(live_id) + " ," + res["error_msg"])
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
        param2 = {
            "id": uid
        }

        data = []
        api_name = "get_live_info-live_info"
        error,s_res = s_request(self.api["live_info"],'GET',2,params=param)
        res = s_check(error,s_res,self.platform,api_name,self.log)

        if not res:
            return self.UNKNOWN_ERROR

        api_name = "get_live_info-follow_info"
        error,s_res = s_request(self.api["follow_info"],'GET',2,params=param2)
        res2 = s_check(error,s_res,self.platform,api_name,self.log)

        if not res2:
            return self.UNKNOWN_ERROR

        if res["dm_error"] == 0:
            d = res["live"]
            avatar = d["creator"].get("portrait","")
            prefix = "http://img.meelive.cn/"
            data = {
                "live_id": live_id,
                "uid": uid,
                "start_time": "",
                "title": d.get("name",""),
                "praises": 0,
                "watches": d["online_users"],
                "image": avatar if "http" in avatar else prefix+avatar,
                "duration": 0,
                "city": d["creator"].get("location",""),
                "is_end": 0 if d["status"] > 0 else 1,
                "extends":{
                    "followings": res2["num_followings"],
                    "followers": res2["num_followers"]
                }
            }
        else:
            self.error("inke get_live_info error, " + str(live_id) + " ," + res["error_msg"])
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
        param = dic_merge(self.param_common, param)

        data = []
        api_name = "get_user_gift_info"
        error,res = s_request(self.api["user_gift_info"],params=param)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return data

        if res["dm_error"] == 0:
            data = {
                "send": res["inout"]["gold"],
                "get": res["inout"]["point"]
            }
        else:
            self.error("get_user_gift_info, " + str(uid) + "," + res["error_msg"])
        return data

    def get_user_feeds(self, uid):
        """
        获取用户直播列表
        :param uid:
        :return: 整理后的数据
        """
        time.sleep(self.sleep_time)
        param = {
            "count": 20, "type": 0, "id": uid, "start": 0
        }
        param = dic_merge(self.param_common, param)

        data = []
        api_name = "get_user_feeds"
        error,res = s_request(self.api["user_feeds"],params=param)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return data

        if res["dm_error"] == 0:
            records = res["records"]
            for d in records:
                data.append({
                    "uid": uid,
                    "live_id": int(d["id"]),
                    "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(d["create_time"])),
                    "title": d["name"]
                })
        return data

    def is_user_living(self, uid):
        """
        判断是否正在直播
        :param uid:
        :return: array
        """
        time.sleep(self.sleep_time)
        param = {
            "id": uid,
            "multiaddr": 1,
        }

        live_id = ""
        api_name = "is_user_living"
        error,res = s_request(self.api["is_user_living"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return live_id

        if res["dm_error"] == 0:
            try:
                d = res["live"]
                live_id =  d["share_addr"].split('&')[1].split('=')[1]
            except:
                 pass

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
            uid = int(item["creator"]["id"])
            data = {
                    "time_stamp":time_stamp,
                    "uid":uid,
                    "pos":pos
                }
            es_data.append(data)
            pos = pos + 1
        return es_data

    def get_follow_list(self,uid):
        """
        拉关注列表
        :param uid
        :return json
        """
        param = {
            "uid":uid,
            "type":"1"
        }
        data = []
        api_name = "get_follow_list"
        error,res = s_request(self.api["get_follow_list"],params=param)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return data

        if res["dm_error"] == 0 and len(res["lives"]) > 0:
            feeds = res["lives"]
            for feed in feeds:
                data.append({
                    "uid": feed["creator"]["id"],
                    "live_id": feed["id"],
                    "status": 1 if feed["status"] > 0 else 0
                })

        return data

    def add_follow(self,suid,duid):
        """
        添加关注
        :param suid
        :param duid
        :return json
        """
        # param = {
        #     "uid": duid
        # }
        #
        result = ""
        #
        # s_account = self.instar.get_account(self.platform,suid)
        # if not s_account:
        #     return result
        #     self.log.error("inke add_follow error:no user in db,suid="+str(suid))
        #
        # self.headers["Cookie"] = "_inke_=" + s_account["token"]
        #
        # api_name = "add_follow"
        # error,res = s_request(self.api["add_follow"],params=param,headers=self.headers)
        # res = s_check(error,res,self.platform,api_name,self.log)
        param = {
            "platform": "inke",
            "suid": suid,
            "duid": duid
        }
        res = requests.get("http://172.16.0.18/add_follow",params=param).json()
        if res["errno"] == 0:
            return res["data"]
        else:
            return result

        if not res:
            return result

        if res["error_code"] == 0 or res["error_code"] == 1099010021:
            result = {
                "msg":res["message"],
                "time": int(time.time())
            }
        elif res["error_code"] == 1099010020:
            self.log.error("inke add_follow error:"+str(res["message"])+" code:"+str(res["error_code"])+" suid:"+str(suid)+" duid:"+str(duid))
            self.instar.update_status("inke",suid,-1)
        else:
            self.log.error("inke add_follow error:"+str(res["message"])+" code:"+str(res["error_code"])+" suid:"+str(suid)+" duid:"+str(duid))
        return result

if __name__ == '__main__':
    inke = Inke()
