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
import json
import netifaces
import socket


class MountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.mainWindow = parent
        self.lang = parent.lang
        self.syslang = parent.syslang

        self.setWindowTitle(self.lang[self.syslang]["Add connection"])
        self.setMinimumSize(400, 200)

        layout = QVBoxLayout(self)

        self.ipLine = QLineEdit()
        self.ipLine.setPlaceholderText(self.lang[self.syslang]["IP Address"])

        self.sharedLine = QLineEdit()
        self.sharedLine.setPlaceholderText(self.lang[self.syslang]["Shared Folder"])

        localLayout = QHBoxLayout()

        self.localLine = QLineEdit()
        self.localLine.setPlaceholderText(self.lang[self.syslang]["Local Folder"])

        self.browseBtn = QPushButton("Browse")
        self.browseBtn.clicked.connect(self.selectLocalFolder)

        localLayout.addWidget(self.localLine)
        localLayout.addWidget(self.browseBtn)

        layout.addWidget(self.ipLine)
        layout.addWidget(self.sharedLine)
        layout.addLayout(localLayout)

        btnLayout = QHBoxLayout()

        self.mountBtn = QPushButton(self.lang[self.syslang]["Mount folder"])
        self.cancelBtn = QPushButton(self.lang[self.syslang]["Cancel"])

        btnLayout.addWidget(self.mountBtn)
        btnLayout.addWidget(self.cancelBtn)

        layout.addLayout(btnLayout)

        self.mountBtn.clicked.connect(self.mountFolder)
        self.cancelBtn.clicked.connect(self.reject)

    def selectLocalFolder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            self.lang[self.syslang]["Local Folder"]
        )

        if folder:
            self.localLine.setText(folder)

    def mountFolder(self):
        ip = self.ipLine.text().strip()
        shared = self.sharedLine.text().strip()
        local = self.localLine.text().strip()

        if not ip or not shared or not local:
            QMessageBox.warning(
                self,
                self.lang[self.syslang]["Error"],
                self.lang[self.syslang]["All fields must be filled"]
            )
            return

        ping = subprocess.run(
            ["ping", "-c", "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if ping.returncode != 0:
            QMessageBox.critical(
                self,
                self.lang[self.syslang]["Error"],
                "Host is unreachable"
            )
            return

        try:
            os.makedirs(local, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(
                self,
                self.lang[self.syslang]["Error"],
                str(e)
            )
            return

        command = f"mount {ip}:{shared} {local}"

        result = subprocess.run(
            ["pkexec", "bash", "-c", command],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            QMessageBox.critical(
                self,
                self.lang[self.syslang]["Error"],
                result.stderr if result.stderr else self.lang[self.syslang]["Mount failed"]
            )
            return

        row = self.mainWindow.connectedTable.rowCount()
        self.mainWindow.connectedTable.insertRow(row)

        self.mainWindow.connectedTable.setItem(
            row, 0, QTableWidgetItem(local)
        )
        self.mainWindow.connectedTable.setItem(
            row, 1, QTableWidgetItem(ip)
        )
        self.mainWindow.connectedTable.setItem(
            row, 2, QTableWidgetItem(shared)
        )

        self.accept()

class AddIPDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.mainWindow = parent

        self.setWindowTitle("Add IP Address")
        self.setMinimumSize(500, 300)

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "PC Name",
            "User",
            "IP Address"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.SelectedClicked |
            QAbstractItemView.EditKeyPressed
        )

        self.table.cellDoubleClicked.connect(self.insertToMainWindow)

        self.layout.addWidget(self.table)

        btnLayout = QHBoxLayout()

        self.addRowBtn = QPushButton("Add")
        self.removeBtn = QPushButton("Remove")

        btnLayout.addWidget(self.addRowBtn)
        btnLayout.addWidget(self.removeBtn)

        self.layout.addLayout(btnLayout)

        self.addRowBtn.clicked.connect(self.addRow)
        self.removeBtn.clicked.connect(self.removeRow)

        self.dataPath = os.path.expanduser("~/.programdates/Dashboard/ippc.json")
        os.makedirs(os.path.dirname(self.dataPath), exist_ok=True)

        self.loadData()

    def addRow(self):
        self.table.insertRow(self.table.rowCount())

    def removeRow(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def loadData(self):
        if not os.path.exists(self.dataPath):
            return

        with open(self.dataPath, "r") as f:
            data = json.load(f)

        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(item["user"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["ip"]))

    def saveData(self):
        data = []
        for row in range(self.table.rowCount()):
            nameItem = self.table.item(row, 0)
            userItem = self.table.item(row, 1)
            ipItem = self.table.item(row, 2)

            if not (nameItem and userItem and ipItem):
                continue

            data.append({
                "name": nameItem.text(),
                "user": userItem.text(),
                "ip": ipItem.text()
            })

        with open(self.dataPath, "w") as f:
            json.dump(data, f, indent=4)

    def closeEvent(self, event):
        self.saveData()
        event.accept()

    def insertToMainWindow(self, row, column):
        if not self.mainWindow:
            return

        userItem = self.table.item(row, 1)
        ipItem = self.table.item(row, 2)

        if userItem and ipItem:
            self.mainWindow.userLineEdit.setText(userItem.text())
            self.mainWindow.ipLineEdit.setText(ipItem.text())

        self.close()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(450, 300)
        self.setWindowTitle("Dashboard")
        self.setWindowIcon(QIcon("images/icon.png"))


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
        self.panel.setStyleSheet("background-color: #10A186;")
        self.resize(450, 300)
        self.resizeEvent = self.widgetSize

        self.homePageButton = QPushButton(self.lang[self.syslang]["Home"], self)
        self.homePageButton.setIcon(QIcon('images/home.png'))
        self.homePageButton.setGeometry(0, 0, 145, 25)
        self.homePageButton.clicked.connect(self.homePage)

        self.updatePageButton = QPushButton(self.lang[self.syslang]["Updating"], self)
        self.updatePageButton.setIcon(QIcon('images/update.png'))
        self.updatePageButton.setGeometry(0, 25, 145, 25)
        self.updatePageButton.clicked.connect(self.updatePage)

        self.connectPageButton = QPushButton(self.lang[self.syslang]["Remote connection"], self)
        self.connectPageButton.setIcon(QIcon('images/connect.png'))
        self.connectPageButton.setGeometry(0, 50, 145, 25)
        self.connectPageButton.clicked.connect(self.connectPage)

        self.servicesPageButton = QPushButton(self.lang[self.syslang]["Services"], self)
        self.servicesPageButton.setIcon(QIcon('images/conf.png'))
        self.servicesPageButton.setGeometry(0, 75, 145, 25)
        self.servicesPageButton.clicked.connect(self.servicesPage)

        self.networkPageButton = QPushButton(self.lang[self.syslang]["Network Folders"], self)
        self.networkPageButton.setIcon(QIcon('images/network.png'))
        self.networkPageButton.setGeometry(0, 100, 145, 25)
        self.networkPageButton.clicked.connect(self.networkPage)

        self.easyTransferPageButton = QPushButton("Easy Transfer", self)
        self.easyTransferPageButton.setIcon(QIcon('images/easytransfer.png'))
        self.easyTransferPageButton.setGeometry(0, 125, 145, 25)
        self.easyTransferPageButton.clicked.connect(self.easyTransferPage)

        self.rsyncPageButton = QPushButton("Rsync", self)
        self.rsyncPageButton.setIcon(QIcon('images/senddatas.png'))
        self.rsyncPageButton.setGeometry(0, 150, 145, 25)
        self.rsyncPageButton.clicked.connect(self.rsyncPage)

        self.aboutPageButton = QPushButton(self.lang[self.syslang]["About"], self)
        self.aboutPageButton.setIcon(QIcon('images/about.png'))
        self.aboutPageButton.setGeometry(0, 175, 145, 25)
        self.aboutPageButton.clicked.connect(self.aboutPage)
        
        
        # MAIN ELEMENTS OF THE PAGES
        
        self.mainLabel = QLabel(self.lang[self.syslang]["Welcome to Dashboard"], self)
        self.mainLabel.setGeometry(150, 0, 300, 50)
        self.mainLabel.setStyleSheet("font-size: 20px")
        
        
        # "HOME" PAGE
        
        self.wikiLinkButton = QPushButton(self.lang[self.syslang]["How to use \nDashboard?"], self)
        self.wikiLinkButton.setStyleSheet("text-align: left; background-color: #006050; color: white; padding: 10px; border-style: none;")
        self.wikiLinkButton.setGeometry(150, 50, 145, 145)
        self.wikiLinkButton.clicked.connect(self.wikiLink)
        
        self.newsLinkButton = QPushButton(self.lang[self.syslang]["What new \nin SerOS?"], self)
        self.newsLinkButton.setStyleSheet("text-align: left; background-color: #006050; color: white; padding: 10px; border-style: none;")
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
        self.updatePackagesButton.clicked.connect(self.updatePackage)
        
        self.downloadsUpdatesButton = QPushButton(self.lang[self.syslang]["Downloads updates"], self)
        self.downloadsUpdatesButton.setGeometry(150, 115, 250, 25)
        self.downloadsUpdatesButton.setIcon(QIcon('images/download.png'))
        self.downloadsUpdatesButton.hide()
        self.downloadsUpdatesButton.clicked.connect(self.downloadsUpdates)
        
        self.toDoAllButtonUpdate = QPushButton(self.lang[self.syslang]["To do all"], self)
        self.toDoAllButtonUpdate.setGeometry(150, 145, 250, 25)
        self.toDoAllButtonUpdate.setIcon(QIcon('images/to-do-all.png'))
        self.toDoAllButtonUpdate.hide()
        self.toDoAllButtonUpdate.clicked.connect(self.toDoAllUpdate)
        
        self.errorLabel = QLabel(self)
        self.errorLabel.setGeometry(150, 210, 300, 100)
        self.errorLabel.hide()
        
        
        # "REMOTE CONNECTION" PAGE
        
        self.yourIPLabel = QLabel(self.lang[self.syslang]["Your IP"] + " (virbr0): " + self.get_interface_ip('virbr0'), self)
        self.yourIPLabel.setGeometry(150, 50, 200, 25)
        self.yourIPLabel.hide()
        
        self.userLineEdit = QLineEdit(self)
        self.userLineEdit.setPlaceholderText(self.lang[self.syslang]["User of PC"])
        self.userLineEdit.setGeometry(150, 75, 200, 25)
        self.userLineEdit.hide()
        
        self.ipLineEdit = QLineEdit(self)
        self.ipLineEdit.setPlaceholderText(self.lang[self.syslang]["IP of PC"])
        self.ipLineEdit.setGeometry(150, 100, 200, 25)
        self.ipLineEdit.hide()
        
        self.openProgramLineEdit = QLineEdit(self)
        self.openProgramLineEdit.setPlaceholderText(self.lang[self.syslang]["Open a program in PC"])
        self.openProgramLineEdit.setGeometry(150, 135, 200, 25)
        self.openProgramLineEdit.hide()
        
        self.connectButton = QPushButton(self.lang[self.syslang]["Connect"], self)
        self.connectButton.setIcon(QIcon('images/connect.png'))
        self.connectButton.setGeometry(150, 170, 200, 25)
        self.connectButton.clicked.connect(self.connectSSH)
        self.connectButton.hide()

        self.IPButton = QPushButton(self.lang[self.syslang]["IP Addresses"], self)
        self.IPButton.setIcon(QIcon('images/bookadress.png'))
        self.IPButton.setGeometry(150, 200, 200, 25)
        self.IPButton.clicked.connect(self.openAddIPDialog)
        self.IPButton.hide()
        

        # "SERVICES" PAGE

        self.servicesTable = QTableWidget(self)
        self.servicesTable.setGeometry(150, 50, 400, 220)
        self.servicesTable.setColumnCount(3)
        self.servicesTable.setHorizontalHeaderLabels([
            "Name",
            "Autostart status",
            "Current status"
        ])
        self.servicesTable.horizontalHeader().setStretchLastSection(True)
        self.servicesTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.servicesTable.hide()

        # NETWORK PAGE

        self.networkTabs = QTabWidget(self)
        self.networkTabs.setGeometry(150, 50, 500, 300)
        self.networkTabs.hide()

        self.connectedTab = QWidget()
        self.connectedLayout = QVBoxLayout(self.connectedTab)

        self.connectedTable = QTableWidget()
        self.connectedTable.setColumnCount(3)
        self.connectedTable.setHorizontalHeaderLabels([
            "Folder with shared files",
            "IP",
            "Shared Folder"
        ])
        self.connectedLayout.addWidget(self.connectedTable)

        self.mountBtn = QPushButton("Mount")
        self.unmountBtn = QPushButton("Unmount")

        btnLayout1 = QHBoxLayout()
        btnLayout1.addWidget(self.mountBtn)
        btnLayout1.addWidget(self.unmountBtn)

        self.connectedLayout.addLayout(btnLayout1)

        self.mountBtn.clicked.connect(self.openMountDialog)
        self.unmountBtn.clicked.connect(self.unmountFolder)

        self.createdTab = QWidget()
        self.createdLayout = QVBoxLayout(self.createdTab)

        self.ipInfoLabel = QLabel(self)
        self.createdLayout.addWidget(self.ipInfoLabel)

        self.createdTable = QTableWidget()
        self.createdTable.setColumnCount(2)
        self.createdTable.setHorizontalHeaderLabels([
            "Shared Folder",
            "Read-only"
        ])
        self.createdLayout.addWidget(self.createdTable)

        self.addShareBtn = QPushButton("Add")
        self.deleteShareBtn = QPushButton("Delete")

        btnLayout2 = QHBoxLayout()
        btnLayout2.addWidget(self.addShareBtn)
        btnLayout2.addWidget(self.deleteShareBtn)

        self.createdLayout.addLayout(btnLayout2)

        self.addShareBtn.clicked.connect(self.addShareDialog)
        self.deleteShareBtn.clicked.connect(self.deleteShare)

        self.networkTabs.addTab(self.connectedTab, "Connected Network Folders")
        self.networkTabs.addTab(self.createdTab, "Created Network Folders")
        
        
        # "EASY TRANSFER" PAGE
        
        self.yourIPforEasyTransferLabel = QLabel(self.lang[self.syslang]["Your IP"] + ": " + self.getMainIPforEasyTranfer(), self)
        self.yourIPforEasyTransferLabel.setGeometry(150, 50, 200, 25)
        self.yourIPforEasyTransferLabel.hide()
        
        self.userLineEasyTransferEdit = QLineEdit(self)
        self.userLineEasyTransferEdit.setPlaceholderText(self.lang[self.syslang]["User of PC"])
        self.userLineEasyTransferEdit.setGeometry(150, 75, 200, 25)
        self.userLineEasyTransferEdit.hide()
        
        self.ipLineEasyTransferEdit = QLineEdit(self)
        self.ipLineEasyTransferEdit.setPlaceholderText(self.lang[self.syslang]["IP of PC"])
        self.ipLineEasyTransferEdit.setGeometry(150, 100, 200, 25)
        self.ipLineEasyTransferEdit.hide()

        self.transferDatasEasyTransferEdit = QPushButton(self.lang[self.syslang]["Transfer Datas"], self)
        self.transferDatasEasyTransferEdit.setIcon(QIcon('images/easytransfer.png'))
        self.transferDatasEasyTransferEdit.setGeometry(150, 125, 200, 25)
        self.transferDatasEasyTransferEdit.clicked.connect(self.easyTransfer)
        self.transferDatasEasyTransferEdit.hide()
        
        self.infoforEasyTransferLabel = QLabel(self.lang[self.syslang]["For transfer datas you must to write user and IP of PC, which must get datas from your current PC."], self)
        self.infoforEasyTransferLabel.setGeometry(150, 160, 400, 100)
        self.infoforEasyTransferLabel.hide()
        
        
        # "RSYNC" PAGE
        
        self.yourIPforRsyncLabel = QLabel(self.lang[self.syslang]["Your IP"] + ": " + self.getMainIPforEasyTranfer(), self)
        self.yourIPforRsyncLabel.setGeometry(150, 50, 270, 25)
        self.yourIPforRsyncLabel.hide()
        
        self.dataLineRsyncEdit = QLineEdit(self)
        self.dataLineRsyncEdit.setPlaceholderText(self.lang[self.syslang]["Direction of your file or folder"])
        self.dataLineRsyncEdit.setGeometry(150, 75, 270, 25)
        self.dataLineRsyncEdit.hide()
        
        self.userLineRsyncEdit = QLineEdit(self)
        self.userLineRsyncEdit.setPlaceholderText(self.lang[self.syslang]["User of PC  for sending"])
        self.userLineRsyncEdit.setGeometry(150, 100, 270, 25)
        self.userLineRsyncEdit.hide()
        
        self.ipLineRsyncEdit = QLineEdit(self)
        self.ipLineRsyncEdit.setPlaceholderText(self.lang[self.syslang]["IP of PC for sending"])
        self.ipLineRsyncEdit.setGeometry(150, 125, 270, 25)
        self.ipLineRsyncEdit.hide()
        
        self.directionLineRsyncEdit = QLineEdit(self)
        self.directionLineRsyncEdit.setPlaceholderText(self.lang[self.syslang]["Direction of recipient PC for saving datas"])
        self.directionLineRsyncEdit.setGeometry(150, 150, 270, 25)
        self.directionLineRsyncEdit.hide()

        self.transferDatasRsyncEdit = QPushButton(self.lang[self.syslang]["Send Datas"], self)
        self.transferDatasRsyncEdit.setIcon(QIcon('images/senddatas.png'))
        self.transferDatasRsyncEdit.setGeometry(150, 175, 270, 25)
        self.transferDatasRsyncEdit.clicked.connect(self.rsyncavz)
        self.transferDatasRsyncEdit.hide()

        
        # "ABOUT" PAGE
        
        self.aboutLabel = QLabel(self.lang[self.syslang]["Dashboard\nAuthor: OrgInfoTech @2024\nVersion: 1.0.1 (07/01/2024)"], self)
        self.aboutLabel.setGeometry(150, 50, 250, 60)
        self.aboutLabel.hide()

    def networkPage(self):
        self.hideAll()
        self.networkTabs.show()
        self.mainLabel.setText(self.lang[self.syslang]["Network Folders"])

        if not self.checkNFS():
            QMessageBox.critical(self, "Error", "NFS is not working on this system!")
            return

        self.loadCreatedShares()
        self.ipInfoLabel.setText("Your IP: " + self.getMainIP())

    def checkNFS(self):
        try:
            rpc_check = subprocess.check_output(
                "rpcinfo -p | grep nfs",
                shell=True
            )
            fs_check = subprocess.check_output(
                "cat /proc/filesystems | grep nfs",
                shell=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def getMainIPforEasyTranfer(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "IP not found"

    def getMainIP(self):
        try:
            result = subprocess.check_output(
                "ip -4 addr show scope global | grep inet",
                shell=True,
                text=True
            )

            line = result.strip().split("\n")[0]
            ip = line.split()[1].split("/")[0]

            return ip

        except:
            return "IP not found"

    def openMountDialog(self):
        dialog = MountDialog(self)
        dialog.exec_()

    def unmountFolder(self):
        row = self.connectedTable.currentRow()
        if row < 0:
            return

        localFolder = self.connectedTable.item(row, 0).text()

        command = f"umount {localFolder}"

        result = subprocess.run(
            ["pkexec", "bash", "-c", command],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            QMessageBox.critical(
                self,
                self.lang[self.syslang]["Error"],
                result.stderr
            )
            return
        self.connectedTable.removeRow(row)

    def loadCreatedShares(self):
        try:
            with open("/etc/exports", "r") as f:
                lines = f.readlines()
            shares = [line for line in lines if not line.startswith("#") and line.strip()]
            self.createdTable.setRowCount(len(shares))
            for row, line in enumerate(shares):
                parts = line.split()
                folder = parts[0]
                if "ro" in line:
                    readonly = "True"
                else:
                    readonly = "False"
                self.createdTable.setItem(row, 0, QTableWidgetItem(folder))
                self.createdTable.setItem(row, 1, QTableWidgetItem(readonly))
        except:
            pass

    def addShareDialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not folder:
            return

        readonlyBox = QMessageBox.question(
            self,
            "Read-only",
            "Make this folder read-only?",
            QMessageBox.Yes | QMessageBox.No
        )

        if readonlyBox == QMessageBox.Yes:
            option = "ro"
            readonlyValue = "True"
        else:
            option = "rw"
            readonlyValue = "False"

        export_line = f"{folder} *(sync,{option},no_subtree_check)\n"

        cmd = f"echo '{export_line}' >> /etc/exports && exportfs -ra && systemctl restart nfs-server"
        self.runSystemctl(cmd)

        self.loadCreatedShares()

    def deleteShare(self):
        row = self.createdTable.currentRow()
        if row < 0:
            return

        folder = self.createdTable.item(row, 0).text()

        cmd = f"sed -i '\\|^{folder}|d' /etc/exports && exportfs -ra && systemctl restart nfs-server"
        self.runSystemctl(cmd)

        self.loadCreatedShares()

    def getSystemdServices(self):
        result = subprocess.check_output(
            ["systemctl", "list-unit-files", "--type=service", "--no-pager"],
            text=True
        )

        services = []
        for line in result.splitlines():
            if ".service" in line:
                services.append(line.split()[0])

        return services
    
    def getAutostartStatus(self, service):
        try:
            result = subprocess.check_output(
                ["systemctl", "is-enabled", service],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            return result
        except subprocess.CalledProcessError:
            return "disabled"
        
    def getServiceStatus(self, service):
        try:
            result = subprocess.check_output(
                ["systemctl", "is-active", service],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            return result
        except subprocess.CalledProcessError:
            return "inactive"

    def loadServices(self):
        services = self.getSystemdServices()
        self.servicesTable.setRowCount(len(services))

        for row, service in enumerate(services):
            nameItem = QTableWidgetItem(service)
            self.servicesTable.setItem(row, 0, nameItem)

            autostartBox = QComboBox()
            autostartBox.blockSignals(True)
            autostartBox.addItems(["Enabled", "Disabled"])

            autostart = self.getAutostartStatus(service)
            if autostart == "enabled":
                autostartBox.setCurrentText("Enabled")
            else:
                autostartBox.setCurrentText("Disabled")

            autostartBox.blockSignals(False)
            autostartBox.currentTextChanged.connect(
                lambda state, s=service: self.changeAutostart(s, state)
            )

            self.servicesTable.setCellWidget(row, 1, autostartBox)

            statusBox = QComboBox()
            statusBox.blockSignals(True)
            statusBox.addItems(["Start", "Stop", "Restart"])

            status = self.getServiceStatus(service)
            if status == "active":
                statusBox.setCurrentText("Stop")
            else:
                statusBox.setCurrentText("Start")

            statusBox.blockSignals(False)
            statusBox.currentTextChanged.connect(
                lambda action, s=service: self.changeServiceState(s, action)
            )

            self.servicesTable.setCellWidget(row, 2, statusBox)

    def runSystemctl(self, command):
        subprocess.call([
            "pkexec",
            "bash",
            "-c",
            command
        ])

    def changeServiceState(self, service, action):
        if action == "Start":
            cmd = f"systemctl start {service}"
        elif action == "Stop":
            cmd = f"systemctl stop {service}"
        elif action == "Restart":
            cmd = f"systemctl restart {service}"
        else:
            return

        self.runSystemctl(cmd)

    def changeAutostart(self, service, state):
        if state == "Enabled":
            cmd = f"systemctl enable {service}"
        elif state == "Disabled":
            cmd = f"systemctl disable {service}"
        else:
            return

        self.runSystemctl(cmd)

    def get_interface_ip(self, interface_name):
        try:
            addresses = netifaces.ifaddresses(interface_name)
            ip_address = addresses[netifaces.AF_INET][0]['addr']
            return ip_address
        except (ValueError, KeyError, IndexError):
            return "Interface not found"

    def widgetSize(self, event):
        self.panel.setGeometry(0, 0, 145, self.height())
        self.servicesTable.setGeometry(150, 50, self.width() - 155, self.height() - 55)
        self.networkTabs.setGeometry(150, 50, self.width() - 150, self.height() - 50)
    
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
        self.servicesTable.hide()
        self.IPButton.hide()
        self.yourIPforEasyTransferLabel.hide()
        self.userLineEasyTransferEdit.hide()
        self.ipLineEasyTransferEdit.hide()
        self.transferDatasEasyTransferEdit.hide()
        self.infoforEasyTransferLabel.hide()
        self.networkTabs.hide()
        self.yourIPforRsyncLabel.hide()
        self.dataLineRsyncEdit.hide()
        self.userLineRsyncEdit.hide()
        self.ipLineRsyncEdit.hide()
        self.transferDatasRsyncEdit.hide()
        self.directionLineRsyncEdit.hide()
    
    def homePage(self):
        self.hideAll()
        
        # SHOW
        self.wikiLinkButton.show()
        self.newsLinkButton.show()

        # SET TEXT
        self.mainLabel.setText(self.lang[self.syslang]["Welcome to Dashboard"])
    
    def easyTransferPage(self):
        self.hideAll()
        
        # SHOW
        self.yourIPforEasyTransferLabel.show()
        self.userLineEasyTransferEdit.show()
        self.ipLineEasyTransferEdit.show()
        self.transferDatasEasyTransferEdit.show()

        # SET TEXT
        self.mainLabel.setText("Easy Transfer")
    
    def rsyncPage(self):
        self.hideAll()
        
        # SHOW
        self.yourIPforRsyncLabel.show()
        self.dataLineRsyncEdit.show()
        self.userLineRsyncEdit.show()
        self.ipLineRsyncEdit.show()
        self.directionLineRsyncEdit.show()
        self.transferDatasRsyncEdit.show()

        # SET TEXT
        self.mainLabel.setText("Rsync")
    
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
        self.IPButton.show()

        # SET TEXT
        self.mainLabel.setText(self.lang[self.syslang]["Remote connection"])
    
    def servicesPage(self):
        self.hideAll()
        self.servicesTable.show()
        self.loadServices()
        header = self.servicesTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)


        # SET TEXT
        self.mainLabel.setText(self.lang[self.syslang]["Services"])

    def aboutPage(self):
        self.hideAll()

        # SHOW
        self.aboutLabel.show()

        # SET TEXT
        self.mainLabel.setText(self.lang[self.syslang]["About"])

    def rsyncavz(self):
        data = self.dataLineRsyncEdit.text()
        direction = self.directionLineRsyncEdit.text()
        user = self.userLineRsyncEdit.text()
        user = self.userLineRsyncEdit.text()
        ip = self.ipLineRsyncEdit.text()
        command = f"sudo rsync -avz {data} {user}@{ip}:{direction}"
        subprocess.call(['xterm', '-e', command])

    def easyTransfer(self):
        user = self.userLineEasyTransferEdit.text()
        ip = self.userLineEasyTransferEdit.text()
        directions = ["Documents", "Downloads", "Music", "Pictures", "Templates", "Videos", "Desktop", ".icons", ".local", ".config", ".programdates", ".themes", ".face"]
        commandList = []
        for direction in directions:
            command = f"sudo rsync -avz ~/{direction} {user}@{ip}:/home/{user}/"
            commandList.append(command)
        command = " && ".join(list)
        subprocess.call(['xterm', '-e', command])
    
    def openAddIPDialog(self):
        dialog = AddIPDialog(self)
        dialog.exec_()

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
            with open('datas/linkForUpdate.txt', 'r') as file:
                linkForUpdate = file.read().strip()

            updateNow = requests.get(linkForUpdate)
            updateNow.raise_for_status()
            remoteData = updateNow.json()
            
            localData = {}
            with open('update/updateNow.json', 'r') as file:
                localData = json.load(file)

            if remoteData["version"] == localData["version"]:
                self.updateStatusLogo.setPixmap(self.updateStatusNormal)
                self.updateStatusLabel.setText(self.lang[self.syslang]["Your PC isn't needing to update now"])
            else:
                self.updateStatusLogo.setPixmap(self.updateStatusMedium)
                self.updateStatusLabel.setText(self.lang[self.syslang]["You should to install updates for your PC"])
                
        except Exception as e:
            print(f"Error details: {e}")
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
