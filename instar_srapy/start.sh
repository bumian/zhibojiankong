#!/usr/bin/env bash
pm2 start web_service.py -x --interpreter python --name 'spider_api'