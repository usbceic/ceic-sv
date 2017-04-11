#!/usr/bin/env python3
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

import gui_rc                   # Módulo que contiene los recursos de la interfaz
from PyQt4.uic import *         # Módulo con las herramientas parar tranajar los archivos .ui
from PyQt4.QtCore import *      # Módulo con procedimientos de Qt
from PyQt4.QtGui import *       # Módulo con estructuras de Qt
from DBManager import *         # Módulo manejador de la base de datos

####################################################################################################################################
## CONSTANTES:
####################################################################################################################################

# Paths
UIpath = "qt/ui/"
stylePath = "qt/stylesheet/"

# UI
MainUI = "material.ui"

# Styles
styles = ["black.css", "default.css", "fuchsia.css", "green.css", "orange.css", "purple.css", "red.css", "yellow.css"]

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

# Ejemplo de ista de cédulas de clientes
clientList = ["513264", "28436485", "32564336", "105746567", "280765423", "670124583"]

####################################################################################################################################
## MANEJADOR DE LA INTERFAZ GRÁFICA:
####################################################################################################################################

class sistema_window(QMainWindow, form_class, QWidget):
    #-------------------------------------------------------------------------------------------------------------------------------
    # Constructor de la clase
    #-------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, parent=None):
        #---------------------------------------------------------------------------------------------------------------------------
        # Iniciar y configurar la interfaz y la base de datos
        #---------------------------------------------------------------------------------------------------------------------------

        # Interfaz
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # Manejador de la base de datos
        self.DB = DBManager("sistema_ventas", "hola", True)

        #---------------------------------------------------------------------------------------------------------------------------
        # Listas necesarias para algunos métodos útiles
        #---------------------------------------------------------------------------------------------------------------------------

        # Parametros para buscar en la tabla de productos
        self.productsParams0 = ["name"]
        self.productsParams1 = ["name", "cost", "category"]

        # Listas de nombres de los productos
        self.productsNames = self.getProductList(self.productsParams0, 0)                     # Completa
        self.productsNamesAvailable = self.getProductList(self.productsParams0, 1)            # Disponibles
        self.productsNamesNotAvailable = self.getProductList(self.productsParams0, 2)         # No disponibles

        # Listas con información para las tablas de productos
        self.productsInfo = self.getProductList(self.productsParams1, 0)                     # Completa
        self.productsInfoAvailable = self.getProductList(self.productsParams1, 1)            # Disponibles
        self.productsInfoNotAvailable = self.getProductList(self.productsParams1, 2)         # No disponibles

        # Barras de búsqueda por cédula:
        self.ciSearch = [self.lineE17, self.lineE47, self.lineE52, self.lineE57]

        # Barras de búsqueda por nombre de producto:
        self.productSearch = [self.lineE23, self.lineE26, self.lineE33]

        # Apartado de productos en inventario
        self.productsRO0 = [self.lineE26, self.lineE27, self.lineE28, self.lineE29, self.lineE30, self.lineE31, self.lineE32]
        self.productsRO1 = [self.lineE27, self.lineE28, self.lineE29, self.lineE30, self.lineE31, self.lineE32]
        self.productsRO2 = [self.lineE27, self.lineE28, self.lineE29, self.lineE31, self.lineE32]
        self.productsRO3 = [self.lineE30]

        # Apartado de lotes en inventario
        self.lotsRO0 = [self.lineE34, self.lineE35, self.lineE36, self.lineE37, self.lineE38, self.lineE39]
        self.lotsRO1 = [self.lineE34, self.lineE35, self.lineE36, self.lineE37, self.lineE38, self.lineE39]
        self.lotsRO2 = [self.lineE34, self.lineE35, self.lineE36, self.lineE38, self.lineE39]
        self.lotsRO3 = [self.lineE37]

        # Tablas
        self.tables = [self.table0, self.table1, self.table2, self.table3, self.table4, self.table5, self.table6, self.table7,
                        self.table8, self.table9, self.table10, self.table11]

        #---------------------------------------------------------------------------------------------------------------------------
        # Cargar configuraciones iniciales
        #---------------------------------------------------------------------------------------------------------------------------

        #Configuración de la barra de búsqueda de cliente por CI
        self.setupSearchBar(self.ciSearch, clientList, True)

        # Configuración de las barras de búsqueda por nombre de producto
        self.setupSearchBar(self.productSearch, self.productsNames)

        # Se connectan los botones entre otras cosas con algunos de los métodos definidos a continuación
        QMetaObject.connectSlotsByName(self)

        # Variable de control para los QPushButton
        self.clicked = False

        # Configurar tablas
        self.setupTables()

        # Setup de las distintas tablas
        self.updateTable(self.table0, self.productsInfoAvailable)
        self.updateTable(self.table1, self.productsInfoNotAvailable)
        self.updateTable(self.table2, self.productsInfo)

    #-------------------------------------------------------------------------------------------------------------------------------
    # Métodos de la clase
    #-------------------------------------------------------------------------------------------------------------------------------

    # Definición de click sobre un QPushButton
    def click(self):
        if self.clicked:
            self.clicked = False
            return True
        else:
            self.clicked = True
            return False

    # Cambiar página de un QStackedWidget
    def setPage(self, stacked, index):
        if self.click(): stacked.setCurrentIndex(index)

    # Seleccionar un item de las listas Top 10 y Nuevo
    def selectItem(self, n):
        if self.click(): self.lineE23.setText(str(n))

    # Cambiar el tema de la interfáz
    def setStyle(self, name):
        if self.click(): self.setStyleSheet(getStyle(name))

    # Método para buscar en un LineEdit
    def setupSearchBar(self, listLE, itemsList, numValidator = False):
        LEmodel = QStringListModel()
        LEmodel.setStringList(itemsList)
        LEcompleter = QCompleter()
        LEcompleter.setModel(LEmodel)
        LEcompleter.setCaseSensitivity(Qt.CaseInsensitive)
        for lineE in listLE:
            if numValidator: lineE.setValidator(QIntValidator(0, 100000000))
            lineE.setCompleter(LEcompleter)

    # Obtener una lista con los nombres de todos los productos
    def getProductList(self, params, mode):
        productsList = self.DB.getItemInfo(productsTable, params, mode)
        if len(params) == 1:
            productsNames = []
            for i in range(len(productsList)):
                productsNames += productsList[i]
            return productsNames

        else: return productsList

    # Borrar contenido de uno o más LineEdit:
    def clearLE(self, listLE):
        for lineE in listLE: lineE.setText("")

    # Marcar en solo lectura uno o más LineEdit:
    def ReadOnlyLE(self, listLE, boolean):
        for lineE in listLE: lineE.setReadOnly(boolean)

    # Cambio de estado de los line edits en un apartado
    def changeRO(self, listaLE0, boolean = True, listaLE1 = []):
        if self.click():
            self.ReadOnlyLE(listaLE0, boolean)
            if len(listaLE1) != 0: self.ReadOnlyLE(listaLE1, not(boolean))

    def setupTables(self):
        for table in self.tables:
            table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)

    # Método para refrescar la tabla de canciones en la ventana
    def updateTable(self, table, itemsList):
        #for i in reversed(range(table.rowCount())): table.removeRow(i)

        #table.setRowCount(len(itemsList))
        for i in range(len(itemsList)):
            name = QTableWidgetItem(str(itemsList[i][0]))
            cost = QTableWidgetItem(str(itemsList[i][1]))
            category = QTableWidgetItem(str(itemsList[i][2]))
            table.setItem(i, 0, name)
            table.setItem(i, 1, cost)
            table.setItem(i, 2, category)

        self.elem_actual = 0
        if len(itemsList) > 0: table.selectRow(self.elem_actual)

    #-------------------------------------------------------------------------------------------------------------------------------
    # Configuración de los botones para cambio de página de los stacked:
    #-------------------------------------------------------------------------------------------------------------------------------

    def on_home_pressed(self): self.setPage(self.MainStacked, 0)
    def on_sales_pressed(self): self.setPage(self.MainStacked, 1)
    def on_inventory_pressed(self): self.setPage(self.MainStacked, 2)
    def on_querys_pressed(self): self.setPage(self.MainStacked, 3)
    def on_providers_pressed(self): self.setPage(self.MainStacked, 4)
    def on_clients_pressed(self): self.setPage(self.MainStacked, 5)
    def on_users_pressed(self): self.setPage(self.MainStacked, 6)
    def on_configure_pressed(self): self.setPage(self.MainStacked, 7)

    def on_arrow0_pressed(self): self.setPage(self.subStacked3, 1)
    def on_arrow1_pressed(self): self.setPage(self.subStacked3, 1)
    def on_arrow2_pressed(self): self.setPage(self.subStacked3, 0)
    def on_arrow3_pressed(self): self.setPage(self.subStacked3, 0)

    def on_arrow4_pressed(self): self.setPage(self.subStacked4, 1)
    def on_arrow5_pressed(self): self.setPage(self.subStacked4, 1)
    def on_arrow6_pressed(self): self.setPage(self.subStacked4, 0)
    def on_arrow7_pressed(self): self.setPage(self.subStacked4, 0)

    def on_arrow8_pressed(self): self.setPage(self.subStacked5, 2)
    def on_arrow9_pressed(self): self.setPage(self.subStacked5, 1)
    def on_arrow10_pressed(self): self.setPage(self.subStacked5, 0)
    def on_arrow11_pressed(self): self.setPage(self.subStacked5, 2)
    def on_arrow12_pressed(self): self.setPage(self.subStacked5, 1)
    def on_arrow13_pressed(self): self.setPage(self.subStacked5, 0)

    def on_arrow14_pressed(self): self.setPage(self.subStacked6, 1)
    def on_arrow15_pressed(self): self.setPage(self.subStacked6, 1)
    def on_arrow16_pressed(self): self.setPage(self.subStacked6, 0)
    def on_arrow17_pressed(self): self.setPage(self.subStacked6, 0)

    def on_arrow18_pressed(self): self.setPage(self.subStacked7, 3)
    def on_arrow19_pressed(self): self.setPage(self.subStacked7, 1)
    def on_arrow20_pressed(self): self.setPage(self.subStacked7, 0)
    def on_arrow21_pressed(self): self.setPage(self.subStacked7, 2)
    def on_arrow22_pressed(self): self.setPage(self.subStacked7, 1)
    def on_arrow23_pressed(self): self.setPage(self.subStacked7, 3)
    def on_arrow24_pressed(self): self.setPage(self.subStacked7, 2)
    def on_arrow25_pressed(self): self.setPage(self.subStacked7, 0)

    def on_arrow26_pressed(self): self.setPage(self.subStacked8, 2)
    def on_arrow27_pressed(self): self.setPage(self.subStacked8, 1)
    def on_arrow28_pressed(self): self.setPage(self.subStacked8, 0)
    def on_arrow29_pressed(self): self.setPage(self.subStacked8, 2)
    def on_arrow30_pressed(self): self.setPage(self.subStacked8, 1)
    def on_arrow31_pressed(self): self.setPage(self.subStacked8, 0)

    def on_arrow32_pressed(self): self.setPage(self.subStacked9, 1)
    def on_arrow33_pressed(self): self.setPage(self.subStacked9, 1)
    def on_arrow34_pressed(self): self.setPage(self.subStacked9, 0)
    def on_arrow35_pressed(self): self.setPage(self.subStacked9, 0)

    def on_arrow36_pressed(self): self.setPage(self.subStacked10, 2)
    def on_arrow37_pressed(self): self.setPage(self.subStacked10, 1)
    def on_arrow38_pressed(self): self.setPage(self.subStacked10, 0)
    def on_arrow39_pressed(self): self.setPage(self.subStacked10, 2)
    def on_arrow40_pressed(self): self.setPage(self.subStacked10, 1)
    def on_arrow41_pressed(self): self.setPage(self.subStacked10, 0)

    def on_arrow42_pressed(self): self.setPage(self.subStacked11, 2)
    def on_arrow43_pressed(self): self.setPage(self.subStacked11, 1)
    def on_arrow44_pressed(self): self.setPage(self.subStacked11, 0)
    def on_arrow45_pressed(self): self.setPage(self.subStacked11, 2)
    def on_arrow46_pressed(self): self.setPage(self.subStacked11, 1)
    def on_arrow47_pressed(self): self.setPage(self.subStacked11, 0)

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

    def on_blackGUI_pressed(self): self.setStyle(styles[0])
    def on_blueGUI_pressed(self): self.setStyle(styles[1])
    def on_fuchsiaGUI_pressed(self): self.setStyle(styles[2])
    def on_greenGUI_pressed(self): self.setStyle(styles[3])
    def on_orangeGUI_pressed(self): self.setStyle(styles[4])
    def on_purpleGUI_pressed(self): self.setStyle(styles[5])
    def on_redGUI_pressed(self): self.setStyle(styles[6])
    def on_yellowGUI_pressed(self): self.setStyle(styles[7])

    #-------------------------------------------------------------------------------------------------------------------------------
    # Configuración de botones del inventario
    #-------------------------------------------------------------------------------------------------------------------------------

    # Radio button para agregar nuevos productos
    def on_rbutton5_pressed(self): self.changeRO(self.productsRO1, False)

    # Radio button para consultar productos
    def on_rbutton6_pressed(self): self.changeRO(self.productsRO1)

    # Radio button para editar productos
    def on_rbutton7_pressed(self): self.changeRO(self.productsRO2, False, self.productsRO3)

    # Radio button para eliminar productos
    def on_rbutton8_pressed(self): self.changeRO(self.productsRO1)

    # Boton "Aceptar" en el apartado de productos
    def on_pbutton11_pressed(self):
        if self.click():
            if self.rbutton5.isChecked():
                name = self.lineE26.text()
                cost = self.lineE27.text()
                category = self.lineE28.text()
                self.DB.createProduct(name, cost)
                self.setupProductsSearchs()
                self.clearLE(self.productsRO0)

    # Boton "Aceptar" en el apartado de lotes
    def on_pbutton13_pressed(self):
        if self.click():
            if self.rbutton9.isChecked():
                productID = self.lineE26.text()
                cost = self.lineE27.text()
                self.DB.createLot(productID, cost)
                self.clearLE(self.productsRO0)

####################################################################################################################################
## FIN :)
####################################################################################################################################
