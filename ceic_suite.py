#!/usr/bin/python3
# -*- encoding: utf-8 -*-

####################################################################################################################################
## DESCRIPCIÓN:
####################################################################################################################################

# Sistema de Ventas CEICSV

####################################################################################################################################
## AUTORES:
####################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com

####################################################################################################################################
## PATH DE LA APLICACIÓN:
####################################################################################################################################

from sys import path       # Importación del path del sistema
from os import getcwd      # Importación de la función para obtener el path actual
from os.path import join   # Importación de función para unir paths con el formato del sistema

# Agregar las rutas faltanes al path
path.append(join(getcwd(), "models"))
path.append(join(getcwd(), "interface"))
path.append(join(getcwd(), "modules"))

####################################################################################################################################
## MODÚLOS:
####################################################################################################################################

from sys import argv, exit
from sessionManager import sessionManager
from guiManager import guiManager
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import Qt, QTimer
from db_manager import *

####################################################################################################################################
## PROGRAMA PRINCIPAL:
####################################################################################################################################

def displayLogin():
    loginApp = QApplication(argv)
    loginWindow = sessionManager()
    loginWindow.splash.show()
    QTimer.singleShot(5000, lambda: loginWindow.splash.hide())
    QTimer.singleShot(5500, lambda: loginWindow.show())
    return exit(loginApp.exec_())

def displayMainWindow(mode, dbm):
    MainWindowApp = QApplication(argv)
    if mode == 0: MainWindow = guiManager(dbm)
    #elif mode == 1: MainWindow = sellerGUI()
    #else: MainWindow = collaboratorGUI()
    MainWindow.show()
    return exit(MainWindowApp.exec_())

if __name__ == '__main__':
    # Inicializar interfaz:
    log = displayLogin()
    #db = dbManager("carlos", "curtis", True)
    #xd = displayMainWindow(0, db)

####################################################################################################################################
## FIN :)
####################################################################################################################################
