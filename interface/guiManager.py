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

from sys import path                        # Importación del path del sistema
from os.path import join, split, basename   # Importación de funciones para unir y separar paths con el formato del sistema

# Para cada path en el path del sistema para la aplicación
for current in path:
    if basename(current) == "interface":
        path.append(join(split(current)[0], "modules"))                          # Agregar la carpeta modules al path
        path.append(join(split(current)[0], "models"))                           # Agregar la carpeta models al path
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
from popUps import errorPopUp, successPopUp, authorizationPopUp

# Módulo que contiene los recursos de la interfaz
import gui_rc

# Módulo con las herramientas parar trabajar los archivos .ui
from PyQt4.uic import loadUiType

# Módulo con procedimientos de Qt
from PyQt4.QtCore import Qt, QMetaObject, pyqtSignal, QDir

# Módulo con estructuras de Qt
from PyQt4.QtGui import QMainWindow, QApplication, QStringListModel, QCompleter, QIntValidator, QHeaderView, QTableWidgetItem, QFileDialog, QIcon, QLineEdit, QLabel, QPushButton

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
## PROCEDIMIENTOS:
###################################################################################################################################################################################

# Devuelve un string con el stylesheet especificado por el parametro name
def getStyle(name):
    file = open(join(stylePath, name), "r")
    style = file.read()
    file.close()
    return style

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
        self.setupUi(self)                      # Configuración de la plantilla
        self.user = user                        # Asignación del usuario que ejecuta la sesión
        self.db = database                      # Asignación del manejador de la base de datos

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # VARIABLES PARA FACILITAR EL USO DE VARIOS MÉTODOS DE LA CLASE
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        self.clicked = False                # Variable de control para saber si un QPushbutton es presionado
        self.writing = False                # Variable de control para saber si el texto de un QLineEdit ha cambiado
        self.newIndex = False               # Variable de control para saber si se está cambiando la el index de un comboBox
        self.indexMutex = False             # Semáforo especial para no actualizar dos veces al cambiar el index del comboBox de lotes
        self.lotMutex1 = False              # Semáforo para saber cuando cargar la info de un lote en los QlineEdit
        self.selectedRowChanged = False     # Variable de control para saber si se cambio la fila seleccionada de un QTableWidget
        self.currentLot = "0"               # Variable de control para el comboBox de seleccion de lotes
        self.currentLots = {}               # Diccionario para lotes de un producto consultado actualmente
        self.tempImage = ""                 # Imagen seleccionada
        self.selectedProductRemaining = {}  # Diccionario de cotas superiores para el spinBox de ventas
        self.selectedProductName = ""       # Nombre del producto seleccionado actualmente en la vista de ventas
        self.selectedProducts = {}          # Diccionario de productos en la factura en la vista de ventas
        self.dateFormat = "%d/%m/%Y"        # Formato de fecha
        self.top10 = []                     # Lista de productos en Top 10
        self.new10 = []                     # Lista de productos en Nuevos

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
                        self.table8, self.table9, self.table10, self.table11]

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
        self.salesClientLE0 = [self.lineE18, self.lineE19, self.lineE20]
        self.salesClientLE1 = [self.lineE17, self.lineE18, self.lineE19, self.lineE20]

        # Apartado de pago en la vista de ventas
        self.salesCheckoutLE = [self.lineE21, self.lineE22, self.lineE152]

        # SpinLines en la vista de ventas
        self.spinBox = [self.spinLine0]

        self.popularItems = [self.popularItem0, self.popularItem1, self.popularItem2, self.popularItem3, self.popularItem4, self.popularItem5, self.popularItem6, self.popularItem7, self.popularItem8, self.popularItem9]

        self.newItems = [self.newItem0, self.newItem1, self.newItem2, self.newItem3, self.newItem4, self.newItem5, self.newItem6, self.newItem7, self.newItem8, self.newItem9]

        self.popularTexts = [self.text44, self.text45, self.text46, self.text47, self.text48, self.text49, self.text50, self.text51, self.text52, self.text53]
        self.newTexts = [self.text54, self.text55, self.text56, self.text57, self.text58, self.text59, self.text60, self.text61, self.text62, self.text63]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE CONFIGURACIONES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de cambio de contraseña
        self.confLE0 = [self.lineE153, self.lineE154, self.lineE155]

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
            if numValidator: lineE.setValidator(QIntValidator(0, 100000000))
            lineE.setCompleter(LEcompleter)

    # Método para configurar un spinLine
    def setupSpinLines(self, listSL):
        for spinL in listSL: spinL.setValidator(QIntValidator(0, 9999999))

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
    def setupTable(self, table):
        table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)

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
        self.refreshBox()

        # Se establece la pagina de caja por defecto
        self.MainStacked.setCurrentIndex(0)
        self.MainTitle.setText("Caja")

    def generalSetup(self):
        # Centrar posición de la ventana
        self.center()

        # Establecer tamaño y ocultar botones de la ventana
        self.setSize()

        # Configurar los spin box
        self.setupSpinLines(self.spinBox)
        self.add0.setAutoRepeat(True)
        self.substract0.setAutoRepeat(True)

    #==============================================================================================================================================================================
    # CAMBIO DE PÁGINA DE LOS STACKED
    #==============================================================================================================================================================================

    # Cambiar a la página principal
    def on_home_pressed(self):
        if self.click():
            self.setPage(self.MainStacked, 0)
            self.MainTitle.setText("Caja")

     # Cambiar a la página de ventas
    def on_sales_pressed(self):
        if self.click() and self.db.isOpenPeriod() and self.db.isOpenDay() and self.db.isOpenTurn():
            self.setPage(self.MainStacked, 1)
            self.MainTitle.setText("Ventas")

    # Cambiar a la página de inventario
    def on_inventory_pressed(self):
        if self.click() and self.db.isOpenPeriod() and self.db.isOpenDay() and self.db.isOpenTurn():
            self.setPage(self.MainStacked, 2)
            self.MainTitle.setText("Inventario")

    # Cambiar a la página de consultas
    def on_querys_pressed(self):
        if self.click() and self.db.isOpenPeriod() and self.db.isOpenDay() and self.db.isOpenTurn():
            self.setPage(self.MainStacked, 3)
            self.MainTitle.setText("Consultas")

    # Cambiar a la página de préstamos
    def on_loans_pressed(self):
        if self.click() and self.db.isOpenPeriod() and self.db.isOpenDay() and self.db.isOpenTurn():
            self.setPage(self.MainStacked, 4)
            self.MainTitle.setText("Préstamos")

    # Cambiar a la página de libros
    def on_books_pressed(self):
        if self.click() and self.db.isOpenPeriod() and self.db.isOpenDay() and self.db.isOpenTurn():
            self.setPage(self.MainStacked, 5)
            self.MainTitle.setText("Libros")

    # Cambiar a la página de clientes
    def on_providers_pressed(self):
        if self.click() and self.db.isOpenPeriod() and self.db.isOpenDay() and self.db.isOpenTurn():
            self.setPage(self.MainStacked, 6)
            self.MainTitle.setText("Proveedores")

    # Cambiar a la página de clientes
    def on_clients_pressed(self):
        if self.click() and self.db.isOpenPeriod() and self.db.isOpenDay() and self.db.isOpenTurn():
            self.setPage(self.MainStacked, 7)
            self.MainTitle.setText("Clientes")

    # Cambiar a la página de clientes
    def on_transfer_pressed(self):
        if self.click() and self.db.isOpenPeriod() and self.db.isOpenDay() and self.db.isOpenTurn():
            self.setPage(self.MainStacked, 8)
            self.MainTitle.setText("Recargas de saldo")

    # Cambiar a la página de usuarios
    def on_users_pressed(self):
        if self.click() and self.db.isOpenPeriod() and self.db.isOpenDay() and self.db.isOpenTurn():
            self.setPage(self.MainStacked, 9)
            self.MainTitle.setText("Usuarios")

    # Cambiar a la página de configuraciones
    def on_configure_pressed(self):
        if self.click() and self.db.isOpenPeriod() and self.db.isOpenDay() and self.db.isOpenTurn():
            self.setPage(self.MainStacked, 10)
            self.MainTitle.setText("Configuraciones")

    # Cambiar a la página de ayuda
    def on_help_pressed(self):
        if self.click() and self.db.isOpenPeriod() and self.db.isOpenDay() and self.db.isOpenTurn():
            self.setPage(self.MainStacked, 11)
            self.MainTitle.setText("Ayuda")

    def on_arrow1_pressed(self): self.changePage(self.subStacked3)      # Cambiar la página del substaked3 hacia la derecha
    def on_arrow3_pressed(self): self.changePage(self.subStacked4)      # Cambiar la página del substaked4 hacia la derecha
    def on_arrow5_pressed(self): self.changePage(self.subStacked5)      # Cambiar la página del substaked5 hacia la derecha
    def on_arrow7_pressed(self): self.changePage(self.subStacked6)      # Cambiar la página del substaked6 hacia la derecha
    def on_arrow9_pressed(self): self.changePage(self.subStacked7)      # Cambiar la página del substaked7 hacia la derecha
    def on_arrow11_pressed(self): self.changePage(self.subStacked8)     # Cambiar la página del substaked8 hacia la derecha
    def on_arrow13_pressed(self): self.changePage(self.subStacked9)     # Cambiar la página del substaked9 hacia la derecha
    def on_arrow15_pressed(self): self.changePage(self.subStacked10)    # Cambiar la página del substaked10 hacia la derecha
    def on_arrow17_pressed(self): self.changePage(self.subStacked11)    # Cambiar la página del substaked11 hacia la derecha
    def on_arrow19_pressed(self): self.changePage(self.subStacked12)    # Cambiar la página del substaked12 hacia la derecha
    def on_arrow21_pressed(self): self.changePage(self.subStacked13)    # Cambiar la página del substaked13 hacia la derecha
    def on_arrow23_pressed(self): self.changePage(self.subStacked14)    # Cambiar la página del substaked14 hacia la derecha
    def on_arrow25_pressed(self): self.changePage(self.subStacked15)    # Cambiar la página del substaked15 hacia la derecha
    def on_arrow27_pressed(self): self.changePage(self.subStacked16)    # Cambiar la página del substaked16 hacia la derecha
    def on_arrow29_pressed(self): self.changePage(self.subStacked17)    # Cambiar la página del substaked17 hacia la derecha
    def on_arrow31_pressed(self): self.changePage(self.subStacked18)    # Cambiar la página del substaked18 hacia la derecha
    def on_arrow33_pressed(self): self.changePage(self.subStacked19)    # Cambiar la página del substaked18 hacia la derecha

    def on_arrow0_pressed(self): self.changePage(self.subStacked3, 1)   # Cambiar la página del substaked3 hacia la izquierda
    def on_arrow2_pressed(self): self.changePage(self.subStacked4, 1)   # Cambiar la página del substaked4 hacia la izquierda
    def on_arrow4_pressed(self): self.changePage(self.subStacked5, 1)   # Cambiar la página del substaked5 hacia la izquierda
    def on_arrow6_pressed(self): self.changePage(self.subStacked6, 1)   # Cambiar la página del substaked6 hacia la izquierda
    def on_arrow8_pressed(self): self.changePage(self.subStacked7, 1)   # Cambiar la página del substaked7 hacia la izquierda
    def on_arrow10_pressed(self): self.changePage(self.subStacked8, 1)  # Cambiar la página del substaked8 hacia la izquierda
    def on_arrow12_pressed(self): self.changePage(self.subStacked9, 1)  # Cambiar la página del substaked9 hacia la izquierda
    def on_arrow14_pressed(self): self.changePage(self.subStacked10, 1) # Cambiar la página del substaked10 hacia la izquierda
    def on_arrow16_pressed(self): self.changePage(self.subStacked11, 1) # Cambiar la página del substaked11 hacia la izquierda
    def on_arrow18_pressed(self): self.changePage(self.subStacked12, 1) # Cambiar la página del substaked12 hacia la izquierda
    def on_arrow20_pressed(self): self.changePage(self.subStacked13, 1) # Cambiar la página del substaked13 hacia la izquierda
    def on_arrow22_pressed(self): self.changePage(self.subStacked14, 1) # Cambiar la página del substaked14 hacia la izquierda
    def on_arrow24_pressed(self): self.changePage(self.subStacked15, 1) # Cambiar la página del substaked15 hacia la izquierda
    def on_arrow26_pressed(self): self.changePage(self.subStacked16, 1) # Cambiar la página del substaked16 hacia la izquierda
    def on_arrow28_pressed(self): self.changePage(self.subStacked17, 1) # Cambiar la página del substaked17 hacia la izquierda
    def on_arrow30_pressed(self): self.changePage(self.subStacked18, 1) # Cambiar la página del substaked18 hacia la izquierda
    def on_arrow32_pressed(self): self.changePage(self.subStacked19, 1) # Cambiar la página del substaked18 hacia la izquierda

    #==============================================================================================================================================================================
    # VISTA DE CAJA
    #==============================================================================================================================================================================
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para actualizar caja
    def refreshBox(self):
        date = datetime.now().date()
        cash, transfer = self.db.getBalance(date, date)
        self.lineE1.setText(str(cash))
        self.lineE2.setText(str(transfer))

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------



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

    # Radio button para consultar productos
    def on_rbutton6_pressed(self):
        if self.click():
            self.deleteProductInput()
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1)
            self.text64.setText("Buscar")
            self.resetProductImage(self.selectedItem1)

    # Radio button para editar productos
    def on_rbutton7_pressed(self):
        if self.click():
            self.addProductInput()
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1, listaLE1 = self.productsRO3)
            self.resetProductImage(self.selectedItem1)

    # Radio button para eliminar productos
    def on_rbutton8_pressed(self):
        if self.click():
            self.deleteProductInput()
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1)
            self.text64.setText("Nombre")
            self.resetProductImage(self.selectedItem1)

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
                    if not self.db.existProduct(product_name):
                        # Obtener información del nuevo producto
                        price = self.lineE27.text()
                        categoy = self.lineE28.text()

                        # Agregar el producto a la BD
                        self.db.createProduct(product_name, price, categoy)

                        if self.tempImage != "":
                            copy2(self.tempImage, join(productPath, product_name))

                        # Refrescar toda la interfaz
                        self.refreshInventory()
                        self.refreshNew10()

                        # Enfocar
                        self.lineE26.setFocus()

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
                            self.db.updateProduct(product_name, newName, newPrice, newCategory)

                        # Refrescar toda la interfaz
                        self.refreshInventory()

                        # Enfocar
                        self.lineE26.setFocus()

            # Modalidad para eliminar productos
            elif self.rbutton8.isChecked():
                if self.lineE26.text() != "":
                    product_name = self.lineE26.text()
                    if self.db.existProduct(product_name):
                        # Eliminar producto
                        self.db.deleteProduct(product_name)

                        # Refrescar toda la interfaz
                        self.refreshInventory()

                        # Enfocar
                        self.lineE26.setFocus()

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

                    kwargs = {
                        "product_name"  : product_name,
                        "provider_name" : provider_name,
                        "received_by"   : self.user,
                        "cost"          : int(cost),
                        "quantity"      : quantity
                    }

                    #if expiration_date != "": kwargs["expiration_date"] = expiration_date

                    # Agregar el lote a la BD
                    self.db.createLot(**kwargs)

                    self.refreshInventory()      # Refrescar toda la interfaz
                    self.lineE33.setFocus()      # Enfocar

            # Modalidad para consultar lotes
            elif self.rbutton10.isChecked():
                self.refreshInventory()      # Refrescar toda la interfaz
                self.lineE33.setFocus()      # Enfocar

            # Modalidad para editar lotes
            elif self.rbutton11.isChecked():
                if (self.lineE33.text() and self.lineE34.text()) != "":
                    product_name = self.lineE33.text()        # Producto
                    provider_name = self.lineE34.text()         # Proveedor
                    if self.db.existProduct(product_name) and self.db.existProvider(provider_name):

                        lot_id = self.currentLots[self.currentLot]                        # Lote
                        cost = float(self.lineE35.text())                                 # Costo
                        """if self.dtE2.text() != "None":
                            expiration_date = datetime.strptime(self.dtE2.text(), self.dateFormat)  # Caducidad"""
                        quantity = int(self.lineE37.text())                               # Cantidad
                        remaining = int(self.lineE38.text())                              # Disponibles

                        self.db.updateLot(lot_id, product_name, provider_name, cost, quantity, remaining)

                        # Refrescar toda la interfaz
                        self.refreshInventory()

                        # Enfocar
                        self.lineE33.setFocus()

            # Modalidad para eliminar lotes
            elif self.rbutton12.isChecked():
                if (self.lineE33.text() and self.lineE34.text()) != "":
                    product_name = self.lineE33.text()        # Producto
                    provider_name = self.lineE34.text()         # Proveedor
                    if self.db.existProduct(product_name) and self.db.existProvider(provider_name):

                        lot_id = self.currentLots[self.currentLot]                        # Lote

                        self.db.deleteLot(lot_id)

                        # Refrescar toda la interfaz
                        self.refreshInventory()

                        # Enfocar
                        self.lineE33.setFocus()

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

                        self.lineE34.setText(lot.provider_name)      # Proveedor
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

                self.lineE34.setText(lot.provider_name)      # Proveedor
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
        self.refreshBox()

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
        count = int(self.spinLine0.text())
        if count > 0:
            self.spinLine0.setText(str(count-1))
            self.lineE25.setText(str(((count-1)*float(self.lineE24.text()))))

    # Sumar al spinBox
    def addToSalesSpinBox(self):
        count = int(self.spinLine0.text())
        if self.selectedProductName in self.selectedProductRemaining:
            if count < self.selectedProductRemaining[self.selectedProductName]:
                self.spinLine0.setText(str(count+1))
                self.lineE25.setText(str(((count+1)*float(self.lineE24.text()))))

    # Seleccionar un item de las listas Top 10 y Nuevo
    def selectPopularItem(self, n):
        if n < len(self.top10):
            product_name = self.top10[n].product_name
            if self.lineE23.text() != product_name:
                self.lineE23.setText(product_name)
                self.clearSpinLines(self.spinBox)

            self.addToSalesSpinBox()

    # Seleccionar un item de las listas Top 10 y Nuevo
    def selectNewItem(self, n):
        if n < len(self.new10):
            product_name = self.new10[n].product_name
            if self.lineE23.text() != product_name:
                self.lineE23.setText(product_name)
                self.clearSpinLines(self.spinBox)

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
            if (self.lineE17.text() and self.lineE21.text()) != "":
                ci = int(self.lineE17.text())
                if  self.db.existClient(ci):
                    total = float(self.lineE21.text())
                    efectivo = 0
                    saldo = 0

                    if self.lineE22.text() != "": efectivo = float(self.lineE22.text())
                    if self.lineE152.text() != "": saldo = float(self.lineE152.text())

                    if efectivo + saldo >= total:

                        purchase_id = self.db.createPurchase(ci, self.user)

                        for key, val in self.selectedProducts.items():
                            self.db.createProductList(purchase_id, key, float(val[0]), int(val[1]))

                        if efectivo > 0: self.db.createCheckout(purchase_id, efectivo)
                        if saldo > 0: self.db.createCheckout(purchase_id, saldo, True)

                        # Setear variables y refrescar la interfaz
                        self.refreshSales()

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

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CAMPOS DE TEXTO
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # LineEdit para ingresar la cédula del cliente
    def on_lineE17_textChanged(self):
        if self.textChanged():
            if self.lineE17.text() != "":
                ci = int(self.lineE17.text())
                if self.db.existClient(ci):
                    client = self.db.getClients(ci)[0]                            # Obtener cliente
                    self.lineE18.setText(client.firstname)                       # Establecer Nombre
                    self.lineE19.setText(client.lastname)                        # Establecer Apellido
                    self.lineE20.setText(str(client.balance))                    # Establecer Saldo
                    self.lineE152.setValidator(QIntValidator(0, client.balance)) # Establecer limite de saldo para pagar

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

                if self.lineE22.text() != "":
                    efectivo = float(self.lineE22.text())
                    cota1 = total - efectivo

                    if self.lineE17.text() != "":
                        ci = int(self.lineE17.text())
                        if self.db.existClient(ci):
                            balance = self.db.getClients(ci)[0].balance

                            if balance < cota1:
                                cota1 = balance

                        else: cota1 = 0
                    else: cota1 = 0

                self.lineE152.setValidator(QIntValidator(0, cota1))
                if self.lineE152.text() != "":
                    saldo = float(self.lineE152.text())

                    if saldo > cota1:
                        self.lineE152.setText(str(cota1))

                if self.lineE152.text() != "":
                    saldo = float(self.lineE152.text())
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
                if self.lineE22.text() != "":
                    efectivo = float(self.lineE22.text())
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
                if self.lineE152.text() != "":
                    saldo = float(self.lineE152.text())
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

                if product_name not in self.selectedProducts:
                    self.selectedProductRemaining[product_name] = product.remaining

                self.selectedItem0.setIcon(QIcon(join(productPath, product_name)))

            else:
                self.clearLEs(self.selectedProductLE0)
                self.clearSpinLine(self.spinLine0)
                self.resetProductImage(self.selectedItem0)

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # TABLAS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Cambio de selección en la factura
    def on_table11_itemClicked(self, item):
        if self.rowChanged():
            if item.column() != 4:
                items = self.table11.selectedItems()
                self.lineE23.setText(items[0].text())
                self.lineE24.setText(items[1].text())
                self.spinLine0.setText(items[2].text())
                self.lineE25.setText(items[3].text())

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

    # Método para refrescar la tabla de factura en ventas
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
            if self.lineE146.text() != "":
                kwargs = {
                    "provider_name"   : self.lineE146.text(),
                    "phone"           : self.lineE147.text(),
                    "email"           : self.lineE148.text(),
                    "description"     : self.textE1.toPlainText(),
                    "pay_information" : self.textE2.toPlainText()
                }
                self.db.createProvider(**kwargs)

                self.clearLEs(self.providersLE0) # Limpiar formulario
                self.refreshProviders()          # Refrescar vista
                self.lineE146.setFocus()         # Enfocar

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

        # Refrescar tabla
        self.updateClientsTable()
        self.updateClientsTable(True)

    # Método para refrescar la tabla de factura en ventas
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

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Botón para crear un cliente
    def on_pbutton17_pressed(self):
        if self.click():
            if self.lineE52.text() != "" and self.lineE53.text() != "" and self.lineE54.text() != "":
                ci = int(self.lineE52.text())
                if not self.db.existClient(ci):
                    kwargs = {
                        "ci"        : ci,
                        "firstname" : self.lineE53.text(),
                        "lastname"  : self.lineE54.text(),
                        "phone"     : self.lineE55.text(),
                        "email"     : self.lineE56.text()
                    }

                    self.db.createClient(**kwargs) # Crear cliente
                    self.clearLEs(self.clientsLE0) # Limpiar formulario
                    self.refreshClients()          # Refrescar vista
                    self.lineE52.setFocus()        # Enfocar

    # Botón para editar un cliente
    def on_pbutton19_pressed(self):
        if self.click():
            if self.lineE57.text() != "" and self.lineE58.text() != "" and self.lineE59.text() != "":
                ci = int(self.lineE52.text())
                if not self.db.existClient(ci):
                    kwargs = {
                        "firstname" : self.lineE58.text(),
                        "lastname"  : self.lineE59.text(),
                        "phone"     : self.lineE60.text(),
                        "email"     : self.lineE61.text()
                    }

                    self.db.updateClient(**kwargs) # Crear cliente
                    self.clearLEs(self.clientsLE1) # Limpiar formulario
                    self.refreshClients()          # Refrescar vista
                    self.lineE57.setFocus()        # Enfocar

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

        self.refreshClients()
        self.refreshBox()

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
                    if pay_type == "Efectivo":
                        if self.lineE158.text() != "":
                            amount = float(self.lineE158.text())

                            self.db.addToClientBalance(ci, amount)

                            self.refreshTransfers()

                            self.lineE47.setFocus()

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

    # Método para refrescar la tabla de factura en ventas
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
            if (self.lineE69.text() and self.lineE70.text() and self.lineE71.text() and self.lineE72.text() and self.lineE73.text()) != "":
                username = self.lineE69.text()
                if not self.db.existUser(username):

                    kwargs = {
                        "username"        : username,
                        "firstname"       : self.lineE70.text(),
                        "lastname"        : self.lineE71.text(),
                        "email"           : self.lineE72.text(),
                        "password"        : self.lineE73.text(),
                        "permission_mask" : self.db.getPermissionMask(self.cbox8.currentText())
                    }

                    self.db.createUser(**kwargs) # Crear cliente
                    self.refreshUsers()          # Refrescar vista
                    self.lineE69.setFocus()      # Enfocar

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

                    self.db.updateUserRange(**kwargs) # Actualizar cliente
                    self.refreshUsers()               # Refrescar vista
                    self.lineE75.setFocus()           # Enfocar

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
        self.setStyleSheet(getStyle(name))

    # Método para cargar la información del usuario
    def loadUserInfo(self):
        user = self.db.getUsers(self.user)[0]
        self.lineE81.setText(user.username)
        self.lineE82.setText(user.firstname)
        self.lineE83.setText(user.lastname)
        self.lineE84.setText(user.email)
        self.lineE85.setText(self.db.getRange(user.permission_mask))
        #self.userBn0.setText(" ".join([user.firstname, user.lastname]))

    # Método para cargar las preferencias del usuario
    def loadUserPreferences(self):
        user = self.db.getUsers(self.user)[0]
        if user.profile != "": self.theme = user.profile
        else: self.theme = "blue.qss"
        self.setStyle(self.theme)

    # Método para cambiar el usuario que usa la intefáz
    def changeUser(self, user):
        self.user = user
        self.refresh()

    # Método para refrescar la vista de Configuraciones y componentes relacionados
    def refreshConfigurations(self):
        self.refreshUsers()
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
                if (self.lineE82.text() and self.lineE83.text() and self.lineE84.text()) != "":
                    self.db.updateUserInfo(self.user, self.lineE82.text(), self.lineE83.text(), self.lineE84.text())
                    self.refreshUsers()

            # Contraseña
            elif self.subStacked18.currentIndex() == 1:
                if self.lineE153.text() != "":
                    password = self.lineE153.text()
                    if self.db.checkPassword(self.user, password):
                        if (self.lineE154.text() and self.lineE155.text()) != "":
                            if self.lineE154.text() == self.lineE155.text():
                                newPassword = self.lineE154.text()
                                self.db.changePassword(self.user, password, newPassword)
                                self.clearLEs(self.confLE0)

            # Tema
            else:
                self.db.updateUserProfile(self.user, self.theme)

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
        event.ignore()      # Aceptar el evento y cerrar la ventana
        self.closed.emit()  # Emitir señal para que la ventana de inicio aparezca
        self.hide()

###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################
