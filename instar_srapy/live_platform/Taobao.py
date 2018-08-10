#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'



from Util.func import *
import requests
import random
import json
import time
from Platform import Platform
from urllib import unquote
from base64 import decodestring
import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class Taobao(Platform):
    def __init__(self):
        Platform.__init__(self)
        self.platform = "taobao"
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
        "item_list_pc": "https://taobaolive.taobao.com/api/item_list/1.0", #?type=0&creatorId=1724005492&liveId=200231611885
        "live_info_pc": "https://taobaolive.taobao.com/api/live_detail/1.0", #?creatorId=&liveId=e334fa03-045d-4a62-b4f0-6e737e9861e5
        "live_info": "mtop.guide.video.liveDetail",
        "video_list": "mtop.mediaplatform.live.videolist",
        "base_url": "http://api.m.taobao.com/h5/",
        "hot_list": "https://taobaolive.taobao.com/api/more_videos/1.0?page=200",
        "get_token": "http://api.m.taobao.com/h5/mtop.mediaplatform.live.videolist/1.0/",
        "live_detail": "https://taobaolive.taobao.com/room/index.htm",
        "anchor_info": "mtop.mediaplatform.anchor.info"
        #"get_token":"https://acs.m.taobao.com/h5/mtop.mediaplatform.live.encryption/1.0/"
    }


    def get_token(self):
        token_list = self.redis_ins.get("taobao_token")
        token_list = eval(token_list)
        token_item = token_list[random.randint(0,4)]
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
        self.set_account(self.api["live_info"],"3.0",str({"creatorId": int(uid)}))
        url = self.api["base_url"]+self.api["live_info"]+"/3.0/"
        param = dic_merge(self.param_sign, self.param_common)

        data = {}

        try:
            res = requests.post(url, data=param, headers=self.headers,proxies=self.proxies,timeout=2)
        except:
            res = ""
        if not self.check_res(res):
            self.set_account(self.api["live_info"],"3.0",str({"creatorId": int(uid)}))
            param = dic_merge(self.param_sign, self.param_common)
            try:
                res = requests.post(url, data=param, headers=self.headers,proxies=self.proxies,timeout=2)
            except:
                res = ""

        if not self.check_res(res):
            self.set_account(self.api["live_info"],"3.0",str({"creatorId": int(uid)}))
            param = dic_merge(self.param_sign, self.param_common)
            try:
                res = requests.post(url, data=param, headers=self.headers,timeout=2)
            except:
                res = ""
        try:
            res = res.json()
        except:
            self.log.error("taobao get user info api error: timeout")
            return self.UNKNOWN_ERROR
        try:
            d = res["data"]
            broadcaster =  d.get("broadCaster","")
            data["uid"] = uid
            if  broadcaster:
                data["followers"]= d["broadCaster"].get("fansNum",0)
                data["city"] = d.get("location") if d.get("location") else ""
                data["avatar"] = d["broadCaster"].get("headImg","")
                data["verified"] = d["broadCaster"].get("v")
                data["nickname"] = d["broadCaster"].get("accountName","")
                data["accountdes"] = d["broadCaster"].get("accountDes","")
                data["hotsnum"] = d["broadCaster"].get("hotsNum")
        except Exception,e:
            self.log.error(str(e))
            self.log.error("taobao get user info api error: ")

        daren = self.get_daren_info(uid)
        data = dic_merge(data,daren)
        if "*" in data["nickname"]:
            anchor = self.get_anchor_info(uid)
            data = dic_merge(data, anchor)
        return data

    def get_live_info(self, live_id, uid):
        data = {}
        data = self.query_live_info("liveId",live_id)
        if 'SPIDER-INTERNALERROR' in data:
            data = self.query_live_info("creatorId",uid)
        return data

    def query_live_info(self, key, id):
        """
        获取直播信息
        :param live_id: 直播 id
        :param uid: 用户id
        :return:
        """
        query = {key:int(id)}
        self.set_account(self.api["live_info"],"3.0",str(query))
        url = self.api["base_url"]+self.api["live_info"]+"/3.0/"
        param = dic_merge(self.param_sign, self.param_common)
        data = {}
        #淘宝恶心策略，重试必须重新生成签名，不能走通用方法s_request
        try:
            res = requests.post(url, data=param, headers=self.headers,proxies=self.proxies,timeout=2)
        except:
            res = ""
        if not self.check_res(res):
            self.set_account(self.api["live_info"],"3.0",str(query))
            param = dic_merge(self.param_sign, self.param_common)
            try:
                res = requests.post(url, data=param, headers=self.headers,proxies=self.proxies,timeout=2)
            except:
                res = ""

        if not self.check_res(res):
            self.set_account(self.api["live_info"],"3.0",str(query))
            param = dic_merge(self.param_sign, self.param_common)
            try:
                res = requests.post(url, data=param, headers=self.headers,timeout=2)
            except:
                res = ""

        try:
            res = res.json()
        except:
            self.log.error("taobao get live info api error: timeout")
            return self.UNKNOWN_ERROR
        print(res["data"])
        return
        try:
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
        except:
            self.log.error("taobao get live info api error,{}-{},: {}".format(key, id, json.dumps(res)))
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
            self.log.error("taobao get item list api error: " + str(res.text))
        return data

    def get_item_list_pc(self, live_id, uid):
        """
        获取宝贝信息
        :param live_id: 直播 id
        :param uid: 用户id
        :return:
        """
        data = {}
        url = self.api["item_list_pc"]
        param = {
            "type": 0,
            "creatorId": "0",
            "liveId": live_id
        }
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
            "Referer": "https://taobaolive.taobao.com/api/item_list/1.0?type=0"
        }
        try:
            res = requests.get(url, params=param, headers=header, proxies=self.proxies, timeout=self.timeout)
        except:
            res = ""

        if not res:
            res = requests.get(url, params=param, headers=header)

        try:
            res = res.text
        except:
            res = ""

        if '"success":true' in res:
            res = eval(res.replace("true","True").replace("null","None").replace("false","False"))
            data = res["result"]["data"]
        else:
            self.log.error("taobao get item list api error: " + str(res.text))
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
            d = res["data"]
            data["nickname"] = d.get("darenName",None)
            data["signature"] = s_get(d,"accountDesc")
            data["is_daren"] = s_get(d,"isDaren")
            data["is_pfv"] = s_get(d,"isV")
            data["followers"] = int(d.get("fansNum",0))
            data["avatar"] = d.get("darenLogo","")
            data["verified"] = d.get("isV")
            data["shop_id"] = ""
            data["shop_fans_num"] = ""
            d = s_get(d,"darenShopInfo")
            if d:
                data["shop_id"] = s_get(d,"shopId")
                data["shop_fans_num"] = s_get(d,"fansNmu")
        else:
            self.log.error("taobao get daren info api error: " + str(res.text))
        return data


    def get_anchor_info(self, uid):
        """
        获取主播信息
        :param uid: 用户id
        :return:
        """
        self.set_account(self.api["anchor_info"],"1.0",str({"broadcasterId": str(uid)}))
        url = self.api["base_url"]+self.api["anchor_info"]+"/1.0/"
        param = dic_merge(self.param_sign, self.param_common)
        try:
            res = requests.post(url, data=param, headers=self.headers,proxies=self.proxies,timeout=self.timeout)
        except:
            res = ""
        data = {}
        if not self.check_res(res):
            self.set_account(self.api["anchor_info"],"1.0",str({"broadcasterId": str(uid)}))
            param = dic_merge(self.param_sign, self.param_common)
            res = requests.post(url, data=param, headers=self.headers)
        if self.check_res(res):
            res = res.json()
            d = res["data"]
            data["nickname"] = d["nick"]
            data["avatar"] = d["headImage"]
        else:
            self.log.error("taobao get anchor info api error: " + str(res.text))
        return data



    def get_live_detail(self,uid):
        """
        获取达人信息
        :param uid: 用户id
        :return:
        """
        param = {
            "userId": uid
        }

        data = {}
        api_name = "get_hot_list"
        error,res = s_request(self.api["live_detail"], params=param)

        if not res:
            self.log.error("taobao get live_detail info api error: " + str(error))
            return data

        try:
            live_detail = re.findall(r"liveDetail.=.(.+).\|\|",res.content)[0]
            res = json.loads(live_detail)
            d = res["broadCaster"]
        except Exception, e:
            self.log.error("taobao get live_detail info re match failed!-{}".format(e))
            return data
        else:
            link = d.get("wangwangLink","")
            try:
                wangwang = decodestring(unquote(link.split("to_user=")[1])).decode('gbk')
            except:
                wangwang = link
            else:
                wangwang = "https://www.taobao.com/go/market/webww/?ver=1&&touid=cntaobao{}&siteid=cntaobao&status=2&portalId=&gid=&itemsId=" \
                        .format(wangwang)
            temp = {}
            temp["signature"] = d.get("accountDes")
            temp["is_pfv"] = d.get("isV")
            temp["wangwanglink"] = wangwang
            temp["followers"] = d.get("fansNum")
            temp["avatar"] = d.get("headImg")
            temp["verified"] = d.get("isV")
            for k, v in temp.items():
                if v:
                    data[k] = v

        return data

    def get_live_detail_live_info(self, uid, liveid):

        param = {
            "feedId": liveid
        }

        data = {}
        api_name = "get_hot_list"
        error,res = s_request(self.api["live_detail"], params=param)

        if not res:
            self.log.error("taobao get live_detail info api error: " + str(error))
            return data

        try:
            live_detail = re.findall(r"liveDetail.=.(.+).\|\|",res.content)[0]
            d = json.loads(live_detail)
        except Exception, e:
            self.log.error("taobao get live_detail info re match failed!-{}".format(e))
            return data
        else:
            data = {
                "live_id": liveid,
                "uid": uid,
                "start_time": d.get("startTime"),
                "title": d.get("title"),
                "praises": d.get("parseCount"),
                "watches": d.get("joinCount"),
                "image": d.get("coverImg",""),
                "location": d.get("location",""),
                "is_end": 2 if int(d["status"]) != 0 and int(d["status"]) != 1 else d["status"],
                "extends":{
                    "tags": s_get(d,"tags")
                }
            }

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
    taobao = Taobao()
