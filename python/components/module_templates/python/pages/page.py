import sys, os
from domino.core import log
from . import Page as BasePage
from domino.pages import *

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
    

