import os


def numCPUs():
    if not hasattr(os, "sysconf"):
        raise RuntimeError("No sysconf detected.")
    return os.sysconf("SC_NPROCESSORS_ONLN")

bind = "0.0.0.0:8000"
# workers = numCPUs() * 2 + 1
workers = 1
backlog = 2048
worker_class = "sync"
# worker_class = "gevent"
debug = True
# daemon = True
# errorlog = 'gunicorn-error.log'
# accesslog = 'gunicorn-access.log'
# log-file= -
loglevel = 'debug'
