#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'
import urllib
from Util.func import *
from Platform import Platform
import requests
import time
from bs4 import BeautifulSoup

class Douyu(Platform):
    def __init__(self):
        Platform.__init__(self)
        self.platform = "douyu"
    api = {
        #"live_list": "https://m.douyu.com/roomlists",
        "live_info": "https://m.douyu.com/html5/live",
        "live_list":"https://capi.douyucdn.cn/api/v1/live",
        #https://capi.douyucdn.cn/api/v1/live/181?offset=0&limit=20&aid=android1&client_sys=android&time=1484152602
        #https://capi.douyucdn.cn/api/v1/getColumnRoom/9?offset=0&limit=20&client_sys=android
        "user_info": "http://apiv2.douyucdn.cn/H5/Anchor/home"
        #http://www.douyu.com/CateList/getColumnDetail?showVertical=0&short_name=game&relate=1&column_id=1
        #http://www.douyu.com/CateList/getchild?tagId=136
    }
    def set_account():
        pass

    def get_weight(self,weight):
        if 't' in weight:
            weight =  float(weight.replace('t','')) * 1000000
        elif 'kg' in weight:
            weight = float(weight.replace('kg','')) * 1000
        else:
            weight = float(weight.replace('g',''))
        return int(weight)

    def get_user_info(self, uid):
        """
        获取用户信息
        :param uid: user id
        :return:
        """
        param = {
            "client_sys": "android",
            "uid":uid
        }
        data = {}
        api_name = "get_user_info"
        error,s_res = s_request(self.api["user_info"],params=param)
        if not s_res:
            self.error("douyu get_user_info error," + str(uid) + ",error:" + str(error))
            return self.UNKNOWN_ERROR

        html = s_res.text
        if "error-data" in html:
            return data
        bsObj = BeautifulSoup(html,'html.parser')
        info = bsObj.find(attrs={'id':'js-owner-info'})
        if not info:
            return data
        user_info = info.find(attrs={'class':'info-anchor'})
        room_info = info.findAll(attrs={'class':'info-room-item'})

        try:
            level = int(user_info.find(attrs={'class':'anchor-name'}).img.attrs['src'].split('lv')[1].split('.')[0])
        except:
            level = ""
        try:
            data = {
                "uid":uid,
                "avatar": user_info.find(attrs={'class':'anchor-photo'}).attrs["src"],
                "nickname": user_info.find(attrs={'class':'name'}).text,
                "gender": "M" if user_info.find(attrs={'class':'icon-boy'}) else "F",
                "level": level if level else int(user_info.find(attrs={'class':'anchor-name'}).img.attrs['src'].split('_')[1].split('.')[0]),
                "signature": user_info.find(attrs={'class':'anchor-text-all'}).text,
                "roomid": int(room_info[0].text.strip().replace(' ','').split('\r\n')[1]),
                "weight": self.get_weight(room_info[1].text.strip().replace(' ','').split('\r\n')[1]),
                "followers": s_int(room_info[2].text.strip().replace(' ','').split('\r\n')[1])
            }
        except Exception,e:
            self.error("douyu get_user_info error," + str(uid) +",error:"+str(e))
        return data

    def get_hot_list(self,offset):
        param = {
            "offset":offset,
            "limit":100,
            "aid":"android1",
            "client_sys":"android",
            "time":int(time.time())
        }
        data = []
        api_name = "get_hot_list"
        error,res = s_request(self.api["live_list"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["error"] == 0:
            data = res["data"]
        return data

    def traverse_living(self, live_type="live",limit=200):
        """
        遍历获取当前所有直播，保存到redis
        :param  $live_type string 榜单类型
        :return:
        """
        data = []
        page_num = limit / 100
        for i in range(0,page_num):
            page = self.get_hot_list(i * 100)
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
            "roomId":live_id
        }
        data = []
        api_name = "get_live_info"
        error,res = s_request(self.api["live_info"], params=param)
        res = s_check(error,res,self.platform,api_name,self.log)
        if not res:
            return data

        if res["error"] == 0:
            d = res["data"]
            data = {
                "live_id": live_id,
                "uid": uid,
                "title": d.get("room_name",""),
                "watches": d.get("online",0),
                "image": d.get("room_src",""),
                "is_end": 0 if d["show_status"] == "1" else 1,
                "extends":{
                    "category":d.get("tag_name","未设置")
                }
            }
        else:
            self.error("douyu get_live_info error," + str(live_id) + " ," + res["msg"])
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
