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
from session import startSession
from sqlalchemy import func, distinct, update
from passlib.hash import bcrypt

###################################################################################################################################################################################
## DECLARACIÓN DEL MANEJADOR:
###################################################################################################################################################################################

class DBManager(object):
    """docstring for DBManager"""
    def __init__(self, name, password, debug=False):
        super(DBManager, self).__init__()
        self.session = startSession(name, password, debug)

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS PARA EL CONTROL DE USUARIOS:
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    """
    Método para verificar que un usuario existe.
     - Retorna True:
        * Cuando el usuario existe
     - Retorna False:
        * Cuando el usuario NO existe
    """
    def userExist(self, username):
        count = self.session.query(User).filter_by(username=username).count()
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
        if not self.userExist(username):
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
    Método para verificar correspondencia entre usuario y contraseña
     - Retorna True:
        * Cuando los datos coinciden con los almacenados en la base de datos
     - Retorna False:
        * Cuando el usuario no existe
        * Cuando los datos NO coinciden con los almacenados en la base de datos
    """
    def checkPassword(self, username, password):
        if self.userExist(username):
            hashedPass = self.session.query(User.password).filter_by(username=username).one()[0]
            if bcrypt.verify(password, hashedPass):
                print("Información de inicio de sesión válidada correctamente")
                return True
            else:
                print("La contraseña no corresponde al usuario especificado")
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
        if self.userExist(username):
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
    Método para actualizar información de un usuario
     - Retorna True:
        * Cuando logra actualizar la información correctamente
     - Retorna False:
        * Cuando el usuario no existe
        * Cuando no pudo actualizarse la infromación por alguna otra razón
    """
    def updateUserInfo(self, username, firstname=None, lastname=None, email=None, description=None):
        if self.userExist(username):
            values = {}
            if firstname != None: values["firstname"] = firstname
            if lastname != None: values["lastname"] = lastname
            if email != None: values["email"] = email
            if description != None: values["description"] = description
            try:
                self.session.query(User).filter(User.username == username).update(values)
                self.session.commit()
                print("Se ha actualizado la información del ususario " + username + "satisfactoriamente")
                return True
            except Exception as e:
                print("Ha ocurrido un error desconocido al intentar actualizar la información del usuario " + username, e)
                self.session.rollback()
                return False
        return False

###################################################################################################################################################################################
## PRUEBAS:
###################################################################################################################################################################################

# Prueba
if __name__ == '__main__':
    m = DBManager("sistema_ventas", "hola", True)

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
    m.updateUserInfo("tobi", lastname="otsutsuki", description="dios ninja")