# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación de los popUp para toda la interfaz de CEIC Suite

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Christian Oliveros, 01christianol01@gmail.com
# Pablo Betancourt, pablodbc30@gmail.com

###################################################################################################################################################################################
## MODÚLOS:
###################################################################################################################################################################################

# Importación de la función para obtener el path actual
from os import getcwd

# Importación de función para unir paths con el formato del sistema
from os.path import join

# Módulo con las herramientas parar trabajar los archivos .ui
from PyQt4.uic import loadUiType

# Módulo con procedimientos de Qt
from PyQt4.QtGui import QDialog

# Módulo con estructuras de Qt
from PyQt4.QtCore import Qt, QMetaObject

###################################################################################################################################################################################
## CONSTANTES:
###################################################################################################################################################################################

UIpath = join(getcwd(), "interface/qt/ui/")             # Path para las plantillas
popUp0 = loadUiType(UIpath+"errorPopUp.ui")[0]          # Cargar platilla para el errorPopup
popUp1 = loadUiType(UIpath+"successPopUp.ui")[0]        # Cargar platilla para el successPopup
popUp2 = loadUiType(UIpath+"authorizationPopUp.ui")[0]  # Cargar platilla para el authorizationPopup

###################################################################################################################################################################################
## DECLARACION DE LOS POPUPS
###################################################################################################################################################################################

# PopUp para errores
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
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint)

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

# PopUp para operaciones exitosas
class successPopUp(QDialog, popUp1):
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
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint)

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

# PopUp para autorizaciones de administrador
class authorizationPopUp(QDialog, popUp2):
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
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint)

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
## FIN :)
###################################################################################################################################################################################