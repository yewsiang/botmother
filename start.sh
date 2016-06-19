#!/bin/bash
# kills everything in background on exit
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

echo "Gunicorn starting!"
gunicorn -c gunicorn.py --reload app:app

