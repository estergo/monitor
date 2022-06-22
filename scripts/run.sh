#!/bin/bash
URL=$1
CUSTOMER=$2
SERVERS=$3
TEST=$4
MONITOR_SVC=$5
AUTH=$6
 while :
 do
    for ((n=1;n<=$SERVERS;n++))
     do
     NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)
     URL=$1/monitor.js?v=$NEW_UUID
     RES=$(curl -s -S -n $URL -H "X-MonitorNode:$CUSTOMER-$n" -o /null -w '%{http_code} %{speed_download} %{time_total} %{time_connect} %{url_effective}')
     IFS=" " INFO=($RES)
     curl -H "Authorization:Basic $AUTH" -d "customer=$CUSTOMER&node=$n&test=$TEST&duration=${INFO[2]}&timestamp=$(date +%s%3N)&status=${INFO[0]}" $MONITOR_SVC
     done
    sleep 5
 done


 
 