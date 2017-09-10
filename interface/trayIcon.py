# -*- encoding: utf-8 -*-

#######################################################################################################################
## DESCRIPCIÓN:
#######################################################################################################################

# Modúlo con la implementación del manejador del icono para la barra de notificaciones.

#######################################################################################################################
## AUTORES:
#######################################################################################################################

# Carlos Serrada, cserradag96@gmail.com

#######################################################################################################################
## MODÚLOS:
#######################################################################################################################

# Función exit del sistema para finalizar correctamente el programa
from sys import exit

# Módulo con procedimientos de Qt
from PyQt4.QtGui import QSystemTrayIcon, QMenu, QAction

#######################################################################################################################
## MANEJADOR DEL ICONO PARA LA BARRA DE NOTIFICACIONES:
#######################################################################################################################

class trayIcon(QSystemTrayIcon):
    #==================================================================================================================
    # CONSTRUCTOR DE LA CLASE
    #==================================================================================================================
    def __init__(self, server, icon, parent=None):
        #--------------------------------------------------------------------------------------------------------------
        # INICIAR Y CONFIGURAR LA INSTANCIA
        #--------------------------------------------------------------------------------------------------------------

        QSystemTrayIcon.__init__(self, icon, parent)            # Iniciar la instancia
        self.parent = parent                                    # Almacenar referencia hacia el padre
        self.server = server

        #--------------------------------------------------------------------------------------------------------------
        # MENU
        #--------------------------------------------------------------------------------------------------------------

        self.menu = QMenu(self.parent)                          # Definir menú para el trayIcon
        self.setContextMenu(self.menu)                          # Enlazar menú con el trayIcon

        self.showWindow = QAction("Mostrar", self)              # Crear acción para mostrar la ventana de la aplicación en el menu
        self.showWindow.triggered.connect(self.parent.show)     # Conectar la acción de mostrar con la función para mostrar la ventana de login
        self.menu.addAction(self.showWindow)                    # Añadir la acción al menú

        self.kill = QAction("Salir", self)                      # Crear acción para cerrar la aplicación
        self.kill.triggered.connect(self.killApp)               # Conectar la acción de cerrar con la función para cerrar el programa
        self.menu.addAction(self.kill)                          # Añadir la acción al menú

        #--------------------------------------------------------------------------------------------------------------
        # SEÑALES
        #--------------------------------------------------------------------------------------------------------------

        self.parent.sessionClosed.connect(self.sessionClosed)   # Conectar la señal de cerrar la ventana principal y cerrar la sesióm
        self.parent.sessionAlive.connect(self.sessionAlive)     # Conectar la señal de cerrar la ventana principal y NO cerrar la sesióm

    #==================================================================================================================
    # MÉTODOS
    #==================================================================================================================

    # Método para atrapar la señal de cerrar la ventana principal y cerrar la sesióm
    def sessionClosed(self):
        self.showWindow.triggered.disconnect()                          # Desconectar la acción de mostrar de cualquier función
        self.showWindow.triggered.connect(self.parent.show)             # Conectar la acción de mostrar con la función para mostrar la ventana de login

    # Método para atrapar la señal de cerrar la ventana principal y NO cerrar la sesióm
    def sessionAlive(self):
        self.showWindow.triggered.disconnect()                          # Desconectar la acción de mostrar de cualquier función
        self.showWindow.triggered.connect(self.parent.mainWindow.show)  # Conectar la acción de mostrar con la función para mostrar la ventana principal

    # Método para terminar el programa
    def killApp(self):
        if self.parent.guiExist:                          # Si existe la ventana principal
            mainWindow = self.parent.mainWindow           # Apuntador hacia la ventana principal
            if mainWindow.db.isOpenTurn():                # Si hay un turno abierto
                mainWindow.db.closeTurn(mainWindow.user)  # Cerrar turno del usuario de la ventana principal
            mainWindow.close()                            # Cerrar la ventana principal
        self.parent.db.close()                            # Cerrar la sesión en la base de datos
        self.parent.close()                               # Cerrar la ventana de login
        self.server.close()                               # Cerrar el servidor de la aplicación
        exit(0)                                           # Salir del programa

#######################################################################################################################
## FIN :)
#######################################################################################################################
