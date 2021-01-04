#< import
import sys
import os
from flask import Flask, request
from domino.core import log
from domino.application import Application

app = Flask(__name__)
application = Application(os.path.abspath(__file__), framework='MDL')

{%- for page in pages %}
#< {{page.url}}
import {{page.module}}
@app.route('{{page.url}}', methods=['POST', 'GET'])
def {{page.function}}():
    try:
        page = {{page.module}}.Page(application, request)
        return page.make_response()
    except BaseException as ex:
        log.exception(request.url)
        return f'{ex}', 500
@app.route('{{page.url}}.<fn>', methods=['POST', 'GET'])
def {{page.function}}_fn(fn):
    try:
        page = pages.start_page.Page(application, request)
        return page.make_response(fn)
    except BaseException as ex:
        log.exception(request.url)
        return f'{ex}', 500
{%- endfor %}

#< navbar
def navbar(page):    
    nav = page.navbar()
    nav.header('{{navbar.header}}', 'pages/start_page')
{%- for item in navbar.items %}
    nav.item('{{item.name}}', '{{item.url}}')
{%- endfor %}
application['navbar'] = navbar
#>

