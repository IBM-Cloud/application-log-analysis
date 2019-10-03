# (C) 2017 IBM
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

import prometheus_client as prom
import time
import random

counter = prom.Counter('wolam_counter', 'A counter')
gauge = prom.Gauge('wolam_gauge', 'A gauge')
histogram = prom.Histogram('wolam_histogram', 'An histogram')
summary = prom.Summary('wolam_summary', 'A summary')
prom.start_http_server(8002)

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
    metriccount=request.POST.get('metriccount', '1')

    for x in range(int(metriccount)):
      counter.inc(random.random())
      gauge.set(random.random() * 10)
      histogram.observe(random.random() * 10)
      summary.observe(random.random() * 10)
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
