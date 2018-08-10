#!/bin/sh
cur_path=$(cd `dirname $0`; pwd)
now=$(date +"%Y_%m_%d_%H_%M_%S")
python $cur_path"/get_living.py"  > "$cur_path/logs/$now.log" 2>&1 &