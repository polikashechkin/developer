from domino.core import log

from domino.pages.start_page import Page as BasePage

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)

    def create_menu(self, menu):
        group = menu.group('')
        group.item('Модули', 'pages/modules')
        group.item('Создать новый модуль', 'pages/module_create')
        group.item('Учетные записи', 'pages/test_accounts')
        group.item('Процедуры', 'domino/pages/procs')


