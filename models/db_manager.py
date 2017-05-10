# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación del manejador de la base de datos de CEIC Suite

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Christian Oliveros, 01christianol01@gmail.com
# Pablo Betancourt, pablodbc30@gmail.com

###################################################################################################################################################################################
## PATH:
###################################################################################################################################################################################

from sys import path                          # Importación del path del sistema
from os.path import join, dirname, basename   # Importación de funciones para unir y separar paths con el formato del sistema

# Para cada path en el path del sistema para la aplicación
for current in path:
    if basename(current) == "models":
        path.append(join(dirname(current), "modules"))  # Agregar la carpeta modules al path
        break

###################################################################################################################################################################################
## DEPENDENCIAS:
###################################################################################################################################################################################

from models import *
from session import startSession, resetDataBase
from db_backup import DBBackup
from sqlalchemy import func, distinct, update, event, and_, or_, desc
from passlib.hash import bcrypt
from str_random import str_random
from app_utilities import noneToZero

###################################################################################################################################################################################
## DECLARACIÓN DEL MANEJADOR:
###################################################################################################################################################################################

class dbManager(object):
    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE LA CLASE dbManager:
    #==============================================================================================================================================================================

    """
    Método de creación de la clase
     - Inicia la sesión con la base de datos
    """
    def __init__(self, name, password, debug=False, dropAll=False, parent=None):
        super(dbManager, self).__init__()
        self.name = name
        self.password = password
        self.open(debug, dropAll)

    """
    Método de destrucción de la clase
     - Cierra la sesión en la base de datos
    """
    def __del__(self):
        self.close()

    """
    Método para abrir la sesión en la base de datos
     - Abre la sesión en la base de datos
    """
    def open(self, debug=False, dropAll=False):
        try:
            self.session = startSession(self.name, self.password, debug, dropAll)
        except Exception as e:
            print("Error desconocido al intentar iniciar la sesión en la base")

    """
    Método para cerrar la sesión en la base de datos
     - Cierra la sesión en la base de datos
    """
    def close(self):
        try:
            self.session.close()
            print("Se ha cerrado correctamente la base de datos")
        except:
            print("La base de datos ya está cerrada")

    """
    Método para hacer backup a la Base de Datos
    Devuelve True si logro hacer backup.
    En caso de encontrar que el ultimo backup esta corrupto, devuelve False
    """
    def backup(self):
        return DBBackup().backup()

    """
    Método para hacer restore a la Base de Datos
    Retorna True si logro hacer restore, False en caso contrario
    """
    def restore(self):
        self.close()
        resetDataBase()
        restore = DBBackup().restore()
        self.open()
        return restore

    """
    Método para borrar el último backup
    Retorna True si la carpeta no existe o  si fue borrada con éxito.
    False en caso contrario.
    """
    def deleteLastBackup(self):
        return DBBackup().deleteLastBackup()

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE USUARIOS:
    #==============================================================================================================================================================================

    """
    Método para verificar que un rango es válido
     - Retorna True:
        * Cuando el rango es un número entero entre 0 y 3
     - Retorna False:
        * Cuando el rango no es un número entero entre 0 y 3
    """
    def validRange(self, range):
        if 0 <= range <= 3: return True
        return False

    """
    Método para obtener el rango asociado a una máscara de permisos
     - Retorna el rango correspondiente a la máscara de permisos especificada
    """
    def getRange(self, permission_mask):
        if permission_mask == 0: return "Colaborador"
        elif permission_mask == 1: return "Vendedor"
        elif permission_mask == 2: return "Administrador"
        else: return "Dios"

    """
    Método para obtener la máscara de permisos asociada a un rango
     - Retorna un número correspondiente ala máscara de permisos asociada al rango especificado
    """
    def getPermissionMask(self, userRange):
        userRange = userRange.title().strip()

        if userRange == "Colaborador": return 0
        elif userRange == "Vendedor": return 1
        elif userRange == "Administrador": return 2
        else: return 3

    """
    Método para verificar que un usuario existe.
     - Retorna True:
        * Cuando el usuario existe
     - Retorna False:
        * Cuando el usuario NO existe
    """
    def existUser(self, username, active=True):
        count = self.session.query(User).filter_by(username=username, active=active).count()
        if count == 0:
            print("El usuario " + username + " NO existe")
            return False
        else:
            print("El usuario " + username + " existe")
            return True

    """
    Método para verificar si existe algun usuario al que pertenezca un correo especificado
     - Retorna True:
        * Cuando el email pertenece a algún usuario
     - Retorna False:
        * Cuando el email NO pertenece a ningun usuario
    """
    def existUserEmail(self, email, active=True):
        count = self.session.query(User).filter_by(email=email, active=active).count()
        if count == 0:
            print("El email " + email + " NO esta registrado")
            return False
        else:
            print("El email " + email + " esta registrado")
            return True

    """
    Método para crear un usuario nuevo
     - Retorna True:
        * Cuando el usuario es creado satisfactoreamente
     - Retorna False:
        * Cuando ya existe el usuario
        * Cuando no se puede crear
    """
    def createUser(self, username, password, firstname, lastname, email, permission_mask):
        if not self.existUser(username):
            newUser = User(username=username, password=bcrypt.hash(password), firstname=firstname, lastname=lastname, email=email, permission_mask=permission_mask)
            self.session.add(newUser)
            try:
                self.session.commit()
                print("Se ha creado correctamente el usuario " + username)
                return True
            except Exception as e:
                print("Error desconocido al crear el usuario " + username +":", e)
                self.session.rollback()
                return False
        else:
            print("No se puede crear el usuario " + username + " porque ya existe")
            return False

    """
    Método para eliminar (desactivar) un usuario
     - Retorna True:
        * Cuando el usuario es eliminado (desactivado) satisfactoreamente
     - Retorna False:
        * Cuando el usuario NO existe
        * Cuando el usuario ya está desactivado
        * Cuando no se puede eliminar (desactivar) por alguna razón
    """
    def deleteUser(self, username):
        if self.existUser(username):
            try:
                self.session.execute(update(User).where(User.username==username).values(active=False))
                self.session.commit()
                print("Se ha desactivado el usuario: " + username)
                return True
            except Exception as e:
                print("Ha ocurrido un error desconocido al intentar desactivar el usuario: " + username, e)
                self.session.rollback()
                return False
        return False

    """
    Método para verificar correspondencia entre usuario y contraseña
     - Retorna True:
        * Cuando los datos coinciden con los almacenados en la base de datos
     - Retorna False:
        * Cuando el usuario no existe
        * Cuando los datos NO coinciden con los almacenados en la base de datos
    """
    def checkPassword(self, username, password):
        if self.existUser(username):
            hashedPass = self.session.query(User.password).filter_by(username=username).all()[0][0]
            if bcrypt.verify(password, hashedPass):
                print("Información de inicio de sesión válidada correctamente")
                return True
            else:
                print("La contraseña no corresponde al usuario especificado")
                return False
        return False

    """
    Método para iniciar sesión. Primero verifica la correspondencia entre username y contraseña con la base de datos y luego actualiza la fecha del último login
     - Retorna 0:
        * Cuando los datos coinciden con los almacenados en la base de datos y se logra actualizar la fecha de último inicio de sesión del usuario
     - Retorna 1:
        * Cuando el usuario NO existe
        * Cuando los datos NO coinciden con los almacenados en la base de datos
     - Retorna 2:
        * Cuando NO se logra actualizar la fecha de último inicio de sesión del usuario por alguna razón
    """
    def loginUser(self, username, password):
        if self.checkPassword(username, password):
            try:
                self.session.execute(update(User).where(User.username==username).values(last_login=datetime.now()))
                self.session.commit()
                print("Se ha actualizado la fecha de último inicio de sesión para el usuario: " + username)
                return 0
            except Exception as e:
                print("Ha ocurrido un error al intentar actualizar la fecha del último inicio de sesión para el usuario " + username, e)
                self.session.rollback()
                return 2
        return 1

    """
    Método para cambiar la contraseña de un usuario
     - Retorna True:
        * Cuando logra cambiar la contraseña correctamente
     - Retorna False:
        * Cuando el usuario no existe
        * Cuando la contraseña antigua no coincide con la almacenada en la base de datos
        * Cuando no pudo cambiarse la contraseña por alguna otra razón
    """
    def changePassword(self, username, oldPass, newPass):
        if self.checkPassword(username, oldPass):
            try:
                self.session.execute(update(User).where(User.username==username).values(password=bcrypt.hash(newPass)))
                self.session.commit()
                print("Se ha cambiado la contraseña del ususario " + "satisfactoriamente")
                return True
            except Exception as e:
                print("Ha ocurrido un error al intentar cambiar la contraseña del usuario " + username, e)
                self.session.rollback()
                return False
        return False

    """
    Método para resetear la contraseña de un usuario generando una nueva
     - Retorna un string de 8 caracteres que representa la nueva contraseña del usuario cuando logra resetear la contraseña
     - Retorna None cuando no puede resetear la contraseña por alguna razón
    """
    def resetPassword(self, username):
        try:
            newPass = str_random()
            self.session.execute(update(User).where(User.username==username).values(password=bcrypt.hash(newPass)))
            self.session.commit()
            print("Se ha cambiado la contraseña del ususario " + "satisfactoriamente")
            return newPass
        except Exception as e:
            print("Ha ocurrido un error al intentar cambiar la contraseña del usuario " + username, e)
            self.session.rollback()
            return None

    """
    Método para cambiar la el perfil de un ususario
     - Retorna True:
        * Cuando logra cambiar el perfil correctamente
     - Retorna False:
        * Cuando el usuario no existe
        * Cuando no pudo cambiarse el perfil por alguna otra razón
    """
    def updateUserProfile(self, username, newProfile):
        if self.existUser(username):
            try:
                self.session.execute(update(User).where(User.username==username).values(profile=newProfile))
                self.session.commit()
                print("Se ha cambiado el perfil del ususario " + username + " satisfactoriamente")
                return True
            except Exception as e:
                print("Ha ocurrido un error al intentar cambiar el perfil del usuario " + username, e)
                self.session.rollback()
                return False
        return False

    """
    Método para cambiar la el rango de un ususario
     - Retorna True:
        * Cuando logra cambiar el rango correctamente
     - Retorna False:
        * Cuando el usuario no existe
        * Cuando no pudo cambiarse el rango por alguna otra razón
    """
    def updateUserRange(self, username, permission_mask):
        if self.existUser(username):
            if self.validRange(permission_mask):
                try:
                    self.session.execute(update(User).where(User.username==username).values(permission_mask=permission_mask))
                    self.session.commit()
                    print("Se ha cambiado el rango de " + username + " satisfactoriamente")
                    return True
                except Exception as e:
                    print("Ha ocurrido un error al intentar cambiar el rango del usuario " + username, e)
                    self.session.rollback()
                    return False
            return False
        return False

    """
    Método para actualizar información de un usuario
     - Retorna True:
        * Cuando logra actualizar la información correctamente
     - Retorna False:
        * Cuando el usuario no existe
        * Cuando no pudo actualizarse la infromación por alguna otra razón
    """
    def updateUserInfo(self, username, firstname=None, lastname=None, email=None):
        if self.existUser(username):
            values = {}
            if firstname != None: values["firstname"] = firstname
            if lastname != None: values["lastname"] = lastname
            if email != None: values["email"] = email
            try:
                self.session.query(User).filter_by(username=username).update(values)
                self.session.commit()
                print("Se ha actualizado la información del ususario " + username + " satisfactoriamente")
                return True
            except Exception as e:
                print("Ha ocurrido un error desconocido al intentar actualizar la información del usuario " + username, e)
                self.session.rollback()
                return False
        return False

    """
    Método para obtener todos los nombres de usuario
     - Retorna un queryset con todos los nombres de usuario
    """
    def getUserNames(self):
        query = self.session.query(User.username).all()
        usersNames = []
        for name in query:
            usersNames.append(name[0])
        return sorted(usersNames)

    """
    Método para obtener información de un usuario
     - Retorna un queryset con la información básica de un usuario
    """
    def getUserInfo(self, username):
        return self.session.query(User.firstname, User.lastname, User.email, User.profile, User.permission_mask, User.last_login).filter(User.username == username).all()[0]

    """
    Método para retornar usuarios segun un filtro especificado
     - Retorna un queryset con los usuarios que pasan el filtro
    """
    def getUsers(self, username = None, firstname = None, lastname = None, email = None, permission_mask = None, limit = None, page = 1):
        filters = {}
        if username != None: filters["username"] = username
        if firstname != None: filters["firstname"] = firstname
        if lastname != None: filters["lastname"] = lastname
        if email != None: filters["email"] = email
        if permission_mask != None: filters["permission_mask"] = permission_mask

        query = self.session.query(User).filter_by(**filters).order_by(desc(User.last_login))

        if limit != None:
            query = self.session.query(User).filter_by(**filters).order_by(desc(User.last_login)).limit(limit).offset((page-1)*limit)

        return query.all()

    """
    Método para retornar la cantidad de usuarios segun un filtro
     - Retorna la cantidad de usuarios segun un filtro
    """
    def getUsersCount(self, permission_mask = None):
        filters = {}
        if permission_mask != None: filters["permission_mask"] = permission_mask

        return self.session.query(User).filter_by(**filters).count()

    """
    Método para retornar el rango de un usuario especificado
     - Retorna el rango del usuario especificado
    """
    def getUserRange(self, username):
        permission_mask = self.session.query(User.permission_mask).filter_by(username=username).scalar()
        return self.getRange(permission_mask)

        """
    Método para retornar el rango de un usuario especificado
     - Retorna el rango del usuario especificado
    """
    def getUserPermissionMask(self, username):
        return self.session.query(User.permission_mask).filter_by(username=username).scalar()

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE PROVEEDORES:
    #==============================================================================================================================================================================

    '''
    Método para verificar la existencia de un proveedor
    retorna True si existe
    retorna False si no existe
    '''
    def existProvider(self, provider_name):
        provider_name = provider_name.title().strip()

        count = self.session.query(Provider).filter_by(provider_name=provider_name).count()
        if count == 0:
            print("El proveedor " + provider_name + " no existe")
            return False
        else:
            print("El proveedor " + provider_name + " ya existe")
            return True

    '''
    Método para agregar un proveedor
    Retorna True si el proveedor fue agregado con exito
    Retorna False cuando el proveedor ya existe
    Genera una excepcion cuando algo sale mal
    '''
    def createProvider(self, provider_name, pay_information = "", phone = "", email = "", description = ""):
        provider_name = provider_name.title().strip()

        if (self.existProvider(provider_name)):
            return False
        kwargs = {'provider_name' : provider_name}

        if pay_information is not None:
            kwargs['pay_information'] = pay_information

        if phone is not None:
            kwargs['phone'] = phone

        if email is not None:
            kwargs['email'] = email

        if description is not None:
            kwargs['description'] = description

        newProvider = Provider(**kwargs)
        self.session.add(newProvider)
        try:
            self.session.commit()
            print("Se ha creado correctamente el proveedor " + provider_name)
            return True
        except Exception as e:
            print("Error al crear el proveedor " + provider_name +":", e)
            self.session.rollback()
            return False

    '''
    Método para actualizar la información de un proveedor.
        -Retorna True si la actualización de datos fue hecha con exito.
        -Retorna False si ocurrió un error durante la actualización de datos.
    '''

    def updateProviderInfo(self,oldName,newName=None,phone=None,email=None,pay_information=None,description=None,active=None,creation_date=None):
        oldName = oldName.title().strip()

        kwargs = {}
        if newName is not None:
            newName = newName.title().strip()
            kwargs['provider_name'] = newName

        if phone is not None:
            kwargs['phone'] = phone

        if email is not None:
            kwargs['email'] = email

        if pay_information is not None:
            kwargs['pay_information'] = pay_information

        if description is not None:
            kwargs['description'] = description

        if active is not None:
            kwargs['active'] = active

        if creation_date is not None:
            kwargs['creation_date'] = creation_date

        try:
            self.session.query(Provider).filter_by(provider_name=oldName).update(kwargs)
            self.session.commit()
            if newName is not None:
                name = newName
            else:
                name = oldName
            print("Se ha actualizado la información del proveedor " + name + " satisfactoriamente")
            return True
        except Exception as e:
            print("Ha ocurrido un error desconocido al intentar actualizar la información del proveedor " + oldName, e)
            self.session.rollback()
            return False
        return False

    '''
    Método para obtener los nombres de TODOS los proveedores
        - Retorna una lista con el nombre de cada proveedor
    '''
    def getProvidersNames(self):
        query = self.session.query(Provider.provider_name).all()
        providersNames = []
        for name in query:
            providersNames.append(name[0])
        return sorted(providersNames)

    '''
    Método para obtener TODA la informacion de un proveedor dado su nombre
        - Retorna la instancia de Proveedor correspondiente al nombre
    '''
    def getProvider(self, provider_name):
        return self.session.query(Provider).filter_by(provider_name=provider_name).all()[0]

    '''
    Método para obtener TODA la informacion de los proveedores existentes en la base de datos
        - Retorna un queryset con TODOS los proveedores
    '''
    def getAllProviders(self, limit = None, page = 1):
        query = self.session.query(Provider).order_by(Provider.creation_date)

        if limit != None:
            query = self.session.query(Provider).order_by(desc(Provider.creation_date)).limit(limit).offset((page-1)*limit)

        return query.all()

    '''
    Método para obtener la cantidad de proveedores registrados
        - Retorna la cantidad de proveedores registrados
    '''
    def getProvidersCount(self):
        return self.session.query(Provider).count()

    '''
    Método para obtener TODOS los nombres de los proveedores existentes en la base de datos en orden lexicografico.
        - Retorna un queryset con los nombres de todos los proveedores en orden lexicografico.
    '''

    def getAllProvidersByName(self):
        return self.session.query(Provider.provider_name).order_by(Provider.provider_name).all()

    '''
    Método para obtener TODOS los nombres de los proveedores existentes en la base de datos en orden de creación.
        - Retorna un queryset con los nombres de todos los proveedores en orden de creacion.
    '''

    def getAllProvidersByCreationDate(self):
        return self.session.query(Provider.provider_name).order_by(Provider.creation_date).all()

    '''
    Método para obtener TODOS los nombres de los proveedores ACTIVOS en la base de datos en orden lexicografico.
        - Retorna un queryset con los nombres de todos los proveedores en orden lexicografico.
    '''

    def getAllActiveProvidersByName(self):
        return self.session.query(Provider.provider_name).filter(Provider.active == True).order_by(Provider.provider_name).all()

    '''
    Método para obtener TODOS los nombres de los proveedores ACTIVOS en la base de datos en orden de creación.
        - Retorna un queryset con los nombres de todos los proveedores en orden de creacion.
    '''

    def getAllActiveProvidersByCreationDate(self):
        return self.session.query(Provider.provider_name).filter(Provider.active == True).order_by(Provider.creation_date).all()

    '''
    Método para obtener TODOS los nombres de los proveedores NO ACTIVOS en la base de datos en orden lexicografico.
        - Retorna un queryset con los nombres de todos los proveedores en orden lexicografico.
    '''

    def getAllActiveProvidersByName(self):
        return self.session.query(Provider.provider_name).filter(Provider.active == False).order_by(Provider.provider_name).all()

    '''
    Método para obtener TODOS los nombres de los proveedores NO ACTIVOS en la base de datos en orden de creación.
        - Retorna un queryset con los nombres de todos los proveedores en orden de creacion.
    '''

    def getAllActiveProvidersByCreationDate(self):
        return self.session.query(Provider.provider_name).filter(Provider.active == False).order_by(Provider.creation_date).all()

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE PRODUCTOS:
    #==============================================================================================================================================================================

    """
    Método para verificar que un producto existe.
     - Retorna True:
        * Cuando el producto existe
     - Retorna False:
        * Cuando el producto NO existe
    """
    def existProduct(self, product_name, available = None, active = True):
        product_name = product_name.title().strip()

        values = {"product_name" : product_name}
        if available != None: values["available"] = available
        if active != None: values["active"] = active

        count = self.session.query(Product).filter_by(**values).count()

        if count == 0:
            print("El producto " + product_name + " NO existe")
            return False
        else:
            print("El producto " + product_name + " existe")
            return True

    """
    Método para crear un producto nuevo
     - Retorna True:
        * Cuando el producto es creado satisfactoreamente
        * Cuando el producto ya existía pero estaba desactivado
     - Retorna False:
        * Cuando ya existe el producto y está activo
        * Cuando no se puede crear
    """
    def createProduct(self, product_name, price, category=""):
        product_name = product_name.title().strip()

        if not self.existProduct(product_name, active = None):
            self.session.add(Product(product_name=product_name, price=price, category=category))
            try:
                self.session.commit()
                print("Se ha creado correctamente el producto: " + product_name)
                return True
            except Exception as e:
                print("Error desconocido al crear el producto: " + product_name +":", e)
                self.session.rollback()
                return False
        elif self.existProduct(product_name, active=False):
            self.updateProduct(product_name, product_name, price, category, active = True)
            print("Se ha actualizado el producto " + product_name + " y se reactivo.")
            return True

        else:
            print("No se puede crear el producto " + product_name + " porque ya existe y está activo")
            return False

    """
    Método para buscar un producto por su nombre o por su id
     - Retorna un queryset con el resultado de la búsqueda
    """
    def getProductByNameOrID(self, product_name=None, product_id=None, available=None):
        product_name = product_name.title().strip()
        filters = and_()
        if (product_name and product_id) != None: filters = and_(filters, or_(Product.product_name == product_name, Product.product_id == product_id))
        elif product_name != None: filters = and_(filters, Product.product_name == product_name)
        else: filters = and_(filters, Product.product_id == product_id)
        if available != None: filters = and_(filters, Product.available == available)
        return self.session.query(Product).filter(*filters).all()

    """
    Método para obtener el id de un producto especificando su nombre
     - Retorna el id correspondiente al producto de nombre especificado si este existe
     - Retorna None cuando no existe un producto con el nombre especificado
    """
    def getProductID(self, product_name, active = True):
        product_name = product_name.title().strip()
        if self.existProduct(product_name, active = active): return self.session.query(Product.product_id).filter_by(product_name=product_name).all()[0][0]
        else: return None

    """
    Método para obtener el nombre de cada producto
     - Retorna un queryset con lós resultados de la búsqueda
    """
    def getProductsNames(self, product_name, acitve=True):
        product_name = product_name.title().strip()
        return self.session.query(Product.product_name).filter_by(active=active).order_by(Product.product_name).all()

    """
    Método para obtener los atributos especificados de todos los productos que cumplan con el filtro especificado
     - Retorna un queryset con lós resultados de la búsqueda
    """
    def getProducts(self, product_id=None, product_name=None, price=None, remaining=None, remaining_lots=None, category=None, available=None, active=None, limit=None, page=1):
        columns = []
        if product_id != None: columns.append(Product.product_id)
        if product_name != None: columns.append(Product.product_name)
        if price != None: columns.append(Product.price)
        if remaining != None: columns.append(Product.remaining)
        if remaining_lots != None: columns.append(Product.remaining_lots)
        if category != None: columns.append(Product.category)

        filters = {}
        if available != None: filters["available"] = available
        if active != None: filters["active"] = active

        query = self.session.query(*columns).filter_by(**filters).order_by(Product.product_name)

        if limit != None:
            query = self.session.query(*columns).filter_by(**filters).order_by(Product.product_name).limit(limit).offset((page-1)*limit)

        return query.all()

    """
    Método para obtener la cantidad de productos segun un filtro
     - Retorna la cantidad de productos segun un filtro
    """
    def getProductsCount(self, available=None, active=True):
        filters = {}
        if available != None: filters["available"] = available
        if active != None: filters["active"] = active

        return self.session.query(Product).filter_by(**filters).count()

    """
    Método para actualizar información de un producto
     - Retorna True:
        * Cuando logra actualizar la información correctamente
     - Retorna False:
        * Cuando el producto no existe
        * Cuando no pudo actualizarse la infromación por alguna otra razón
    """
    def updateProduct(self, product_name, new_product_name=None, price=None, category=None, active = None):
        product_name = product_name.title().strip()

        if self.existProduct(product_name, active = None):
            values = {}
            if new_product_name != None:
                new_product_name = new_product_name.title().strip()
                values["product_name"] = new_product_name.title().strip()
            if price != None: values["price"] = price
            if category != None: values["category"] = category
            if active != None: values["active"] = active
            try:
                self.session.query(Product).filter_by(product_name=product_name).update(values)
                self.session.commit()
                print("Se ha actualizado la información del producto " + product_name + " satisfactoriamente")
                return True
            except Exception as e:
                print("Ha ocurrido un error desconocido al intentar actualizar la información del producto " + product_name, e)
                self.session.rollback()
                return False
        return False

    """
    Método para eliminar (desactivar) un producto
     - Retorna True:
        * Cuando el producto es eliminado (desactivado) satisfactoreamente
     - Retorna False:
        * Cuando el producto NO existe
        * Cuando el producto ya está desactivado
        * Cuando no se puede eliminar (desactivar) por alguna razón
    """
    def deleteProduct(self, product_name):
        product_name = product_name.title().strip()

        if self.existProduct(product_name):
            self.session.query(Product).filter_by(product_name=product_name).update({"active" : False})
            try:
                self.session.commit()
                self.afterDeleteProduct(product_name)
                print("Se ha desactivado el producto: " + product_name)
                return True

            except Exception as e:
                print("Ha ocurrido un error desconocido al intentar desactivar el producto: " + product_name, e)
                self.session.rollback()
                return False
        return False

    """
    Pseudo-Trigger para eliminar los lotes asociados al producto desactivado
     - No retorna nada
    """
    def afterDeleteProduct(self, product_name):
        product_name = product_name.title().strip()
        product_id = self.getProductID(product_name, active = False)
        lots = self.getLotsIDByProductID(product_id)
        for lot_id in lots:
            self.session.query(Lot).filter_by(lot_id=lot_id).update({"available" : False, "current" : False})
            try:
                self.session.commit()
                print("Se ha eliminado el lote " + str(lot_id) + " del producto desactivado: " + product_name)

            except Exception as e:
                self.session.rollback()
                print("No se pudo eliminar el lote " + str(lot_id) + " del producto desactivado: " + product_name)
        self.afterUpdateLot(lots[0])

    """
    Método para restarle uno a la cantidad de lotes restantes de un producto
     - Retorna True:
        * Cuando logra restarle uno a la cantidad de lotes restantes
     - Retorna False:
        * Cuando NO pudo restarle uno a la cantidad de lotes restantes por alguna otra razón
    """
    def substractToRemainingLots(self, product_id):
        remaining_lots = self.session.query(Product.remaining_lots).filter_by(product_id=product_id).scalar()
        self.session.query(Product).filter_by(product_id=product_id).update({"remaining_lots" : remaining_lots-1})

        try:
            self.session.commit()
            self.afterUpdateRemainingLots(product_id)
            print("Actualizado lotes restantes del producto " + str(product_id))
            return True

        except Exception as e:
            self.session.rollback()
            print("Ha ocurrido un error desconocido al intentar actualizar los lotes restantes del producto " + str(product_id), e)
            return False

    """
    Método para actualizar la disponibilidad de un producto
     - Retorna True:
        * Cuando logra actualizar la disponibilidad
     - Retorna False:
        * Cuando NO pudo actualizar la disponibilidad por alguna otra razón
    """
    def afterUpdateRemainingLots(self, product_id):
        remaining_lots = self.session.query(Product.remaining_lots).filter_by(product_id=product_id).scalar()
        if remaining_lots == 0:
            self.session.query(Product).filter_by(product_id=product_id).update({"available" : False})
            try:
                self.session.commit()
                print("Actualizada disponibilidad del producto " + str(product_id))
                return True

            except Exception as e:
                self.session.rollback()
                print("Ha ocurrido un error desconocido al intentar actualizar la disponibilidad del producto " + str(product_id), e)
                return False

    """
    Método para obtener los 10 productos más vendidos
     - Retorna un queryset con el nombre y precio de cada uno de los 10 productos más vendidos
    """
    def getTop10(self):
        subQuery = self.session.query(Product_list.product_id.label("product_id"), func.sum(Product_list.amount).label("total")).group_by(Product_list.product_id).order_by(desc("total")).limit(10).subquery("subQuery")

        return self.session.query(Product.product_name.label("product_name"), Product.price.label("price")).join(subQuery, Product.product_id == subQuery.c.product_id).order_by(desc("total")).all()

    """
    Método para obtener los 10 productos más nuevos
     - Retorna un queryset con los 10 productos más nuevos
    """
    def getNew10(self):
        return self.session.query(Product.product_name, Product.price).order_by(desc(Product.creation_date)).limit(10).all()

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE LOTES:
    #==============================================================================================================================================================================

    """
    Método para verificar que un lote existe.
     - Retorna True:
        * Cuando el lote existe
     - Retorna False:
        * Cuando el lote NO existe
    """
    def existLot(self, lot_id, available=True):
        count = self.session.query(Lot).filter_by(lot_id=lot_id, available=available).count()
        if count == 0:
            print("El lote " + str(lot_id) + " NO existe")
            return False
        else:
            print("El lote " + str(lot_id) + " existe")
            return True

    """
    Método para verificar que un producto tine lotes disponibles
     - Retorna True:
        * Cuando el producto tiene lotes disponibles
     - Retorna False:
        * Cuando el producto NO tiene lotes disponibles
    """
    def hasAvailableLot(self, product_id):
        count = self.session.query(Lot).filter_by(product_id=product_id, available=True).count()
        if count == 0:
            print("El producto " + str(product_id) + " NO tiene lotes disponibles")
            return False
        else:
            print("El producto " + str(product_id) + " tiene lotes disponibles")
            return True

    """
    Método para verificar que un producto tine lotes en current
     - Retorna True:
        * Cuando el producto tiene lotes en current
     - Retorna False:
        * Cuando el producto NO tiene lotes en current
    """
    def hasCurrentLot(self, product_id):
        count = self.session.query(Lot).filter_by(product_id=product_id, current=True).count()
        if count == 0:
            print("El producto " + str(product_id) + " NO tiene lotes en current")
            return False
        else:
            print("El producto " + str(product_id) + " tiene lotes en current")
            return True

    """
    Método para crear un lote nuevo
     - Retorna True:
        * Cuando el lote es creado satisfactoreamente
     - Retorna False:
        * Cuando NO existe el producto
        * Cuando NO existe el proveedor
        * Cuando NO existe el ususario
        * Cuando NO se puede crear por alguna otra razón
    """
    def createLot(self, product_name, provider_name, received_by, cost, quantity, expiration_date=None):
        product_name = product_name.title().strip()
        provider_name = provider_name.title().strip()

        if self.existProvider(provider_name) and self.existProduct(product_name) and self.existUser(received_by):
            product_id = self.getProductID(product_name)
            kwargs = {
                "product_id"  : product_id,
                "provider_id" : provider_name,
                "received_by" : received_by,
                "cost"        : cost,
                "quantity"    : quantity,
                "remaining"   : quantity
            }

            if expiration_date != None:
                kwargs["perishable"] = True
                kwargs["expiration_date"] = expiration_date

            if not self.hasCurrentLot(product_id): kwargs["current"] = True

            newLot = Lot(**kwargs)
            self.session.add(newLot)

            try:
                self.session.commit()
                print("Se ha creado correctamente el lote")
                self.afterInsertLot(newLot.lot_id)
                return True
            except Exception as e:
                self.session.rollback()
                print("No se ha podido crear el lote", e)
                return False
        return False

    """
    Pseudo-Trigger para actualizar un producto luego de haber insertado un lote del mismo
     - No retorna nada
    """
    def afterInsertLot(self, lot_id):
        product_id, quantity = self.session.query(Lot.product_id, Lot.quantity).filter_by(lot_id=lot_id, available=True).all()[0]
        remaining, remaining_lots = self.session.query(Product.remaining, Product.remaining_lots).filter_by(product_id=product_id).all()[0]

        values = {
            "remaining"      : remaining+quantity,
            "remaining_lots" : remaining_lots+1,
            "available"      : True
        }

        for i in range(10):
            self.session.query(Product).filter_by(product_id = product_id).update(values)
            try:
                self.session.commit()
                print("Se ha actualizado el producto")
                break

            except Exception as e:
                self.session.rollback()
                print("No se pudo actualizar el producto")

    """
    Método para actualizar información de un lote
     - Retorna True:
        * Cuando logra actualizar la información correctamente
     - Retorna False:
        * Cuando el lote no existe
        * Cuando no pudo actualizarse la infromación por alguna otra razón
    """
    def updateLot(self, lot_id, product_name=None, provider_id=None, cost=None, quantity=None, remaining=None, expiration_date=None):
        if self.existLot(lot_id):
            values = {}
            remainingTrigger = False

            if product_name != None:
                product_name = product_name.title().strip()
                if self.existProduct(product_name):
                    values["product_id"] = self.getProductID(product_name)

            if provider_id != None:
                provider_id = provider_id.title().strip()
                if self.existProvider(provider_id):
                    values["provider_id"] = provider_id

            if cost != None:
                values["cost"] = cost

            if quantity != None and quantity > 0:
                values["quantity"] = quantity

            if remaining != None and remaining <= quantity:
                values["remaining"] = remaining
                if remaining <= 0: remainingTrigger = True

            elif remaining == None and quantity > 0:
                values["remaining"] = quantity

            if expiration_date != None:
                if expiration_date > datetime.now().date():
                    values["expiration_date"] = expiration_date
                    values["perishable"] = True

                else:
                    values["expiration_date"] = None
                    values["perishable"] = False

            try:
                self.session.query(Lot).filter_by(lot_id=lot_id).update(values)
                self.session.commit()

                if remainingTrigger:
                    self.afterUpdateCurrentLotRemaining(lot_id=lot_id)

                self.afterUpdateLot(lot_id)

                print("Se ha actualizado la información del lote " + str(lot_id) + " satisfactoriamente")
                return True
            except Exception as e:
                print("Ha ocurrido un error desconocido al intentar actualizar la información del lote " + str(lot_id), e)
                self.session.rollback()
                return False
        return False

    """
    Pseudo-trigger para actualizar la informacion de un producto enlazado a un lote modificado
     - No retorna nada
    """
    def afterUpdateLot(self, lot_id):
        product_id = self.session.query(Lot.product_id).filter_by(lot_id=lot_id).scalar()
        remaining = self.session.query(func.sum(Lot.remaining)).filter_by(product_id=product_id, available=True).scalar()
        remaining_lots = self.session.query(Lot).filter_by(product_id=product_id, available=True).count()

        if remaining == None: remaining = 0

        values = {"remaining" : remaining, "remaining_lots" : remaining_lots}

        if remaining == 0 and remaining_lots == 0: values["available"] = False

        self.session.query(Product).filter_by(product_id = product_id).update(values)

        try:
            self.session.commit()
            print("Se ha actualizado el producto")

        except Exception as e:
            self.session.rollback()
            print("No se pudo actualizar el producto")

    """
    Pseudo-trigger para calcular el nuevo lote current de un producto luego de haber realizado un update del remaining del current
     - No retorna nada
    """
    def afterUpdateCurrentLotRemaining(self, lot_id = None, product_id = None):
        if (lot_id or product_id) != None:

            if lot_id != None and product_id == None:
                product_id = self.session.query(Lot.product_id).filter_by(lot_id=lot_id).scalar()

            values = {"available" : False, "current" : False}
            remaining = self.session.query(Lot.remaining).filter_by(product_id=product_id, current=True).scalar()
            if remaining == 0:
                self.session.query(Lot).filter_by(product_id=product_id, current=True).update(values)

                try:
                    self.session.commit()

                    self.substractToRemainingLots(product_id)

                    if self.hasAvailableLot(product_id):
                        lot_id = self.session.query(Lot.lot_id).filter_by(product_id=product_id, available=True).scalar()
                        self.session.query(Lot).filter_by(lot_id=lot_id).update({"current" : True})
                        try:
                            self.session.commit()
                            print("Actualizado lote en afterUpdate correctamente")

                        except Exception as e:
                            self.session.rollback()
                            print("Ha ocurrido un error desconocido al intentar actualizar la información del lote " + str(lot_id), e)

                    print("Actualizado lote en afterUpdate correctamente")

                except Exception as e:
                    self.session.rollback()
                    print("Ha ocurrido un error desconocido al intentar actualizar la información del lote", e)

            elif remaining < 0:
                values["remaining"] = 0
                self.session.query(Lot).filter_by(product_id=product_id, current=True).update(values)

                try:
                    self.session.commit()

                    self.substractToRemainingLots(product_id)

                    if self.hasAvailableLot(product_id):
                        print("entre")
                        lot_id, lot_remaining = self.session.query(Lot.lot_id, Lot.remaining).filter_by(product_id=product_id, available=True).all()[0]
                        values = {"current" : True, "remaining" : lot_remaining + remaining}
                        print(remaining)
                        self.session.query(Lot).filter_by(lot_id=lot_id).update(values)

                        try:
                            self.session.commit()
                            self.afterUpdateCurrentLotRemaining(product_id=product_id)
                            print("Actualizado lote en afterUpdate correctamente")

                        except Exception as e:
                            self.session.rollback()
                            print("Ha ocurrido un error desconocido al intentar actualizar la información del lote " + str(lot_id), e)

                    print("Actualizado lote en afterUpdate correctamente")

                except Exception as e:
                    self.session.rollback()
                    print("Ha ocurrido un error desconocido al intentar actualizar la información del lote", e)

    """
    Método para retornar los lotes asociados a un producto
     - Retorna un queryset con los resultados de la búsqueda
    """
    def getLotsIDByProductID(self, product_id, available = True):
        values = {
            "product_id" : product_id,
            "available"  : available
        }

        query = self.session.query(Lot.lot_id).filter_by(**values).order_by(desc(Lot.adquisition_date)).all()
        lotIDs = []
        for ID in query:
            lotIDs.append(str(ID[0]))
        return lotIDs

    """
    Método para retornar los lotes asociados a un filtro
     - Retorna un queryset con los resultados de la búsqueda
    """
    def getLots(self, lot_id = None, product_id = None, provider_id = None, available = None):
        values = {}
        if lot_id != None: values["lot_id"] = lot_id
        if product_id != None: values["product_id"] = product_id
        if provider_id != None: values["provider_id"] = provider_id
        if available != None: values["available"] = available

        return self.session.query(Lot).filter_by(**values).all()

    """
    Método para eliminar lotes (Marcar como no disponible)
     - Retorna True:
        * Cuando logra marcar el lote como no disponible
     - Retorna False:
        * Cuando el lote no existe
        * Cuando NO logra marcar el lote como no disponible
    """
    def deleteLot(self, lot_id):
        if self.existLot(lot_id):
            current = self.session.query(Lot.current).filter_by(lot_id=lot_id).all()[0][0]

            if not current:
                self.session.query(Lot).filter_by(lot_id=lot_id).update({"available" : False})

                try:
                    self.session.commit()
                    self.afterUpdateLot(lot_id)
                    print("Se ha marcado el lote " + str(lot_id) + " como no disponible")
                    return True

                except Exception as e:
                    print("Ha ocurrido un error desconocido al intentar marcar el lote " + str(lot_id) + " como no disponible", e)
                    self.session.rollback()
                    return False

            else:
                self.session.query(Lot).filter_by(lot_id=lot_id).update({"remaining" : 0})
                try:
                    self.session.commit()
                    self.afterUpdateCurrentLotRemaining(lot_id=lot_id)
                    self.afterUpdateLot(lot_id)
                    print("Se ha marcado el lote " + str(lot_id) + " como no disponible")
                    return True

                except Exception as e:
                    print("Ha ocurrido un error desconocido al intentar marcar el lote " + str(lot_id) + " como no disponible", e)
                    self.session.rollback()
                    return False

        return False

    """
    Pseudo-Trigger para actualizar un producto luego de haber eliminado un lote del mismo
     - No retorna nada
    """
    def afterDeleteLot(self, lot_id):
        product_id, reaiming_in_lot = self.session.query(Lot.product_id, Lot.remaining).filter_by(lot_id=lot_id, available=True).all()[0]
        remaining, remaining_lots = self.session.query(Product.remaining, Product.remaining_lots).filter_by(product_id=product_id).all()[0]

        values = {
            "remaining"      : remaining-remaining_in_lot,
            "remaining_lots" : remaining_lots-1,
        }

        if remaining_lots-1 == 0: values["available"] = False

        for i in range(10):
            self.session.query(Product).filter_by(product_id = product_id).update(values)
            try:
                self.session.commit()
                print("Se ha actualizado el producto")
                break

            except Exception as e:
                self.session.rollback()
                print("No se pudo actualizar el producto")

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE SERVICIOS:
    #==============================================================================================================================================================================

    # Método para verificar que un servicio existe.
    # Retorna true cuando el servicio existe y false en caso contario
    def existService(self, service_id):
        count = self.session.query(Service).filter_by(service_id=service_id).count()
        if count == 0:
            print("El servicio con id " + str(service_id) + " NO existe")
            return False
        else:
            print("El servicio con id " + str(service_id) + " existe")
            return True

    # Método para buscar servicios.
    # Retorna queryset de los servicios que cumplan el filtro. Los bound son cerrados
    def getService(self, service_id=None, service_name=None, available=None, price_lower_bound=None, price_upper_bound=None):
        if service_id is None and service_name is None and available is None and price_lower_bound is None and price_upper_bound is None:
            return self.session.query(Service).all()

        filters = and_()
        if service_id is not None:
            filters = and_(filters, Service.service_id == service_id)

        if service_name is not None:
            filters = and_(filters, Service.service_name.ilike("%"+service_name+"%"))

        if available is not None:
            filters = and_(filters, Service.available == available)

        if price_lower_bound is not None:
            filters = and_(filters, Service.price >= price_lower_bound)

        if price_upper_bound is not None:
            filters = and_(filters, Service.price <= price_upper_bound)

        return self.session.query(Service).filter(*filters).all()


    # Método para crear un servicio nuevo
    # Retorna true cuando el servicio es creado satisfactoreamente y false cuando no se puede crear o cuando ya existia el servicio
    def createService(self, service_name, price, available=None, description=None, category=None):
        kwargs = {
            'service_name' : service_name,
            'price' : price,
        }

        if available is not None:
            kwargs['available'] = available

        if description is not None:
            kwargs['description'] = description

        if category is not None:
            kwargs['category'] = category

        newService = Service(**kwargs)
        self.session.add(newService)
        try:
            self.session.commit()
            print("Se ha creado correctamente el servicio " + str(newService))
            return True
        except Exception as e:
            print("Error al crear el servicio " + str(newService) +":", e)
            self.session.rollback()
            return False

    """
    Método para actualizar información de un servicio
     - Retorna True:
        * Cuando logra actualizar la información correctamente
     - Retorna False:
        * Cuando el servicioo no existe
        * Cuando no pudo actualizarse la infromación por alguna otra razón
    """
    def updateService(self, service_id, service_name=None, price=None, available=None, description=None, category=None):
        if self.existService(service_id):
            values = {}
            if service_name != None: values["service_name"] = service_name
            if price != None: values["price"] = price
            if available != None: values["available"] = available
            if description != None: values["description"] = description
            if category != None: values["category"] = category
            try:
                self.session.query(Service).filter(Service.service_id == service_id).update(values)
                self.session.commit()
                print("Se ha actualizado la información del servicio " + str(service_id) + " satisfactoriamente")
                return True
            except Exception as e:
                print("Ha ocurrido un error desconocido al intentar actualizar la información del servicio " + str(service_id), e)
                self.session.rollback()
                return False
        return False

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE CLIENTES:
    #==============================================================================================================================================================================

    '''
    Método para verificar que un cliente existe.
        - Retorna true cuando el cliente existe y false en caso contario
    '''
    def existClient(self, ci):
        count = self.session.query(Client).filter_by(ci=ci).count()
        if count == 0:
            print("El cliente con ci " + str(ci) + " NO existe")
            return False
        else:
            print("El cliente con ci " + str(ci) + " existe")
            return True

    '''
    Método para obtener las ci de TODOS los clientes
        - Retorna una lista con el ci de cada cliente
    '''
    def getClientsCI(self):
        query = self.session.query(Client.ci).all()
        clientsCI = []
        for ci in query:
            clientsCI.append(str(ci[0]))
        return sorted(clientsCI)

    '''
    Método para buscar clientes.
        - Retorna queryset de los clientes que cumplan el filtro
    '''
    def getClients(self, ci=None, firstname=None, lastname=None, indebted=None, limit=None, page=1):
        if ci is None and firstname is None and lastname is None and indebted is None and limit is None:
            return self.session.query(Client).order_by(desc(Client.last_seen)).all()

        filters = and_()
        if ci is not None:
            filters = and_(filters, Client.ci == ci)

        if firstname is not None:
            filters = and_(filters, Client.firstname.ilike("%"+firstname+"%"))

        if lastname is not None:
            filters = and_(filters, Client.lastname.ilike("%"+lastname+"%"))

        if indebted is not None:
            if indebted:
                filters = and_(filters, Client.debt > 0)

            else:
                filters = and_(filters, Client.debt == 0)

        query = self.session.query(Client).filter(*filters).order_by(desc(Client.last_seen))

        if limit != None:
            query = self.session.query(Client).filter(*filters).order_by(desc(Client.last_seen)).limit(limit).offset((page-1)*limit)

        return query.all()

    '''
    Método para contar clientes.
        - Retorna la cantidad de clientes.
    '''
    def getClientsCount(self, debt = None):
        if debt is None:
            return self.session.query(Client).count()

        filters = and_()
        if debt: filters = and_(filters, Client.balance < 0)
        else: filters = and_(filters, Client.balance >= 0)

        return self.session.query(Client).filter(*filters).count()

    '''
    Método para crear un cliente nuevo
        - Retorna true cuando el cliente es creado satisfactoreamente y false cuando no se puede crear o cuando ya existia el cliente
    '''
    def createClient(self, ci, firstname, lastname, phone=None, email=None, debt_permission=None, book_permission=None):
        if self.existClient(ci):
            return False

        kwargs = {
            'ci' : ci,
            'firstname' : firstname,
            'lastname' : lastname
        }

        if phone is not None:
            kwargs['phone'] = phone

        if email is not None:
            kwargs['email'] = email

        if debt_permission is not None:
            kwargs['debt_permission'] = debt_permission

        if book_permission is not None:
            kwargs['book_permission'] = book_permission

        newClient = Client(**kwargs)
        self.session.add(newClient)
        try:
            self.session.commit()
            print("Se ha creado correctamente el cliente " + str(newClient))
            return True
        except Exception as e:
            print("Error al crear el cliente " + str(newClient) +":", e)
            self.session.rollback()
            return False

    """
    Método para actualizar información de un cliente
     - Retorna True:
        * Cuando logra actualizar la información correctamente
     - Retorna False:
        * Cuando el cliente no existe
        * Cuando no pudo actualizarse la infromación por alguna otra razón
    """
    def updateClient(self, ciOriginal, ci=None, firstname=None, lastname=None, phone=None, email=None, debt_permission=None, book_permission=None, blocked=None, last_seen=None):
        if self.existClient(ciOriginal):
            values = {}
            if ci != None: values["ci"] = ci
            if firstname != None: values["firstname"] = firstname
            if lastname != None: values["lastname"] = lastname
            if phone != None: values["phone"] = phone
            if email != None: values["email"] = email
            if debt_permission != None: values["debt_permission"] = debt_permission
            if book_permission != None: values["book_permission"] = book_permission
            if blocked != None: values["blocked"] = blocked
            if last_seen != None: values["last_seen"] = last_seen
            try:
                self.session.query(Client).filter(Client.ci == ciOriginal).update(values)
                self.session.commit()
                print("Se ha actualizado la información del cliente " + str(ciOriginal) + " satisfactoriamente")
                return True
            except Exception as e:
                print("Ha ocurrido un error desconocido al intentar actualizar la información del cliente " + str(ciOriginal), e)
                self.session.rollback()
                return False
        return False

    """
    Método para añadir saldo al balance de un cliente
     - Retorna el saldo total resultante del cliente cuando logra añadir el saldo
     - Retorna None en caso contrario
    """
    def addToClientBalance(self, ci, amount):
        balance = self.session.query(Client.balance).filter_by(ci=ci).scalar()
        total = float(balance)+float(amount)
        self.session.query(Client).filter_by(ci=ci).update({"balance" : total})
        try:
            self.session.commit()
            print("Se ha actualizado correctamente el saldo del cliente")
            return total
        except Exception as e:
            self.session.rollback()
            print("No se pudo actualizar el saldo del cliente", e)
            return None

    """
    Método para restar saldo al balance de un cliente
     - Retorna el saldo total resultante del cliente cuando logra restar el saldo
     - Retorna None en caso contrario
    """
    def substractFromClientBalance(self, ci, amount, purchase_id = None):
        balance = self.session.query(Client.balance).filter_by(ci=ci).scalar()
        total = float(balance)-float(amount)
        if total >= 0:
            self.session.query(Client).filter_by(ci=ci).update({"balance" : total})
            try:
                self.session.commit()
                print("Se ha actualizado correctamente el saldo del cliente")
                return total
            except Exception as e:
                self.session.rollback()
                print("No se pudo actualizar el saldo del cliente", e)
                return None

        elif purchase_id != None:
            self.createDebt(purchase_id, amount)
            return balance

        else:
            return None

    """
    Método para refrescar la deuda de un cliente
    - Retorna el saldo total resultante del cliente cuando logra refrescar el saldo
    - Retorna None en caso contrario
    """
    def refreshClientDebt(self, ci):
        totalDebt = self.session.query(func.sum(Debt.amount))\
        .join(Purchase, Debt.purchase_id == Purchase.purchase_id)\
        .filter(Debt.pay_date == None, Purchase.ci == ci)\
        .scalar()

        totalIncrease = self.session.query(func.sum(Increase.amount))\
        .filter_by(ci=ci, pay_date=None)\
        .scalar()

        if totalDebt == None: totalDebt = 0
        if totalIncrease == None: totalIncrease = 0

        total= totalDebt + totalIncrease

        self.session.query(Client).filter_by(ci=ci).update({ "debt" : total})
        try:
            self.session.commit()
            print("Se ha actualizado correctamente la deuda del cliente")
            return total
        except Exception as e:
            self.session.rollback()
            print("No se pudo actualizar la deuda del cliente", e)
            return None

    """
    Método para hacer check in de un cliente
     - Retorna True:
        * Cuando logra hacer check in correctamente
     - Retorna False:
        * Cuando el cliente no existe
        * Cuando no pudo hacerse check in por alguna otra razón
    """
    def checkInClient(self, ci):
        return self.updateClient(ci, last_seen=datetime.now())

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE ORDENES DE COMPRAS (PURCHASE):
    #==============================================================================================================================================================================

    """
    Método para verificar que una compra existe.
     - Retorna True:
        * Cuando la compra existe
     - Retorna False:
        * Cuando la compra NO existe
    """
    def existPurchase(self, purchase_id, payed = False):
        count = self.session.query(Purchase).filter_by(purchase_id=purchase_id, payed=payed).count()
        if count == 0:
            print("La compra " + str(purchase_id) + " NO existe")
            return False
        else:
            print("La compra " + str(purchase_id) + " existe")
            return True

    """
    Método para crear una compra nueva
     - Retorna una cadena UUID:
        * Cuando la compra es creada satisfactoreamente
     - Retorna None:
        * Cuando no se puede crear
    """
    def createPurchase(self, ci, clerk):
        if self.existClient(ci) and self.existUser(clerk):
            kwargs = {"ci" : ci, "clerk" : clerk}
            newPurchase = Purchase(**kwargs)
            self.session.add(newPurchase)
            try:
                self.session.commit()
                self.checkInClient(ci)
                print("Se ha creado correctamente la compra")
                return str(newPurchase.purchase_id)
            except Exception as e:
                print("Error desconocido al intentar crear la compra", e)
                self.session.rollback()
                return None
        else:
            print("No se puede crear la compra porque NO existe el cliente o el vendedor")
            return None

    """
    Método para obtener la cédula del cliente asociado a una compra
     - Retorna la cédula del cliente que realizo la compra especificada
    """
    def getPurchaseCI(self, purchase_id):
        return self.session.query(Purchase.ci).filter_by(purchase_id=purchase_id).all()[0]

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE LISTAS DE PRODUCTOS:
    #==============================================================================================================================================================================

    """
    Método para verificar que una lista de productos existe
     - Retorna True:
        * Cuando la lista de productos existe
     - Retorna False:
        * Cuando la lista de productos NO existe
    """
    def existProductList(self, product_id, purchase_id):
        count = self.session.query(Product_list).filter_by(product_id=product_id, purchase_id=purchase_id).count()
        if count == 0:
            print("La lista de " + str(product_id) + "asociada a la compra " + str(purchase_id) + " NO existe")
            return False
        else:
            print("La lista de " + str(product_id) + "asociada a la compra " + str(purchase_id) + " existe")
            return True

    """
    Método para crear una lista de productos
     - Retorna True:
        * Cuando la lista de productos es creada satisfactoreamente
     - Retorna False:
        * Cuando no se puede crear
    """
    def createProductList(self, purchase_id, product_name, price, amount):
        product_name = product_name.title().strip()

        if self.existPurchase(purchase_id) and self.existProduct(product_name):
            product_id = self.getProductID(product_name)
            kwargs = {"purchase_id" : purchase_id, "product_id" : product_id, "price" : price, "amount" : amount}
            self.session.add(Product_list(**kwargs))
            try:
                self.session.commit()
                print("Se ha añadido correctamente la lista de productos a la compra")
                self.afterInsertProductList(purchase_id, price*amount, product_id, amount)
                return True
            except Exception as e:
                print("Error desconocido al intentar añadir la lista de productos a la compra", e)
                self.session.rollback()
                return False
        else:
            print("No se puede añadir la lista de productos porque NO existe la compra o el producto")
            return False

    """
    Pseudo-Trigger para agregar el costo de una lista de productos a la compra asociada
     - No retorna nada
    """
    def afterInsertProductList(self, purchase_id, subtotal, product_id, amount):
        # Actualizar costo de la compra
        total = self.session.query(Purchase.total).filter_by(purchase_id = purchase_id).scalar()
        for i in range(10):
            self.session.query(Purchase).filter_by(purchase_id = purchase_id).update({"total" : float(total)+float(subtotal)})
            try:
                self.session.commit()
                print("Se ha actualizado la compra correctamente")
                break

            except Exception as e:
                self.session.rollback()
                print("No se pudo actualizar la compra")

        # Descontar cantidad de productos vendidos en producto
        remaining = self.session.query(Product.remaining).filter_by(product_id=product_id).scalar()
        for i in range(10):
            self.session.query(Product).filter_by(product_id=product_id).update({"remaining" : remaining-amount})
            try:
                self.session.commit()
                print("Se ha actualizado el producto correctamente")
                break

            except Exception as e:
                self.session.rollback()
                print("No se pudo actualizar el producto")

        # Descontar cantidad de productos vendidos en el lote actual del producto
        remaining = self.session.query(Lot.remaining).filter_by(product_id=product_id, current=True).scalar()
        for i in range(10):
            self.session.query(Lot).filter_by(product_id=product_id, current=True).update({"remaining" : remaining-amount})

            try:
                self.session.commit()
                self.afterUpdateCurrentLotRemaining(product_id=product_id)
                print("Se ha actualizado el lote correctamente")
                break

            except Exception as e:
                self.session.rollback()
                print("No se pudo actualizar el lote", e)

    # Método para buscar ProductList.
    # Retorna queryset de los ProductList que cumplan el filtro
    def getProductList(self, purchase_id=None, product_name=None):
        if purchase_id is None  and product_name is None:
            return self.session.query(Product_list).all()

        kwargs = {}
        if purchase_id is not None and self.existPurchase(purchase_id):
            kwargs['purchase_id'] = purchase_id
        if product_name is not None:
            product_name = product_name.title().strip()
            if self.existProduct(product_name):
                kwargs['product_id'] = self.getProductID(product_name)

        # Diccionario Vacio
        if not kwargs:
            return []
        return self.session.query(Product_list).filter_by(**kwargs).all()

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE LISTAS DE SERVICIOS:
    #==============================================================================================================================================================================

    """
    Método para verificar que una lista de servicios existe
     - Retorna True:
        * Cuando la lista de servicios existe
     - Retorna False:
        * Cuando la lista de servicios NO existe
    """
    def existServiceList(self, service_id, purchase_id):
        count = self.session.query(Service_list).filter_by(service_id=service_id, purchase_id=purchase_id).count()
        if count == 0:
            print("La lista de " + str(service_id) + "asociada a la compra " + str(purchase_id) + " NO existe")
            return False
        else:
            print("La lista de " + str(service_id) + "asociada a la compra " + str(purchase_id) + " existe")
            return True

    """
    Método para crear una lista de servicios
     - Retorna True:
        * Cuando la lista de servicios es creada satisfactoreamente
     - Retorna False:
        * Cuando no se puede crear
    """
    def createServiceList(self, purchase_id, service_id, price, amount):
        if self.existPurchase(purchase_id) and self.existService(service_id):
            kwargs = {"purchase_id" : purchase_id, "service_id" : service_id, "price" : price, "amount" : amount}
            self.session.add(Service_list(**kwargs))
            try:
                self.session.commit()
                print("Se ha añadido correctamente la lista de servicios a la compra")
                self.afterInsertServiceList(purchase_id, price*amount)
                return True
            except Exception as e:
                print("Error desconocido al intentar añadir la lista de servicios a la compra", e)
                self.session.rollback()
                return False
        else:
            print("No se puede añadir la lista de servicios porque NO existe la compra o el producto")
            return False

    """
    Pseudo-Trigger para agregar el costo de una lista de servicios a la compra asociada
     - No retorna nada
    """
    def afterInsertServiceList(self, purchase_id, total_list):
        total = self.session.query(Purchase.total).filter_by(purchase_id = purchase_id).scalar()
        for i in range(10):
            self.session.query(Purchase).filter_by(purchase_id = purchase_id).update({"total" : total+total_list})
            try:
                self.session.commit()
                print("Se ha actualizado la compra correctamente")
                break

            except Exception as e:
                self.session.rollback()
                print("No se pudo actualizar la compra")

    # Método para buscar ServiceList.
    # Retorna queryset de los ServiceList que cumplan el filtro
    def getServiceList(self, purchase_id=None, service_id=None):
        if purchase_id is None  and service_id is None:
            return self.session.query(Service_list).all()

        kwargs = {}
        if purchase_id is not None and self.existPurchase(purchase_id):
            kwargs['purchase_id'] = purchase_id
        if service_id is not None and self.existService(service_id):
            kwargs['service_id'] = service_id

        # Diccionario Vacio
        if not kwargs:
            return []
        return self.session.query(Service_list).filter_by(**kwargs).all()

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE PAGOS (CHECKOUT):
    #==============================================================================================================================================================================

    """
    Método para crear un pago nuevo
     - Retorna una cadena UUID:
        * Cuando el pago es creado satisfactoreamente
     - Retorna None:
        * Cuando no se puede crear
    """
    def createCheckout(self, purchase_id, amount, with_balance = False):
        if self.existPurchase(purchase_id):
            kwargs = {"purchase_id" : purchase_id, "amount" : amount, "with_balance" : with_balance}
            newCheckout = Checkout(**kwargs)
            self.session.add(newCheckout)
            try:
                self.session.commit()
                print("Se ha creado correctamente el pago")

                if with_balance:
                    ci = self.getPurchaseCI(purchase_id)
                    self.substractFromClientBalance(ci, amount, purchase_id)

                self.afterInsertCheckout(purchase_id)
                return str(newCheckout.checkout_id)
            except Exception as e:
                print("Error desconocido al intentar crear el pago", e)
                self.session.rollback()
                return None
        else:
            print("No se puede crear el pago porque NO existe la compra")
            return None

    """
    Pseudo-Trigger para verificar que una compra fué cancelada y sumar el excedente al balance del usuario
     - No retorna nada
    """
    def afterInsertCheckout(self, purchase_id):
        checkout = self.session.query(func.sum(Checkout.amount)).filter_by(purchase_id=purchase_id).scalar()
        total = self.session.query(Purchase.total).filter_by(purchase_id=purchase_id).scalar()

        # Si la suma de los pagos es mayor al total de la compra
        if  total <= checkout:
            ci = self.session.query(Purchase.ci).filter_by(purchase_id=purchase_id).scalar()
            balance = self.session.query(Client.balance).filter_by(ci = ci).scalar()

            # Se marca la orden de compra como pagada
            for i in range(10):
                self.session.query(Purchase).filter_by(purchase_id = purchase_id).update({"payed" : True, "payed_date" : datetime.now()})
                try:
                    self.session.commit()
                    print("Se ha actualizado la compra correctamente")
                    break

                except Exception as e:
                    self.session.rollback()
                    print("No se pudo actualizar la compra")

            # Se le suma el exceso al balance del usuario
            for i in range(10):
                self.session.query(Client).filter_by(ci = ci).update({"balance" : balance+(checkout-total)})
                try:
                    self.session.commit()
                    print("Se ha actualizado la compra correctamente")
                    break

                except Exception as e:
                    self.session.rollback()
                    print("No se pudo actualizar la compra")

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE DEUDAS (DEBT):
    #==============================================================================================================================================================================

    """
    Método para crear una deuda nuevo
     - Retorna una cadena UUID:
        * Cuando la deuda es creado satisfactoreamente
     - Retorna None:
        * Cuando no se puede crear
    """
    def createDebt(self, purchase_id, amount):
        if self.existPurchase(purchase_id):
            kwargs = {"purchase_id" : purchase_id, "amount" : amount}
            newDebt = Debt(**kwargs)
            self.session.add(newDebt)
            try:
                self.session.commit()
                print("Se ha creado correctamente la deuda")
                self.afterInsertDebt(purchase_id)
                return str(newDebt.debt_id)
            except Exception as e:
                print("Error desconocido al intentar crear la deuda", e)
                self.session.rollback()
                return None
        else:
            print("No se puede crear la deuda porque NO existe la compra")
            return None

    """
    Pseudo-Trigger para actualizar el monto de la deuda de un cliente
     - No retorna nada
    """
    def afterInsertDebt(self, purchase_id):
        ci = self.session.query(Purchase.ci).filter_by(purchase_id=purchase_id).scalar()
        self.refreshClientDebt(ci)

    """
    Método para pagar una deuda
     - Retorna una cadena UUID:
        * Cuando la deuda es pagada satisfactoreamente
     - Retorna None:
        * Cuando no se puede pagar
    """
    def payDebt(self, debt_id):
        self.session.query(Debt).filter_by(debt_id=debt_id).update({ "pay_date" : datetime.now() })
        try:
            self.session.commit()
            print("Se ha pagado la deuda " + str(debt_id) + "satisfactoriamente")
            return True
        except Exception as e:
            self.session.rollback()
            print("No se pudo pagar la deuda " + str(debt_id), e)
            return False

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE INCREMENTO EN DEUDA (INCREASE):
    #==============================================================================================================================================================================

    """
    Método para crear un incremento nuevo
     - Retorna una cadena UUID:
        * Cuando el incremento es creado satisfactoreamente
     - Retorna None:
        * Cuando no se puede crear
    """
    def createIncrease(self, ci, amount):
        if self.existClient(ci):
            kwargs = {"ci" : ci, "amount" : amount}
            newIncrease = Increase(**kwargs)
            self.session.add(newIncrease)
            try:
                self.session.commit()
                print("Se ha creado correctamente el incremento")
                self.afterInsertIncrease(ci)
                return str(newIncrease.increase_id)
            except Exception as e:
                print("Error desconocido al intentar crear el incremento", e)
                self.session.rollback()
                return None
        else:
            print("No se puede crear el incremento porque NO existe el cliente")
            return None

    """
    Pseudo-Trigger para actualizar el monto de la deuda de un cliente
     - No retorna nada
    """
    def afterInsertIncrease(self, ci):
        self.refreshClientDebt(ci)

    """
    Método para pagar un incremento
     - Retorna una cadena UUID:
        * Cuando el incremento es pagada satisfactoreamente
     - Retorna None:
        * Cuando no se puede pagar
    """
    def payIncrease(self, increase_id):
        self.session.query(Increase).filter_by(increase_id=increase_id).update({ "pay_date" : datetime.now() })
        try:
            self.session.commit()
            print("Se ha pagado el incremento " + str(increase_id) + "satisfactoriamente")
            return True
        except Exception as e:
            self.session.rollback()
            print("No se pudo pagar el incremento " + str(increase_id), e)
            return False

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE TRANSFERENCIAS:
    #==============================================================================================================================================================================

    """
    Método para verificar que una transferencia existe
     - Retorna True:
        * Cuando la transferencia existe
     - Retorna False:
        * Cuando la transferencia NO existe
    """
    def existTransfer(self, bank, confirmation_code):
        bank = bank.title().strip()

        count = self.session.query(Transfer).filter_by(bank=bank, confirmation_code=confirmation_code).count()
        if count == 0:
            print("La transferencia desde el banco " + bank + " número " + confirmation_code + " NO existe")
            return False
        else:
            print("La transferencia desde el banco " + bank + " número " + confirmation_code + " existe")
            return True

    """
    Método para crear una transferencia nueva
     - Retorna True:
        * Cuando la transferencia es creada satisfactoreamente
     - Retorna False:
        * Cuando no se puede crear
    """
    def createTransfer(self, ci, clerk, amount, bank, confirmation_code, description):
        bank = bank.title().strip()

        if not self.existTransfer(bank, confirmation_code):
            kwargs = {"ci" : ci, "clerk" : clerk, "amount" : amount, "bank" : bank, "confirmation_code" : confirmation_code, "description" : description}
            self.session.add(Transfer(**kwargs))
            try:
                self.session.commit()
                print("Se ha registrado correctamente la transferencia")
                self.afterInsertTransfer(ci, amount)
                return True
            except Exception as e:
                print("Error desconocido al intentar registrar la transferencia", e)
                self.session.rollback()
                return False
        else:
            print("La transferencia ya está registrada")
            return False

    """
    Pseudo-Trigger para registrar el monto de una transferencia en el balnce del cliente que transfirió
     - No retorna nada
    """
    def afterInsertTransfer(self, ci, amount):
        # Sumar la cantidad al saldo del cliente
        balance = self.addToClientBalance(ci, amount)

        # Si no hubo errores
        if balance != None:
            # Se calculan todas las deudas sin pagar del cliente que sean menor o igual a lo que posee en su saldo
            debts = self.session.query(Debt.debt_id.label("debt_id"), Debt.amount.label("amount"))\
                .join(Purchase, Debt.purchase_id == Purchase.purchase_id)\
                .join(Client, Purchase.ci == Client.ci)\
                .filter(Debt.pay_date == None, Debt.amount <= balance, Client.ci == ci)\
                .order_by(Debt.amount)\
                .all()

            # Se pagan todas las deudas que se puedan
            for debt in debts:
                if balance == None: break
                elif debt.amount <= balance:
                    self.payDebt(debt.debt_id)                                  # Pagar deuda
                    self.refreshClientDebt(ci)                                  # Actualizar deuda del cliente
                    balance = self.substractFromClientBalance(ci, debt.amount)  # Actualizar saldo del cleinte

            # Si no hubo errores o y aun hay saldo
            if balance != None:
                # Se calculan todos los incrementos sin pagar del cliente que sean menor o igual a lo que posee en su saldo
                increases = self.session.query(Increase.increase_id, Increase.amount)\
                    .filter(Increase.pay_date == None, Increase.amount <= balance, Increase.ci == ci)\
                    .all()

                # Se pagan todas las deudas que se puedan
                for increase in increases:
                    if balance == None: break
                    elif increase.amount <= balance:
                        self.payIncrease(increase.increase_id)                          # Pagar incremento
                        self.refreshClientDebt(ci)                                      # Actualizar deuda del cliente
                        balance = self.substractFromClientBalance(ci, increase.amount)  # Actualizar saldo del cleinte

    # Método para buscar transferencias
    # Retorna queryset de las transferencias que cumplan el filtro
    def getTransfers(self, clerk = None, ci = None, limit = None, page = 1):
        if clerk is None and ci is None and limit is None:
            return self.session.query(Transfer).order_by(desc(Transfer.transfer_date)).all()

        kwargs = {}
        if clerk != None and self.existUser(clerk): kwargs['clerk'] = clerk
        if ci != None and self.existClient(ci): kwargs['ci'] = ci

        query = self.session.query(Transfer).filter_by(**kwargs).order_by(desc(Transfer.transfer_date))

        if limit != None:
            query = self.session.query(Transfer).filter_by(**kwargs).order_by(desc(Transfer.transfer_date)).limit(limit).offset((page-1)*limit)

        return query.all()

    '''
    Método para contar transferencias
        - Retorna la cantidad de transferencias que cumplan el filtro
    '''
    def getTransfersCount(self, clerk = None, ci = None):
        if clerk is None and ci is None:
            return self.session.query(Transfer).count()

        kwargs = {}
        if clerk != None and self.existUser(clerk): kwargs['clerk'] = clerk
        if ci != None and self.existClient(ci): kwargs['ci'] = ci

        return self.session.query(Transfer).filter_by(**kwargs).count()

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE DEPÓSITOS:
    #==============================================================================================================================================================================

    """
    Método para crear un depósito nuevo
     - Retorna True:
        * Cuando el depósito es creado satisfactoreamente
     - Retorna False:
        * Cuando no se puede crear
    """
    def createDeposit(self, ci, clerk, amount):
        kwargs = {"ci" : ci, "clerk" : clerk, "amount" : amount}
        self.session.add(Deposit(**kwargs))
        try:
            self.session.commit()
            print("Se ha registrado correctamente el depósito")
            self.afterInsertDeposit(ci, amount)
            return True
        except Exception as e:
            print("Error desconocido al intentar registrar el depósito", e)
            self.session.rollback()
            return False

    """
    Pseudo-Trigger para registrar el monto de una transferencia en el balnce del cliente que depositó
     - No retorna nada
    """
    def afterInsertDeposit(self, ci, amount):
        # Sumar la cantidad al saldo del cliente
        balance = self.addToClientBalance(ci, amount)

        # Si no hubo errores
        if balance != None:
            # Se calculan todas las deudas sin pagar del cliente que sean menor o igual a lo que posee en su saldo
            debts = self.session.query(Debt.debt_id.label("debt_id"), Debt.amount.label("amount"))\
                .join(Purchase, Debt.purchase_id == Purchase.purchase_id)\
                .join(Client, Purchase.ci == Client.ci)\
                .filter(Debt.pay_date == None, Debt.amount <= balance, Client.ci == ci)\
                .order_by(Debt.amount)\
                .all()

            # Se pagan todas las deudas que se puedan
            for debt in debts:
                if balance == None: break
                elif debt.amount <= balance:
                    self.payDebt(debt.debt_id)                                  # Pagar deuda
                    self.refreshClientDebt(ci)                                  # Actualizar deuda del cliente
                    balance = self.substractFromClientBalance(ci, debt.amount)  # Actualizar saldo del cleinte

            # Si no hubo errores o y aun hay saldo
            if balance != None:
                # Se calculan todos los incrementos sin pagar del cliente que sean menor o igual a lo que posee en su saldo
                increases = self.session.query(Increase.increase_id, Increase.amount)\
                    .filter(Increase.pay_date == None, Increase.amount <= balance, Increase.ci == ci)\
                    .all()

                # Se pagan todas las deudas que se puedan
                for increase in increases:
                    if balance == None: break
                    elif increase.amount <= balance:
                        self.payIncrease(increase.increase_id)                          # Pagar incremento
                        self.refreshClientDebt(ci)                                      # Actualizar deuda del cliente
                        balance = self.substractFromClientBalance(ci, increase.amount)  # Actualizar saldo del cleinte

    '''
    Método para buscar Depósitos
        - Retorna queryset de los depósitos que cumplan el filtro
    '''
    def getDeposits(self, clerk = None, ci = None, limit = None, page = 1):
        if clerk is None and ci is None and limit is None:
            return self.session.query(Deposit).order_by(desc(Deposit.deposit_date)).all()

        kwargs = {}
        if clerk != None and self.existUser(clerk): kwargs['clerk'] = clerk
        if ci != None and self.existClient(ci): kwargs['ci'] = ci

        query = self.session.query(Deposit).filter_by(**kwargs).order_by(desc(Deposit.deposit_date))

        if limit != None:
            query = self.session.query(Deposit).filter_by(**kwargs).order_by(desc(Deposit.deposit_date)).limit(limit).offset((page-1)*limit)

        return query.all()

    '''
    Método para contar Depósitos
        - Retorna la cantidad de depósitos que cumplan el filtro
    '''
    def getDepositsCount(self, clerk = None, ci = None):
        if clerk is None and ci is None:
            return self.session.query(Deposit).count()

        kwargs = {}
        if clerk != None and self.existUser(clerk): kwargs['clerk'] = clerk
        if ci != None and self.existClient(ci): kwargs['ci'] = ci

        return self.session.query(Deposit).filter_by(**kwargs).count()

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE REVERSE PRODUCT LIST:
    #==============================================================================================================================================================================

    """
    Método para verificar que existe una devolución de lista de productos
     - Retorna True:
        * Cuando la devolución de lista de productos existe
     - Retorna False:
        * Cuando la devolución de lista de productos NO existe
    """
    def existReverseProductList(self, product_id, purchase_id):
        count = self.session.query(Reverse_product_list).filter_by(product_id=product_id, purchase_id=purchase_id).count()
        if count == 0:
            print("La Devolucion de la lista de productos asociada al ID " + str((product_id, purchase_id)) + " NO existe")
            return False
        else:
            print("La Devolucion de la lista de productos asociada al ID " + str((product_id, purchase_id)) + " existe")
            return True

    """
    Método para crear una devolución de lista de productos
     - Retorna True:
        * Cuando la devolución de lista de productos es creada satisfactoreamente
     - Retorna False:
        * Cuando no se puede crear
    """
    def createReverseProductList(self, product_list, clerk_username, amount, cash=True, cash_amount=None, description=""):
        if not self.existProductList(product_list.product_id, product_list.purchase_id) \
            or not self.existUser(clerk_username) or self.existReverseProductList(product_list.product_id, product_list.purchase_id):
            return False

        if product_list.amount < amount:
            print("Error, No se puede devolver mas de lo que se vendio")
            return False

        if cash_amount is None:
            if cash:
                cash_amount = product_list.price * amount
            else:
                cash_amount = 0
        else:
            if cash_amount > product_list.price * product_list.amount:
                print("No se puede devolver mas dinero que el costo de todos los productos")
                return False

        kwargs = {
            'product_id'  : product_list.product_id,
            'purchase_id' : product_list.purchase_id,
            'clerk_id'    : clerk_username,
            'amount'      : amount,
            'cash'        : cash,
            'cash_amount' : cash_amount,
            'description' : description
        }
        new_reverse = Reverse_product_list(**kwargs)
        new_reverse.product_list = product_list
        self.session.add(new_reverse)

        try:
            self.session.commit()
            print("Se ha añadido correctamente la devolucion de la lista de productos a la compra")
            return True
        except Exception as e:
            print("Error desconocido al intentar añadir la devolucion de la lista de productos a la compra", e)
            self.session.rollback()
            return False

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE REVERSE SERVICE LIST:
    #==============================================================================================================================================================================

    """
    Método para verificar que existe una devolución de lista de servicios
     - Retorna True:
        * Cuando la devolución de lista de servicios existe
     - Retorna False:
        * Cuando la devolución de lista de servicios NO existe
    """
    def existReverseServiceList(self, service_id, purchase_id):
        count = self.session.query(Reverse_service_list).filter_by(service_id=service_id, purchase_id=purchase_id).count()
        if count == 0:
            print("La Devolucion de la lista de servicios asociada al ID " + str((service_id, purchase_id)) + " NO existe")
            return False
        else:
            print("La Devolucion de la lista de servicios asociada al ID " + str((service_id, purchase_id)) + " existe")
            return True

    """
    Método para crear una devolución de lista de productos
     - Retorna True:
        * Cuando la devolución de lista de productos es creada satisfactoreamente
     - Retorna False:
        * Cuando no se puede crear
    """
    def createReverseServiceList(self, service_list, clerk_username, amount, cash=True, cash_amount=None, description=""):
        if not self.existServiceList(service_list.service_id, service_list.purchase_id) \
            or not self.existUser(clerk_username) or self.existReverseServiceList(service_list.service_id, service_list.purchase_id):
            return False

        if service_list.amount < amount:
            print("Error, No se puede devolver mas de lo que se vendio")
            return False

        if cash_amount is None:
            if cash:
                cash_amount = service_list.price * amount
            else:
                cash_amount = 0
        else:
            if cash_amount > service_list.price * service_list.amount:
                print("No se puede devolver mas dinero que el costo de todos los servicios")
                return False

        kwargs = {
            'service_id' : service_list.service_id,
            'purchase_id' : service_list.purchase_id,
            'clerk_id' : clerk_username,
            'amount' : amount,
            'cash' : cash,
            'cash_amount' : cash_amount,
            'description' : description
        }
        new_reverse = Reverse_service_list(**kwargs)
        new_reverse.service_list = service_list
        self.session.add(new_reverse)

        try:
            self.session.commit()
            print("Se ha añadido correctamente la devolucion de la lista de servicios a la compra")
            return True
        except Exception as e:
            print("Error desconocido al intentar añadir la devolucion de la lista de servicios a la compra", e)
            self.session.rollback()
            return False

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DEL LOG DE OPERACIONES:
    #==============================================================================================================================================================================

    """
    Método para Obtener el ÚLTIMO inicio y fin de período de ventas (Generalmente un Trimestre)
     - Devuelve tupla donde el primer elemento marca el inicio y el segundo elemento marca el final
    """
    def getPeriodStartAndEnd(self):
        possible_period_start = self.session.query(Operation_log).filter_by(open_record=True, op_type=0).order_by(Operation_log.recorded.desc()).first()

        if possible_period_start is None:
            return (None, None)

        filters = and_(
                    Operation_log.recorded >= possible_period_start.recorded,
                    Operation_log.op_type == 0,
                    Operation_log.open_record == False
                )

        if_ended = self.session.query(Operation_log).filter(*filters).order_by(Operation_log.recorded.desc()).first()
        if if_ended is None:
            return (possible_period_start, None)
        else:
            return (possible_period_start, if_ended)

    """
    Método para saber si el perído está abierto
    """
    def isOpenPeriod(self):
        possible_period = self.getPeriodStartAndEnd()
        return possible_period[0] is not None and possible_period[1] is None

    """
    Método para Iniciar Perído
     - Devuelve True si se logró con éxito
     - Devuelve False en caso contrario
    """
    def startPeriod(self, clerk, starting_cash = 0, starting_total = 0, description=""):
        last_period = self.getPeriodStartAndEnd()

        # Estamos en un periodo abierto o no existe otro periodo
        if last_period[1] is None:
            # No existe otro periodo
            if last_period[0] is None:
                new_period = Operation_log(clerk=clerk, op_type=0, open_record=True, cash_total=starting_cash, total_money=starting_total, description=description)
                self.session.add(new_period)
                try:
                    self.session.commit()
                    print("Inicio de Periodo Exitoso")
                    print("Info:", new_period)
                    return True
                except Exception as e:
                    self.session.rollback()
                    print("Error Desconocido al Abrir Periodo")
                    print("Razon:", e)
                    return False

            # Periodo ya abierto
            else:
                print("Periodo ya abierto")
                print("Info:", last_period[0])
                return False
        # Esta cerrado el ultimo periodo
        else:
            new_period = Operation_log(clerk=clerk, op_type=0, open_record=True, cash_total=starting_cash, total_money=starting_total, description=description)
            self.session.add(new_period)
            try:
                self.session.commit()
                print("Inicio de Periodo Exitoso")
                print("Info:", new_period)
                return True
            except Exception as e:
                self.session.rollback()
                print("Error Desconocido al Abrir Periodo")
                print("Razon:", e)
                return False

    """
    Método para Obtener el ÚLTIMO inicio y fin de día de ventas del período
     - Devuelve tupla donde el primer elemento marca el inicio y el segundo elemento marca el final
    """
    def getDayStartAndEnd(self):
        period = self.getPeriodStartAndEnd()

        if period[0] is None or (period[0] is not None and period[1] is not None):
            return (None, None)


        filters = and_(
                    Operation_log.recorded >= period[0].recorded,
                    Operation_log.op_type == 1,
                    Operation_log.open_record == True
                )

        possible_day_start = self.session.query(Operation_log).filter(*filters).order_by(Operation_log.recorded.desc()).first()

        if possible_day_start is None:
            return (None, None)

        filters = and_(
                    Operation_log.recorded >= possible_day_start.recorded,
                    Operation_log.op_type == 1,
                    Operation_log.open_record == False
                )

        if_ended = self.session.query(Operation_log).filter(*filters).order_by(Operation_log.recorded.desc()).first()
        if if_ended is None:
            return (possible_day_start, None)
        else:
            return (possible_day_start, if_ended)

    """
    Método para saber si el día está abierto del período
    """
    def isOpenDay(self):
        possible_day = self.getDayStartAndEnd()
        return possible_day[0] is not None and possible_day[1] is None

    """
    Método para Iniciar Día.
     - Devuelve Tupla, donde la primera posicion marca si esta abierto el período y la segunda si se logró abrir el día
     - Devuelve tupla (True, True) si se logró con éxito
     - Devuelve (False, False), (True, False) en caso contrario
    """
    def startDay(self, clerk, starting_cash = 0, starting_total = 0, description=""):
        is_open_period = self.isOpenPeriod()

        if not is_open_period:
            print("No se puede abrir el dia si el periodo esta cerrado")
            return (False, False)


        last_day = self.getDayStartAndEnd()

        # Estamos en un dia abierto o no existe otro dia
        if last_day[1] is None:
            # No existe otro Dia
            if last_day[0] is None:
                new_day = Operation_log(clerk=clerk, op_type=1, open_record=True, cash_total=starting_cash, total_money=starting_total, description=description)
                self.session.add(new_day)
                try:
                    self.session.commit()
                    print("Inicio de Dia Exitoso")
                    print("Info:", new_day)
                    return (True, True)
                except Exception as e:
                    self.session.rollback()
                    print("Error Desconocido al Abrir Dia")
                    print("Razon:", e)
                    return (True, False)

            # Dia ya abierto
            else:
                print("Dia ya abierto")
                print("Info:", last_day[0])
                return (True, False)
        # Esta cerrado el ultimo Dia
        else:
            new_day = Operation_log(clerk=clerk, op_type=1, open_record=True, cash_total=starting_cash, total_money=starting_total, description=description)
            self.session.add(new_day)
            try:
                self.session.commit()
                print("Inicio de Dia Exitoso")
                print("Info:", new_day)
                return (True, True)
            except Exception as e:
                self.session.rollback()
                print("Error Desconocido al Abrir Dia")
                print("Razon:", e)
                return (True, False)

    """
    Método para Obtener el ÚLTIMO inicio y fin de turno de ventas del día
     - Devuelve tupla donde el primer elemento marca el inicio y el segundo elemento marca el final
    """
    def getTurnStartAndEnd(self):
        day = self.getDayStartAndEnd()

        if day[0] is None or (day[0] is not None and day[1] is not None):
            return (None, None)


        filters = and_(
                    Operation_log.recorded >= day[0].recorded,
                    Operation_log.op_type == 2,
                    Operation_log.open_record == True
                )

        possible_turn_start = self.session.query(Operation_log).filter(*filters).order_by(Operation_log.recorded.desc()).first()

        if possible_turn_start is None:
            return (None, None)

        filters = and_(
                    Operation_log.recorded >= possible_turn_start.recorded,
                    Operation_log.op_type == 2,
                    Operation_log.open_record == False
                )

        if_ended = self.session.query(Operation_log).filter(*filters).order_by(Operation_log.recorded.desc()).first()
        if if_ended is None:
            return (possible_turn_start, None)
        else:
            return (possible_turn_start, if_ended)

    """
    Método para saber si el turno está abierto del período
    """
    def isOpenTurn(self):
        possible_turn = self.getTurnStartAndEnd()
        return possible_turn[0] is not None and possible_turn[1] is None

    """
    Método para Iniciar Turno.
     - Devuelve Tupla, donde la primera posicion marca si esta abierto el día y la segunda si se logró abrir el turno
     - Devuelve tupla (True, True) si se logró con éxito
     - Devuelve (False, False), (True, False) en caso contrario
    """
    def startTurn(self, clerk, description=""):
        day = self.getDayStartAndEnd()

        if day[0] is None or (day[0] is not None and day[1] is not None):
            print("No se puede abrir el turno si el dia esta cerrado")
            return (False, False)


        last_turn = self.getTurnStartAndEnd()

        # Estamos en un turno abierto o no existe otro turno
        if last_turn[1] is None:
            # No existe otro turno
            if last_turn[0] is None:
                new_turn = Operation_log(clerk=clerk, op_type=2, open_record=True, cash_total=day[0].cash_total, total_money=day[0].total_money, description=description)
                self.session.add(new_turn)
                try:
                    self.session.commit()
                    print("Inicio de Turno Exitoso")
                    print("Info:", new_turn)
                    return (True, True)
                except Exception as e:
                    self.session.rollback()
                    print("Error Desconocido al Abrir Turno")
                    print("Razon:", e)
                    return (True, False)

            # Turno ya abierto
            else:
                print("Turno ya abierto")
                print("Info:", last_turn[0])
                return (True, False)
        # Esta cerrado el ultimo Turno
        else:
            new_turn = Operation_log(clerk=clerk, op_type=2, open_record=True, cash_total=last_turn[1].cash_total, total_money=last_turn[1].total_money, description=description)
            self.session.add(new_turn)
            try:
                self.session.commit()
                print("Inicio de Turno Exitoso")
                print("Info:", new_turn)
                return (True, True)
            except Exception as e:
                self.session.rollback()
                print("Error Desconocido al Abrir Turno")
                print("Razon:", e)
                return (True, False)

    """
    Método para agregar una entrada al sistema
     - Devuelve Tupla, donde la primera posicion marca si esta abierto el turno y la segunda si se crear la entrada
     - Devuelve tupla (True, True) si se logró con éxito
     - Devuelve (False, False), (True, False) en caso contrario
    """
    def createEntry(self, clerk, op_type, cash_balance, transfer_balance, cash_total, description=""):

        if 0 <= op_type and op_type <= 2:
            print("Las operaciones 0..2 estan reservadas")
            return (False, False)

        if not self.isOpenTurn():
            print("No se puede agregar una entrada al sistema si el turno esta cerrado")
            return (False, False)


        new_entry = Operation_log(clerk=clerk, op_type=op_type, transfer_balance=transfer_balance, cash_balance=cash_balance, cash_total=cash_total, total_money=0, description=description)
        self.session.add(new_entry)
        try:
            self.session.commit()
            print("Inicio de Turno Exitoso")
            print("Info:", new_entry)
            return (True, True)
        except Exception as e:
            self.session.rollback()
            print("Error Desconocido al Abrir Turno")
            print("Razon:", e)
            return (True, False)

    """
    Método para realizar un movimiento del tipo 3 (Ingreso)
     - Devuelve True si logra hacer el ingreso
     - Devuelve False si NO logra hacer el ingreso
    """
    def incomeOperation(self, clerk, cash_balance = 0, transfer_balance = 0, description=""):
        if cash_balance >= 0 and transfer_balance >= 0:
            if cash_balance > 0 or transfer_balance > 0:

                if cash_balance > 0: cash_total = cash_balance
                else: cash_total = transfer_balance

                kwargs = {
                    'clerk'            : clerk,
                    'op_type'          : 3,
                    'cash_balance'     : cash_balance,
                    'transfer_balance' : transfer_balance,
                    'cash_total'       : cash_total,
                    'description'      : description
                }

                self.createEntry(**kwargs)
                print("Se ha hecho el ingreso exitosamente")
                return True

            else:
                print("La cantidad a ingresar debe ser mayor a cero")
                return False

        else:
            print("No se puede ingresar una cantidad negativa")
            return False

    """
    Método para realizar un movimiento del tipo 4 (Egreso)
     - Devuelve True si logra hacer el egreso
     - Devuelve False si NO logra hacer el egreso
    """
    def expenditureOperation(self, clerk, cash_balance = 0, transfer_balance = 0, description=""):
        if cash_balance >= 0 and transfer_balance >= 0:
            if cash_balance > 0 or transfer_balance > 0:

                if cash_balance > 0: cash_total = cash_balance
                else: cash_total = transfer_balance

                kwargs = {
                    'clerk'            : clerk,
                    'op_type'          : 4,
                    'cash_balance'     : -cash_balance,
                    'transfer_balance' : -transfer_balance,
                    'cash_total'       : -cash_total,
                    'description'      : description
                }

                self.createEntry(**kwargs)
                print("Se ha hecho el egreso exitosamente")
                return True

            else:
                print("La cantidad a egresar debe ser mayor a cero")
                return False

        else:
            print("No se puede egresar una cantidad negativa")
            return False

    """
    Método para obtener todas las operaciones entre dos fechas (inclusivas)
     - Devuelve los query per se, no los objetos, en una tupla
     - La tupla tiene el siguiente orden:
       * Pagos en efectivo
       * Productos devueltos con efectivo devuelto
       * Servicios devueltos con efectivo devuelto
       * Transferencias
       * Todas las Operaciones en log
    """
    def _getOperations(self, lower_date=None, upper_date=None):

        lower_none = lower_date is None
        upper_none = upper_date is None
        both_none  = lower_none and upper_none


        if both_none:
            cash_checkouts = self.session.query(Checkout).filter_by(with_balance=False)
            product_reverse = self.session.query(Reverse_product_list).filter_by(cash=True)
            service_reverse = self.session.query(Reverse_service_list).filter_by(cash=True)
            transfers = self.session.query(Transfer)
            deposits = self.session.query(Deposit)
            log = self.session.query(Operation_log)
        else:
            filters_cash_checkouts = and_()
            filters_product_reverse = and_()
            filters_service_reverse = and_()
            filters_transfer = and_()
            filters_deposit = and_()
            filters_log = and_()

            if not lower_none:
                filters_cash_checkouts = and_(filters_cash_checkouts, Checkout.pay_date>=lower_date)
                filters_product_reverse = and_(filters_product_reverse, Reverse_product_list.reverse_date>=lower_date)
                filters_service_reverse = and_(filters_service_reverse, Reverse_service_list.reverse_date>=lower_date)
                filters_transfer = and_(filters_transfer, Transfer.transfer_date>=lower_date)
                filters_deposit = and_(filters_deposit, Deposit.deposit_date>=lower_date)
                filters_log = and_(filters_log, Operation_log.recorded>=lower_date)

            if not upper_none:
                filters_cash_checkouts = and_(filters_cash_checkouts, Checkout.pay_date<=upper_date)
                filters_product_reverse = and_(filters_product_reverse, Reverse_product_list.reverse_date<=upper_date)
                filters_service_reverse = and_(filters_service_reverse, Reverse_service_list.reverse_date<=upper_date)
                filters_transfer = and_(filters_transfer, Transfer.transfer_date<=upper_date)
                filters_deposit = and_(filters_deposit, Deposit.deposit_date<=upper_date)
                filters_log = and_(filters_log, Operation_log.recorded<=upper_date)

            filters_cash_checkouts = and_(filters_cash_checkouts, Checkout.with_balance==False)
            filters_product_reverse = and_(filters_product_reverse, Reverse_product_list.cash==True)
            filters_service_reverse = and_(filters_service_reverse, Reverse_service_list.cash==True)

            cash_checkouts = self.session.query(Checkout).filter(*filters_cash_checkouts)
            product_reverse = self.session.query(Reverse_product_list).filter(*filters_product_reverse)
            service_reverse = self.session.query(Reverse_service_list).filter(*filters_service_reverse)
            transfers = self.session.query(Transfer).filter(*filters_transfer)
            deposits = self.session.query(Deposit).filter(*filters_deposit)
            log = self.session.query(Operation_log).filter(*filters_log)

        return (cash_checkouts, product_reverse, service_reverse, transfers, deposits, log)

    """
    Método para obtener todas las operaciones entre dos fechas (inclusivas)
     - Devuelve los objetos en una tupla
     - La tupla tiene el siguiente orden:
       * Pagos en efectivo
       * Productos devueltos con efectivo devuelto
       * Servicios devueltos con efectivo devuelto
       * Transferencias
       * Todas las Operaciones en log
    """
    def getOperations(self, lower_date=None, upper_date=None):
        cash_checkouts, product_reverse, service_reverse, transfers, deposits, log = self._getOperations(lower_date, upper_date)
        return (cash_checkouts.all(), product_reverse.all(), service_reverse.all(), transfers.all(), deposits.all(), log.all())

    """
    Método que devuelve el balance entre dos fechas inclusivas
     - Devuelve Tupla donde le primer elemento es el balance de efectivo y el segundo elemento es el balance de transferencias
    """
    def getBalance(self, lower_date=None, upper_date=None):
        cash_checkouts, product_reverse, service_reverse, transfers, deposits, log = self._getOperations(lower_date=None, upper_date=None)

        cash_balance = 0

        cash_balance += noneToZero(cash_checkouts.with_entities(func.sum(Checkout.amount)).scalar())
        cash_balance -= noneToZero(product_reverse.with_entities(func.sum(Reverse_product_list.cash_amount)).scalar())
        cash_balance -= noneToZero(service_reverse.with_entities(func.sum(Reverse_service_list.cash_amount)).scalar())
        cash_balance += noneToZero(deposits.with_entities(func.sum(Deposit.amount)).scalar())
        cash_balance += noneToZero(log.with_entities(func.sum(Operation_log.cash_balance)).scalar())

        transfer_balance = 0
        transfer_balance += noneToZero(transfers.with_entities(func.sum(Transfer.amount)).scalar())
        transfer_balance += noneToZero(log.with_entities(func.sum(Operation_log.transfer_balance)).scalar())
        return (cash_balance, transfer_balance)

    """
    Método para cerrar turno
     - Devuelve True si hay cierre con éxito
     - False en caso contrario
    """
    def closeTurn(self, clerk, description=""):
        current_turn = self.getTurnStartAndEnd()

        if current_turn[0] is None or (current_turn[0] is not None and current_turn[1] is not None):
            print("No se puede Cerrar el turno si el turno esta cerrado")
            return False

        balance = self.getBalance(current_turn[0].recorded, None)

        new_end_turn = Operation_log(clerk=clerk, op_type=2, open_record=False, cash_total=current_turn[0].cash_total+balance[0], total_money=current_turn[0].total_money+balance[0]+balance[1], description=description)
        self.session.add(new_end_turn)
        try:
            self.session.commit()
            print("Cierre de Turno Exitoso")
            print("Info:", new_end_turn)
            return True
        except Exception as e:
            self.session.rollback()
            print("Error Desconocido al Cerrar Turno")
            print("Razon:", e)
            return False

    """
    Método para cerrar día
     - Devuelve True si hay cierre con éxito
     - False en caso contrario
    """
    def closeDay(self, clerk, description=""):
        current_day = self.getDayStartAndEnd()

        if current_day[0] is None or (current_day[0] is not None and current_day[1] is not None):
            print("No se puede Cerrar el Dia si el turno esta cerrado")
            return False

        balance = self.getBalance(current_day[0].recorded, None)

        new_end_day = Operation_log(clerk=clerk, op_type=1, open_record=False, cash_total=current_day[0].cash_total+balance[0], total_money=current_day[0].total_money+balance[0]+balance[1], description=description)
        self.session.add(new_end_day)
        try:
            self.session.commit()
            print("Cierre de Dia Exitoso")
            print("Info:", new_end_day)
            return True
        except Exception as e:
            self.session.rollback()
            print("Error Desconocido al Cerrar Dia")
            print("Razon:", e)
            return False

    """
    Método para cerrar Período
     - Devuelve True si hay cierre con éxito
     - False en caso contrario
    """
    def closePeriod(self, clerk, description=""):
        current_period = self.getPeriodStartAndEnd()

        if current_period[0] is None or (current_period[0] is not None and current_period[1] is not None):
            print("No se puede Cerrar el Periodo si el turno esta cerrado")
            return False

        balance = self.getBalance(current_period[0].recorded, None)

        new_end_period = Operation_log(clerk=clerk, op_type=0, open_record=False, cash_total=current_period[0].cash_total+balance[0], total_money=current_period[0].total_money+balance[0]+balance[1], description=description)
        self.session.add(new_end_period)
        try:
            self.session.commit()
            print("Cierre de Periodo Exitoso")
            print("Info:", new_end_period)
            return True
        except Exception as e:
            self.session.rollback()
            print("Error Desconocido al Cerrar Periodo")
            print("Razon:", e)
            return False

    """
    Método para obtener los movimientos de caja (ingresos, egresos, apertura y cierre de caja y periodo)
     - Retorna queryset con los movimientos que cumplan el filtro
    """
    def getMovements(self, limit = None, page = 1):
        if limit is None:
            return self.session.query(Operation_log).filter(Operation_log.op_type != 2).order_by(desc(Operation_log.recorded)).all()

        return self.session.query(Operation_log).filter(Operation_log.op_type != 2).order_by(desc(Operation_log.recorded)).limit(limit).offset((page-1)*limit).all()

    """
    Método para obtener la cantidad de movimientos de caja (ingresos, egresos, apertura y cierre de caja y periodo)
     - Retorna la cantidad de movimientos que cumplan el filtro
    """
    def getMovementsCount(self):
        return self.session.query(Operation_log).filter(Operation_log.op_type != 2).count()

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE MONEDAS / BILLETES PARA PAGO:
    #==============================================================================================================================================================================

    """
    Método para verificar que existe una Moneda / Billete en sistema
     - Retorna True:
        * Cuando la Moneda / Billete existe en sistema
     - Retorna False:
        * Cuando la Moneda / Billete NO existe en sistema
    """
    def existLegalTender(self, amount):
        count = self.session.query(Legal_tender).filter_by(amount=amount).count()
        if count == 0:
            print("La Moneda / Billete de " + str(amount) + " NO existe en sistema")
            return False
        else:
            print("La Moneda / Billete de " + str(amount) + " existe en sistema")
            return True

    """
    Método para buscar Monedas / Billetes en sistema.
     - Retorna queryset de los Legal_tender que cumplan el filtro
     - Si amount es pasado, no se toman en cuenta los bound
    """
    def getLegalTender(self, amount=None, lower_bound=None, upper_bound=None):
        if amount is None and lower_bound is None and upper_bound is None:
            return self.session.query(Legal_tender).order_by(desc(Legal_tender.amount)).all()

        if amount is not None:
            return self.session.query(Legal_tender).filter_by(amount=amount).order_by(desc(Legal_tender.amount)).all()

        filters = and_()
        if price_lower_bound is not None:
            filters = and_(filters, Legal_tender.amount >= lower_bound)

        if price_upper_bound is not None:
            filters = and_(filters, Legal_tender.amount <= upper_bound)

        return self.session.query(Legal_tender).filter(*filters).order_by(desc(Legal_tender.amount)).all()

    """
    Método para crea una Moneda / Billete en sistema
     - Retorna True:
        * Cuando la Moneda / Billete es creada en el sistema
     - Retorna False:
        * Cuando la Moneda / Billete NO es creada en el sistema
    """
    def createLegalTender(self, amount):
        if self.existLegalTender(amount):
            return False

        self.session.add(Legal_tender(amount=amount))
        try:
            self.session.commit()
            print("La Moneda / Billete de " + str(amount) + " fue creada")
            return True
        except Exception as e:
            print("Error desconocido al intentar crear La Moneda / Billete de " + str(amount) + ":", e)
            self.session.rollback()
            return False

    """
    Método para eliminar una Moneda / Billete en sistema
     - Retorna True:
        * Cuando la Moneda / Billete es eliminada del sistema
     - Retorna False:
        * Cuando la Moneda / Billete NO es eliminada del sistema
    """
    def deleteLegalTender(self, amount):
        obj_list = self.getLegalTender(amount=amount)

        if len(obj_list) == 0:
            print("La Moneda / Billete de " + str(amount) + " NO existe en sistema")
            return False

        self.session.delete(obj_list[0])
        try:
            self.session.commit()
            print("La Moneda / Billete de " + str(amount) + " fue eliminada")
            return True
        except Exception as e:
            print("Error desconocido al intentar eliminar La Moneda / Billete de " + str(amount) + ":", e)
            self.session.rollback()
            return False

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE LIBROS:
    #==============================================================================================================================================================================

    """
    Método para verificar la existencia de un libro.
        - Retorna True: Cuando el libro existe en el sistema.
        - Retorna False: Cuando el libro NO existe en el sistema.
    """
    def existBook(self,book_id):
        count = self.session.query(Book).filter_by(product_id=book_id).count()
        if count == 0:
            print("El libro asociado al ID " + str(book_id) + " NO existe")
            return False
        else:
            print("El libro asociado al ID " + str(book_id) + " existe")
            return True

    """
    Método para crear un libro
     - Retorna True:
        * Cuando el libro es creado satisfactoreamente.
     - Retorna False:
        * Cuando no se puede crear el libro o cuando el libro ya existe.
    """
    def createBook(self,book_id,title,edition,book_year,lang,isbn=None):
        if (self.existBook(book_id)):
            return False
        kwargs = {
            'book_id'   : book_id,
            'title'     : title,
            'edition'   : edition,
            'book_year' : book_year,
            'lang'      : lang
        }
        if isbn is not None:
            kwargs['isbn'] = isbn

        newBook = Book(**kwargs)
        self.session.add(newBook)
        try:
            self.session.commit()
            print("Se ha creado correctamente el libro " + title)
            return True
        except Exception as e:
            print("Error al crear el libro " + title +":", e)
            self.session.rollback()
            return False

    """
    Método para actualizar la información de un libro
        - Retorna True:
            Cuando la información del libro es actualizada exitosamente
        - Retorna False:
            Cuando el libro no existe u ocurrió un error actualizando la información
    """

    def updateBookInfo(self,oldID,newID=None,title=None,isbn=None,edition=None,book_year=None,lang=None,quantity=None,quantity_lent=None):
        kwargs = {}
        if newID is not None:
            kwargs['book_id'] = newID

        if title is not None:
            kwargs['title'] = title

        if isbn is not None:
            kwargs['isbn'] = isbn

        if edition is not None:
            kwargs['edition'] = edition

        if book_year is not None:
            kwargs['book_year'] = book_year

        if lang is not None:
            kwargs['lang'] = lang

        if quantity is not None:
            kwargs['quantity'] = quantity

        if quantity_lent is not None:
            kwargs['quantity_lent'] = quantity_lent

        try:
            self.session.query(Book).filter_by(book_id=oldID).update(kwargs)
            self.session.commit()
            if newID is not None:
                ID = newID
            else:
                ID = oldID
            print("Se ha actualizado la información del libro asociado al id " + ID + " satisfactoriamente")
            return True
        except Exception as e:
            print("Ha ocurrido un error desconocido al intentar actualizar la información del libro asociado al id " + oldID, e)
            self.session.rollback()
            return False
        return False

###################################################################################################################################################################################
## PRUEBAS:
###################################################################################################################################################################################

# Prueba
if __name__ == '__main__':
    m = dbManager("sistema_ventas", "hola", dropAll=True)
    m.createUser("Hola", "hola", "Naruto", "Uzumaki", "seventh.hokage@konoha.com", 3)

    kwargs = {
        "ci"              : 0,
        "firstname"       : "Anónimo",
        "lastname"        : "",
        "debt_permission" : False,
        "book_permission" : False
    }

    m.createClient(**kwargs)

    """print(m.getBalance())

    # Abrir turno antes de dia
    print("----------------------------------------------")
    print(m.isOpenTurn())
    print(m.getTurnStartAndEnd())
    print(m.startTurn("Hola", description="Prueba"))

    # Abrir dia antes de periodo
    print("----------------------------------------------")
    print(m.isOpenDay())
    print(m.getDayStartAndEnd())
    print(m.startDay("Hola", starting_cash=10, starting_total=20, description="Prueba"))

    # Abrir periodo
    print("----------------------------------------------")
    print(m.isOpenPeriod())
    print(m.getPeriodStartAndEnd())
    print(m.startPeriod("Hola", starting_cash=10, starting_total=20, description="Prueba"))

    # Mostrar que esta abierto periodo y que no se puede abrir otra vez
    print("----------------------------------------------")
    print(m.isOpenPeriod())
    print(m.getPeriodStartAndEnd())
    print(m.startPeriod("Hola", starting_cash=10, starting_total=20, description="Prueba"))

    # Mostrar que sigue abierto periodo
    print("----------------------------------------------")
    print(m.isOpenPeriod())
    print(m.getPeriodStartAndEnd())

    # Abrir dia
    print("----------------------------------------------")
    print(m.isOpenDay())
    print(m.getDayStartAndEnd())
    print(m.startDay("Hola", starting_cash=100, starting_total=200, description="Prueba"))

    # Mostrar que esta abierto dia y que no se puede abrir otra vez
    print("----------------------------------------------")
    print(m.isOpenDay())
    print(m.getDayStartAndEnd())
    print(m.startDay("Hola", starting_cash=10, starting_total=20, description="Prueba"))

    # Mostrar que sigue abierto dia
    print("----------------------------------------------")
    print(m.isOpenDay())
    print(m.getDayStartAndEnd())

    # Abrir turno
    print("----------------------------------------------")
    print(m.isOpenTurn())
    print(m.getTurnStartAndEnd())
    print(m.startTurn("Hola", description="Prueba"))

    # Mostrar que esta abierto turno y que no se puede abrir otra vez
    print("----------------------------------------------")
    print(m.isOpenTurn())
    print(m.getTurnStartAndEnd())
    print(m.startTurn("Hola", description="Prueba"))

    # Mostrar que sigue abierto turno
    print("----------------------------------------------")
    print(m.isOpenTurn())
    print(m.getTurnStartAndEnd())

    print("----------------------------------------------")
    print(m.closeTurn("Hola", description="Prueba"))
    print(m.isOpenTurn())

    print("----------------------------------------------")
    print(m.closeDay("Hola", description="Prueba"))
    print(m.isOpenDay())

    print("----------------------------------------------")
    print(m.closePeriod("Hola", description="Prueba"))
    print(m.isOpenPeriod())"""



    """
    m.deleteLegalTender(0)
    m.createLegalTender(0)
    m.createLegalTender(1)
    m.createLegalTender(2)
    print(m.getLegalTender())
    m.deleteLegalTender(1)
    print(m.getLegalTender())
    """
    """
    m.restore()
    m.deleteLastBackup()
    """

    """
    Insert Example
    user1 = User(username="saitama", password="xd", firstname="carlos", lastname="serrada", email="xd@gmail.com", permission_mask=2)
    m.session.add(user1)
    m.session.commit()
    """

    """
    Query Example
    query = m.session.query(func.count(distinct(User.username)))
    for i in query: print(i)
    """

    """
    l = Valid_language(lang_name="ES")
    m.session.add(l)
    try:
        m.session.commit()
    except Exception as e:
        print("Excepcion de Lenguaje:", e)
        m.session.rollback()

    try:
        b = m.session.query(Book).filter_by(title="Prueba", lang=l.lang_name).all()[0]
    except Exception as e:
        print("Excepcion de Libro:", e)
        import datetime
        b = Book(title="Prueba", book_year=datetime.now(), lang=l.lang_name)
        m.session.add(b)
        m.session.commit()

    s = Subject(subject_code="CI123", subject_name="Test")
    m.session.add(s)
    try:
        m.session.commit()
    except Exception as e:
        print("Excepcion de Materia:", e)
        m.session.rollback()
        s = m.session.query(Subject).filter_by(subject_code="CI123").all()[0]

    print("Soy b", b)
    s.books.append(b)
    m.session.commit()
    print("-----------------------------------")
    for book in s.books:
        print(book)

                for subjects in b.subjects:
                    print(subjects)
    """
    """Pruebas de los métodos para usuarios"""

    """
    # Probar createUser
    print("\nPrueba del método createUser\n")
    m.createUser("tobi", "loveurin", "obito", "uchiha", "tobi@akatsuki.com", 3)

    # Probar checkPassword
    print("\nPrueba del método checkPassword\n")
    m.checkPassword("tobi", "loveurin")

    # Probar changePassword
    print("\nPrueba del método changePassword\n")
    m.changePassword("tobi", "loveurin", "hateukakashi")
    print("")
    m.checkPassword("tobi", "loveurin")
    print("")
    m.checkPassword("tobi", "hateukakashi")

    # Probar updateUserProfile
    print("\nPrueba del método updateUserProfile\n")
    m.updateUserProfile("tobi", "xD")

    # Probar updateUserInfo
    print("\nPrueba del método updateUserInfo\n")
    m.updateUserInfo("tobi", "madara")
    m.updateUserInfo("tobi", lastname="uchiha")

    # Probar getUserNames
    print("\nPrueba del método getUserNames\n")
    print(m.getUserNames())

    # Probar getUserInfo
    print("\nPrueba del método getUserInfo\n")
    print(m.getUserInfo("tobi"))
    """

    """
    print("\nPrueba de Cliente y Busqueda\n")
    m.createClient(42, "Kurt", "Cobain")
    m.createClient(666, "Kurtis", "Cobain")
    print(m.getClients(ci=42))
    print(m.getClients(ci=43))
    print(m.getClients(firstname="kurt"))
    """

    """
    print("\nPrueba de Cliente y Update\n")
    m.createClient(777, "David", "Grohl")
    print(m.getClients(ci=777))
    m.updateClient(777, debt_permission=False)
    print(m.getClients(ci=777))
    m.checkInClient(777)
    print(m.getClients(ci=777))
    """



    """Pruebas de los métodos para productos"""
    """
    # Probar createProduct
    print("\nPrueba del método createProduct\n")
    m.createProduct("Agua", 1100)

    print(m.getProducts(product_name=True, product_id=True, active=True))
    """


    """Pruebas de los métodos para lotes"""
    """
    m.createUser("tobi", "loveurin", "obito", "uchiha", "tobi@akatsuki.com", 3)
    m.createProvider("kabuto", "xD")
    m.createLot("agua", "kabuto", "tobi", 20000, 42)

    m.createClient(777, "David", "Grohl")
    purchase = m.createPurchase(777, "tobi")
    m.createProductList(purchase, "agua", 1100, 2)
    m.createCheckout(purchase, 1000)
    m.createCheckout(purchase, 1200)

    print(m.getBalance())

    product_list_agua = m.getProductList(purchase, "agua")[0]
    print(product_list_agua)

    m.createReverseProductList(product_list_agua, "Hola", 2)
    print(product_list_agua.reversed_product_list)

    print(m.getBalance())
    """


    """
    m.createService("ExtraLifes", 1)
    print(m.getService(service_name="ExtraLifes"))
    m.createService("ExtraLifes*2", 2)
    print("------------")
    print(m.getService(service_name="ExtraLifes"))
    print("------------")
    print(m.getService(price_lower_bound=0))
    print("------------")
    print(m.getService(price_lower_bound=0, price_upper_bound=1))
    """

    """
    Ejemplo de los eventos inutiles de sqlalchemy
    def afterInsertCheckout(mapper, connection, target):
        print(target)
        print(connection)
        print(mapper)

        s = scoped_session(sessionmaker(bind=connection))
        print(s.query(User).all())

    event.listen(Checkout, 'after_insert', afterInsertCheckout)
    """

    #m.backup()
