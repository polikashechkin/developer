
import os, sys, json, time, datetime
from domino.core import log, Version, DOMINO_ROOT
from domino.page import Page as BasePage
from domino.page_controls import Кнопка as Button
from domino.page_controls import КраснаяКнопка
from domino.page_controls import TabControl
from domino.page_controls import Кнопка as Button
from domino.jobs import Proc
from jinja2 import Template
from domino.pages import Button, EditIconButton

#from domino_types.DominoProject import DominoProject
from tables.postgres.user_profile import UserProfile

def последняя_версия_продукта(product):
    последняя_версия = None
    for name in os.listdir(os.path.join(DOMINO_ROOT, 'products', product)):
        try:
            версия = Version.parse(name)
            if версия is not None and версия.is_draft:
                if последняя_версия is None or последняя_версия < версия:
                    последняя_версия = версия
        except:
            pass
    return последняя_версия

TheTabs = TabControl('modules_tabs')
TheTabs.item('all_tab', 'Все', 'all_tab')
TheTabs.item('favorites_tab', 'Избранные', 'favorites_tab')
 
class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.show_mode = self.attribute('show_mode')
    
    def create_and_publicate(self):
        product = self.get('product')
        version = Version.parse(self.get('версия'))
        ID = Proc.get_id(self.account_id, 'developer', 'create_and_publicate.py')
        if ID is None:
            ID = Proc.create(self.account_id, 'developer', 'create_and_publicate.py')
        NAME = f'{self.account_id}:developer:create_and_publicate:{product}:{version}'
        DESCRIPTION = f'Создание новой сборки {product}.{version}'
        INFO = {'product':product, 'version':str(version)}
        Proc.start_by_id(ID, name=NAME, description=DESCRIPTION, info=INFO)
        time.sleep(0.5)
        self.message(f'Запущено создание новой сборки {product} {version}')

    def all_tab(self):
        self.print_modules()

    def favorites_tab(self):
        toolbar = self.Toolbar('toolbar').mt(1)
        table = self.Table('table', mt=1)


    def switch_favourite(self):
        module_id = self.get('module_id')
        user_profile = self.postgres.query(UserProfile).filter(UserProfile.user_id == self.user_id, UserProfile.module_id == module_id).one_or_none()
        user_profile.favourite = not user_profile.favourite
        self.print_modules()

    def print_module_row(self, table, module_id, cur, user_profile):
        
        версия = последняя_версия_продукта(module_id)
        if версия is None:
            return
        try:
            with open(f'/DOMINO/products/{module_id}/{версия}/info.json') as f:
                info = json.load(f)
        except:
            return
        #-------------------------------------
        NAME = f'{self.account_id}:developer:create_and_publicate:{module_id}:{версия}'
        cur.execute('select ID, STATE from proc_jobs where name = ? order by ID desc limit 1', [NAME])
        job = cur.fetchone()
        if job:
            JOB_ID, JOB_STATE = job
        else:
            JOB_ID = None
            JOB_STATE = None
        #-------------------------------------
        row = table.row(module_id)
        cell = row.cell(width=1)
        if user_profile.favourite:
            button = cell.icon_button('check', style='color:green')
        else:
            button = cell.icon_button('check', style='color:lightgray')
        button.onclick('.switch_favourite', {'module_id':module_id})
        #-------------------------------------
        row.cell().href(module_id, 'pages/module', {'module_id':module_id, 'version':f'{версия}'})
        row.cell().text(info.get('short_name', ''))
        row.cell().text(info.get('description', ''))
        row.cell().text(f'{версия}')
        #-------------------------------
        text = row.cell().text_block()
        if JOB_ID:
            if JOB_STATE == Proc.Job.STATE_ONLINE:
                text.glif('spinner', css=' fa-pulse')    
            text.href(JOB_ID, 'job', {'job_id':JOB_ID})
        #-------------------------------------
        cell = row.cell(align='right')
        if JOB_ID and JOB_STATE == Proc.Job.STATE_ONLINE:
            pass
        else:
            EditIconButton(cell).onclick('pages/module_edit', {'module_id':module_id, 'version':str(версия)})
            Button(cell, 'Собрать')\
                .onclick('.create_and_publicate', {'product':module_id, 'версия' : str(версия)})\
                .tooltip('Создать и опубликовать новцю сборку')
        
        #-------------------------------

    def print_modules(self):
        cur = Proc.connect().cursor()
        table = self.Table('table', mt=1)
        table.column()
        table.column().text('ID')
        table.column().text('Краткое наименование')
        table.column().text('Полное наименование')
        table.column().text('Версия')
        table.column()
        for module_id in sorted(os.listdir(f'/DOMINO/products')):
            user_profile = self.postgres.query(UserProfile).filter(UserProfile.user_id == self.user_id, UserProfile.module_id == module_id).one_or_none()
            if not user_profile:
                user_profile = UserProfile(user_id=self.user_id, module_id = module_id, favourite = True, ctime=datetime.datetime.now())
                self.postgres.add(user_profile)
            if self.show_mode != 'all_modules' and not user_profile.favourite:
                continue
            self.print_module_row(table, module_id, cur, user_profile)

    def __call__(self):
        #account_id = self.request.account_id()
        self.title('Модули')
        toolbar = self.Toolbar('toolbar')
        select = toolbar.item().select(name='show_mode')
        select.option('', 'ТОЛЬКО МОДУЛИ В РАБОТЕ')
        select.option('all_modules','ВСЕ ДОСТУПНЫЕ МОДУЛИ')
        select.onchange('.print_modules', forms=[toolbar])
        #toolbar.item(ml='auto').input(name='module_id', label='Модуль')
        #КраснаяКнопка(toolbar.item(ml=0.5), 'Создать новый модуль').onclick('.create_module', forms=[toolbar])

        self.print_modules()
        #TheTabs(self)
            
