#!/usr/bin/env python
# coding: utf-8
__author__ = 'Danny'

from instar import *
from live_platform.Huajiao import Huajiao

# -------------------------------------------------
# 主程序
# -------------------------------------------------
if __name__ == '__main__':
    db = get_mysql()
    log = get_logger()
    redis_ins = get_redis()
    instar = Instar()
    platform = ["huajiao"]
    crontab_time = 300  # 单位: 秒
    for pf in platform:
        # 动态产生平台实例
        pf_ins = eval(pf.capitalize() + '()')
        # 获取当前榜单数据保存到redis
        lives_hot = pf_ins.traverse_living("live")  # 当前热门榜
        lives_new = pf_ins.traverse_living("latest")  # 当前最新榜单
        lives_all = lives_hot + lives_new
        all_plat_users = instar.get_all_platform_users(pf)  # 平台所有用户id
        log.info("total crawled platform user in mysql: " + str(len(all_plat_users)))
        plat_bind_uid = instar.get_bind_platform_user(pf)  # 已绑定的平台所有用户id
        sent_room_ids = redis_ins.smembers("sent_" + pf)  # 已经添加到直播间队列的ids
        living_key = "living_" + pf  # redis缓存key name
        # 已经存在的live_id
        old_living_id = []
        for live_id in redis_ins.hkeys(living_key):
            # 将str转为int
            old_living_id.append(int(live_id))
        # 当前直播id数组
        now_living_id = []
        for live in lives_all:
            now_living_id.append(live["feed"]["relateid"])
        # 计算结束直播的id
        stop_living_id = list(set(old_living_id).difference(set(now_living_id)))
        log.info("stop living num: " + str(len(stop_living_id)))
        # 处理停播的
        for live_id in stop_living_id:
            # 取上次存的数据
            live_data = redis_ins.hget(living_key, live_id)
            if not live_data:
                continue
            live_data = json.loads(live_data)
            # 不是我们的绑定用户才直接保存直播信息
            # 绑定用户会从直播间发起保存请求，会附带直播间详细数据
            if live_data["uid"] in plat_bind_uid:
                continue
            live_info = pf_ins.get_live_info(live_id, True)
            if live_info["errno"] != 0:
                log.warning("get live info error " + str(live_id) + " " + live_info["errmsg"])
                continue
            if live_info["data"]["feed"]["duration"] == 0:
                log.warning("live still on living " + str(live_id))
                continue
            # 保存直播信息
            instar.save_live(pf, live_info["data"], live_data)
            # 从榜单池中删除
            redis_ins.hdel(living_key, live_id)
        # 删除上次直播数据
        redis_ins.delete("living_last")
        log.info("start deal lives ……")
        live_rank = 1  # 热门榜单排名
        hot_length = len(lives_hot)
        saved_users = []
        for live in lives_all:
            uid = int(live["author"]["uid"])
            live_id = live["feed"]["relateid"]
            if live_id in stop_living_id:
                # 停止播放的已处理
                continue
            data = {
                "live_id": live_id,
                "uid": uid,
                "live_title": live["feed"]["title"],
                "time": current_time()
            }
            # 前面的是热门榜,记录位置
            if live_rank <= hot_length:
                data["rank"] = live_rank
            # 之前已记录数据的话就累加
            old = redis_ins.hget(living_key, live_id)
            if live_id in old_living_id and old:
                old = json.loads(old)
                data["live_time"] = old["live_time"] + crontab_time / (60.0 * 60)  # 总直播小时数
                data["tf"] = old["tf"] + live["feed"]["watches"] / 60  # 观看人*小时
            else:
                data["live_time"] = crontab_time / (60.0 * 60)
                data["tf"] = live["feed"]["watches"] / 60
            # 保存当前榜单数据
            redis_ins.hset(living_key, live_id, json.dumps(data))
            # 首次上榜单，并且本次爬取没有保存过，才保存该用户到我们的数据库
            if uid not in all_plat_users and uid not in saved_users:
                log.info("new user " + str(uid))
                # 新用户加到redis队列，异步处理
                redis_ins.sadd("new_user_" + pf, uid)
                saved_users.append(uid)
            # 保存当前直播数据
            redis_ins.hset("living_last", live_id, json.dumps(live))
            live_rank += 1
        log.info(pf + " hot live deal completed")
    log.info("all platform hot live deal completed")
