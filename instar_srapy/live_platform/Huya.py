#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'
import urllib
from Util.func import *
from Platform import Platform
from bs4 import BeautifulSoup
import requests
import time
import re

class Huya(Platform):
    def __init__(self):
        Platform.__init__(self)
        self.platform = "huya"
    api = {
        "live_list": "http://www.huya.com/cache.php",
        "live_info": "http://www.huya.com"
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
        url = '/'.join([self.api["live_info"],uid])
        error,res = s_request(url)

        if not res:
            return data

        bsObj = BeautifulSoup(res.content,'html.parser')

        try:
            data = {
                "uid": uid,
                "avatar": bsObj.find(attrs={'id':'avatar-img'}).attrs["src"],
                "nickname": bsObj.find(attrs={'class':'host-name'}).text,
                "weight": 0,
                "signature": bsObj.find(attrs={'class':'notice-cont'}).text,
                "roomid": int(re.findall(r"l_p\s=\s\'(.+)\'",res.content)[0]),
                "followers": bsObj.find(attrs={'id':'activityCount'}).text
            }

        except Exception,e:
            self.error("huya get_user_info error," + str(uid) +",error:"+str(e))
        return data

    def get_hot_list(self,page_num):
        param = {
            "m": "LiveList",
            "do": "getLiveListByPage",
            "tagAll": "0",
            "page": page_num
        }
        data = []
        api_name = "get_hot_list"
        error,res = s_request(self.api["live_list"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["status"] == 200:
            data = res["data"]["datas"]
        return data

    def traverse_living(self, live_type="live",limit=200):
        """
        遍历获取当前所有直播，保存到redis
        :param  $live_type string 榜单类型
        :return:
        """
        data = []
        page_num = limit / 120
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
        api_name = "get_live_info"
        url = '/'.join([self.api["live_info"],live_id])
        error,res = s_request(url)

        if not res:
            return data

        bsObj = BeautifulSoup(res.content,'html.parser')

        try:
            live_type = re.findall(r"\"screenType\".+?\"(.+)\"",res.content)
            live_count = bsObj.find(attrs={'id':'live-count'})
            data = {
                "live_id": live_id,
                "uid": int(re.findall(r"l_p\s=\s\'(.+)\'",res.content)[0]),
                "title": bsObj.find(attrs={'class':'host-title'}).text,
                "watches": int(live_count.text.replace(',','')) if live_count else 0,
                "image": "",
                "is_end": 0 if live_type else 1,
                "extends":{
                    "category":bsObj.find(attrs={'class':'host-channel'}) \
                                .findAll(attrs={'class':'host-spl clickstat'})[1].text
                }
            }
        except Exception,e:
            self.error("huya get_live_info error," + str(uid) +",error:"+str(e))
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
