import sys, os
from domino.core import log
from domino.pages import Title, Text
from domino.pages.start_page import Page as BasePage

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
    
    def create_menu(self, menu):
        pass


