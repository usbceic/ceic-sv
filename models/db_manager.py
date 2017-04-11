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
## DEPENDENCIAS:
###################################################################################################################################################################################

from models import *
from session import *

from db_backup import *
from sqlalchemy import func, distinct, update, event, and_, or_
from passlib.hash import bcrypt

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
        self.session = startSession(name, password, debug, dropAll)

        self.createUser("Hola", "hola", "Naruto", "Uzumaki", "seventh.hokage@konoha.com", 3)

    """
    Método de destrucción de la clase
     - Cierra la sesión con la base de datos
    """
    def __del__(self):
        try:
            self.session.close()
            print("Se ha cerrado correctamente la base de datos")
        except:
            print("La base de datos ya está cerrada")

    """
    Método para hacer backup a la Base de Datos
    """
    def backup(self):
        DBBackup(self.session).backup()

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
                m.session.rollback()
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
            hashedPass = self.session.query(User.password).filter_by(username=username).one()[0]
            if bcrypt.verify(password, hashedPass):
                print("Información de inicio de sesión válidada correctamente")
                return True
            else:
                print("La contraseña no corresponde al usuario especificado")
                return False
        return False

    """
    Método para iniciar sesión. Primero verifica la correspondencia entre username y contraseña con la base de datos y luego actualiza la fecha del último login
     - Retorna True:
        * Cuando los datos coinciden con los almacenados en la base de datos y se logra actualizar la fecha de último inicio de sesión del usuario
     - Retorna False:
        * Cuando el usuario NO existe
        * Cuando los datos NO coinciden con los almacenados en la base de datos
        * Cuando NO se logra actualizar la fecha de último inicio de sesión del usuario por alguna razón
    """
    def loginUser(self, username, password):
        if self.checkPassword(username, password):
            try:
                self.session.execute(update(User).where(User.username==username).values(last_login=datetime.datetime.now))
                self.session.commit()
                print("Se ha actualizado la fecha de último inicio de sesión para el usuario: " + username)
                return True
            except Exception as e:
                print("Ha ocurrido un error al intentar la fecha del último inicio de sesión para el usuario " + username, e)
                self.session.rollback()
                return False
        return False

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
    def updateUserRange(self, username, newRange):
        if self.existUser(username):
            if self.validRange(newRange):
                try:
                    self.session.execute(update(User).where(User.username==username).values(permission_mask=newRange))
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
        return self.session.query(User.username).all()

    """
    Método para obtener información de un usuario
     - Retorna un queryset con la información básica de un usuario
    """
    def getUserInfo(self, username):
        return self.session.query(User.firstname, User.lastname, User.email, User.profile, User.permission_mask, User.last_login).filter(User.username == username).one()

    """
    Método para obtener información de todos los usuarios
     - Retorna un queryset con la información básica de todos los usuarios
    """
    def getUsersInfo(self):
        return self.session.query(User.firstname, User.lastname, User.email, User.profile, User.permission_mask, User.last_login).all()

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE PROVEEDORES:
    #==============================================================================================================================================================================

    '''
    Metodo para verificar la existencia de un proveedor
    retorna True si existe
    retorna False si no existe
    '''
    def existProvider(self, provider_name):
        count = self.session.query(Provider).filter_by(provider_name=provider_name).count()
        if count == 0:
            print("El proveedor " + provider_name + " no existe")
            return False
        else:
            print("El proveedor " + provider_name + " ya existe")
            return True

    '''
    Metodo para agregar un proveedor
    Retorna True si el proveedor fue agregado con exito
    Retorna False cuando el proveedor ya existe
    Genera una excepcion cuando algo sale mal
    '''
    def createProvider(self, provider_name, pay_information = None, phone = None, email = None, description = None):
        if(self.existProvider(provider_name)):
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
    Metodo para obtener TODA la informacion de los proveedores existentes en la base de datos

        -Retorna un queryset con TODOS los proveedores
    '''
    def getAllProviders(self):
        return self.session.query(Provider).all()

    '''
    Metodo para obtener TODOS los nombres de los proveedores existentes en la base de datos en orden lexicografico.
        - Retorna un queryset con los nombres de todos los proveedores en orden lexicografico.
    '''

    def getAllProvidersByName(self):
        return self.session.query(Provider.provider_name).all().order_by(Provider.provider_name)

    '''
    Metodo para obtener TODOS los nombres de los proveedores existentes en la base de datos en orden de creación.
        - Retorna un queryset con los nombres de todos los proveedores en orden de creacion.
    '''

    def getAllProvidersByCreationDate(self):
        return self.session.query(Provider.provider_name).all().order_by(Provider.creation_date)

    '''
    Metodo para obtener TODOS los nombres de los proveedores ACTIVOS en la base de datos en orden lexicografico.
        - Retorna un queryset con los nombres de todos los proveedores en orden lexicografico.
    '''

    def getAllActiveProvidersByName(self):
        return self.session.query(Provider.provider_name).filter(Provider.active == True).order_by(Provider.provider_name)

    '''
    Metodo para obtener TODOS los nombres de los proveedores ACTIVOS en la base de datos en orden de creación.
        - Retorna un queryset con los nombres de todos los proveedores en orden de creacion.
    '''

    def getAllActiveProvidersByCreationDate(self):
        return self.session.query(Provider.provider_name).filter(Provider.active == True).order_by(Provider.creation_date)

    '''
    Metodo para obtener TODOS los nombres de los proveedores ACTIVOS en la base de datos en orden lexicografico.
        - Retorna un queryset con los nombres de todos los proveedores en orden lexicografico.
    '''

    def getAllActiveProvidersByName(self):
        return self.session.query(Provider.provider_name).filter(Provider.active == False).order_by(Provider.provider_name)

    '''
    Metodo para obtener TODOS los nombres de los proveedores ACTIVOS en la base de datos en orden de creación.
        - Retorna un queryset con los nombres de todos los proveedores en orden de creacion.
    '''

    def getAllActiveProvidersByCreationDate(self):
        return self.session.query(Provider.provider_name).filter(Provider.active == False).order_by(Provider.creation_date)

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
    def existProduct(self, product_name, active=True):
        count = self.session.query(Product).filter_by(product_name=product_name.lower().strip(), active=active).count()
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
     - Retorna False:
        * Cuando ya existe el producto
        * Cuando no se puede crear
    """
    def createProduct(self, product_name, price, category=""):
        if not self.existProduct(product_name):
            self.session.add(Product(product_name=product_name.lower().strip(), price=price, category=category))
            try:
                self.session.commit()
                print("Se ha creado correctamente el producto: " + product_name)
                return True
            except Exception as e:
                print("Error desconocido al crear el producto: " + product_name +":", e)
                m.session.rollback()
                return False
        else:
            print("No se puede crear el producto " + product_name + " porque ya existe")
            return False

    """
    Método para buscar un producto por su nombre o por su id
     - Retorna un queryset con el resultado de la búsqueda
    """
    def getProductByNameOrID(self, product_name=None, product_id=None, onlyAvailable=True):
        if product_name == None and product_id == None: return []
        if product_name != None and product_id != None:
            if onlyAvailable: return self.session.query(Product).filter_by(or_(product_name=product_name.lower().strip(), product_id=product_id), available=True).all()
            return self.session.query(Product).filter_by(or_(product_name=product_name.lower().strip(), product_id=product_id)).all()
        elif product_name != None:
            if onlyAvailable: return self.session.query(Product).filter_by(product_name=product_name.lower().strip(), available=True).all()
            return self.session.query(Product).filter_by(product_name=product_name.lower().strip()).all()
        else:
            if onlyAvailable: return self.session.query(Product).filter_by(product_id=product_id, available=True).all()
            return self.session.query(Product).filter_by(product_id=product_id).all()

    """
    Método para obtener el id de un producto especificando su nombre
     - Retorna el id correspondiente al producto de nombre especificado si este existe
     - Retorna None cuando no existe un producto con el nombre especificado
    """
    def getProductID(self, product_name):
        if self.existProduct(product_name): return self.session.query(Product.product_id).filter_by(product_name=product_name.lower().strip()).one()[0]
        else: return None

    """
    Método para obtener el nombre de cada producto
     - Retorna un queryset con lós resultados de la búsqueda
    """
    def getProductsNames(self, product_name, acitve=True):
        return self.session.query(Product.product_name).filter_by(active=active).all()

    """
    Método para obtener los atributos especificados de todos los productos que cumplan con el filtro especificado
     - Retorna un queryset con lós resultados de la búsqueda
    """
    def getProducts(self, product_id=None, product_name=None, price=None, remaining=None, remaining_lots=None, category=None, available=None, active=None):
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

        return self.session.query(*columns).filter_by(**filters).all()

    """
    Método para actualizar información de un producto
     - Retorna True:
        * Cuando logra actualizar la información correctamente
     - Retorna False:
        * Cuando el producto no existe
        * Cuando no pudo actualizarse la infromación por alguna otra razón
    """
    def updateProduct(self, product_name, new_product_name=None, price=None, category=None):
        if self.existProduct(product_name):
            values = {}
            if new_product_name != None: values["product_name"] = new_product_name.lower().strip()
            if price != None: values["price"] = price
            if category != None: values["category"] = category
            try:
                self.session.query(Product).filter_by(product_name=product_name.lower().strip()).update(values)
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
        if existProduct(product_name):
            try:
                self.session.execute(update(Product).where(Product.product_name==product_name.lower().strip()).values(active=False))
                self.session.commit()
                print("Se ha desactivado el producto: " + product_name)
                return True
            except Exception as e:
                print("Ha ocurrido un error desconocido al intentar desactivar el producto: " + product_name, e)
                self.session.rollback()
                return False
        return False

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
            print("El lote " + lot_id + " NO existe")
            return False
        else:
            print("El lote " + lot_id + " existe")
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

            count = self.session.query(Lot).filter_by(product_id=product_id, current=True).count()
            if count == 0: kwargs["current"] = True

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
        product_id, quantity = self.session.query(Lot.product_id, Lot.quantity).filter_by(lot_id=lot_id, available=True).one()
        remaining, remaining_lots = self.session.query(Product.remaining, Product.remaining_lots).filter_by(product_id=product_id).one()

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
            if product_name != None and self.existProduct(product_name): values["product_id"] = self.getProductID(product_name)
            if provider_id != None and self.existProvider(provider_id): values["provider_id"] = provider_id
            if cost != None: values["cost"] = cost
            if quantity != None: values["quantity"] = quantity
            if remaining != None and remaining <= quantity: values["remaining"] = remaining
            if expiration_date != None: values["expiration_date"] = expiration_date
            try:
                self.session.query(Lot).filter_by(lot_id=lot_id).update(values)
                self.session.commit()
                print("Se ha actualizado la información del lote " + lot_id + " satisfactoriamente")
                return True
            except Exception as e:
                print("Ha ocurrido un error desconocido al intentar actualizar la información del lote " + lot_id, e)
                self.session.rollback()
                return False
        return False

    """
    Método para retornar los lotes asociados a un producto
     - Retorna un queryset con los resultados de la búsqueda
    """
    def getLotsByProductID(self, product_id, onlyAvailables = True):
        if onlyAvailables: return self.session.query(Lot).filter_by(product_id=product_id, onlyAvailables=True).all()
        return self.session.query(Lot).filter_by(product_id=product_id).all()

    """
    Método para eliminar lotes (Marcar como no disponible)
     - Retorna True:
        * Cuando logra marcar el lote como no disponible
     - Retorna False:
        * Cuando el lote no existe
        * Cuando NO logra marcar el lote como no disponible
    """
    def deleteLot(self, lot_id):
        if existLot(lot_id):
            try:
                self.session.execute(update(Lot).where(Lot.lot_id==lot_id).values(available=False))
                self.session.commit()
                print("Se ha marcado el lote " + lot_id + " como no disponible")
                return True
            except Exception as e:
                print("Ha ocurrido un error desconocido al intentar marcar el lote " + lot_id + " como no disponible", e)
                self.session.rollback()
                return False
        return False

    """
    Pseudo-Trigger para actualizar un producto luego de haber eliminado un lote del mismo
     - No retorna nada
    """
    def afterDeleteLot(self, lot_id):
        product_id, reaiming_in_lot = self.session.query(Lot.product_id, Lot.remaining).filter_by(lot_id=lot_id, available=True).one()
        remaining, remaining_lots = self.session.query(Product.remaining, Product.remaining_lots).filter_by(product_id=product_id).one()

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

    # Método para verificar que un cliente existe.
    # Retorna true cuando el cliente existe y false en caso contario
    def existClient(self, ci):
        count = self.session.query(Client).filter_by(ci=ci).count()
        if count == 0:
            print("El cliente con ci " + str(ci) + " NO existe")
            return False
        else:
            print("El cliente con ci " + str(ci) + " existe")
            return True

    # Método para buscar clientes.
    # Retorna queryset de los clientes que cumplan el filtro
    def getClient(self, ci=None, firstname=None, lastname=None):
        if ci is None and firstname is None and lastname is None:
            return self.session.query(Client).all()

        filters = and_()
        if ci is not None:
            filters = and_(filters, Client.ci == ci)

        if firstname is not None:
            filters = and_(filters, Client.firstname.ilike("%"+firstname+"%"))

        if lastname is not None:
            filters = and_(filters, Client.lastname.ilike("%"+lastname+"%"))

        return self.session.query(Client).filter(*filters).all()


    # Método para crear un cliente nuevo
    # Retorna true cuando el cliente es creado satisfactoreamente y false cuando no se puede crear o cuando ya existia el cliente
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
    Método para hacer check in de un cliente
     - Retorna True:
        * Cuando logra hacer check in correctamente
     - Retorna False:
        * Cuando el cliente no existe
        * Cuando no pudo hacerse check in por alguna otra razón
    """
    def checkInClient(self, ci):
        return self.updateClient(ci, last_seen=datetime.datetime.now())

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
            print("La compra " + purchase_id + " NO existe")
            return False
        else:
            print("La compra " + purchase_id + " existe")
            return True

    """
    Método para crear una compra nueva
     - Retorna una cadena UUID:
        * Cuando la compra es creada satisfactoreamente
     - Retorna None:
        * Cuando no se puede crear
    """
    def createPurchase(self, ci, clerk, debt = False):
        if self.existClient(ci) and self.existUser(clerk):
            kwargs = {"ci" : ci, "clerk" : clerk, "debt" : debt}
            newPurchase = Purchase(**kwargs)
            self.session.add(newPurchase)
            try:
                self.session.commit()
                print("Se ha creado correctamente la compra")
                return str(newPurchase.purchase_id)
            except Exception as e:
                print("Error desconocido al intentar crear la compra", e)
                m.session.rollback()
                return None
        else:
            print("No se puede crear la compra porque NO existe el cliente o el vendedor")
            return None


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
            print("La lista de " + product_id + "asociada a la compra " + purchase_id + " NO existe")
            return False
        else:
            print("La lista de " + product_id + "asociada a la compra " + purchase_id + " existe")
            return True

    """
    Método para crear una lista de productos
     - Retorna True:
        * Cuando la lista de productos es creada satisfactoreamente
     - Retorna False:
        * Cuando no se puede crear
    """
    def createProductList(self, purchase_id, product_name, price, amount):
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
                m.session.rollback()
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
            self.session.query(Purchase).filter_by(purchase_id = purchase_id).update({"total" : total+subtotal})
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
                print("Se ha actualizado el lote correctamente")
                # Falta afterUpdateLotRemaining -- IMPORTANTE!
                break

            except Exception as e:
                self.session.rollback()
                print("No se pudo actualizar el lote")

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
            print("La lista de " + service_id + "asociada a la compra " + purchase_id + " NO existe")
            return False
        else:
            print("La lista de " + service_id + "asociada a la compra " + purchase_id + " existe")
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
                m.session.rollback()
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
                self.afterInsertCheckout(purchase_id)
                return str(newCheckout.checkout_id)
            except Exception as e:
                print("Error desconocido al intentar crear el pago", e)
                m.session.rollback()
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
                self.session.query(Purchase).filter_by(purchase_id = purchase_id).update({"payed" : True, "payed_date" : datetime.datetime.now()})
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
    # MÉTODOS PARA EL CONTROL DE TRANSFERENCIAS:
    #==============================================================================================================================================================================

    """
    Método para verificar que una lista de servicios existe
     - Retorna True:
        * Cuando la lista de servicios existe
     - Retorna False:
        * Cuando la lista de servicios NO existe
    """
    def existTransfer(self, bank, confirmation_code):
        count = self.session.query(Transfer).filter_by(bank=bank, confirmation_code=confirmation_code).count()
        if count == 0:
            print("La lista de " + bank + "asociada a la compra " + confirmation_code + " NO existe")
            return False
        else:
            print("La lista de " + bank + "asociada a la compra " + confirmation_code + " existe")
            return True

    """
    Método para crear una transferencia nueva
     - Retorna True:
        * Cuando la transferencia es creada satisfactoreamente
     - Retorna False:
        * Cuando no se puede crear
    """
    def createTransfer(self, ci, clerk, amount, bank, confirmation_code, description):
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
                m.session.rollback()
                return False
        else:
            print("La transferencia ya está registrada")
            return False

    """
    Pseudo-Trigger para registrar el monto de una transferencia en el balnce del cliente que transfirió
     - No retorna nada
    """
    def afterInsertTransfer(self, ci, amount):
        balance = self.session.query(Client.balance).filter_by(ci=ci).scalar()
        for i in range(10):
            self.session.query(Client).filter_by(ci=ci).update({"balance" : balance+amount})
            try:
                self.session.commit()
                print("Se ha actualizado correctamente el saldo del cliente")
                break
            except Exception as e:
                self.session.rollback()
                print("No se pudo actualizar el saldo del cliente", e)

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE REVERSE PRODUCT LIST:
    #==============================================================================================================================================================================

    # Completar

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DE REVERSE SERVICE LIST:
    #==============================================================================================================================================================================

    # Completar

    #==============================================================================================================================================================================
    # MÉTODOS PARA EL CONTROL DEL LOG DE OPERACIONES:
    #==============================================================================================================================================================================

    # Completar

###################################################################################################################################################################################
## PRUEBAS:
###################################################################################################################################################################################

# Prueba
if __name__ == '__main__':
    m = dbManager("sistema_ventas", "hola")

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
        b = m.session.query(Book).filter_by(title="Prueba", lang=l.lang_name).one()
    except Exception as e:
        print("Excepcion de Libro:", e)
        import datetime
        b = Book(title="Prueba", book_year=datetime.datetime.now(), lang=l.lang_name)
        m.session.add(b)
        m.session.commit()

    s = Subject(subject_code="CI123", subject_name="Test")
    m.session.add(s)
    try:
        m.session.commit()
    except Exception as e:
        print("Excepcion de Materia:", e)
        m.session.rollback()
        s = m.session.query(Subject).filter_by(subject_code="CI123").one()

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
    print(m.getClient(ci=42))
    print(m.getClient(ci=43))
    print(m.getClient(firstname="kurt"))
    """
    """
    print("\nPrueba de Cliente y Update\n")
    m.createClient(777, "David", "Grohl")
    print(m.getClient(ci=777))
    m.updateClient(777, debt_permission=False)
    print(m.getClient(ci=777))
    m.checkInClient(777)
    print(m.getClient(ci=777))
    """

    """Pruebas de los métodos para productos"""

    # Probar createProduct
    print("\nPrueba del método createProduct\n")
    m.createProduct("Agua", 1100)

    print(m.getProducts(product_name=True, product_id=True, active=True))

    """Pruebas de los métodos para lotes"""
    m.createUser("tobi", "loveurin", "obito", "uchiha", "tobi@akatsuki.com", 3)
    m.createProvider("kabuto", "xD")
    m.createLot("agua", "kabuto", "tobi", 20000, 42)

    m.createClient(777, "David", "Grohl")
    purchase = m.createPurchase(777, "tobi")
    m.createProductList(purchase, "agua", 1100, 2)
    m.createCheckout(purchase, 1000)
    m.createCheckout(purchase, 1200)

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

    m.backup()
