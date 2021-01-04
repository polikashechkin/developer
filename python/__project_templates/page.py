from domino.core import log
from pages.base_page import Page as BasePage
from pages.base_page import Title, Toolbar, Input, InputText, Button

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)

    def __call__(self):
        Title(self, '{{page.name}}')

