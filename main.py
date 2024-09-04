from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
from language import langDict
import sys
import requests
import webbrowser
import subprocess
import os
import socket


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(450, 300)
        self.setWindowTitle("Dashboard")
        self.setWindowIcon(QIcon("images/icon.png"))


        styleButton = "background-color: white; border-radius: 3px"
        palette = QPalette()
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        
        
        # LANGUAGE
        
        self.lang = langDict
        self.syslang = QLocale.system().name()
        if self.syslang not in self.lang:
            self.syslang = "en_US"
        

        # BACK PANEL
        
        self.panel = QWidget(self)
        heightPanel = int(self.geometry().height())
        self.panel.setGeometry(0, 0, 145, heightPanel)
        self.panel.setStyleSheet("background-color: #000099;")
        self.resize(450, 300)
        self.resizeEvent = self.panelHeight

        self.homePageButton = QPushButton(self.lang[self.syslang]["Home"], self)
        self.homePageButton.setIcon(QIcon('images/home.png'))
        self.homePageButton.setGeometry(0, 0, 145, 25)
        self.homePageButton.clicked.connect(self.homePage)
        self.homePageButton.setPalette(palette)

        self.updatePageButton = QPushButton(self.lang[self.syslang]["Updating"], self)
        self.updatePageButton.setIcon(QIcon('images/update.png'))
        self.updatePageButton.setGeometry(0, 25, 145, 25)
        self.updatePageButton.clicked.connect(self.updatePage)
        self.updatePageButton.setPalette(palette)

        self.connectPageButton = QPushButton(self.lang[self.syslang]["Remote connection"], self)
        self.connectPageButton.setIcon(QIcon('images/connect.png'))
        self.connectPageButton.setGeometry(0, 50, 145, 25)
        self.connectPageButton.clicked.connect(self.connectPage)
        self.connectPageButton.setPalette(palette)

        self.aboutPageButton = QPushButton(self.lang[self.syslang]["About"], self)
        self.aboutPageButton.setIcon(QIcon('images/about.png'))
        self.aboutPageButton.setGeometry(0, 75, 145, 25)
        self.aboutPageButton.clicked.connect(self.aboutPage)
        self.aboutPageButton.setPalette(palette)
        
        
        # MAIN ELEMENTS OF THE PAGES
        
        self.mainLabel = QLabel(self.lang[self.syslang]["Welcome to Dashboard"], self)
        self.mainLabel.setGeometry(150, 0, 300, 50)
        self.mainLabel.setStyleSheet("font-size: 20px")
        
        
        # "HOME" PAGE
        
        self.wikiLinkButton = QPushButton(self.lang[self.syslang]["How to use \nDashboard?"], self)
        self.wikiLinkButton.setStyleSheet("text-align: left; background-color: #000099; color: white; padding: 10px; border-style: none;")
        self.wikiLinkButton.setGeometry(150, 50, 145, 145)
        self.wikiLinkButton.clicked.connect(self.wikiLink)
        
        self.newsLinkButton = QPushButton(self.lang[self.syslang]["What new \nin SerOS?"], self)
        self.newsLinkButton.setStyleSheet("text-align: left; background-color: #000099; color: white; padding: 10px; border-style: none;")
        self.newsLinkButton.setGeometry(300, 50, 145, 145)
        self.newsLinkButton.clicked.connect(self.newsLink)
        
        
        # "UPDATING" PAGE
        
        self.updateStatus = QPixmap('images/checking.png')
        self.updateStatusNormal = QPixmap('images/update-normal-status.png')
        self.updateStatusMedium = QPixmap('images/update-recomend.png')
        self.updateStatusFail = QPixmap('images/update-failed.png')
        self.updateStatusLogo = QLabel(self)
        self.updateStatusLogo.setPixmap(self.updateStatus)
        self.updateStatusLogo.setGeometry(150, 50, 32, 32)
        self.updateStatusLogo.hide()
        
        self.updateStatusLabel = QLabel(self.lang[self.syslang]["Checking ..."], self)
        self.updateStatusLabel.setGeometry(185, 50, 300, 32)
        self.updateStatusLabel.hide()
        
        self.updatePackagesButton = QPushButton(self.lang[self.syslang]["Update packages"], self)
        self.updatePackagesButton.setGeometry(150, 85, 250, 25)
        self.updatePackagesButton.setIcon(QIcon('images/update.png'))
        self.updatePackagesButton.hide()
        self.updatePackagesButton.setStyleSheet(styleButton)
        self.updatePackagesButton.clicked.connect(self.updatePackage)
        
        self.downloadsUpdatesButton = QPushButton(self.lang[self.syslang]["Downloads updates"], self)
        self.downloadsUpdatesButton.setGeometry(150, 115, 250, 25)
        self.downloadsUpdatesButton.setIcon(QIcon('images/download.png'))
        self.downloadsUpdatesButton.hide()
        self.downloadsUpdatesButton.setStyleSheet(styleButton)
        self.downloadsUpdatesButton.clicked.connect(self.downloadsUpdates)
        
        self.toDoAllButtonUpdate = QPushButton(self.lang[self.syslang]["To do all"], self)
        self.toDoAllButtonUpdate.setGeometry(150, 145, 250, 25)
        self.toDoAllButtonUpdate.setIcon(QIcon('images/to-do-all.png'))
        self.toDoAllButtonUpdate.hide()
        self.toDoAllButtonUpdate.setStyleSheet(styleButton)
        self.toDoAllButtonUpdate.clicked.connect(self.toDoAllUpdate)
        
        self.errorLabel = QLabel(self)
        self.errorLabel.setGeometry(150, 210, 300, 100)
        self.errorLabel.hide()
        
        
        # "REMOTE CONNECTION" PAGE
        
        self.ippc = socket.gethostbyname(socket.gethostname())
        
        self.yourIPLabel = QLabel(self.lang[self.syslang]["Your IP"] + ": " + str(self.ippc), self)
        self.yourIPLabel.setGeometry(150, 50, 200, 25)
        self.yourIPLabel.hide()
        
        self.userLineEdit = QLineEdit(self)
        self.userLineEdit.setPlaceholderText(self.lang[self.syslang]["User of PC"])
        self.userLineEdit.setGeometry(150, 75, 200, 30)
        self.userLineEdit.hide()
        
        self.ipLineEdit = QLineEdit(self)
        self.ipLineEdit.setPlaceholderText(self.lang[self.syslang]["IP of PC"])
        self.ipLineEdit.setGeometry(150, 105, 200, 30)
        self.ipLineEdit.hide()
        
        self.openProgramLineEdit = QLineEdit(self)
        self.openProgramLineEdit.setPlaceholderText(self.lang[self.syslang]["Open a program in PC"])
        self.openProgramLineEdit.setGeometry(150, 145, 200, 30)
        self.openProgramLineEdit.hide()
        
        self.connectButton = QPushButton(self.lang[self.syslang]["Connect"], self)
        self.connectButton.setIcon(QIcon('images/connect.png'))
        self.connectButton.setStyleSheet(styleButton)
        self.connectButton.setGeometry(150, 190, 200, 30)
        self.connectButton.clicked.connect(self.connectSSH)
        self.connectButton.hide()
        
        
        # "ABOUT" PAGE
        
        self.aboutLabel = QLabel(self.lang[self.syslang]["Dashboard\nAuthor: OrgInfoTech @2024\nVersion: 1.0.1 (07/01/2024)"], self)
        self.aboutLabel.setGeometry(150, 50, 250, 60)
        self.aboutLabel.hide()
    
    def panelHeight(self, event):
        self.panel.setGeometry(0, 0, 145, self.height())   
    
    def hideAll(self):
        self.updateStatusLogo.hide()
        self.updateStatusLabel.hide()
        self.updatePackagesButton.hide()
        self.downloadsUpdatesButton.hide()
        self.toDoAllButtonUpdate.hide()
        self.errorLabel.hide()
        self.aboutLabel.hide()
        self.yourIPLabel.hide()
        self.userLineEdit.hide()
        self.ipLineEdit.hide()
        self.connectButton.hide()
        self.wikiLinkButton.hide()
        self.newsLinkButton.hide()
        self.openProgramLineEdit.hide()
    
    def homePage(self):
        self.hideAll()
        
        # SHOW
        self.wikiLinkButton.show()
        self.newsLinkButton.show()

        # SET TEXT
        self.mainLabel.setText(self.lang[self.syslang]["Welcome to Dashboard"])
    
    def updatePage(self):
        self.hideAll()
        
        # SHOW
        self.updateStatusLogo.show()
        self.updateStatusLabel.show()
        self.updatePackagesButton.show()
        self.downloadsUpdatesButton.show()
        self.toDoAllButtonUpdate.show()
        self.errorLabel.show()

        # SET TEXT
        
        self.mainLabel.setText(self.lang[self.syslang]["Updating"])
        
        # FUNCTIONS
        
        self.checkingOfUpdates()
    
    def connectPage(self):
        self.hideAll()
        
        # SHOW
        self.yourIPLabel.show()
        self.userLineEdit.show()
        self.ipLineEdit.show()
        self.connectButton.show()
        self.openProgramLineEdit.show()

        # SET TEXT
        self.mainLabel.setText(self.lang[self.syslang]["Remote connection"])
    
    def aboutPage(self):
        self.hideAll()

        # SHOW
        self.aboutLabel.show()

        # SET TEXT
        self.mainLabel.setText(self.lang[self.syslang]["About"])
        
    def updatePackage(self):
        try:
            self.updatePackagesButton.isEnabled = False
            self.downloadsUpdatesButton.isEnabled = False
            self.toDoAllButtonUpdate.isEnabled = False

            command = f"sudo apt update && sudo apt upgrade -y && sudo apt-get update && sudo apt-get upgrade -y"
            try:
                subprocess.call(['xterm', '-e', command])
            except:
                print("Error")

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            self.updatePackagesButton.isEnabled = True
            self.downloadsUpdatesButton.isEnabled = True
            self.toDoAllButtonUpdate.isEnabled = True

        
    def downloadsUpdates(self):
        url = "https://orginfotech2024.github.io/Dashboard/update/updater.sh"
        file_path = "updater.sh"

        command = f"sudo wget {url} && sh updater.sh && sudo rm updater.sh"
        try:
            subprocess.call(['xterm', '-e', command])
        except:
            print("Error")
        
    def toDoAllUpdate(self):
        self.updatePackage()
        self.downloadsUpdates()
    
    def checkingOfUpdates(self):
        try:
            linkForUpdate = ""
            with open('datas/linkForUpdate.txt', 'r') as file:
                linkForUpdate = file.read()
            updateNow = requests.get(linkForUpdate)
            updateNowText = updateNow.json()
            
            updatePC = ""
            with open('datas/updateNow.txt', 'r') as file:
                updatePC = file.read()
                
            
            if updateNowText["version"] == updatePC:
                self.updateStatusLogo.setPixmap(self.updateStatusNormal)
                self.updateStatusLabel.setText(self.lang[self.syslang]["Your PC isn't needing to update now"])
            else:
                self.updateStatusLogo.setPixmap(self.updateStatusMedium)
                self.updateStatusLabel.setText(self.lang[self.syslang]["You should to install updates for your PC"])
            
        except:
            self.updateStatusLogo.setPixmap(self.updateStatusFail)
            self.updateStatusLabel.setText(self.lang[self.syslang]["Finding of updates was failed"])
    
    def connectSSH(self):
        program = self.openProgramLineEdit.text()
        user = self.userLineEdit.text()
        ip = self.ipLineEdit.text()
        if program == None:
            command = f"sudo ssh -X {user}@{ip}"
            subprocess.call(['xterm', '-e', command])
        else:
            command = f"sudo ssh -X {user}@{ip} {program}"
            subprocess.call(['xterm', '-e', command])
    
    def wikiLink(self):
        with open('datas/wikiLink.txt', 'r') as file:
            linkForUpdate = file.read()
            webbrowser.open(linkForUpdate)
    
    def newsLink(self):
        with open('datas/newsLink.txt', 'r') as file:
            linkForUpdate = file.read()
            webbrowser.open(linkForUpdate)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
