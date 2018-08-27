
import sys
import os
import json

try:
    from PySide2 import QtCore, QtWidgets, QtGui, QtNetwork
except:
    try:
        from PySide import QtCore, QtGui, QtNetwork
        QtWidgets = QtGui
    except:
        print("Application must support PySide or PySide2")
        sys.exit()

from random import randrange
import re

SIGNAL = QtCore.Signal
SLOT = QtCore.Slot

QW = QtWidgets
QC = QtCore
QG = QtGui
QN = QtNetwork
Qt = QC.Qt

PORTS = (9990, 9999)
PORT = 9997
SIZEOF_UINT32 = 4

app_name = "Unknown"
app_dict = {
    "3dsmax": {"pymxs.runtime":"rt", "MaxPlus":"mp"},
    "maya": {"pymel.core":"pm", "maya.OpenMaya":"om", "maya.cmds":"cmds"},
    "ue4": {"unreal_engine":"ue"},
}

for app, pkgs in app_dict.items():
    for pkg, apv in pkgs.items():
        try:
            exec("import {} as {}".format(pkg, apv),globals(), locals())
            print("{} module init----import {} as {}----".format(app,pkg,apv))
            app_name = app
        except:
            pass

def runFile(filePath):
    exec(open(filePath).read(), globals(), locals())

class ServerDlg(QW.QPushButton):
    serverDataPath = "{}/SparxTA/AppServer/ServerDatas.json".format(os.environ["LOCALAPPDATA"])
    def __init__(self, parent=None, app=None):
        super(ServerDlg, self).__init__("&Close Server", parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint | Qt.Window)
        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.NoFocus)
        font = self.font()
        font.setPointSize(18)
        self.setFont(font)
        self.initServerData()
        self.resize(200,50)
        self.setSizePolicy(QW.QSizePolicy.Fixed, QW.QSizePolicy.Fixed)
        self.clicked.connect(self.close)

        self.app = app
        self.appDir = self.app.applicationFilePath()
        self.appPid = self.app.applicationPid()
        self.appname = self.app.applicationName()
        if not self.appname:
            self.appname = app_name
        self.app.aboutToQuit.connect(self.close)
        self.app.focusChanged.connect(self.updateServerStatus)
        # self.app.lastWindowClosed.connect(self.close)
        # self.app.applicationStateChanged.connect(self.updateServerStatus)
        self._host = "0.0.0.0"
        self._port = PORT
        
        self.tcpServer = QN.QTcpServer(self)
        self.tcpServer.newConnection.connect(self.addConnection)
        self.connections = []

        self.setWindowTitle("{} Server".format(self.appname))
        self.initServer()

    @property
    def host(self):
        return QN.QHostAddress(self._host)

    @host.setter
    def host(self, newHost):
        cond = re.compile(r"^(\b(\d{3}\.?){4}\b|\blocalhost\b)$")
        if cond.match(newHost):
            self._host = newHost
        else:
            print( "Failed to set host to {}. Host Address might be invalid".format(newHost))

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, newPort):
        self._port = newPort

    def initServer(self):
        for _ in range(*PORTS):
            print("{} Server is attempting to listening on {}:{}".format(
                self.appname, self.getServerName(), self.port))
            self.tcpServer.listen(self.host, self.port)
            if self.tcpServer.isListening():
                break
            self.changePort()

        if self.tcpServer.isListening():
            serverPort = self.serverData["Servers"].get(self.appname, -1)
            i = 1
            iterAppName = self.appname
            while serverPort != self.port:
                if serverPort == -1:
                    break
                iterAppName = "{}_{}".format(self.appname, i)
                serverPort = self.serverData["Servers"].get(iterAppName, -1)
            self.appname = iterAppName
            self.serverData["Servers"][self.appname] = self.port
            self.serverData["Current"] = self.appname
            self.saveServerData()
            print("{} Server is listening".format(self.appname))
            return
        print("Server failed to listen")
        self.close()
        sys.exit()

    def initServerData(self):
        if os.path.isfile(self.serverDataPath):
            self.getServerData()
        else:
            if not os.path.isdir(os.path.dirname(self.serverDataPath)):
                QC.QDir().mkpath(os.path.dirname(self.serverDataPath))
            self.serverData = {
                "Current":"",
                "Servers":{}
            }
            self.saveServerData()

    def getServerData(self, customPath=""):
        ppath = self.serverDataPath
        if customPath:
            ppath = customPath
        with open(ppath, 'r') as read_file:
            self.serverData = json.load(read_file)

    def saveServerData(self, customPath=""):
        ppath = self.serverDataPath
        with open(ppath, 'w') as write_file:
            json.dump(self.serverData, write_file, indent=4, sort_keys=True)

    def updateServerStatus(self, *args):
        self.getServerData()
        self.serverData["Current"] = self.appname
        self.saveServerData()

    def serverEnvExit(self):
        self.getServerData()
        self.serverData["Servers"][self.appname] = -1
        self.serverData["Current"] = ""
        self.saveServerData()

    def changePort(self):
        start, end = PORTS
        self.port += 1
        if self.port > end:
            self.port = start

    def getServerName(self):
        if self.host.toString() == "0.0.0.0":
            return "localhost"
        return self.host.toString()

    # def showEvent(self, event):
    #     for _ in range(*PORTS):
    #         print("{} Server is attempting to listening on {}:{}".format(
    #             self.appname, self.getServerName(), self.port))
    #         self.tcpServer.listen(self.host, self.port)
    #         if self.tcpServer.isListening():
    #             break
    #         self.changePort()

    #     if self.tcpServer.isListening():
    #         print("Server is listening")
    #         self.serverData[self.appname] = self.port
    #         self.saveServerData()
    #         event.accept()
    #     else:
    #         print("Server failed to listen")
    #         event.ignore()
    #         self.close()
    #         sys.exit()
        # self.parent().hide()

    def closeEvent(self, event):
        self.tcpServer.close()
        self.serverEnvExit()
        event.accept()
        # self.app.quit()

    def resizeEvent(self, event):
        event.ignore()

    def addConnection(self):
        clientConnection = self.tcpServer.nextPendingConnection()
        clientConnection.nextBlockSize = 0
        self.connections.append(clientConnection)

        clientConnection.readyRead.connect(self.receiveMessage)
        clientConnection.disconnected.connect(self.removeConnection)
        clientConnection.error.connect(self.socketError)

        self.sendText(clientConnection, "Connected To {} Server at {}:{}".format(
            self.appname, self.getServerName(), self.port))

    def receiveMessage(self):
        for s in self.connections:
            if s.bytesAvailable() > 0:
                stream = QC.QDataStream(s)
                stream.setVersion(QC.QDataStream.Qt_4_2)

                if s.nextBlockSize == 0:
                    if s.bytesAvailable() < SIZEOF_UINT32:
                        return
                    s.nextBlockSize = stream.readUInt32()

                if s.bytesAvailable() < s.nextBlockSize:
                    return

                textFromClient = stream.readQString()
                s.nextBlockSize = 0
                result = None
                try:
                    result = eval(textFromClient)
                except SyntaxError:
                    exec(textFromClient, globals(), locals())
                if not result:
                    self.sendMessage(textFromClient, s.socketDescriptor(), prefix="Executed")
                else:
                    self.sendMessage(result, s.socketDescriptor(), prefix="Result")
                s.nextBlockSize = 0

    def sendMessage(self, text, socketID, prefix="Message"):
        for s in self.connections:
            if s.socketDescriptor() == socketID:
                message = "{} >> {}".format(prefix, text)
            else:
                message = "{} >> {}".format(socketID, text)
            self.sendText(s, message)

    def sendText(self, connection, text):
        reply = QC.QByteArray()
        stream = QC.QDataStream(reply, QC.QIODevice.WriteOnly)
        stream.setVersion(QC.QDataStream.Qt_4_2)
        stream.writeUInt32(0)
        stream.writeQString(text)
        stream.device().seek(0)
        stream.writeUInt32(reply.size() - SIZEOF_UINT32)
        connection.write(reply)

    def removeConnection(self):
        pass

    def socketError(self):
        pass

if __name__ == "__main__":

    app = QW.QApplication.instance()
    appIsInstance = True
    if not app:
        app = QW.QApplication(sys.argv)
        appIsInstance = False
    server = ServerDlg(app=app)
    # server.show()
    if not appIsInstance:
        try:
            sys.exit(app.exec_())
        except:
            pass