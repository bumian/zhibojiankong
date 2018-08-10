#!/bin/bash

while true; do
    cd /root/instar_srapy
    python add_hot_users.py
    sleep 600
done
