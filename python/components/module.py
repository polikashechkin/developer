
import os, sys, json
from domino.core import log, Version, DOMINO_ROOT
from jinja2 import Template
from domino.account import Account

PYTHON = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(PYTHON, 'components','module_templates')

class Module:

    class IndexHtml:
        TEMPLATE = Template(open(os.path.join(TEMPLATES, 'web','index.html')).read())
        def __init__(self, module):
            self.module = module

        def file(self):
            return os.path.join(self.module.root, 'web', 'index.html')
        
        def create(self):
            file = self.file()
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, 'w') as f:
                f.write(self.TEMPLATE.render(module=self.module))

    class Page:
        def __init__(self, module, path, name = None, is_system = False):
            # path : pages/my_page | my_page | domino/pages/my_page
            log.debug(f'Page({path}, is_system={is_system})')
            self.path = path
            self.url = f'/{path}'
            self.func = self.url.replace('/', '_')
            self.page_module = path.replace('/', '.')
            self.module = module
            self.is_system = is_system
            self.template = None
            if not is_system:
                template_file = os.path.join(TEMPLATES, 'python', f'{path}.py')
                log.debug(f'{template_file}')
                if not os.path.exists(template_file):
                    template_file = os.path.join(TEMPLATES, 'python', 'pages', 'page.py')
                log.debug(f'{template_file}')
                self.template = Template(open(template_file).read())

        def file(self):
            return 

        def create(self):
            if self.template:
                file = os.path.join(self.module.root, 'python', f'{self.path}.py')
                os.makedirs(os.path.dirname(file), exist_ok=True)
                with open(file, 'w') as f:
                    f.write(self.template.render(page=self, module=self.module))

    class Application:
        def __init__(self, module):
            self.module = module
            self.template = Template(open(os.path.join(TEMPLATES, 'python', 'application.py')).read())
            self.pages_template = Template(open(os.path.join(TEMPLATES, 'python','pages','__init__.py')).read())
            self.pages = []
            self.system_pages = []
            self.menuitems = []

        def page(self, path, is_system = False, name=None):
            page = Module.Page(self.module, path, is_system=is_system, name = name)
            if is_system:
                self.system_pages.append(page)
            else:
                self.pages.append(page)

        def menu(self, path, name):
            self.menuitems.append({'path':path, 'name':name})

        def create(self):
            # python/application.py
            file = os.path.join(self.module.root, 'python', 'application.py')
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, 'w') as f:
                f.write(self.template.render(application=self, module=self.module))
            
            # python/pages/__init__.py 
            file = os.path.join(self.module.root, 'python', 'pages', '__init__.py')
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, 'w') as f:
                f.write(self.pages_template.render(module=self.module))

            # python/pages/page.py 
            for page in self.pages:
                if not page.is_system:
                    page.create()

    class OnActivate:
        def __init__(self, module):
            self.module = module
            self.template = Template(open(os.path.join(TEMPLATES, 'python', 'on_activate.py')).read())

        def file(self):
            return os.path.join(self.module.root, 'python', 'on_activate.py')

        def create(self):
            file = self.file()
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, 'w') as f:
                f.write(self.template.render())

    class VersionInfo:
        def __init__(self, module, name = None):
            self.module = module
            self.exists = False
            #-----------------------------------
            self.version_info = {}
            self.version_info['product'] = self.module.id
            self.version_info['id'] = self.module.id
            self.version_info['version'] = str(self.module.version)
            self.version_info['short_name'] = name if name else module.id
            self.version_info['description'] = name if name else module.id
            self.version_info['run_type'] = 'login'
            try:
                with open(os.path.join(self.module.root, 'info.json')) as f:
                    self.version_info = json.load(f)
                self.exists = True
            except:
                log.exception(__file__)
            #-----------------------------------
            self.settings_json = {}
            self.settings_json['start_page'] = f"/python/pages/start_page"
            try:
                with open(os.path.join(self.module.root, 'settings.json')) as f:
                    self.settings_json = json.load(f)
            except:
                log.exception(__file__)
        
        def create(self):
            with open(os.path.join(self.module.root, 'info.json'), 'w') as f:
                json.dump(self.version_info, f, ensure_ascii=False)
            with open(os.path.join(self.module.root, 'settings.json'), 'w') as f:
                json.dump(self.settings_json, f, ensure_ascii=False)
            self.exists = True

    class System:
        def __init__(self, module):
            self.module = module
            self.root = os.path.join(DOMINO_ROOT, 'products', '_system')
            self.system_modules = []

        def hard_link(self, src, dst, file_names, recursive):
            log.debug(f'hard_link(self, {src}, {dst}, {file_names}, {recursive})')
            os.makedirs(dst, exist_ok=True)
            for file_name in os.listdir(src):
                if file_names and file_name not in file_names:
                    continue
                src_file = os.path.join(src, file_name)
                dst_file = os.path.join(dst, file_name)
                if os.path.isfile(src_file):
                    if not os.path.exists(dst_file):
                        os.link(src_file, dst_file)
                elif os.path.isdir(src_file):
                    self.hard_link(src_file, dst_file, file_names, recursive)

        def include(self, src, dst, files=None, recursive=False):
            system_module = {}
            system_module['src'] = src
            system_module['dst'] = dst
            system_module['files'] = files
            system_module['recirsive'] = recursive
            self.system_modules.append(system_module)

        def create(self):
            for system_module in self.system_modules:
                src = os.path.join(self.root, system_module['src'])
                dst = os.path.join(self.module.root, system_module['dst'])
                self.hard_link(src, dst, system_module.get('files'), system_module.get('recursive'))

    def __init__(self, id, version = '11.7.0', name = None):
        self.id = id
        self.version = Version.parse(version)
        self.root = os.path.join(DOMINO_ROOT, 'products', self.id, str(self.version))
        log.debug(f'{self.root}')
        self.version_info = Module.VersionInfo(self, name)
    
    @property
    def name(self):
        return self.version_info.version_info.get('short_name')

    def create_uwsgi_socket(self):
        vassal_ini = os.path.join(DOMINO_ROOT, 'uwsgi', 'vassals', f'{self.id}.active.ini')
        socked_sock = os.path.join(DOMINO_ROOT, 'uwsgi', 'sockets', f'{self.id}.active.sock')
        application_py = os.path.join(self.root, 'python', 'application.py')
        with open(vassal_ini, 'w') as f:
            f.write(f'[uwsgi]\n')
            f.write(f'chdir = {os.path.dirname(application_py)}\n')
            f.write(f'socket = {socked_sock}\n')
            f.write(f'touch-reload = {application_py}\n')
            f.write(f'python-autoreload=1\n')
            f.write(f'harakiri = 10\n')

    '''    
    def is_active(self, account_id):
        account = Account(account_id)
        info = account.info.js
        products = info.get('products')
        if products is None:
            products = []
            info['products'] = products
        for product in products:
            if product.id == self.id:
                return True
        return False

    def activate(self, account_id):
        account = Account(account_id)
        info = account.info.js
        products = info.get('products')
        if products is None:
            products = []
            info['products'] = products
        for product in products:
            if product.id == self.id:
                return
        products.append({'id':self.id, 'version':'active'})
    '''
    def create(self): 
        if os.path.exists(self.root):
            raise Exception(f'Модуль уже существует')
        os.makedirs(self.root, exist_ok=True)
        #----------------------------
        self.version_info.create()
        Module.IndexHtml(self).create()
        #----------------------------
        application = Module.Application(self)
        application.page('pages/start_page')
        application.page('domino/pages/procs', is_system=True, name='Процедуры')
        application.page('domino/pages/jobs', is_system=True)
        application.page('domino/pages/job', is_system=True)
        application.create()
        #----------------------------
        system = Module.System(self)
        system.include('python/domino', 'python/domino', files=['core.py', 'application.py', 'account.py', 'page.py', 'page_controls.py', 'jobs.py'])
        system.include('python/templates', 'python/templates', files=['page.html', 'page_widgets.html', 'page_update.html'])
        system.include('python/databases', 'python/domino/databases', recursive=True)
        system.include('python/pages', 'python/domino/pages', recursive=True)
        system.include('python/responses', 'python/domino/responses', recursive=True)
        system.include('python/components', 'python/domino/components', recursive=True)
        system.include('python/tables', 'python/domino/tables', recursive=True)
        system.create()
        #----------------------------
        Module.OnActivate(self).create()
        #----------------------------
        draft_folder = os.path.join(DOMINO_ROOT, 'products.draft', self.id)
        if os.path.exists(draft_folder):
            os.remove(draft_folder)
        os.symlink(self.root, draft_folder)
        active_folder = os.path.join(os.path.dirname(self.root), 'active')
        if os.path.exists(active_folder):
            os.remove(active_folder)
        os.symlink(self.root, active_folder)
        self.create_uwsgi_socket()
