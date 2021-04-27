#!/usr/bin/env python
from flask import Flask, request, jsonify
from waitress import serve
import os

from function import handler
from elasticapm.contrib.flask import ElasticAPM

app = Flask(__name__)

apm = ElasticAPM(app)

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
    return 200

def format_body(res):
    if 'body' not in res:
        return jsonify({})
    elif type(res['body']) == dict:
        return jsonify(res['body'])
    else:
        return jsonify({"body": str(res['body'])})

def format_headers(res):
    if 'headers' not in res:
        return [('Content-type', 'application/json')]
    elif type(res['headers']) == dict:
        headers = [('Content-type', 'application/json')]
        for key in res['headers'].keys():
            header_tuple = (key, res['headers'][key])
            headers.append(header_tuple)
        return headers
    headers = res['headers'].append('Content-type', 'application/json')
    return headers

def format_response(res):
    if res == None:
        return ('', 200)

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
    serve(app, host='0.0.0.0', port=5000)
