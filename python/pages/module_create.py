import os, sys, json
from domino.core import log, Version, DOMINO_ROOT
from domino.page import Page as BasePage
from domino.pages import Input, Title, Button, Table, FlatTable
from settings import MODULE_ID
from components.module import Module

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
    
    def create(self):
        module_id = self.get('module_id')
        module_name = self.get('module_name', module_id)
        try:
            module = Module(module_id, name=module_name)
            module.create()
        except Exception as ex:
            log.exception(__file__)
            self.error(ex)
            return
        self.message(f'{module_id}, {module_name}')
    
    def __call__(self):
        Title(self, f'Создание нового модуля')
        table = FlatTable(self, 'table').css('table-hover', False).css('borderless')
        Input(table.row().cell(), name = 'module_id', label='Идетификатор')
        Input(table.row().cell(), name = 'module_name', label='Наименование')
        Button(self, 'создать').onclick('.create', forms=[table])
    

            
