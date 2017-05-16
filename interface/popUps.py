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

from PyQt4.uic import loadUiType                           # Módulo con las herramientas parar trabajar los archivos .ui
from PyQt4.QtGui import QDialog, QLabel                    # Módulo con procedimientos de Qt
from PyQt4.QtCore import Qt, QMetaObject                   # Módulo con estructuras de Qt
from app_utilities import getStyle, dateTimeFormat, dateFormat, timeFormat # Módulo con funciones útiles

###################################################################################################################################################################################
## CONSTANTES:
###################################################################################################################################################################################

popUp0 = loadUiType(join(UIpath, "errorPopUp.ui"))[0]          # Cargar platilla para el errorPopup
popUp1 = loadUiType(join(UIpath, "warningPopUp.ui"))[0]        # Cargar platilla para el warningPopup
popUp2 = loadUiType(join(UIpath, "successPopUp.ui"))[0]        # Cargar platilla para el successPopup
popUp3 = loadUiType(join(UIpath, "confirmationPopUp.ui"))[0]   # Cargar platilla para el confirmationPopup
popUp4 = loadUiType(join(UIpath, "authorizationPopUp.ui"))[0]  # Cargar platilla para el authorizationPopup
popUp5 = loadUiType(join(UIpath, "detailsPopUp.ui"))[0]        # Cargar platilla para el detailsPopup
popUp6 = loadUiType(join(UIpath, "especialPopUp0.ui"))[0]      # Cargar platilla para el detailsPopup2

# Flags para los elementos del marco de la ventana
dialogFlags = (Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint) & ~Qt.WindowMaximizeButtonHint

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
        self.setFixedSize(self.sizeHint())
        self.setWindowFlags(dialogFlags)

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
        self.setFixedSize(self.sizeHint())
        self.setWindowFlags(dialogFlags)

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
        self.setFixedSize(self.sizeHint())
        self.setWindowFlags(dialogFlags)

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
        self.setFixedSize(self.sizeHint())
        self.setWindowFlags(dialogFlags)

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
        #self.setFixedSize(self.sizeHint())
        self.setWindowFlags(dialogFlags)

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
## DECLARACIÓN DEL POPUP PARA MOSTRAR INFORMACIÓN DETALLADA
###################################################################################################################################################################################

class detailsPopUp(QDialog, popUp5):
    #==============================================================================================================================================================================
    # CONSTRUCTOR DE LA CLASE
    #==============================================================================================================================================================================
    def __init__(self, details, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # INICIAR Y CONFIGURAR EL POPUP
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Crear y configurar los objetos del ui
        super(detailsPopUp, self).__init__(parent)
        self.setupUi(self)

        # Configurar mensaje del popUp
        self.loadDetails(details)

        # Configurar resolucion del popUp
        self.setFixedSize(self.sizeHint())
        self.setWindowFlags(dialogFlags)

        # Configurar tema
        self.stylePath = join(stylesPath, "detailsPopUp")
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

    # Cargar la información que se mostrará en el popUp
    def loadDetails(self, details):
        for item in details:
            title = QLabel(str(item[0]))
            title.setStyleSheet("font-weight: 600;")
            content = QLabel(str(item[1]))
            self.detailsLayout.addRow(title, content)

    # Acción al presionar el botón de continuar
    def on_dpbutton0_pressed(self):
        if self.click():
            self.accept()

###################################################################################################################################################################################
## DECLARACIÓN DEL POPUP PARA MOSTRAR INFORMACIÓN DETALLADA PARA CLIENTES ENDEUDADOS
###################################################################################################################################################################################

class especialPopUp0(QDialog, popUp6):
    #==============================================================================================================================================================================
    # CONSTRUCTOR DE LA CLASE
    #==============================================================================================================================================================================
    def __init__(self, ci, db, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # INICIAR Y CONFIGURAR EL POPUP
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Crear y configurar los objetos del ui
        super(especialPopUp0, self).__init__(parent)
        self.setupUi(self)

        # Guardar identificador de cliente y referencia al manejador de la base de datos
        self.ci = ci
        self.db = db

        # Inicializar variables
        self.mutex = False
        self.newIndex = False
        self.purchases = {}
        self.currentPurchase = "Compra #1"

        # Configurar mensaje del popUp
        self.loadDetails()

        # Configurar resolucion del popUp
        self.setFixedSize(self.sizeHint())
        self.setWindowFlags(dialogFlags)

        # Configurar tema
        self.stylePath = join(stylesPath, "especialPopUp0")
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

    # Cambio de texto en un QLineEdit
    def indexChanged(self):
        if self.newIndex:
            self.newIndex = False
            return True
        else:
            self.newIndex = True
            return False

    # Cambiar el tema de la interfáz
    def setStyle(self, theme):
        style = getStyle(join(self.stylePath, theme))
        if style != None:
            self.setStyleSheet(style)

    # Función para recargar la información de la vista de compras dependiendo de la selección
    def selectPurchase(self, purchase_id):
        resume = self.db.getPurchaseResume(purchase_id)  # Cargar datos
        self.dtext8.setText(resume["clerk"])             # Registrado por
        self.dtext9.setText(str(resume["total"]))        # Total
        self.dtext10.setText(dateFormat(resume["date"])) # Fecha
        self.dtext11.setText(timeFormat(resume["date"])) # Hora
        self.dtext12.setText(resume["products"])         # Productos
        self.dtext13.setText(resume["checkouts"])        # Pagos
        self.dtext14.setText(str(resume["debt"]))        # Deuda

    # Cargar la información que se mostrará en el popUp
    def loadDetails(self):

        # Cargar información básica del cliente
        client = self.db.getClients(self.ci)[0]
        self.dtext0.setText(str(client.ci))
        self.dtext1.setText(client.firstname)
        self.dtext2.setText(client.lastname)
        self.dtext3.setText(client.phone)
        self.dtext4.setText(client.email)
        self.dtext5.setText(str(client.balance))
        self.dtext6.setText(str(client.debt))
        self.dtext7.setText(dateTimeFormat(client.last_seen))

        # Cargar información de las compras con deudas del cliente
        purchases = self.db.getClientPurchasesWithDebt(self.ci)
        for i in range(1, len(purchases)+1):
            key = "Compra #" + str(i)
            self.cobox0.addItem(key)
            self.purchases[key] = purchases[i-1]
        self.selectPurchase(purchases[0])
        self.mutex = True

    # Acción al presionar el botón de continuar
    def on_dpbutton0_pressed(self):
        if self.click():
            self.accept()

    # ComboBox para seleccionar una compra
    def on_cobox0_currentIndexChanged(self):
        if self.indexChanged() and self.mutex:
            if self.currentPurchase != self.cobox0.currentText():
                self.currentPurchase = self.cobox0.currentText()
                purchase_id = self.purchases[self.currentPurchase]
                self.selectPurchase(purchase_id)

###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################