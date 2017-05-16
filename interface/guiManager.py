# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación de la clase encargada de la interfaz gráfica.

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Christian Oliveros, 01christianol01@gmail.com
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
        productPath = join(join(current, "images"), "inventory")                 # Declarar path para las imágenes de los productos
        break

###################################################################################################################################################################################
## MODÚLOS:
###################################################################################################################################################################################

# Módulo con funciones del sistema operativo
from os import mkdir

# Módulo con funciones para el manejo de rutas del sistema operativo
from os.path import isdir

# Módulo con funciones para manejo de archivos en alto nivel (en especifico para este caso... copiar)
from shutil import copy2

# Módulo que contiene el tipo de dato datetime para hcaer operaciones con fechas
from datetime import datetime

# Módulo que contiene funciones matemáticas
from math import ceil

# Módulo manejador de la base de datos
from db_manager import dbManager

# Módulo con las clases para los popUp
from popUps import errorPopUp, warningPopUp, successPopUp, confirmationPopUp, authorizationPopUp, detailsPopUp, especialPopUp0

# Módulo con los validadores para campos de texto
from validators import intValidator, floatValidator, anyCharacterValidator, validatePhoneNumber, validateEmail, validateName

# Módulo con los validadores para campos de texto
from app_utilities import getStyle, naturalFormat, paragraphFormat, dateTimeFormat, dateFormat, timeFormat, openLink

# Módulo que contiene los recursos de la interfaz
import gui_rc

# Módulo con las herramientas parar trabajar los archivos .ui
from PyQt4.uic import loadUiType

# Módulo con procedimientos de Qt
from PyQt4.QtCore import Qt, QMetaObject, pyqtSignal, QDir, QDate

# Módulo con estructuras de Qt
from PyQt4.QtGui import QMainWindow, QApplication, QStringListModel, QCompleter, QHeaderView, QTableWidgetItem, QFileDialog, QIcon, QLineEdit, QLabel, QPushButton

###################################################################################################################################################################################
## CONSTANTES:
###################################################################################################################################################################################

# UI
MainUI = "MainWindow.ui"

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

# Interfaz .ui creada con qt designer
form_class = loadUiType(join(UIpath, MainUI))[0]

###################################################################################################################################################################################
## MANEJADOR DE LA INTERFAZ GRÁFICA DE LA VENTANA PRINCIPAL:
###################################################################################################################################################################################

class guiManager(QMainWindow, form_class):
    closed = pyqtSignal() # Señal para saber si se cerró la ventana

    #==============================================================================================================================================================================
    # CONSTRUCTOR DE LA CLASE
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
        self.closeForgotten = False          # Variable para saber si hay un día abierto que no corresponde al día actual
        self.pageLimit = 25                  # Valor por defecto para entradas por página en las tablas

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # PREFERENCIAS DE USUARIO
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        self.theme = "blue.qss"

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS DE PROPOSITO GENERAL
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Barras de búsqueda por cédula:
        self.clientsSearch = [self.lineE16, self.lineE17, self.lineE47, self.lineE52, self.lineE57]

        # Barras de búsqueda por nombre de producto:
        self.productSearch = [self.lineE23, self.lineE26, self.lineE33]

        # Barras de búsqueda por nombre de proveedor
        self.providersSearch = [self.lineE149, self.lineE34]

        # Barras de búsqueda por username de usuario
        self.usersSearch = [self.lineE62, self.lineE75]

        # Tablas
        self.tables = [self.table0, self.table1, self.table2, self.table3, self.table4, self.table5, self.table6, self.table7,
                        self.table8, self.table9, self.table10, self.table11, self.table12, self.table13, self.table14, self.table15, self.table16]

        # Páginas
        self.tablesPages = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.tablesTotalPages = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        # Contenido de las tablas
        self.depositsTableItems  = []
        self.transfersTableItems = []
        self.usersTableItems0    = []
        self.usersTableItems1    = []
        self.usersTableItems2    = []
        self.providersTableItems = []
        self.movementsTableItems = []

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE CAJA
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de Caja y Periodo
        self.cashLE0 = [self.lineE2, self.lineE3, self.lineE4]
        self.cashLE1 = [self.lineE1, self.lineE2, self.lineE3, self.lineE4, self.lineE6, self.lineE15]

        # Apartado de movimientos
        self.cashLE2 = [self.lineE8]
        self.cashLE3 = [self.lineE9]

        # Calculadora
        self.calc0 = [self.calcT0, self.calcT1, self.calcT2, self.calcT3, self.calcT4, self.calcT5, self.calcT6, self.calcT7, self.calcT8, self.calcT9, self.calcT10, self.calcT11, self.calcT12, self.calcT13, self.calcT14]

        self.calc1 = [self.calcLE0, self.calcLE1, self.calcLE2, self.calcLE3, self.calcLE4, self.calcLE5, self.calcLE6, self.calcLE7, self.calcLE8, self.calcLE9, self.calcLE10, self.calcLE11, self.calcLE12, self.calcLE13, self.calcLE14]

        # LineEdits para solo números reales
        self.cashOF = [self.lineE1, self.lineE4, self.lineE6, self.lineE8, self.lineE9]

        # Tablas
        self.cashTables = [self.table15]

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

        # LineEdits para solo números reales
        self.lotsOF = [self.lineE35]

        # LineEdits para solo números enteros
        self.lotsOI = [self.lineE37, self.lineE38]

        # LineEdits para solo números reales
        self.productsOF0 = [self.lineE27]
        self.productsOF1 = [self.lineE28]

        # Tablas
        self.productsTables = [self.table0, self.table1, self.table2]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE PROVEEDORES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de proveedores
        self.providersLE0 = [self.lineE146, self.lineE147, self.lineE148]
        self.providersLE1 = [self.lineE149, self.lineE150, self.lineE151]
        self.providersLE2 = [self.lineE150, self.lineE151]
        self.providersTE0 = [self.textE1, self.textE2]
        self.providersTE1 = [self.textE3, self.textE4]

        # Tablas
        self.providersTables = [self.table13]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE CLIENTES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de clientes
        self.clientsLE0 = [self.lineE52, self.lineE53, self.lineE54, self.lineE55, self.lineE56]
        self.clientsLE1 = [self.lineE57, self.lineE58, self.lineE59, self.lineE60, self.lineE61]
        self.clientsLE2 = [self.lineE58, self.lineE59, self.lineE60, self.lineE61]
        self.clientsLE3 = [self.lineE16, self.lineE31, self.lineE32, self.lineE80, self.lineE67, self.lineE68]
        self.clientsLE4 = [self.lineE31, self.lineE32, self.lineE80, self.lineE67, self.lineE68]

        # LineEdits para solo números reales
        self.clientsOF = [self.lineE68]

        # Tablas
        self.clientsTables = [self.table6, self.table7]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE RECARGAS
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de cliente
        self.transfersLE0 = [self.lineE47, self.lineE48, self.lineE49, self.lineE50, self.lineE90]
        self.transfersLE1 = [self.lineE48, self.lineE49, self.lineE50, self.lineE90]
        self.transfersLE2 = [self.lineE51, self.lineE156, self.lineE157]
        self.transfersLE3 = [self.lineE158]

        # LineEdits para solo números reales
        self.transfersOF = [self.lineE51, self.lineE158]

        # Tablas
        self.transfersTables = [self.table14, self.table16]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE USUARIOS
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de usuarios
        self.usersLE0 = [self.lineE62, self.lineE63, self.lineE64, self.lineE65, self.lineE66]
        self.usersLE1 = [self.lineE69, self.lineE70, self.lineE71, self.lineE72, self.lineE73, self.lineE74]
        self.usersLE2 = [self.lineE75, self.lineE76, self.lineE77, self.lineE78]

        # Tablas
        self.usersTables = [self.table8, self.table9, self.table10]

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

        # LineEdits para solo números reales
        self.salesOF = [self.lineE22, self.lineE152]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE CONFIGURACIONES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de cambio de contraseña
        self.confLE0 = [self.lineE153, self.lineE154, self.lineE155]

        # Apartado de sistema monetario
        self.confLE1 = [self.lineE88]

        # LineEdits para solo números
        self.confOF = [self.lineE88]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # CARGAR CONFIGURACIONES INICIALES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Se connectan los botones entre otras cosas con algunos de los métodos definidos a continuación
        QMetaObject.connectSlotsByName(self)

        # Crear respaldo de la base de datos
        self.db.backup()

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
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

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

    # Cambiar el tema de la interfáz
    def setStyle(self, theme):
        style = getStyle(join(stylePath, theme))
        if style != None:
            self.setStyleSheet(style)

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
        validator = intValidator()
        for lineE in listLE:
            if numValidator: lineE.setValidator(validator)
            lineE.setCompleter(LEcompleter)

    # Método para configurar campos para ingresar cualquier cosa
    def setAnyCharacter(self, listAC):
        validator = anyCharacterValidator()
        for item in listAC: item.setValidator(validator)

    # Método para configurar campos para solo ingresar números
    def setOnlyInteger(self, listON):
        validator = intValidator()
        for item in listON: item.setValidator(validator)

    # Método para configurar campos para solo ingresar números
    def setOnlyFloat(self, listON):
        validator = floatValidator()
        for item in listON: item.setValidator(validator)

    # Método para setear en 0 una lista spinLine
    def clearSpinLines(self, listSL):
        for spinL in listSL: self.clearSpinLine(spinL)

    # Método para setear en 0 un spinLine
    def clearSpinLine(self, spinL):
        spinL.setText("0")
        self.add0.setEnabled(False)
        self.substract0.setEnabled(False)

    # Obtener una lista con los nombres de todos los productos
    def getProductList(self, params, mode = 0):
        if mode == 0: params.update({"available" : None, "page" : self.tablesPages[self.tables.index(self.table2)]})
        elif mode == 1: params.update({"available" : True, "page" :self.tablesPages[self.tables.index(self.table0)]})
        else: params.update({"available" : False, "page" : self.tablesPages[self.tables.index(self.table1)]})

        productsList = self.db.getProducts(**params)

        if len(params) == 4:
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

    # Método para limpiar un DateEdit
    def clearDE(self, dateEdit, readOnly):
        dateEdit.setReadOnly(readOnly)
        dateEdit.setDate(QDate().currentDate())

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
        for table in tables:
            self.setupTable(table)
            table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

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
        self.refreshPages()
        self.refreshSales()
        self.refreshProviders()
        self.refreshTransfers()
        self.refreshConfigurations()
        self.refreshCash()

        # Si el usuario tiene rango mayor a Colaborador
        if self.db.getUserPermissionMask(self.user) > 0:
            if self.MainStacked.currentIndex() != 10:
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

        # Verificar si no se cerró el último día abierto anterior al día actual
        self.verifyCloseForgotten()

    # Método para aplicar las configuraciones iniciales
    def generalSetup(self):
        # Centrar posición de la ventana
        self.center()

        # Establecer tamaño y ocultar botones de la ventana
        self.setSize()

        # Configurar los spin box
        if not self.rbutton7.isChecked():
            self.setOnlyFloat(self.productsOF0)
            self.setAnyCharacter(self.productsOF1)

        else:
            self.setOnlyFloat(self.productsOF1)
            self.setAnyCharacter(self.productsOF0)

        self.setOnlyFloat(self.lotsOF)
        self.setOnlyFloat(self.confOF)
        self.setOnlyFloat(self.clientsOF)
        self.setOnlyFloat(self.transfersOF)
        self.setOnlyFloat(self.salesOF)
        self.setOnlyFloat(self.cashOF)
        self.setOnlyInteger(self.calc1)
        self.setOnlyInteger(self.lotsOI)
        self.setOnlyInteger(self.spinBox)
        self.add0.setEnabled(False)
        self.substract0.setEnabled(False)
        self.add0.setAutoRepeat(True)
        self.substract0.setAutoRepeat(True)
        self.setupTables(self.tables)
        self.textE0.anchorClicked.connect(openLink)

    # Método para verificar si no se hizo cierre de un día anterior
    def verifyCloseForgotten(self):
        if self.db.isOpenDay():
            date = self.db.getDayStartAndEnd()[0].recorded.date()
            current = datetime.now().date()
            if date < current:
                self.closeForgotten = True
                warningPopUp("Debe realizar cierre de caja", self).exec_()

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
            # Si no hay cierres olvidados:
            if not self.closeForgotten:
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

            # Si no hay día abierto olvidado
            else:
                warningPopUp("Debe realizar cierre de caja", self).exec_()

    # Cambiar a la página de inventario
    def on_inventory_pressed(self):
        if self.click():
            # Si el usuario tiene rango mayor a Colaborador
            if self.db.getUserPermissionMask(self.user) > 1:
                # Si no hay cierres olvidados:
                if not self.closeForgotten:
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

                # Si no hay día abierto olvidado
                else:
                    warningPopUp("Debe realizar cierre de caja", self).exec_()

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
                # Si no hay cierres olvidados:
                if not self.closeForgotten:
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

                # Si no hay día abierto olvidado
                else:
                    warningPopUp("Debe realizar cierre de caja", self).exec_()

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
    def on_arrow35_pressed(self): self.changePage(self.subStacked22)     # Cambiar la página del subStacked18 hacia la derecha

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
    def on_arrow34_pressed(self): self.changePage(self.subStacked22, 1)  # Cambiar la página del subStacked18 hacia la izquierda

    #==============================================================================================================================================================================
    # PAGINACIÓN
    #==============================================================================================================================================================================

    # Calcular el total de páginas de las tablas de productos
    def getProductsTotalPages(self):
        self.tablesTotalPages[self.tables.index(self.table0)] = ceil(self.db.getProductsCount(True)/self.pageLimit)   # Disponibles
        self.tablesTotalPages[self.tables.index(self.table1)] = ceil(self.db.getProductsCount(False)/self.pageLimit)  # No disponibles
        self.tablesTotalPages[self.tables.index(self.table2)] = ceil(self.db.getProductsCount()/self.pageLimit)       # Todos

        self.checkValidPage(self.productsTables)

    # Calcular el total de páginas de las tablas de clientes
    def getClientsTotalPages(self):
        self.tablesTotalPages[self.tables.index(self.table6)] = ceil(self.db.getClientsCount(True)/self.pageLimit)  # Endeudados
        self.tablesTotalPages[self.tables.index(self.table7)] = ceil(self.db.getClientsCount()/self.pageLimit)      # No endeudados

        self.checkValidPage(self.clientsTables)

    # Calcular el total de páginas de las tablas de usuarios
    def getUsersTotalPages(self):
        self.tablesTotalPages[self.tables.index(self.table8)]  = ceil(self.db.getUsersCount(2)/self.pageLimit)  # Colaboradores
        self.tablesTotalPages[self.tables.index(self.table9)]  = ceil(self.db.getUsersCount(1)/self.pageLimit)  # Vendedores
        self.tablesTotalPages[self.tables.index(self.table10)] = ceil(self.db.getUsersCount(0)/self.pageLimit)  # Administradores

        self.checkValidPage(self.usersTables)

    # Calcular el total de páginas de la tabla de proveedores
    def getProvidersTotalPages(self):
        self.tablesTotalPages[self.tables.index(self.table13)] = ceil(self.db.getProvidersCount()/self.pageLimit)

        self.checkValidPage(self.providersTables)

    # Calcular el total de páginas de las tablas de recargas
    def getTransfersTotalPages(self):
        self.tablesTotalPages[self.tables.index(self.table14)] = ceil(self.db.getTransfersCount()/self.pageLimit)  # Transferencias
        self.tablesTotalPages[self.tables.index(self.table16)] = ceil(self.db.getDepositsCount()/self.pageLimit)   # Efectivo

        self.checkValidPage(self.transfersTables)

    # Calcular el total de páginas de la tabla de movimientos
    def getMovementsTotalPages(self):
        self.tablesTotalPages[self.tables.index(self.table15)] = ceil(self.db.getMovementsCount()/self.pageLimit)

        self.checkValidPage(self.cashTables)

    # Validador de número de página
    def checkValidPage(self, tables):
        for table in tables:
            index = self.tables.index(table)
            self.tablesPages[index] = max(min(self.tablesPages[index], self.tablesTotalPages[index]), 1)

    # Setear todas las páginas en 1
    def refreshPages(self):
        for i in range(len(self.tablesPages)):
            self.tablesPages[i] = 1

    # Ir a la primera página
    def firstPage(self, table):
        index = self.tables.index(table)
        self.tablesPages[index] = 1

    # Ir a la página anterior
    def previousPage(self, table):
        index = self.tables.index(table)
        if self.tablesPages[index] > 1:
            self.tablesPages[index] -= 1

    # Ir a la págna siguiente
    def nextPage(self, table):
        index = self.tables.index(table)
        if self.tablesPages[index] < self.tablesTotalPages[index]:
            self.tablesPages[index] += 1

    # Ir a la última página
    def lastPage(self, table):
        index = self.tables.index(table)
        self.tablesPages[index] = self.tablesTotalPages[index]

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Todas las flechas para ir a la primera página
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Tablas de productos
    def on_arrow42_pressed(self):
        if self.click():
            subStackedPage = self.subStacked5.currentIndex()

            # Disponibles
            if subStackedPage == 0:
                self.firstPage(self.table0)
                self.productsInfoAvailable = self.getProductList(self.productsParams1, 1)
                self.updateProductsTable(self.table0, self.productsInfoAvailable)

            # No disponibles
            elif subStackedPage == 1:
                self.firstPage(self.table1)
                self.productsInfoNotAvailable = self.getProductList(self.productsParams1, 2)
                self.updateProductsTable(self.table1, self.productsInfoNotAvailable)

            # Todos
            else:
                self.firstPage(self.table2)
                self.productsInfo = self.getProductList(self.productsParams1)
                self.updateProductsTable(self.table2, self.productsInfo)

    # Tablas de clientes
    def on_arrow58_pressed(self):
        if self.click():
            subStackedPage = self.subStacked9.currentIndex()

            # Endeudados
            if subStackedPage == 0:
                self.firstPage(self.table7)
                self.updateClientsTable()

            # No endeudados
            else:
                self.firstPage(self.table6)
                self.updateClientsTable(True)

    # Tablas de usuarios
    def on_arrow62_pressed(self):
        if self.click():
            subStackedPage = self.subStacked11.currentIndex()

            # Aministradores
            if subStackedPage == 0:
                self.firstPage(self.table8)
                self.updateUsersTable(2)

            # Vendedores
            elif subStackedPage == 1:
                self.firstPage(self.table9)
                self.updateUsersTable(1)

            # Colaboradores
            else:
                self.firstPage(self.table10)
                self.updateUsersTable(0)

    # Tablas de libros
    def on_arrow66_pressed(self):
        if self.click():
            self.firstPage(self.table12)

    # Tabla de proveedores
    def on_arrow70_pressed(self):
        if self.click():
            self.firstPage(self.table13)
            self.updateProvidersTable()

    # Tablas de recargas
    def on_arrow74_pressed(self):
        if self.click():
            subStackedPage = self.subStacked22.currentIndex()

            # Transferencias
            if subStackedPage == 0:
                self.firstPage(self.table14)
                self.updateTranfersTable()

            # Depósitos en efectivo
            else:
                self.firstPage(self.table16)
                self.updateDepositsTable()

    # Tabla de movimientos
    def on_arrow78_pressed(self):
        if self.click():
            self.firstPage(self.table15)
            self.updateMovementsTable()

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Todas las flechas para ir a la página anterior
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Tablas de productos
    def on_arrow43_pressed(self):
        if self.click():
            subStackedPage = self.subStacked5.currentIndex()

            # Disponibles
            if subStackedPage == 0:
                self.previousPage(self.table0)
                self.productsInfoAvailable = self.getProductList(self.productsParams1, 1)
                self.updateProductsTable(self.table0, self.productsInfoAvailable)

            # No disponibles
            elif subStackedPage == 1:
                self.previousPage(self.table1)
                self.productsInfoNotAvailable = self.getProductList(self.productsParams1, 2)
                self.updateProductsTable(self.table1, self.productsInfoNotAvailable)

            # Todos
            else:
                self.previousPage(self.table2)
                self.productsInfo = self.getProductList(self.productsParams1)
                self.updateProductsTable(self.table2, self.productsInfo)

    # Tablas de clientes
    def on_arrow59_pressed(self):
        if self.click():
            subStackedPage = self.subStacked9.currentIndex()

            # Endeudados
            if subStackedPage == 0:
                self.previousPage(self.table7)
                self.updateClientsTable()

            # No endeud
            else:
                self.previousPage(self.table6)
                self.updateClientsTable(True)

    # Tablas de usuarios
    def on_arrow63_pressed(self):
        if self.click():
            subStackedPage = self.subStacked11.currentIndex()

            # Aministradores
            if subStackedPage == 0:
                self.previousPage(self.table8)
                self.updateUsersTable(2)

            # Vendedores
            elif subStackedPage == 1:
                self.previousPage(self.table9)
                self.updateUsersTable(1)

            # Colaboradores
            else:
                self.previousPage(self.table10)
                self.updateUsersTable(0)

    # Tablas de libros
    def on_arrow67_pressed(self):
        if self.click():
            self.previousPage(self.table12)

    # Tabla de proveedores
    def on_arrow71_pressed(self):
        if self.click():
            self.previousPage(self.table13)
            self.updateProvidersTable()

    # Tablas de recargas
    def on_arrow75_pressed(self):
        if self.click():
            subStackedPage = self.subStacked22.currentIndex()

            # Transferencias
            if subStackedPage == 0:
                self.previousPage(self.table14)
                self.updateTranfersTable()

            # Depósitos en efectivo
            else:
                self.previousPage(self.table16)
                self.updateDepositsTable()

    # Tabla de movimientos
    def on_arrow79_pressed(self):
        if self.click():
            self.previousPage(self.table15)
            self.updateMovementsTable()

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Todas las flechas para ir a la página siguiente
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Tablas de productos
    def on_arrow44_pressed(self):
        if self.click():
            subStackedPage = self.subStacked5.currentIndex()

            # Disponibles
            if subStackedPage == 0:
                self.nextPage(self.table0)
                self.productsInfoAvailable = self.getProductList(self.productsParams1, 1)
                self.updateProductsTable(self.table0, self.productsInfoAvailable)

            # No disponibles
            elif subStackedPage == 1:
                self.nextPage(self.table1)
                self.productsInfoNotAvailable = self.getProductList(self.productsParams1, 2)
                self.updateProductsTable(self.table1, self.productsInfoNotAvailable)

            # Todos
            else:
                self.nextPage(self.table2)
                self.productsInfo = self.getProductList(self.productsParams1)
                self.updateProductsTable(self.table2, self.productsInfo)

    # Tablas de clientes
    def on_arrow60_pressed(self):
        if self.click():
            subStackedPage = self.subStacked9.currentIndex()

            # Endeudados
            if subStackedPage == 0:
                self.nextPage(self.table7)
                self.updateClientsTable()

            # No endeudados
            else:
                self.nextPage(self.table6)
                self.updateClientsTable(True)

    # Tablas de usuarios
    def on_arrow64_pressed(self):
        if self.click():
            subStackedPage = self.subStacked11.currentIndex()

            # Aministradores
            if subStackedPage == 0:
                self.nextPage(self.table8)
                self.updateUsersTable(2)

            # Vendedores
            elif subStackedPage == 1:
                self.nextPage(self.table9)
                self.updateUsersTable(1)

            # Colaboradores
            else:
                self.nextPage(self.table10)
                self.updateUsersTable(0)

    # Tablas de libros
    def on_arrow68_pressed(self):
        if self.click():
            self.nextPage(self.table12)

    # Tabla de proveedores
    def on_arrow72_pressed(self):
        if self.click():
            self.nextPage(self.table13)
            self.updateProvidersTable()

    # Tablas de recargas
    def on_arrow76_pressed(self):
        if self.click():
            subStackedPage = self.subStacked22.currentIndex()

            # Transferencias
            if subStackedPage == 0:
                self.nextPage(self.table14)
                self.updateTranfersTable()

            # Depósitos en efectivo
            else:
                self.nextPage(self.table16)
                self.updateDepositsTable()

    # Tabla de movimientos
    def on_arrow80_pressed(self):
        if self.click():
            self.nextPage(self.table15)
            self.updateMovementsTable()

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Todas las flechas para ir a la última página
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Tablas de productos
    def on_arrow45_pressed(self):
        if self.click():
            subStackedPage = self.subStacked5.currentIndex()

            # Disponibles
            if subStackedPage == 0:
                self.lastPage(self.table0)
                self.productsInfoAvailable = self.getProductList(self.productsParams1, 1)
                self.updateProductsTable(self.table0, self.productsInfoAvailable)

            # No disponibles
            elif subStackedPage == 1:
                self.lastPage(self.table1)
                self.productsInfoNotAvailable = self.getProductList(self.productsParams1, 2)
                self.updateProductsTable(self.table1, self.productsInfoNotAvailable)

            # Todos
            else:
                self.lastPage(self.table2)
                self.productsInfo = self.getProductList(self.productsParams1)
                self.updateProductsTable(self.table2, self.productsInfo)

    # Tablas de clientes
    def on_arrow61_pressed(self):
        if self.click():
            subStackedPage = self.subStacked9.currentIndex()

            # Endeudados
            if subStackedPage == 0:
                self.lastPage(self.table7)
                self.updateClientsTable()

            # No endeudados
            else:
                self.lastPage(self.table6)
                self.updateClientsTable(True)

    # Tablas de usuarios
    def on_arrow65_pressed(self):
        if self.click():
            subStackedPage = self.subStacked11.currentIndex()

            # Aministradores
            if subStackedPage == 0:
                self.lastPage(self.table8)
                self.updateUsersTable(2)

            # Vendedores
            elif subStackedPage == 1:
                self.lastPage(self.table9)
                self.updateUsersTable(1)

            # Colaboradores
            else:
                self.lastPage(self.table10)
                self.updateUsersTable(0)

    # Tablas de libros
    def on_arrow69_pressed(self):
        if self.click():
            self.lastPage(self.table12)

    # Tabla de proveedores
    def on_arrow73_pressed(self):
        if self.click():
            self.lastPage(self.table13)
            self.updateProvidersTable()

    # Tablas de recargas
    def on_arrow77_pressed(self):
        if self.click():
            subStackedPage = self.subStacked22.currentIndex()

            # Transferencias
            if subStackedPage == 0:
                self.lastPage(self.table14)
                self.updateTranfersTable()

            # Depósitos en efectivo
            else:
                self.lastPage(self.table16)
                self.updateDepositsTable()

    # Tabla de movimientos
    def on_arrow81_pressed(self):
        if self.click():
            self.lastPage(self.table15)
            self.updateMovementsTable()

    #==============================================================================================================================================================================
    # VISTA DE CAJA
    #==============================================================================================================================================================================
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para actualizar caja
    def refreshCash(self):
        if self.db.isOpenPeriod():
            self.setPage(self.subStacked2, 1)                                        # Cambiar a la página para ver y cerrar un periodo
            period = self.db.getPeriodStartAndEnd()[0]                               # Obtener información del inicio del periodo
            name = period.description                                                # Obtener nombre del periodo
            startDate = period.recorded                                              # Obtener fecha de inicio del periodo
            cash, bank = self.db.getBalance(lower_date=startDate)                    # Obtener dinero en efectivo y en banco ganado durante el periodo
            self.lineE10.setText(name)                                               # Actualizar campo de nombre del periodo
            self.lineE11.setText(dateFormat(startDate))                          # Actualizar campo de fecha de inicio
            self.lineE13.setText(str(cash + period.cash_total))                      # Actualizar campo de efectivo en periodo
            self.lineE14.setText(str(bank + period.total_money - period.cash_total)) # Actualizar campo de banco en periodo

            if self.db.isOpenDay():
                self.setPage(self.subStacked1, 1)                                    # Cambiar a la página para ver y cerrar un dia
                day = self.db.getDayStartAndEnd()[0]                                 # Obtener información del inicio del día
                name = day.description                                               # Obtener nombre del día
                startDate = day.recorded                                             # Obtener fecha de inicio del día
                dayCash, dayBank = self.db.getBalance(lower_date=startDate)          # Obtener dinero en efectivo y en banco ganado en la fecha
                self.lineE2.setText(str(dayCash + day.cash_total))     	             # Actualizar campo de efectivo
                self.lineE3.setText(str(dayBank + day.total_money - day.cash_total)) # Actualizar campo de banco

            else:
                self.setPage(self.subStacked1, 0)                       # Cambiar a la página para abrir un día
                self.clearLEs(self.cashLE0)                             # Limpiar los campos de caja

        else:
            self.setPage(self.subStacked2, 0)                           # Cambiar a la página para abrir un nuevo periodo
            self.clearLEs(self.cashLE1)                                 # Limpiar los campos de los apartados de periodo y caja

        self.clearLEs(self.calc1)                                       # Limpiar calculadora
        self.getMovementsTotalPages()
        self.updateMovementsTable()

    # Método para configurar la calculadora
    def updateCalc(self, legalTenders):
        for i in range(len(self.calc0)):
            if i < len(legalTenders):
                self.calc0[i].setText(naturalFormat(legalTenders[i]))
                self.calc1[i].setReadOnly(False)

            else:
                self.calc0[i].setText("0")
                self.calc1[i].setReadOnly(True)

        self.clearLEs(self.calc1)
        self.setStyle(self.theme)

    # Método para realizar la suma en la calculadora
    def executeCalc(self, legalTenders):
        total = 0.0
        for i in range(len(legalTenders)):
            if self.calc1[i].text() != "":
                total += float(self.calc1[i].text())*float(legalTenders[i])
        self.lineE79.setText(naturalFormat(total))

    # Método para convertir el identificador númerico de tipo de operación a un identificador sde tipo string
    def opTypeConversion(self, op_type, open_record, cash_balance):
        if op_type == 0:
            if open_record: movement = "Apertura de periodo"
            else: movement = "Cierre de periodo"
        elif op_type == 1:
            if open_record: movement = "Apertura de caja"
            else: movement = "Cierre caja"
        elif op_type == 3:
            if cash_balance > 0: movement = "Ingreso en efectivo"
            else: movement = "Ingreso en banco"
        else:
            if cash_balance > 0: movement = "Egreso en efectivo"
            else: movement = "Egreso en banco"

        return movement

    # Método para refrescar la tabla de movimientos de caja
    def updateMovementsTable(self):
        table = self.table15
        self.movementsTableItems = self.db.getMovements(limit=self.pageLimit, page=self.tablesPages[self.tables.index(table)])

        self.clearTable(table)                                             # Vaciar la tabla
        table.setRowCount(len(self.movementsTableItems))                   # Contador de filas
        for i in range(len(self.movementsTableItems)):                     # Llenar tabla
            op_type      = self.movementsTableItems[i].op_type
            clerk        = self.movementsTableItems[i].clerk
            open_record  = self.movementsTableItems[i].open_record
            cash_balance = self.movementsTableItems[i].cash_balance
            cash_total   = str(self.movementsTableItems[i].cash_total)
            date         = dateFormat(self.movementsTableItems[i].recorded)
            time         = timeFormat(self.movementsTableItems[i].recorded)
            movement     = self.opTypeConversion(op_type, open_record, cash_balance)

            table.setItem(i, 0, QTableWidgetItem(movement))    # Tipo
            table.setItem(i, 1, QTableWidgetItem(clerk))       # Usuario
            table.setItem(i, 2, QTableWidgetItem(cash_total))  # Monto
            table.setItem(i, 3, QTableWidgetItem(date))        # Fecha
            table.setItem(i, 4, QTableWidgetItem(time))        # Hora

        self.elem_actual = 0                                      # Definir la fila que se seleccionará
        if len(self.movementsTableItems) > 0: table.selectRow(self.elem_actual)  # Seleccionar fila
        table.resizeColumnsToContents()                           # Redimensionar columnas segun el contenido
        self.setupTable(table, 2)                                 # Reconfigurar tabla

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Boton para abrir día
    def on_pbutton3_pressed(self):
        if self.click():
            if self.db.isOpenPeriod():
                if self.lineE4.text() != "":

                    # Argumentos
                    kwargs = {
                        "clerk"          : self.user,
                        "starting_cash"  : float(self.lineE4.text()),
                        "starting_total" : float(self.lineE4.text()),
                        "description"    : self.cbox2.currentText()
                    }

                    # Abrir Día
                    if self.db.startDay(**kwargs) == (True, True):
                        successPopUp(parent = self).exec_()
                    else:
                        errorPopUp("Error desconocido al intentar abrir el día", self).exec_()

                    # Abrir turno
                    if self.db.startTurn(self.user) != (True, True):
                        errorPopUp("Error desconocido al intentar abrir el turno", self).exec_()

                    # Refrescar la interfaz
                    self.refreshCash()

                else:
                    warningPopUp("Debe especificar el efectivo para aperturar", self).exec_()

            else:
                warningPopUp("Falta apertura de periodo", self).exec_()

    # Boton para finalizar día
    def on_pbutton4_pressed(self):
        if self.click():

            # Argumentos
            kwargs = {
                "clerk"       : self.user,
                "description" : self.cbox3.currentText()
            }

            # Cerrar turno
            if not self.db.closeTurn(self.user):
                errorPopUp("Error desconocido al intentar cerrar el turno", self).exec_()

            # Cerrar día
            if self.db.closeDay(**kwargs):
                successPopUp(parent = self).exec_()
            else:
                errorPopUp("Error desconocido al intentar cerrar el día", self).exec_()

            # Marcar que no hay cierres olvidados
            self.closeForgotten = False

            # Refrescar la interfaz
            self.refreshCash()

    # Boton para abrir periodo
    def on_pbutton5_pressed(self):
        if self.click():
            if self.lineE15.text() != "":
                if self.lineE1.text() != "":
                    if self.lineE6.text() != "":
                        if self.db.getUserPermissionMask(self.user) > 1:

                            # Argumentos
                            kwargs = {
                                "clerk"          : self.user,
                                "starting_cash"  : float(self.lineE1.text()),
                                "starting_total" : float(self.lineE1.text()) + float(self.lineE6.text()),
                                "description"    : self.lineE15.text()
                            }

                            # Abrir periodo
                            if self.db.startPeriod(**kwargs):
                                successPopUp(parent = self).exec_()
                            else:
                                errorPopUp("Error desconocido al intentar abrir el periodo", self).exec_()

                            # Refrescar la interfaz
                            self.refreshCash()

                        else:
                            errorPopUp("No tiene permiso para realizar esta acción", self).exec_()

                    else:
                        warningPopUp("Falta específicar dinero inicial en banco", self).exec_()

                else:
                    warningPopUp("Falta específicar dinero inicial en efectivo", self).exec_()

            else:
                warningPopUp("Falta específicar un nombre", self).exec_()

    # Boton para finalizar periodo
    def on_pbutton6_pressed(self):
        if self.click():
            if not self.db.isOpenDay():
                if self.db.getUserPermissionMask(self.user) > 1:

                    # Cerrar periodo
                    if self.db.closePeriod(self.user):
                        successPopUp(parent = self).exec_()
                    else:
                        errorPopUp("Error desconocido al intentar cerrar el periodo", self).exec_()

                    # Refrescar la interfaz
                    self.refreshCash()

                else:
                    errorPopUp("No tiene permiso para realizar esta acción", self).exec_()

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

                        # Argumentos
                        kwargs = {"clerk" : self.user, "description" : self.cbox21.currentText()}

                        # Modalidad de efectivo
                        if self.cbox1.currentText() == "Efectivo":
                            kwargs["cash_balance"] = float(self.lineE8.text())

                        # Modalidad de banco
                        else:
                            kwargs["transfer_balance"] = float(self.lineE8.text())

                        # Crear movimiento
                        if self.db.incomeOperation(**kwargs):
                            # Operación exitosa
                            successPopUp(parent = self).exec_()
                            # Refrescar
                            self.refreshCash()

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

                        # Argumentos
                        kwargs = {"clerk" : self.user, "description" : self.cbox23.currentText()}

                        # Modalidad de efectivo
                        if self.cbox1.currentText() == "Efectivo":
                            kwargs["cash_balance"] = float(self.lineE9.text())

                        # Modalidad de banco
                        else:
                            kwargs["transfer_balance"] = float(self.lineE9.text())

                        # Crear movimiento
                        if self.db.expenditureOperation(**kwargs):
                            # Operación exitosa
                            successPopUp(parent = self).exec_()
                            # Refrescar
                            self.refreshCash()

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

    # Boton para limpiar calculadora
    def on_cancelpb24_pressed(self):
        if self.click():
            self.clearLEs(self.calc1)

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

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # TABLAS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Clickear una fila de la tabla de movimientos
    def on_table15_itemClicked(self, item):
        if self.rowChanged():
            # Obtener la información completa del movimiento
            item = self.table15.selectedItems()
            selected = [item[0].text(), item[1].text(), item[2].text(), item[3].text(), item[4].text()]

            movement = None
            for elem in self.movementsTableItems:
                op_type      = elem.op_type
                open_record  = elem.open_record
                cash_balance = elem.cash_balance

                op_name = self.opTypeConversion(op_type, open_record, cash_balance)
                clerk   = elem.clerk
                amount  = str(elem.cash_total)
                date    = dateFormat(elem.recorded)
                time    = timeFormat(elem.recorded)

                current = [op_name, clerk, amount, date, time]

                if selected == current:
                    movement = current + [paragraphFormat(elem.description)]
                    break

            if movement != None:
                kwargs = [
                    ("Tipo",        movement[0]),
                    ("Usuario",     movement[1]),
                    ("Monto",       movement[2]),
                    ("Fecha",       movement[3]),
                    ("Hora",        movement[4]),
                    ("Descripción", movement[5])
                ]

                detailsPopUp(kwargs, self).exec_()

    #==============================================================================================================================================================================
    # VISTA DE VENTAS
    #==============================================================================================================================================================================

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para refrescar la vista del Ventas y elementos relacionados
    def refreshSales(self):
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
        self.setupTable(table)                                    # Reconfigurar tabla

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
            if self.lineE17.text() == "": ci = 0   # Cliente Anonimo
            else: ci = int(self.lineE17.text())    # Cliente registrado

            if  self.db.existClient(ci):
                if len(self.selectedProducts) > 0:
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
                        client = self.db.getClients(ci)[0]
                        if client.balance >= total - efectivo:
                            saldo = total - efectivo

                            message = "Se descontarán " + naturalFormat(saldo) + " del saldo del cliente"
                            popUp = confirmationPopUp(message, self)

                            if popUp.exec_():
                                if popUp.getValue():
                                    try:
                                        purchase_id = self.db.createPurchase(ci, self.user)                         # Crear compra
                                        for key, val in self.selectedProducts.items():                              # Tomar cada producto seleccionado
                                            self.db.createProductList(purchase_id, key, float(val[0]), int(val[1])) # Crear la lista de productos
                                        if efectivo > 0: self.db.createCheckout(purchase_id, efectivo)              # Crear pago con dinero
                                        self.db.createCheckout(purchase_id, saldo, True)                            # Crear pago con saldo
                                        successPopUp(parent = self).exec_()                                         # Venta exitosa

                                    except:
                                        errorPopUp(parent = self).exec_()                                           # Venta fallida

                                    # Setear variables y refrescar la interfaz
                                    self.refreshSales()

                        elif client.debt_permission:
                            saldo = float(client.balance)

                            if saldo == 0:
                                deuda = total - efectivo
                                message = "Se le cargará una deuda de " + naturalFormat(deuda) + " al cliente"

                            else:
                                deuda = total - efectivo - saldo
                                message = "Se descontarán " + naturalFormat(saldo) + " del saldo del cliente y se creará una deuda de " + naturalFormat(deuda)

                            popUp = confirmationPopUp(message, self)
                            if popUp.exec_():
                                if popUp.getValue():
                                    try:
                                        purchase_id = self.db.createPurchase(ci, self.user)                         # Crear compra
                                        for key, val in self.selectedProducts.items():                              # Tomar cada producto seleccionado
                                            self.db.createProductList(purchase_id, key, float(val[0]), int(val[1])) # Crear la lista de productos
                                        if efectivo > 0: self.db.createCheckout(purchase_id, efectivo)              # Crear pago con dinero
                                        if saldo > 0: self.db.createCheckout(purchase_id, saldo, True)              # Crear pago con saldo
                                        self.db.createCheckout(purchase_id, deuda, True)                            # Crear pago con deuda
                                        successPopUp(parent = self).exec_()                                         # Venta exitosa

                                    except:
                                        errorPopUp(parent = self).exec_()                                           # Venta fallida

                                    # Setear variables y refrescar la interfaz
                                    self.refreshSales()

                        else:
                            warningPopUp("Pago insuficiente", self).exec_()
                else:
                    warningPopUp("No se han agregado productos", self).exec_()
            else:
                warningPopUp("El cliente no existe", self).exec_()

    # Botón para agregar lista de producto
    def on_pbutton9_pressed(self):
        if self.click():
            name = self.lineE23.text()
            if self.db.existProduct(name) and self.spinLine0.text() != "" and int(self.spinLine0.text()) > 0:

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

                        if self.lineE152.text() != "":
                            saldo = float(self.lineE152.text())
                            if saldo > cota:
                                self.lineE152.setText(str(cota))

                else:
                    self.clearLEs(self.salesClientLE0)          # Limpiar lineEdits del apartado
            else:
                self.clearLEs(self.salesClientLE0)              # Limpiar lineEdits del apartado

    # LineEdit para mostrar el total a pagar
    def on_lineE21_textChanged(self):
        if self.textChanged():
            if self.lineE21.text() != "":
                total = float(self.lineE21.text())

                if self.lineE22.text() != "": efectivo = float(self.lineE22.text())
                else: efectivo = 0

                if self.lineE152.text() != "": saldo = float(self.lineE152.text())
                else: saldo = 0

                if efectivo + saldo > total:

                    if efectivo > total:
                        efectivo = total
                        self.lineE22.setText(str(efectivo))

                    if saldo > total - efectivo:
                        self.lineE152.setText(str(total - efectivo))

            else:
                self.lineE22.setText("")
                self.lineE152.setText("")

    # LineEdit para ingresar el monto a pagar en efectivo
    def on_lineE22_textChanged(self):
        if self.textChanged():
            if self.lineE21.text() != "":
                total = float(self.lineE21.text())

                if self.lineE22.text() != "": efectivo = float(self.lineE22.text())
                else: efectivo = 0

                if self.lineE152.text() != "": saldo = float(self.lineE152.text())
                else: saldo = 0

                if efectivo + saldo > total:

                    if efectivo > total:
                        efectivo = total
                        self.lineE22.setText(str(efectivo))

                    if saldo > total - efectivo:
                        self.lineE152.setText(str(total - efectivo))

            else: self.lineE22.setText("")

    # LineEdit para ingresar el monto a pagar con saldo
    def on_lineE152_textChanged(self):
        if self.textChanged():
            if self.lineE21.text() != "":
                if self.lineE17.text() != "":
                    ci = int(self.lineE17.text())
                    if self.db.existClient(ci):
                        balance = self.db.getClients(ci)[0].balance

                        if balance > 0:

                            total = float(self.lineE21.text())

                            if self.lineE152.text() != "": saldo = float(self.lineE152.text())
                            else: saldo = 0

                            if self.lineE22.text() != "": efectivo = float(self.lineE22.text())
                            else: efectivo = 0

                            if saldo > min(saldo, balance, total):
                                saldo = min(saldo, balance, total)
                                self.lineE152.setText(str(saldo))

                            if efectivo + saldo > total:

                                if efectivo > total - saldo:
                                    self.lineE22.setText(str(total - saldo))

                        else: self.lineE152.setText("")
                    else: self.lineE152.setText("")
                else: self.lineE152.setText("")
            else: self.lineE152.setText("")

    # LineEdit para ingresar el nombre del producto seleccionado
    def on_lineE23_textChanged(self):
        if self.textChanged():
            product_name = self.lineE23.text()
            if product_name != "":
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

                    self.selectedProductRemaining[product_name] = product.remaining
                    self.selectedItem0.setIcon(QIcon(join(productPath, product_name)))
                    if product.remaining > 0: self.add0.setEnabled(True)
                    self.spinLine0.setText(amount)

                else:
                    self.selectedProductName = ""
                    self.clearLEs(self.selectedProductLE0)
                    self.clearSpinLine(self.spinLine0)
                    self.substract0.setEnabled(False)
                    self.add0.setEnabled(False)
                    self.resetProductImage(self.selectedItem0)

            else:
                self.selectedProductName = ""
                self.clearLEs(self.selectedProductLE0)
                self.clearSpinLine(self.spinLine0)
                self.substract0.setEnabled(False)
                self.add0.setEnabled(False)
                self.resetProductImage(self.selectedItem0)

    # LineEdit para ingresar nombres de los productos
    def on_spinLine0_textChanged(self):
        if self.textChanged():
            product_name = self.lineE23.text()
            if product_name != "":
                if self.db.existProduct(product_name):
                    if self.spinLine0.text() != "": count = int(self.spinLine0.text())
                    else: count = 0

                    if count == 0:
                        self.substract0.setEnabled(False)
                        if self.selectedProductRemaining[self.selectedProductName] == 0 or self.selectedProductName == "":
                            self.add0.setEnabled(False)

                    elif 0 < count < self.selectedProductRemaining[self.selectedProductName]:
                        self.add0.setEnabled(True)
                        self.substract0.setEnabled(True)

                    else:
                        if count > self.selectedProductRemaining[self.selectedProductName]:
                            count = self.selectedProductRemaining[self.selectedProductName]
                            self.spinLine0.setText(str(count))
                        self.add0.setEnabled(False)
                        self.substract0.setEnabled(True)

                    self.lineE25.setText(str(((count)*float(self.lineE24.text()))))

                else:
                    self.substract0.setEnabled(False)
                    self.add0.setEnabled(False)

            else:
                self.substract0.setEnabled(False)
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
            "active"         : True,
            "limit"          : self.pageLimit
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
        self.getProductsTotalPages()
        self.updateProductsTable(self.table0, self.productsInfoAvailable)
        self.updateProductsTable(self.table1, self.productsInfoNotAvailable)
        self.updateProductsTable(self.table2, self.productsInfo)

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

        if self.rbutton9.isChecked() or self.rbutton11.isChecked():
            self.clearDE(self.dtE2, False)

        else:
            self.clearDE(self.dtE2, True)

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
    def updateProductsTable(self, table, itemsList):
        self.clearTable(table)

        table.setRowCount(len(itemsList))
        for i in range(len(itemsList)):
            table.setItem(i, 0, QTableWidgetItem(str(itemsList[i][1]))) # Nombre
            table.setItem(i, 1, QTableWidgetItem(str(itemsList[i][2]))) # Precio
            table.setItem(i, 2, QTableWidgetItem(str(itemsList[i][5]))) # Categoria
            table.setItem(i, 3, QTableWidgetItem(str(itemsList[i][3]))) # Cantidad
            table.setItem(i, 4, QTableWidgetItem(str(itemsList[i][4]))) # Lotes

        self.elem_actual = 0                                      # Definir la fila que se seleccionará
        if len(itemsList) > 0: table.selectRow(self.elem_actual)  # Seleccionar fila
        table.resizeColumnsToContents()                           # Redimensionar columnas segun el contenido
        self.setupTable(table)                                    # Reconfigurar tabla

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
            self.setOnlyFloat(self.productsOF0)
            self.setAnyCharacter(self.productsOF1)

    # Radio button para consultar productos
    def on_rbutton6_pressed(self):
        if self.click():
            self.deleteProductInput()
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1)
            self.text64.setText("Buscar")
            self.resetProductImage(self.selectedItem1)
            self.setOnlyFloat(self.productsOF0)
            self.setAnyCharacter(self.productsOF1)

    # Radio button para editar productos
    def on_rbutton7_pressed(self):
        if self.click():
            self.addProductInput()
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1, listaLE1 = self.productsRO3)
            self.resetProductImage(self.selectedItem1)
            self.setOnlyFloat(self.productsOF1)
            self.setAnyCharacter(self.productsOF0)

    # Radio button para eliminar productos
    def on_rbutton8_pressed(self):
        if self.click():
            self.deleteProductInput()
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1)
            self.text64.setText("Nombre")
            self.resetProductImage(self.selectedItem1)
            self.setOnlyFloat(self.productsOF0)
            self.setAnyCharacter(self.productsOF1)

    # Radio button para agregar nuevos lotes
    def on_rbutton9_pressed(self):
        if self.click():
            self.lotMutex1 = False
            self.clearCB(self.cbox5)
            self.clearLEs(self.lotsRO0)
            self.changeRO(self.lotsRO2, False, self.lotsRO3)
            self.readOnlyCB(self.cbox5, True)
            self.clearDE(self.dtE2, False)
            self.resetProductImage(self.selectedItem2)
            self.setStyle(self.theme)

    # Radio button para consultar lotes
    def on_rbutton10_pressed(self):
        if self.click():
            self.lotMutex1 = False
            self.clearCB(self.cbox5)
            self.clearLEs(self.lotsRO0)
            self.changeRO(self.lotsRO1)
            self.readOnlyCB(self.cbox5, False)
            self.clearDE(self.dtE2, True)
            self.resetProductImage(self.selectedItem2)
            self.setStyle(self.theme)

    # Radio button para editar lotes
    def on_rbutton11_pressed(self):
        if self.click():
            self.lotMutex1 = False
            self.clearCB(self.cbox5)
            self.clearLEs(self.lotsRO0)
            self.changeRO(self.lotsRO0, False)
            self.readOnlyCB(self.cbox5, False)
            self.clearDE(self.dtE2, False)
            self.resetProductImage(self.selectedItem2)
            self.setStyle(self.theme)

    # Radio button para eliminar lotes
    def on_rbutton12_pressed(self):
        if self.click():
            self.lotMutex1 = False
            self.clearCB(self.cbox5)
            self.clearLEs(self.lotsRO0)
            self.changeRO(self.lotsRO1)
            self.readOnlyCB(self.cbox5, False)
            self.clearDE(self.dtE2, True)
            self.resetProductImage(self.selectedItem2)
            self.setStyle(self.theme)

    # Boton "Aceptar" en el apartado de productos
    def on_pbutton11_pressed(self):
        if self.click():
            # Modalidad para agregar nuevos productos
            if self.rbutton5.isChecked():
                if self.lineE26.text() != "":
                    product_name = self.lineE26.text().title().strip()

                    if self.lineE27.text() != "":
                        # Obtener información del nuevo producto
                        price = self.lineE27.text()
                        categoy = self.lineE28.text()

                        if not self.db.existProduct(product_name):
                            # Agregar el producto a la BD
                            if self.db.createProduct(product_name, price, categoy):

                                if self.tempImage != "":
                                    if not isdir(productPath): mkdir(productPath)
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
                    product_name = self.lineE26.text().title().strip()
                    if self.db.existProduct(product_name):
                        newName = self.lineE27.text()
                        newPrice = float(self.lineE28.text())
                        newCategory = self.lineE29.text()

                        if newName != "" and newPrice > 0:
                            # Actualizar información de producto
                            if self.db.updateProduct(product_name, newName, newPrice, newCategory):

                                if self.tempImage != "":
                                    if not isdir(productPath): mkdir(productPath)
                                    copy2(self.tempImage, join(productPath, product_name))

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
                product_name = self.lineE33.text()   # Producto
                provider_name = self.lineE34.text()  # Proveedor
                cost = self.lineE35.text()           # Costo
                expiration_date = self.dtE2.date().toPyDate()   # Fecha de expiración
                quantity = self.lineE37.text()       # Cantidad

                # Verificar completitud de los campos obligatorios
                if (product_name and provider_name and cost and quantity) != "":

                    if self.db.existProduct(product_name):

                        if self.db.existProvider(provider_name):

                            kwargs = {
                                "product_name"    : product_name,
                                "provider_name"   : provider_name,
                                "received_by"     : self.user,
                                "cost"            : float(cost),
                                "quantity"        : int(quantity),
                                'expiration_date' : expiration_date
                            }

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

                product_name = self.lineE33.text()                  # Producto
                provider_name = self.lineE34.text()                 # Proveedor
                cost =  self.lineE35.text()                         # Costo
                expiration_date = self.dtE2.date().toPyDate()   # Fecha de expiración
                quantity = self.lineE37.text()                      # Cantidad
                remaining = self.lineE38.text()                     # Disponibles

                if (product_name and provider_name and cost and quantity and remaining) != "":

                    if self.db.existProduct(product_name):

                        if self.db.existProvider(provider_name):

                            kwargs = {
                                "lot_id"          : self.currentLots[self.currentLot],
                                "product_name"    : product_name,
                                "provider_id"     : provider_name,
                                "cost"            : float(cost),
                                "quantity"        : int(quantity),
                                "remaining"       : int(remaining),
                                'expiration_date' : expiration_date
                            }

                            if quantity >= remaining:

                                if self.db.updateLot(**kwargs):
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
            if self.rbutton5.isChecked() or self.rbutton7.isChecked():
                filePath = QFileDialog.getOpenFileName(self, 'Seleccionar imágen', QDir.currentPath(), "Imágenes (*.bmp *.jpg *.jpeg *.png)")
                if filePath != "":
                    self.selectedItem1.setIcon(QIcon(filePath))
                    self.tempImage = filePath

    # Boton de cancelar en el apartado de productos
    def on_cancelpb2_pressed(self):
        if self.click():
            self.clearLEs(self.productsRO0)

    # Boton de cancelar en el apartado de lotes
    def on_cancelpb3_pressed(self):
        if self.click():
            self.clearLEs(self.lotsRO0)

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CAMPOS DE TEXTO
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # LineEdit para ingresar nombres de los productos en el aparatado de productos
    def on_lineE26_textChanged(self):
        if self.textChanged():
            if not self.rbutton5.isChecked():
                if self.lineE26.text() != "":
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
                        if self.rbutton7.isChecked(): self.clearLE(self.lineExtra)
                        self.clearLEs(self.productsRO1)
                        self.resetProductImage(self.selectedItem1)
                else:
                    if self.rbutton7.isChecked(): self.clearLE(self.lineExtra)
                    self.clearLEs(self.productsRO1)
                    self.resetProductImage(self.selectedItem1)

    # LineEdit para ingresar nombres de los productos en el apartado de lotes
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
                            self.lineE37.setText(str(lot.quantity))      # Cantidad
                            self.lineE38.setText(str(lot.remaining))     # Disponibilidad

                            # Fecha de expiración
                            dateStr = dateFormat(lot.expiration_date, "%Y-%m-%d")
                            date = QDate().fromString(dateStr, 'yyyy-MM-dd')
                            self.dtE2.setDate(date)

                        self.lotMutex1 = True

                else:
                    self.clearLEs(self.lotsRO1)
                    self.lotMutex1 = False
                    self.clearCB(self.cbox5)
                    self.lotMutex1 = True
                    self.resetProductImage(self.selectedItem2)
                    self.dtE2.setDate(QDate().currentDate())

            else:
                self.clearLEs(self.lotsRO1)
                self.lotMutex1 = False
                self.clearCB(self.cbox5)
                self.lotMutex1 = True
                self.resetProductImage(self.selectedItem2)
                self.dtE2.setDate(QDate().currentDate())

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
                self.lineE37.setText(str(lot.quantity))      # Cantidad
                self.lineE38.setText(str(lot.remaining))     # Disponibilidad

                # Fecha de expiración
                dateStr = dateFormat(lot.expiration_date, "%Y-%m-%d")
                date = QDate().fromString(dateStr, 'yyyy-MM-dd')
                self.dtE2.setDate(date)

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # TABLAS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Clickear una fila de la tabla de productos diponibles
    def on_table0_itemClicked(self, item):
        if self.rowChanged():
            # Obtener la información completa del producto
            product = self.db.getProductByNameOrID(self.table0.selectedItems()[0].text())[0]

            kwargs = [
                ("Nombre",      product.product_name),
                ("Precio",      str(product.price)),
                ("Categoria",   product.category),
                ("Lotes",       str(product.remaining_lots)),
                ("Disp. total", str(product.remaining)),
            ]

            detailsPopUp(kwargs, self).exec_()

    # Clickear una fila de la tabla de productos no diponibles
    def on_table1_itemClicked(self, item):
        if self.rowChanged():
            # Obtener la información completa del producto
            product = self.db.getProductByNameOrID(self.table1.selectedItems()[0].text())[0]

            kwargs = [
                ("Nombre",      product.product_name),
                ("Precio",      str(product.price)),
                ("Categoria",   product.category),
                ("Lotes",       str(product.remaining_lots)),
                ("Disp. total", str(product.remaining)),
            ]

            detailsPopUp(kwargs, self).exec_()

    # Clickear una fila de la tabla de todos los productos
    def on_table2_itemClicked(self, item):
        if self.rowChanged():
            # Obtener la información completa del producto
            product = self.db.getProductByNameOrID(self.table2.selectedItems()[0].text())[0]

            kwargs = [
                ("Nombre",      product.product_name),
                ("Precio",      str(product.price)),
                ("Categoria",   product.category),
                ("Lotes",       str(product.remaining_lots)),
                ("Disp. total", str(product.remaining)),
            ]

            detailsPopUp(kwargs, self).exec_()

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
        self.getProvidersTotalPages()
        self.updateProvidersTable()

    # Método para refrescar la tabla de proveedores
    def updateProvidersTable(self):
        table = self.table13
        self.providersTableItems = self.db.getAllProviders(limit=self.pageLimit, page=self.tablesPages[self.tables.index(table)])

        self.clearTable(table)                                                                      # Vaciar la tabla
        table.setRowCount(len(self.providersTableItems))                                            # Contador de filas
        for i in range(len(self.providersTableItems)):                                              # Llenar tabla
            table.setItem(i, 0, QTableWidgetItem(str(self.providersTableItems[i].provider_name)))   # Nombre
            table.setItem(i, 1, QTableWidgetItem(str(self.providersTableItems[i].phone)))           # Teléfono
            table.setItem(i, 2, QTableWidgetItem(str(self.providersTableItems[i].email)))           # Correo
            table.setItem(i, 3, QTableWidgetItem(str(self.providersTableItems[i].description)))     # Descripción
            table.setItem(i, 4, QTableWidgetItem(str(self.providersTableItems[i].pay_information))) # Informacion de pago

        self.elem_actual = 0                                                    # Definir la fila que se seleccionará
        if len(self.providersTableItems) > 0: table.selectRow(self.elem_actual) # Seleccionar fila
        table.resizeColumnsToContents()                                         # Redimensionar columnas segun el contenido
        self.setupTable(table, 4)                                               # Reconfigurar tabla

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

    # Botón cancelar de editar proveedor
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

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # TABLAS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Clickear una fila de la tabla de proveedores
    def on_table13_itemClicked(self, item):
        if self.rowChanged():
            # Obtener la información completa del proveedor
            provider = self.db.getProvider(self.table13.selectedItems()[0].text())

            kwargs = [
                ("Proveedor",          provider.provider_name),
                ("Teléfono",           provider.phone),
                ("Correo",             provider.email),
                ("Descripción",        paragraphFormat(provider.description)),
                ("Info. de pago",      paragraphFormat(provider.pay_information)),
                ("Fecha de registro",  dateFormat(provider.creation_date)),
                ("Hora de registro",   timeFormat(provider.creation_date))
            ]

            detailsPopUp(kwargs, self).exec_()

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
        self.clearLEs(self.clientsLE1)
        self.clearLEs(self.clientsLE3)

        # Setear los comboBox
        self.resetClientsCBs()

        # Refrescar tabla
        self.getClientsTotalPages()
        self.updateClientsTable()
        self.updateClientsTable(True)

    # Método para refrescar las tablas de clientes
    def updateClientsTable(self, indebted = False):
        if indebted:
            table = self.table6
            clients = self.db.getClients(indebted=indebted, limit=self.pageLimit, page=self.tablesPages[self.tables.index(table)])

        else:
            table = self.table7
            clients = self.db.getClients(indebted=indebted, limit=self.pageLimit, page=self.tablesPages[self.tables.index(table)])

        self.clearTable(table)                                                       # Vaciar la tabla
        table.setRowCount(len(clients))                                              # Contador de filas
        for i in range(len(clients)):                                                # Llenar tabla
            table.setItem(i, 0, QTableWidgetItem(str(clients[i].ci)))                # Cédula
            table.setItem(i, 1, QTableWidgetItem(str(clients[i].firstname)))         # Nombre
            table.setItem(i, 2, QTableWidgetItem(str(clients[i].lastname)))          # Apellido
            table.setItem(i, 3, QTableWidgetItem(str(clients[i].balance)))           # Saldo
            if indebted: table.setItem(i, 4, QTableWidgetItem(str(clients[i].debt))) # Deuda

        self.elem_actual = 0                                            # Definir la fila que se seleccionará
        if len(clients) > 0: table.selectRow(self.elem_actual)          # Seleccionar fila
        table.resizeColumnsToContents()                                 # Redimensionar columnas segun el contenido
        if indebted: self.setupTable(table, 4)                          # Reconfigurar tabla
        else: self.setupTable(table, 3)                                 # Reconfigurar tabla

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
            ci        = self.lineE52.text()
            firstname = self.lineE53.text()
            lastname  = self.lineE54.text()
            phone     = self.lineE55.text()
            email     = self.lineE56.text()
            flag = False
            if (ci and firstname and lastname) != "":
                ci = int(ci)
                if not self.db.existClient(ci):

                    if validateName(firstname):

                        if validateName(lastname):

                            if (phone != "" and validatePhoneNumber(phone)) or phone == "":

                                if (email != "" and validateEmail(email)) or email == "":

                                    debt = (self.cbox10.currentText() == "Permitir")
                                    book = (self.cbox11.currentText() == "Permitir")
                                    kwargs = {
                                        "ci"              : ci,
                                        "firstname"       : firstname,
                                        "lastname"        : lastname,
                                        "phone"           : phone,
                                        "email"           : email,
                                        "debt_permission" : debt,
                                        "book_permission" : book
                                    }
                                    flag = debt
                                else:
                                    errorPopUp("Formato de correo no válido",self).exec_()

                            else:
                                errorPopUp("Formato de teléfono no válido",self).exec_()

                        else:
                            errorPopUp("Formato de apellido no válido", self).exec_()

                    else:
                        errorPopUp("Formato de nombre no válido", self).exec_()

                else:
                    errorPopUp("Número de cédula previamente registrado", self).exec_()

            else:
                errorPopUp("Datos obligatorios: CI,Nombre y Apellido", self).exec_()

            if flag:
                popUp = authorizationPopUp(parent=self)
                if popUp.exec_():
                    adminUsername, adminPassword = popUp.getValues()
                    if (adminUsername and adminPassword) != None:
                        if self.db.checkPassword(adminUsername, adminPassword):
                            userRange = self.db.getUserRange(adminUsername)
                            if userRange == "Administrador" or userRange == "Dios":
                                if self.db.createClient(**kwargs): # Crear cliente
                                    successPopUp(parent = self).exec_()

                                else:
                                    errorPopUp(parent = self).exec_()

                                self.clearLEs(self.clientsLE0) # Limpiar formulario
                                self.refreshClients()          # Refrescar vista
                                self.lineE52.setFocus()        # Enfocar
                            else:
                                errorPopUp("El usuario "+ adminUsername +" no es administrador", self).exec_()
                        else:
                            errorPopUp("Datos incorrectos", self).exec_()
            else:
                if self.db.createClient(**kwargs): # Crear cliente
                    successPopUp(parent = self).exec_()

                else:
                    errorPopUp(parent = self).exec_()

                self.clearLEs(self.clientsLE0) # Limpiar formulario
                self.refreshClients()          # Refrescar vista
                self.lineE52.setFocus()        # Enfocar

    #Botón para cancelar creación de cliente
    def on_cancelpb16_pressed(self):
        self.clearLEs(self.clientsLE0)
        self.lineE52.setFocus()

    # Botón para editar un cliente
    def on_pbutton19_pressed(self):
        if self.click():
            ci         = self.lineE57.text()
            firstname  = self.lineE58.text()
            lastname   = self.lineE59.text()
            phone      = self.lineE60.text()
            email      = self.lineE61.text()

            if ci != "":
                ci = int(ci)
                if self.db.existClient(ci):
                    if validateName(firstname):
                        if validateName(lastname):
                            if (phone != "" and validatePhoneNumber(phone)) or phone == "":
                                if (email != "" and validateEmail(email)) or email == "":

                                    client = self.db.getClients(ci)[0]
                                    debt = (self.cbox12.currentText() == "Permitir")
                                    book = (self.cbox13.currentText() == "Permitir")

                                    kwargs = {
                                        "ciOriginal" : ci,
                                        "firstname"  : firstname,
                                        "lastname"   : lastname,
                                        "phone"      : phone,
                                        "email"      : email,
                                        "debt_permission" : debt,
                                        "book_permission" : book
                                    }

                                    changeDebt = (debt != client.debt_permission)

                                    if changeDebt:
                                        if debt or client.balance >= 0:
                                            popUp = authorizationPopUp(parent=self)
                                            if popUp.exec_():
                                                adminUsername, adminPassword = popUp.getValues()
                                                if (adminUsername and adminPassword) != None:
                                                    if self.db.checkPassword(adminUsername, adminPassword):
                                                        userRange = self.db.getUserRange(adminUsername)
                                                        if userRange == "Administrador" or userRange == "Dios":
                                                            if self.db.updateClient(**kwargs):      # Actualizar cliente
                                                                successPopUp(parent = self).exec_()

                                                            else:
                                                                errorPopUp(parent = self).exec_()

                                                            self.clearLEs(self.clientsLE1) # Limpiar formulario
                                                            self.refreshClients()          # Refrescar vista
                                                            self.lineE57.setFocus()        # Enfocar
                                                        else:
                                                            errorPopUp("El usuario "+ adminUsername +" no es administrador", self).exec_()
                                                    else:
                                                        errorPopUp("Datos incorrectos", self).exec_()
                                        else:
                                            errorPopUp("No se le puede quitar el permiso de deudas a un cliente endeudado",self).exec_()
                                    else:
                                        if self.db.updateClient(**kwargs):      # Actualizar cliente
                                            successPopUp(parent = self).exec_()

                                        else:
                                            errorPopUp(parent = self).exec_()

                                        self.clearLEs(self.clientsLE1) # Limpiar formulario
                                        self.refreshClients()          # Refrescar vista
                                        self.lineE57.setFocus()        # Enfocar

                                else:
                                    errorPopUp("Formato de correo no válido",self).exec_()
                            else:
                                errorPopUp("Formato de teléfono no válido",self).exec_()
                        else:
                            errorPopUp("Formato de apellido no válido", self).exec_()
                    else:
                        errorPopUp("Formato de nombre no válido", self).exec_()
                else:
                    errorPopUp("Número de cédula no registrado", self).exec_()
            else:
                errorPopUp("Número de cédula no específicado", self).exec_()

    # Botón para cancelar creación de cliente
    def on_cancelpb17_pressed(self):
        self.clearLEs(self.clientsLE1)
        self.lineE57.setFocus()

    # Botón para hacer incremento de deuda a un cliente
    def on_pbutton16_pressed(self):
        if self.click():
            ci = self.lineE16.text()
            if ci != "":
                ci = int(ci)
                if self.db.existClient(ci):
                    client = self.db.getClients(ci)[0]
                    if client.debt > 0:
                        amount = self.lineE68.text()
                        if amount != "":
                            amount = float(amount)
                            popUp = authorizationPopUp(parent=self)
                            if popUp.exec_():
                                adminUsername, adminPassword = popUp.getValues()
                                if (adminUsername and adminPassword) != None:
                                    if self.db.checkPassword(adminUsername, adminPassword):
                                        userRange = self.db.getUserRange(adminUsername)
                                        if userRange == "Administrador" or userRange == "Dios":

                                            # Registrar deuda
                                            if self.db.createIncrease(ci, self.user, amount):
                                                # Operación exitosa
                                                successPopUp(parent = self).exec_()

                                            else:
                                                # Operación fallida
                                                errorPopUp(parent = self).exec_()

                                            self.clearLEs(self.clientsLE3) # Limpiar formulario
                                            self.refreshClients()          # Refrescar vista
                                            self.lineE16.setFocus()        # Enfocar
                                        else:
                                            errorPopUp("El usuario "+ adminUsername +" no es administrador", self).exec_()
                                    else:
                                        errorPopUp("Datos incorrectos", self).exec_()
                        else:
                           errorPopUp("Incremento no específicado", self).exec_()
                    else:
                        errorPopUp("El cliente no está endeudado", self).exec_()
                else:
                   errorPopUp("Número de cédula no registrado", self).exec_()
            else:
                errorPopUp("Número de cédula no específicado", self).exec_()

    # Botón para cancelar registrar incremento a un cliente
    def on_cancelpb25_pressed(self):
        self.clearLEs(self.clientsLE3) # Limpiar formulario
        self.lineE16.setFocus()        # Enfocar

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

    # LineEdit para ingresar la cédula del cliente
    def on_lineE16_textChanged(self):
        if self.textChanged():
            if self.lineE16.text() != "":
                ci = int(self.lineE16.text())
                if self.db.existClient(ci):
                    client = self.db.getClients(ci)[0]
                    self.lineE31.setText(client.firstname)
                    self.lineE32.setText(client.lastname)
                    self.lineE80.setText(str(client.balance))
                    self.lineE67.setText(str(client.debt))

                else:
                    self.clearLEs(self.clientsLE4)

            else:
                self.clearLEs(self.clientsLE4)

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # TABLAS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Clickear una fila de la tabla de clientes endeudados
    def on_table6_itemClicked(self, item):
        if self.rowChanged():
            # Obtener la información completa del cliente
            ci = self.table6.selectedItems()[0].text()
            especialPopUp0(ci, self.db, self).exec_()

    # Clickear una fila de la tabla de clientes No endeudados
    def on_table7_itemClicked(self, item):
        if self.rowChanged():
            # Obtener la información completa del cliente
            client = self.db.getClients(self.table7.selectedItems()[0].text())[0]

            kwargs = [
                ("Cédula",        str(client.ci)),
                ("Nombre",        client.firstname),
                ("Apellido",      client.lastname),
                ("Teléfono",      client.phone),
                ("Correo",        client.email),
                ("Saldo",         str(client.balance)),
                ("Última visita", dateTimeFormat(client.last_seen)),
            ]

            detailsPopUp(kwargs, self).exec_()

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
        self.getTransfersTotalPages()
        self.updateTranfersTable()
        self.updateDepositsTable()
        self.refreshSales()

    # Método para refrescar la tabla de transferencias
    def updateTranfersTable(self):
        table = self.table14
        self.transferTableItems = self.db.getTransfers(limit=self.pageLimit, page=self.tablesPages[self.tables.index(table)])

        self.clearTable(table)                                                                       # Vaciar la tabla
        table.setRowCount(len(self.transferTableItems))                                              # Contador de filas
        for i in range(len(self.transferTableItems)):                                                # Llenar tabla
            table.setItem(i, 0, QTableWidgetItem(str(self.transferTableItems[i].clerk)))             # Usuario
            table.setItem(i, 1, QTableWidgetItem(str(self.transferTableItems[i].ci)))                # Cliente
            table.setItem(i, 2, QTableWidgetItem(str(self.transferTableItems[i].amount)))            # Monto
            table.setItem(i, 3, QTableWidgetItem(str(self.transferTableItems[i].bank)))              # Banco
            table.setItem(i, 4, QTableWidgetItem(str(self.transferTableItems[i].confirmation_code))) # Código de confirmación

        self.elem_actual = 0                                                    # Definir la fila que se seleccionará
        if len(self.transferTableItems) > 0: table.selectRow(self.elem_actual)  # Seleccionar fila
        table.resizeColumnsToContents()                                         # Redimensionar columnas segun el contenido
        self.setupTable(table, 4)                                               # Reconfigurar tabla

    # Método para refrescar la tabla de transferencias
    def updateDepositsTable(self):
        table = self.table16
        self.depositsTableItems = self.db.getDeposits(limit=self.pageLimit, page=self.tablesPages[self.tables.index(table)])

        self.clearTable(table)                                                                         # Vaciar la tabla
        table.setRowCount(len(self.depositsTableItems))                                                # Contador de filas
        for i in range(len(self.depositsTableItems)):                                                  # Llenar tabla
            table.setItem(i, 0, QTableWidgetItem(str(self.depositsTableItems[i].clerk)))               # Usuario
            table.setItem(i, 1, QTableWidgetItem(str(self.depositsTableItems[i].ci)))                  # Cliente
            table.setItem(i, 2, QTableWidgetItem(str(self.depositsTableItems[i].amount)))              # Monto
            table.setItem(i, 3, QTableWidgetItem(dateFormat(self.depositsTableItems[i].deposit_date))) # Fecha
            table.setItem(i, 4, QTableWidgetItem(timeFormat(self.depositsTableItems[i].deposit_date))) # Hora

        self.elem_actual = 0                                                     # Definir la fila que se seleccionará
        if len(self.depositsTableItems) > 0: table.selectRow(self.elem_actual)   # Seleccionar fila
        table.resizeColumnsToContents()                                          # Redimensionar columnas según el contenido
        self.setupTable(table, 3)                                                # Reconfigurar tabla

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Boton aceptar para hacer una recarga de saldo
    def on_pbutton15_pressed(self):
        if self.click():
            ci = self.lineE47.text()
            if ci != "":
                ci = int(ci)
                if self.db.existClient(ci):
                    pay_type = self.cbox7.currentText()

                    # Modo de recarga con depósito
                    if pay_type == "Efectivo":
                        if self.lineE158.text() != "":
                            amount = float(self.lineE158.text())
                            if self.textE8.toPlainText() != "":
                                description = self.textE8.toPlainText()

                                # Crear depósito
                                if self.db.createDeposit(ci, self.user, amount, description):
                                    # Operación exitosa
                                    successPopUp(parent = self).exec_()
                                else:
                                    # Operación fallida
                                    errorPopUp(parent = self).exec_()

                                # Refrescar
                                self.refreshTransfers()
                                self.lineE47.setFocus()

                            else:
                                errorPopUp("Debe ingresar una descripción",self).exec_()
                        else:
                            errorPopUp("Debe ingresar monto a recargar",self).exec_()

                    # Modo de recarga con transferencia
                    else:
                        if (self.lineE51.text() and self.lineE156.text() and self.lineE157.text() and self.textE7.toPlainText()) != "":
                            bank = self.lineE156.text()
                            confirmation_code =  self.lineE157.text()

                            # Si la transferencia no existe
                            if not self.db.existTransfer(bank, confirmation_code):
                                # Argumentos
                                kwargs = {
                                    "clerk"             : self.user,
                                    "ci"                : ci,
                                    "amount"            : float(self.lineE51.text()),
                                    "bank"              : bank,
                                    "confirmation_code" : confirmation_code,
                                    "description"       : self.textE7.toPlainText()
                                }

                                # Crear transferencia
                                if self.db.createTransfer(**kwargs):
                                    # Operación exitosa
                                    successPopUp(parent = self).exec_()
                                else:
                                    # Operación fallida
                                    errorPopUp(parent = self).exec_()

                                # Refrescar
                                self.refreshTransfers()
                                self.lineE47.setFocus()

                            else:
                                errorPopUp("La transferencia ya está registrada",self).exec_()
                        else:
                            errorPopUp("Faltan datos",self).exec_()
                else:
                    errorPopUp("Cliente no existente",self).exec_()
            else:
                errorPopUp("Cédula requerida",self).exec_()

    #Boton de cancelar de recarga de saldo
    def on_cancelpb15_pressed(self):
        self.clearLEs(self.transfersLE0)
        self.clearLEs(self.transfersLE2)
        self.clearLEs(self.transfersLE3)
        self.clearTE(self.textE7)
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
                    self.lineE90.setText(str(client.debt))

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

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # TABLAS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Clickear una fila de la tabla de transferencias
    def on_table14_itemClicked(self, item):
        if self.rowChanged():
            # Obtener la información completa de la transferencia
            item = self.table14.selectedItems()

            kwargs = {
                "bank"              : item[3].text(),
                "confirmation_code" : item[4].text()
            }

            transfer = self.db.getTransfers(**kwargs)[0]

            kwargs = [
                ("Registrado por", str(transfer.clerk)),
                ("Cliente",        str(transfer.ci)),
                ("Fecha",          dateFormat(transfer.transfer_date)),
                ("Hora",           timeFormat(transfer.transfer_date)),
                ("Monto",          str(transfer.amount)),
                ("Banco",          str(transfer.bank)),
                ("Código",         str(transfer.confirmation_code)),
                ("Descripción",    paragraphFormat(transfer.description))
            ]

            detailsPopUp(kwargs, self).exec_()

    # Clickear una fila de la tabla de depósitos
    def on_table16_itemClicked(self, item):
        if self.rowChanged():
            # Obtener la información completa del depósito
            item = self.table16.selectedItems()
            selected = [item[0].text(), item[1].text(), item[2].text(), item[3].text(), item[4].text()]

            deposit = None
            for elem in self.depositsTableItems:
                clerk  = str(elem.clerk)
                ci     = str(elem.ci)
                amount = str(elem.amount)
                date   = dateFormat(elem.deposit_date)
                time   = timeFormat(elem.deposit_date)

                current = [clerk, ci, amount, date, time]

                if selected == current:
                    deposit =  self.db.getDeposits(elem.deposit_id)[0]

            if deposit != None:
                kwargs = [
                    ("Registrado por", str(deposit.clerk)),
                    ("Cliente",        str(deposit.ci)),
                    ("Monto",          str(deposit.amount)),
                    ("Fecha",          dateFormat(deposit.deposit_date)),
                    ("Hora",           timeFormat(deposit.deposit_date)),
                    ("Descripción",    paragraphFormat(deposit.description))
                ]

                detailsPopUp(kwargs, self).exec_()

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
        self.getUsersTotalPages()
        self.updateUsersTable(0) # Tabla de colaboradores
        self.updateUsersTable(1) # Tabla de vendedores
        self.updateUsersTable(2) # Tabla de administradores

    # Método para refrescar la tabla de usuarios
    def updateUsersTable(self, permission_mask):
        if permission_mask == 0: table = self.table10
        elif permission_mask == 1: table = self.table9
        else: table = self.table8

        users = self.db.getUsers(permission_mask=permission_mask, limit=self.pageLimit, page=self.tablesPages[self.tables.index(table)])

        if permission_mask == 0: self.usersTableItems0 = users
        elif permission_mask == 1: self.usersTableItems1 = users
        else: self.usersTableItems2 = users

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
        self.setupTable(table, 3)                            # Reconfigurar tabla

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Botón para crear un usuario
    def on_pbutton21_pressed(self):
        if self.click():
            flag = False

            username         = self.lineE69.text()
            firstname        = self.lineE70.text()
            lastname         = self.lineE71.text()
            email            = self.lineE72.text()
            password         = self.lineE73.text()
            passConfirmation = self.lineE74.text()
            if (username and firstname and lastname and email and password and passConfirmation) != "":
                if validateName(firstname):
                    if validateName(lastname):
                        if(validateEmail(email)):
                            if password == passConfirmation:
                                if not self.db.existUser(username):
                                    kwargs = {
                                        "username"        : username,
                                        "firstname"       : firstname,
                                        "lastname"        : lastname,
                                        "email"           : email,
                                        "password"        : password,
                                        "permission_mask" : self.db.getPermissionMask(self.cbox8.currentText())
                                    }
                                    flag = True

                                else:
                                    errorPopUp("El usuario "+username+" ya existe",self).exec_()
                            else:
                                errorPopUp("Las contraseñas no coinciden",self).exec_()
                        else:
                            errorPopUp("Formato incorrecto de correo",self).exec_()
                    else:
                        errorPopUp("Formato incorrecto para apellido",self).exec_()
                else:
                    errorPopUp("Formato incorrecto para nombre",self).exec_()
            else:
                errorPopUp("Faltan datos",self).exec_()
            if flag:
                popUp = authorizationPopUp(parent=self)
                if popUp.exec_():
                    adminUsername, adminPassword = popUp.getValues()
                    if (adminUsername and adminPassword) != None:
                        if self.db.checkPassword(adminUsername, adminPassword):
                            userRange = self.db.getUserRange(adminUsername)
                            if userRange == "Administrador" or userRange == "Dios":
                                if self.db.createUser(**kwargs):        # Crear usuario
                                    successPopUp("Se ha creado el usuario "+username+" exitosamente",self).exec_()
                                else:
                                    errorPopUp(parent = self).exec_()

                                self.refreshUsers()          # Refrescar vista
                                self.lineE69.setFocus()      # Enfocar
                            else:
                                errorPopUp("El usuario "+ adminUsername +" no es administrador", self).exec_()
                        else:
                            errorPopUp("Datos incorrectos", self).exec_()

    #Botón para cancelar creación de usuario
    def on_cancelpb18_pressed(self):
        self.clearLEs(self.usersLE0)
        self.clearLEs(self.usersLE1)
        self.clearLEs(self.usersLE2)
        self.lineE69.setFocus()

    # Botón para editar un usuario
    def on_pbutton23_pressed(self):
        if self.click():
            flag = False
            username   = self.lineE75.text()
            if username != "":
                if self.db.existUser(username):

                    newRangeInfo = {
                        "username"        : username,
                        "permission_mask" : self.db.getPermissionMask(self.cbox9.currentText())
                    }
                    flag = True
                else:
                    errorPopUp("El usuario "+username+" no existe",self).exec_()
            else:
                errorPopUp("Falta nombre de usuario", self).exec_()

            if flag:
                popUp = authorizationPopUp(parent=self)
                if popUp.exec_():
                    adminUsername, adminPassword = popUp.getValues()
                    if (adminUsername and adminPassword) != None:
                        if self.db.checkPassword(adminUsername, adminPassword):
                            userRange = self.db.getUserRange(adminUsername)
                            if userRange == "Administrador" or userRange == "Dios":
                                if self.db.updateUserRange(**newRangeInfo):    # Actualizar usuario
                                    successPopUp(parent = self).exec_()

                                else:
                                    errorPopUp(parent = self).exec_()

                                self.refreshUsers()               # Refrescar vista
                                self.lineE75.setFocus()           # Enfocar
                            else:
                                errorPopUp("El usuario "+ adminUsername +" no es administrador", self).exec_()
                        else:
                            errorPopUp("Datos incorrectos", self).exec_()

    #Botón para cancelar edición de usuario
    def on_cancelpb18_pressed(self):
        self.clearLEs(self.usersLE0)
        self.clearLEs(self.usersLE1)
        self.clearLEs(self.usersLE2)
        self.lineE75.setFocus()

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

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # TABLAS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Clickear una fila de la tabla de colaboradores
    def on_table10_itemClicked(self, item):
        if self.rowChanged():
            # Obtener la información completa del colaborador
            collaborator = self.usersTableItems0[self.table10.selectedItems()[0].row()]

            kwargs = [
                ("Username",      collaborator.username),
                ("Nombre",        collaborator.firstname),
                ("Apellido",      collaborator.lastname),
                ("Email",         collaborator.email),
                ("Rango",         self.db.getRange(collaborator.permission_mask)),
                ("Registro",      dateTimeFormat(collaborator.creation_date)),
                ("Última visita", dateTimeFormat(collaborator.last_login))
            ]

            detailsPopUp(kwargs, self).exec_()

    # Clickear una fila de la tabla de vendedores
    def on_table9_itemClicked(self, item):
        if self.rowChanged():
            # Obtener la información completa del vendedor
            seller = self.usersTableItems1[self.table9.selectedItems()[0].row()]

            kwargs = [
                ("Username",      seller.username),
                ("Nombre",        seller.firstname),
                ("Apellido",      seller.lastname),
                ("Email",         seller.email),
                ("Rango",         self.db.getRange(seller.permission_mask)),
                ("Registro",      dateTimeFormat(seller.creation_date)),
                ("Última visita", dateTimeFormat(seller.last_login))
            ]

            detailsPopUp(kwargs, self).exec_()

    # Clickear una fila de la tabla de administradores
    def on_table8_itemClicked(self, item):
        if self.rowChanged():
            # Obtener la información completa del administrador
            admin = self.usersTableItems2[self.table8.selectedItems()[0].row()]

            kwargs = [
                ("Username",      admin.username),
                ("Nombre",        admin.firstname),
                ("Apellido",      admin.lastname),
                ("Email",         admin.email),
                ("Rango",         self.db.getRange(admin.permission_mask)),
                ("Registro",      dateTimeFormat(admin.creation_date)),
                ("Última visita", dateTimeFormat(admin.last_login))
            ]

            detailsPopUp(kwargs, self).exec_()

    #==============================================================================================================================================================================
    # VISTA DE CONFIGURACIONES
    #==============================================================================================================================================================================

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Cambiar el tema de la interfáz
    def changeTheme(self, theme):
        if self.theme != theme:
            self.theme = theme
            self.setStyle(self.theme)

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
        if user.profile != "": self.changeTheme(user.profile)
        else: self.changeTheme("blue.qss")

    # Método para cambiar el usuario que usa la intefáz
    def changeUser(self, user):
        self.db.backup()
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
            self.changeTheme(styles[0])

    # Boton para establecer el tema 1
    def on_theme1_pressed(self):
        if self.click():
            self.changeTheme(styles[1])

    # Boton para establecer el tema 2
    def on_theme2_pressed(self):
        if self.click():
            self.changeTheme(styles[2])

    # Boton para establecer el tema 3
    def on_theme3_pressed(self):
        if self.click():
            self.changeTheme(styles[3])

    # Boton para establecer el tema 4
    def on_theme4_pressed(self):
        if self.click():
            self.changeTheme(styles[4])

    # Boton para establecer el tema 5
    def on_theme5_pressed(self):
        if self.click():
            self.changeTheme(styles[5])

    # Boton para establecer el tema 6
    def on_theme6_pressed(self):
        if self.click():
            self.changeTheme(styles[6])

    # Boton para establecer el tema 7
    def on_theme7_pressed(self):
        if self.click():
            self.changeTheme(styles[7])

    # Boton para establecer el tema 0
    def on_theme8_pressed(self):
        if self.click():
            self.changeTheme(styles[8])

    # Boton para establecer el tema 1
    def on_theme9_pressed(self):
        if self.click():
            self.changeTheme(styles[9])

    # Boton para establecer el tema 2
    def on_theme10_pressed(self):
        if self.click():
            self.changeTheme(styles[10])

    # Boton para establecer el tema 3
    def on_theme11_pressed(self):
        if self.click():
            self.changeTheme(styles[11])

    # Boton para establecer el tema 4
    def on_theme12_pressed(self):
        if self.click():
            self.changeTheme(styles[12])

    # Boton para establecer el tema 5
    def on_theme13_pressed(self):
        if self.click():
            self.changeTheme(styles[13])

    # Boton para establecer el tema 6
    def on_theme14_pressed(self):
        if self.click():
            self.changeTheme(styles[14])

    # Boton para establecer el tema 7
    def on_theme15_pressed(self):
        if self.click():
            self.changeTheme(styles[15])

        # Boton para establecer el tema 0
    def on_theme16_pressed(self):
        if self.click():
            self.changeTheme(styles[16])

    # Boton para establecer el tema 1
    def on_theme17_pressed(self):
        if self.click():
            self.changeTheme(styles[17])

    # Boton para establecer el tema 2
    def on_theme18_pressed(self):
        if self.click():
            self.changeTheme(styles[18])

    # Boton para establecer el tema 3
    def on_theme19_pressed(self):
        if self.click():
            self.changeTheme(styles[19])

    # Boton para hacer backup
    def on_pbutton24_pressed(self):
        if self.click():
            popUp = authorizationPopUp(parent=self)
            if popUp.exec_():
                adminUsername, adminPassword = popUp.getValues()
                if (adminUsername and adminPassword) != None:
                    if self.db.checkPassword(adminUsername, adminPassword):
                        userRange = self.db.getUserRange(adminUsername)
                        if userRange == "Administrador" or userRange == "Dios":
                            # Realizar respaldo
                            if self.db.backup():
                                # Operación exitosa
                                successPopUp(parent = self).exec_()

                            else:
                                # Operación fallida
                                errorPopUp(parent = self).exec_()
                        else:
                            errorPopUp("El usuario "+ adminUsername +" no es administrador", self).exec_()
                    else:
                        errorPopUp("Datos incorrectos", self).exec_()

    # Boton para restaurar desde el ultimo backup
    def on_pbutton25_pressed(self):
        if self.click():
            popUp = authorizationPopUp(parent=self)
            if popUp.exec_():
                adminUsername, adminPassword = popUp.getValues()
                if (adminUsername and adminPassword) != None:
                    if self.db.checkPassword(adminUsername, adminPassword):
                        userRange = self.db.getUserRange(adminUsername)
                        if userRange == "Administrador" or userRange == "Dios":
                            popUp = confirmationPopUp("Todas las operaciones que no esten en el backup se perderán", self)
                            if popUp.exec_():
                                if popUp.getValue():
                                    if self.db.restore():
                                        # Operación exitosa
                                        successPopUp(parent = self).exec_()

                                    else:
                                        # Operación fallida
                                        errorPopUp(parent = self).exec_()

                                    # Refrescar
                                    self.refresh()

                        else:
                            errorPopUp("El usuario "+ adminUsername +" no es administrador", self).exec_()
                    else:
                        errorPopUp("Datos incorrectos", self).exec_()

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

                                    # Refrescar
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

    # Botón de cancelar en el apartado del usuario
    def on_cancelpb20_pressed(self):
        if self.click():
            if  self.subStacked18.currentIndex() == 0:
                self.loadUserInfo()

            if  self.subStacked18.currentIndex() == 1:
                self.clearLEs(self.confLE0)

            else:
                self.loadUserPreferences()

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
