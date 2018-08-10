#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'
import urllib
from Util.func import *
from Platform import Platform
import requests
import time
import json

class Bilibili(Platform):
    def __init__(self):
        Platform.__init__(self)
        self.platform = "bilibili"
    api = {
        "live_list": "http://live.bilibili.com/area/liveList",#area=all&order=online&page=2
        #"dance_list": "http://live.bilibili.com/area/liveList?area=sing-dance&order=online&page=2"
        #"mobile_game": "http://live.bilibili.com/area/home?area=mobile-game&order=online&cover=1"
        "live_info": "http://live.bilibili.com/live/getInfo",#get roomid=2383761
        "user_info": "http://space.bilibili.com/ajax/member/GetInfo",#post form mid,_ time_stamp
        "category": "http://live-api.bilibili.com/index/dynamic?callback=jsonpCallback",
        "is_live":"http://live.bilibili.com/bili/getRoomInfo/"
    }
    def set_account():
        pass

    def get_user_info(self, uid):
        """
        获取用户信息
        :param uid: user id
        :return:
        """
        form = {
            "mid":uid,
            "_":int(time.time())
        }
        header={'Referer':'http://space.bilibili.com/'}
        data = []
        api_name = "get_user_info"
        error,res = s_request(self.api["user_info"],'POST',1,data=form,headers=header)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["status"]:
            d = res["data"]
            data = {
                "uid":uid,
                "avatar": d.get("face",""),
                "nickname": d.get("name",""),
                "gender": "M" if d.get("sex") == "女" else "F",
                "followers": int(d.get("fans",0)),
                "followings": int(d.get("friend",0)),
                "signature": d.get("sign",""),
                "level": d["level_info"]["current_level"]
            }
        else:
            self.error("bilibili get_uid_info error," + str(uid) + " ," + str(res))
            return self.UNKNOWN_ERROR
        return data

    def get_hot_list(self,page_num):
        param = {
            "area":"all",
            "order":"online",
            "page":page_num
        }
        data = []
        api_name = "get_hot_list"
        error,res = s_request(self.api["live_list"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["code"] == 0:
            data = res["data"]
        return data

    def traverse_living(self, live_type="live",limit=200):
        """
        遍历获取当前所有直播，保存到redis
        :param  $live_type string 榜单类型
        :return:
        """
        data = []
        page_num = limit / 30
        for i in range(0,page_num):
            page = self.get_hot_list(i+1)
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
        area = {-1:"未填写",1:"单机联机",2:"御宅文化",3:"网络游戏",4:"电子竞技",6:"生活娱乐",7:"放映厅",9:"绘画专区",10:"唱见舞见",11:"手机直播",12:"手游直播"}
        param = {
            "roomid":live_id
        }
        data = []
        api_name = "get_live_info"
        error,res = s_request(self.api["live_info"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["code"] == 0:
            d = res["data"]
            data = {
                "live_id": live_id,
                "uid": uid,
                "title": d.get("ROOMTITLE",""),
                "image": d.get("COVER",""),
                "is_end": 0 if d["LIVE_STATUS"] == "LIVE" else 1,
                "extends":{
                    "category":area.get(d["AREAID"],d["AREAID"]),
                    "followers": d.get("FANS_COUNT",0)
                }
            }
        else:
            self.error("bilibili get_live_info error," + str(live_id) + " ," + res["msg"])
            return self.UNKNOWN_ERROR
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
        live_id = ""
        api_name = "is_user_living"
        error,res = s_request(self.api["is_live"] + str(uid))
        if not res:
            return live_id

        try:
            res = json.loads(res.text[1:-2])
        except:
            self.error("bilibili is_user_living error,no json,"+str(res.text))
            return live_id

        if res["code"] != 0:
            self.error("bilibili is_user_living error,"+res["msg"])
            return live_id

        res = res["data"]
        live_id = res["url"].split('/')[3] if res["liveStatus"] == 1 else ""

        return live_id

    def host_list_format(self,time_stamp,lives_hot):
        """
        热门榜单列表格式化，用于存es
        :param time_stamp
        :param lives_hot
        :return json
        """
        pass
