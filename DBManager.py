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
            self.createTableProducts()

            # Pruebas de correctitud (Borrar luego)
            self.createProduct("hola", 10.85)
            self.createProduct("pedro", 10.85)
            self.createProduct("Dos Partes", 10.85)
            self.createProduct("Tres Partes :D", 10.85)

            print (self.getProduct(onlyAvailables = False))
            print (self.getProductInfo(onlyAvailables = False))
            print (self.getProductByNameOrID(productID = 2, onlyAvailables = False))
            print (self.getProductByNameOrID(name = "Dos", onlyAvailables = False))
            print (self.getProductByNameOrID(name = "Partes", onlyAvailables = False))
            print (self.getProductByNameOrID(name = " ", onlyAvailables = False))
            print (self.getProductByNameOrID(name = "Dos Partes", onlyAvailables = False))
            print (self.getProductByNameOrID(name = "partes", onlyAvailables = False))
            print (self.getProductByNameOrID(name = "partes", caseInsensitive= True, onlyAvailables = False))

            print("")
            print (self.getProductByNameOrID(productID = 2, onlyAvailables = False))
            self.updateProduct(2, "Juan", 1000.1, True)
            print (self.getProductByNameOrID(productID = 2))

            print("")
            print (self.getProductByNameOrID(productID = 4, onlyAvailables = False))
            self.deleteProduct(4)
            print (self.getProductByNameOrID(productID = 4, onlyAvailables = False))

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

    # Cierra Sesion de Bases de Datos
    def closeDB(self):
        self._cur.close() # Cerrar el pipe
        self._con.close() # Cerrar la connexion

    #-------------------------------------------------------------------------------------------------------------------------------
    # Métodos de control del inventario
    #-------------------------------------------------------------------------------------------------------------------------------

    # Crear tabla de products
    def createTableProducts(self):
        action = """CREATE TABLE products (
                    category text,
                    cost numeric,
                    expiration date,
                    lotID integer,
                    name text,
                    productID SERIAL PRIMARY KEY,
                    remaining integer DEFAULT 0,
                    remainingLots integer DEFAULT 0,
                    available boolean DEFAULT false
        )"""

        # Cuidado si no se quiere dropear la tabla si ya existe
        try:
            self._cur.execute(action)
        except:
            print("Tabla ya existente, se intentará eliminar y crear una nueva")
            self.dropTableProducts()
            try:
                self._cur.execute(action)
            except:
                print("ERROR: No se pudo crear la tabla")

    # Eliminar tabla de products
    def dropTableProducts(self):
        print("Eliminando tabla: products")
        self._cur.execute("DROP TABLE products")

    # Crear producto
    def createProduct(self, name, cost):
        self._cur.execute("INSERT INTO products(name, cost) VALUES (\'" + name +"\',\'" + str(cost)+ "\')" )

    # Obtener el productID y el nombre de los productos
    def getProduct(self, onlyAvailables = True):
        if onlyAvailables: self._cur.execute("SELECT productID, name FROM products WHERE available = true")
        else: self._cur.execute("SELECT productID, name FROM products")
        return self._cur.fetchall()

    # Obtener toda la información de los productos
    def getProductInfo(self, onlyAvailables = True):
        if onlyAvailables: self._cur.execute("SELECT * FROM products WHERE available = true")
        else: self._cur.execute("SELECT * FROM products")
        return self._cur.fetchall()

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

####################################################################################################################################
## FIN :)
####################################################################################################################################
