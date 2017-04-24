# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación de los popUp para toda la interfaz de CEIC Suite

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com

###################################################################################################################################################################################
## PATH:
###################################################################################################################################################################################

from sys import path                        # Importación del path del sistema
from os.path import join, basename          # Importación de funciones para manipular paths con el formato del sistema

# Para cada path en el path del sistema para la aplicación
for current in path:
    if basename(current) == "interface":
        UIpath = join(join(current, "qt"), "ui") # Declara imagen para la plantilla UI
        break

###################################################################################################################################################################################
## MODÚLOS:
###################################################################################################################################################################################

# Módulo con las herramientas parar trabajar los archivos .ui
from PyQt4.uic import loadUiType

# Módulo con procedimientos de Qt
from PyQt4.QtGui import QDialog

# Módulo con estructuras de Qt
from PyQt4.QtCore import Qt, QMetaObject

###################################################################################################################################################################################
## CONSTANTES:
###################################################################################################################################################################################

popUp0 = loadUiType(join(UIpath, "errorPopUp.ui"))[0]          # Cargar platilla para el errorPopup
popUp1 = loadUiType(join(UIpath, "warningPopUp.ui"))[0]        # Cargar platilla para el warningPopup
popUp2 = loadUiType(join(UIpath, "successPopUp.ui"))[0]        # Cargar platilla para el successPopup
popUp3 = loadUiType(join(UIpath, "authorizationPopUp.ui"))[0]  # Cargar platilla para el authorizationPopup

###################################################################################################################################################################################
## DECLARACION DEL POPUPS PARA ERRORES
###################################################################################################################################################################################

class errorPopUp(QDialog, popUp0):
    #==============================================================================================================================================================================
    # CONSTRUCTOR DE LA CLASE
    #==============================================================================================================================================================================
    def __init__(self, message=None, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # INICIAR Y CONFIGURAR EL POPUP
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Crear y configurar los objetos del ui
        super(errorPopUp, self).__init__(parent)
        self.setupUi(self)

        # Configurar mensaje del popUp
        if message != None: self.dtitle0.setText(message)

        # Configurar resolucion del popUp
        self.setMinimumSize(self.sizeHint())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        # Variable de control para saber cuando se hcae click sobre un botón
        self.clicked = False

        # Conectar los eventos mediante los nombres de los métodos
        QMetaObject.connectSlotsByName(self)

    #==============================================================================================================================================================================
    # MÉTODOS DE LA CLASE
    #==============================================================================================================================================================================

    # Definición de click sobre un QPushButton
    def click(self):
        if self.clicked:
            self.clicked = False
            return True
        else:
            self.clicked = True
            return False

    # Acción al presionar el botón de continuar
    def on_dpbutton0_pressed(self):
        if self.click():
            self.accept()

###################################################################################################################################################################################
## DECLARACION DEL POPUPS PARA ALERTAS
###################################################################################################################################################################################

class warningPopUp(QDialog, popUp1):
    #==============================================================================================================================================================================
    # CONSTRUCTOR DE LA CLASE
    #==============================================================================================================================================================================
    def __init__(self, message=None, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # INICIAR Y CONFIGURAR EL POPUP
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Crear y configurar los objetos del ui
        super(warningPopUp, self).__init__(parent)
        self.setupUi(self)

        # Configurar mensaje del popUp
        if message != None: self.dtitle0.setText(message)

        # Configurar resolucion del popUp
        self.setMinimumSize(self.sizeHint())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        # Variable de control para saber cuando se hcae click sobre un botón
        self.clicked = False

        # Conectar los eventos mediante los nombres de los métodos
        QMetaObject.connectSlotsByName(self)

    #==============================================================================================================================================================================
    # MÉTODOS DE LA CLASE
    #==============================================================================================================================================================================

    # Definición de click sobre un QPushButton
    def click(self):
        if self.clicked:
            self.clicked = False
            return True
        else:
            self.clicked = True
            return False

    # Acción al presionar el botón de continuar
    def on_dpbutton0_pressed(self):
        if self.click():
            self.accept()

###################################################################################################################################################################################
## DECLARACION DEL POPUPS PARA OPERACIONES EXITOSAS
###################################################################################################################################################################################

class successPopUp(QDialog, popUp2):
    #==============================================================================================================================================================================
    # CONSTRUCTOR DE LA CLASE
    #==============================================================================================================================================================================
    def __init__(self, message=None, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # INICIAR Y CONFIGURAR EL POPUP
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Crear y configurar los objetos del ui
        super(successPopUp, self).__init__(parent)
        self.setupUi(self)

        # Configurar mensaje del popUp
        if message != None: self.dtitle0.setText(message)

        # Configurar resolucion del popUp
        self.setMinimumSize(self.sizeHint())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        # Variable de control para saber cuando se hcae click sobre un botón
        self.clicked = False

        # Conectar los eventos mediante los nombres de los métodos
        QMetaObject.connectSlotsByName(self)

    #==============================================================================================================================================================================
    # MÉTODOS DE LA CLASE
    #==============================================================================================================================================================================

    # Definición de click sobre un QPushButton
    def click(self):
        if self.clicked:
            self.clicked = False
            return True
        else:
            self.clicked = True
            return False

    # Acción al presionar el botón de continuar
    def on_dpbutton0_pressed(self):
        if self.click():
            self.accept()

###################################################################################################################################################################################
## DECLARACION DEL POPUPS PARA AUTORIZACIONES DE ADMINISTRADOR
###################################################################################################################################################################################

class authorizationPopUp(QDialog, popUp3):
    #==============================================================================================================================================================================
    # CONSTRUCTOR DE LA CLASE
    #==============================================================================================================================================================================

    def __init__(self, message=None, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # INICIAR Y CONFIGURAR EL POPUP
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Crear y configurar los objetos del ui
        super(authorizationPopUp, self).__init__(parent)
        self.setupUi(self)

        # Configurar resolucion del popUp
        self.setMinimumSize(self.sizeHint())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        # Variable de control para saber cuando se hcae click sobre un botón
        self.clicked = False

        # Conectar los eventos mediante los nombres de los métodos
        QMetaObject.connectSlotsByName(self)

    #==============================================================================================================================================================================
    # MÉTODOS DE LA CLASE
    #==============================================================================================================================================================================

    # Definición de click sobre un QPushButton
    def click(self):
        if self.clicked:
            self.clicked = False
            return True
        else:
            self.clicked = True
            return False

    # Función para retornar los valores de los lineEdit
    def getValues(self):
        return self.dlineE0.text(), self.dlineE1.text()

    # Acción al presionar el botón de continuar
    def on_dpbutton0_pressed(self):
        if self.click():
            self.accept()

    # Acción al presionar el botón de cancelar
    def on_dpbutton1_pressed(self):
        if self.click():
            self.accept()

###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################