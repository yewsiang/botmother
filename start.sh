#!/bin/bash
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

redis-server&
# Get the PID of the server
redis_pid=$!

echo "Redis PID"
echo $redis_pid

sleep 2
gunicorn -c gunicorn.py --reload app:app

