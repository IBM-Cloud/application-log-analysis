# (C) 2017 IBM
# Author: Henrik Loeser
#
# Very short sample app to demonstrate the Log Analytics service on IBM Cloud.
# It offers a web form to change the log level and to send messages that
# then are logged.

import os
from flask import Flask,redirect,render_template,request,jsonify
import json
import logging

app = Flask(__name__)

# get service information if on IBM Cloud / Cloud Foundry
if 'VCAP_SERVICES' in os.environ:
    appenv = json.loads(os.environ['VCAP_APPLICATION'])
else:
    # Running locally, so build appenv JSON structure
    appenv = {}
    appenv['application_name'] = 'Local Log'


# Return index page designed as single page application
@app.route('/', methods=['GET'])
def index():
    # log to both stdout and stderr, return template
    print "printed: rendering index"
    logger.info('logged: rendering index')
    return render_template('index.html')

# Receive message to be logged, log message and return response
@app.route('/logit', methods=['POST'])
def logit():
    # Access form data from app
    message=request.form['message']
    level=request.form['level']
    # Log to stdout stream
    print "Logit: Message:'",message,"' with level:'",level,"'"
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
        print "No valid combination passed in"

    # return message to JavaScript function in index page
    return jsonify(smsg=message)

# Adjust the server-side log level, controlled by function in index page
@app.route('/setLogLevel', methods=['POST'])
def setLogLevel():
    loggerlevel=request.form['loggerlevel']
    # Log change to stdout
    print "setLogLevel: Setting to new level'",loggerlevel,"'"
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
        print "No valid level passed in"

    # return message to JS function
    return "New log level set to "+loggerlevel


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    # Use StreamHandler to log messages
    handler = logging.StreamHandler()

    # Format the log message and include time, app name, log level and the message
    # Experiment with formats and included parts
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Or log in a JSON format if you want
    #formatter = logging.Formatter('{"time":"%(asctime)s", "appname": "%(name)s", "loglevel": "%(levelname)s", "msg": "%(message)s"}')

    # Activate our formatter
    handler.setFormatter(formatter)
    # Set logger name to our app name
    logger = logging.getLogger(appenv["application_name"])

    # Adjust server-side log level to "warning". Thus, info and debug level
    # is not logged initially.
    # Warning: this overwrites the handler level
    logger.setLevel(logging.WARN)

    # Add the handler to the logger
    logger.addHandler(handler)
    app.run(host='0.0.0.0', port=int(port))
