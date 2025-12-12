from PyQt6.QtWidgets import *
import os
import csv
import re
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from bankAccGui import * 

#add type hinting, docstrings, private class variables, error handling
class Logic(QMainWindow, Ui_MainWindow): 
    LOGINPATH = os.path.join('files', 'loginInfo.csv')
    HISTORYPATH = os.path.join('files', 'history.csv')
    
    def __init__(self) -> None:
        """
        Initializes the GUI and checks to see if system files exist. If they do not they are created with their headers only.
        Connects buttons to functions
        Sets up chart as well
        """
        super().__init__()
        self.setupUi(self)
        
        self.initFiles()
        self.initChart()
        
        
        self.loginButton.clicked.connect(self.loginButtonFunc)
        self.submitButton.clicked.connect(self.signUpButtonFunc)
        self.depositButton.clicked.connect(self.depositFunc)
        self.withdrawButton.clicked.connect(self.withdrawFunc)
        self.transferButton.clicked.connect(self.transferFunc)
        self.signOutButton.clicked.connect(self.signOut)
        
    def initFiles(self) -> None:
        """
        Checks to see if the files exist when the program is run. If they are not there they are created
        """
        if not self.doesFileExist(self.LOGINPATH): #checks to see if the info file is there upon initialization
            with open(self.LOGINPATH, 'w', newline='') as output:
                CSVwriter = csv.writer(output)
                CSVwriter.writerow(['username', 'password', 'checkingBalance', 'savingBalance', 'depositsUntilInterest'])
                
        if not self.doesFileExist(self.HISTORYPATH):
            with open(self.HISTORYPATH, 'w', newline='') as output:
                CSVwriter = csv.writer(output)
                CSVwriter.writerow(['username', 'timestamp', 'totalBalance'])

    def initChart(self) -> None:
        """Sets up the matplotlib canvas once."""
        # Create layout if it doesn't exist
        if self.chartWidget.layout() is None:
            layout = QVBoxLayout(self.chartWidget)
            layout.setContentsMargins(0, 0, 0, 0)
            self.chartWidget.setLayout(layout)

        # Create Figure and Canvas
        self.fig = Figure(figsize=(4, 2.5), dpi=80)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.chartWidget.layout().addWidget(self.canvas)
        
    def validateAmount(self, text) -> float:
        """Parses and validates monetary input."""
        try:
            amount = float(text.strip().strip('$'))
            if amount <= 0:
                raise ValueError("Amount must be positive")
            return amount
        except ValueError:
            self.errorLabel.setText("Please enter a valid monetary amount")
            return None
    
    def getLoginInfo(self) -> str:
        """
        A helper function that gets the text from the login boxes on login page. 
        """
        return self.usernameEntry.text().strip().lower(), self.passwordEntry.text().strip()
    
    def getSignInInfo(self) -> str:
        """
        A helper function that gets the text from the sign in boxes on login page. 
        """
        return self.usernameSUentry.text().strip().lower(), self.passwordSUentry.text().strip()
    
    def loginButtonFunc(self) -> None:  #Check to see if info is in the loginInfo csv and if it is let the user see the bank info.
        """
        Handles logic of the login button and gets info from system documents. 
        If sign in fails gives errors message
        If login succeeds change the stacked index to the home page. 
        """
        username, password = self.getLoginInfo()
        
        with open(self.LOGINPATH, 'r') as file: 
            csvReader = csv.reader(file)
            next(csvReader)
            
            for row in csvReader:
                if row[0] == username and row[1] == password:
                    self.stackedWidget.setCurrentIndex(1)
                    self.syncMainPage()
                
        self.signInMessage.setText("Login failed: Username or password is incorrect")

    def signUpButtonFunc(self) -> None:
        """
        Allows users to create new accounts.
        Usernames must not be taken and password must meet requirements to be stored. 
        Handles error messages if these criteria are not met. 
        """
        username, password = self.getSignInInfo()
        data = [username, password, 0.00, 0.00, 5]
        
        #Check to ensure password quality
        reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#%])[A-Za-z\d@$#%]{7,20}$" #got the regex from online 
        pattern = re.compile(reg) #googled this function
        match = re.search(pattern, password) #returns a boolean based on if the password meets complexity requirements
        
        # first check to see if user name is already in the csv
        with open(self.LOGINPATH, 'r') as file: 
            csvReader = csv.reader(file)
            next(csvReader)
            
            for row in csvReader:
                if row[0] == username:
                    self.passwordEntryLabel.setText("Username already in use.\nPlease pick a different one.")
                    return 
        
        if match and len(username) > 4: 
            with open(self.LOGINPATH, 'a', newline='') as file2: 
                CSVwriter = csv.writer(file2)
                CSVwriter.writerow(data)
            
            self.passwordEntryLabel.setText("Sign up successful! \nPlease login with your credintials")
            self.usernameSUentry.setText("")
            self.passwordSUentry.setText("")
            
        else:
            self.passwordEntryLabel.setText("Password does not meet complexity requirements or \nUsername too short \nPlease try again")

    def doesFileExist(self, path) -> bool: 
        """
        Helper function to provide reducency by checking to see if file exists and returning a boolean. 
        """
        return os.path.isfile(path)
    
    def syncMainPage(self) -> None:
        """
        Most important function and dictates the home pages display based on who is signed in. 
        Gets the username and their info the login info.csv
        Updates all the labels and displays the chart only if the user exists.
        This function is called everytime the homepage needs updated
        """
        username, password = self.getLoginInfo()
        
        with open(self.LOGINPATH, 'r') as file: 
            csvReader = csv.reader(file)
            next(csvReader)
            
            for row in csvReader:
                if row[0] == username:
                    checkingBal = float(row[2])
                    savingsbal = float(row[3])
                    totalBal = checkingBal + savingsbal
                    
                    self.balanceLabel.setText(f"Balance: ${totalBal:.2f}")
                    self.nameBalanceLabel.setText(f"{username.upper()} -- ${checkingBal:.2f}")
                    self.savingsNameBalanceLabel.setText(f"{username.upper()} -- ${savingsbal:.2f}")
                    self.interestLabel.setText(f'Deposits Until Interest {row[4]}')
                    self.showChart()

    def depositFunc(self) -> None:
        """
        Handles the logic of the deposit button
        Ensures the input is valid monetary value to prevent runtime errors. 
        Dictates the interest on the money in the savings account based on data from the loginInfo.csv
        Allows money to be put in either account 
        """
        username, password = self.getLoginInfo()
        amount = self.depositAmt.text().strip().strip('$') #Dont forget validation for this 

        amount = self.validateAmount(amount)
        if amount is None:
            return
        
        rows = []
        with open(self.LOGINPATH, 'r') as file: 
            csvReader = csv.reader(file)
            header = next(csvReader)
            rows.append(header)
            
            for row in csvReader:
                if row[0] == username:
                    if self.depositCombo.currentIndex() == 0: #checking
                        row[2] = float(row[2]) + amount
                        row[4] = int(row[4]) -1
                    elif self.depositCombo.currentIndex() == 1: #savings
                        row[3] = float(row[3]) + amount
                        row[4] = int(row[4]) -1
                        
                    totalBalance = float(row[2]) + float(row[3])
                    self.interestLabel.setText(f'Deposits Until Interst: {int(row[4])}') 
                if row[4] == 0: 
                    row[3] = float(row[3])*1.05 #This is the interest rate. Intentionally only applied to savings
                    row[4] = 5
                rows.append(row)
                
                
        with open(self.LOGINPATH, 'w', newline='') as file:
            csvWriter = csv.writer(file)
            csvWriter.writerows(rows)
    
        self.errorLabel.setText("")
        self.logBalance(username, totalBalance)
        self.syncMainPage()
        self.depositAmt.setText("")
        self.errorLabel.setText("")
        self.showChart()
        
        
    def withdrawFunc(self) -> None:
        """
        Takes money out of either account. 
        Ensures sufficient funds are in account before allowing withdrawl as well as making sure value is monetary value.
        Updates chart
        """
        username, password = self.getLoginInfo()
        amount = self.withdrawAmt.text().strip().strip('$') #Dont forget validation for this 
        
        amount = self.validateAmount(amount)
        if amount is None:
            return
        
        rows = []
        with open(self.LOGINPATH, 'r') as file: 
            csvReader = csv.reader(file)
            header = next(csvReader)
            rows.append(header)
            try: 
                for row in csvReader:
                    if row[0] == username:
                        if self.withdrawCombo.currentIndex() == 0: #checking
                            if float(row[2]) < amount:
                                raise ValueError
                            row[2] = float(row[2]) - amount
                        elif self.withdrawCombo.currentIndex() == 1: #savings
                            if float(row[3]) < amount:
                                raise ValueError
                            row[3] = float(row[3]) - amount
                        totalBalance = float(row[2]) + float(row[3])
                    rows.append(row)
            except ValueError:
                self.errorLabel.setText("Insufficient Funds")
                return
                
        with open(self.LOGINPATH, 'w', newline='') as file:
            csvWriter = csv.writer(file)
            csvWriter.writerows(rows)

        self.errorLabel.setText("")    
        self.logBalance(username, totalBalance)
        self.syncMainPage()
        self.withdrawAmt.setText("") 
        self.errorLabel.setText("") 
        self.showChart()       
    
    def transferFunc(self) -> None:
        """
        Allows funds to be moved from one account to the other
        Validation for both input and minimum values.
        """
        username, password = self.getLoginInfo()
        amount = self.transferAmt.text().strip().strip('$') #Dont forget validation for this 
        
        amount = self.validateAmount(amount)
        if amount is None:
            return
        
        rows = []
        with open(self.LOGINPATH, 'r') as file: 
            csvReader = csv.reader(file)
            header = next(csvReader)
            rows.append(header)
            
            try:
                for row in csvReader:
                    if row[0] == username:
                        if self.transferCombo.currentIndex() == 0: #From checking
                            if float(row[2]) < amount:
                                raise ValueError
                            row[2] = float(row[2]) - amount #Need hella validation
                            row[3] = float(row[3]) + amount
                        elif self.transferCombo.currentIndex() == 1: #from savings
                            if float(row[3]) < amount:
                                raise ValueError
                            row[3] = float(row[3]) - amount
                            row[2] = float(row[2]) + amount
                        
                        totalBalance = float(row[2]) + float(row[3])
                    rows.append(row)
            except ValueError: 
                self.errorLabel.setText("Insufficient Funds")
                return
            
        with open(self.LOGINPATH, 'w', newline='') as file:
            csvWriter = csv.writer(file)
            csvWriter.writerows(rows)
    
        self.errorLabel.setText("")   
        self.logBalance(username, totalBalance)
        self.syncMainPage()
        self.transferAmt.setText("") 
        self.showChart()
    
    def logBalance(self, username, totalBalance) -> None:
        """
        Called when balances are changed to be added to the history.csv
        Simply appends it to a big list to be filtered through later
        """
        with open(self.HISTORYPATH, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, datetime.now().isoformat(), totalBalance])
    
    def showChart(self) -> None:
        """
        Uses matplotlib to create a chart based on balance history
        If the chart is not there it initializes it and if it is there from previous or needs updating it deletes the chart before putting it back
        If there is not a minimum number of deposits chart does not display
        """
        username, password = self.getLoginInfo()
        times = []
        balances = []
        
        if os.path.exists(self.HISTORYPATH):
            with open(self.HISTORYPATH, 'r') as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    if row and row[0] == username:
                        try:
                            times.append(datetime.fromisoformat(row[1]))
                            balances.append(float(row[2]))
                        except (ValueError, IndexError):
                            continue # Skip broken rows

        # Clear the Axes
        self.ax.clear()
        
        if len(balances) >= 2:
            self.ax.step(times, balances, where='post', linewidth=2, color= '#0E0B80') #This is a mix of the matplotlib documentation and google
            self.ax.set_xlabel('Date/Time', fontsize=8)
            self.ax.set_ylabel('Balance ($)', fontsize=8)
            self.ax.set_title('Balance History', fontsize=10)
            self.ax.grid(True, alpha=0.3)
            self.ax.tick_params(labelsize=7)
            self.fig.autofmt_xdate(rotation=45)
            self.fig.tight_layout()
        else:
            self.ax.text(0.5, 0.5, "Not enough data to display chart", transform=self.ax.transAxes, ha='center')

        # Redraw the canvas
        self.canvas.draw()
        
    def signOut(self) -> None:
        """
        Signs out of the mainpage and sets the text in the logins boxes to clear
        Changes the stacked widgets. 
        """
        self.stackedWidget.setCurrentIndex(0)
        self.usernameEntry.setText("")
        self.passwordEntry.setText("")
        self.signInMessage.setText("")