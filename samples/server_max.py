'''
3dsmax Usage:
    python.executeFile(@"D:\Works\Code\Qt_crossapps\samples\server_max.py")

Initialize Qt Server to listen to External Tool
'''

import sys
from PySide2 import QtCore, QtWidgets, QtGui, QtNetwork
try:
    import pymxs
    import MaxPlus
except:
    sys.exit()

rt = pymxs.runtime
evalmsx = MaxPlus.Core.EvalMAXScript
MainWindow = MaxPlus.GetQMaxMainWindow()

SIGNAL = QtCore.Signal
SLOT = QtCore.Slot

QW = QtWidgets
QC = QtCore
QG = QtGui
QN = QtNetwork
Qt = QC.Qt

PORTS = (9998, 9999)
PORT = 9999
SIZEOF_UINT32 = 4

rt.enableAccelerators = False
class ServerDlg(QW.QPushButton):
    def __init__(self, parent=None):
        super(ServerDlg, self).__init__("&Close Server", parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint | Qt.Window)
        self._name = "Max"
        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.NoFocus)
        self.tcpServer = QN.QTcpServer(self)
        self.tcpServer.listen(QN.QHostAddress("0.0.0.0"), PORT)
        # self.connect(
            # self.tcpServer, SIGNAL("newConnection()"), self.addConnection)
        self.tcpServer.newConnection.connect(self.addConnection)
        self.connections = []

        self.clicked.connect(self.close)
        font = self.font()
        font.setPointSize(18)
        self.setFont(font)
        self.setWindowTitle("Max Server")
        self.resize(200,50)
        self.setSizePolicy(QW.QSizePolicy.Fixed, QW.QSizePolicy.Fixed)
        print("Server is listening at {}".format(PORT))

    # def closeEvent(self, event):
    #     event.accept()
    #     self.deleteLater()

    def addConnection(self):
        clientConnection = self.tcpServer.nextPendingConnection()
        clientConnection.nextBlockSize = 0
        self.connections.append(clientConnection)

        clientConnection.readyRead.connect(self.receiveMessage)
        clientConnection.disconnected.connect(self.removeConnection)
        clientConnection.error.connect(self.socketError)
        self.sendText(clientConnection, "Connected To {} Server at {}".format(self._name, PORT))

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
                result = eval(textFromClient)
                self.activateWindow()
                rt.completeRedraw()
                self.sendMessage(result, s.socketDescriptor())
                s.nextBlockSize = 0

    def sendMessage(self, text, socketID):
        for s in self.connections:
            if s.socketDescriptor() == socketID:
                message = "Result >> {}".format(text)
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
    if not app:
        app = QW.QApplication(sys.argv)
    try:
        form.close()
    except:
        pass
    form = ServerDlg()
    form.show()
    # app.exec_()
