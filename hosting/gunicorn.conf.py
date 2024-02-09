import logging
import multiprocessing
import sys

bind = "0.0.0.0:80"
workers = 1
threads = multiprocessing.cpu_count()
wsgi_app = "P8yStickyScale:app"
accesslog = "-"
errorlog = "/error_log.txt"
loglevel = "debug"
