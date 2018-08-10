#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'
import urllib
from Util.func import *
from Platform import Platform
import requests
import time

class Zhanqi(Platform):
    def __init__(self):
        Platform.__init__(self)
        self.platform = "zhanqi"
    api = {
        "live_list": "https://www.zhanqi.tv/api/static/live.hots/",
        "live_info": "https://www.zhanqi.tv/api/static/v2.1/room/domain/"
    }
    def set_account():
        pass

    def get_user_info(self, uid):
        """
        获取用户信息
        :param uid: user id
        :return:
        """
        data = []
        api_name = "get_user_info"
        url = "{}{}.json".format(self.api["live_info"],uid)
        error,res = s_request(url)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["code"] == 0:
            d = res["data"]
            data = {
                "uid": int(d["code"]),
                "avatar": d.get("avatar",""),
                "nickname": d.get("nickname",""),
                "weight": 0,
                "signature": d.get("starDesc",""),
                "roomid": int(d["uid"]),
                "followers": d.get("follows",0)
            }
        else:
            self.error("zhanqi get_user_info error," + str(uid) + " ," + res["message"])
        return data

    def get_hot_list(self,page_num):
        data = []
        api_name = "get_hot_list"
        url = "{}100-{}.json".format(self.api["live_list"],page_num)
        error,res = s_request(url)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["code"] == 0:
            data = res["data"]["rooms"]
        return data

    def traverse_living(self, live_type="live",limit=200):
        """
        遍历获取当前所有直播，保存到redis
        :param  $live_type string 榜单类型
        :return:
        """
        data = []
        page_num = limit / 100
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
        data = []
        api_name = "get_user_info"
        url = "{}{}.json".format(self.api["live_info"],live_id)
        error,res = s_request(url)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["code"] == 0:
            d = res["data"]
            data = {
                "live_id": live_id,
                "uid": d["uid"],
                "title": d.get("title",""),
                "image": d.get("spic",""),
                "is_end": 0 if d["status"] == "4" else 1,
                "extends":{
                    "category":d.get("gameName","未设置")
                }
            }
        else:
            self.error("zhanqi get_live_info error," + str(live_id) + " ," + res["message"])
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
