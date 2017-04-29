# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación de la clase para construir una aplicación de Qt que solo permita ejecutar una instancia a la vez (singleton).

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com

###################################################################################################################################################################################
## DEPENDENCIAS:
###################################################################################################################################################################################

from sys import exit
from sessionManager import sessionManager
from PyQt4.QtCore import Qt, QTimer, QTextStream, pyqtSignal
from PyQt4.QtGui import QApplication
from PyQt4.QtNetwork import QLocalSocket, QLocalServer

###################################################################################################################################################################################
## DECLARACIÓN DEL SINGLETON:
###################################################################################################################################################################################

class QSingleton(QApplication):

    messageReceived = pyqtSignal()

    def __init__(self, id, *argv):

        super(QSingleton, self).__init__(*argv)
        self._id = id
        self._activationWindow = None
        self._activateOnMessage = False

        # Is there another instance running?
        self._outSocket = QLocalSocket()
        self._outSocket.connectToServer(self._id)
        self._isRunning = self._outSocket.waitForConnected()

        if self._isRunning:
            # Yes, there is.
            self._outStream = QTextStream(self._outSocket)
            self._outStream.setCodec('UTF-8')
        else:
            # No, there isn't.
            self._outSocket = None
            self._outStream = None
            self._inSocket = None
            self._inStream = None
            self._server = QLocalServer()
            self._server.listen(self._id)
            self._server.newConnection.connect(self._onNewConnection)

        self.setQuitOnLastWindowClosed(False)

    def initCS(self):
        self.sessionManager = sessionManager()
        self.sessionManager.splash.show()
        self.setActivationWindow(self.sessionManager)
        QTimer.singleShot(5000, lambda: self.sessionManager.splash.hide())
        QTimer.singleShot(5500, lambda: self.sessionManager.show())
        return exit(self.exec_())

    def isRunning(self):
        return self._isRunning

    def id(self):
        return self._id

    def activationWindow(self):
        return self._activationWindow

    def setActivationWindow(self, activationWindow, activateOnMessage = True):
        self._activationWindow = activationWindow
        self._activateOnMessage = activateOnMessage

    def activateWindow(self):
        if not self._activationWindow:
            return
        self._activationWindow.setWindowState(
            self._activationWindow.windowState() & ~Qt.WindowMinimized)
        self._activationWindow.raise_()
        self._activationWindow.activateWindow()

    def sendMessage(self, msg):
        if not self._outStream:
            return False
        self._outStream << msg << '\n'
        self._outStream.flush()
        return self._outSocket.waitForBytesWritten()

    def _onNewConnection(self):
        if self._inSocket:
            self._inSocket.readyRead.disconnect(self._onReadyRead)
        self._inSocket = self._server.nextPendingConnection()
        if not self._inSocket:
            return
        self._inStream = QTextStream(self._inSocket)
        self._inStream.setCodec('UTF-8')
        self._inSocket.readyRead.connect(self._onReadyRead)
        if self._activateOnMessage:
            self.activateWindow()

    def _onReadyRead(self):
        while True:
            msg = self._inStream.readLine()
            if not msg: break
            self.messageReceived.emit(msg)

###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################