#!/usr/bin/env python
# coding: utf-8
__author__ = 'Danny'
import urllib
from Util.func import *
from Platform import Platform
import requests
import time
import sys
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding("utf-8")

class Yizhibo(Platform):
    def __init__(self):
        Platform.__init__(self)
        self.platform = "yizhibo"
        pass
    param_common = {"lc": "3000000000006495", "cv": "IK2.9.60_Android", "cc": "TG36415", "ua": "htcHTCT329t", "uid": "53438311", "sid": "211aHEWUIJe6E95Cq4KI6Ji2NBwc2i0c4aGko2Rgi2HjIxkv7V1aG",
                    "devi": "55895025256510", "imsi": "370270000000000", "imei": "867895025256510", "icc": "89514103211118510721", "conn": "WIFI", "vv": "1.0.3-2016060211417.android",
                    "aid": "66ff6d923d499104", "osversion": "android_17", "proto": "4", "smid": "DuzvvftLIdB0GRrFsBY2OaaaazGxLfnLE2vPS0mxzSoKNWbzoRIvS531y6avt3bHAiRP7gGHedExL96Q616rsqkr"}
    api = {
        "live_list": "http://www.yizhibo.com/www/web/get_hot_list",
        "live_info": "http://www.yizhibo.com/live/h5api/get_basic_live_info",
        "user_info": "http://www.yizhibo.com/member/h5api/get_member_info_for_live",
        "user_feeds":"http://www.yizhibo.com/live/h5api/get_live_member_content_list",
        "get_follow_list":"http://yizhibo.com/www/web/get_follow_member_lives",
        "add_follow":"http://www.yizhibo.com/member/h5api/follow_friends",
        "view_num":"http://yizhibo.com/member/personel/user_videos"
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
            "memberid": uid
        }
        param = dic_merge(self.param_common, param)

        data = []
        api_name = "get_user_info"
        error,res = s_request(self.api["user_info"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["result"] == 1:
            d = res["data"]
            data = {
                "uid": uid,
                "followers": s_int(s_get(d,"fanstotal")),
                "verified": s_get(d,"ytypevt"),
                "nickname": d["nickname"],
                "level": d["level"],
                "gender": "F" if d["sex"] == 2 else "M",
                "followings":s_int(s_get(d,"focustotal")),
                "avatar": s_get(d,"avatar"),
                "signature": s_get(d,"desc")
            }
        else:
            self.error("yizhibo get_user_info, " + str(uid) + "," + res["msg"])
        return data

    def get_hot_list(self,start,cookie):
        param = {
            "start":start,
            "limit":50
        }
        data = []
        api_name = "get_hot_list"
        error,res = s_request(self.api["live_list"], params=param,cookies=cookie)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["result"] == 1:
            data = res["data"]["list"]
        return data

    def traverse_living(self, live_type="live",limit=200):
        """
        遍历获取当前所有直播，保存到redis
        :param  $live_type string 榜单类型
        :return:
        """
        data = []
        page_num = limit / 50
        url = 'http://www.yizhibo.com/www/web/get_hot_list?start=0&limit=1'
        cookie = dict(requests.get(url).cookies)
        for i in range(0,page_num):
            page = self.get_hot_list(i * 50,cookie)
            data.extend(page)
            time.sleep(0.5)
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
            "scid": live_id
        }

        data = []
        api_name = "get_live_info"
        error,res = s_request(self.api["live_info"],'GET',2,params=param)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return self.UNKNOWN_ERROR

        if res["result"] == 1:
            d = res["data"]
            data = {
                "live_id": live_id,
                "uid": uid,
                "title": s_get(d,"live_title"),
                "praises": 0,
                "watches": s_get(d,"online"),
                "image": d["covers"],
                "duration": 0,
                "location": "",
                "goldcoin":d.get("goldcoin",0),
                "is_end": 0 if int(d["status"]) == 10 else 1
            }
        else:
            self.error("yizhibo get_live_info error," + str(live_id) + " ," + res["msg"])
            return self.UNKNOWN_ERROR
        return data

    def get_view_num(self,live_id,uid):
        """
        获取直播观看人数
        :param live_id: 直播 id
        :return:
        """
        time.sleep(self.sleep_time)
        param = {
            "memberid": uid
        }
        data = {
            "live_id": live_id,
            "view_num": 0
            }
        api_name = "get_view_num"
        error,s_res = s_request(self.api["view_num"],'GET',2,params=param)
        if not s_res:
            self.error("yizhibo get_view_num error," + str(live_id) + ",error:" + str(error))
            return self.UNKNOWN_ERROR

        html = s_res.text
        if "nodata" in html:
            return data
        bsObj = BeautifulSoup(html,'html.parser')
        feed_list = bsObj.find(attrs={'class':'index_all_list'})
        if not feed_list:
            self.error("yizhibo get_view_num error," + str(live_id) + ",html parse error:no class index_all_list")
            return self.UNKNOWN_ERROR
        view_num = [num.text for num in feed_list.findAll(attrs={'class':'index_num'})]
        scid_num = [scid.text for scid in feed_list.findAll(attrs={'class':'scid'})]
        if live_id not in scid_num:
            return data
        live_id = str(live_id)
        data["view_num"] = s_int(view_num[scid_num.index(live_id)].replace("\xe4\xba\xba",""))
        return data


    def get_user_gift_info(self, uid):
        """
        获取用户收礼物信息
        :param uid: 用户id
        :return:
        """
        time.sleep(self.sleep_time)
        param = {
            "memberid": uid
        }
        param = dic_merge(self.param_common, param)

        data = []
        api_name = "get_user_gift_info"
        error,res = s_request(self.api["user_info"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return data

        if res["result"] == 1:
            d = res["data"]
            data = {
                "send":s_int(s_get(d,"sent_goldcoin")),
                "get":s_int(s_get(d,"receive_goldcoin"))
            }
        else:
            self.error("yizhibo get_gift_info, " + str(uid) + "," + res["msg"])
        return data

    def get_user_feeds(self, uid):
        """
        获取用户直播列表
        :param uid:
        :return: 整理后的数据
        """
        time.sleep(self.sleep_time)
        param = {
            "memberid": uid
        }
        data = []
        api_name = "get_user_feeds"
        error,res = s_request(self.api["user_feeds"],headers=self.headers, params=param)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return data

        if res["result"] == 1:
            d = res["data"]
            data = s_get(d,"list")

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
        status = feeds[0]["status"]
        live_id = feeds[0]["scid"] if int(status) == 10 else ""

        if live_id:
            live_id = repr(live_id.encode('utf8'))

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
            uid = int(item["memberid"])
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
        result = ""

        s_account = self.instar.get_account(self.platform,uid)
        if not s_account:
            return result

        cookie = {
            "yxa_uid":uid,
            "XIAOKASID":s_account["token"]
        }

        data = []
        api_name = "get_follow_list"
        error,res = s_request(self.api["get_follow_list"],cookies=cookie)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return data

        if res["result"] == 1:
            if len(res["data"]["list"]) < 1:
                return data
            feeds = res["data"]["list"]
            for feed in feeds:
                live_id = feed["scid"]
                data.append({
                    "uid": feed["memberid"],
                    "live_id": repr(live_id.encode('utf8')),
                    "status": 1 if int(feed["status"]) == 10 else 0
                })
        else:
            self.log.error("yizhibo get_follow_list error:"+str(res["msg"])+" code:"+str(res["result"])+" uid:"+str(uid))
            self.instar.update_status("yizhibo",uid,-1)
        return data

    def add_follow(self,suid,duid):
        """
        添加关注
        :param suid
        :param duid
        :return json
        """
        param = {
            "p_from": ""
        }

        body = {
            "friendid": duid
        }

        result = ""

        s_account = self.instar.get_account(self.platform,suid)
        if not s_account:
            return result
            self.log.error("yizhibo add_follow error:no user in db,suid="+str(suid))

        self.headers["Cookie"] = "XIAOKASID=" + s_account["token"]+";yxauid=" + str(suid)
        self.headers["Referer"] = "http://www.yizhibo.com/l/UxUb5rp0xp_Mp4yQ.html?p_from=pHome.HotAnchorTop"
        api_name = "add_follow"
        error,res = s_request(self.api["add_follow"],'POST',params=param,data=body,headers=self.headers)
        res = s_check(error,res,self.platform,api_name,self.log)

        if not res:
            return result

        if res["result"] == 1:
            result = {
                "msg":res["msg"],
                "time": int(time.time())
            }
        elif res["result"] == 600:
            self.log.error("yizhibo add_follow error:"+str(res["msg"])+" code:"+str(res["result"])+" suid:"+str(suid))
            self.instar.update_status("yizhibo",suid,-1)
        else:
            self.log.error("yizhibo add_follow error:"+str(res["msg"])+" code:"+str(res["result"])+" suid:"+str(suid))

        return result



if __name__ == '__main__':
    inke = Yizhibo()
    print inke.get_live_info("btWLFfbTbUJL9kdW", 3)
