# -*- encoding: utf-8 -*-

#######################################################################################################################
## DESCRIPCIÓN:
#######################################################################################################################

# Modúlo con la implementación del QSingleton personalizado para ejecutar CEICSuite.

#######################################################################################################################
## AUTORES:
#######################################################################################################################

# Carlos Serrada, cserradag96@gmail.com

#######################################################################################################################
## DEPENDENCIAS:
#######################################################################################################################

from sys import exit                        # Método del sistema para finalizar la aplicación
from sessionManager import sessionManager   # Manejador de sessiones
from QSingleton import QSingleton           # Clase para crear singletones
from PyQt4.QtCore import QTimer             # Temporizador para programar actividades

#######################################################################################################################
## DECLARACIÓN DE LA CLASE PARA EJECUTAR CEIC SUITE
#######################################################################################################################

class CEICSuiteApp(QSingleton):
    #==================================================================================================================
    # CONSTRUCTOR DE LA CLASE
    #==================================================================================================================
    def __init__(self, argv, appID="CEICSuiteServerAplication"):

        #--------------------------------------------------------------------------------------------------------------
        # INICIAR LA CLASE
        #--------------------------------------------------------------------------------------------------------------
        super(CEICSuiteApp, self).__init__(appID, argv)

        #--------------------------------------------------------------------------------------------------------------
        # RUTINA DE INICIO DE LA APLICACIÓN
        #--------------------------------------------------------------------------------------------------------------

        if self.isRunning(): exit(0)           # Si hay instancias corriendo entonces finaliza el programa
        self.setApplicationName("CEIC Suite")  # Nombre de la aplicación
        self.setApplicationVersion('1.0')      # Versión de la aplicación
        self.setQuitOnLastWindowClosed(False)  # Desactivar cierre en cascada
        self.startApp()                        # Iniciar la aplicación

    #==================================================================================================================
    # MÉTODOS
    #==================================================================================================================

    # Método para iniciar la aplicación
    def startApp(self):
        self.sessionManager = sessionManager(self._server)                  # Crear el manejador de la sessión
        self.sessionManager.splash.show()                                   # Mostrar la pantalla splash
        QTimer.singleShot(5000, lambda: self.sessionManager.splash.hide())  # Ocultamiento de la pantalla splash
        QTimer.singleShot(5500, lambda: self.sessionManager.show())         # Despliegue del manejador de sessiones
        return exit(self.exec_())                                           # Bucle principal de la aplicación

#######################################################################################################################
## FIN :)
#######################################################################################################################
