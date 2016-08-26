#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

####################################################################################################################################
## DESCRIPCIÓN:
####################################################################################################################################

# Modúlo con la implementación de la clase encargada del manejo de la base de datos.

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

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

####################################################################################################################################
## CONSTANTES:
####################################################################################################################################

#-----------------------------------------------------------------------------------------------------------------------------------
# Tablas
#-----------------------------------------------------------------------------------------------------------------------------------

# Nombre de la tabla de productos
productsTable = "products"

# Columnas de la tabla de productos
productsColumns = """productID SERIAL PRIMARY KEY,
                    name text,
                    cost numeric,
                    category text,
                    remaining integer DEFAULT 0,
                    remainingLots integer DEFAULT 0,
                    available boolean DEFAULT false"""

# Nombre de la tabla de lotes
lotsTable = "lots"

# Columnas de la tabla de lotes
lotsColumns = """lotID SERIAL PRIMARY KEY,
                productID integer,
                adquisition date,
                category text,
                cost numeric,
                expiration date,
                provider text,
                quantity integer DEFAULT 0,
                available boolean DEFAULT false"""

####################################################################################################################################
## MANEJADOR DE LA BASE DE DATOS:
####################################################################################################################################

class DBManager:
    #-------------------------------------------------------------------------------------------------------------------------------
    # Constructor de la clase
    #-------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, userName, password, firstInit=False):
        # Conexion actual
        self._con = connect(dbname = 'ceicsv', user = userName, password = password, host = 'localhost')
        self._con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # Pipe para enviar comandos sql
        self._cur = self._con.cursor()

        # Modalidad de primer inicio del programa
        if firstInit:
            self.createTable(productsTable, productsColumns)    # Tabla que registra cada producto diferente en el inventario
            self.createTable(lotsTable, lotsColumns)            # Tabla que registra cada lote adquirido

            # Pruebas de correctitud (Borrar luego)
            self.createProduct("Dona", 499.99)
            self.createProduct("Pizza", 699.99)
            #print(self.getProducts(onlyAvailables = False))
            #print(self.getProductByNameOrID(productID = 1, onlyAvailables = False))
            #print(self.getItemInfo(productsTable, ["name"]))


    #-------------------------------------------------------------------------------------------------------------------------------
    # Destructor de la clase
    #-------------------------------------------------------------------------------------------------------------------------------

    def __del__(self):
        if self._con is not None and self._cur is not None:
            try:
                self.closeDB()
                print("Se ha cerrado correctamente la base de datos")
            except:
                print("La base de datos ya está cerrada")
        else:
            print("La base de datos ya está cerrada")

    #-------------------------------------------------------------------------------------------------------------------------------
    # Métodos de control de la base de datos
    #-------------------------------------------------------------------------------------------------------------------------------

    # Cierra sesion en la base de datos
    def closeDB(self):
        self._cur.close() # Cerrar el pipe
        self._con.close() # Cerrar la connexion

    # Crear una tabla en la base de datos
    def createTable(self, table, columns):
        action = "CREATE TABLE " + table + "(" + columns + ")"

        # Se intenta crear una tabla nueva
        try:
            self._cur.execute(action)
            print("Se ha creado la tabla " + table + " correctamente.")

        # Si no se puedo posiblemente ya existe
        except:
            print("La tabla " + table + " ya existe, se intentará eliminar y crear una nueva")
            # Se elimina
            self.dropTable(table)

            # Se intenta crear de nuevo
            try:
                self._cur.execute(action)
                print("Se ha creado la tabla " + table + " correctamente.")

            # Si no se puede hay algún error grabe en la base de datos
            except: print("ERROR: No se pudo crear la tabla " + table)

    # Eliminar una tabla en la base de datos
    def dropTable(self, table):
        print("Eliminando tabla: " + table)
        self._cur.execute("DROP TABLE " + table)

    # Obtener informacion personalizada de una tabla (Recomendado para productos y lotes)
    def getItemInfo(self, table, params = [], mode = 0):
        action = "SELECT "
        if len(params) == 0: action += "*"
        else:
            for i in range(len(params)):
                if i > 0: action += ", "
                action += params[i]
        action += " FROM " + table
        if mode == 1: action += " WHERE available = true"
        if mode == 2: action += " WHERE available = false"
        self._cur.execute(action)
        return self._cur.fetchall()

    #-------------------------------------------------------------------------------------------------------------------------------
    # Métodos de control de los productos (INVENTARIO)
    #-------------------------------------------------------------------------------------------------------------------------------

    # Crear producto
    def createProduct(self, name, cost, category):
        self._cur.execute("INSERT INTO products(name, cost, category) VALUES (\'" + name +"\',\'" + str(cost)+ "\',\'" category +"\')")

    # Buscar producto por nombre o por el productID
    def getProductByNameOrID(self, name = None, productID = None, caseInsensitive = False, onlyAvailables = True):
        action = """SELECT * FROM products WHERE"""

        if productID is None and name is None: return []
        if onlyAvailables: action = action + " available = true AND ("
        if productID is not None: action = action + " productID = %d" %productID
        if name is not None:
            if productID is not None: action = action + " OR"
            action = action + " name SIMILAR TO '%{}%'".format(name)
            if caseInsensitive: action = action + " OR LOWER(name) SIMILAR TO '%{}%'".format(name.lower())
        if onlyAvailables: action = action + " )"

        self._cur.execute(action)
        return self._cur.fetchall()

    # Actualizar información de un producto
    def updateProduct(self, productID, name = None, cost = None, available = None):
        if name is None and cost is None and available is None: return

        action = "UPDATE products SET"
        if name is not None: action = action + " name = '{}'".format(name)
        if cost is not None:
            if name is not None: action = action + ","
            action = action + " cost = " + str(cost)
        if available is not None:
            if name is not None or cost is not None: action = action + ","
            action = action + " available = " + str(available)

        action = action + " WHERE productID = %d" %productID
        self._cur.execute(action)

    # Eliminar un producto
    def deleteProduct(self, productID):
        print("Eliminando producto: " + str(productID))
        action = "DELETE FROM products WHERE productID = " + str(productID)
        self._cur.execute(action)

    #-------------------------------------------------------------------------------------------------------------------------------
    # Métodos de control de los lotes de productos (INVENTARIO)
    #-------------------------------------------------------------------------------------------------------------------------------

    # Crear producto
    def createLot(self, productID, cost):
        self._cur.execute("INSERT INTO products(productID, cost) VALUES (\'" + int(productID) +"\',\'" + str(cost)+ "\')" )

    # Obtener el productID y el nombre de los productos
    def getLots(self, onlyAvailables = True):
        if onlyAvailables: self._cur.execute("SELECT productID, cost FROM lots WHERE available = true")
        else: self._cur.execute("SELECT productID, cost FROM lots")
        return self._cur.fetchall()

####################################################################################################################################
## FIN :)
####################################################################################################################################


