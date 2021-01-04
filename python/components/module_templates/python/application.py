import sys, os
from flask import Flask, request
from domino.core import log 
from domino.application import Application

app = Flask(__name__)
application = Application(os.path.abspath(__file__), framework='MDL')

# ----------------------------------------------
{%- for page in application.system_pages %}
import {{page.page_module}}
@app.route('{{page.url}}', methods=['POST', 'GET'])
@app.route('{{page.url}}.<fn>', methods=['POST', 'GET'])
def {{page.func}}(fn=None):
    return application.response(request, {{page.page_module}}.Page, fn)
{% endfor %}
# ----------------------------------------------
{%- for page in application.pages %}
import {{page.page_module}}
@app.route('{{page.url}}', methods=['POST', 'GET'])
@app.route('{{page.url}}.<fn>', methods=['POST', 'GET'])
def {{page.func}}(fn=None):
    return application.response(request, {{page.page_module}}.Page, fn)
{% endfor %}
# ----------------------------------------------
def navbar(page):
    nav = page.navbar()
    nav.header('{{module.name}}', 'pages/start_page')
{%- for item in application.menuitems %}
    nav.item('{{item.name}}', '{{item.path}}')
{%- endfor %}
application['navbar'] = navbar
 