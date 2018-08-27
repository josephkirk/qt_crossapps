import sys
from PySide2 import QtCore, QtWidgets, QtGui, QtNetwork
import time
import os
import json
SIGNAL = QtCore.Signal
SLOT = QtCore.Slot

QW = QtWidgets
QC = QtCore
QG = QtGui
QN = QtNetwork

PORTS = (9990, 10000)
PORT = 9997
SIZEOF_UINT32 = 4

class CodeEdit(QW.QTextEdit):
    sendCode = SIGNAL()
    def __init__(self, *args, **kws):
        super(CodeEdit, self).__init__(*args, **kws)

class ClientDlg(QW.QWidget):
    serverDataPath = os.path.normpath("{}/AppServer/ServerDatas.json".format(os.environ["LOCALAPPDATA"]))
    def __init__(self, parent=None):
        super(ClientDlg, self).__init__(parent)

        self._port = PORT
        self.initServerData()
        self.socket = QN.QTcpSocket()

        self.nextBlockSize = 0
        self.request = None

        self.browser = QW.QTextBrowser()
        self.lineeditLabel = QW.QLabel("Enter Command Here:")
        self.codeedit = CodeEdit()
        self.codeedit.setUndoRedoEnabled(True)
        self.codeedit.selectAll()

        self.portLineEdit = QW.QLineEdit()
        self.portLineEdit.setValidator(QtGui.QIntValidator(1, 65535, self))
        self.portLineEdit.setText(str(PORT))

        self.serverListBox = QW.QComboBox()
        self.updateServerList()
        self.currentServerName = self.serverListBox.currentText()

        self.sendButton = QW.QPushButton("Send")

        self.refreshButton = QW.QPushButton("Refresh")
        self.cleanServerButton = QW.QPushButton("Clean Server Datas")

        self.connectButton = QW.QPushButton("Connect")
        self.connectButton.setEnabled(True)

        self.disconnectButton = QW.QPushButton("Disconnect")
        self.disconnectButton.setEnabled(False)

        self.connectShortCut = QW.QShortcut(QG.QKeySequence("Ctrl+Shift+C"), self)
        self.sendShortCut = QW.QShortcut(QG.QKeySequence("Ctrl+E"), self)
        self.undoShortCut = QW.QShortcut(QG.QKeySequence("Ctrl+Z"), self)

        layout = QW.QVBoxLayout()

        layout.addWidget(self.serverListBox)
        layout.addWidget(self.cleanServerButton)
        # layout.addWidget(self.sendButton)
        layout.addWidget(self.connectButton)
        layout.addWidget(self.disconnectButton)
        layout.addWidget(self.browser)
        layout.addWidget(self.lineeditLabel)
        layout.addWidget(self.codeedit)
        layout.addWidget(self.sendButton)

        # self.addAction(self.sendAction)
        self.setLayout(layout)
        self.codeedit.setFocus()
        # self.codeedit.sendCode.connect(self.sendMessage)
        self.sendButton.clicked.connect(self.sendMessage)
        self.connectButton.clicked.connect(self.connectToServer)
        self.disconnectButton.clicked.connect(self.disconnectServer)
        self.serverListBox.currentTextChanged.connect(self.changeServer)
        self.refreshButton.clicked.connect(self.updateServerList)
        self.cleanServerButton.clicked.connect(self.cleanServerDatas)

        self.sendShortCut.activated.connect(self.sendMessage)
        self.connectShortCut.activated.connect(self.connectToServer)
        self.undoShortCut.activated.connect(self.codeedit.undo)

        self.socket.readyRead.connect(self.readFromServer)
        self.socket.disconnected.connect(self.serverHasStopped)
        self.socket.error.connect(self.serverHasError)

        self.setWindowTitle('DCC Test Com')
        self.updateLoop = QC.QTimer()
        self.updateLoop.timeout.connect(self.updateServerStatus)
        self.updateLoop.start(1000)

    @property
    def port(self):
        # self.updateServerList()
        serverName = self.currentServerName
        if serverName in self.serverData["Servers"]:
            port = self.serverData["Servers"][serverName]
            return int(port)
        else:
            QW.QMessageBox.critical(self, "Server Error", "{} Server is not available".format(serverName))
            self.updateServerList()

    def initServerData(self):
        if os.path.isfile(self.serverDataPath):
            self.getServerData()
        else:
            self.serverData = {
                "Current":"",
                "Servers":{}
            }

    def getServerData(self, customPath=""):
        ppath = self.serverDataPath
        if customPath:
            ppath = customPath
        with open(ppath, 'r') as read_file:
            self.serverData = json.load(read_file)

    def updateServerStatus(self):
        self.initServerData()
        print(self.serverData)

    def cleanServerDatas(self):
        os.remove(self.serverDataPath)
        self.initServerData()

    def updateServerList(self):
        self.serverListBox.clear()
        self.getServerData()
        for appname, port in self.serverData["Servers"].items():
            if port != -1:
                self.serverListBox.addItem(appname)

    def changeServer(self, serverName):
        self.currentServerName = serverName
        # print( self.currentServerName)
        # self.disconnectServer()
        # self.connectToServer()

    def updateUI(self, text):
        self.browser.append(text)

    def connectToServer(self):
        if self.port:
            self.connectButton.setEnabled(False)
            self.disconnectButton.setEnabled(True)
            self.socket.connectToHost("localhost", self.port)

    def disconnectServer(self):
        self.disconnectButton.setEnabled(False)
        self.serverHasStopped()
        self.browser.clearHistory()
        self.updateUI("{:_^40}".format(
            "{} Server Disconnect".format(self.currentServerName)))

    def issueRequest(self, request):
        self.request = QC.QByteArray()
        stream = QC.QDataStream(self.request, QC.QIODevice.WriteOnly)
        stream.setVersion(QC.QDataStream.Qt_4_2)
        stream.writeUInt32(0)
        stream.writeQString(request)
        stream.device().seek(0)
        stream.writeUInt32(self.request.size() - SIZEOF_UINT32)
        self.socket.write(self.request)
        self.nextBlockSize = 0
        self.request = None

    def sendMessage(self):
        self.issueRequest(self.codeedit.toPlainText())
        self.codeedit.setText("")

    def readFromServer(self):
        stream = QC.QDataStream(self.socket)
        stream.setVersion(QC.QDataStream.Qt_4_2)
        while True:
            if self.nextBlockSize == 0:
                if self.socket.bytesAvailable() < SIZEOF_UINT32:
                    break
                self.nextBlockSize = stream.readUInt32()
            if self.socket.bytesAvailable() < self.nextBlockSize:
                break
            textFromServer = stream.readQString()
            self.updateUI(textFromServer)
            self.nextBlockSize = 0

    def serverHasStopped(self):
        try:
            self.socket.close()
        except RuntimeError:
            pass
        self.connectButton.setEnabled(True)
        self.updateServerList()

    def serverHasError(self):
        self.updateUI("{} Server Connection Error: \n{}".format(
            self.currentServerName,
            self.socket.errorString()
        ))
        self.socket.close()
        self.updateServerList()
        self.connectButton.setEnabled(True)
        self.disconnectButton.setEnabled(False)

if __name__ == "__main__":
    app = QW.QApplication(sys.argv)
    form = ClientDlg()
    form.show()
    sys.exit(app.exec_())



    