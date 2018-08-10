#!/usr/bin/env bash
cd /root/instar_srapy
git pull
pm2 restart 'spider_api'