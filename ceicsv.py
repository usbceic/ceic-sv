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
# Christian Oliveros, 01christianol01@gmail.com
# José Acevedo, joseluisacevedo1995@gmail.com
# David Cabeza, cabezadavide@gmail.com
# Pablo Betancourt, pablodbc30@gmail.com

####################################################################################################################################
## MODÚLOS:
####################################################################################################################################

import sys
from sessionManager import loginGUI
from guiManager import adminGUI
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import Qt, QTimer
from DBManager import *

####################################################################################################################################
## PROGRAMA PRINCIPAL:
####################################################################################################################################

def displayLogin():
    loginApp = QApplication(sys.argv)
    loginWindow = loginGUI()
    loginWindow.splash.show()
    QTimer.singleShot(5000, lambda: loginWindow.splash.hide())
    QTimer.singleShot(5500, lambda: loginWindow.show())
    return loginApp.exec_()

def displayMainWindow(mode, dbm):
    MainWindowApp = QApplication(sys.argv)
    if mode == 0: MainWindow = adminGUI(dbm)
    #elif mode == 1: MainWindow = sellerGUI()
    #else: MainWindow = collaboratorGUI()
    MainWindow.show()
    return MainWindowApp.exec_()

if __name__ == '__main__':
    # Inicializar interfaz:
    log = displayLogin()
    #db = DBManager("carlos", "curtis", True)
    #xd = displayMainWindow(0, db)

####################################################################################################################################
## FIN :)
####################################################################################################################################
