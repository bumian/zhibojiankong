    #!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'Danny'
from config import *
from instar import *
from abc import ABCMeta, abstractmethod
import json
import socket

class Platform:
    __metaclass__ = ABCMeta

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 4.2.2; zh-cn; HTC T329t Build/JDQ39E) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    }
    redis_ins = get_redis()
    log = get_logger()
    instar = Instar()
    host_name = socket.gethostname()
    page_num = 401
    proxies = {"http":"proxy.instarx.net:8080"}
    timeout = 0
    #proxies = ""
    sleep_time = 0
    platform = ""
    UNKNOWN_ERROR = "SPIDER-INTERNALERROR"

    def __init__(self):
        pass

    def set_page_num(self, page_num):
        """
        设置请求分页数量
        :param page_num: 每页数据量
        :return:
        """
        self.page_num = page_num

    def error(self, message):
        self.log.error(message)

    def alarm(self, s_type, message):
        data = {
            "src": "spider",
            "type": s_type,
            "detail": message + "\nFrom:" + self.host_name
        }
        self.log.error("[Alarm]\t"+message)
        self.redis_ins.rpush("bit_error_log",json.dumps(data))

    def check_res(self,res):
        try:
            res = res.json()
            if  res["data"]:
                return True
            else:
                return False
        except:
                return False

    @abstractmethod
    def set_account(self):
        """
        设置平台账号
        :return:
        """
        pass

    # 获取用户信息
    @abstractmethod
    def get_user_info(self, uid):
        pass

    # 获取用户收礼物信息
    @abstractmethod
    def get_user_gift_info(self, uid):
        pass

    @abstractmethod
    def get_live_info(self, live_id, uid):
        """
        获取直播信息
        必须包含is_end字段，取值0/1
        :param live_id:
        :param uid:
        :return:
        """
        pass

    @abstractmethod
    def get_user_feeds(self, uid):
        """
        获取用户直播列表
        :param uid: 用户id
        :return:
        """
        pass

    @abstractmethod
    def is_user_living(self, uid):
        """
        判断用户是否正在直播，如果正在直播返回直播信息
        直播信息必须包含is_living字段，取值0/1
        :param uid: 用户id
        :return: array
        """
        pass
