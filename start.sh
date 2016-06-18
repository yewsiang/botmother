#!/bin/bash
trap ctrl_c INT

function ctrl_c {
  kill $REDIS_PID;
}
  
# run the redis server and get its pid on background
redis-server&
REDIS_PID = $!

sleep 2
gunicorn -c gunicorn.py --reload app:app

