import os, sys, json
from domino.core import log, Version, DOMINO_ROOT
from domino.account import Account
from domino.page import Page as BasePage
from domino.pages import Input, Title, Button, Table, FlatTable, CheckIconButton, Rows
from domino.page_controls import TabControl
from settings import MODULE_ID
from components.module import Module
from tables.postgres.test_account import TestAccount

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.module_id = self.attribute('module_id')
        self.version = self.attribute('version')
        self._module = None
     
    @property
    def module(self):
        if self._module is None:
            self._module = Module(self.module_id, version=self.version)
        return self._module
    
    def change_account_entry(self):
        id = self.get('id')
        test_account = self.postgres.query(TestAccount).get(id)
        account = Account(test_account.account_id)
        deleted = False
        products = []
        for product in account.info.js['products']:
            if product['id'] == self.module.id:
                deleted = True
            else:
                products.append(product)
        if not deleted:
            products.append({'id':self.module_id, 'version':'active'})
        
        account.info.js['products'] = products
        account.save()
        row = Rows(self, 'table').row(id)
        self.print_login_row(row, test_account)
        self.message(f'{id}')

    def print_login_row(self, row, test_account):
        account = Account(test_account.account_id)
        products = []
        try:
            for p in account.info.js.get('products'):
                products.append(p['id'])
        except:
            pass
        cell = row.cell(width=2)
        CheckIconButton(cell, self.module.id in products).onclick('.change_account_entry', {'id':test_account.id})

        row.cell().text(test_account.account_id)
        row.cell().text(account.info.name)

        row.cell().text(test_account.user_id)

    def print_login_table(self):
        table = Table(self, 'table')
        #table.column().text('Учетная запись')
        for test_account in self.postgres.query(TestAccount):
            row = table.row(test_account.id)
            self.print_login_row(row, test_account)

    def __call__(self):
        Title(self, f'{self.module.id}, {self.module.name}, {self.module.version}')
        self.print_login_table()
        
    

             
