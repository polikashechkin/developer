import os, datetime
from domino.core import log
from domino.page import Page as BasePage
from domino.page_controls import Кнопка as Button

def IconButton(page, icon, **kwargs):
    return page.icon_button(icon, **kwargs)

def Title(page, text):
    return page.title(text)

def Toolbar(page, ID, **kwargs):
    return page.toolbar(ID, **kwargs)

def Input(page, **kwargs):
    return page.input(**kwargs)

def InputDate(page, **kwargs):
    return page.input(type='date', **kwargs)

def Table(page, ID, **kwargs):
    return page.Table(ID, **kwargs)

def InputText(page, ID = None, height=10, **kwargs):
    return page.textarea(ID, **kwargs).style(f'height:{height}rem')

def Text(page, ID = None, **kwargs):
    return page.text_block(ID, **kwargs)

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
    

