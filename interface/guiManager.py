# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación de la clase encargada de la interfaz gráfica.

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Pablo Betancourt, pablodbc30@gmail.com

###################################################################################################################################################################################
## PATH:
###################################################################################################################################################################################

from sys import path                         # Importación del path del sistema
from os.path import join, dirname, basename  # Importación de funciones para manipular paths con el formato del sistema

# Para cada path en el path del sistema para la aplicación
for current in path:
    if basename(current) == "interface":
        path.append(join(dirname(current), "modules"))                           # Agregar la carpeta modules al path
        path.append(join(dirname(current), "models"))                            # Agregar la carpeta models al path
        UIpath = join(join(current, "qt"), "ui")                                 # Declara imagen para la plantilla UI
        stylePath = join(join(join(current, "qt"), "stylesheet"), "MainWindow")  # Declarar path para los qss
        splashPath = join(join(current, "qt"), "images")                         # Declarar path para la imagen splash
        productPath = join(join(current, "images"), "inventory")
        break

###################################################################################################################################################################################
## MODÚLOS:
###################################################################################################################################################################################

# Módulo con funciones para manejo de archivos en alto nivel (en especifico para este caso... copiar)
from shutil import copy2

# Módulo que contiene el tipo de dato datetime para hcaer operaciones con fechas
from datetime import datetime

# Módulo manejador de la base de datos
from db_manager import dbManager

# Módulo con las clases para los popUp
from popUps import errorPopUp, warningPopUp, successPopUp, authorizationPopUp

# Módulo con los validadores para campos de texto
from validators import validatePhoneNumber, validateEmail

# Módulo con los validadores para campos de texto
from app_utilities import getStyle, naturalFormat

# Módulo que contiene los recursos de la interfaz
import gui_rc

# Módulo con las herramientas parar trabajar los archivos .ui
from PyQt4.uic import loadUiType

# Módulo con procedimientos de Qt
from PyQt4.QtCore import Qt, QMetaObject, pyqtSignal, QDir, QRegExp

# Módulo con estructuras de Qt
from PyQt4.QtGui import QMainWindow, QApplication, QStringListModel, QCompleter, QIntValidator, QHeaderView, QTableWidgetItem, QFileDialog, QIcon, QLineEdit, QLabel, QPushButton, QRegExpValidator

###################################################################################################################################################################################
## CONSTANTES:
###################################################################################################################################################################################

# UI
MainUI = "material.ui"

# Styles
styles = [
    "amber.qss",
    "black.qss",
    "blue-grey.qss",
    "blue.qss",
    "brown.qss",
    "cyan.qss",
    "deep-orange.qss",
    "deep-purple.qss",
    "green.qss",
    "grey.qss",
    "indigo.qss",
    "light-blue.qss",
    "light-green.qss",
    "lime.qss",
    "orange.qss",
    "pink.qss",
    "purple.qss",
    "red.qss",
    "teal.qss",
    "yellow.qss"
]

LEpopup = "LEpopup.qss"

# Interfaz .ui creada con qt designer
form_class = loadUiType(join(UIpath, MainUI))[0]

# Constante de primer inicio
A = True

###################################################################################################################################################################################
## MANEJADOR DE LA INTERFAZ GRÁFICA DE LA VENTANA PRINCIPAL:
###################################################################################################################################################################################

class guiManager(QMainWindow, form_class):
    closed = pyqtSignal() # Señal para saber si se cerró la ventana

    #==============================================================================================================================================================================
    # Constructor de la clase
    #==============================================================================================================================================================================
    def __init__(self, user, database, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # INICIAR Y CONFIGURAR LA CLASE Y EL MANEJADOR DE LA BASE DE DATOS
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        super(guiManager, self).__init__(parent)  # Construcción de la instancia
        self.setupUi(self)                        # Configuración de la plantilla
        self.user = user                          # Asignación del usuario que ejecuta la sesión
        self.db = database                        # Asignación del manejador de la base de datos
        self.openTurn(self.user)                  # Realizar apertura de turno del usuario en la base de datos

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # VARIABLES PARA FACILITAR EL USO DE VARIOS MÉTODOS DE LA CLASE
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        self.clicked = False                 # Variable de control para saber si un QPushbutton es presionado
        self.writing = False                 # Variable de control para saber si el texto de un QLineEdit ha cambiado
        self.newIndex = False                # Variable de control para saber si se está cambiando la el index de un comboBox
        self.indexMutex = False              # Semáforo especial para no actualizar dos veces al cambiar el index del comboBox de lotes
        self.lotMutex1 = False               # Semáforo para saber cuando cargar la info de un lote en los QlineEdit
        self.selectedRowChanged = False      # Variable de control para saber si se cambio la fila seleccionada de un QTableWidget
        self.currentLot = "0"                # Variable de control para el comboBox de seleccion de lotes
        self.currentLots = {}                # Diccionario para lotes de un producto consultado actualmente
        self.tempImage = ""                  # Imagen seleccionada
        self.selectedProductRemaining = {}   # Diccionario de cotas superiores para el spinBox de ventas
        self.selectedProductName = ""        # Nombre del producto seleccionado actualmente en la vista de ventas
        self.selectedProducts = {}           # Diccionario de productos en la factura en la vista de ventas
        self.dtFormat = "%d/%m/%y  %H:%M"    # Formato de fecha
        self.top10 = []                      # Lista de productos en Top 10
        self.new10 = []                      # Lista de productos en Nuevos
        self.legalTenders = []               # Lista para las denominaciones del sistema monetario

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # PREFERENCIAS DE USUARIO
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        self.theme = "blue.qss"

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS DE PROPOSITO GENERAL
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Barras de búsqueda por cédula:
        self.clientsSearch = [self.lineE17, self.lineE47, self.lineE52, self.lineE57]

        # Barras de búsqueda por nombre de producto:
        self.productSearch = [self.lineE23, self.lineE26, self.lineE33]

        # Barras de búsqueda por nombre de proveedor
        self.providersSearch = [self.lineE149, self.lineE34]

        # Barras de búsqueda por username de usuario
        self.usersSearch = [self.lineE62, self.lineE75]

        # Tablas
        self.tables = [self.table0, self.table1, self.table2, self.table3, self.table4, self.table5, self.table6, self.table7,
                        self.table8, self.table9, self.table10, self.table11, self.table12, self.table13, self.table14]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE CAJA
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de Caja
        self.cashLE0 = [self.lineE2, self.lineE3]
        self.cashLE1 = [self.lineE2, self.lineE3, self.lineE15]

        # Apartado de movimientos
        self.cashLE2 = [self.lineE8]
        self.cashLE3 = [self.lineE9]

        # Calculadora
        self.calc0 = [self.calcT0, self.calcT1, self.calcT2, self.calcT3, self.calcT4, self.calcT5, self.calcT6, self.calcT7, self.calcT8, self.calcT9, self.calcT10, self.calcT11, self.calcT12, self.calcT13, self.calcT14]

        self.calc1 = [self.calcLE0, self.calcLE1, self.calcLE2, self.calcLE3, self.calcLE4, self.calcLE5, self.calcLE6, self.calcLE7, self.calcLE8, self.calcLE9, self.calcLE10, self.calcLE11, self.calcLE12, self.calcLE13, self.calcLE14]

        # LineEdits para solo números
        self.cashON = [self.lineE8, self.lineE9]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE INVENTARIO
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de productos en inventario
        self.productsRO0 = [self.lineE26, self.lineE27, self.lineE28, self.lineE29, self.lineE30]
        self.productsRO1 = [self.lineE27, self.lineE28, self.lineE29, self.lineE30]
        self.productsRO2 = [self.lineE27, self.lineE28]
        self.productsRO3 = [self.lineE27, self.lineE28, self.lineE29]

        # Apartado de lotes en inventario
        self.lotsRO0 = [self.lineE33, self.lineE34, self.lineE35, self.lineE37, self.lineE38]
        self.lotsRO1 = [self.lineE34, self.lineE35, self.lineE37, self.lineE38]
        self.lotsRO2 = [self.lineE34, self.lineE35, self.lineE37]
        self.lotsRO3 = [self.lineE38]

        # Tablas de productos
        self.productTables = [self.table1, self.table2, self.table3]

        # LineEdits para solo números
        self.productsON0 = [self.lineE27]
        self.productsON1 = [self.lineE28]
        self.lotsON = [self.lineE35, self.lineE37, self.lineE38]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE PROVEEDORES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de proveedores
        self.providersLE0 = [self.lineE146, self.lineE147, self.lineE148]
        self.providersLE1 = [self.lineE149, self.lineE150, self.lineE151]
        self.providersLE2 = [self.lineE150, self.lineE151]
        self.providersTE0 = [self.textE1, self.textE2]
        self.providersTE1 = [self.textE3, self.textE4]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE CLIENTES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de clientes
        self.clientsLE0 = [self.lineE52, self.lineE53, self.lineE54, self.lineE55, self.lineE56]
        self.clientsLE1 = [self.lineE57, self.lineE58, self.lineE59, self.lineE60, self.lineE61]
        self.clientsLE2 = [self.lineE58, self.lineE59, self.lineE60, self.lineE61]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE RECARGAS
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de cliente
        self.transfersLE0 = [self.lineE47, self.lineE48, self.lineE49, self.lineE50, self.lineE51]
        self.transfersLE1 = [self.lineE48, self.lineE49, self.lineE50]
        self.transfersLE2 = [self.lineE51, self.lineE156, self.lineE157]
        self.transfersLE3 = [self.lineE158]

        # LineEdits para solo números
        self.transfersON = [self.lineE51, self.lineE158]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE USUARIOS
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de usuarios
        self.usersLE0 = [self.lineE62, self.lineE63, self.lineE64, self.lineE65, self.lineE66]
        self.usersLE1 = [self.lineE69, self.lineE70, self.lineE71, self.lineE72, self.lineE73]
        self.usersLE2 = [self.lineE75, self.lineE76, self.lineE77, self.lineE78]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE VENTAS
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de producto seleccionado en ventas
        self.selectedProductLE0 = [self.lineE24, self.lineE25]
        self.selectedProductLE1 = [self.lineE23, self.lineE24, self.lineE25]

        # Apartado de cliente en ventas
        self.salesClientLE0 = [self.lineE18, self.lineE19, self.lineE20, self.lineE152]
        self.salesClientLE1 = [self.lineE17, self.lineE18, self.lineE19, self.lineE20, self.lineE152]

        # Apartado de pago en la vista de ventas
        self.salesCheckoutLE = [self.lineE21, self.lineE22, self.lineE152]

        # SpinLines en la vista de ventas
        self.spinBox = [self.spinLine0]

        # Apartado de productos NUevos y Top 10
        self.popularTexts = [self.text44, self.text45, self.text46, self.text47, self.text48, self.text49, self.text50, self.text51, self.text52, self.text53]
        self.newTexts     = [self.text54, self.text55, self.text56, self.text57, self.text58, self.text59, self.text60, self.text61, self.text62, self.text63]
        self.newItems     = [self.newItem0, self.newItem1, self.newItem2, self.newItem3, self.newItem4, self.newItem5, self.newItem6, self.newItem7, self.newItem8, self.newItem9]
        self.popularItems = [self.popularItem0, self.popularItem1, self.popularItem2, self.popularItem3, self.popularItem4, self.popularItem5, self.popularItem6, self.popularItem7, self.popularItem8, self.popularItem9]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE CONFIGURACIONES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de cambio de contraseña
        self.confLE0 = [self.lineE153, self.lineE154, self.lineE155]

        # Apartado de sistema monetario
        self.confLE1 = [self.lineE88]

        # LineEdits para solo números
        self.confON = [self.lineE88]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # CARGAR CONFIGURACIONES INICIALES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Se connectan los botones entre otras cosas con algunos de los métodos definidos a continuación
        QMetaObject.connectSlotsByName(self)

        # Aplicar configuraciones generales de la interfaz
        self.generalSetup()

        # Refrescar todos los elementos de la interfaz
        self.refresh()

    #==============================================================================================================================================================================
    # CONFIGURACIONES DE LA VENTANA
    #==============================================================================================================================================================================

    # Centrar la ventana
    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    # Fijar tamaño de la ventana
    def setSize(self):
        self.setFixedSize(self.width(), self.height())
        #self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

    #==============================================================================================================================================================================
    # CONFIGURACIÓN DE LAS PREFERENCIAS DE USUARIO
    #==============================================================================================================================================================================

    # Falta agregar

    #==============================================================================================================================================================================
    # MÉTODOS GENERALES MULTIPROPÓSITOS
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
    def textChanged(self):
        if self.writing:
            self.writing = False
            return True
        else:
            self.writing = True
            return False

    # Cambio de texto en un QLineEdit
    def indexChanged(self):
        if self.newIndex:
            self.newIndex = False
            return True
        else:
            self.newIndex = True
            return False

    # Cambio de texto en un QLineEdit
    def rowChanged(self):
        if self.selectedRowChanged:
            self.selectedRowChanged = False
            return True
        else:
            self.selectedRowChanged = True
            return False

    # Cambiar página de un QStackedWidget
    def setPage(self, stacked, index):
        stacked.setCurrentIndex(index)

    # Cambiar página de un QStackedWidget
    def changePage(self, stacked, move = -1):
        if self.click():
            if move == -1: stacked.setCurrentIndex((stacked.currentIndex()+stacked.count()-1)%stacked.count())
            if move == 1: stacked.setCurrentIndex((stacked.currentIndex()+1)%stacked.count())

    # Método para buscar en un LineEdit
    def setupSearchBar(self, listLE, itemsList, numValidator = False):
        LEmodel, LEcompleter = QStringListModel(), QCompleter()
        LEmodel.setStringList(itemsList)
        LEcompleter.setModel(LEmodel)
        LEcompleter.setCompletionMode(QCompleter.PopupCompletion)
        LEcompleter.setCaseSensitivity(Qt.CaseInsensitive)
        for lineE in listLE:
            if numValidator: lineE.setValidator(QIntValidator(0, 99999999))
            lineE.setCompleter(LEcompleter)

    # Método para configurar campos para ingresar cualquier cosa
    def setAnyCharacter(self, listAC):
        validator = QRegExpValidator(QRegExp('.*'))
        for item in listAC: item.setValidator(validator)

    # Método para configurar campos para solo ingresar números
    def setOnlyNumbers(self, listON):
        for item in listON: item.setValidator(QIntValidator(0, 9999999))

    # Método para configurar un spinLine
    def setupSpinLines(self, listSL):
        for spinL in listSL: spinL.setValidator(QIntValidator(0, 0))

    # Método para setear en 0 una lista spinLine
    def clearSpinLines(self, listSL):
        for spinL in listSL: spinL.setText("0")

    # Método para setear en 0 un spinLine
    def clearSpinLine(self, spinL):
        spinL.setText("0")

    # Obtener una lista con los nombres de todos los productos
    def getProductList(self, params, mode = 0):
        if mode == 0: params.update({"available" : None})
        elif mode == 1: params.update({"available" : True})
        else:  params.update({"available" : False})

        productsList = self.db.getProducts(**params)

        if len(params) == 3:
            productsNames = []
            for i in range(len(productsList)):
                productsNames += productsList[i]
            return sorted(productsNames)

        else:
            return sorted(productsList, key = lambda product: product[1])

    # Establecer un comboBox como de solo lectura
    def readOnlyCB(self, cbox, readOnly):
        if readOnly: cbox.setStyleSheet("border: 1px solid silver; background: #F5F5F5;")
        else: cbox.setStyleSheet("border: 1px solid #BDBDBD; background: #FFFFFF;")

    # Borrar contenido de una lista de PlainTextEdit:
    def clearCBs(self, listCB):
        for CB in listCB: CB.clear()

    # Borrar contenido de un ComboBox:
    def clearCB(self, cbox):
        cbox.clear()

    # Borrar contenido de un PlainTextEdit:
    def clearTE(self, textE):
        textE.setPlainText("")

    # Borrar contenido de una lista de PlainTextEdit:
    def clearTEs(self, listTE):
        for textE in listTE: textE.setPlainText("")

    # Borrar contenido de un LineEdit:
    def clearLE(self, lineE):
        lineE.setText("")

    # Borrar contenido de una lista de LineEdit:
    def clearLEs(self, listLE):
        for lineE in listLE: lineE.setText("")

    # Marcar en solo lectura uno o más LineEdit:
    def ReadOnlyLE(self, listLE, boolean):
        for lineE in listLE: lineE.setReadOnly(boolean)
        self.setStyle(self.theme)

    # Cambio de estado de los line edits en un apartado
    def changeRO(self, listaLE0, boolean = True, listaLE1 = []):
        self.ReadOnlyLE(listaLE0, boolean)
        self.ReadOnlyLE(listaLE1, not(boolean))

    # Aplicar configuración general de redimiensionamiento a una tabla
    def setupTable(self, table, column = 0):
        table.horizontalHeader().setResizeMode(column, QHeaderView.Stretch)

    # Aplicar configuración general de redimiensionamiento a una lista de tablas
    def setupTables(self, tables):
        for table in self.tables:
            self.setupTable(table)

    # Vaciar el contenido de cada tabla especificada en la lista "tables"
    def clearTables(self, tables):
        for i in range(len(tables)):
            for i in reversed(range(table.rowCount())):
                table.removeRow(i)

    # Vaciar el contenido de una tabla
    def clearTable(self, table):
        for i in reversed(range(table.rowCount())): table.removeRow(i)

    # Método para refrescar la interfaz
    def refresh(self):
        self.refreshSales()
        self.refreshProviders()
        self.refreshTransfers()
        self.refreshConfigurations()
        self.refreshCash()

        # Si el usuario tiene rango mayor a Colaborador
        if self.db.getUserPermissionMask(self.user) > 0:
            # Se establece la pagina de caja por defecto
            self.MainStacked.setCurrentIndex(0)
            self.MainTitle.setText("Caja")

        # Si el usuario es Colaborador
        else:
            # Si hay dia y periodo abierto:
            if self.db.isOpenPeriod() and self.db.isOpenDay():
                self.MainStacked.setCurrentIndex(1)
                self.MainTitle.setText("Ventas")

            # Si NO hay dia y periodo abierto:
            else:
                self.setPage(self.MainStacked, 4)
                self.MainTitle.setText("Préstamos")

        # Si el usuario tiene rango mayor a Vendedor
        if self.db.getUserPermissionMask(self.user) > 1:
            # Mostrar configuraciones del programa
            self.groupBox6.show()

        # Si el usuario es Colaborador o Vendedor
        else:
            # Ocultar configuraciones del programa
            self.groupBox6.hide()

    # Método para aplicar las configuraciones iniciales
    def generalSetup(self):
        # Centrar posición de la ventana
        self.center()

        # Establecer tamaño y ocultar botones de la ventana
        self.setSize()

        # Configurar los spin box
        if not self.rbutton7.isChecked():
            self.setOnlyNumbers(self.productsON0)
            self.setAnyCharacter(self.productsON1)

        else:
            self.setOnlyNumbers(self.productsON1)
            self.setAnyCharacter(self.productsON0)

        self.setOnlyNumbers(self.lotsON)
        self.setOnlyNumbers(self.confON)
        self.setOnlyNumbers(self.transfersON)
        self.setOnlyNumbers(self.cashON)
        self.setupSpinLines(self.spinBox)
        self.add0.setAutoRepeat(True)
        self.substract0.setAutoRepeat(True)

    # Método para abrir turno
    def openTurn(self, user):
        if self.db.isOpenDay() and self.db.isOpenPeriod():      # Verificar que haya un día y periodo abierto
            if self.db.isOpenTurn():                            # Verificar si ya hay un turno abierto
                clerk = self.db.getTurnStartAndEnd()[0].clerk   # Obtener usuario que dejo el turno abierto
                self.db.closeTurn(clerk)                        # Cerrar el turno del usuario
            self.db.startTurn(user)                             # Abrir turno del usuario en la base de datos

    #==============================================================================================================================================================================
    # BOTON PARA CERRAR SESIÓN
    #==============================================================================================================================================================================

    def on_userBn0_pressed(self):
        if self.click():
            if self.db.isOpenTurn():
                self.db.closeTurn(self.user)

    #==============================================================================================================================================================================
    # CAMBIO DE PÁGINA DE LOS STACKED
    #==============================================================================================================================================================================

    # Cambiar a la página principal
    def on_home_pressed(self):
        if self.click():
            # Si el usuario tiene rango mayor a Colaborador
            if self.db.getUserPermissionMask(self.user) > 0:
                self.setPage(self.MainStacked, 0)
                self.MainTitle.setText("Caja")

            # Si el usuario es Colaborador
            else:
                warningPopUp("No tiene permisos de acceso a esta vista", self).exec_()

     # Cambiar a la página de ventas
    def on_sales_pressed(self):
        if self.click():
            # Si hay dia y periodo abierto:
            if self.db.isOpenPeriod() and self.db.isOpenDay():
                self.setPage(self.MainStacked, 1)
                self.MainTitle.setText("Ventas")

            # Si no hay periodo abierto
            elif not self.db.isOpenPeriod():
                warningPopUp("Falta apertura de periodo", self).exec_()

            # Si no hay día abierto
            else:
                warningPopUp("Falta apertura de caja", self).exec_()

    # Cambiar a la página de inventario
    def on_inventory_pressed(self):
        if self.click():
            # Si el usuario tiene rango mayor a Colaborador
            if self.db.getUserPermissionMask(self.user) > 1:
                # Si hay dia y periodo abierto:
                if self.db.isOpenPeriod() and self.db.isOpenDay():
                    self.setPage(self.MainStacked, 2)
                    self.MainTitle.setText("Inventario")

                # Si no hay periodo abierto
                elif not self.db.isOpenPeriod():
                    warningPopUp("Falta apertura de periodo", self).exec_()

                # Si no hay día abierto
                else:
                    warningPopUp("Falta apertura de caja", self).exec_()

            # Si el usuario es Colaborador
            else:
                warningPopUp("No tiene permisos de acceso a esta vista", self).exec_()

    # Cambiar a la página de consultas
    def on_querys_pressed(self):
        if self.click():
            # Si el usuario tiene rango mayor a Colaborador
            if self.db.getUserPermissionMask(self.user) > 0:
                self.setPage(self.MainStacked, 3)
                self.MainTitle.setText("Consultas")

            # Si el usuario es Colaborador
            else:
                warningPopUp("No tiene permisos de acceso a esta vista", self).exec_()

    # Cambiar a la página de préstamos
    def on_loans_pressed(self):
        if self.click():
            self.setPage(self.MainStacked, 4)
            self.MainTitle.setText("Préstamos")

    # Cambiar a la página de libros
    def on_books_pressed(self):
        if self.click():
            # Si el usuario tiene rango mayor a Colaborador
            if self.db.getUserPermissionMask(self.user) > 0:
                self.setPage(self.MainStacked, 5)
                self.MainTitle.setText("Libros")

            # Si el usuario es Colaborador
            else:
                warningPopUp("No tiene permisos de acceso a esta vista", self).exec_()

    # Cambiar a la página de clientes
    def on_providers_pressed(self):
        if self.click():
            # Si el usuario tiene rango mayor a Colaborador
            if self.db.getUserPermissionMask(self.user) > 1:
                self.setPage(self.MainStacked, 6)
                self.MainTitle.setText("Proveedores")

            # Si el usuario es Colaborador
            else:
                warningPopUp("No tiene permisos de acceso a esta vista", self).exec_()

    # Cambiar a la página de clientes
    def on_clients_pressed(self):
        if self.click():
            # Si el usuario tiene rango mayor a Colaborador
            if self.db.getUserPermissionMask(self.user) > 0:
                self.setPage(self.MainStacked, 7)
                self.MainTitle.setText("Clientes")

            # Si el usuario es Colaborador
            else:
                warningPopUp("No tiene permisos de acceso a esta vista", self).exec_()

    # Cambiar a la página de clientes
    def on_transfer_pressed(self):
        if self.click():
            # Si el usuario tiene rango mayor a Colaborador
            if self.db.getUserPermissionMask(self.user) > 0:
                # Si hay dia y periodo abierto:
                if self.db.isOpenPeriod() and self.db.isOpenDay():
                    self.setPage(self.MainStacked, 8)
                    self.MainTitle.setText("Recargas de saldo")

                # Si no hay periodo abierto
                elif not self.db.isOpenPeriod():
                    warningPopUp("Falta apertura de periodo", self).exec_()

                # Si no hay día abierto
                else:
                    warningPopUp("Falta apertura de caja", self).exec_()

            # Si el usuario es Colaborador
            else:
                warningPopUp("No tiene permisos de acceso a esta vista", self).exec_()

    # Cambiar a la página de usuarios
    def on_users_pressed(self):
        if self.click():
            # Si el usuario tiene rango mayor a Vendedor
            if self.db.getUserPermissionMask(self.user) > 1:
                self.setPage(self.MainStacked, 9)
                self.MainTitle.setText("Usuarios")

            # Si el usuario es Colaborador o Vendedor
            else:
                warningPopUp("No tiene permisos de acceso a esta vista", self).exec_()

    # Cambiar a la página de configuraciones
    def on_configure_pressed(self):
        if self.click():
            self.setPage(self.MainStacked, 10)
            self.MainTitle.setText("Configuraciones")

    # Cambiar a la página de ayuda
    def on_help_pressed(self):
        if self.click():
            print(self.user)
            self.setPage(self.MainStacked, 11)
            self.MainTitle.setText("Ayuda")

    def on_arrow1_pressed(self): self.changePage(self.subStacked3)       # Cambiar la página del subStacked3 hacia la derecha
    def on_arrow3_pressed(self): self.changePage(self.subStacked4)       # Cambiar la página del subStacked4 hacia la derecha
    def on_arrow5_pressed(self): self.changePage(self.subStacked5)       # Cambiar la página del subStacked5 hacia la derecha
    def on_arrow7_pressed(self): self.changePage(self.subStacked6)       # Cambiar la página del subStacked6 hacia la derecha
    def on_arrow9_pressed(self): self.changePage(self.subStacked7)       # Cambiar la página del subStacked7 hacia la derecha
    def on_arrow11_pressed(self): self.changePage(self.subStacked8)      # Cambiar la página del subStacked8 hacia la derecha
    def on_arrow13_pressed(self): self.changePage(self.subStacked9)      # Cambiar la página del subStacked9 hacia la derecha
    def on_arrow15_pressed(self): self.changePage(self.subStacked10)     # Cambiar la página del subStacked10 hacia la derecha
    def on_arrow17_pressed(self): self.changePage(self.subStacked11)     # Cambiar la página del subStacked11 hacia la derecha
    def on_arrow19_pressed(self): self.changePage(self.subStacked12)     # Cambiar la página del subStacked12 hacia la derecha
    def on_arrow21_pressed(self): self.changePage(self.subStacked13)     # Cambiar la página del subStacked13 hacia la derecha
    def on_arrow23_pressed(self): self.changePage(self.subStacked14)     # Cambiar la página del subStacked14 hacia la derecha
    def on_arrow25_pressed(self): self.changePage(self.subStacked15)     # Cambiar la página del subStacked15 hacia la derecha
    def on_arrow27_pressed(self): self.changePage(self.subStacked16)     # Cambiar la página del subStacked16 hacia la derecha
    def on_arrow29_pressed(self): self.changePage(self.subStacked17)     # Cambiar la página del subStacked17 hacia la derecha
    def on_arrow31_pressed(self): self.changePage(self.subStacked18)     # Cambiar la página del subStacked18 hacia la derecha
    def on_arrow33_pressed(self): self.changePage(self.subStacked19)     # Cambiar la página del subStacked18 hacia la derecha

    def on_arrow0_pressed(self): self.changePage(self.subStacked3, 1)    # Cambiar la página del subStacked3 hacia la izquierda
    def on_arrow2_pressed(self): self.changePage(self.subStacked4, 1)    # Cambiar la página del subStacked4 hacia la izquierda
    def on_arrow4_pressed(self): self.changePage(self.subStacked5, 1)    # Cambiar la página del subStacked5 hacia la izquierda
    def on_arrow6_pressed(self): self.changePage(self.subStacked6, 1)    # Cambiar la página del subStacked6 hacia la izquierda
    def on_arrow8_pressed(self): self.changePage(self.subStacked7, 1)    # Cambiar la página del subStacked7 hacia la izquierda
    def on_arrow10_pressed(self): self.changePage(self.subStacked8, 1)   # Cambiar la página del subStacked8 hacia la izquierda
    def on_arrow12_pressed(self): self.changePage(self.subStacked9, 1)   # Cambiar la página del subStacked9 hacia la izquierda
    def on_arrow14_pressed(self): self.changePage(self.subStacked10, 1)  # Cambiar la página del subStacked10 hacia la izquierda
    def on_arrow16_pressed(self): self.changePage(self.subStacked11, 1)  # Cambiar la página del subStacked11 hacia la izquierda
    def on_arrow18_pressed(self): self.changePage(self.subStacked12, 1)  # Cambiar la página del subStacked12 hacia la izquierda
    def on_arrow20_pressed(self): self.changePage(self.subStacked13, 1)  # Cambiar la página del subStacked13 hacia la izquierda
    def on_arrow22_pressed(self): self.changePage(self.subStacked14, 1)  # Cambiar la página del subStacked14 hacia la izquierda
    def on_arrow24_pressed(self): self.changePage(self.subStacked15, 1)  # Cambiar la página del subStacked15 hacia la izquierda
    def on_arrow26_pressed(self): self.changePage(self.subStacked16, 1)  # Cambiar la página del subStacked16 hacia la izquierda
    def on_arrow28_pressed(self): self.changePage(self.subStacked17, 1)  # Cambiar la página del subStacked17 hacia la izquierda
    def on_arrow30_pressed(self): self.changePage(self.subStacked18, 1)  # Cambiar la página del subStacked18 hacia la izquierda
    def on_arrow32_pressed(self): self.changePage(self.subStacked19, 1)  # Cambiar la página del subStacked18 hacia la izquierda

    #==============================================================================================================================================================================
    # VISTA DE CAJA
    #==============================================================================================================================================================================
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para actualizar caja
    def refreshCash(self):
        if self.db.isOpenPeriod():
            self.setPage(self.subStacked2, 1)                           # Cambiar a la página para ver y cerrar un periodo
            period = self.db.getPeriodStartAndEnd()[0]                  # Obtener información del inicio del periodo
            name = period.description                                   # Obtener nombre del periodo
            startDate = period.recorded                                 # Obtener fecha de inicio del periodo
            cash, bank = self.db.getBalance(startDate)                  # Obtener dinero en efectivo y en banco ganado durante el periodo
            self.lineE10.setText(name)                                  # Actualizar campo de nombre del periodo
            self.lineE11.setText(startDate.strftime(self.dtFormat))     # Actualizar campo de fecha de inicio
            self.lineE13.setText(str(cash))                             # Actualizar campo de efectivo en periodo
            self.lineE14.setText(str(bank))                             # Actualizar campo de banco en periodo

            if self.db.isOpenDay():
                self.setPage(self.subStacked1, 1)                       # Cambiar a la página para ver y cerrar un dia
                day = self.db.getDayStartAndEnd()[0]                    # Obtener información del inicio del día
                name = day.description                                  # Obtener nombre del día
                startDate = day.recorded                                # Obtener fecha de inicio del día
                dayBank = self.db.getBalance(startDate)[1]              # Obtener dinero en efectivo y en banco ganado en la fecha
                self.lineE0.setText("Abierta")                          # Cambiar el campo de estado a Abierta
                self.lineE2.setText(str(cash))                          # Actualizar campo de efectivo
                self.lineE3.setText(str(dayBank))                       # Actualizar campo de banco

            else:
                self.lineE0.setText("Cerrada")                          # Cambiar el campo de estado a Cerrada
                self.setPage(self.subStacked1, 0)                       # Cambiar a la página para abrir un día
                self.clearLEs(self.cashLE0)                             # Limpiar los campos de caja

        else:
            self.setPage(self.subStacked2, 0)                           # Cambiar a la página para abrir un nuevo periodo
            self.clearLEs(self.cashLE1)                                 # Limpiar los campos de los apartados de periodo y caja

        self.clearLEs(self.calc1)                                       # Limpiar calculadora

    # Método para configurar la calculadora
    def updateCalc(self, legalTenders):
        for i in range(len(self.calc0)):
            if i < len(legalTenders):
                self.calc0[i].setText(naturalFormat(legalTenders[i]))
                self.calc1[i].setReadOnly(False)

            else:
                self.calc0[i].setText("0")
                self.calc1[i].setReadOnly(True)

        self.setOnlyNumbers(self.calc1)
        self.setStyle(self.theme)

    # Método para realizar la suma en la calculadora
    def executeCalc(self, legalTenders):
        total = 0.0
        for i in range(len(legalTenders)):
            if self.calc1[i].text() != "":
                total += float(self.calc1[i].text())*float(legalTenders[i])
        self.lineE79.setText(naturalFormat(total))

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Boton para limpiar calculadora
    def on_cancelpb24_pressed(self):
        if self.click():
            self.clearLEs(self.calc1)

    # Boton para abrir día
    def on_pbutton3_pressed(self):
        if self.click():
            if self.db.isOpenPeriod():
                description = self.cbox2.currentText()
                self.db.startDay(self.user, description = description)
                self.db.startTurn(self.user)
                self.refreshCash()

            elif not self.db.isOpenPeriod():
                warningPopUp("Falta apertura de periodo", self).exec_()

            else:
                warningPopUp("Debe especificar el efectivo para aperturar", self).exec_()

    # Boton para finalizar día
    def on_pbutton4_pressed(self):
        if self.click():
            description = self.cbox3.currentText()
            self.db.closeTurn(self.user)
            self.db.closeDay(self.user, description = description)
            self.refreshCash()

    # Boton para abrir periodo
    def on_pbutton5_pressed(self):
        if self.click():
            if self.lineE15.text() != "":
                description = self.lineE15.text()
                self.db.startPeriod(self.user, description=description)
                self.refreshCash()

    # Boton para finalizar periodo
    def on_pbutton6_pressed(self):
        if self.click():
            if not self.db.isOpenDay():
                self.db.closePeriod(self.user)
                self.refreshCash()

            else:
                warningPopUp("Debe cerrar caja primero", self).exec_()

    # Radio button de ingresos
    def on_rbutton0_pressed(self):
        if self.click():
            self.setPage(self.subStacked0, 0)
            self.clearLEs(self.cashLE2)

    # Radio button de egresos
    def on_rbutton1_pressed(self):
        if self.click():
            self.setPage(self.subStacked0, 1)
            self.clearLEs(self.cashLE3)

    # Boton para registrar un movimiento
    def on_pbutton1_pressed(self):
        if self.click():
            # Verificar que haya tanto un periodo como un día abierto
            if self.db.isOpenDay() and self.db.isOpenPeriod():
                # Modalidad para registrar ingresos
                if self.rbutton0.isChecked():
                    if self.lineE8.text() != "":
                        cash_balance = float(self.lineE8.text())
                        description  = self.cbox21.currentText()
                        if self.db.incomeOperation(self.user, cash_balance = cash_balance, description = description):
                            successPopUp(parent = self).exec_()

                        # Operación fallida
                        else:
                            errorPopUp("No se pudo realizar la operación", self).exec_()

                        # Limpiar
                        self.clearLEs(self.cashLE2)

                    else:
                        errorPopUp("Debe especificar el monto del ingreso", self).exec_()

                # Modalidad para registrar egresos
                else:
                    if self.lineE9.text() != "":
                        cash_balance = float(self.lineE9.text())
                        description  = self.cbox23.currentText()
                        if self.db.expenditureOperation(self.user, cash_balance = cash_balance, description = description):
                            successPopUp(parent = self).exec_()

                        # Operación fallida
                        else:
                            errorPopUp("No se pudo realizar la operación", self).exec_()

                        # Limpiar
                        self.clearLEs(self.cashLE3)

                    else:
                        errorPopUp("Debe especificar el monto del egreso", self).exec_()

            # Si no hay periodo abierto
            elif not self.db.isOpenPeriod():
                warningPopUp("Falta apertura de periodo", self).exec_()

            # Si no hay día abierto
            else:
                warningPopUp("Falta apertura de caja", self).exec_()

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CAMPOS DE TEXTO
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Campo 0 de la calculadora
    def on_calcLE0_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 1 de la calculadora
    def on_calcLE1_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 2 de la calculadora
    def on_calcLE2_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 3 de la calculadora
    def on_calcLE3_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 4 de la calculadora
    def on_calcLE4_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 5 de la calculadora
    def on_calcLE5_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 6 de la calculadora
    def on_calcLE6_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 7 de la calculadora
    def on_calcLE7_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 8 de la calculadora
    def on_calcLE8_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 9 de la calculadora
    def on_calcLE9_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 10 de la calculadora
    def on_calcLE10_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 11 de la calculadora
    def on_calcLE11_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 12 de la calculadora
    def on_calcLE12_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 13 de la calculadora
    def on_calcLE13_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    # Campo 14 de la calculadora
    def on_calcLE14_textChanged(self):
        if self.textChanged():
            self.executeCalc(self.legalTenders)

    #==============================================================================================================================================================================
    # VISTA DE INVENTARIO
    #==============================================================================================================================================================================
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para refrescar la vista del Inventario y elementos relacionados
    def refreshInventory(self):
        # Parametros para buscar con la función getProducts el nombre de los productos activos
        self.productsParams0 = {
            "product_name" : True,
            "active"       : True
        }

        # Parametros para buscar con la función getProducts la información necesaria para mostrar un producto en el inventario
        self.productsParams1 = {
            "product_id"     : True,
            "product_name"   : True,
            "price"          : True,
            "remaining"      : True,
            "remaining_lots" : True,
            "category"       : True,
            "active"         : True
        }

        # Listas de nombres de los productos
        self.productsNames = self.getProductList(self.productsParams0)                # Completa
        self.productsNamesAvailable = self.getProductList(self.productsParams0, 1)    # Disponibles
        self.productsNamesNotAvailable = self.getProductList(self.productsParams0, 2) # No disponibles

        # Listas con información para las tablas de productos
        self.productsInfo = self.getProductList(self.productsParams1)                # Completa
        self.productsInfoAvailable = self.getProductList(self.productsParams1, 1)    # Disponibles
        self.productsInfoNotAvailable = self.getProductList(self.productsParams1, 2) # No disponibles

        # Configuración de las barras de búsqueda por nombre de producto
        self.setupSearchBar(self.productSearch, self.productsNames)

        # Setup de las distintas tablas
        self.updateProductTable(self.table0, self.productsInfoAvailable)
        self.updateProductTable(self.table1, self.productsInfoNotAvailable)
        self.updateProductTable(self.table2, self.productsInfo)

        # Configurar tablas
        self.setupTables(self.productTables)

        # Limpiar campos
        if hasattr(self, 'lineExtra') and self.lineExtra != None: self.clearLE(self.lineExtra)
        self.clearLEs(self.productsRO0)
        self.clearLEs(self.lotsRO0)
        #self.dtE2.clear()

        self.indexMutex = False
        self.lotMutex1 = False
        self.currentLot = "0"
        self.currentLots = {}
        self.clearCB(self.cbox5)
        self.resetProductImage(self.selectedItem1)
        self.resetProductImage(self.selectedItem2)

        # Adición de campos extras
        if self.rbutton7.isChecked(): self.addProductInput()
        else:
            self.deleteProductInput()
            if self.rbutton6.isChecked():
                self.text64.setText("Buscar")

    def resetProductImage(self, button):
        self.tempImage = ""
        button.setIcon(QIcon(':/buttons/cross'))

    # Añadir campo extra en el apartado de productos
    def addProductInput(self):
        if (not hasattr(self, 'lineExtra') and not hasattr(self, 'textExtra')) or ((self.textExtra and self.lineExtra) == None):
            self.text64.setText("Buscar")
            self.text65.setText("Nombre")
            self.text66.setText("Precio")
            self.text67.setText("Categoria")
            self.text68.setText("Lotes")
            self.lineExtra = QLineEdit()
            self.textExtra = QLabel("Disp. total")

            self.textExtra.setStyleSheet("""
                color: #757575;
                background: transparent;
                font-family: Open Sans;
                font-size: 11pt;
            """)

            self.lineExtra.setStyleSheet("""
                border: 1px solid silver;
                border-radius: 2px;
                min-width: 5.5em;
                min-height: 1.25em;
                padding: 2px;
                background: #F5F5F5;
            """)

            self.lineExtra.setReadOnly(True)
            self.productLayout.addRow(self.textExtra, self.lineExtra)

    # Eliminar el campo extra en el apartado de productos
    def deleteProductInput(self):
        if hasattr(self, 'lineExtra') and hasattr(self, 'textExtra') and ((self.textExtra and self.lineExtra) != None):
            self.productLayout.removeWidget(self.textExtra)
            self.productLayout.removeWidget(self.lineExtra)
            self.textExtra.deleteLater()
            self.lineExtra.deleteLater()
            self.textExtra = None
            self.lineExtra = None

            self.text64.setText("Nombre")
            self.text65.setText("Precio")
            self.text66.setText("Categoria")
            self.text67.setText("Lotes")
            self.text68.setText("Disp. total")

    # Método para refrescar la tabla de productos en el inventario
    def updateProductTable(self, table, itemsList):
        self.clearTable(table)

        table.setRowCount(len(itemsList))
        for i in range(len(itemsList)):
            table.setItem(i, 0, QTableWidgetItem(str(itemsList[i][1]))) # Nombre
            table.setItem(i, 1, QTableWidgetItem(str(itemsList[i][2]))) # Precio
            table.setItem(i, 2, QTableWidgetItem(str(itemsList[i][5]))) # Categoria
            table.setItem(i, 3, QTableWidgetItem(str(itemsList[i][3]))) # Cantidad
            table.setItem(i, 4, QTableWidgetItem(str(itemsList[i][4]))) # Lotes

        self.elem_actual = 0
        if len(itemsList) > 0: table.selectRow(self.elem_actual)

        table.resizeColumnsToContents()

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Radio button para agregar nuevos productos
    def on_rbutton5_pressed(self):
        if self.click():
            self.deleteProductInput()
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1, listaLE1 = self.productsRO2)
            self.text64.setText("Nombre")
            self.resetProductImage(self.selectedItem1)
            self.setOnlyNumbers(self.productsON0)
            self.setAnyCharacter(self.productsON1)

    # Radio button para consultar productos
    def on_rbutton6_pressed(self):
        if self.click():
            self.deleteProductInput()
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1)
            self.text64.setText("Buscar")
            self.resetProductImage(self.selectedItem1)
            self.setOnlyNumbers(self.productsON0)
            self.setAnyCharacter(self.productsON1)

    # Radio button para editar productos
    def on_rbutton7_pressed(self):
        if self.click():
            self.addProductInput()
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1, listaLE1 = self.productsRO3)
            self.resetProductImage(self.selectedItem1)
            self.setOnlyNumbers(self.productsON1)
            self.setAnyCharacter(self.productsON0)

    # Radio button para eliminar productos
    def on_rbutton8_pressed(self):
        if self.click():
            self.deleteProductInput()
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1)
            self.text64.setText("Nombre")
            self.resetProductImage(self.selectedItem1)
            self.setOnlyNumbers(self.productsON0)
            self.setAnyCharacter(self.productsON1)

    # Radio button para agregar nuevos lotes
    def on_rbutton9_pressed(self):
        if self.click():
            self.clearCB(self.cbox5)
            self.clearLEs(self.lotsRO0)
            self.changeRO(self.lotsRO2, False, self.lotsRO3)
            self.readOnlyCB(self.cbox5, True)
            self.resetProductImage(self.selectedItem2)

    # Radio button para consultar lotes
    def on_rbutton10_pressed(self):
        if self.click():
            self.clearCB(self.cbox5)
            self.clearLEs(self.lotsRO0)
            self.changeRO(self.lotsRO1)
            self.readOnlyCB(self.cbox5, False)
            self.resetProductImage(self.selectedItem2)

    # Radio button para editar lotes
    def on_rbutton11_pressed(self):
        if self.click():
            self.clearCB(self.cbox5)
            self.clearLEs(self.lotsRO0)
            self.changeRO(self.lotsRO0, False)
            self.readOnlyCB(self.cbox5, False)
            self.resetProductImage(self.selectedItem2)

    # Radio button para eliminar lotes
    def on_rbutton12_pressed(self):
        if self.click():
            self.clearCB(self.cbox5)
            self.clearLEs(self.lotsRO0)
            self.changeRO(self.lotsRO1)
            self.readOnlyCB(self.cbox5, False)
            self.resetProductImage(self.selectedItem2)

    # Boton "Aceptar" en el apartado de productos
    def on_pbutton11_pressed(self):
        if self.click():
            # Modalidad para agregar nuevos productos
            if self.rbutton5.isChecked():
                if self.lineE26.text() != "":
                    product_name = self.lineE26.text()

                    if self.lineE27.text() != "":
                        # Obtener información del nuevo producto
                        price = self.lineE27.text()
                        categoy = self.lineE28.text()

                        if not self.db.existProduct(product_name):
                            # Agregar el producto a la BD
                            if self.db.createProduct(product_name, price, categoy):

                                if self.tempImage != "":
                                    copy2(self.tempImage, join(productPath, product_name))

                                successPopUp(parent = self).exec_()

                            else:
                                errorPopUp(parent = self).exec_()

                            # Refrescar toda la interfaz
                            self.refreshInventory()
                            self.refreshNew10()

                            # Enfocar
                            self.lineE26.setFocus()

                        else:
                            errorPopUp("El producto ya existe", self).exec_()

                    else:
                        warningPopUp("Debe especificar el precio del producto", self).exec_()

                else:
                    warningPopUp("Debe especificar el nombre del producto", self).exec_()

            # Modalidad para consultar productos
            elif self.rbutton6.isChecked():
                # Enfocar
                self.lineE26.setFocus()

            # Modalidad para editar productos
            elif self.rbutton7.isChecked():
                if self.lineE26.text() != "":
                    product_name = self.lineE26.text()
                    if self.db.existProduct(product_name):
                        newName = self.lineE27.text()
                        newPrice = float(self.lineE28.text())
                        newCategory = self.lineE29.text()

                        if newName != "" and newPrice > 0:
                            # Actualizar información de producto
                            if self.db.updateProduct(product_name, newName, newPrice, newCategory):
                                successPopUp(parent = self).exec_()

                            else:
                                errorPopUp(parent = self).exec_()

                        # Refrescar toda la interfaz
                        self.refreshInventory()

                        # Enfocar
                        self.lineE26.setFocus()

                    else:
                        errorPopUp("El producto no existe", self).exec_()

                else:
                    warningPopUp("Debe especificar el nombre del producto", self).exec_()

            # Modalidad para eliminar productos
            elif self.rbutton8.isChecked():
                if self.lineE26.text() != "":
                    product_name = self.lineE26.text()
                    if self.db.existProduct(product_name):
                        # Eliminar producto
                        if self.db.deleteProduct(product_name):
                            successPopUp(parent = self).exec_()

                        else:
                            errorPopUp(parent = self).exec_()

                        # Refrescar toda la interfaz
                        self.refreshInventory()

                        # Enfocar
                        self.lineE26.setFocus()

                    else:
                        errorPopUp("El producto no existe", self).exec_()

                else:
                    warningPopUp("Debe especificar el nombre del producto", self).exec_()

    # Boton "Aceptar" en el apartado de lotes
    def on_pbutton13_pressed(self):
        if self.click():

            # Modalidad para agregar nuevos lotes
            if self.rbutton9.isChecked():

                # Obtener información del nuevo lote
                product_name = self.lineE33.text()
                provider_name = self.lineE34.text()
                cost = self.lineE35.text()
                #expiration_date = self.dtE2.text()
                quantity = self.lineE37.text()

                # Verificar completitud de los campos obligatorios
                if (product_name and provider_name and cost and quantity) != "":

                    if self.db.existProduct(product_name):

                        if self.db.existProvider(provider_name):

                            kwargs = {
                                "product_name"  : product_name,
                                "provider_name" : provider_name,
                                "received_by"   : self.user,
                                "cost"          : float(cost),
                                "quantity"      : int(quantity)
                            }

                            #if expiration_date != "": kwargs["expiration_date"] = expiration_date

                            # Agregar el lote a la BD
                            if self.db.createLot(**kwargs):
                                successPopUp(parent = self).exec_()

                            else:
                                errorPopUp(parent = self).exec_()

                            self.refreshInventory()      # Refrescar toda la interfaz
                            self.lineE33.setFocus()      # Enfocar

                        else:
                            errorPopUp("El proveedor no existe", self).exec_()

                    else:
                        errorPopUp("El producto no existe", self).exec_()

                else:
                    warningPopUp("Debe llenar todos los campos", self).exec_()

            # Modalidad para consultar lotes
            elif self.rbutton10.isChecked():
                self.refreshInventory()      # Refrescar toda la interfaz
                self.lineE33.setFocus()      # Enfocar

            # Modalidad para editar lotes
            elif self.rbutton11.isChecked():

                product_name = self.lineE33.text()   # Producto
                provider_name = self.lineE34.text()  # Proveedor
                cost =  self.lineE35.text()          # Costo
                quantity = self.lineE37.text()       # Cantidad
                remaining = self.lineE38.text()      # Disponibles

                """if self.dtE2.text() != "None":
                    expiration_date = datetime.strptime(self.dtE2.text(), self.dateFormat)  # Caducidad"""

                if (product_name and provider_name and cost and quantity and remaining) != "":

                    if self.db.existProduct(product_name):

                        if self.db.existProvider(provider_name):

                            cost      = float(cost)                        # Costo
                            quantity  = int(quantity)                      # Cantidad
                            remaining = int(remaining)                     # Disponibles

                            if quantity >= remaining:

                                lot_id    = self.currentLots[self.currentLot]  # Lote

                                if self.db.updateLot(lot_id, product_name, provider_name, cost, quantity, remaining):
                                    successPopUp(parent = self).exec_()

                                else:
                                    errorPopUp(parent = self).exec_()

                                # Refrescar toda la interfaz
                                self.refreshInventory()

                                # Enfocar
                                self.lineE33.setFocus()

                            else:
                                errorPopUp("La disponibilidad no puede ser mayor a la cantidad", self).exec_()

                        else:
                            errorPopUp("El proveedor no existe", self).exec_()

                    else:
                        errorPopUp("El producto no existe", self).exec_()

                else:
                    warningPopUp("Debe llenar todos los campos", self).exec_()

            # Modalidad para eliminar lotes
            elif self.rbutton12.isChecked():
                product_name = self.lineE33.text()          # Producto
                provider_name = self.lineE34.text()         # Proveedor

                if (product_name and provider_name) != "":

                    if self.db.existProduct(product_name):

                        if self.db.existProvider(provider_name):

                            lot_id = self.currentLots[self.currentLot]  # Lote

                            if self.db.deleteLot(lot_id):
                                successPopUp(parent = self).exec_()

                            else:
                                errorPopUp(parent = self).exec_()

                            # Refrescar toda la interfaz
                            self.refreshInventory()

                            # Enfocar
                            self.lineE33.setFocus()

                        else:
                            errorPopUp("El proveedor no existe", self).exec_()

                    else:
                        errorPopUp("El producto no existe", self).exec_()

                else:
                    warningPopUp("Debe llenar todos los campos", self).exec_()

    # Boton para ver/agregar imágen de un producto
    def on_selectedItem1_pressed(self):
        if self.click():
            if self.rbutton5.isChecked():
                filePath = QFileDialog.getOpenFileName(self, 'Seleccionar imágen', QDir.currentPath(), "Imágenes (*.bmp *.jpg *.jpeg *.png)")
                if filePath != "":
                    self.selectedItem1.setIcon(QIcon(filePath))
                    self.tempImage = filePath

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CAMPOS DE TEXTO
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # LineEdit para ingresar nombres de los productos
    def on_lineE26_textChanged(self):
        if self.textChanged():
            if not self.rbutton5.isChecked() and self.lineE26.text() != "":
                product_name = self.lineE26.text()
                if self.db.existProduct(product_name):
                    product = self.db.getProductByNameOrID(product_name=product_name)[0]
                    self.selectedItem1.setIcon(QIcon(join(productPath, product_name)))
                    if self.rbutton7.isChecked():
                        self.lineE27.setText(product.product_name)        # Product Name
                        self.lineE28.setText(str(product.price))          # Precio
                        self.lineE29.setText(product.category)            # Categoria
                        self.lineE30.setText(str(product.remaining_lots)) # Lotes
                        self.lineExtra.setText(str(product.remaining))    # Disp. Total

                    else:
                        self.lineE27.setText(str(product.price))          # Precio
                        self.lineE28.setText(product.category)            # Categoria
                        self.lineE29.setText(str(product.remaining_lots)) # Lotes
                        self.lineE30.setText(str(product.remaining))      # Disp. Total

                else:
                    self.clearLEs(self.productsRO1)
                    self.resetProductImage(self.selectedItem1)

    # LineEdit para ingresar nombres de los productos
    def on_lineE33_textChanged(self):
        if self.textChanged():
            if self.lineE33.text() != "":
                product_name = self.lineE33.text()
                if self.db.existProduct(product_name):
                    self.selectedItem2.setIcon(QIcon(join(productPath, product_name)))
                    if not self.rbutton9.isChecked():
                        product_id = self.db.getProductID(product_name)
                        lotIDs = self.db.getLotsIDByProductID(product_id)
                        self.currentLot = "0"
                        self.currentLots = {}
                        self.lotMutex1 = False
                        for i in range(1, len(lotIDs)+1):
                            self.cbox5.addItem(str(i))
                            self.currentLots[str(i)] = lotIDs[i-1]

                        if len(lotIDs) > 0:
                            self.currentLot = "1"
                            lot_id = self.currentLots[self.currentLot]
                            lot = self.db.getLots(lot_id=lot_id)[0]

                            self.lineE34.setText(lot.provider_id)        # Proveedor
                            self.lineE35.setText(str(lot.cost))          # Costo
                            #self.dtE2.setText(str(lot.expiration_date)) # Caducidad
                            self.lineE37.setText(str(lot.quantity))      # Cantidad
                            self.lineE38.setText(str(lot.remaining))     # Disponibilidad

                        self.lotMutex1 = True

                else:
                    self.clearLEs(self.lotsRO1)
                    self.resetProductImage(self.selectedItem2)

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # COMBO BOX
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # ComboBox para elegir el número de lote
    def on_cbox5_currentIndexChanged(self):
        if self.indexChanged() and self.lotMutex1:
            if self.currentLot != self.cbox5.currentText() and self.currentLot != "0":
                self.currentLot = self.cbox5.currentText()
                lot_id = self.currentLots[self.currentLot]
                lot = self.db.getLots(lot_id=lot_id)[0]

                self.lineE34.setText(lot.provider_id)        # Proveedor
                self.lineE35.setText(str(lot.cost))          # Costo
                #self.dtE2.setText(str(lot.expiration_date)) # Caducidad
                self.lineE37.setText(str(lot.quantity))      # Cantidad
                self.lineE38.setText(str(lot.remaining))     # Disponibilidad

    #==============================================================================================================================================================================
    # VISTA DE VENTAS
    #==============================================================================================================================================================================

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para refrescar la vista del Ventas y elementos relacionados
    def refreshSales(self):
        # Configurar restricciones de los LineEdit en la vista de ventas
        self.setupSalesLE()

        # Setear variables de control
        self.selectedProductRemaining = {}
        self.selectedProductName = ""
        self.selectedProducts = {}

        # Configurar botones para añadir y quitar
        self.add0.setEnabled(True)
        self.substract0.setEnabled(False)

        # Limpiar los campos
        self.clearSpinLines(self.spinBox)
        self.clearLEs(self.salesClientLE1)
        self.clearLEs(self.salesCheckoutLE)
        self.clearTable(self.table11)

        self.refreshTop10()
        self.refreshNew10()

        # Refrescar el inventario
        self.refreshInventory()
        self.refreshClients()
        self.refreshCash()

        # Enfocar
        self.lineE17.setFocus()

    # Función para aplicar la configuración por defecto de los lineEdit de la vista de ventas
    def setupSalesLE(self):
        self.lineE152.setValidator(QIntValidator(0, 0)) # Establecer limite de saldo para pagar
        self.lineE22.setValidator(QIntValidator(0, 0))  # Establecer limite de efectivo para pagar

    # Método para refrescar la tabla de factura en ventas
    def updateInvoiceTable(self, table, itemsList):
        self.clearTable(table)             # Vaciar la tabla
        total = 0                          # Variable para contar el total a pagar
        table.setRowCount(len(itemsList))  # Contador de filas
        for i in range(len(itemsList)):    # LLenar tabla
            table.setItem(i, 0, QTableWidgetItem(str(itemsList[i][0]))) # Nombre
            table.setItem(i, 1, QTableWidgetItem(str(itemsList[i][1]))) # Precio
            table.setItem(i, 2, QTableWidgetItem(str(itemsList[i][2]))) # Cantidad
            table.setItem(i, 3, QTableWidgetItem(str(itemsList[i][3]))) # Subtotal

            # Añadir boton para eliminar la fila
            removeButton = QPushButton()
            removeButton.setIcon(QIcon(':/buttons/cross'))
            removeButton.setStyleSheet("background: transparent; border: none;")
            removeButton.clicked.connect(self.on_removeRow_clicked)
            table.setCellWidget(i, 4, removeButton)

            # Sumar subtotal al total
            total += float(itemsList[i][3])

        self.lineE21.setText(str(total))                          # Actualizar el lineEdit del total
        self.elem_actual = 0                                      # Definir la fila que se seleccionará
        if len(itemsList) > 0: table.selectRow(self.elem_actual)  # Seleccionar fila
        table.resizeColumnsToContents()                           # Redimensionar columnas segun el contenido

    # Refrescar apartado de Top 10
    def refreshTop10(self):
        self.top10 = self.db.getTop10()
        for i in range(len(self.top10)):
            product_name = self.top10[i].product_name
            price = str(self.top10[i].price)
            self.popularItems[i].setIcon(QIcon(join(productPath, product_name)))
            self.popularTexts[i].setText(price)

    # Refrescar apartado de Nuevos
    def refreshNew10(self):
        self.new10 = self.db.getNew10()
        for i in range(len(self.new10)):
            product_name = self.new10[i].product_name
            price = str(self.new10[i].price)
            self.newItems[i].setIcon(QIcon(join(productPath, product_name)))
            self.newTexts[i].setText(price)

    # Restar al spinBox
    def substractToSalesSpinBox(self):
        if self.spinLine0.text() != "":  count = int(self.spinLine0.text())
        else: count = 0

        if count > 0:
            self.spinLine0.setText(str(count-1))

    # Sumar al spinBox
    def addToSalesSpinBox(self):
        if self.spinLine0.text() != "":  count = int(self.spinLine0.text())
        else: count = 0

        if self.selectedProductName in self.selectedProductRemaining:
            if count < self.selectedProductRemaining[self.selectedProductName]:
                self.spinLine0.setText(str(count+1))

            else:
                warningPopUp("Límite de disponibilidad alcanzado", self).exec_()

    # Seleccionar un item de las listas Top 10 y Nuevo
    def selectPopularItem(self, n):
        if n < len(self.top10):
            product_name = self.top10[n].product_name
            if self.lineE23.text() != product_name:
                self.clearSpinLines(self.spinBox)
                self.lineE23.setText(product_name)

            else:
                self.addToSalesSpinBox()

    # Seleccionar un item de las listas Top 10 y Nuevo
    def selectNewItem(self, n):
        if n < len(self.new10):
            product_name = self.new10[n].product_name
            if self.lineE23.text() != product_name:
                self.clearSpinLines(self.spinBox)
                self.lineE23.setText(product_name)

            else:
                self.addToSalesSpinBox()

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Boton 1 del apartado de Top 10
    def on_popularItem0_pressed(self):
        if self.click():
            self.selectPopularItem(0)

    # Boton 2 del apartado de Top 10
    def on_popularItem1_pressed(self):
        if self.click():
            self.selectPopularItem(1)

    # Boton 3 del apartado de Top 10
    def on_popularItem2_pressed(self):
        if self.click():
            self.selectPopularItem(2)

    # Boton 4 del apartado de Top 10
    def on_popularItem3_pressed(self):
        if self.click():
            self.selectPopularItem(3)

    # Boton 5 del apartado de Top 10
    def on_popularItem4_pressed(self):
        if self.click():
            self.selectPopularItem(4)

    # Boton 6 del apartado de Top 10
    def on_popularItem5_pressed(self):
        if self.click():
            self.selectPopularItem(5)

    # Boton 7 del apartado de Top 10
    def on_popularItem6_pressed(self):
        if self.click():
            self.selectPopularItem(6)

    # Boton 8 del apartado de Top 10
    def on_popularItem7_pressed(self):
        if self.click():
            self.selectPopularItem(7)

    # Boton 9 del apartado de Top 10
    def on_popularItem8_pressed(self):
        if self.click():
            self.selectPopularItem(8)

    # Boton 10 del apartado de Top 10
    def on_popularItem9_pressed(self):
        if self.click():
            self.selectPopularItem(9)

    # Boton 1 del apartado de Nuevos
    def on_newItem0_pressed(self):
        if self.click():
            self.selectNewItem(0)

    # Boton 2 del apartado de Nuevos
    def on_newItem1_pressed(self):
        if self.click():
            self.selectNewItem(1)

    # Boton 3 del apartado de Nuevos
    def on_newItem2_pressed(self):
        if self.click():
            self.selectNewItem(2)

    # Boton 4 del apartado de Nuevos
    def on_newItem3_pressed(self):
        if self.click():
            self.selectNewItem(3)

    # Boton 5 del apartado de Nuevos
    def on_newItem4_pressed(self):
        if self.click():
            self.selectNewItem(4)

    # Boton 6 del apartado de Nuevos
    def on_newItem5_pressed(self):
        if self.click():
            self.selectNewItem(5)

    # Boton 7 del apartado de Nuevos
    def on_newItem6_pressed(self):
        if self.click():
            self.selectNewItem(6)

    # Boton 8 del apartado de Nuevos
    def on_newItem7_pressed(self):
        if self.click():
            self.selectNewItem(7)

    # Boton 9 del apartado de Nuevos
    def on_newItem8_pressed(self):
        if self.click():
            self.selectNewItem(8)

    # Boton 10 del apartado de Nuevos
    def on_newItem9_pressed(self):
        if self.click():
            self.selectNewItem(9)

    # Botón para sumar al spinLine
    def on_add0_pressed(self):
        if self.click():
            self.addToSalesSpinBox()

    # Botón para restar al spinLine
    def on_substract0_pressed(self):
        if self.click():
            self.substractToSalesSpinBox()

    # Botón para efectuar venta
    def on_pbutton7_pressed(self):
        if self.click():
            if self.lineE17.text() != "":
                if self.lineE21.text() != "":
                    ci = int(self.lineE17.text())
                    if  self.db.existClient(ci):
                        total = float(self.lineE21.text())
                        efectivo = 0
                        saldo = 0

                        if self.lineE22.text() != "": efectivo = float(self.lineE22.text())
                        if self.lineE152.text() != "": saldo = float(self.lineE152.text())

                        if efectivo + saldo >= total:

                            try:
                                purchase_id = self.db.createPurchase(ci, self.user)                         # Crear compra
                                for key, val in self.selectedProducts.items():                              # Tomar cada producto seleccionado
                                    self.db.createProductList(purchase_id, key, float(val[0]), int(val[1])) # Crear la lista de productos
                                if efectivo > 0: self.db.createCheckout(purchase_id, efectivo)              # Crear pago con dinero
                                if saldo > 0: self.db.createCheckout(purchase_id, saldo, True)              # Crear pago con saldo
                                successPopUp(parent = self).exec_()                                         # Venta exitosa

                            except:
                                errorPopUp(parent = self).exec_()                                           # Venta fallida

                            # Setear variables y refrescar la interfaz
                            self.refreshSales()

                        else:
                            warningPopUp("Pago insuficiente", self).exec_()

                    else:
                        warningPopUp("El cliente no existe", self).exec_()

                else:
                    warningPopUp("No se han agregado productos", self).exec_()

            else:
                 warningPopUp("Debe especificar un cliente", self).exec_()

    # Botón para agregar lista de producto
    def on_pbutton9_pressed(self):
        if self.click():
            name = self.lineE23.text()
            if self.db.existProduct(name) and int(self.spinLine0.text()) > 0:

                # Cargar información
                product = self.db.getProductByNameOrID(name)[0]                     # Obtener cliente
                price = str(product.price)                                          # Obtener precio
                cantidad = self.spinLine0.text()                                    # Obtener cantidad
                subtotal = float(price)*int(cantidad)                               # Obtener subtotal

                # Actualizar datos en el manejador
                if name not in self.selectedProducts:
                    self.selectedProducts[name] = [price, cantidad, subtotal]             # Añadir a la lista de productos seleccionados
                    self.selectedProductRemaining[name] = product.remaining-int(cantidad) # Acutalizar la cota superior del contador

                else:
                    temp = self.selectedProducts[name]
                    temp[1] = str(int(temp[1])+int(cantidad))
                    temp[2] = str(float(temp[2])+float(subtotal))
                    self.selectedProducts[name] = temp                                   # Actualizar la instancia del producto en la lista de productos seleccionados
                    self.selectedProductRemaining[name] = product.remaining-int(temp[1]) # Acutalizar la cota superior del contador

                selectedList = []
                for key, value in self.selectedProducts.items():
                    selectedList.append([key, value[0], value[1], value[2]])

                self.selectedProductName = ""

                # Refrescar interfaz
                self.updateInvoiceTable(self.table11, selectedList) # Actualizar la factura
                self.setupTable(self.table11)                       # Reconfigurar la tabla de factura
                self.clearLEs(self.selectedProductLE1)              # Limpiar los lineEdit de este apartado
                self.clearSpinLine(self.spinLine0)                  # Setear en 0 el lineEdit del contador

    # Botones para eliminar listas de productos
    def on_removeRow_clicked(self):
        key = self.table11.selectedItems()[0].text()
        del self.selectedProducts[key]

        selectedList = []
        for key, value in self.selectedProducts.items():
            selectedList.append([key, value[0], value[1], value[2]])

        self.selectedProductName = ""

        # Refrescar interfaz
        self.updateInvoiceTable(self.table11, selectedList) # Actualizar la factura
        self.setupTable(self.table11)                       # Reconfigurar la tabla de factura

    # Boton para cancelar una compra
    def on_cancelpb0_pressed(self):
        if self.click():
            self.refreshSales()

    # Boton para descartar una seleccion de producto
    def on_cancelpb1_pressed(self):
        if self.click():
            self.selectedProductName = ""
            self.clearLEs(self.selectedProductLE1)
            self.clearSpinLine(self.spinLine0)
            self.setupSpinLines(self.spinBox)
            self.resetProductImage(self.selectedItem0)

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CAMPOS DE TEXTO
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # LineEdit para ingresar la cédula del cliente
    def on_lineE17_textChanged(self):
        if self.textChanged():
            if self.lineE17.text() != "":
                ci = int(self.lineE17.text())
                if self.db.existClient(ci):
                    client = self.db.getClients(ci)[0]                           # Obtener cliente
                    self.lineE18.setText(client.firstname)                       # Establecer Nombre
                    self.lineE19.setText(client.lastname)                        # Establecer Apellido
                    self.lineE20.setText(str(client.balance))                    # Establecer Saldo

                    if self.lineE21.text() != "":
                        total = float(self.lineE21.text())
                        cota = total

                        if self.lineE22.text() != "":
                            efectivo = float(self.lineE22.text())

                        else:
                            efectivo = 0

                        cota = total - efectivo
                        balance = client.balance

                        if balance < cota:
                            cota = balance

                        self.lineE152.setValidator(QIntValidator(0, cota))
                        if self.lineE152.text() != "":
                            saldo = float(self.lineE152.text())
                            if saldo > cota:
                                self.lineE152.setText(str(cota))

                else:
                    self.clearLEs(self.salesClientLE0)              # Limpiar lineEdits del apartado
                    self.lineE152.setValidator(QIntValidator(0, 0)) # Establecer limite de saldo para pagar
            else:
                self.clearLEs(self.salesClientLE0)              # Limpiar lineEdits del apartado
                self.lineE152.setValidator(QIntValidator(0, 0)) # Establecer limite de saldo para pagar

    # LineEdit para ingresar el total a pagar
    def on_lineE21_textChanged(self):
        if self.textChanged():
            if self.lineE21.text() != "":
                total = float(self.lineE21.text())
                cota1 = total
                cota2 = total

                if self.lineE22.text() != "": efectivo = float(self.lineE22.text())
                else: efectivo = 0

                cota1 = total - efectivo

                if self.lineE17.text() != "":
                    ci = int(self.lineE17.text())
                    if self.db.existClient(ci):
                        balance = self.db.getClients(ci)[0].balance

                        if balance >= 0:
                            if balance < cota1:
                                cota1 = balance

                        else: cota1 = 0
                    else: cota1 = 0
                else: cota1 = 0

                self.lineE152.setValidator(QIntValidator(0, cota1))
                if self.lineE152.text() != "":
                    saldo = float(self.lineE152.text())

                    if saldo > cota1:
                        self.lineE152.setText(str(cota1))

                if self.lineE152.text() != "": saldo = float(self.lineE152.text())
                else: saldo = 0

                cota2 = total - saldo

                self.lineE22.setValidator(QIntValidator(0, cota2))
                if self.lineE22.text() != "":
                    efectivo = float(self.lineE22.text())

                    if efectivo > cota2:
                        self.lineE22.setText(str(cota2))

            else:
                self.lineE152.setValidator(QIntValidator(0, 0)) # Establecer limite de saldo para pagar
                self.lineE22.setValidator(QIntValidator(0, 0))  # Establecer limite de efectivo para pagar

    # LineEdit para ingresar el monto a pagar en efectivo
    def on_lineE22_textChanged(self):
        if self.textChanged():
            if self.lineE21.text() != "":
                total = float(self.lineE21.text())
                cota = total

                if self.lineE22.text() != "": efectivo = float(self.lineE22.text())
                else: efectivo = 0

                cota = total - efectivo
                if self.lineE17.text() != "":
                    ci = int(self.lineE17.text())
                    if self.db.existClient(ci):
                        balance = self.db.getClients(ci)[0].balance

                        if balance < cota:
                            cota = balance

                    else: cota = 0
                else: cota = 0

                self.lineE152.setValidator(QIntValidator(0, cota))
                if self.lineE152.text() != "":
                    saldo = float(self.lineE152.text())

                    if saldo > cota:
                        self.lineE152.setText(str(cota))

    # LineEdit para ingresar el monto a pagar con saldo
    def on_lineE152_textChanged(self):
        if self.textChanged():
            if self.lineE21.text() != "":
                total = float(self.lineE21.text())
                cota = total
                if self.lineE152.text() != "": saldo = float(self.lineE152.text())
                else: saldo = 0

                cota = total - saldo

                self.lineE22.setValidator(QIntValidator(0, cota))
                if self.lineE22.text() != "":
                    efectivo = float(self.lineE22.text())

                    if efectivo > cota:
                        self.lineE22.setText(str(cota))

    # LineEdit para ingresar el nombre del producto seleccionado
    def on_lineE23_textChanged(self):
        if self.textChanged():
            product_name = self.lineE23.text()
            if self.db.existProduct(product_name):
                product = self.db.getProductByNameOrID(product_name)[0]
                self.lineE24.setText(str(product.price))
                self.selectedProductName = product_name
                amount = "0"

                if product_name in self.selectedProducts:
                    # Actualizar cantidad
                    amount = self.table11.selectedItems()[2].text()

                    # Eliminar producto de la factura
                    del self.selectedProducts[product_name]

                    # Recalcular elementos en la factura
                    selectedList = []
                    for key, value in self.selectedProducts.items():
                        selectedList.append([key, value[0], value[1], value[2]])

                    # Refrescar factura
                    self.updateInvoiceTable(self.table11, selectedList)
                    self.setupTable(self.table11)

                self.selectedProductRemaining[product_name] = product.remaining
                self.spinLine0.setValidator(QIntValidator(0, product.remaining))
                self.selectedItem0.setIcon(QIcon(join(productPath, product_name)))
                self.spinLine0.setText(amount)

            else:
                self.selectedProductName = ""
                self.clearLEs(self.selectedProductLE0)
                self.clearSpinLine(self.spinLine0)
                self.setupSpinLines(self.spinBox)
                self.resetProductImage(self.selectedItem0)

    # LineEdit para ingresar nombres de los productos
    def on_spinLine0_textChanged(self):
        if self.textChanged():
            product_name = self.lineE23.text()
            if product_name != "":
                if self.db.existProduct(product_name):
                    if self.spinLine0.text() != "": count = int(self.spinLine0.text())
                    else: count = 0

                    self.lineE25.setText(str(((count)*float(self.lineE24.text()))))

                    if count == 0: self.substract0.setEnabled(False)
                    elif 0 < count < self.selectedProductRemaining[self.selectedProductName]:
                        self.add0.setEnabled(True)
                        self.substract0.setEnabled(True)
                    else:
                        self.add0.setEnabled(False)

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # TABLAS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Cambio de selección en la factura
    def on_table11_itemClicked(self, item):
        if self.rowChanged():
            if item.column() != 4:
                # Cargar información
                items = self.table11.selectedItems()

                # Actualizar los campos
                self.lineE23.setText(items[0].text())

    #==============================================================================================================================================================================
    # VISTA DE PROVEEDORES
    #==============================================================================================================================================================================

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para refrescar la vista del Ventas y elementos relacionados
    def refreshProviders(self):
        # Configuración de la barra de búsqueda de cliente por CI
        providersNames = self.db.getProvidersNames()
        self.setupSearchBar(self.providersSearch, providersNames)

        # Limpiar los campos
        self.clearLEs(self.providersLE0)
        self.clearLEs(self.providersLE1)
        self.clearTEs(self.providersTE0)
        self.clearTEs(self.providersTE1)

        # Refrescar tabla
        self.updateProvidersTable()

    # Método para refrescar la tabla de proveedores
    def updateProvidersTable(self):
        table = self.table13
        providers = self.db.getAllProviders()

        self.clearTable(table)                                                       # Vaciar la tabla
        table.setRowCount(len(providers))                                            # Contador de filas
        for i in range(len(providers)):                                              # Llenar tabla
            table.setItem(i, 0, QTableWidgetItem(str(providers[i].provider_name)))   # Nombre
            table.setItem(i, 1, QTableWidgetItem(str(providers[i].phone)))           # Teléfono
            table.setItem(i, 2, QTableWidgetItem(str(providers[i].email)))           # Correo
            table.setItem(i, 3, QTableWidgetItem(str(providers[i].description)))     # Descripción
            table.setItem(i, 4, QTableWidgetItem(str(providers[i].pay_information))) # Informacion de pago

        self.elem_actual = 0                                            # Definir la fila que se seleccionará
        if len(providers) > 0: table.selectRow(self.elem_actual)        # Seleccionar fila
        table.resizeColumnsToContents()                                 # Redimensionar columnas segun el contenido
        self.setupTable(table)                                          # Reconfigurar tabla

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Botón para crear un proveedor
    def on_pbutton20_pressed(self):
        if self.click():
            name = self.lineE146.text()
            phone = self.lineE147.text()
            email = self.lineE148.text()
            if name != "":
                if not (self.db.existProvider(name)):
                    if (phone != "" and validatePhoneNumber(phone)) or phone == "":
                        if (email != "" and validateEmail(email)) or email == "":
                            kwargs = {
                                "provider_name"   : name,
                                "phone"           : phone,
                                "email"           : email,
                                "description"     : self.textE1.toPlainText(),
                                "pay_information" : self.textE2.toPlainText()
                            }
                            self.db.createProvider(**kwargs)
                            successPopUp("Proveedor "+name+" creado exitosamente",self).exec_()

                            self.clearLEs(self.providersLE0) # Limpiar formulario
                            self.refreshProviders()          # Refrescar vista
                            self.lineE146.setFocus()         # Enfocar
                        else:
                            errorPopUp("Formato incorrecto de correo",self).exec_()

                    else:
                        errorPopUp("Formato incorrecto para número telefónico",self).exec_()
                else:
                    errorPopUp("El proveedor "+name+" ya existe",self).exec_()
            else:
                errorPopUp("Falta nombre de proveedor",self).exec_()

    #Botón para cancelar en registrar proveedor
    def on_cancelpb22_pressed(self):
        self.clearLEs(self.providersLE0)
        self.clearTEs(self.providersTE0)
        self.lineE146.setFocus()

    #Boton para editar proveedor
    def on_pbutton22_pressed(self):
        if self.click():
            name = self.lineE149.text()
            phone = self.lineE150.text()
            email = self.lineE151.text()
            if name != "":
                if self.db.existProvider(name):
                    if (phone != "" and validatePhoneNumber(phone)) or phone == "":
                        if (email != "" and validateEmail(email)) or email == "":
                            kwargs = {
                                "oldName"         : name,
                                "phone"           : phone,
                                "email"           : email,
                                "description"     : self.textE3.toPlainText(),
                                "pay_information" : self.textE4.toPlainText()
                            }
                            self.db.updateProviderInfo(**kwargs)
                            successPopUp("Proveedor "+name+" actualizado exitosamente",self).exec_()

                            self.clearLEs(self.providersLE1) # Limpiar formulario
                            self.refreshProviders()          # Refrescar vista
                            self.lineE149.setFocus()         # Enfocar
                        else:
                            errorPopUp("Formato incorrecto de correo",self).exec_()

                    else:
                        errorPopUp("Formato incorrecto para número telefónico",self).exec_()
                else:
                    errorPopUp("El proveedor "+name+" no existe",self).exec_()
            else:
                errorPopUp("Falta nombre de proveedor",self).exec_()

    #Botón cancelar de editar proveedor
    def on_cancelpb23_pressed(self):
        self.clearLEs(self.providersLE1)
        self.clearTEs(self.providersTE1)
        self.lineE149.setFocus()

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CAMPOS DE TEXTO
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # LineEdit para ingresar el nombre del proveedor en el aparato de editar
    def on_lineE149_textChanged(self):
        if self.textChanged():
            provider_name = self.lineE149.text()
            if self.db.existProvider(provider_name):
                provider = self.db.getProvider(provider_name)
                self.lineE150.setText(provider.phone)
                self.lineE151.setText(provider.email)
                self.textE3.setPlainText(provider.description)
                self.textE4.setPlainText(provider.pay_information)

            else:
                self.clearLEs(self.providersLE2)
                self.clearTEs(self.providersTE1)

    #==============================================================================================================================================================================
    # VISTA DE CLIENTES
    #==============================================================================================================================================================================

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para refrescar la vista del Ventas y elementos relacionados
    def refreshClients(self):
        # Configuración de la barra de búsqueda de cliente por CI
        clientsCI = self.db.getClientsCI()
        self.setupSearchBar(self.clientsSearch, clientsCI, True)

        # Limpiar los campos
        self.clearLEs(self.clientsLE0)
        self.clearLEs(self.clientsLE0)
        self.clearLEs(self.clientsLE1)

        # Setear los comboBox
        self.resetClientsCBs()

        # Refrescar tabla
        self.updateClientsTable()
        self.updateClientsTable(True)

    # Método para refrescar las tablas de clientes
    def updateClientsTable(self, debt = False):
        if debt:
            table = self.table6
            clients = self.db.getClients(debt=debt)

        else:
            table = self.table7
            clients = self.db.getClients()

        self.clearTable(table)                                                # Vaciar la tabla
        table.setRowCount(len(clients))                                       # Contador de filas
        for i in range(len(clients)):                                         # Llenar tabla
            table.setItem(i, 0, QTableWidgetItem(str(clients[i].ci)))         # Cédula
            table.setItem(i, 1, QTableWidgetItem(str(clients[i].firstname)))  # Nombre
            table.setItem(i, 2, QTableWidgetItem(str(clients[i].lastname)))   # Apellido
            table.setItem(i, 3, QTableWidgetItem(str(clients[i].balance)))    # Saldo


        self.elem_actual = 0                                            # Definir la fila que se seleccionará
        if len(clients) > 0: table.selectRow(self.elem_actual)          # Seleccionar fila
        table.resizeColumnsToContents()                                 # Redimensionar columnas segun el contenido
        self.setupTable(table)                                          # Reconfigurar tabla

    # Método para reestablecer los comboBox en registrar y editar
    def resetClientsCBs(self):
        self.cbox10.clear()
        self.cbox11.clear()
        self.cbox12.clear()
        self.cbox13.clear()

        allow = ["Permitir", "No permitir"]
        disallow = ["No permitir", "Permitir"]

        self.cbox10.addItems(disallow)
        self.cbox11.addItems(allow)
        self.cbox12.addItems(disallow)
        self.cbox13.addItems(disallow)

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Botón para crear un cliente
    def on_pbutton17_pressed(self):
        if self.click():
            if self.lineE52.text() != "":
                ci = int(self.lineE52.text())
                if not self.db.existClient(ci):
                    if self.lineE53.text() != "":
                        if self.lineE54.text() != "":

                            debt = (self.cbox10.currentText() == "Permitir")
                            book = (self.cbox11.currentText() == "Permitir")

                            kwargs = {
                                "ci"              : ci,
                                "firstname"       : self.lineE53.text(),
                                "lastname"        : self.lineE54.text(),
                                "phone"           : self.lineE55.text(),
                                "email"           : self.lineE56.text(),
                                "debt_permission" : debt,
                                "book_permission" : book
                            }

                            if self.db.createClient(**kwargs): # Crear cliente
                                successPopUp(parent = self).exec_()

                            else:
                                errorPopUp(parent = self).exec_()

                            self.clearLEs(self.clientsLE0) # Limpiar formulario
                            self.refreshClients()          # Refrescar vista
                            self.lineE52.setFocus()        # Enfocar

                        else:
                            warningPopUp("Apellido no específicado", self).exec_()

                    else:
                        warningPopUp("Nombre no específicado", self).exec_()

                else:
                    errorPopUp("Número de cédula previamente registrado", self).exec_()

            else:
                warningPopUp("Número de cédula no específicado", self).exec_()

    # Botón para editar un cliente
    def on_pbutton19_pressed(self):
        if self.click():
            if self.lineE57.text() != "":
                ci = int(self.lineE57.text())
                if self.db.existClient(ci):
                    if self.lineE58.text() != "":
                        if self.lineE59.text() != "":

                            debt = (self.cbox12.currentText() == "Permitir")
                            book = (self.cbox13.currentText() == "Permitir")

                            kwargs = {
                                "ciOriginal" : ci,
                                "firstname"  : self.lineE58.text(),
                                "lastname"   : self.lineE59.text(),
                                "phone"      : self.lineE60.text(),
                                "email"      : self.lineE61.text(),
                                "debt_permission" : debt,
                                "book_permission" : book
                            }

                            if self.db.updateClient(**kwargs):      # Crear cliente
                                successPopUp(parent = self).exec_()

                            else:
                                errorPopUp(parent = self).exec_()

                            self.clearLEs(self.clientsLE1) # Limpiar formulario
                            self.refreshClients()          # Refrescar vista
                            self.lineE57.setFocus()        # Enfocar

                        else:
                            warningPopUp("Apellido no específicado", self).exec_()

                    else:
                        warningPopUp("Nombre no específicado", self).exec_()

                else:
                    errorPopUp("Número de cédula no registrado", self).exec_()

            else:
                warningPopUp("Número de cédula no específicado", self).exec_()

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CAMPOS DE TEXTO
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # LineEdit para ingresar la cédula del cliente
    def on_lineE57_textChanged(self):
        if self.textChanged():
            if self.lineE57.text() != "":
                ci = int(self.lineE57.text())
                if self.db.existClient(ci):
                    client = self.db.getClients(ci)[0]
                    self.lineE58.setText(client.firstname)
                    self.lineE59.setText(client.lastname)
                    self.lineE60.setText(client.phone)
                    self.lineE61.setText(client.email)

                    self.cbox12.clear()
                    self.cbox13.clear()

                    allow = ["Permitir", "No permitir"]
                    disallow = ["No permitir", "Permitir"]

                    if client.debt_permission: self.cbox12.addItems(allow)
                    else: self.cbox12.addItems(disallow)

                    if client.book_permission: self.cbox13.addItems(allow)
                    else: self.cbox13.addItems(disallow)

                else:
                    self.clearLEs(self.clientsLE2)

            else:
                self.clearLEs(self.clientsLE2)

    #==============================================================================================================================================================================
    # VISTA DE RECARGAS
    #==============================================================================================================================================================================

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Refrescar vista de transferencias y componentes asociados
    def refreshTransfers(self):
        self.clearLEs(self.transfersLE0)
        self.clearLEs(self.transfersLE2)
        self.clearLEs(self.transfersLE3)
        self.clearTE(self.textE7)
        self.updateTranfersTable()
        self.refreshSales()

    # Método para refrescar la tabla de transferencias
    def updateTranfersTable(self):
        table = self.table14
        transfers = self.db.getTransfers()

        self.clearTable(table)                                                         # Vaciar la tabla
        table.setRowCount(len(transfers))                                              # Contador de filas
        for i in range(len(transfers)):                                                # Llenar tabla
            table.setItem(i, 0, QTableWidgetItem(str(transfers[i].clerk)))             # Usuario
            table.setItem(i, 1, QTableWidgetItem(str(transfers[i].ci)))                # Cliente
            table.setItem(i, 2, QTableWidgetItem(str(transfers[i].amount)))            # Monto
            table.setItem(i, 3, QTableWidgetItem(str(transfers[i].bank)))              # Banco
            table.setItem(i, 4, QTableWidgetItem(str(transfers[i].confirmation_code))) # Código de confirmación

        self.elem_actual = 0                                            # Definir la fila que se seleccionará
        if len(transfers) > 0: table.selectRow(self.elem_actual)        # Seleccionar fila
        table.resizeColumnsToContents()                                 # Redimensionar columnas segun el contenido
        self.setupTable(table, 4)                                       # Reconfigurar tabla

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Boton aceptar para hacer una recarga de saldo
    def on_pbutton15_pressed(self):
        if self.click():
            if self.lineE47.text() != "":
                ci = int(self.lineE47.text())
                if self.db.existClient(ci):
                    pay_type = self.cbox7.currentText()

                    # Modo de recarga con depósito
                    if pay_type == "Efectivo":
                        if self.lineE158.text() != "":
                            amount = float(self.lineE158.text())
                            self.db.createDeposit(ci, self.user, amount)
                            self.refreshTransfers()
                            self.lineE47.setFocus()

                    # Modo de recarga con transferencia
                    else:
                        if (self.lineE51.text() and self.lineE156.text() and self.lineE157.text() and self.textE7.toPlainText()) != "":
                            amount = float(self.lineE51.text())
                            bank = self.lineE156.text()
                            confirmation_code = self.lineE157.text()
                            description = self.textE7.toPlainText()
                            self.db.createTransfer(ci, self.user, amount, bank, confirmation_code, description)
                            self.refreshTransfers()
                            self.lineE47.setFocus()

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CAMPOS DE TEXTO
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # LineEdit para ingresar la cédula del cliente
    def on_lineE47_textChanged(self):
        if self.textChanged():
            if self.lineE47.text() != "":
                ci = int(self.lineE47.text())
                if self.db.existClient(ci):
                    client = self.db.getClients(ci)[0]
                    self.lineE48.setText(client.firstname)
                    self.lineE49.setText(client.lastname)
                    self.lineE50.setText(str(client.balance))

                else:
                    self.clearLEs(self.transfersLE1)

            else:
                self.clearLEs(self.transfersLE1)

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # COMBO BOX
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # ComboBox para elegir el número de lote
    def on_cbox7_currentIndexChanged(self):
        if self.indexChanged():
            if self.indexMutex:
                pay_type = self.cbox7.currentText()
                if pay_type == "Efectivo": self.subStacked20.setCurrentIndex(1)
                else: self.subStacked20.setCurrentIndex(0)
                self.indexMutex = False

            else:
                self.indexMutex = True

    #==============================================================================================================================================================================
    # VISTA DE USUARIOS
    #==============================================================================================================================================================================

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para refrescar la vista del Ventas y elementos relacionados
    def refreshUsers(self):
        # Configuración de la barra de búsqueda de cliente por CI
        usersID = self.db.getUserNames()
        self.setupSearchBar(self.usersSearch, usersID)

        # Limpiar los campos
        self.clearLEs(self.usersLE0)
        self.clearLEs(self.usersLE1)
        self.clearLEs(self.usersLE2)

        # Refrescar tabla
        self.updateUsersTable(0) # Tabla de colaboradores
        self.updateUsersTable(1) # Tabla de vendedores
        self.updateUsersTable(2) # Tabla de administradores

    # Método para refrescar la tabla de usuarios
    def updateUsersTable(self, permission_mask):
        if permission_mask == 0: table = self.table10
        elif permission_mask == 1: table = self.table9
        else: table = self.table8

        users = self.db.getUsers(permission_mask=permission_mask)
        self.clearTable(table)                                             # Vaciar la tabla
        table.setRowCount(len(users))                                      # Contador de filas
        for i in range(len(users)):                                        # Llenar tabla
            table.setItem(i, 0, QTableWidgetItem(str(users[i].username)))  # Username
            table.setItem(i, 1, QTableWidgetItem(str(users[i].firstname))) # Nombre
            table.setItem(i, 2, QTableWidgetItem(str(users[i].lastname)))  # Apellido
            table.setItem(i, 3, QTableWidgetItem(str(users[i].email)))     # Correo

        self.elem_actual = 0                                 # Definir la fila que se seleccionará
        if len(users) > 0: table.selectRow(self.elem_actual) # Seleccionar fila
        table.resizeColumnsToContents()                      # Redimensionar columnas segun el contenido
        self.setupTable(table)                               # Reconfigurar tabla

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Botón para crear un usuario
    def on_pbutton21_pressed(self):
        if self.click():
            if self.lineE69.text() != "":
                username = self.lineE69.text()
                if not self.db.existUser(username):
                    if self.lineE70.text() != "":
                        if self.lineE71.text() != "":
                            if self.lineE72.text() != "":
                                if self.lineE73.text() != "":

                                    kwargs = {
                                        "username"        : username,
                                        "firstname"       : self.lineE70.text(),
                                        "lastname"        : self.lineE71.text(),
                                        "email"           : self.lineE72.text(),
                                        "password"        : self.lineE73.text(),
                                        "permission_mask" : self.db.getPermissionMask(self.cbox8.currentText())
                                    }

                                    if self.db.createUser(**kwargs):        # Crear usuario
                                        successPopUp(parent = self).exec_()

                                    else:
                                        errorPopUp(parent = self).exec_()

                                    self.refreshUsers()          # Refrescar vista
                                    self.lineE69.setFocus()      # Enfocar

                                else:
                                    warningPopUp("Clave no específicada", self).exec_()

                            else:
                                warningPopUp("Correo no específicado", self).exec_()

                        else:
                            warningPopUp("Apellido no específicado", self).exec_()

                    else:
                        warningPopUp("Nombre no específicado", self).exec_()

                else:
                    errorPopUp("UserID previamente registrado", self).exec_()

            else:
                warningPopUp("UserID no específicado", self).exec_()

    # Botón para editar un usuario
    def on_pbutton23_pressed(self):
        if self.click():
            if self.lineE75.text() != "":
                username = self.lineE75.text()
                if self.db.existUser(username):

                    kwargs = {
                        "username"        : username,
                        "permission_mask" : self.db.getPermissionMask(self.cbox9.currentText())
                    }

                    if self.db.updateUserRange(**kwargs):    # Actualizar cliente
                        successPopUp(parent = self).exec_()

                    else:
                        errorPopUp(parent = self).exec_()

                    self.refreshUsers()               # Refrescar vista
                    self.lineE75.setFocus()           # Enfocar

                else:
                    errorPopUp("UserID no registrado", self).exec_()

            else:
                warningPopUp("UserID no específicado", self).exec_()


    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CAMPOS DE TEXTO
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # LineEdit para ingresar el username en el apartado de editar
    def on_lineE75_textChanged(self):
        if self.textChanged():
            if self.lineE75.text() != "":
                username = self.lineE75.text()
                if self.db.existUser(username):
                    user = self.db.getUsers(username)[0]
                    self.lineE76.setText(user.firstname)
                    self.lineE77.setText(user.lastname)
                    self.lineE78.setText(user.email)

    # LineEdit para ingresar el username en el apartado de consultas
    def on_lineE62_textChanged(self):
        if self.textChanged():
            if self.lineE62.text() != "":
                username = self.lineE62.text()
                if self.db.existUser(username):
                    user = self.db.getUsers(username)[0]
                    self.lineE63.setText(user.firstname)
                    self.lineE64.setText(user.lastname)
                    self.lineE65.setText(user.email)
                    self.lineE66.setText(self.db.getRange(user.permission_mask))

    #==============================================================================================================================================================================
    # VISTA DE CONFIGURACIONES
    #==============================================================================================================================================================================

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Cambiar el tema de la interfáz
    def setStyle(self, name):
        self.setStyleSheet(getStyle(join(stylePath, name)))

    # Método para cargar la información del sistema monetario
    def loadLegalTenders(self):
        legalTenders, query = [], self.db.getLegalTender()     # Obtener los billetes o monedas
        for legalTender in query:                              # Para cada billete o moneda
            legalTenders.append(legalTender.amount)            # Se agrega su denominacion a la lista
        return legalTenders

    # Método para actualizar el comboBox del sistema monetario
    def updateLegalTendersCB(self, legalTenders):
        self.cbox0.clear()                                 # Se limpia el comboBox
        for i in legalTenders:                             # Por cada denominacion
            self.cbox0.addItem(naturalFormat(i))              # Se añade la denominacion formateada

    # Método para cargar la información del usuario
    def loadUserInfo(self):
        user = self.db.getUsers(self.user)[0]
        self.lineE81.setText(user.username)
        self.lineE82.setText(user.firstname)
        self.lineE83.setText(user.lastname)
        self.lineE84.setText(user.email)
        self.lineE85.setText(self.db.getRange(user.permission_mask))

    # Método para cargar las preferencias del usuario
    def loadUserPreferences(self):
        user = self.db.getUsers(self.user)[0]
        if user.profile != "": self.theme = user.profile
        else: self.theme = "blue.qss"
        self.setStyle(self.theme)

    # Método para cambiar el usuario que usa la intefáz
    def changeUser(self, user):
        self.user = user
        self.openTurn(self.user)
        self.refresh()

    # Método para refrescar el sistema monetario
    def refreshLegalTenders(self):
        self.clearLEs(self.confLE1)
        self.legalTenders = self.loadLegalTenders()
        self.updateLegalTendersCB(self.legalTenders)
        self.updateCalc(self.legalTenders)

    # Método para refrescar la vista de Configuraciones y componentes relacionados
    def refreshConfigurations(self):
        self.refreshUsers()
        self.refreshLegalTenders()
        self.clearLEs(self.confLE0)
        self.loadUserInfo()
        self.loadUserPreferences()

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Boton para establecer el tema 0
    def on_theme0_pressed(self):
        if self.click():
            self.setStyle(styles[0])
            self.theme = styles[0]

    # Boton para establecer el tema 1
    def on_theme1_pressed(self):
        if self.click():
            self.setStyle(styles[1])
            self.theme = styles[1]

    # Boton para establecer el tema 2
    def on_theme2_pressed(self):
        if self.click():
            self.setStyle(styles[2])
            self.theme = styles[2]

    # Boton para establecer el tema 3
    def on_theme3_pressed(self):
        if self.click():
            self.setStyle(styles[3])
            self.theme = styles[3]

    # Boton para establecer el tema 4
    def on_theme4_pressed(self):
        if self.click():
            self.setStyle(styles[4])
            self.theme = styles[4]

    # Boton para establecer el tema 5
    def on_theme5_pressed(self):
        if self.click():
            self.setStyle(styles[5])
            self.theme = styles[5]

    # Boton para establecer el tema 6
    def on_theme6_pressed(self):
        if self.click():
            self.setStyle(styles[6])
            self.theme = styles[6]

    # Boton para establecer el tema 7
    def on_theme7_pressed(self):
        if self.click():
            self.setStyle(styles[7])
            self.theme = styles[7]

    # Boton para establecer el tema 0
    def on_theme8_pressed(self):
        if self.click():
            self.setStyle(styles[8])
            self.theme = styles[8]

    # Boton para establecer el tema 1
    def on_theme9_pressed(self):
        if self.click():
            self.setStyle(styles[9])
            self.theme = styles[9]

    # Boton para establecer el tema 2
    def on_theme10_pressed(self):
        if self.click():
            self.setStyle(styles[10])
            self.theme = styles[10]

    # Boton para establecer el tema 3
    def on_theme11_pressed(self):
        if self.click():
            self.setStyle(styles[11])
            self.theme = styles[11]

    # Boton para establecer el tema 4
    def on_theme12_pressed(self):
        if self.click():
            self.setStyle(styles[12])
            self.theme = styles[12]

    # Boton para establecer el tema 5
    def on_theme13_pressed(self):
        if self.click():
            self.setStyle(styles[13])
            self.theme = styles[13]

    # Boton para establecer el tema 6
    def on_theme14_pressed(self):
        if self.click():
            self.setStyle(styles[14])
            self.theme = styles[14]

    # Boton para establecer el tema 7
    def on_theme15_pressed(self):
        if self.click():
            self.setStyle(styles[15])
            self.theme = styles[15]

        # Boton para establecer el tema 0
    def on_theme16_pressed(self):
        if self.click():
            self.setStyle(styles[16])
            self.theme = styles[16]

    # Boton para establecer el tema 1
    def on_theme17_pressed(self):
        if self.click():
            self.setStyle(styles[17])
            self.theme = styles[17]

    # Boton para establecer el tema 2
    def on_theme18_pressed(self):
        if self.click():
            self.setStyle(styles[18])
            self.theme = styles[18]

    # Boton para establecer el tema 3
    def on_theme19_pressed(self):
        if self.click():
            self.setStyle(styles[19])
            self.theme = styles[19]

    # Boton para hacer backup
    def on_pbutton24_pressed(self):
        if self.click():
            self.db.backup()

    # Boton para restaurar desde el ultimo backup
    def on_pbutton25_pressed(self):
        if self.click():
            self.db.restore()
            self.refresh()

    # Boton para guardar cambios
    def on_pbutton26_pressed(self):
        if self.click():
            # Perfil
            if self.subStacked18.currentIndex() == 0:
                if self.lineE82.text() != "":
                    if self.lineE83.text() != "":
                        if self.lineE84.text() != "":
                            if self.db.updateUserInfo(self.user, self.lineE82.text(), self.lineE83.text(), self.lineE84.text()):
                                successPopUp(parent = self).exec_()

                            else:
                                errorPopUp(parent = self).exec_()

                            self.refreshUsers()

                        else:
                            warningPopUp("Correo no específicado", self).exec_()

                    else:
                        warningPopUp("Apellido no específicado", self).exec_()

                else:
                    warningPopUp("Nombre no específicado", self).exec_()

            # Contraseña
            elif self.subStacked18.currentIndex() == 1:
                if self.lineE153.text() != "":
                    password = self.lineE153.text()
                    if self.db.checkPassword(self.user, password):
                        if self.lineE154.text() != "":
                            if self.lineE155.text() != "":
                                if self.lineE154.text() == self.lineE155.text():
                                    newPassword = self.lineE154.text()
                                    if self.db.changePassword(self.user, password, newPassword):
                                        successPopUp(parent = self).exec_()

                                    else:
                                        errorPopUp(parent = self).exec_()

                                    self.clearLEs(self.confLE0)

                                else:
                                    errorPopUp("La clave nueva no coincide con su confirmación", self).exec_()

                            else:
                                warningPopUp("Debe confirmar la clave nueva", self).exec_()

                        else:
                            warningPopUp("Clave nueva no específicada", self).exec_()

                    else:
                        errorPopUp("La clave actual no coincide con la registrada", self).exec_()

                else:
                    warningPopUp("Clave actual no específicado", self).exec_()

            # Tema
            else:
                if self.db.updateUserProfile(self.user, self.theme):
                    successPopUp(parent = self).exec_()

                else:
                    errorPopUp(parent = self).exec_()

    # Boton para cambiar al modo de agregar denominación
    def on_rbutton2_pressed(self):
        if self.click():
            self.setPage(self.subStacked21, 0)
            self.clearLEs(self.confLE1)

    # Boton para cambiar al modo de eliminar denominación
    def on_rbutton3_pressed(self):
        if self.click():
            self.setPage(self.subStacked21, 1)

    # Boton para añadir o eliminar denominaciones en el sistema monetario
    def on_pbutton28_pressed(self):
        if self.click():
            # Modalidad para añadir billetes o monedas
            if self.rbutton2.isChecked():
                if self.lineE88.text() != "":
                    amount = float(self.lineE88.text())
                    if not self.db.existLegalTender(amount):
                        if len(self.legalTenders) < 15:
                            if self.db.createLegalTender(amount):
                                successPopUp(parent = self).exec_()

                            else:
                                errorPopUp(parent = self).exec_()

                            self.refreshLegalTenders()

                        else:
                            errorPopUp("Límite de denominaciones alcanzado", self).exec_()

                    else:
                        errorPopUp("Denominación previamente registrada", self).exec_()

                else:
                    warningPopUp("Debe especificar la denominación", self).exec_()

            # Modalidad para eliminar billetes o monedas
            else:
                amount = self.legalTenders[self.cbox0.currentIndex()]
                if self.db.deleteLegalTender(amount):
                    successPopUp(parent = self).exec_()

                else:
                    errorPopUp(parent = self).exec_()

                self.refreshLegalTenders()

    #==============================================================================================================================================================================
    # MANEJADOR DE EVENTOS DE TECLADO
    #==============================================================================================================================================================================

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            currentPage = self.MainStacked.currentIndex()

            if currentPage == 0:
                # code goes here
                print("XD")

            if currentPage == 1:
                # code goes here
                print("XD")

            elif currentPage == 2:
                # code goes here
                print("XD")

            elif currentPage == 3:
                # code goes here
                print("XD")

            elif currentPage == 4:
                # code goes here
                print("XD")

            elif currentPage == 5:
                # code goes here
                print("XD")

            elif currentPage == 6:
                # code goes here
                print("XD")

    #==============================================================================================================================================================================
    # EVENTO DE CIERRE
    #==============================================================================================================================================================================

    def closeEvent(self,event):
        self.closed.emit()  # Emitir señal para avisarle al sessionManager que se intento cerrar la ventana principal
        event.accept()      # Aceptar el cierre de la ventana principal

###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################
