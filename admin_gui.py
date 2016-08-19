#!/usr/bin/env python
# -*- encoding: utf-8 -*-

####################################################################################################################################
## DESCRIPCIÓN:
####################################################################################################################################

# Modúlo con la implementación de la clase encargada de la interfaz gráfica.

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

import gui_rc                   # Módulo que contiene los recursos de la interfaz
from PyQt4.uic import *         # Módulo con las herramientas parar tranajar los archivos .ui
from PyQt4.QtCore import *      # Módulo con procedimientos de Qt
from PyQt4.QtGui import *       # Modulo con estructuras de Qt

####################################################################################################################################
## CONSTANTES:
####################################################################################################################################

# Paths
UIpath = "qt/ui/"
stylePath = "qt/stylesheet/"

# UI
MainUI = "material.ui"

# Styles
styles = ["black.css", "default.css", "fuchsia.css", "green.css", "orange.css", "purple.css", "red.css", "yellow.css"]

# Interfaz .ui creada con qt designer
form_class = loadUiType(UIpath+MainUI)[0]

####################################################################################################################################
## PROCEDIMIENTOS:
####################################################################################################################################

# Devuelve un string con el stylesheet especificado por el parametro name
def getStyle(name):
    file = open(stylePath+name, "r")
    style = file.read()
    file.close()
    return style

####################################################################################################################################
# VARIABLES:
####################################################################################################################################

# Ejemplo de ista de cédulas de clientes
clientList = ["513264", "28436485", "32564336", "105746567", "280765423", "670124583"]

####################################################################################################################################
## MANEJADOR DE LA INTERFAZ GRÁFICA:
####################################################################################################################################

class sistema_window(QMainWindow, form_class, QWidget):
    def __init__(self, parent=None):
        # Se inicia y configura la interfaz
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        #Configuración de la barra de búsqueda de cliente por CI
        self.LEmodel = QStringListModel()
        self.LEmodel.setStringList(clientList)
        self.ciCompleter = QCompleter()
        self.ciCompleter.setModel(self.LEmodel)
        self.lineE17.setValidator(QIntValidator(0, 100000000))
        self.lineE17.setCompleter(self.ciCompleter)

        # Se connectan los botones entre otras cosas con algunos de los métodos definidos a continuación
        QMetaObject.connectSlotsByName(self)

        # Variable de control para los QPushButton
        self.clicked = False

    #-------------------------------------------------------------------------------------------------------------------------------
    # Métodos de la clase
    #-------------------------------------------------------------------------------------------------------------------------------

    # Definición de click sobre un QPushButton
    def click(self):
        if self.clicked:
            self.clicked = False
            return True
        else:
            self.clicked = True
            return False

    # Cambiar página de un QStackedWidget
    def setPage(self, stacked, index):
        if self.click(): stacked.setCurrentIndex(index)

    # Seleccionar un item de las listas Top 10 y Nuevo
    def selectItem(self, n):
        if self.click(): self.lineE23.setText(str(n))

    # Cambiar el tema de la interfáz
    def setStyle(self, name):
        if self.click(): self.setStyleSheet(getStyle(name))

    #-------------------------------------------------------------------------------------------------------------------------------
    # Configuración de los botones para cambio de página de los stacked:
    #-------------------------------------------------------------------------------------------------------------------------------

    def on_home_pressed(self): self.setPage(self.MainStacked, 0)
    def on_sales_pressed(self): self.setPage(self.MainStacked, 1)
    def on_inventory_pressed(self): self.setPage(self.MainStacked, 2)
    def on_querys_pressed(self): self.setPage(self.MainStacked, 3)
    def on_clients_pressed(self): self.setPage(self.MainStacked, 4)
    def on_users_pressed(self): self.setPage(self.MainStacked, 5)
    def on_configure_pressed(self): self.setPage(self.MainStacked, 6)

    def on_arrow0_pressed(self): self.setPage(self.subStacked3, 1)
    def on_arrow1_pressed(self): self.setPage(self.subStacked3, 1)
    def on_arrow2_pressed(self): self.setPage(self.subStacked3, 0)
    def on_arrow3_pressed(self): self.setPage(self.subStacked3, 0)

    def on_arrow4_pressed(self): self.setPage(self.subStacked4, 1)
    def on_arrow5_pressed(self): self.setPage(self.subStacked4, 1)
    def on_arrow6_pressed(self): self.setPage(self.subStacked4, 0)
    def on_arrow7_pressed(self): self.setPage(self.subStacked4, 0)

    def on_arrow8_pressed(self): self.setPage(self.subStacked5, 2)
    def on_arrow9_pressed(self): self.setPage(self.subStacked5, 1)
    def on_arrow10_pressed(self): self.setPage(self.subStacked5, 0)
    def on_arrow11_pressed(self): self.setPage(self.subStacked5, 2)
    def on_arrow12_pressed(self): self.setPage(self.subStacked5, 1)
    def on_arrow13_pressed(self): self.setPage(self.subStacked5, 0)

    def on_arrow14_pressed(self): self.setPage(self.subStacked6, 1)
    def on_arrow15_pressed(self): self.setPage(self.subStacked6, 1)
    def on_arrow16_pressed(self): self.setPage(self.subStacked6, 0)
    def on_arrow17_pressed(self): self.setPage(self.subStacked6, 0)

    def on_arrow18_pressed(self): self.setPage(self.subStacked7, 3)
    def on_arrow19_pressed(self): self.setPage(self.subStacked7, 1)
    def on_arrow20_pressed(self): self.setPage(self.subStacked7, 0)
    def on_arrow21_pressed(self): self.setPage(self.subStacked7, 2)
    def on_arrow22_pressed(self): self.setPage(self.subStacked7, 1)
    def on_arrow23_pressed(self): self.setPage(self.subStacked7, 3)
    def on_arrow24_pressed(self): self.setPage(self.subStacked7, 2)
    def on_arrow25_pressed(self): self.setPage(self.subStacked7, 0)

    def on_arrow26_pressed(self): self.setPage(self.subStacked8, 2)
    def on_arrow27_pressed(self): self.setPage(self.subStacked8, 1)
    def on_arrow28_pressed(self): self.setPage(self.subStacked8, 0)
    def on_arrow29_pressed(self): self.setPage(self.subStacked8, 2)
    def on_arrow30_pressed(self): self.setPage(self.subStacked8, 1)
    def on_arrow31_pressed(self): self.setPage(self.subStacked8, 0)

    def on_arrow32_pressed(self): self.setPage(self.subStacked9, 1)
    def on_arrow33_pressed(self): self.setPage(self.subStacked9, 1)
    def on_arrow34_pressed(self): self.setPage(self.subStacked9, 0)
    def on_arrow35_pressed(self): self.setPage(self.subStacked9, 0)

    def on_arrow36_pressed(self): self.setPage(self.subStacked10, 2)
    def on_arrow37_pressed(self): self.setPage(self.subStacked10, 1)
    def on_arrow38_pressed(self): self.setPage(self.subStacked10, 0)
    def on_arrow39_pressed(self): self.setPage(self.subStacked10, 2)
    def on_arrow40_pressed(self): self.setPage(self.subStacked10, 1)
    def on_arrow41_pressed(self): self.setPage(self.subStacked10, 0)

    def on_arrow42_pressed(self): self.setPage(self.subStacked11, 2)
    def on_arrow43_pressed(self): self.setPage(self.subStacked11, 1)
    def on_arrow44_pressed(self): self.setPage(self.subStacked11, 0)
    def on_arrow45_pressed(self): self.setPage(self.subStacked11, 2)
    def on_arrow46_pressed(self): self.setPage(self.subStacked11, 1)
    def on_arrow47_pressed(self): self.setPage(self.subStacked11, 0)

    #-------------------------------------------------------------------------------------------------------------------------------
    # Configuración de los botones de las listas de productos Top 10 y Nuevo:
    #-------------------------------------------------------------------------------------------------------------------------------

    def on_popularItem0_pressed(self): self.selectItem(0)
    def on_popularItem1_pressed(self): self.selectItem(1)
    def on_popularItem2_pressed(self): self.selectItem(2)
    def on_popularItem3_pressed(self): self.selectItem(3)
    def on_popularItem4_pressed(self): self.selectItem(4)
    def on_popularItem5_pressed(self): self.selectItem(5)
    def on_popularItem6_pressed(self): self.selectItem(6)
    def on_popularItem7_pressed(self): self.selectItem(7)
    def on_popularItem8_pressed(self): self.selectItem(8)
    def on_popularItem9_pressed(self): self.selectItem(9)

    def on_newItem0_pressed(self): self.selectItem(0)
    def on_newItem1_pressed(self): self.selectItem(1)
    def on_newItem2_pressed(self): self.selectItem(2)
    def on_newItem3_pressed(self): self.selectItem(3)
    def on_newItem4_pressed(self): self.selectItem(4)
    def on_newItem5_pressed(self): self.selectItem(5)
    def on_newItem6_pressed(self): self.selectItem(6)
    def on_newItem7_pressed(self): self.selectItem(7)
    def on_newItem8_pressed(self): self.selectItem(8)
    def on_newItem9_pressed(self): self.selectItem(9)

    #-------------------------------------------------------------------------------------------------------------------------------
    # Configuración de los botones de cambio de color de la interfáz
    #-------------------------------------------------------------------------------------------------------------------------------

    def on_blackGUI_pressed(self): self.setStyle(styles[0])
    def on_blueGUI_pressed(self): self.setStyle(styles[1])
    def on_fuchsiaGUI_pressed(self): self.setStyle(styles[2])
    def on_greenGUI_pressed(self): self.setStyle(styles[3])
    def on_orangeGUI_pressed(self): self.setStyle(styles[4])
    def on_purpleGUI_pressed(self): self.setStyle(styles[5])
    def on_redGUI_pressed(self): self.setStyle(styles[6])
    def on_yellowGUI_pressed(self): self.setStyle(styles[7])

    #-------------------------------------------------------------------------------------------------------------------------------







