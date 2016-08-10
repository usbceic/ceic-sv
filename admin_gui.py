#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#####################################################################################
## DESCRIPCIÓN:
#####################################################################################

# Modúlo con la implementación de la clase encargada de la interfaz gráfica.

#####################################################################################
## AUTORES:
#####################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Christian Oliveros, 01christianol01@gmail.com
# José Acevedo, joseluisacevedo1995@gmail.com
# David Cabeza, cabezadavide@gmail.com

#####################################################################################
## MODÚLOS:
#####################################################################################

import gui_rc

from PyQt4.uic import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#import sales

#####################################################################################
## IMPLEMENTACIÓN DE LA INTERFAZ GRÁFICA:
#####################################################################################

# Cargar interfaz .ui creada con qt designer:
form_class = loadUiType("qt/ui/admin_gui.ui")[0]

#clientList = ["24464334", "24464335", "24464336", "10382827", "28073981", "6331396"]

class sistema_window(QMainWindow, form_class, QWidget):
    def __init__(self, parent=None):

        # Se inicia y configura la interfaz
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        #self.stackedWidget = QStackedWidget()

        #Configuración de la barra de búsqueda de cliente por CI
        #self.LEmodel = QStringListModel()
        #self.LEmodel.setStringList(clientList)

        #self.ciCompleter = QCompleter()
        #self.ciCompleter.setModel(self.LEmodel)
        #self.ciLE.setValidator(QIntValidator(0, 100000000))
        #self.paymentAmountLE.setValidator(QIntValidator(0, 100000000))

        #self.ciLE.setCompleter(self.ciCompleter)

        # Se connectan los botones entre otras cosas con algunos de los métodos definidos a continuación
        QMetaObject.connectSlotsByName(self)

    def selectPopular(self, n):
        self.selectProductLE.setText(unicode(str(n), "utf-8"))

    def on_popularItemBn0_pressed(self):
        self.selectPopular(0)

    def on_popularItemBn1_pressed(self):
        self.selectPopular(1)

    def on_popularItemBn2_pressed(self):
        self.selectPopular(2)

    def on_popularItemBn3_pressed(self):
        self.selectPopular(3)

    def on_popularItemBn4_pressed(self):
        self.selectPopular(4)

    def on_popularItemBn5_pressed(self):
        self.selectPopular(5)

    def on_popularItemBn6_pressed(self):
        self.selectPopular(6)

    def on_popularItemBn7_pressed(self):
        self.selectPopular(7)

    def on_popularItemBn8_pressed(self):
        self.selectPopular(8)

    def on_popularItemBn9_pressed(self):
        self.selectPopular(9)



