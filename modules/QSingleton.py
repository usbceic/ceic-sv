# -*- encoding: utf-8 -*-

#######################################################################################################################
## DESCRIPCIÓN:
#######################################################################################################################

# Modúlo con la implementación de la clase para construir una aplicación de Qt que solo permita ejecutar una instancia a la vez (singleton).

#######################################################################################################################
## AUTORES:
#######################################################################################################################

# Carlos Serrada, cserradag96@gmail.com

#######################################################################################################################
## DEPENDENCIAS:
#######################################################################################################################

from PyQt5.QtCore import QTextStream, pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtNetwork import QLocalSocket, QLocalServer

#######################################################################################################################
## DECLARACIÓN DEL SINGLETON:
#######################################################################################################################

class QSingleton(QApplication):
    messageReceived = pyqtSignal()  # Señal de mensaje recibido

    #==================================================================================================================
    # CONSTRUCTOR DE LA CLASE
    #==================================================================================================================
    def __init__(self, appID, argv):
        #--------------------------------------------------------------------------------------------------------------
        # INICIAR LA CLASE
        #--------------------------------------------------------------------------------------------------------------
        super(QSingleton, self).__init__(argv)

        #--------------------------------------------------------------------------------------------------------------
        # CONFIGURACIONES INICIALES
        #--------------------------------------------------------------------------------------------------------------

        self.appID = appID
        self._outSocket = QLocalSocket()
        self._outSocket.connectToServer(self.appID)
        self._isRunning = self._outSocket.waitForConnected()

        # Si hay instancias previas corriendo
        if self._isRunning:
            self._outStream = QTextStream(self._outSocket)
            self._outStream.setCodec('UTF-8')

        # Si es la primera instancia
        else:
            self._outSocket = None
            self._outStream = None
            self._inSocket = None
            self._inStream = None
            self._server = QLocalServer()
            self._server.listen(self.appID)
            self._server.newConnection.connect(self._onNewConnection)

    #==================================================================================================================
    # MÉTODOS
    #==================================================================================================================

    # Método para saber si hay instancias previas ejecutandose
    def isRunning(self):
        return self._isRunning

    # Método para crear una nueva conexión
    def _onNewConnection(self):
        if self._inSocket:
            self._inSocket.readyRead.disconnect(self._onReadyRead)
        self._inSocket = self._server.nextPendingConnection()
        if not self._inSocket:
            return
        self._inStream = QTextStream(self._inSocket)
        self._inStream.setCodec('UTF-8')
        self._inSocket.readyRead.connect(self._onReadyRead)

    # Método para lectura del socket
    def _onReadyRead(self):
        while True:
            msg = self._inStream.readLine()
            if not msg: break
            self.messageReceived.emit(msg)

#######################################################################################################################
## FIN :)
#######################################################################################################################
