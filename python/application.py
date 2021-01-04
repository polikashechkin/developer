import sys, os, json, sqlite3, arrow 
from flask import Flask, make_response, request, render_template
from domino.core import log
from domino.application import Application, Status
from domino.postgres import Postgres
 
POSTGRES = Postgres.Pool()
                                                                                                                                                                                                    
app = Flask(__name__)
application = Application(os.path.abspath(__file__), framework='MDL')
            
#-------------------------------------------    
import domino.pages.version_history
@app.route('/domino/pages/version_history', methods=['POST', 'GET'])
@app.route('/domino/pages/version_history.<fn>', methods=['POST', 'GET'])
def _domino_pages_version_history(fn = None):
    return application.response(request, domino.pages.version_history.Page, fn)
  
import domino.pages.procs
@app.route('/domino/pages/procs', methods=['POST', 'GET'])
@app.route('/domino/pages/procs.<fn>', methods=['POST', 'GET'])
def _domino_pages_procs(fn = None):
    return application.response(request, domino.pages.procs.Page, fn)
   
import domino.pages.proc_shedule
@app.route('/domino/pages/proc_shedule', methods=['POST', 'GET'])
@app.route('/domino/pages/proc_shedule.<fn>', methods=['POST', 'GET'])
def _domino_pages_proc_shedule(fn = None):
    return application.response(request, domino.pages.proc_shedule.Page, fn)
     
import domino.pages.jobs
@app.route('/domino/pages/jobs', methods=['POST', 'GET'])
@app.route('/domino/pages/jobs.<fn>', methods=['POST', 'GET'])
def _domino_pages_jobs(fn = None):
    return application.response(request, domino.pages.jobs.Page, fn)
            
import domino.pages.job
@app.route('/domino/pages/job', methods=['POST', 'GET'])
@app.route('/domino/pages/job.<fn>', methods=['POST', 'GET'])
def _domino_pages_job(fn = None):
    return application.response(request, domino.pages.job.Page, fn)
                
import domino.responses.job
@app.route('/domino/job', methods=['POST', 'GET'])
@app.route('/domino/job.<fn>', methods=['POST', 'GET'])
def _domino_responses_job(fn=None):
    return application.response(request, domino.responses.job.Response, fn)
#-------------------------------------------    
import pages.start_page
@app.route('/pages/start_page', methods=['POST', 'GET'])
@app.route('/pages/start_page.<fn>', methods=['POST', 'GET'])
def pages_start_page(fn = None):
    return application.response(request, pages.start_page.Page, fn, [POSTGRES])
       
import pages.module_create
@app.route('/pages/module_create', methods=['POST', 'GET'])
@app.route('/pages/module_create.<fn>', methods=['POST', 'GET'])
def pages_module_create(fn = None):
    return application.response(request, pages.module_create.Page, fn, [POSTGRES])
   
import pages.module_edit
@app.route('/pages/module_edit', methods=['POST', 'GET'])
@app.route('/pages/module_edit.<fn>', methods=['POST', 'GET'])
def pages_module_edit(fn = None):
    return application.response(request, pages.module_edit.Page, fn, [POSTGRES])
      
#< page /pages/test_accounts
import pages.test_accounts
@app.route('/pages/test_accounts', methods=['POST', 'GET'])
def pages_test_accounts():
    try: 
        return pages.test_accounts.Page(application, request).make_response()
    except BaseException as ex:
        log.exception(request.url)
        return f'{ex}', 500
@app.route('/pages/test_accounts.<fn>', methods=['POST', 'GET'])
def pages_test_accounts_fn(fn):
    try:
        return pages.test_accounts.Page(application, request).make_response(fn)
    except BaseException as ex:
        log.exception(request.url)
        return f'{ex}', 500

import pages.modules
@app.route('/pages/modules', methods=['POST', 'GET'])
def _pages_modules():
    return application.response(request, pages.modules.Page, None, [POSTGRES])
@app.route('/pages/modules.<fn>', methods=['POST', 'GET'])
def _pages_modules_fn(fn):
    return application.response(request, pages.modules.Page, fn, [POSTGRES])
   
from pages.module import ModulePage
@app.route('/pages/module', methods=['POST', 'GET'])
def pages_module():
    try:
        return ModulePage(application, request).make_response()
    except BaseException as ex:
        log.exception(request.url)
        return f'{ex}', 500
@app.route('/pages/modules.<fn>', methods=['POST', 'GET'])
def pages_module_fn(fn):
    try:
        return ModulePage(application, request).make_response(fn)
    except BaseException as ex:
        log.exception(request.url)
        return f'{ex}', 500
     
def navbar(page):    
    nav = page.navbar()
    nav.header('Разаботчик', 'pages/start_page')
    nav.item('Модули', 'pages/modules')
    nav.item('Учетные записи', 'pages/test_accounts')
    #nav.item('Задачи', 'jobs')
                                  
application['navbar'] = navbar

# DOMINO SECTION END
 