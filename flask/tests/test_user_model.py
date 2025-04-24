import unittest
import time
from datetime import datetime
from app import create_app,db
from app.models import *

class UserModelTestCase(unittest.TestCase)
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app+