
import os, sys, json
from domino.core import log, Version, DOMINO_ROOT
from domino.page import Page as BasePage
from domino.page_controls import Кнопка as Button
from domino.page_controls import КраснаяКнопка
from domino.page_controls import TabControl
from domino.page_controls import Кнопка as Button
from jinja2 import Template
from domino.postgres import Postgres
from domino.account import find_account_id, Account

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.pg_connection = Postgres.connect(self.account_id)
        self.pg_cursor = self.pg_connection.cursor()
    
    def print_account_row(self, row, account_id, user_id):
        account = Account(account_id)
        cell = row.cell()
        cell.text(f'{account_id} {account.info.name}')
        #row.cell().text(account.info.js)
        cell = row.cell()
        cell.text(user_id)

    def print_accounts(self):
        toolbar = self.Toolbar('toolbar').mt(1)
        toolbar.item(ml='auto').input(name='account_id', label='Учетная запись')
        toolbar.item(ml=0.5).input(name='user_id', value='FIRST_USER', label='Пользователь')
        КраснаяКнопка(toolbar.item(ml=0.5), 'Создать').onclick('.on_create', forms=[toolbar])

        table = self.Table('table', mt=1)
        table.column().text('Учетная запись')
        table.column().text('Пользователь')
        self.pg_cursor.execute('select "id", "account_id", "user_id" from "testaccount" order by account_id')
        for id, account_id, user_id in self.pg_cursor.fetchall():
            row = table.row(id)
            self.print_account_row(row, account_id, user_id)

    def on_create(self):
        try:
            account_query = self.get('account_id')
            if not account_query:
                self.error('Не задана учетная запись')
                return
            account_id = find_account_id(account_query)
            if account_id is None:
                self.error(f'Нет такой учетной записи "{account_query}"')
                return
            user_id = self.get('user_id')
            with self.pg_connection:
                self.pg_cursor.execute('insert into TestAccount (account_id, user_id) values(%s,%s)', [account_id, user_id])
            self.print_accounts()
        except BaseException as ex:
            log.exception(__file__)
            self.error(f'{ex}')

    def __call__(self):
        self.title('Учетные записи')
        self.print_accounts()

