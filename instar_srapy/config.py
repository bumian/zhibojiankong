#!/usr/bin/env python
# coding: utf-8
import redis
import logging
import ConfigParser
from Util.MySQL import MySQL

__author__ = 'Danny'

redis_instance = None
db_instance = None
log_instance = None
config_reader = None

def get_conf():
    global config_reader
    if config_reader:
        return config_reader
    config_reader = ConfigParser.ConfigParser()
    config_reader.read("global.conf")
    return config_reader

def get_redis():
    global redis_instance
    if redis_instance:
        return redis_instance
    redis_config = {
        "host": get_conf().get("redis","host"),
        "port": 6379,
        "password": "qGNF2V6dhBr7OQcsl8j9iw"
    }
    redis_instance = redis.Redis(redis_config["host"], redis_config["port"], 0, redis_config["password"])
    return redis_instance


def get_logger():
    global log_instance
    if log_instance:
        return log_instance
    log_instance = logging.getLogger('live_logger')
    log_instance.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log_instance.addHandler(ch)
    return log_instance


def get_mysql():
    #global db_instance
    #if db_instance:
    #    return db_instance
    db_instance = MySQL(get_conf().get("mysql","host"), 'instar', '512vCUXMFHU2Wxe4F4+MSg==', 'instar')
    return db_instance
