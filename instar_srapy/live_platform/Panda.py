#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'
import urllib
from Util.func import *
from Platform import Platform
import requests
import time

class Panda(Platform):
    def __init__(self):
        Platform.__init__(self)
        self.platform = "panda"
    api = {
        "live_list": "http://api.m.panda.tv/ajax_live_lists",
        "live_info": "http://api.m.panda.tv/ajax_get_liveroom_baseinfo",
        "category": "http://api.m.panda.tv/index.php?method=category.list&type=game&__version=1.1.2.1351&__plat=android",
        "Allsub": "http://api.m.panda.tv/ajax_get_all_subcate?__version=1.1.2.1351&__plat=android"
    }
    def set_account():
        pass

    def get_user_info(self, uid):
        """
        获取用户信息
        :param uid: user id
        :return:
        """

        param = {
            "roomid":uid
        }
        data = []
        api_name = "get_user_info"
        error,res = s_request(self.api["live_info"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["errno"] == 0:
            d = res["data"]["info"]["hostinfo"]
            room_info = res["data"]["info"]["roominfo"]
            data = {
                "uid": int(uid),
                "avatar": d.get("avatar",""),
                "nickname": d.get("name",""),
                "weight": d.get("bamboos",0),
                "signature": room_info.get("bulletin",""),
                "roomid": int(d["rid"]),
                "followers": room_info.get("fans",0)
            }
        else:
            self.error("panda get_user_info error," + str(uid) + " ," + res["errmsg"])
        return data

    def get_hot_list(self,page_num):
        param = {
            "pageno":page_num,
            "pagenum":40,
            "status":2,
            "order":"person_num",
            "__version":"1.1.2.1351",
            "__plat":"android"
        }
        data = []
        api_name = "get_hot_list"
        error,res = s_request(self.api["live_list"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["errno"] == 0:
            data = res["data"]["items"]
        return data

    def traverse_living(self, live_type="live",limit=200):
        """
        遍历获取当前所有直播，保存到redis
        :param  $live_type string 榜单类型
        :return:
        """
        data = []
        page_num = limit / 40
        for i in range(1,page_num):
            page = self.get_hot_list(i)
            if not page:
                break
            data.extend(page)
        return data

    def get_live_info(self, live_id, uid):
        """
        获取直播信息, 同时包含直播的状态以判断直播是否结束
        :param live_id: 直播 id
        :param uid: 用户id
        :return:
        """
        param = {
            "roomid":live_id
        }
        data = []
        api_name = "get_live_info"
        error,res = s_request(self.api["live_info"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["errno"] == 0:
            d = res["data"]["info"]["roominfo"]
            video_info = res["data"]["info"]["videoinfo"]
            data = {
                "live_id": live_id,
                "uid": uid,
                "title": d.get("name",""),
                "image": d["pictures"].get("img",""),
                "is_end": 0 if video_info["status"] == "2" else 1,
                "extends":{
                    "category":d.get("classification","未设置")
                }
            }
        else:
            self.error("panda get_live_info error," + str(live_id) + " ," + res["errmsg"])
        return data

    def get_user_gift_info(self, live_id):
        """
        获取用户收礼物信息
        :param uid: 用户id
        :return:
        """
        pass
    def get_user_feeds(self, uid):
        """
        获取用户直播列表
        :param uid:
        :return: 整理后的数据
        """
        pass
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
