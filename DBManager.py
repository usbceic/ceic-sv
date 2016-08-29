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

import datetime
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
                    price numeric,
                    category text,
                    remaining integer DEFAULT 0,
                    remainingLots integer DEFAULT 0,
                    currentLot integer DEFAULT 0,
                    available boolean DEFAULT false"""

# Nombre de la tabla de lotes General, para especifica de producto ver lots_ID
lotsTable = "lots_"

# Columnas de la tabla de lotes especificos de un producto
lotsColumns = """lotID SERIAL PRIMARY KEY,
				cost numeric,
				quantity integer,
				category text,
                adquisition date DEFAULT now(),                
                provider text, 
                perishable boolean DEFAULT false,
                expiration date,               
                available boolean DEFAULT false"""

loginTable = "login"

loginColumns = """username text CONSTRAINT must_be_different UNIQUE,
				password text NOT NULL"""
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
            self.createTable(loginTable, loginColumns)

            #Pruebas de Usuario
            self.createUser("Hola","hola")
            print(self.checkUser("Hola", "a"))
            print(self.checkUser("Hola", "hola"))

            # Pruebas de correctitud (Borrar luego)
            self.createProduct("Dona", 499.99)
            self.createProduct("Pizza", 699.99)
            self.createProduct("Memes", 100000000)
            print(self.getProductByNameOrID(productID = 1, onlyAvailables = False))
            self.deleteProduct(1)
            print(self.getProductByNameOrID(productID = 1, onlyAvailables = False))
            self.createLot(2, 10.5, 50, adquisitionDate=datetime.datetime.now().date().isoformat())
            self.createLot(2, 1.5, 5, adquisitionDate=datetime.date(1998, 8,15).isoformat())
            print(self.getProductByNameOrID(productID = 2, onlyAvailables = False))
            print(self.getLots(False))
            self.updateLot(2, 2, quantity=100, available=True)
            print(self.getLots(False))
            print(self.getProductByNameOrID(productID = 2, onlyAvailables = False))
            #self.updateLot(2, 2, available=False)
            self.deleteLot(2, 2)
            print(self.getProductByNameOrID(productID = 2, onlyAvailables = False))
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
    def createProduct(self, name, price, category = ""):
    	# Crear row de producto en tabla prodructs
        self._cur.execute("INSERT INTO products(name, price, category) VALUES (%s,%s,%s) RETURNING productID",(name, price, category))
        # Crear la tabla lots_(serial de producto) para guardar los lotes relacionados a producto
        self.createTable(lotsTable+str(self._cur.fetchall()[0][0]), lotsColumns)

    # Buscar producto por nombre o por el productID
    def getProductByNameOrID(self, name = None, productID = None, caseInsensitive = False, onlyAvailables = True):
        action = """SELECT * FROM products WHERE"""
        kwargs = ()

        if productID is None and name is None: return []

        if onlyAvailables: action = action + " available = true AND ("

        if productID is not None: 
        	action = action + " productID = %s"
        	kwargs = kwargs + (productID,)

        if name is not None:
            if productID is not None: action = action + " OR"
            action = action + " name SIMILAR TO %s"
            kwargs = kwargs + (name,)
            if caseInsensitive: 
            	action = action + " OR LOWER(name) SIMILAR TO %s"
            	kwargs = kwargs + (name.lower(),)

        if onlyAvailables: action = action + " )"

        self._cur.execute(action, kwargs)
        return self._cur.fetchall()

    # Actualizar información de un producto
    def updateProduct(self, productID, name = None, price = None, currentLot =None, available = None):
        if name is None and price is None and available is None: return

        kwargs = ()
        action = "UPDATE products SET"

        if name is not None: 
        	action = action + " name = %s"
        	kwargs = kwargs + (name,)

        if price is not None:
            if name is not None: action = action + ","
            action = action + " price = %s"
            kwargs = kwargs + (price,)

        if currentLot is not None:
        	if name is not None or price is not None: action = action + ","
        	action = action + " currentLot = %s"
        	kwargs = kwargs + (currentLot,)

        if available is not None:
            if name is not None or price is not None or currentLot is not None: action = action + ","
            action = action + " available = %s"
            kwargs = kwargs + (available,)

        action = action + " WHERE productID = %s"
        kwargs = kwargs + (productID,)
        self._cur.execute(action,kwargs)

    # Eliminar un producto
    def deleteProduct(self, productID):
        print("Eliminando producto: " + str(productID))
        try:
        	print("Eliminando la tabla de lotes relacionada con producto: " + str(productID))
        	self.dropTable(lotsTable+str(productID))
        except:
        	print("Tabla no existia o ID de producto invalido")
        action = "DELETE FROM products WHERE productID = %s"
        kwargs = (productID,)
        self._cur.execute(action,kwargs)

    #-------------------------------------------------------------------------------------------------------------------------------
    # Métodos de control de los lotes de productos (INVENTARIO)
    #-------------------------------------------------------------------------------------------------------------------------------

    # Crear Lote
    def createLot(self, productID, cost, quantity, category = "", provider="", adquisitionDate=None, expirationDate=None):
    	if quantity == 0:
    		print("Error, no se pueden añadir lotes vacios")
    		return

    	kwargs = (cost, quantity, category, provider)
    	action = "INSERT INTO " + lotsTable + str(productID) + "(cost, quantity, category, provider"
    	
    	if adquisitionDate is not None:
    		action = action + ", adquisition"

    	if expirationDate is not None:
    		action = action + ", perishable, expiration"

    	action = action +") VALUES (%s,%s,%s,%s"
    	
    	if adquisitionDate is not None:
    		action = action + ",%s"
    		kwargs = kwargs + (adquisitionDate,)

    	if expirationDate is not None:
    		action = action + ",true,%s"
    		kwargs = kwargs + (expirationDate,)

    	action = action + ")"

        self._cur.execute(action, kwargs)

    # Obtener toda la info de los lotes asociados a un producto
    def getLotsInfoByProductID(self, productID, onlyAvailables = True):
     	action = "SELECT * FROM " + lotsTable +str(productID)
     	if onlyAvailables:
     		action = action + "WHERE available = true"
     	self._cur.execute(action)
     	return self._cur.fetchall()

    # Obtener el productID y el nombre de los productos
    def getLots(self, onlyAvailables = True):
    	action = "SELECT productID FROM products"
    	if onlyAvailables:
    		action = action + " WHERE available = true"
    	self._cur.execute(action)
    	productIDs = self._cur.fetchall()
    	resp = {}
    	for productID in productIDs:
    		resp[productID[0]] = self.getLotsInfoByProductID(productID[0], onlyAvailables)
    	return resp
    	

    # Cambiar informacion de un lote
    def updateLot(self, productID, lotID, cost=None, quantity=None, category=None, provider=None, adquisitionDate=None, perishable = None, expirationDate=None, available=None):
    	if cost is None and quantity is None and category is None \
    		and provider is None and adquisitionDate is None \
    		and expirationDate is None and available is None:
    		return

    	action = "UPDATE " + lotsTable + str(productID) + " SET"
    	kwargs = ()

    	if quantity is not None or available is not None:
    		self._cur.execute("SELECT quantity, available FROM " + lotsTable + str(productID) + " WHERE lotID = %s", (lotID,) )
    		preChange = self._cur.fetchall()[0]
    		kwargsProduct = ()
    		actionProduct = "UPDATE products SET "
    		changeRequired =  False
    		if available is not None:
    			action = action + " available = %s,"
    			kwargs = kwargs + (available,)
    			if preChange[1] and not available:
    				changeRequired = True
    				actionProduct = actionProduct + " currentLot = CASE WHEN currentLot = %s THEN 0 ELSE currentLot END,  remainingLots = remainingLots-1,"
    				kwargsProduct = kwargsProduct + (lotID,)
    				if quantity is None:
    					actionProduct = actionProduct + "remaining = remaining + %s"
    					kwargsProduct = kwargsProduct + (-preChange[0],)
    			elif not preChange[1] and available:
    				changeRequired = True
    				actionProduct = actionProduct + " currentLot = CASE WHEN currentLot = 0 THEN %s ELSE currentLot END,  remainingLots = remainingLots+1,"
    				kwargsProduct = kwargsProduct + (lotID,)
    				if quantity is None:
    					actionProduct = actionProduct + "remaining = remaining + %s"
    					kwargsProduct = kwargsProduct + (preChange[0],)

    		if quantity is not None:
    			action = action + " quantity = %s,"
    			kwargs = kwargs + (quantity,)
    			if preChange[1]:
    				changeRequired = True
    				actionProduct = actionProduct + "remaining = remaining + %s"
    				if available is not None and not available:
    					kwargsProduct = kwargsProduct + (-preChange[0],)
    				else:
    					kwargsProduct = kwargsProduct + (quantity-preChange[0],)
    			elif not preChange[1] and available is not None and available:
    				changeRequired = True
    				actionProduct = actionProduct + "remaining = remaining + %s"
    				kwargsProduct = kwargsProduct + (quantity,)

    		if changeRequired:
	    		actionProduct = actionProduct + " WHERE productID = %s"
	    		kwargsProduct = kwargsProduct + (productID,)
	    		self._cur.execute(actionProduct, kwargsProduct)

    	

    	if cost is not None:
    		action = action + " cost = %s,"
    		kwargs = kwargs + (cost,)

    	if category is not None:
    		action = action + " category = %s,"
    		kwargs = kwargs + (category,)

    	if provider is not None:
    		action = action + " provider = %s,"
    		kwargs = kwargs + (provider,)

    	if adquisitionDate is not None:
    		action = action + " adquisition = %s,"
    		kwargs = kwargs + (adquisitionDate,)

    	if perishable is not None and expirationDate is None:
    		action = action + " perishable = %s,"
    		kwargs = kwargs + (perishable,)


    	if expirationDate is not None:
    		action = action + " perishable = True, expiration = %s,"
    		kwargs = kwargs + (expirationDate,)

    	action = action[:len(action)-1] + " WHERE lotId = %s"
    	kwargs = kwargs + (lotID,)

    	self._cur.execute(action, kwargs)

    # Borrar lote
    def deleteLot(self, productID, lotID):
    	self._cur.execute("SELECT quantity, available FROM " + lotsTable + str(productID) + " WHERE lotID = %s", (lotID,) )
    	preChange = self._cur.fetchall()[0]

    	if preChange[1]:
    		actionProduct = """
    		UPDATE products SET 
    			remaining = remaining + %s, 
    			remainingLots = remainingLots-1,
    			currentLot = 
    			CASE WHEN currentLot = %s THEN
    				0
    			ELSE
    				currentLot
    			END
    		WHERE productID = %s;
    		"""
    		self._cur.execute(actionProduct, (-preChange[0], lotID, productID))

    	action = "DELETE FROM " + lotsTable + str(productID) + " WHERE lotID = %s"
    	self._cur.execute(action, (lotID,))

    #-------------------------------------------------------------------------------------------------------------------------------
    # Métodos de control de LOGIN
    #-------------------------------------------------------------------------------------------------------------------------------

    def createUser(self, username, password):
    	action = "INSERT INTO login(username, password) VALUES(%s,%s)"
    	try:
    		self._cur.execute(action, (username, password))
    		print("Usuario " + username + " ha sido creado")
    		return True
    	except:
    		print("Usuario " + username + " ya existente")
    		return False

    def checkUser(self, username, password):
    	action = "SELECT username FROM login WHERE username = %s AND password = %s"
    	self._cur.execute(action, (username, password))
    	return (len(self._cur.fetchall()) != 0)

####################################################################################################################################
## FIN :)
####################################################################################################################################

# Pruebas de archivo
if __name__ == '__main__':
	DBManager("sistema_ventas", "hola", True)
