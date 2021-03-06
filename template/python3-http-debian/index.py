#!/usr/bin/env python
from flask import Flask, request, jsonify
from waitress import serve
import os
import logging

from function import handler
from elasticapm.contrib.flask import ElasticAPM

app = Flask(__name__)
apm = ElasticAPM(app)

logger = logging.getLogger('waitress')
logger.setLevel(logging.ERROR)
class Event:
    def __init__(self):
        self.body = request.get_data()
        self.headers = request.headers
        self.method = request.method
        self.query = request.args
        self.path = request.path

class Context:
    def __init__(self):
        self.hostname = os.getenv('HOSTNAME', 'localhost')

def format_status_code(res):
    if 'statusCode' in res:
        return res['statusCode']
    return 500

def format_body(res):
    if 'body' not in res:
        return jsonify({"message": res})
    return res['body']

def format_headers(res):
    if 'headers' not in res:
        return [('Content-type', 'application/json')]
    elif type(res['headers']) != dict:
        headers = res['headers']
        headers.append('Content-type', 'application/json')
        return headers
    headers = [('Content-type', 'application/json')]
    for key in res['headers'].keys():
        header_tuple = (key, res['headers'][key])
        headers.append(header_tuple)
    return headers

def format_response(res):
    if res == None:
        return (jsonify({"message": "Error: no response"}), 500, [('Content-type', 'application/json')])

    statusCode = format_status_code(res)
    body = format_body(res)

    headers = format_headers(res)

    return (body, statusCode, headers)

@app.route('/', defaults={'path': ''}, methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
def call_handler(path):
    event = Event()
    context = Context()

    response_data = handler.handle(event, context)
    
    res = format_response(response_data)
    return res

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000, channel_timeout=3600, asyncore_use_poll=True)
