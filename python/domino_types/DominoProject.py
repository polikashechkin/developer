
import os, sys, json
from domino.core import log, Version, DOMINO_ROOT
from jinja2 import Template

PYTHON = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_TEMPLATES = os.path.join(PYTHON, 'project_templates')

INDEX_HTML = Template(open(os.path.join(PROJECT_TEMPLATES, 'index.html')).read())
#APPLICATION_PY = Template(open(os.path.join(PROJECT_TEMPLATES, 'application.py')).read())
PAGE_PY = Template(open(os.path.join(PROJECT_TEMPLATES, 'page.py')).read())
BASE_PAGE_PY = Template(open(os.path.join(PROJECT_TEMPLATES, 'base_page.py')).read())

class ProjectPage:
    def __init__(self, module_name, page_id, name = None):
        self.page_id = page_id
        self.module_name = module_name
        self.url = f'/{module_name}/{page_id}'
        self.module = f'{module_name}.{page_id}'
        self.function = f'_{module_name}_{name}'
        self.name = name if name else page_id

    def create_file(self, module_root):
        page_file_py = os.path.join(module_root, 'python', self.module_name, f'{self.page_id}.py')
        os.makedirs(os.path.dirname(page_file_py), exist_ok=True)
        with open(page_file_py, 'w') as f:
            f.write(PAGE_PY.render(page=self))

class Navbar:
    def __init__(self, header):
        self.header = header
        self.items = []
        
class DominoProject:
    def __init__(self, module_id):
        self.module_id = module_id
        self.module_name = self.module_id
        self.version = Version.parse('11.7.0')
        self.module_root = os.path.join(DOMINO_ROOT, 'products', self.module_id, str(self.version))
        self.python_root = os.path.join(self.module_root, 'python')
        self.application_py = os.path.join(self.python_root, 'application.py')

    def create_base_page_py(self):
        PAGES = os.path.join(self.python_root, 'pages')
        os.makedirs(PAGES, exist_ok=True)
        with open(os.path.join(PAGES, 'base_page.py'), 'w') as f:
            f.write(BASE_PAGE_PY.render())

    def create_index_html(self):
        web = os.path.join(self.module_root, 'web')
        os.makedirs(web, exist_ok=True)
        index_html = os.path.join(web, 'index.html')
        with open(index_html, 'w') as f:
            f.write(INDEX_HTML.render(module_id=self.module_id))

    def create_application_py(self, pages, navbar):
        APPLICATION_PY = Template(open(os.path.join(PROJECT_TEMPLATES, 'application.py')).read())
        with open(self.application_py, 'w') as f:
            f.write(APPLICATION_PY.render(pages=pages, navbar=navbar))
        for page in pages:
            page.create_file(self.module_root)

    def create_on_activate_py(self):
        ON_ACTIVATE_PY = Template(open(os.path.join(PROJECT_TEMPLATES, 'on_activate.py')).read())
        on_activate_py = os.path.join(self.python_root, 'on_activate.py')
        with open(on_activate_py, 'w') as f:
            f.write(ON_ACTIVATE_PY.render())
    
    def create_hard_links(self, src_folder, dst_folder, src_file_names):
        os.makedirs(dst_folder, exist_ok=True)
        links = []
        for file_name in os.listdir(src_folder):
            if file_name in src_file_names:
                links.append([os.path.join(src_folder, file_name), os.path.join(dst_folder, file_name)])
        for src_file, dst_file in links:
            if not os.path.exists(dst_file):
                os.link(src_file, dst_file)

    def create_uwsgi_socket(self):
        vassal_ini = os.path.join(DOMINO_ROOT, 'uwsgi', 'vassals', f'{self.module_id}.active.ini')
        socked_sock = os.path.join(DOMINO_ROOT, 'uwsgi', 'sockets', f'{self.module_id}.active.sock')
        with open(vassal_ini, 'w') as f:
            f.write(f'[uwsgi]\n')
            f.write(f'chdir = {self.python_root}')
            f.write(f'socket = {socked_sock}\n')
            f.write(f'touch-reload = {self.application_py}\n')
            f.write(f'python-autoreload=1\n')
            f.write(f'harakiri = 10\n')
    
    def create_version_info(self):
        version_info = {}
        version_info['product'] = self.module_id
        version_info['id'] = self.module_id
        version_info['version'] = str(self.version)
        version_info['short_name'] = self.module_name
        version_info['description'] = self.module_name
        version_info['run_type'] = 'login'
        with open(os.path.join(self.module_root, 'info.json'), 'w') as f:
            json.dump(version_info, f, ensure_ascii=False)

    def create_module(self):
        if os.path.exists(self.module_root):
            raise Exception(f'Модуль уже существует')
        os.makedirs(self.module_root, exist_ok=True)
        os.makedirs(self.python_root, exist_ok=True)
        #----------------------------
        domino = os.path.join(self.python_root, 'domino')
        self.create_hard_links(
            os.path.join(DOMINO_ROOT, 'products', '_system', 'python', 'domino'), domino,
            ['core.py', 'application.py', 'account.py', 'page.py', 'page_controls.py', 'jobs.py', 'jobs_pages.py', 'postgres.py', 'databases.py']
            )
        tmplates = os.path.join(self.python_root, 'templates')
        self.create_hard_links(
            os.path.join(DOMINO_ROOT, 'products', '_system', 'python', 'templates'), tmplates,
            ['page.html', 'page_widgets.html', 'page_update.html']
            )
        #----------------------------
        draft = os.path.join(DOMINO_ROOT, 'products.draft', self.module_id)
        if not os.path.exists(draft):
            os.symlink(self.module_root, draft)
        #----------------------------
        self.create_base_page_py()
        pages = [
            ProjectPage('pages', 'start_page', self.module_name)
        ]
        navbar = Navbar(self.module_name)
        self.create_application_py(pages, navbar)
        self.create_on_activate_py()
        #----------------------------
        os.makedirs(os.path.join(self.python_root, 'procs'), exist_ok=True)
        #----------------------------
        self.create_version_info()
        self.create_index_html()
        self.create_uwsgi_socket()
