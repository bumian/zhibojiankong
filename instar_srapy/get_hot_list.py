#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'

from instar import *
from live_platform.Huajiao import Huajiao
from live_platform.Inke import Inke
from live_platform.Yizhibo import Yizhibo
from live_platform.Meipai import Meipai
import time
import requests

def get_es_type(time_stamp):
    type = time_stamp/(60 * 60 * 24) # 每天一个type
    return "hot_"+str(type)

if __name__ == '__main__':
    time_stamp =  int(time.time())
    log = get_logger()
    platform = ["huajiao","inke","yizhibo","meipai"]
    es = get_conf().get("es","url")
    for pf in platform:
        es_bulk = ""
        # 动态产生平台实例
        pf_ins = eval(pf.capitalize() + '()')
        lives_hot = pf_ins.traverse_living("live")  # 当前热门榜
        es_data = pf_ins.host_list_format(time_stamp,lives_hot) # 格式化用于存es
        head_line = {
            "create": { "_index": pf, "_type": get_es_type(time_stamp) }
        }
        for item in es_data:
            es_bulk = es_bulk + str(head_line) +"\n"+str(item)+"\n"
        es_url = es+"_bulk"
        requests.post(es_url,data=es_bulk.replace("\'","\""))
        log.info(pf + "get hot list finished")
    log.info("all platform hot list finished")
