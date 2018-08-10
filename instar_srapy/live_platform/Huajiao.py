#!/usr/bin/env python
# coding: utf-8
__author__ = 'Danny'
from Util.func import *
import requests
import random
import json
import time
from Platform import Platform


class Huajiao(Platform):
    def __init__(self):
        Platform.__init__(self)
        self.platform = "huajiao"
        self.cache_key = cache_key()
        self.live_type = ""
        pass

    param_sign = {
        "deviceid": "1986649f8b5d324b596e304cc5f15a33",
        "netspeed": 2048,
        "network": "wifi",
        "platform": "android",
        "rand": "",
        "time": "",
        "userid": 57772075,
        "version": "4.2.2.1014"
    }

    param_common = {"channel": "guanwangbtn", "device": "prototd", "devicebrand": "htccn_chs_cmcc",
                    "devicemanufacturer": "htc",
                    "model": "HTC+T329t", "androidversion": "4.2.2", "androidversioncode": 17,
                    "lng": 126.49474219682923, "lat": 49.21179870896539, "province": "北京市", "city": "北京市",
                    "town": "东城区",
                    "district": "东城区"}

    api = {
        "live_list": "http://webh.huajiao.com/live/listcategory",
        "live_info": "http://live.huajiao.com/feed/getFeedInfo",
        "user_info": "http://passport.huajiao.com/user/getUserInfo",
        "user_gift_info": "http://message.huajiao.com/user/getInfo",
        "user_feeds": "http://webh.huajiao.com/User/getUserFeeds",
        "get_follow_list":"http://webh.huajiao.com/User/getUserNews",
        "add_follow":"http://passport.huajiao.com/follow/add"
    }

    accounts = [
        {
            "userid": 79405590,
            "deviceid": "1d394869ab62785b74075706d416f33f",
            "token": "0204bba21658b6b8bdb15f58DomKhjlNta1ab8d9"
        }
    ]

    def set_account(self,s_account={}):
        """
        设置账号
        :return:
        """
        if not s_account:
            # total_count = len(self.accounts) - 1
            # account = self.accounts[random.randint(0, total_count)]
            account = self.accounts[0]
            self.headers["Cookie"] = "token=" + account["token"]
            self.param_sign["userid"] = account["userid"]
            self.param_sign["deviceid"] = account["deviceid"]
        else:
            self.headers["Cookie"] = "token=" + s_account["token"]
            self.param_sign["userid"] = s_account["uid"]
            self.param_sign["deviceid"] = md5(str(time.time()))

    def gene_sign(self,s_account={}):
        """
        生成签名参数
        :return:
        """
        self.set_account(s_account)
        self.param_sign["rand"] = random.uniform(0, 1)
        self.param_sign["time"] = time.time()
        sign_str = ""
        # 根据key排序，拼接字符串
        for key in sorted(self.param_sign.keys()):
            sign_str += key + "=" + str(self.param_sign[key])
        # 加上固定字符串
        sign_str += "eac63e66d8c4a6f0303f00bc76d0217c"
        return dic_merge(self.param_sign, {"guid": md5(sign_str)})

    def get_live(self, offset=0):
        """
        获取热门及最新榜单直播列表
        :param offset:
        :return:
        """
        param_sign = self.gene_sign()
        param_sign = dic_merge(param_sign, self.param_common)
        param_api = {"nums": 20, "cateid": 1000}
        if offset > 0:
            param_api["offset"] = offset
        param = dic_merge(param_sign, param_api)
        try:
            res = requests.get(self.api["live_list"], params=param, headers=self.headers)
            res = res.json()
        except Exception,e:
            self.log.error("huajiao get_live error: " + str(res.text))
            return 0, []
        if res["errno"] == 0 and res.get("data"):
            data = res["data"]
            return data["total"], data["feeds"]
        else:
            self.log.warn("huajiao api error: " + str(res))
            return 0, []

    def save_rank_feeds(self, feeds, index):
        """
        保存直播榜单到redis
        :param feeds:
        :param index:
        :return:
        """
        _cache_key = "live_" + self.live_type + "_" + self.cache_key
        for feed in feeds:
            self.redis_ins.zadd(_cache_key, json.dumps(feed), index)
            index -= 1
        # 设置过期时间
        self.redis_ins.expire(_cache_key, 60 * 60)
        return index

    def traverse_living(self, live_type="live"):
        """
        遍历获取当前所有直播，保存到redis
        :param  $live_type string 榜单类型
        :return:
        """
        self.live_type = live_type
        total, feeds = self.get_live()
        all_feeds = feeds
        page = total / 20
        if total % 20 != 0:
            page += 1
        self.log.info("huajiao start get hot live data")
        self.log.info("huajiao rank " + self.live_type + " total: " + str(total))
        for i in range(1, page):
            time.sleep(self.sleep_time)
            self.log.info("huajiao start get live data " + str(i + 1) + "/" + str(page))
            total, feeds = self.get_live(20 * i)
            all_feeds += feeds
        return all_feeds

    def get_user_info(self, uid):
        """
        获取花椒用户信息
        :param uid: user id
        :return:
        """
        # time.sleep(self.sleep_time)
        # param_sign = self.gene_sign()
        # param = dic_merge(param_sign, self.param_common)
        #
        # data = {}
        # api_name = "get_user_info"
        # error,res = s_request(self.api["user_info"],'POST',params=param, data={"uid": uid}, headers=self.headers)
        # res = s_check(error,res,self.platform,api_name,self.log)
        #
        # if not res:
        #     return data
        param_sign = self.gene_sign()
        param = dic_merge(param_sign, self.param_common)
        res_from = "proxy"
        #huajiao恶心策略，重试必须重新生成签名，否则报重复请求错误
        try:
            res = requests.post(self.api["user_info"], params=param, data={"uid": uid}, headers=self.headers,proxies=self.proxies,timeout=2)
        except:
            res = ""
        try:
            res_json = res.json()
            error = res_json["errno"]
        except:
            error = 1

        if not res or error !=0:
            res_from = "local"
            param_sign = self.gene_sign()
            param = dic_merge(param_sign, self.param_common)
            try:
                res = requests.post(self.api["user_info"], params=param, data={"uid": uid}, headers=self.headers,timeout=2)
            except:
                res = ""

        if not res:
            self.log.warn("huajiao get user_info api error: timeout from "+res_from)
            return self.UNKNOWN_ERROR

        data = {}
        try:
            res = res.json()
        except:
            self.log.warn("huajiao get user_info api error: result is not json ")
            return self.UNKNOWN_ERROR

        if res["errno"] == 0:
            d = res["data"]
            # 为防止花椒接口增加字段，所以只拿出需要的字段
            data = {
                "uid": uid,
                "praises": d["praises"],
                "source": d["source"],
                "followers": d["followers"],
                "astro": d["astro"],
                "verified": d["verified"],
                "nickname": d["verifiedinfo"].get("realname",d["nickname"]),
                "level": d["level"],
                "gender": d["gender"],
                "followings": d["followings"],
                "avatar": d["avatar_l"],
                "signature": d["signature"],
                "feeds": d["feeds"],
                "vs_status":d.get("vs_status") if d.get("vs_status") else "",
                "vs_realname":d.get("vs_realname") if d.get("vs_realname") else "",
                "vs_school":d.get("vs_school") if d.get("vs_school") else "",
                "tags": json.dumps(d.get("tags","")) if d.get("tags","") else "",
            }

            location = d["location"].split(" ")
            data["province"] = location[0]
            if len(location) > 1:
                data["city"] = location[1]
        else:
            self.log.warn("huajiao get user info api error: " + res["errmsg"])
        return data

    def get_live_info(self, live_id, uid):
        """
        获取直播信息
        :param live_id: 直播 id
        :param uid: 用户id
        :return:
        """
        time.sleep(self.sleep_time)
        param_sign = self.gene_sign()
        param = dic_merge(param_sign, self.param_common)
        res_from = "proxy"
        #huajiao恶心策略，重试必须重新生成签名，否则报重复请求错误
        try:
            res = requests.post(self.api["live_info"], params=param, data={"relateid": live_id}, headers=self.headers,proxies=self.proxies,timeout=2)
        except:
            res = ""
        try:
            res_json = res.json()
            error = res_json["errno"]
        except:
            error = 1

        if not res or error !=0:
            res_from = "local"
            param_sign = self.gene_sign()
            param = dic_merge(param_sign, self.param_common)
            try:
                res = requests.post(self.api["live_info"], params=param, data={"relateid": live_id}, headers=self.headers,timeout=2)
            except:
                res = ""

        if not res:
            self.log.warn("huajiao get live info api error: timeout from "+res_from)
            return self.UNKNOWN_ERROR

        data = {}
        # api_name = "get_live_info"
        # error,res = s_request(self.api["live_info"],'POST',params=param, data={"relateid": live_id}, headers=self.headers)
        # res = s_check(error,res,self.platform,api_name,self.log)
        #
        # if not res:
        #     return self.UNKNOWN_ERROR
        try:
            res = res.json()
        except:
            self.log.warn("huajiao get live info api error: result is not json ")
            return self.UNKNOWN_ERROR

        if res["errno"] == 1506:
                data = {"is_end":1}
                return data

        if res["errno"] != 0:
            self.log.warn("huajiao live_info api error: " + res["errmsg"] + ", live_id " + str(live_id)+",from "+res_from)
            return self.UNKNOWN_ERROR
        else:
            d = res["data"]["feed"]
            data = {
                "live_id": d["relateid"],
                "uid": res["data"]["author"]["uid"],
                "start_time": d["publishtime"],
                "title": d["title"],
                "praises": d["praises"],
                "watches": d["watches"],
                "image": d["image"],
                "duration": d["duration"],
                "location": d["location"],
                "is_end": 1 if d["duration"] else 0,
                "extends":{
                    "tags": d.get("labels","")
                }
            }
        return data

    def get_user_gift_info(self, uid):
        """
        获取用户收礼物信息
        :param uid: 用户id
        :return:
        """

        param_sign = self.gene_sign()
        param = dic_merge(param_sign, self.param_common)
        res_from = "proxy"
        #huajiao恶心策略，重试必须重新生成签名，否则报重复请求错误
        try:
            res = requests.post(self.api["user_gift_info"], params=param, data={"uid": uid}, headers=self.headers,proxies=self.proxies,timeout=2)
        except:
            res = ""
        try:
            res_json = res.json()
            error = res_json["errno"]
        except:
            error = 1

        if not res or error !=0:
            res_from = "local"
            param_sign = self.gene_sign()
            param = dic_merge(param_sign, self.param_common)
            try:
                res = requests.post(self.api["user_gift_info"], params=param, data={"uid": uid}, headers=self.headers,timeout=2)
            except:
                res = ""

        if not res:
            self.log.warn("huajiao get gift info api error: timeout from "+res_from)
            return self.UNKNOWN_ERROR

        data = {}
        try:
            res = res.json()
        except:
            self.log.warn("huajiao get gift info api error: result is not json ")
            return self.UNKNOWN_ERROR

        # time.sleep(self.sleep_time)
        # param_sign = self.gene_sign()
        # param = dic_merge(param_sign, self.param_common)
        #
        # data = {}
        # api_name = "get_user_gift_info"
        # error,res = s_request(self.api["user_gift_info"],'POST',params=param, data={"uid": uid}, headers=self.headers)
        # res = s_check(error,res,self.platform,api_name,self.log)
        #
        # if not res:
        #     return self.UNKNOWN_ERROR

        if res["errno"]  == 0:
            data = {
                "send": res["data"]["disRewardTotal"]["totalsend"],
                "get": res["data"]["disRewardTotal"]["totalreceive"]
            }
        elif res["errno"] == 1104:
            self.alarm("huajiao get_user_gift_info",res["errmsg"])
        else:
            self.error("huajiao get_user_gift_info, " + str(uid)+" ,error "+res["errmsg"])

        return data

    def get_user_feeds(self, uid):
        """
        获取用户直播列表
        :param uid:
        :return: 原样数据
        """
        #time.sleep(self.sleep_time)
        param = {
            "fmt": "json",
            "uid": uid,
            "_": time.time()
        }

        data = []
        api_name = "get_user_feeds"
        error,res = s_request(self.api["user_feeds"],params=param)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return data

        if res["errno"] == 0 and len(res["data"]) > 0:
            records = res["data"]["feeds"]
            for d in records:
                data.append({
                    "uid": uid,
                    "live_id": int(d["feed"]["relateid"]),
                    "start_time": d["creatime"],
                    "title": d["feed"]["title"],
                    "status": d["type"]
                })

        return data

    def is_user_living(self, uid):
        """
        判断是否正在直播
        :param uid:
        :return: live_id
        """
        live_id = ""
        feeds = self.get_user_feeds(uid)
        if len(feeds) > 0 and feeds[0]["status"] == 1:
                live_id = feeds[0]["live_id"]
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
            uid = int(item["author"]["uid"])
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
            "fmt": "json",
            "uid": uid,
        }
        data = []
        api_name = "get_follow_list"
        error,res = s_request(self.api["get_follow_list"],params=param)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return data

        if res["errno"] == 0 and len(res["data"]) > 0:
            feeds = res["data"]["feeds"]
            for feed in feeds:
                data.append({
                    "uid": feed["author"]["uid"],
                    "live_id": feed["feed"]["relateid"],
                    "status": feed["type"]
                })

        return data

    def add_follow(self,suid,duid):
        """
        添加关注
        :param suid
        :param duid
        :return json
        """
        body = {
            "uid":duid
        }
        result = ""

        s_account = self.instar.get_account(self.platform,suid)
        if not s_account:
            return result
            self.log.error("huajiao add_follow error:no user in db,suid="+str(suid))

        param_sign = self.gene_sign(s_account)
        param = dic_merge(param_sign, self.param_common)


        api_name = "add_follow"
        error,res = s_request(self.api["add_follow"],'POST',params=param,headers=self.headers,data=body)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return result

        if res["errno"] == 0:
            result = {
                "consume":res["consume"],
                "time":res["time"]
            }
        elif res["errno"] == 1103:
            result = {
                "consume":"repeat",
                "time":res["time"]
            }
        elif res["errno"] == 1104:
            self.log.error("huajiao add_follow error,account is disabled suid:"+str(suid))
            self.instar.update_status("huajiao",suid,-1)
        elif res["errno"] == 1105:
            self.log.error("huajiao add_follow error,account is disabled suid:"+str(suid))
            self.instar.update_status("huajiao",suid,1)
        else:
            self.log.error("huajiao add_follow error:"+str(res["errmsg"])+" code:"+str(res["errno"])+" suid:"+str(suid)+" duid:"+str(duid))
        return result

if __name__ == '__main__':
    huajiao = Huajiao()
