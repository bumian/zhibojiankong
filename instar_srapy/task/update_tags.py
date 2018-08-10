#coding:'utf-8'
from live_platform.Taobao import Taobao
from config import *

if __name__ == "__main__":
    platform = "tmall"
    table = "instar.live_"+platform
    log_file = open(platform+"task.log",'a')
    taobao = Taobao()
    db = get_mysql()
    live_list = db.get_all("SELECT uid,liveid FROM "+table)
    for live in live_list:
        uid = live["uid"]
        liveid = live["liveid"]
        live_info = taobao.get_live_info(liveid,uid)
        if not live_info:
            out_head = "get live_info error"
        else:
            tags = live_info["extends"]["tags"]
            try:
                sql = "UPDATE " + table + " set tags =\'"+tags+"\'  WHERE  liveid=" + str(liveid) + " and uid=" + str(uid)
                db.query(sql)
                out_head = "update success"
            except:
                out_head = "db update error"
        out = "["+out_head+"]"+"-"+str(liveid)+"-"+str(uid)+"\n"
        print out.strip()
        db.commit()
        log_file.write(out)
