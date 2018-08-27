#!/usr/bin/env python
"""PySide2 port of the network/threadedfortuneserver example from Qt v5.x, originating from PyQt"""

import random
try:
    from PySide2.QtCore import (Signal, QByteArray, QDataStream, QIODevice,
            QThread, Qt)
    from PySide2.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
            QMessageBox, QPushButton, QVBoxLayout)
    from PySide2.QtNetwork import (QHostAddress, QNetworkInterface, QTcpServer,
            QTcpSocket)
except:
    from PySide.QtCore import (Signal, QByteArray, QDataStream, QIODevice,
            QThread, Qt)
    from PySide.QtGui import (QApplication, QDialog, QHBoxLayout, QLabel,
            QMessageBox, QPushButton, QVBoxLayout)
    from PySide.QtNetwork import (QHostAddress, QNetworkInterface, QTcpServer,
            QTcpSocket)
#from pymxs import runtime as rt

class FortuneThread(QThread):
    error = Signal(QTcpSocket.SocketError)
    msg = Signal(str)
    def __init__(self, socketDescriptor, fortune, parent):
        super(FortuneThread, self).__init__(parent)
        #print socketDescriptor
        self.socketDescriptor = socketDescriptor
        self.text = fortune

    def run(self):
        tcpSocket = QTcpSocket()
        if not tcpSocket.setSocketDescriptor(self.socketDescriptor):
            self.error.emit(tcpSocket.error())
            return


        block = QByteArray()
        outstr = QDataStream(block, QIODevice.WriteOnly)
        outstr.setVersion(QDataStream.Qt_4_0)
        outstr.writeUInt16(0)
        outstr.writeQString(self.text)
        outstr.device().seek(0)
        outstr.writeUInt16(block.size() - 2)
        msg = tcpSocket.readAll()
        self.msg.emit(msg)
        print(msg)
        tcpSocket.write(block)
        tcpSocket.disconnectFromHost()
        tcpSocket.waitForDisconnected()


class FortuneServer(QTcpServer):
    fortune = []

    def incomingConnection(self, socketDescriptor):
        fortune = str([i for i in rt.selection])
        thread = FortuneThread(socketDescriptor, fortune, self)
        thread.finished.connect(thread.deleteLater)
        thread.start()


class Dialog(QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        self.server = FortuneServer()

        statusLabel = QLabel()
        statusLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
        statusLabel.setWordWrap(True)
        quitButton = QPushButton("Quit")
        quitButton.setAutoDefault(False)

        if not self.server.listen():
            QMessageBox.critical(self, "Threaded Fortune Server",
                    "Unable to start the server: %s." % self.server.errorString())
            self.close()
            return

        for ipAddress in QNetworkInterface.allAddresses():
            if ipAddress != QHostAddress.LocalHost and ipAddress.toIPv4Address() != 0:
                break
        else:
            ipAddress = QHostAddress(QHostAddress.LocalHost)

        ipAddress = ipAddress.toString()

        statusLabel.setText("The server is running on\n\nIP: %s\nport: %d\n\n"
                "Run the Fortune Client example now." % (ipAddress, self.server.serverPort()))

        quitButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(quitButton)
        buttonLayout.addStretch(1)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(statusLabel)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

        self.setWindowTitle("Threaded Fortune Server")


if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    dialog = Dialog()
    dialog.show()
    sys.exit(dialog.exec_())
