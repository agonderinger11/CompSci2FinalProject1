from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import os
from bankAccGui import * 

#add type hinting, docstrings, private class variables, error handling
class Logic(QMainWindow, Ui_MainWindow): 
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        
        self.loginButton.clicked.connect(self.getLoginInfo)
        self.submitButton.clicked.connect(self.getSignInInfo)
        
    def getLoginInfo(self):
        print(self.usernameEntry.text(), self.passwordEntry.text())
        return self.usernameEntry.text(), self.passwordEntry.text()
    
    def getSignInInfo(self):
        print(self.usernameSUentry.text(), self.passwordSUentry.text())
        return self.usernameSUentry.text(), self.passwordSUentry.text()