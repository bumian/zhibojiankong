# -*- encoding:utf8 -*-
"""
@author: peablog.com
@version: 2015-7-10
"""
import MySQLdb
import MySQLdb.cursors


class MySQL:
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        try:
            self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, cursorclass=MySQLdb.cursors.DictCursor)
            self.conn.select_db(db_name)
            self.conn.set_character_set("utf8mb4")
            self.cur = self.conn.cursor()
        except MySQLdb.Error as e:
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))

    # 切换数据库
    def select_db(self, db_name):
        try:
            self.conn.select_db(db_name)
        except MySQLdb.Error as e:
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))

    # 直接执行sql
    def query(self, sql):
        try:
            n = self.cur.execute(sql)
            return n
        except MySQLdb.Error as e:
            print("Mysql Error:%s\nSQL:%s" % (e, sql))

    # 查询并返回一条记录
    def get_one(self, sql):
        self.query(sql)
        result = self.cur.fetchone()
        return result

    # 查询并返回所有记录
    def get_all(self, sql):
        self.query(sql)
        result = self.cur.fetchall()
        return result

    # 插入一条记录
    def insert(self, table_name, data):
        for key in data:
            v = data[key]
            if isinstance(v, int) or isinstance(v, bool):
                v = str(v)
            data[key] = "'" + v.replace("'", "\\'").replace("\"", "\\\"") + "'"
        key = ','.join(data.keys())
        value = ','.join(data.values())
        real_sql = "INSERT INTO " + table_name + " (" + key + ") VALUES (" + value + ")"
        return self.query(real_sql)

    # 更新一条记录
    def update(self, table_name, field, value, data):
        sets = []
        for key in data:
            v = data[key]
            if isinstance(v, bool):
                v = str(v)
            if isinstance(v, str):
                v = v.replace("'", "\\'").replace("\"", "\\\"")
            if isinstance(v, int):
                sets.append(key + " = " + str(v))
            else:
                sets.append(key + " = '" + v + "'")
        values = ' , '.join(sets)
        real_sql = "UPDATE " + table_name + " set " + values + " WHERE " + field + "=" + str(value)
        return self.query(real_sql)

    def get_last_insert_id(self):
        return self.cur.lastrowid

    def rowcount(self):
        return self.cur.rowcount

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    print """usage :
    db = MySQL('hostname', 'username', 'password', 'dbname')
    print db.get_one("sql")
    """
