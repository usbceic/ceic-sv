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
        UIpath = join(join(current, "qt"), "ui")              # Declara imagen para la plantilla UI
        stylesPath = join(join(current, "qt"), "stylesheet")  # Declarar path para los qss
        break

###################################################################################################################################################################################
## MODÚLOS:
###################################################################################################################################################################################

from PyQt4.uic import loadUiType         # Módulo con las herramientas parar trabajar los archivos .ui
from PyQt4.QtGui import QDialog          # Módulo con procedimientos de Qt
from PyQt4.QtCore import Qt, QMetaObject # Módulo con estructuras de Qt
from app_utilities import getStyle       # Módulo con los validadores para campos de texto

###################################################################################################################################################################################
## CONSTANTES:
###################################################################################################################################################################################

popUp0 = loadUiType(join(UIpath, "errorPopUp.ui"))[0]          # Cargar platilla para el errorPopup
popUp1 = loadUiType(join(UIpath, "warningPopUp.ui"))[0]        # Cargar platilla para el warningPopup
popUp2 = loadUiType(join(UIpath, "successPopUp.ui"))[0]        # Cargar platilla para el successPopup
popUp3 = loadUiType(join(UIpath, "confirmationPopUp.ui"))[0]   # Cargar platilla para el confirmationPopup
popUp4 = loadUiType(join(UIpath, "authorizationPopUp.ui"))[0]  # Cargar platilla para el authorizationPopup

###################################################################################################################################################################################
## DECLARACIÓN DEL POPUP PARA ERRORES
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

        # Configurar tema
        self.stylePath = join(stylesPath, "errorPopUp")
        self.setStyle(parent.theme)

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

    # Cambiar el tema de la interfáz
    def setStyle(self, theme):
        style = getStyle(join(self.stylePath, theme))
        if style != None:
            self.setStyleSheet(style)

    # Acción al presionar el botón de continuar
    def on_dpbutton0_pressed(self):
        if self.click():
            self.accept()

###################################################################################################################################################################################
## DECLARACIÓN DEL POPUP PARA ALERTAS
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

        # Configurar tema
        self.stylePath = join(stylesPath, "warningPopUp")
        self.setStyle(parent.theme)

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

    # Cambiar el tema de la interfáz
    def setStyle(self, theme):
        style = getStyle(join(self.stylePath, theme))
        if style != None:
            self.setStyleSheet(style)

    # Acción al presionar el botón de continuar
    def on_dpbutton0_pressed(self):
        if self.click():
            self.accept()

###################################################################################################################################################################################
## DECLARACIÓN DEL POPUP PARA OPERACIONES EXITOSAS
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

        # Configurar tema
        self.stylePath = join(stylesPath, "successPopUp")
        self.setStyle(parent.theme)

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

    # Cambiar el tema de la interfáz
    def setStyle(self, theme):
        style = getStyle(join(self.stylePath, theme))
        if style != None:
            self.setStyleSheet(style)

    # Acción al presionar el botón de continuar
    def on_dpbutton0_pressed(self):
        if self.click():
            self.accept()

###################################################################################################################################################################################
## DECLARACIÓN DEL POPUP PARA CONFIRMACIONES
###################################################################################################################################################################################

class confirmationPopUp(QDialog, popUp3):
    #==============================================================================================================================================================================
    # CONSTRUCTOR DE LA CLASE
    #==============================================================================================================================================================================
    def __init__(self, message=None, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # INICIAR Y CONFIGURAR EL POPUP
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Crear y configurar los objetos del ui
        super(confirmationPopUp, self).__init__(parent)
        self.setupUi(self)

        # Configurar mensaje del popUp
        if message != None: self.dtitle0.setText(message)

        # Valores por defecto de la variable a retornar
        self.confirmation = False

        # Configurar resolucion del popUp
        self.setMinimumSize(self.sizeHint())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        # Configurar tema
        self.stylePath = join(stylesPath, "confirmationPopUp")
        self.setStyle(parent.theme)

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

    # Cambiar el tema de la interfáz
    def setStyle(self, theme):
        style = getStyle(join(self.stylePath, theme))
        if style != None:
            self.setStyleSheet(style)

    # Función para retornar el valor de la confirmacíón
    def getValue(self):
        return self.confirmation

    # Acción al presionar el botón de continuar
    def on_dpbutton0_pressed(self):
        if self.click():
            self.confirmation = True
            self.accept()

    # Acción al presionar el botón de cancelar
    def on_dpbutton1_pressed(self):
        if self.click():
            self.accept()

###################################################################################################################################################################################
## DECLARACIÓN DEL POPUP PARA AUTORIZACIONES DE ADMINISTRADOR
###################################################################################################################################################################################

class authorizationPopUp(QDialog, popUp4):
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

        # Valores por defecto de las variables a retornar
        self.value0, self.value1 = None, None

        # Configurar resolucion del popUp
        self.setMinimumSize(self.sizeHint())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        # Configurar tema
        self.stylePath = join(stylesPath, "authorizationPopUp")
        self.setStyle(parent.theme)

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

    # Cambiar el tema de la interfáz
    def setStyle(self, theme):
        style = getStyle(join(self.stylePath, theme))
        if style != None:
            self.setStyleSheet(style)

    # Función para retornar los valores de los lineEdit
    def getValues(self):
        return self.value0, self.value1

    # Acción al presionar el botón de continuar
    def on_dpbutton0_pressed(self):
        if self.click():
            self.value0 = self.dlineE0.text()
            self.value1 = self.dlineE1.text()
            self.accept()

    # Acción al presionar el botón de cancelar
    def on_dpbutton1_pressed(self):
        if self.click():
            self.accept()

###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################