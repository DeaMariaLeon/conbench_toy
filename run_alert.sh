#! /bin/bash

cp ~/conbench/conbench_toy/asv_processed_files_server /tmp/asv_processed_files_server
cp asv_processed_files_server asv_processed_files_serverOLD
cp ~/conbench/conbench_toy/asv_processed_files_server .
cp alert_processed_files_server alert_processed_files_serverOLD
cp -r ./output/* ./outputOLD
~/miniforge3/envs/conbench-env/bin/python alert.py 2>&1 &

echo "Alert run: $(date)" >> /home/bench/conbench/conbench_alert/conbench_toy/log/alert.log 2>&1