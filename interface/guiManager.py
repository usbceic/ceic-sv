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
## MODÚLOS:
###################################################################################################################################################################################

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
from PyQt4.QtGui import QMainWindow, QApplication, QStringListModel, QCompleter, QIntValidator, QHeaderView, QTableWidgetItem, QFileDialog, QIcon

# Módulo manejador de la base de datos
from db_manager import dbManager

###################################################################################################################################################################################
## CONSTANTES:
###################################################################################################################################################################################

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

###################################################################################################################################################################################
## PROCEDIMIENTOS:
###################################################################################################################################################################################

# Devuelve un string con el stylesheet especificado por el parametro name
def getStyle(name):
    file = open(stylePath+name, "r")
    style = file.read()
    file.close()
    return style

###################################################################################################################################################################################
## MANEJADOR DE LA INTERFAZ GRÁFICA:
###################################################################################################################################################################################

# Manejador de la interfaz del administrador
class adminGUI(QMainWindow, form_class):
    closed = pyqtSignal() # Señal para saber si se cerró la ventana

    #==============================================================================================================================================================================
    # Constructor de la clase
    #==============================================================================================================================================================================
    def __init__(self, user, database, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Iniciar y configurar la interfaz y la base de datos
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        super(adminGUI, self).__init__(parent)  # Construcción de la instancia
        self.setupUi(self)                      # Configuración de la plantilla
        self.user = user                        # Asignación del usuario que ejecuta la sesión
        self.db = database                      # Asignación del manejador de la base de datos

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Constantes para fácilitar el uso de varios métodos de la clase
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

        self.clicked = False                # QPushbutton presionado
        self.writing = False                # Texto de un QLineEdit cambiado
        self.currentProduct = None          # Instancia de producto en uso
        self.tempImage = ""                 # Imagen seleccionada
        self.selectedProductRemaining = {}  # Diccionario de cotas superiores para el spinBox de ventas
        self.selectedProductName = ""       # Nombre del producto seleccionado actualmente en la vista de ventas
        self.selectedProducts = {}          # Diccionario de productos en la factura en la vista de ventas

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS DE PROPOSITO GENERAL
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Barras de búsqueda por cédula:
        self.clientsSearch = [self.lineE17, self.lineE47, self.lineE52, self.lineE57]

        # Barras de búsqueda por nombre de producto:
        self.productSearch = [self.lineE23, self.lineE26, self.lineE33]

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

        # Apartado de lotes en inventario
        self.lotsRO0 = [self.lineE33, self.lineE34, self.lineE35, self.lineE36, self.lineE37, self.lineE38]
        self.lotsRO1 = [self.lineE34, self.lineE35, self.lineE36, self.lineE37, self.lineE38]
        self.lotsRO2 = [self.lineE34, self.lineE35, self.lineE36, self.lineE37]
        self.lotsRO3 = [self.lineE38]

        # Tablas de productos
        self.productTables = [self.table1, self.table2, self.table3]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE PROVEEDORES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de proveedores
        self.providersSearch = [self.lineE149, self.lineE34]

        # Apartado de proveedores
        self.providersLE0 = [self.lineE146, self.lineE147, self.lineE148]
        self.providersLE1 = [self.lineE149, self.lineE150, self.lineE151]
        self.providersTE0 = [self.textE1, self.textE2]
        self.providersTE1 = [self.textE3, self.textE4]

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # LISTAS PARA LA VISTA DE CLIENTES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Apartado de clientes
        self.clientsLE0 = [self.lineE47, self.lineE48, self.lineE49, self.lineE50, self.lineE51]
        self.clientsLE1 = [self.lineE52, self.lineE53, self.lineE54, self.lineE55, self.lineE56]
        self.clientsLE2 = [self.lineE57, self.lineE58, self.lineE59, self.lineE60, self.lineE61]

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

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Cargar configuraciones iniciales
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Se connectan los botones entre otras cosas con algunos de los métodos definidos a continuación
        QMetaObject.connectSlotsByName(self)

        # Aplicar configuraciones generales de la interfaz
        self.generalSetup()

        # Refrescar todos los elementos de la interfaz
        self.refresh()

        # Se establece la pagina de caja por defecto
        self.MainStacked.setCurrentIndex(0)
        self.MainTitle.setText("Caja")

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

    # Cambiar página de un QStackedWidget
    def setPage(self, stacked, index):
        if self.click(): stacked.setCurrentIndex(index)

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
        self.setStyleSheet(getStyle(styles[1]))

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
        self.refreshClients()

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
        self.setPage(self.MainStacked, 0)
        self.MainTitle.setText("Caja")

     # Cambiar a la página de ventas
    def on_sales_pressed(self):
        self.setPage(self.MainStacked, 1)
        self.MainTitle.setText("Ventas")

    # Cambiar a la página de inventario
    def on_inventory_pressed(self):
        self.setPage(self.MainStacked, 2)
        self.MainTitle.setText("Inventario")

    # Cambiar a la página de consultas
    def on_querys_pressed(self):
        self.setPage(self.MainStacked, 3)
        self.MainTitle.setText("Consultas")

    # Cambiar a la página de préstamos
    def on_loans_pressed(self):
        self.setPage(self.MainStacked, 4)
        self.MainTitle.setText("Préstamos")

    # Cambiar a la página de libros
    def on_books_pressed(self):
        self.setPage(self.MainStacked, 5)
        self.MainTitle.setText("Libros")

    # Cambiar a la página de clientes
    def on_providers_pressed(self):
        self.setPage(self.MainStacked, 6)
        self.MainTitle.setText("Proveedores")

    # Cambiar a la página de clientes
    def on_clients_pressed(self):
        self.setPage(self.MainStacked, 7)
        self.MainTitle.setText("Clientes")

    # Cambiar a la página de usuarios
    def on_users_pressed(self):
        self.setPage(self.MainStacked, 8)
        self.MainTitle.setText("Usuarios")

    # Cambiar a la página de configuraciones
    def on_configure_pressed(self):
        self.setPage(self.MainStacked, 9)
        self.MainTitle.setText("Configuraciones")

    # Cambiar a la página de ayuda
    def on_help_pressed(self):
        self.setPage(self.MainStacked, 10)
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

    #==============================================================================================================================================================================
    # VISTA DE INVENTARIO
    #==============================================================================================================================================================================
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para refrescar la vista del Inventario y elementos relacionados
    def refreshInventory(self):
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
        self.clearLEs(self.productsRO0)
        self.clearLEs(self.lotsRO0)

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
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1, listaLE1 = self.productsRO2)

    # Radio button para consultar productos
    def on_rbutton6_pressed(self):
        if self.click():
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1)

    # Radio button para editar productos
    def on_rbutton7_pressed(self):
        if self.click():
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1, listaLE1 = self.productsRO2)

    # Radio button para eliminar productos
    def on_rbutton8_pressed(self):
        if self.click():
            self.clearLEs(self.productsRO0)
            self.changeRO(self.productsRO1)

    # Radio button para agregar nuevos lotes
    def on_rbutton9_pressed(self):
        if self.click():
            self.clearLEs(self.lotsRO0)
            self.changeRO(self.lotsRO2, False, self.lotsRO3)

    # Radio button para consultar lotes
    def on_rbutton10_pressed(self):
        if self.click():
            self.clearLEs(self.lotsRO0)
            self.changeRO(self.lotsRO1)

    # Radio button para editar lotes
    def on_rbutton11_pressed(self):
        if self.click():
            self.clearLEs(self.lotsRO0)
            self.changeRO(self.lotsRO0, False)

    # Radio button para eliminar lotes
    def on_rbutton12_pressed(self):
        if self.click():
            self.clearLEs(self.lotsRO0)
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
                self.refreshInventory()

                # Enfocar
                self.lineE26.setFocus()

            # Modalidad para consultar productos
            elif self.rbutton6.isChecked():
                productName = self.lineE26.text()
                product = self.db.getProductByNameOrID(productName)

                # Refrescar toda la interfaz
                self.refreshInventory()

                # Enfocar
                self.lineE26.setFocus()

            # Modalidad para editar productos
            elif self.rbutton7.isChecked():
                productName = self.lineE26.text()
                productPrice = self.lineE27.text()
                productCategoy = self.lineE28.text()

                # Refrescar toda la interfaz
                self.refreshInventory()

                # Enfocar
                self.lineE26.setFocus()

            # Modalidad para eliminar productos
            elif self.rbutton8.isChecked():

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
                expiration_date = self.lineE36.text()
                quantity = self.lineE37.text()

                # Verificar completitud de los campos obligatorios
                if (product_name and provider_name and cost and quantity) != "":

                    kwargs = {
                        "product_name" : product_name,
                        "provider_name"  : provider_name,
                        "received_by"  : self.user,
                        "cost"         : int(cost),
                        "quantity"     : quantity
                    }

                    if expiration_date != "": kwargs["expiration_date"] = expiration_date

                    # Agregar el lote a la BD
                    self.db.createLot(**kwargs)

                    self.refreshInventory()               # Refrescar toda la interfaz
                    self.lineE33.setFocus()      # Enfocar

            elif self.rbutton10.isChecked(): # Modalidad para consultar lotes
                self.refreshInventory()               # Refrescar toda la interfaz
                self.lineE33.setFocus()      # Enfocar

            elif self.rbutton11.isChecked(): # Modalidad para editar lotes
                self.refreshInventory()               # Refrescar toda la interfaz
                self.lineE33.setFocus()      # Enfocar

            elif self.rbutton12.isChecked(): # Modalidad para eliminar lotes
                self.refreshInventory()               # Refrescar toda la interfaz
                self.lineE33.setFocus()      # Enfocar

    # Boton para ver/agregar imágen de un producto
    def on_selectedItem1_pressed(self):
        if self.click():
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
            if (self.rbutton6.isChecked() or self.rbutton8.isChecked() or self.rbutton7.isChecked()) and self.lineE26.text() != "":
                productName = self.lineE26.text()
                if productName in self.productsNames:
                    product = self.productsInfo[self.productsNames.index(productName)]
                    self.currentProduct = str(product[0]) # Product ID
                    self.lineE27.setText(str(product[2])) # Precio
                    self.lineE28.setText(product[5])      # Categoria
                    self.lineE29.setText(str(product[4])) # Lotes
                    self.lineE30.setText(str(product[3])) # Disp. Total

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

        # Refrescar el inventario
        self.refreshInventory()

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
            total += float(itemsList[i][3])                             # Sumar subtotal al total

        self.lineE21.setText(str(total))                          # Actualizar el lineEdit del total
        self.elem_actual = 0                                      # Definir la fila que se seleccionará
        if len(itemsList) > 0: table.selectRow(self.elem_actual)  # Seleccionar fila
        table.resizeColumnsToContents()                           # Redimensionar columnas segun el contenido

    # Seleccionar un item de las listas Top 10 y Nuevo
    def selectItem(self, n):
        if self.click(): self.lineE23.setText(str(n))

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

    # Botón para sumar al spinLine
    def on_add0_pressed(self):
        if self.click():
            count = int(self.spinLine0.text())
            if self.selectedProductName in self.selectedProductRemaining:
                if count < self.selectedProductRemaining[self.selectedProductName]:
                    self.spinLine0.setText(str(count+1))
                    self.lineE25.setText(str(((count+1)*float(self.lineE24.text()))))

    # Botón para restar al spinLine
    def on_substract0_pressed(self):
        if self.click():
            count = int(self.spinLine0.text())
            if count > 0:
                self.spinLine0.setText(str(count-1))
                self.lineE25.setText(str(((count-1)*float(self.lineE24.text()))))

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
            if self.db.existProduct(name):

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
                # limpiar Imagen                                    # Cargar imagen por defecto

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CAMPOS DE TEXTO
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # LineEdit para ingresar la cédula del cliente
    def on_lineE17_textChanged(self):
        if self.textChanged():
            if self.lineE17.text() != "":
                ci = int(self.lineE17.text())
                if self.db.existClient(ci):
                    client = self.db.getClient(ci)[0]                            # Obtener cliente
                    self.lineE18.setText(client.firstname)                       # Establecer Nombre
                    self.lineE19.setText(client.lastname)                        # Establecer Apellido
                    self.lineE20.setText(str(client.balance))                    # Establecer Saldo
                    self.lineE152.setValidator(QIntValidator(0, client.balance)) # Establecer limite de saldo para pagar

                else:
                    self.clearLEs(self.salesClientLE0)              # Limpiar lineEdits del apartado
                    self.lineE152.setValidator(QIntValidator(0, 0)) # Establecer limite de saldo para pagar

    # LineEdit para ingresar el monto a pagar en efectivo
    def on_lineE21_textChanged(self):
        if self.textChanged():
            print("Irga si se activa")
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
                            balance = self.db.getClient(ci)[0].balance

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
                            balance = self.db.getClient(ci)[0].balance

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
            name = self.lineE23.text()
            if self.db.existProduct(name, available=True):
                product = self.db.getProductByNameOrID(name)[0]                         # Obtener cliente
                self.lineE24.setText(str(product.price))                                # Establecer Nombre
                self.selectedProductName = name

                if name not in self.selectedProducts:
                    self.selectedProductRemaining[name] = product.remaining

                # cargar imagen
            else:
                self.clearLEs(self.selectedProductLE0)
                self.clearSpinLine(self.spinLine0)

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
        self.clearLEs(self.clientsLE2)

        # Refrescar tabla
        self.updateClientsTable()

    # Método para refrescar la tabla de factura en ventas
    def updateClientsTable(self):
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
            if self.lineE53.text() != "" and self.lineE54.text() != "" and self.lineE55.text() != "":
                kwargs = {
                    "ci"        : self.lineE52.text(),
                    "firstname" : self.lineE53.text(),
                    "lastname"  : self.lineE54.text(),
                    "phone"     : self.lineE55.text(),
                    "email"     : self.lineE56.text()
                }
                self.db.createClient(**kwargs)

                self.clearLEs(self.clientsLE1) # Limpiar formulario
                                               # Actualizar tabla
                                               # Actualizar autocompletado
                self.lineE53.setFocus()        # Enfocar

    #==============================================================================================================================================================================
    # VISTA DE CONFIGURACIONES
    #==============================================================================================================================================================================

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Cambiar el tema de la interfáz
    def setStyle(self, name):
        if self.click(): self.setStyleSheet(getStyle(name))

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def on_theme0_pressed(self): self.setStyle(styles[1])
    def on_theme1_pressed(self): self.setStyle(styles[5])
    def on_theme2_pressed(self): self.setStyle(styles[3])
    def on_theme3_pressed(self): self.setStyle(styles[4])
    def on_theme4_pressed(self): self.setStyle(styles[6])
    def on_theme5_pressed(self): self.setStyle(styles[7])
    def on_theme6_pressed(self): self.setStyle(styles[2])
    def on_theme7_pressed(self): self.setStyle(styles[0])

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
        self.closed.emit()  # Emitir señal para que la ventana de inicio aparezca
        event.accept()      # Aceptar el evento y cerrar la ventana

###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################
