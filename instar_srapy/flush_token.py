#!/usr/bin/env python
# coding: utf-8
__author__ = 'chenyong'

import time
import requests
from instar import *

timeout = 2
proxies = {"http": "proxy.instarx.net:8080"}
redis_ins = get_redis()
log = get_logger()


def get_token():
    result = ""
    url = "http://api.m.taobao.com/h5/mtop.mediaplatform.live.videolist/1.0/"
    try:
        res = requests.get(url, proxies=proxies, timeout=timeout)
        print(res.headers)
    except:
        res = requests.get(url)
        print(res.headers)
    try:
        token = res.headers["set-cookie"].split(';')[0]
        token_enc = res.headers["set-cookie"].split(';')[3].split(' ')[2]
        result = token + ";" + token_enc
    except:
        return result
    return result


def flush_token():
    token_list = []
    while len(token_list) < 208:
        time.sleep(1)
        token = get_token()

        if token:
            token_list.append(token)
            log.info("add token to redis:" + str(len(token_list)))
    redis_ins.set("taobao_token_new", json.dumps(token_list))
    log.info(str(len(token_list)) + " token update")


if __name__ == "__main__":
    flush_token()
    # get_token()
