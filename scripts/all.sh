#!/bin/bash
URL=$1
TEST=$2
MONITOR_SVC=$3
AUTH=$4
sh ./run.sh $URL 106 5 $TEST $MONITOR_SVC $AUTH &
sh ./run.sh $URL 132 8 $TEST $MONITOR_SVC $AUTH &
sh ./run.sh $URL 126 2 $TEST $MONITOR_SVC $AUTH &
sh ./run.sh $URL 128 4 $TEST $MONITOR_SVC $AUTH &
sh ./run.sh $URL 114 3 $TEST $MONITOR_SVC $AUTH &
sh ./run.sh $URL 149 2 $TEST $MONITOR_SVC $AUTH &

