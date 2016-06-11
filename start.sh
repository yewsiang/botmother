#!/bin/sh
gunicorn -c gunicorn.py --reload app:app

