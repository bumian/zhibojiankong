#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'

import requests
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def query_by_sid(sid):
    res = ""
    header = {
        "Cookie":"cna=PmZ3DeH99z4CAd9IVHB0zy8z; thw=cn; _m_h5_tk=fb7183c1edb1321e98a666e1279a73b8_1483337803750; _m_h5_tk_enc=ed3a3490cbd9a0352e0ae9839698eb7e; v=0; uc3=sg2=V3ic9JIleqtSSD4D%2BYQo6SGchWeorcAkmzDJBtf2ZMc%3D&nk2=GhIma1pFJ01bSQ%3D%3D&id2=WvKWWxPedZl9&vt3=F8dARHfL6%2F%2F4ebwb4To%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D; existShop=MTQ4MzMzODIyNQ%3D%3D; uss=WvA3bWgqUlIMD%2FoOybuRT63VrhK8foLuGD%2BtxpcOjy5lYnjw4hd8L3dHebE%3D; lgc=yyyyxxzzqq; tracknick=yyyyxxzzqq; cookie2=3c478239268413b571ad485fceb5f5dc; sg=q48; cookie1=UoKPUMSn88i36S7mEcmWbRkdPsUMFDEnuupvFH9lJZo%3D; unb=921465694; skt=a457e47777b74106; t=94f1bfb265da54755bd5ba4d96b06a61; _cc_=VFC%2FuZ9ajQ%3D%3D; tg=0; _l_g_=Ug%3D%3D; _nk_=yyyyxxzzqq; cookie17=WvKWWxPedZl9; mt=ci=10_1&cyk=0_0; _tb_token_=4oXXnIrAgU10; uc1=cookie16=UtASsssmPlP%2Ff1IHDsDaPRu%2BPw%3D%3D&cookie21=VFC%2FuZ9ainBZ&cookie15=VT5L2FSpMGV7TQ%3D%3D&existShop=true&pas=0&cookie14=UoW%2FXtcL9EMIMQ%3D%3D&tag=2&lng=zh_CN; apush3aa8830717656276433b67764b6e548c=%7B%22ts%22%3A1483342317313%2C%22parentId%22%3A1483342308285%7D; l=AhcXOZClel7CbpFx4Sv7/DwlJ5BhXuu-; isg=AvDwLUzFXJmn4ACefQva5pdRwbjAe2zRuI6Q2OpBvssepZJPkkl_Ev_Tnxc6"
    }
    url = "https://upload.taobao.com/auction/json/reload_cats.htm?customId=&fenxiaoProduct=&sid="+str(sid)
    res = requests.get(url,headers=header).json()
    try:
        res = res[0]
    except:
        pass

    return res

def get_child(res,path,category):
    child_list = []
    if not res:
        return child_list

    # if res["isBrand"] == "1":
    #     return child_list
    for main_data in res["data"]:
        for data in main_data["data"]:
            child = {
                "name":data["name"],
                "sid":data["sid"],
                "path":'/'.join([path,data["sid"]]),
                "category": '>>'.join([category, data["name"]]),
            }
            print "{sid}\t{name}\t{path}\t{category}".format(**child)
            child_list.append(child)

def get_root_list():
    root_list = []
    res = query_by_sid(262)
    for data in res["data"]:
        path = data["id"]
        category = data["name"]
        for chlid_data in data["data"]:
            chlid = {
                "name": chlid_data["name"],
                "sid": chlid_data["sid"],
                "category":'>>'.join([category,chlid_data["name"]]),
                "path": '/'.join([path,chlid_data["sid"]])
            }
            root_list.append(chlid)
    return  root_list


def tree_query(chlid_list):
    if not chlid_list:
        return
    for child in chlid_list:
        new_child = get_child(query_by_sid(child["sid"]), child["path"],child["category"])


def run():
    root_list = get_root_list()
    for root in root_list:
        print "{sid}\t{name}\t{path}\t{category}".format(**root)
        child = get_child(query_by_sid(root["sid"]),root["path"],root["category"])
        tree_query(child)


if __name__ == "__main__":
    run()
