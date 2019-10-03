# (C) 2019 IBM
# Author: Henrik Loeser
#
# Very short sample app to demonstrate the Log Analytics service on IBM Cloud.
# It offers a web form to change the log level and to send messages that
# then are logged.
from __future__ import unicode_literals

from django.http import JsonResponse
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render
from django import forms
import os
import logging
import json

import prometheus_client
import time
import random

# Metrics for endpoints that exist in this application, incremented when calling the logit, setLogLevel and createMetrics endpoints below.
logit_count = prometheus_client.Counter('wolam_logit_counter', 'A counter to keep track of calls to the logit endpoint.')
set_log_level_count = prometheus_client.Counter('wolam_set_log_level_counter', 'A counter to keep track of calls to the setLogLevel endpoint.')
create_metrics_count = prometheus_client.Counter('wolam_create_metrics_counter', 'A counter to keep track of calls to the createMetrics endpoint.')

# Example of metrics that are randomly incremented/decreased when calling the createMetrics endpoint.

# Counters go up, and reset when the process restarts.
api_count = prometheus_client.Counter('wolam_api_counter', 'An example counter to keep track of calls to an API endpoint.', ['method', 'endpoint'])

# Gauges can go up and down. Use set, inc or dec
active_session_gauge = prometheus_client.Gauge('wolam_active_session_gauge', 'An example counter to keep track of active sessions (can go up/down).') 

# Histograms track the size and number of events in buckets. This allows for aggregatable calculation of quantiles.
histogram = prometheus_client.Histogram('wolam_histogram', 'An example histogram')

# Summaries track the size and number of events.
summary = prometheus_client.Summary('wolam_summary', 'A summary')

prometheus_client.start_http_server(8002)

# get service information if on IBM Cloud
if 'VCAP_SERVICES' in os.environ:
    appenv = json.loads(os.environ['VCAP_APPLICATION'])
else:
    # Running locally, so build appenv JSON structure
    appenv = {}
    appenv['application_name'] = 'Local Log'

# Get an instance of a logger
logger = logging.getLogger(appenv["application_name"])

def index(request):
    return render(request, 'index.html')

def logit(request):
    logit_count.inc()
    # Access form data from app
    message=request.POST.get('message', '')
    level=request.POST.get('level', '')

    # Log to stdout stream
    print("Logit: Message:'",message,"' with level:'",level,"'")
    # Now log to stderr via logger
    if level=="critical":
        logger.critical(message)
    elif level=="error":
        logger.error(message)
    elif level=="warn":
        logger.warn(message)
    elif level=="info":
        logger.info(message)
    elif level=="debug":
        logger.debug(message)
    else:
        print("No valid combination passed in")
    # return message to JavaScript function in index page
    return JsonResponse({'smsg':message})    

def setLogLevel(request):
    set_log_level_count.inc()
    loggerlevel=request.POST.get('loggerlevel', '')
    # Log change to stdout
    print("setLogLevel: Setting to new level'",loggerlevel,"'")
    if loggerlevel=="critical":
        logger.setLevel(logging.CRITICAL)
    elif loggerlevel=="error":
        logger.setLevel(logging.ERROR)
    elif loggerlevel=="warn":
        logger.setLevel(logging.WARN)
    elif loggerlevel=="info":
        logger.setLevel(logging.INFO)
    elif loggerlevel=="debug":
        logger.setLevel(logging.DEBUG)
    else:
        print("No valid level passed in")

    # return message to JS function
    return HttpResponse("New log level set to "+loggerlevel)

def health(request):
    state = {"status": "UP"}
    return JsonResponse(state)

def createMetrics(request):
    create_metrics_count.inc()
    metriccount=request.POST.get('metriccount', '1')

    for x in range(int(metriccount)):
      api_count.labels('get', '/').inc()
      api_count.labels('post', '/submit').inc()
      active_session_gauge.set(random.random())
      histogram.observe(random.random())
      summary.observe(random.random())
      time.sleep(5)

    state = {"status": "Metrics Generated " + metriccount}
    return JsonResponse(state)

def log(request):
    context = {"log_page": "active"}
    return render(request, 'log.html', context)

def monitor(request):
    context = {"monitor_page": "active"}
    return render(request, 'monitor.html', context)

def handler404(request):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
