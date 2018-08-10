#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'
from Util.func import *
import requests
import random
import json
import time
from Platform import Platform

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class Tmall(Platform):
    def __init__(self):
        Platform.__init__(self)
        self.platform = "tmall"
        self.cache_key = cache_key()
        self.live_type = ""
        pass

    param_sign = {
        "t": "",
        "api": "",
        "v": "",
        "data": "",
        "sign":""
    }

    param_common = {
        "appKey": "12574478",
        "type": "json",  # 页面调用的是jsonp
        "timeout": 20000,
        "callback": "mtopjsonp2",
        }

    api = {
        "daren_info":"mtop.guide.daren.hompage.info",
        "item_list": "mtop.mediaplatform.video.livedetail.itemlist",
        "live_info": "mtop.guide.video.liveDetail",
        "video_list": "mtop.mediaplatform.live.videolist",
        "base_url": "http://api.m.taobao.com/h5/",
        "hot_list": "https://taobaolive.taobao.com/api/more_videos/1.0?page=200",
        "get_token": "http://api.m.taobao.com/h5/mtop.mediaplatform.live.videolist/1.0/"
        #"get_token":"https://acs.m.taobao.com/h5/mtop.mediaplatform.live.encryption/1.0/"
    }


    def get_token(self):
        token_list = self.redis_ins.get("taobao_token")
        token_list = eval(token_list)
        token_item = token_list[random.randint(0,19)]
        token = token_item["token"]
        token_enc = token_item["token_enc"]

        return token,token_enc

    def set_account(self,api,v,data):
        """
        设置账号
        :return:
        """
        token,token_enc = self.get_token()
        self.headers["Cookie"] = token+";"+token_enc+";"
        self.param_sign["t"] = str(int(time.time()) * 1000 + random.randint(100, 999))
        self.param_sign["v"] = v
        self.param_sign["data"] = data
        self.param_sign["api"] = api
        self.param_sign["sign"] = md5(token.split("=")[1].split('_')[0] + "&" + self.param_sign["t"] + \
                            "&" + self.param_common["appKey"] + "&" + data)

    def get_live(self, offset=0):
        """
        获取热门及最新榜单直播列表
        :param offset:
        :return:
        """
        pass


    def save_rank_feeds(self, feeds, index):
        """
        保存直播榜单到redis
        :param feeds:
        :param index:
        :return:
        """
        pass

    def traverse_living(self, live_type="live"):
        """
        获取淘宝热门用户列表
        :param  $live_type string 榜单类型
        :return:
        """
        res = requests.get(self.api["hot_list"])
        res = res.json()
        data = {}
        if res["result"].get("success"):
            data = res["result"].get("model")
        return data


    def get_user_info(self, uid):
        """
        获取淘宝用户信息
        :param uid: user id
        :return:
        """
        #time.sleep(self.sleep_time)
        self.set_account(self.api["live_info"],"2.0",str({"creatorId": int(uid)}))
        url = self.api["base_url"]+self.api["live_info"]+"/2.0/"
        param = dic_merge(self.param_sign, self.param_common)
        try:
            res = requests.post(url, data=param, headers=self.headers,proxies=self.proxies,timeout=self.timeout)
        except:
            res = ""
        data = {}
        if not self.check_res(res):
            self.set_account(self.api["live_info"],"2.0",str({"creatorId": int(uid)}))
            param = dic_merge(self.param_sign, self.param_common)
            res = requests.post(url, data=param, headers=self.headers)


        if self.check_res(res):
            res = res.json()
            d = res["data"]
            data["uid"] = d.get("accountId")
            data["followers"]= d["broadCaster"].get("fansNum")
            data["city"] = d.get("location") if d.get("location") else ""
            data["avatar"] = d["broadCaster"].get("headImg") if \
                            d["broadCaster"].get("headImg") else ""
            data["verified"] = d["broadCaster"].get("v")
            data["nickname"] = d["broadCaster"].get("accountName")
            data["accountdes"] = d["broadCaster"].get("accountDes") if \
                                d["broadCaster"].get("accountDes") else ""
            #data["type"] = d["broadCaster"].get("type")
            data["hotsnum"] = d["broadCaster"].get("hotsNum")
        else:
            self.log.warn("tmall get user info api error: " + str(res.text))
        daren = self.get_daren_info(uid)
        return dic_merge(data,daren)

    def get_live_info(self, live_id, uid):
        """
        获取直播信息
        :param live_id: 直播 id
        :param uid: 用户id
        :return:
        """
        time.sleep(0.5)
        self.set_account(self.api["live_info"],"2.0",str({"liveId": str(live_id),"creatorId": int(uid)}))
        url = self.api["base_url"]+self.api["live_info"]+"/2.0/"
        param = dic_merge(self.param_sign, self.param_common)
        data = {}
        try:
            res = requests.post(url, data=param, headers=self.headers,proxies=self.proxies,timeout=self.timeout)
        except:
            res = ""

        if not self.check_res(res):
            self.set_account(self.api["live_info"],"2.0",str({"liveId": str(live_id),"creatorId": int(uid)}))
            param = dic_merge(self.param_sign, self.param_common)
            res = requests.post(url, data=param, headers=self.headers)

        if self.check_res(res):
            res = res.json()
            d = res["data"]
            data = {
                "live_id": d.get("id"),
                "uid": d.get("accountId"),
                "start_time": d.get("startTime"),
                "title": d.get("title"),
                "praises": d.get("parseCount"),
                "watches": d.get("joinCount"),
                "image": d.get("coverImg") if d.get("coverImg") else "",
                "location": d.get("location") if d.get("location") else "",
                "is_end": 2 if int(d["status"]) != 0 and int(d["status"]) != 1 else d["status"],
                "extends":{
                    "tags": s_get(d,"tags")
                }
            }
        else:
            self.log.warn("tmall get live info api error: " + str(res.text))
            return self.UNKNOWN_ERROR
        return data

    def get_item_list(self, live_id, uid):
        """
        获取宝贝信息
        :param live_id: 直播 id
        :param uid: 用户id
        :return:
        """
        #time.sleep(self.sleep_time)
        data = {}
        self.set_account(self.api["live_info"],"2.0",str({"type":0,"liveId": int(live_id)}))
        url = self.api["base_url"]+self.api["item_list"]+"/1.0/"
        param = dic_merge(self.param_sign, self.param_common)
        try:
            res = requests.post(url, data=param, headers=self.headers,proxies=self.proxies,timeout=self.timeout)
        except:
            res = ""

        if not self.check_res(res):
            self.set_account(self.api["live_info"],"2.0",str({"type":0,"liveId": int(live_id)}))
            url = self.api["base_url"]+self.api["item_list"]+"/1.0/"
            param = dic_merge(self.param_sign, self.param_common)
            res = requests.post(url, data=param, headers=self.headers)

        if self.check_res(res):
            res = res.json()
            data = res["data"]
        else:
            self.log.warn("tmall get item list api error: " + str(res.text))
        return data

    def get_daren_info(self,uid):
        """
        获取达人信息
        :param uid: 用户id
        :return:
        """
        self.set_account(self.api["daren_info"],"2.0",str({"accountId": str(uid)}))
        url = self.api["base_url"]+self.api["daren_info"]+"/2.0/"
        param = dic_merge(self.param_sign, self.param_common)
        try:
            res = requests.post(url, data=param, headers=self.headers,proxies=self.proxies,timeout=self.timeout)
        except:
            res = ""
        data = {}
        if not self.check_res(res):
            self.set_account(self.api["daren_info"],"2.0",str({"accountId": str(uid)}))
            param = dic_merge(self.param_sign, self.param_common)
            res = requests.post(url, data=param, headers=self.headers)

        if self.check_res(res):
            res = res.json()
            d = dict(res["data"])
            data["signature"] = s_get(d,"accountDesc")
            data["is_daren"] = s_get(d,"isDaren")
            data["is_pfv"] = s_get(d,"isV")
            data["shop_id"] = ""
            data["shop_fans_num"] = ""
            d = s_get(d,"darenShopInfo")
            if d:
                data["shop_id"] = s_get(d,"shopId")
                data["shop_fans_num"] = s_get(d,"fansNmu")
        else:
            self.log.warn("tmall get daren info api error: " + str(res.text))
        return data

    def get_user_gift_info(self, uid):
        """
        获取用户礼物信息
        :param uid:
        :return: 原样数据
        """
        data = {}
        return data

    def get_user_feeds(self, uid):
        """
        获取用户直播列表
        :param uid:
        :return: 原样数据
        """

        data = []
        return data

    def is_user_living(self, uid):
        """
        判断是否正在直播
        :param uid:
        :return: array
        """
        pass

    def host_list_format(self,time_stamp,lives_hot):
        """
        热门榜单列表格式化，用于存es
        :param time_stamp
        :param lives_hot
        :return json
        """
        pass

if __name__ == '__main__':
    tmall = Tmall()
