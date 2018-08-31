
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
import logging

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

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

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
    def __init__(self, parent=None, app=None):
        super(ServerDlg, self).__init__("&Close Server", parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint | Qt.Window)
        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.NoFocus)
        self.setObjectName("Qt_Crossapp_Server")
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

        self._host = "0.0.0.0"
        self._port = PORT
        
        self.udpSocket4 = QN.QUdpSocket(self)
        self.udpSocket6 = QN.QUdpSocket(self)
        self._ip4Address = QN.QHostAddres("10.0.134.38")
        self._ip6Address = QN.QHostAddres("fe80::41d0")

        self.setWindowTitle("{} Server".format(self.appname))
        self.initServer()

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        log.info("Switch port to {}".format(self._port))

    @property
    def ip4Address(self):
        return QN.QHostAddress(self._ip4Address)

    @ip4Address.setter
    def ip4Address(self, address):
        cond = re.compile(r"^(\b(\d+\.?){4}\b|\blocalhost\b)$")
        if cond.match(address):
            self._ip4Address = address
        else:
            log.error( "Failed to set ip4 adrress to {}. Host Address might be invalid".format(address))

    @property
    def ip6Address(self):
        return QN.QHostAddress(self._ip6Address)

    @ip6Address.setter
    def ip6Address(self, address):
        cond = re.compile(r"^((\d|[a-z]){4}(:{2})?)+$")
        if cond.match(address):
            self._ip6Address = address
        else:
            log.error( "Failed to set ip4 adrress to {}. Host Address might be invalid".format(address))

    def bindSocket(self):
        self.udpSocket4.bind(QN.QHostAddress.AnyIPv4, self.port, QN.QUdpSocket.ShareAdrress)
        self.udpSocket4.joinMulticastGroup(self.ip4Address)
        if (not self.udpSocket6.bind(QN.QHostAddress.AnyIPv4, self.port, QN.QUdpSocket.ShareAdrress) and 
                not self.udpSocket6.join(MultiCastGroup(self.ip6Address))):
            log.info("Listening To multicast message on IPV4 only")
        self.udpSocket4.readyRead.connect(self.processPendingData)
        self.udpSocket6.readyRead.connect(self.processPendingData)

    def initServer(self):
        self.bindSocket()
        log.info("{} Server is listening".format(self.appname))

    def processPendingData(self):
        while self.udpSocket4.hasPendingDatagrams():
            self.processData(self.udpSocket4)

        while self.udpSocket6.hasPendingDatagrams():
            self.processData(self.udpSocket6)

    def processData(self, socket):
        datagram = QC.QByteArray()
        datagram.resize(int(socket.pendingDatagramSize()))
        socket.readDatagram(datagram.data(), datagram.size())
        if self.executeData(datagram):
            log.info("Received Message: {}".format(datagram.constData()))
        

    def processData2(self, socket):
        """Qt 5.8+ method"""
        datagram = socket.receiveDatagram()
        if self.executeData(datagram):
            log.info("Received Message from {}:{}: {}".format(
                str(datagram.senderAddress()), datagram.senderPort(), datagram.data().constData()))

    def excecuteData(self, data):
        try:
            try:
                result = eval(textFromClient)
            except SyntaxError:
                exec(textFromClient, globals(), locals())
            if not result:
                self.sendMessage(textFromClient, s.socketDescriptor(), prefix="Executed")
            else:
                self.sendMessage(result, s.socketDescriptor(), prefix="Result")
            return True
        except:
            log.debug("Failed to execute message:\n{}".format(data))

    def sendMessage(self, message, prefix="Message"):
        log.info("Sending Reply")
        data = QC.QByteArray("{} >> {}".format(prefix, message))
        self.udpSocket4.writeDatagram(data, self.ipAddress4, self.port)
        if self.udpSocket6.state() == QN.QAbstractSocket.BoundState:
            self.udpSocket6.writeDatagram(data, self.ipAddress6, self.port)

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