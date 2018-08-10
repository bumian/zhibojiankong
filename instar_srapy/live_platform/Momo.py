#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'
import urllib
from Util.func import *
from Platform import Platform
import requests
import time
import json

class Momo(Platform):
    def __init__(self):
        Platform.__init__(self)
        self.platform = "momo"
        pass

    api = {
        "live_list":"https://live-api.immomo.com/guestv2/index/index",
        "new_list":"https://live-api.immomo.com/guestv2/index/newLive",
        "nearby_list": "https://live-api.immomo.com/guestv2/index/nearbyList",
        "user_info": "https://web.immomo.com/webmomo/api/scene/profile/infosv2",
        "or_user_info":"https://live-api.immomo.com/v2/user/card/lite",
        "get_session":"https://live-api.immomo.com/v2/user/login_guest",
        "get_uid":"http://ihani.tv/h5/v2/share/home/shared",
        "get_cid": "https://web.immomo.com/"
    }
    accounts = []
    def set_account(self):
        """
        设置账号
        :return:
        """
        pass
    def get_session(self):
         sessionid = ""
         api_name = "get_session"
         param = {
            "uuid":"5eb42b52-0c3c-3d28-a79b-8558222c6d51",
             "lng":"-1.0",
             "lat":"-1.0"
         }
         header = {
             "User-Agent": "Molive/20160325 Android/1 (8692-A00; Android 5.1.1; Gapps 0; zh_CN; 2)",
             "Cookie":"SESSIONID=3d7efdfe4e896c0090b9747ab1fef6f3",
             "host":"live-api.immomo.com"
         }
         api_name = "get_cid"
         res = s_request(api["get_session"],'POST',params=param,headers=header,verify=False)
         res = s_check(error,s_res,self.platform,api_name,self.log)

         if not res:
             return cId

         data = res["data"]["sessionid"]
         sessionid =  data.encode('utf8')
         return sessionid

    def get_cid(self):
        cId = ""
        try:
            res = requests.get(self.api["get_cid"])
        except:
            return cId

        cookie = dict(res.cookies)
        cId = cookie["cId"]
        return cId

    def get_uid(self,live_id):
        header = {
            "User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36"
        }
        param = {
            "roomid":live_id
        }
        try:
            html = s_request(self.api["get_uid"],params=param,headers=header).text
            bsObj = BeautifulSoup(html,"html.parser")
            data = bsObj.find(attrs={'class':'hani_info'})
            if not data:
                data = bsObj.find(attrs={'class': 'idnum'})
                p = str(data)
                uid = int(p.split(':')[1].split('<')[0])
            else:
                p =  str(data.p)
                uid =  int(p.split(':')[1].split('<')[0])
        except:
            uid = ""
            self.warn("momo covert roomid to uid error,roomid:"+str(live_id))

        return uid

    def get_user_info(self, uid):
        """
        获取用户信息
        :param uid: user id
        :return:
        """
        time.sleep(self.sleep_time)
        param = {
            "stid": uid
        }
        self.headers["Cookie"] = "cId="+self.get_cid()
        # api_name = "get_user_info"
        # error,res = s_request(self.api["user_info"], data=param,headers=self.headers)
        # res = s_check(error,res,self.platform,api_name,self.log)
        res = requests.post(self.api["user_info"], data=param,headers=self.headers).json()

        data = []
        if not res:
            return data

        try:
            d = res["data"]
            if not d:
                return data
            data = {
                "uid": uid,
                "followers": s_int(s_get(d,"fos")),
                #"verified": s_get(d,"verified"),
                "nickname": d["name"],
                #"level": d["level"],
                #"gender": "M" if d["gender"] == "m" else "F",
                #"followings":s_int(s_get(d,"friends_count")),
                "avatar": s_get(d,"avatar"),
                #"signature": s_get(d,"description")
            }
        except:
            self.error("meipai get_user_info, " + str(uid) + "," + json.dumps(res))
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
        self.info("meipai get host list:"+str(len(data)))
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
        error,res = s_request(self.api["live_info"], params=param)

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
    def get_user_gift_info(self, live_id):
        """
        获取用户收礼物信息
        :param uid: 用户id
        :return:
        """
        time.sleep(self.sleep_time)
        param = {
            "id": live_id
        }
        param = dic_merge(self.param_common, param)

        data = []
        api_name = "get_user_gift_info"
        error,res = s_request(self.api["gift_info"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return data

        try:
            d = res["data"]
            data = {
                "send":0,
                "get":s_int(s_get(d,"meiBean"))
            }
        except:
            self.error("meipai get_gift_info, " + str(uid) + "," + json.dumps(res))
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
