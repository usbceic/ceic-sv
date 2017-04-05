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

####################################################################################################################################
## MODÚLOS:
####################################################################################################################################

import sys
import datetime
from psycopg2 import connect, ProgrammingError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from os import mkdir
from os.path import isdir, join

####################################################################################################################################
## CONSTANTES:
####################################################################################################################################

#-----------------------------------------------------------------------------------------------------------------------------------
# Modelo PostgreSQL
#-----------------------------------------------------------------------------------------------------------------------------------

modelPath = "PSQL/old"             # Ruta donde se encuentra el modelo sql

modelCreator = [
    "create_extensions.sql",    # Crear extensiones
    "create_types.sql",         # Crear tipos y enums
    "create_tables.sql",        # Crear tablas
    "create_functions.sql",     # Crear funciones generales
    "create_triggers.sql",      # Crear triggers y sus funciones
]

modelKiller = [
    "remove_triggers.sql",      # Eliminar triggers y sus funciones
    "remove_functions.sql",     # Eliminar funciones generales
    "remove_tables.sql",        # Eliminar tablas
    "remove_extensions.sql",    # Eliminar extensiones
    "remove_types.sql",         # Eliminar tipos y enums
]

userTable = "db_user"                             # Tabla de usuarios
providerTable = "provider"                        # Tabla de proveedores
productTable = "product"                          # Tabla de productos
lotTable = "lot"                                  # Tabla de lotes
serviceTable = "service"                          # Tabla de servicios
clientTable = "client"                            # Tabla de clientes
purchaseTable = "purchase"                        # Tabla de compras
checkoutTable = "checkout"                        # Tabla de pagos de orden de compra
productListTable = "product_list"                 # Tabla de lista de productos de orden de compra
serviceListTable = "service_list"                 # Tabla de lista de servicios de orden de compra
reverseProductListTable = "reverse_product_list"  # Tabla de lista de productos de orden de compra
reverseServiceListTable = "reverse_service_list"  # Tabla de reversar lista de servicios de orden de compra
transferTable = "transfer"                        # Tabla de transferencias
operationLogTable = "operation_log"               # Tabla de registro de operaciones de caja
languageTable = "valid_language"                  # Tabla de lenguajes validos
bookTable = "book"                                # Tabla de libros
subjectTable = "subject"                          # Tabla de asignaturas
authorTable = "author"                            # Tabla de autores
associatedWithTable = "associated_with"           # Tabla que asocia libros con asignaturas
writtenByTable = "written_by"                     # Tabla que asocia libros con autores
lenToTable = "lent_to"                            # Tabla de préstamos de libros

#-----------------------------------------------------------------------------------------------------------------------------------
# Varios
#-----------------------------------------------------------------------------------------------------------------------------------

backupPath = "Backup/"

####################################################################################################################################
## MANEJADOR DE LA BASE DE DATOS:
####################################################################################################################################

class dbManager:
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
            self.executeFiles(modelKiller)   # Eliminar el modelo existente
            self.executeFiles(modelCreator)  # Crear un nuevo modelo

            self.createUser("Hola", "hola", "PRIVATE", "SNAFU", "coreoCaliente@gmail.com")
            self.createUser("Test2","test2","Soy", "Prueba","google@hotmail.com")
            print(self.getUsersInfo())
            print(self.getUserInfo("Hola"))

            #Prueba de Backup
            self.backupTable(clientTable, backupPath)

    #-------------------------------------------------------------------------------------------------------------------------------
    # Destructor de la clase
    #-------------------------------------------------------------------------------------------------------------------------------

    def __del__(self):
        if self._con is not None and self._cur is not None:
            try:
                self.closeDB()
                print("\nSe ha cerrado correctamente la base de datos\n")
            except:
                print("\nLa base de datos ya está cerrada\n")
        else:
            print("\nLa base de datos ya está cerrada\n")

    #-------------------------------------------------------------------------------------------------------------------------------
    # Métodos de control de la base de datos
    #-------------------------------------------------------------------------------------------------------------------------------

    # Cierra sesion en la base de datos
    def closeDB(self):
        self._cur.close() # Cerrar el pipe
        self._con.close() # Cerrar la connexion

    # Verifica si una tabla ya existe
    def tableExists(self, table):
        action = "SELECT to_regclass(%s)"
        self._cur.execute(action, ("public." + table,))
        return self._cur.fetchall()[0][0] is not None

    # Eliminar una tabla en la base de datos
    def dropTable(self, table):
        print("\nEliminando tabla: " + table)
        self._cur.execute("DROP TABLE " + table)

    # Método para ejecutar una lista de archivos .sql
    def executeFiles(self, files):
        print("")
        for file in files:
            try:
                fullPath = join(modelPath, file)
                self._cur.execute(open(fullPath, 'r').read())
                print("Ejecutado correctamente: "+fullPath)

            except ProgrammingError as psqlError:
                print("[ERROR] Se ha encontrado un problema al ejecutar: " + fullPath)
                print(psqlError)

            except FileNotFoundError:
                print("[ERROR] No se pudo encontrar el archivo: " + fullpath)

            except:
                print("Ha ocurrido un error inesperado:", sys.exc_info()[0])

    # Método para hacer BackUp a una tabla
    # Si no se especifica customName se llamara como la tabla
    def backupTable(self, table, savePath, customName=None):
        if not isdir(savePath): mkdir(savePath)      # Verificar que exista carpeta de salida

        if customName is None: tmp = table + ".sql"  # Establecer nombre de la abla por defecto
        else: tmp = customName + ".sql"              # Estalecer el nombre personalizado
        fullPath = join(savePath, tmp)               # Se crea la ruta completa

        print("\nCreando Backup de la tabla " + table + " en: " + fullPath)

        try:
            # Intentar hacer el BackUp
            with open(fullPath, 'w') as backup:
                self._cur.copy_to(backup, table)
                backup.close()
            print("BackUp creado satisfactoreamente.")

        except:
            print("Ha ocurrido un error inesperado:", sys.exc_info()[0])

    # Método para restaurar una tabla desde un BackUp
    # Si no se especifica customName se buscara archivo con mismo nombre de la tabla
    # En condiciones normales se deberia dropear la tabla y crearla de nuevo
    """def restoreTable(self, table, columns, filePath, customName=None, drop=True):
        if customName is None: tmp = table + ".sql"
        else: tmp = customName + ".sql"
        fullPath = join(filePath, tmp)

        print("\nRestaurando la tabla " + table + " desde: " + fullPath)

        try:
            backup = open(file, 'r')

        except FileNotFoundError:
            print("[ERROR] No se pudo encontrar el archivo: " + fullpath)

        except:
            print("[ERROR] No se pudo abrir el archivo: " + file)

        else:
            if not drop and self.tableExists(table):
                print("[ADVERTENCIA] La tabla " + table + "existe y no fue vuelta a crear. Pueden ocurrir errores con los datos")

            self.createTable(table, columns, drop)
            try:
                self._cur.copy_from(f, table)
                print("Tabla restaurada satisfactoriamente")

            except Exception as e:
                print("[ERROR] No se pudieron copiar los datos a la tabla")
                print(e)
            backup.close()"""

    #-------------------------------------------------------------------------------------------------------------------------------
    # Métodos asociados a la tabla de usuarios
    #-------------------------------------------------------------------------------------------------------------------------------

    # Crear un usuario nuevo
    def createUser(self, userName, password, firstName, lastName, email, permissionsMask=0):
        action = "SELECT create_db_user(%s, %s, %s, %s, %s, %s);"
        kwargs = (userName, password, firstName, lastName, email, permissionsMask,)

        try:
            self._cur.execute(action, kwargs)
            print("\nSe ha creado el usuario " + userName + " satisfactoriamente")
            return True

        except:
            print("\nNo se pudo crear el usuario: " + userName)
            return False

    # Verificar correspondencia de usuario y contraseña para el login
    def check_password(self, userName, password):
        action = "SELECT check_password(%s, %s)"
        kwargs = (userName, password,)

        self._cur.execute(action, kwargs)
        query = self._cur.fetchall()

        if len(query) == 1: return True
        return False

    # Obtener la info de los usuarios (sin contraseña)
    def getUsersInfo(self, orderByLastLogin=False, descendentingOrderLastLogin=False):
        action = "SELECT get_users_info(%s, %s)"
        kwargs = (orderByLastLogin, descendentingOrderLastLogin,)

        try:
            self._cur.execute(action, kwargs)
            return self._cur.fetchall()

        except:
            print("\n[ERROR] No se pudo realizar la consulta")
            return None

    # Obtener la info de un usuario dado su username
    def getUserInfo(self, userName):
        action = "SELECT get_user_info(%s)"
        kwargs = (userName,)

        try:
            self._cur.execute(action, kwargs)
            return self._cur.fetchall()

        except:
            print("\n[ERROR] No se pudo realizar la consulta")
            return None

    #-------------------------------------------------------------------------------------------------------------------------------
    # Métodos varios
    #-------------------------------------------------------------------------------------------------------------------------------

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

# Pruebas de archivo
if __name__ == '__main__':
    dbManager("postgres", "iron-man", True)