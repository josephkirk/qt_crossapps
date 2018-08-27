#/usr/bin/env python
# -*- coding: utf-8 -*-

_name = "Universal_Tool_Checker"
_version = "001.00"
_author = "Nguyen Phi Hung"

try:
    from PySide2 import QtCore, QtGui, QtWidgets, QtNetwork
except ImportError:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui
import logging
from .Lib.ui import styleSheet

# Pyside Refactor
Signal = QtCore.Signal
Slot = QtCore.Slot
QW = QtWidgets
QC = QtCore
QG = QtGui

# Logging initialize #
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Utils Function

# UIClass
class main(QtWidgets.QMainWindow):
    '''
    Universal Tool Finder
    '''

    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(_name)
        self.setObjectName(_name)
        # init UI
        self._initMainUI()
        self.createMenuBar()
        self.statusBar()

    # Util Function


    # Initial Value Definition
    def _initUIValue(self):
        pass

    def _getUIValue(self):
        pass

    def _initMainUI(self):
        self._initUIValue()
        self._getUIValue()
        # create Widget
        self.topFiller = QtWidgets.QWidget(self)
        self.topFiller.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.bottomFiller = QtWidgets.QWidget(self)
        self.bottomFiller.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.mainCtner = QtWidgets.QWidget(self)
        # Create Layout
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainCtner)
        # Add widget
        self.addWidgets()
        # Set Layout
        self.mainCtner.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainCtner)
        self.setStyleSheet(uiStyle.styleSheet)
        self._connectFunction()

    def addWidgets(self):
        pass

    def _connectFunction(self):
        def connect(button,func):
            button.clicked.connect(func)
        pass

    def createMenuBar(self):
        # create Action
        self.reset_action = QtWidgets.QAction('Reset', self)
        self.reset_action.setToolTip('Reset UI To Default Value')
        self.reset_action.setStatusTip('Reset UI To Default Value')
        self.reset_action.triggered.connect(self.resetUI)
        # create Menu
        self.menubar = self.menuBar()
        self.optionmenu = self.menubar.addMenu('Option')
        self.optionmenu.addAction(self.reset_action)
        # self.me

    def resetUI(self):
        self._initMainUI()
        self.show()


    @classmethod
    def showUI(cls):
        cls().show()

def show():
    win = main()
    win.show()
    return win

if __name__ =='__main__':
    try:
        app = QtWidgets.QApplication([])
    except:
        raise
    show()
    if app in globals():
        app.exec_()