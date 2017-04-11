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

# Importación de la función para obtener el path actual
from os import getcwd

# Importación de función para unir paths con el formato del sistema
from os.path import join

# Módulo que contiene los recursos de la interfaz
import gui_rc

# Módulo con las herramientas parar trabajar los archivos .ui
from PyQt4.uic import loadUiType

# Módulo con procedimientos de Qt
from PyQt4.QtCore import Qt, QMetaObject, pyqtSignal, QDir

# Módulo con estructuras de Qt
from PyQt4.QtGui import QMainWindow, QApplication, QStringListModel, QCompleter, QIntValidator, QHeaderView, QTableWidgetItem, \
QFileDialog, QIcon

# Módulo manejador de la base de datos
from db_manager import dbManager

####################################################################################################################################
## CONSTANTES:
####################################################################################################################################

# Paths
UIpath = join(getcwd(), "interface/qt/ui/")
stylePath = join(getcwd(), "interface/qt/stylesheet/MainWindow/")
productPath = join(getcwd(), "interface/images/inventory/")

# UI
MainUI = "material.ui"

# Styles
styles = ["teal.qss", "default.qss", "pink.qss", "green.qss", "orange.qss", "purple.qss", "red.qss", "yellow.qss"]
LEpopup = "LEpopup.qss"

# Interfaz .ui creada con qt designer
form_class = loadUiType(UIpath+MainUI)[0]

# Constante de primer inicio
A = True

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

# Ejemplo de lista de cédulas de clientes
clientList = ["513264", "28436485", "32564336", "105746567", "280765423", "670124583"]

####################################################################################################################################
## MANEJADOR DE LA INTERFAZ GRÁFICA:
####################################################################################################################################

class adminGUI(QMainWindow, form_class):
    closed = pyqtSignal()
    #-------------------------------------------------------------------------------------------------------------------------------
    # Constructor de la clase
    #-------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, user, database, parent=None):
        #---------------------------------------------------------------------------------------------------------------------------
        # Iniciar y configurar la interfaz y la base de datos
        #---------------------------------------------------------------------------------------------------------------------------

        # Interfaz
        super(adminGUI, self).__init__(parent)
        self.setupUi(self)

        # Usuario del programa
        self.user = user

        # Manejador de la base de datos
        self.db = database

        #---------------------------------------------------------------------------------------------------------------------------
        # Listas necesarias para algunos métodos útiles
        #---------------------------------------------------------------------------------------------------------------------------

        # Parametros para buscar en la tabla de productos
        self.productsParams0 = {
            "product_name" : True,
            "active"       : True
        }

        self.productsParams1 = {
            "product_id"     : True,
            "product_name"   : True,
            "price"          : True,
            "remaining"      : True,
            "remaining_lots" : True,
            "category"       : True,
            "active"         : True
        }

        # Barras de búsqueda por cédula:
        self.ciSearch = [self.lineE17, self.lineE47, self.lineE52, self.lineE57]

        # Barras de búsqueda por nombre de producto:
        self.productSearch = [self.lineE23, self.lineE26, self.lineE33]

        # Apartado de productos en inventario
        self.productsRO0 = [self.lineE26, self.lineE27, self.lineE28, self.lineE29, self.lineE30]
        self.productsRO1 = [self.lineE27, self.lineE28, self.lineE29, self.lineE30]
        self.productsRO2 = [self.lineE27, self.lineE28]

        # Apartado de lotes en inventario
        self.lotsRO0 = [self.lineE33, self.lineE34, self.lineE35, self.lineE36, self.lineE37, self.lineE38]
        self.lotsRO1 = [self.lineE34, self.lineE35, self.lineE36, self.lineE37, self.lineE38]
        self.lotsRO2 = [self.lineE34, self.lineE35, self.lineE36, self.lineE37]
        self.lotsRO3 = [self.lineE38]

        # Tablas
        self.tables = [self.table0, self.table1, self.table2, self.table3, self.table4, self.table5, self.table6, self.table7,
                        self.table8, self.table9, self.table10, self.table11]

        # SpinLines
        self.spinBox = [self.spinLine0]

        #---------------------------------------------------------------------------------------------------------------------------
        # Cargar configuraciones iniciales
        #---------------------------------------------------------------------------------------------------------------------------

        # Se connectan los botones entre otras cosas con algunos de los métodos definidos a continuación
        QMetaObject.connectSlotsByName(self)

        # Variables de control
        self.clicked = False        # QPushbutton presionado
        self.writing = False        # Texto de un QLineEdit cambiado
        self.currentProduct = None  # Instancia de producto en uso

        # Variables para almacenar data temporal
        self.tempImage = ""

        # Aplicar configuraciones generales de la interfaz
        self.generalSetup()

        # Refrescar todos los elementos de la interfaz
        self.refresh()

        # Se establece la pagina de caja por defecto
        self.MainStacked.setCurrentIndex(0)
        self.MainTitle.setText("Caja")

    #-------------------------------------------------------------------------------------------------------------------------------
    # Configuraciones básicas de la ventana
    #-------------------------------------------------------------------------------------------------------------------------------

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

    #-------------------------------------------------------------------------------------------------------------------------------
    # Procedimientos de la clase (Métodos)
    #-------------------------------------------------------------------------------------------------------------------------------

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

    # Cambiar página de un QStackedWidget
    def setPage(self, stacked, index):
        if self.click(): stacked.setCurrentIndex(index)

    # Cambiar página de un QStackedWidget
    def changePage(self, stacked, move = -1):
        if self.click():
            if move == -1: stacked.setCurrentIndex((stacked.currentIndex()+stacked.count()-1)%stacked.count())
            if move == 1: stacked.setCurrentIndex((stacked.currentIndex()+1)%stacked.count())

    # Seleccionar un item de las listas Top 10 y Nuevo
    def selectItem(self, n):
        if self.click(): self.lineE23.setText(str(n))

    # Cambiar el tema de la interfáz
    def setStyle(self, name):
        if self.click(): self.setStyleSheet(getStyle(name))

    def setupLE(self):

        self.lineE0.setPlaceholderText("Balance")
        self.lineE1.setPlaceholderText("Efectivo")
        self.lineE2.setPlaceholderText("Transferencias")
        self.lineE3.setPlaceholderText("Deudas")

        self.lineE4.setPlaceholderText("Monto")
        self.lineE31.setPlaceholderText("Monto")
        self.lineE32.setPlaceholderText("Monto")

        self.lineE5.setPlaceholderText("Estado")
        self.lineE6.setPlaceholderText("Inicio")
        self.lineE7.setPlaceholderText("Ventas")
        self.lineE8.setPlaceholderText("Ingresos")
        self.lineE9.setPlaceholderText("Egresos")
        self.lineE10.setPlaceholderText("Ganancias")

        self.lineE11.setPlaceholderText("Nombre")
        self.lineE12.setPlaceholderText("Inicio")
        self.lineE13.setPlaceholderText("Ventas")
        self.lineE14.setPlaceholderText("Ingresos")
        self.lineE15.setPlaceholderText("Egresos")
        self.lineE16.setPlaceholderText("Ganancias")

        # Ventas
        self.lineE17.setPlaceholderText("Cédula")
        self.lineE18.setPlaceholderText("Nombre")
        self.lineE19.setPlaceholderText("Apellido")
        self.lineE20.setPlaceholderText("Saldo")
        self.lineE21.setPlaceholderText("Total")
        self.lineE22.setPlaceholderText("Pagar")

        self.lineE23.setPlaceholderText("Producto")
        self.lineE24.setPlaceholderText("Precio")
        self.lineE25.setPlaceholderText("Subtotal")

        self.lineE26.setPlaceholderText("Nombre")
        self.lineE27.setPlaceholderText("Precio")
        self.lineE28.setPlaceholderText("Categoria")
        self.lineE29.setPlaceholderText("Lotes")
        self.lineE30.setPlaceholderText("Disponibilidad")

        self.lineE33.setPlaceholderText("Producto")
        self.lineE34.setPlaceholderText("Proveedor")
        self.lineE35.setPlaceholderText("Costo")
        self.lineE36.setPlaceholderText("Caducidad")
        self.lineE37.setPlaceholderText("Cantidad")
        self.lineE38.setPlaceholderText("Disponibles")

        self.lineE39.setPlaceholderText("Nombre")
        self.lineE40.setPlaceholderText("Fecha de inicio")
        self.lineE41.setPlaceholderText("Fecha de cierre")
        self.lineE42.setPlaceholderText("Días laborados")
        self.lineE43.setPlaceholderText("Ventas totales")
        self.lineE44.setPlaceholderText("Ingresos")
        self.lineE45.setPlaceholderText("Egresos")
        self.lineE46.setPlaceholderText("Ganancias")

        self.lineE47.setPlaceholderText("Cédula")
        self.lineE48.setPlaceholderText("Nombre")
        self.lineE49.setPlaceholderText("Apellido")
        self.lineE50.setPlaceholderText("Saldo")
        self.lineE51.setPlaceholderText("Déposito")

        self.lineE52.setPlaceholderText("Cédula")
        self.lineE53.setPlaceholderText("Nombre")
        self.lineE54.setPlaceholderText("Apellido")
        self.lineE55.setPlaceholderText("Teléfono")
        self.lineE56.setPlaceholderText("Correo")

        self.lineE57.setPlaceholderText("Cédula")
        self.lineE58.setPlaceholderText("Nombre")
        self.lineE59.setPlaceholderText("Apellido")
        self.lineE60.setPlaceholderText("Teléfono")
        self.lineE61.setPlaceholderText("Correo")

        self.lineE62.setPlaceholderText("Usuario")
        self.lineE63.setPlaceholderText("Nombre")
        self.lineE64.setPlaceholderText("Apellido")
        self.lineE65.setPlaceholderText("Teléfono")
        self.lineE66.setPlaceholderText("Correo")
        self.lineE67.setPlaceholderText("Contraseña")
        self.lineE68.setPlaceholderText("Rango")

        self.lineE69.setPlaceholderText("Usuario")
        self.lineE70.setPlaceholderText("Nombre")
        self.lineE71.setPlaceholderText("Apellido")
        self.lineE72.setPlaceholderText("Teléfono")
        self.lineE73.setPlaceholderText("Correo")
        self.lineE74.setPlaceholderText("Contraseña")

        self.lineE75.setPlaceholderText("Usuario")
        self.lineE76.setPlaceholderText("Nombre")
        self.lineE77.setPlaceholderText("Apellido")
        self.lineE78.setPlaceholderText("Teléfono")
        self.lineE79.setPlaceholderText("Correo")
        self.lineE80.setPlaceholderText("Contraseña")

        self.lineE81.setPlaceholderText("Usuario")
        self.lineE82.setPlaceholderText("Nombre")
        self.lineE83.setPlaceholderText("Apellido")
        self.lineE84.setPlaceholderText("Teléfono")
        self.lineE85.setPlaceholderText("Correo")
        self.lineE86.setPlaceholderText("Contraseña")
        self.lineE87.setPlaceholderText("Rango")

        self.lineE88.setPlaceholderText("R.I.F.")
        self.lineE89.setPlaceholderText("Tasa (%)")
        self.lineE90.setPlaceholderText("Tasa (%)")

        self.lineE91.setPlaceholderText("Cédula")
        self.lineE92.setPlaceholderText("Nombre")
        self.lineE93.setPlaceholderText("Apellido")
        self.lineE94.setPlaceholderText("Código")
        self.lineE95.setPlaceholderText("Titulo")
        self.lineE96.setPlaceholderText("Autor")
        self.lineE97.setPlaceholderText("Entrega")

        self.lineE98.setPlaceholderText("Titulo")
        self.lineE99.setPlaceholderText("Año")
        self.lineE100.setPlaceholderText("Edición")
        self.lineE101.setPlaceholderText("Editorial")
        self.lineE102.setPlaceholderText("Lenguaje")
        self.lineE103.setPlaceholderText("ISBN")
        self.lineE104.setPlaceholderText("Copias")
        self.lineE105.setPlaceholderText("BookID")

        self.lineE106.setPlaceholderText("BookID")
        self.lineE107.setPlaceholderText("Titulo")
        self.lineE108.setPlaceholderText("Año")
        self.lineE109.setPlaceholderText("Edición")
        self.lineE110.setPlaceholderText("Editorial")
        self.lineE111.setPlaceholderText("Lenguaje")
        self.lineE112.setPlaceholderText("ISBN")
        self.lineE113.setPlaceholderText("Disponibles")

        self.lineE114.setPlaceholderText("Código")
        self.lineE115.setPlaceholderText("Nombre")
        self.lineE116.setPlaceholderText("Código")
        self.lineE117.setPlaceholderText("Nombre")

        self.lineE118.setPlaceholderText("Nombre")
        self.lineE119.setPlaceholderText("Año")
        self.lineE120.setPlaceholderText("País")
        self.lineE121.setPlaceholderText("Nombre")
        self.lineE122.setPlaceholderText("Año")
        self.lineE123.setPlaceholderText("País")

        self.lineE124.setPlaceholderText("BookID")
        self.lineE125.setPlaceholderText("Título")
        self.lineE126.setPlaceholderText("Año")
        self.lineE127.setPlaceholderText("Edición")
        self.lineE128.setPlaceholderText("Año")
        self.lineE129.setPlaceholderText("País")
        self.lineE130.setPlaceholderText("BookID")
        self.lineE131.setPlaceholderText("Título")
        self.lineE132.setPlaceholderText("Año")
        self.lineE133.setPlaceholderText("Edición")
        self.lineE134.setPlaceholderText("Año")
        self.lineE135.setPlaceholderText("País")

        self.lineE136.setPlaceholderText("BookID")
        self.lineE137.setPlaceholderText("Título")
        self.lineE138.setPlaceholderText("Año")
        self.lineE139.setPlaceholderText("Edición")
        self.lineE140.setPlaceholderText("Nombre")
        self.lineE141.setPlaceholderText("BookID")
        self.lineE142.setPlaceholderText("Título")
        self.lineE143.setPlaceholderText("Año")
        self.lineE144.setPlaceholderText("Edición")
        self.lineE145.setPlaceholderText("Nombre")

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
    def setupSpinLine(self, listSL):
        for spinL in listSL: spinL.setValidator(QIntValidator(0, 9999999))

    # Método para configurar un spinLine
    def clearSpinLine(self, listSL):
        for spinL in listSL: spinL.setText("0")

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

    # Borrar contenido de uno o más LineEdit:
    def clearLE(self, listLE):
        for lineE in listLE: lineE.setText("")

    # Marcar en solo lectura uno o más LineEdit:
    def ReadOnlyLE(self, listLE, boolean):
        for lineE in listLE: lineE.setReadOnly(boolean)
        self.setStyleSheet(getStyle(styles[1]))

    # Cambio de estado de los line edits en un apartado
    def changeRO(self, listaLE0, boolean = True, listaLE1 = []):
        self.ReadOnlyLE(listaLE0, boolean)
        self.ReadOnlyLE(listaLE1, not(boolean))

    def setupTables(self):
        for table in self.tables:
            table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)

    # Método para refrescar la tabla de canciones en la ventana
    def updateTable(self, table, itemsList):
        for i in reversed(range(table.rowCount())): table.removeRow(i)

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

    # Método para refrescar la interfaz
    def refresh(self):
        # Listas de nombres de los productos
        self.productsNames = self.getProductList(self.productsParams0)                # Completa
        self.productsNamesAvailable = self.getProductList(self.productsParams0, 1)    # Disponibles
        self.productsNamesNotAvailable = self.getProductList(self.productsParams0, 2) # No disponibles

        # Listas con información para las tablas de productos
        self.productsInfo = self.getProductList(self.productsParams1)                # Completa
        self.productsInfoAvailable = self.getProductList(self.productsParams1, 1)    # Disponibles
        self.productsInfoNotAvailable = self.getProductList(self.productsParams1, 2) # No disponibles

        # Configuración de la barra de búsqueda de cliente por CI
        self.setupSearchBar(self.ciSearch, clientList, True)

        # Limpiar los spinLine
        self.clearSpinLine(self.spinBox)

        # Configuración de las barras de búsqueda por nombre de producto
        self.setupSearchBar(self.productSearch, self.productsNames)

        # Setup de las distintas tablas
        self.updateTable(self.table0, self.productsInfoAvailable)
        self.updateTable(self.table1, self.productsInfoNotAvailable)
        self.updateTable(self.table2, self.productsInfo)

        # Configurar tablas
        self.setupTables()

        # Limpiar campos
        self.clearLE(self.ciSearch)
        self.clearLE(self.productSearch)
        self.clearLE(self.productsRO0)
        self.clearLE(self.lotsRO0)

    def generalSetup(self):
        # Centrar posición de la ventana
        self.center()

        # Establecer tamaño y ocultar botones de la ventana
        self.setSize()

        # Configurar los spin box
        self.setupSpinLine(self.spinBox)
        self.add0.setAutoRepeat(True)
        self.substract0.setAutoRepeat(True)

        #self.setupLE()

    #-------------------------------------------------------------------------------------------------------------------------------
    # Configuración de los botones para cambio de página de los stacked:
    #-------------------------------------------------------------------------------------------------------------------------------

    # Cambio de página en MainStacked
    def on_home_pressed(self):
        self.setPage(self.MainStacked, 0)         # Cambiar a la página principal
        self.MainTitle.setText("Caja")

    def on_sales_pressed(self):
        self.setPage(self.MainStacked, 1)         # Cambiar a la página de ventas
        self.MainTitle.setText("Ventas")

    def on_inventory_pressed(self):
        self.setPage(self.MainStacked, 2)         # Cambiar a la página de inventario
        self.MainTitle.setText("Inventario")

    def on_querys_pressed(self):
        self.setPage(self.MainStacked, 3)         # Cambiar a la página de consultas
        self.MainTitle.setText("Consultas")

    def on_loans_pressed(self):
        self.setPage(self.MainStacked, 4)         # Cambiar a la página de préstamos
        self.MainTitle.setText("Préstamos")

    def on_books_pressed(self):
        self.setPage(self.MainStacked, 5)         # Cambiar a la página de libros
        self.MainTitle.setText("Libros")

    def on_providers_pressed(self):
        self.setPage(self.MainStacked, 6)         # Cambiar a la página de clientes
        self.MainTitle.setText("Proveedores")

    def on_clients_pressed(self):
        self.setPage(self.MainStacked, 7)         # Cambiar a la página de clientes
        self.MainTitle.setText("Clientes")

    def on_users_pressed(self):
        self.setPage(self.MainStacked, 8)         # Cambiar a la página de usuarios
        self.MainTitle.setText("Usuarios")

    def on_configure_pressed(self):
        self.setPage(self.MainStacked, 9)         # Cambiar a la página de configuraciones
        self.MainTitle.setText("Configuraciones")

    def on_help_pressed(self):
        self.setPage(self.MainStacked, 10)        # Cambiar a la página de ayuda
        self.MainTitle.setText("Ayuda")

    # Cambio de página en subStacked
    def on_arrow1_pressed(self): self.changePage(self.subStacked3)
    def on_arrow3_pressed(self): self.changePage(self.subStacked4)
    def on_arrow5_pressed(self): self.changePage(self.subStacked5)
    def on_arrow7_pressed(self): self.changePage(self.subStacked6)
    def on_arrow9_pressed(self): self.changePage(self.subStacked7)
    def on_arrow11_pressed(self): self.changePage(self.subStacked8)
    def on_arrow13_pressed(self): self.changePage(self.subStacked9)
    def on_arrow15_pressed(self): self.changePage(self.subStacked10)
    def on_arrow17_pressed(self): self.changePage(self.subStacked11)
    def on_arrow19_pressed(self): self.changePage(self.subStacked12)
    def on_arrow21_pressed(self): self.changePage(self.subStacked13)
    def on_arrow23_pressed(self): self.changePage(self.subStacked14)
    def on_arrow25_pressed(self): self.changePage(self.subStacked15)
    def on_arrow27_pressed(self): self.changePage(self.subStacked16)

    def on_arrow0_pressed(self): self.changePage(self.subStacked3, 1)
    def on_arrow2_pressed(self): self.changePage(self.subStacked4, 1)
    def on_arrow4_pressed(self): self.changePage(self.subStacked5, 1)
    def on_arrow6_pressed(self): self.changePage(self.subStacked6, 1)
    def on_arrow8_pressed(self): self.changePage(self.subStacked7, 1)
    def on_arrow10_pressed(self): self.changePage(self.subStacked8, 1)
    def on_arrow12_pressed(self): self.changePage(self.subStacked9, 1)
    def on_arrow14_pressed(self): self.changePage(self.subStacked10, 1)
    def on_arrow16_pressed(self): self.changePage(self.subStacked11, 1)
    def on_arrow18_pressed(self): self.changePage(self.subStacked12, 1)
    def on_arrow20_pressed(self): self.changePage(self.subStacked13, 1)
    def on_arrow22_pressed(self): self.changePage(self.subStacked14, 1)
    def on_arrow24_pressed(self): self.changePage(self.subStacked15, 1)
    def on_arrow26_pressed(self): self.changePage(self.subStacked16, 1)

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

    def on_theme0_pressed(self): self.setStyle(styles[1])
    def on_theme1_pressed(self): self.setStyle(styles[5])
    def on_theme2_pressed(self): self.setStyle(styles[3])
    def on_theme3_pressed(self): self.setStyle(styles[4])
    def on_theme4_pressed(self): self.setStyle(styles[6])
    def on_theme5_pressed(self): self.setStyle(styles[7])
    def on_theme6_pressed(self): self.setStyle(styles[2])
    def on_theme7_pressed(self): self.setStyle(styles[0])

    #-------------------------------------------------------------------------------------------------------------------------------
    # Configuración de botones del inventario
    #-------------------------------------------------------------------------------------------------------------------------------

    # Radio button para agregar nuevos productos
    def on_rbutton5_pressed(self):
        if self.click():
            self.clearLE(self.productsRO0)
            self.changeRO(self.productsRO1, listaLE1 = self.productsRO2)

    # Radio button para consultar productos
    def on_rbutton6_pressed(self):
        if self.click():
            self.clearLE(self.productsRO0)
            self.changeRO(self.productsRO1)

    # Radio button para editar productos
    def on_rbutton7_pressed(self):
        if self.click():
            self.clearLE(self.productsRO0)
            self.changeRO(self.productsRO1, listaLE1 = self.productsRO2)

    # Radio button para eliminar productos
    def on_rbutton8_pressed(self):
        if self.click():
            self.clearLE(self.productsRO0)
            self.changeRO(self.productsRO1)

    # Radio button para agregar nuevos lotes
    def on_rbutton9_pressed(self):
        if self.click():
            self.clearLE(self.lotsRO0)
            self.changeRO(self.lotsRO2, False, self.lotsRO3)

    # Radio button para consultar lotes
    def on_rbutton10_pressed(self):
        if self.click():
            self.clearLE(self.lotsRO0)
            self.changeRO(self.lotsRO1)

    # Radio button para editar lotes
    def on_rbutton11_pressed(self):
        if self.click():
            self.clearLE(self.lotsRO0)
            self.changeRO(self.lotsRO0, False)

    # Radio button para eliminar lotes
    def on_rbutton12_pressed(self):
        if self.click():
            self.clearLE(self.lotsRO0)
            self.changeRO(self.lotsRO1)

    # Boton "Aceptar" en el apartado de productos
    def on_pbutton11_pressed(self):
        if self.click():
            # Modalidad para agregar nuevos productos
            if self.rbutton5.isChecked():
                # Obtener información del nuevo producto
                productName = self.lineE26.text()
                productPrice = self.lineE27.text()
                productCategoy = self.lineE28.text()

                # Agregar el producto a la BD
                self.db.createProduct(productName, productPrice, productCategoy)

                # Refrescar toda la interfaz
                self.refresh()

                # Enfocar
                self.lineE26.setFocus()

            # Modalidad para consultar productos
            elif self.rbutton6.isChecked():
                productName = self.lineE26.text()
                product = self.db.getProductByNameOrID(productName)

                # Refrescar toda la interfaz
                self.refresh()

                # Enfocar
                self.lineE26.setFocus()

            # Modalidad para editar productos
            elif self.rbutton7.isChecked():
                productName = self.lineE26.text()
                productPrice = self.lineE27.text()
                productCategoy = self.lineE28.text()

                # Refrescar toda la interfaz
                self.refresh()

                # Enfocar
                self.lineE26.setFocus()

            # Modalidad para eliminar productos
            elif self.rbutton8.isChecked():

                # Refrescar toda la interfaz
                self.refresh()

                # Enfocar
                self.lineE26.setFocus()

    # Boton "Aceptar" en el apartado de lotes
    def on_pbutton13_pressed(self):
        if self.click():

            # Modalidad para agregar nuevos lotes
            if self.rbutton9.isChecked():
                # Obtener información del nuevo lote
                lotProduct = self.lineE33.text()
                lotProvider = self.lineE34.text()
                lotCost = self.lineE35.text()
                lotExpiration = self.lineE36.text()
                lotQuantity = self.lineE37.text()

                kwargs = {
                    "product_name" : lotProduct,
                    "provider_id"  : lotProvider,
                    "received_by"  : self.user,
                    "cost"         : lotCost,
                    "quantity"     : lotQuantity
                }

                # Agregar el lote a la BD
                if lotExpiration != "": kwargs["expiration_date"] = lotExpiration
                self.db.createLot(**kwargs)

                """product = self.db.getProductByNameOrID(lotProduct, onlyAvailables = False)[0]
                remaining = product[4] + int(lotQuantity)
                lots = product[5] + 1
                current = product[6]

                if current != 0: self.db.updateProduct(lotProduct, remaining=remaining, remainingLots=lots, available=True)
                else: self.db.updateProduct(lotProduct, remaining=remaining, remainingLots=lots, currentLot=0, available=True)"""

                self.refresh()               # Refrescar toda la interfaz
                self.lineE33.setFocus()      # Enfocar

            elif self.rbutton10.isChecked(): # Modalidad para consultar lotes
                self.refresh()               # Refrescar toda la interfaz
                self.lineE33.setFocus()      # Enfocar

            elif self.rbutton11.isChecked(): # Modalidad para editar lotes
                self.refresh()               # Refrescar toda la interfaz
                self.lineE33.setFocus()      # Enfocar

            elif self.rbutton12.isChecked(): # Modalidad para eliminar lotes
                self.refresh()               # Refrescar toda la interfaz
                self.lineE33.setFocus()      # Enfocar

    # Boton para ver/agregar imágen de un producto
    def on_selectedItem1_pressed(self):
        if self.click():
            filePath = QFileDialog.getOpenFileName(self, 'Seleccionar imágen', QDir.currentPath(), "Imágenes (*.bmp *.jpg *.jpeg *.png)")
            if filePath != "":
                self.selectedItem1.setIcon(QIcon(filePath))
                self.tempImage = filePath

    # LineEdit para ingresar nombres de los productos
    def on_lineE26_textChanged(self):
        if self.textChanged():
            if (self.rbutton6.isChecked() or self.rbutton8.isChecked() or self.rbutton7.isChecked()) and self.lineE26.text() != "":
                productName = self.lineE26.text()
                if productName in self.productsNames:
                    product = self.productsInfo[self.productsNames.index(productName)]
                    self.currentProduct = str(product[0]) # Product ID
                    self.lineE27.setText(str(product[2])) # Precio
                    self.lineE28.setText(product[5])      # Categoria
                    self.lineE29.setText(str(product[4])) # Lotes
                    self.lineE30.setText(str(product[3])) # Disp. Total


    #-------------------------------------------------------------------------------------------------------------------------------
    # Configuración de botones de ventas
    #-------------------------------------------------------------------------------------------------------------------------------

    # Botón para sumar al spinLine
    def on_add0_pressed(self):
        if self.click():
            count = int(self.spinLine0.text())
            if count < 9999999:
                self.spinLine0.setText(str(count+1))

    # Botón para restar al spinLine
    def on_substract0_pressed(self):
        if self.click():
            count = int(self.spinLine0.text())
            if count > 0:
                self.spinLine0.setText(str(count-1))

    #-------------------------------------------------------------------------------------------------------------------------------
    # Manejador de eventos de teclas presionadas
    #-------------------------------------------------------------------------------------------------------------------------------

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

####################################################################################################################################
## FIN :)
####################################################################################################################################
