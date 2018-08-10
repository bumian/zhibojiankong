#!/usr/bin/env python
# coding: utf-8
__author__ = 'Danny'

import os
import web
import operator
from instar import *
from live_platform import *
from abc import ABCMeta, abstractmethod


urls = (
    '/', 'Index',
    '/user_info', 'UserInfo',
    '/user_gift_info', 'UserGiftInfo',
    '/user_feeds', 'UserFeeds',
    '/live_info', 'LiveInfo',
    '/live_data', 'LiveData',
    '/hot_list_pos', 'HotListPos',
    '/item_list','ItemList',
    '/get_follow_list','FollowList',
    '/add_follow','AddFollow',
    '/view_num','ViewNum'
)


class Api:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.ERROR_CODE = {
            "0": "操作成功",
            "2000": "instarx spider api server",
            "3000": "缺少参数",
            "3001": "不支持的平台",
            "5001": "没有获取到数据",
            "6001": "未知错误"
        }
        self.platforms = [ "huajiao", "inke", "yizhibo","taobao", \
                            "tmall", "meipai", "momo", "douyu", \
                            "bilibili", "panda", "huya", "zhanqi"
                            ]
        self.params = web.input(platform="", uid="", live_id="", start_time="",end_time="",suid="",duid="")
        self.pf = None
        self.time_start = time.time()
        self.es = get_conf().get("es","url")


    @abstractmethod
    def GET(self):
        pass

    @staticmethod
    def set_json_response():
        """
        设置响应content-type为json
        :return:
        """
        web.header('content-type', 'application/json;charset=utf-8', unique=True)

    def check_param(self, check_params):
        """
        检查输入参数
        :param check_params:
        :return:
        """
        for para in check_params:
            if not self.params.get(para):
                return self.json(3000)
        if self.params.platform not in self.platforms:
            return self.json(3001)
        else:
            module_name = self.params.platform.capitalize()
            self.pf = eval("{0}.{0}()".format(module_name))
        return ""

    def json(self, errno, data=None):
        """
        发送json格式响应
        :param errno:
        :param data:
        :return:
        """
        data = data if data else []
        self.set_json_response()
        res = {
            "errno": errno,
            "message": self.ERROR_CODE[str(errno)],
            "data": data,
            "time": round(time.time() - self.time_start, 2)
        }
        return json.dumps(res)

    def result(self, data):
        """
        根据查询结果返回json
        :param data:
        """
        if not data:
            return self.json(5001)
        else:
            return self.json(0, data)


class Index(Api):
    """
    首页
    """

    def GET(self):
        return self.json(2000)


class UserInfo(Api):
    """
    获取用户基本信息
    """

    def GET(self):
        check_res = self.check_param(["uid"])
        if check_res:
            return check_res
        data = self.pf.get_user_info(self.params.uid)
        if "SPIDER-INTERNALERROR" in data:
            internalerror()
        else:
            return self.result(data)


class UserGiftInfo(Api):
    """
    用户收礼送礼信息
    """

    def GET(self):
        check_res = self.check_param(["uid"])
        if check_res:
            return check_res
        data = self.pf.get_user_gift_info(self.params.uid)
        return self.result(data)


class UserFeeds(Api):
    """
    获取用户直播列表
    """

    def GET(self):
        check_res = self.check_param(["uid"])
        if check_res:
            return check_res
        data = self.pf.get_user_feeds(self.params.uid)
        return self.result(data)

class ItemList(Api):
    """
    获取用户宝贝列表
    """
    def GET(self):
        check_res = self.check_param(["live_id"])
        if check_res:
            return check_res
        data = self.pf.get_item_list(self.params.live_id, self.params.uid)
        return self.result(data)

class LiveInfo(Api):
    """
    获取直播的基本信息
    """

    def GET(self):
        check_res = self.check_param(["live_id"])
        if check_res:
            return check_res
        data = self.pf.get_live_info(self.params.live_id, self.params.uid)
        if "SPIDER-INTERNALERROR" in data:
            internalerror()
        else:
            return self.result(data)

class ViewNum(Api):
    """
    获取直播观看人数
    """

    def GET(self):
        check_res = self.check_param(["live_id"])
        if check_res:
            return check_res
        data = self.pf.get_view_num(self.params.live_id, self.params.uid)
        if "SPIDER-INTERNALERROR" in data:
            internalerror()
        else:
            return self.result(data)

class FollowList(Api):
    """
    拉关注列表
    """

    def GET(self):
        check_res = self.check_param(["uid"])
        if check_res:
            return check_res
        data = self.pf.get_follow_list(self.params.uid)
        return self.result(data)

class AddFollow(Api):
    """
    添加关注
    """

    def GET(self):
        check_res = self.check_param(["suid","duid"])
        if check_res:
            return check_res
        data = self.pf.add_follow(self.params.suid,self.params.duid)
        return self.result(data)

class LiveData(Api):
    """
    从elastic中查历史数据
    """

    def get_type(self):
        """
        计算es 的type名
        :return:
        """
        index = "*"
        if self.params.platform == "huajiao":
            # 花椒的直播id是8位递增数字
            index = int(self.params.live_id) / 100000
        elif self.params.platform == "inke":
            # 映客的直播id是毫秒时间戳+3位数字
            # 每10天一个type
            index = int(self.params.live_id) / (1000 * 1000 * 60 * 60 * 24 * 10)
        elif self.params.platform == "yizhibo":
            # 一直播的直播id取第一个字符
            index = self.params.live_id[0]
        return str(index)

    def GET(self):
        check_res = self.check_param(["live_id"])
        if check_res:
            return check_res
        es_type = self.get_type()
        url = self.es+"%s/live_%s/_search?q=live_id:\"%s\"&size=600" % \
              (str(self.params.platform), es_type, str(self.params.live_id))
        data = requests.get(url).json()
        live_data = []
        for hit in data["hits"]["hits"]:
            live_data.append(hit["_source"])
        live_data = sorted(live_data, key=operator.itemgetter('time'))
        return self.result(live_data)


class HotListPos(Api):
    """
    从elastic中查榜单数据
    """

    def get_type(self,time_stamp):
        """
        计算es 的type名
        :return:
        """
        return "hot_"+str(time_stamp/(60 * 60 * 24))

    def query_from_es_new(self):
        es_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "term": {
                                    "uid": self.params.uid
                                }
                            }
                        ]
                    }
                },
                "size": 1,
                "sort": {
                    "time_stamp": {
                        "order": "desc"
                    }
                }
            }
        url = self.es+"%s/%s/_search" % \
              (str(self.params.platform),self.get_type(int(time.time())))
        data = requests.post(url,json.dumps(es_query)).json()
        hot_data = []
        if len(data["hits"]["hits"]) == 0:
            return hot_data
        for hit in data["hits"]["hits"]:
            hot_data.append(hit["_source"])

        return hot_data


    def query_from_es(self,es_type):
        #es查询语句 返回大于start_time小于end_time且uid符合条件的
        es_query = {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "range": {
                                        "time_stamp": {
                                            "gt": self.params.start_time,
                                            "lt": self.params.end_time
                                        }
                                    }
                                },
                                {
                                    "term": {
                                        "uid": self.params.uid
                                    }
                                }
                            ]
                        }
                    },
                    "size": 1000,
                    "sort": [
                        "time_stamp"
                    ]
                }
        url = self.es+"%s/%s/_search" % \
              (str(self.params.platform), es_type)
        data = requests.post(url,json.dumps(es_query)).json()
        hot_data = []
        if len(data["hits"]["hits"]) == 0:
            return hot_data
        for hit in data["hits"]["hits"]:
            hot_data.append(hit["_source"])

        return hot_data

    def result_format(self,result):
        #输出结果格式化，不在榜单的自动补0
        sub = 30
        formated_result = []
        if not result:
            return formated_result
        start_time,end_time = self.params.start_time,self.params.end_time
        start_time = int(start_time)
        sub_count =  (result[0]["time_stamp"] - start_time) / sub
        while sub_count > 0:
                item = {
                        "time_stamp": result[0]["time_stamp"] - (sub_count * sub),
                        "uid": self.params.uid,
                        "pos": 0
                }
                formated_result.append(item)
                sub_count = sub_count - 1


        res_start_time = result[0]["time_stamp"]
        index = 0
        while res_start_time < (int(end_time) - sub):
                if index < len(result):
                    pos = result[index]["pos"]
                    #if result[index]["time_stamp"] != res_start_time:
                    if (result[index]["time_stamp"] - res_start_time) > sub:
                            pos = 0
                            index = index - 1
                    if 0 < (result[index]["time_stamp"] - res_start_time) <= sub:
                            pos = result[index]["pos"]
                else:
                    pos = 0
                item = {
                        "time_stamp": res_start_time,
                        "uid": self.params.uid,
                        "pos": pos
                }
                formated_result.append(item)
                index = index + 1
                res_start_time = res_start_time + sub
        return formated_result

    def GET(self):
        #接口1 返回一段时间热门变化
        check_res = self.check_param(["uid","start_time","end_time"])
        if check_res:
            #接口2 返回最新一条的热门排名
            check_res2 = self.check_param(["uid"])
            if check_res2:
                return check_res2
            #返回接口2
            return self.result(self.query_from_es_new())

        #返回接口1
        start_type = self.get_type(int(self.params.start_time))
        end_type = self.get_type(int(self.params.end_time))
        result = self.query_from_es(start_type)
        #如果跨天且数据不为空，就查天的数据合并
        if start_type != end_type:
            res_part2 = self.query_from_es(end_type)
            if not res_part2:
                result.extend(res_part2)
        return self.result(self.result_format(result))

def internalerror():
    return web.internalerror(LiveInfo().json(6001))

app = web.application(urls, globals())
app.internalerror = internalerror
application = app.wsgifunc()

if __name__ == "__main__":
    os.environ["PORT"] = "9090" if os.uname()[0] == "Darwin" else "80"
    app.run()
