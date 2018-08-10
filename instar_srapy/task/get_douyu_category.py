#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'

import requests
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

type_list = {
        "game":"热门游戏",
        "ydyx":"移动游戏",
        "ylxtd":"鱼乐新天地",
        "yz":"颜值",
        "kj":"科技",
        "wykt":"文娱课堂",
        "znl":"正能量"
    }

api = {
    "cateList": "http://www.douyu.com/CateList/getColumnDetail",
    "child": "http://www.douyu.com/CateList/getchild"
}


def getCateList():
    for type,type_name in type_list.items():
        param = {
            "short_name":type
        }
        res = requests.get(api["cateList"],params=param).json()
        res = res["data"]
        for cate in res:
            data = {
                "cate_id": cate["tag_id"],
                "cate_name": cate["tag_name"],
                "id_path": cate["tag_id"],
                "name_path":'/'.join([type_name,cate["tag_name"]])
            }
            print "{cate_id}\t{cate_name}\t{id_path}\t{name_path}".format(**data)
            getChild(data["cate_id"],data["cate_name"],data["name_path"])

def getChild(tag_id,cate_name,name_path):
    param = {
        "tagId": tag_id
    }
    res = requests.get(api["child"], params=param).json()
    res = res["data"]
    for cate in res:
        data = {
            "cate_id": cate["id"],
            "cate_name": cate["name"],
            "id_path": '/'.join([tag_id,cate["id"]]),
            "name_path": '/'.join([name_path,cate["name"]])
        }
        print "{cate_id}\t{cate_name}\t{id_path}\t{name_path}".format(**data)



if __name__ == "__main__":
    getCateList()
