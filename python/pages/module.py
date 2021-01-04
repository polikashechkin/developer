 
import os, sys, json
from domino.core import log, Version, DOMINO_ROOT
from domino.page import Page
from domino.page_controls import Кнопка as Button
from domino.page_controls import TabControl
from domino.jobs import Proc

MODULE_ID = 'developer'

class ModulePage(Page):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.module_id = self.attribute('module_id')
        self.version = self.attribute('version')
        self.folder = os.path.join(DOMINO_ROOT, 'products', self.module_id, self.version)
        self.info_file = os.path.join(self.folder, 'info.json')
        self.load_info()
    
    def load_info(self):
        with open(self.info_file) as f:
            self.info = json.load(f)
    def save_info(self):
        with open(self.info_file, 'w') as f:
            json.dump(self.info, f, ensure_ascii=False)
    
    def create_and_publicate(self):
        ID = Proc.get_id(self.account_id, MODULE_ID, 'create_and_publicate.py')
        if ID is None:
            ID = Proc.create(self.account_id, MODULE_ID, 'create_and_publicate.py')
        NAME = f'{self.account_id}:developer:create_and_publicate:{self.module_id}:{self.version}'
        DESCRIPTION = f'Создание новой сборки {self.module_id}.{self.version}'
        INFO = {'product':self.module_id, 'version':str(self.version)}
        Proc.start_by_id(ID, name=NAME, description=DESCRIPTION, info=INFO)
        self.message(f'Запущено создание новой сборки {self.module_id} {self.version}')

    def __call__(self):
        self.title(f'{self.module_id} {self.version}')
        table = self.Table('table')
        row = table.row()
        row.cell().text('Краткое наименование')
        row.cell().text(self.info.get('short_name'))
        row = table.row()
        row.cell().text('Полное наименование')
        row.cell().text(self.info.get('description'))

            
