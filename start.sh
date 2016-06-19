#!/bin/bash
  
# run the redis server in the  background
redis-server&
# Get the PID of the server
redis_pid=$!

echo "Redis PID"
echo $redis_pid

sleep 2
gunicorn -c gunicorn.py --reload app:app

