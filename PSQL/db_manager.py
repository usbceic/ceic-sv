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
from sqlalchemy import func, distinct, and_
from passlib.hash import bcrypt

###################################################################################################################################################################################
## DECLARACIÓN DEL MANEJADOR:
###################################################################################################################################################################################

class DBManager(object):
    """docstring for DBManager"""
    def __init__(self, name, password, debug=False):
        super(DBManager, self).__init__()
        self.session = startSession(name, password, debug)

        """
        Insert Example
        user1 = User(username="saitama", password="xd", firstname="carlos", lastname="serrada", email="xd@gmail.com", permission_mask=2)
        self.session.add(user1)
        self.session.commit()
        """

        """
        Query Example
        query = self.session.query(func.count(distinct(User.username)))
        for i in query: print(i)
        """

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS PARA EL CONTROL DE USUARIOS:
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para verificar que un usuario existe.
    # Retorna true cuando el usuario existe y false en caso contario
    def userExist(self, username):
        count = self.session.query(User).filter_by(username=username).count()
        if count == 0:
            print("El usuario " + username + " NO existe")
            return False
        else:
            print("El usuario " + username + " existe")
            return True

    # Método para crear un usuario nuevo
    # Retorna true cuando el usuario es creado satisfactoreamente y false cuando no se puede crear o cuando ya existia el usuario
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

    # Método para verificar correspondencia entre usuario y contraseña
    # Retorna true cuando los datos coinciden con los almacenados en la base de datos y retorna false cuando no coinciden o cuando el usuario no existe
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

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS PARA EL CONTROL DE CLIENTES:
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para verificar que un cliente existe.
    # Retorna true cuando el cliente existe y false en caso contario
    def clientExist(self, ci):
        count = self.session.query(Client).filter_by(ci=ci).count()
        if count == 0:
            print("El cliente con ci " + str(ci) + " NO existe")
            return False
        else:
            print("El cliente con ci " + str(ci) + " existe")
            return True

    # Método para buscar clientes.
    # Retorna queryset de los clientes que cumplan el filtro
    def clientSearch(self, ci=None, firstname=None, lastname=None):
        if ci is None and firstname is None and lastname is None:
            return []

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
    def clientCreate(self, ci, firstname, lastname, carnet=None, phone=None, debt_permission=None, book_permission=None):
        if self.clientExist(ci):
            return False

        kwargs = {
            'ci' : ci,
            'firstname' : firstname,
            'lastname' : lastname
        }

        if carnet is not None:
            kwargs['carnet'] = carnet

        if phone is not None:
            kwargs['phone'] = phone

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
            m.session.rollback()
            return False



###################################################################################################################################################################################
## PRUEBAS:
###################################################################################################################################################################################

# Prueba
if __name__ == '__main__':
    m = DBManager("sistema_ventas", "hola", True)
    l = Valid_language(lang_name="ES")
    """m.session.add(l)
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
        m.session.commit()"""

    m.createUser("tobi", "loveurin", "obito", "uchiha", "tobi@akatsuki.com", 3)
    m.checkPassword("tobi", "loveurin")

    """s = Subject(subject_code="CI123", subject_name="Test")
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
        print(subjects)"""

    m.clientCreate(42, "Kurt", "Cobain")
    m.clientCreate(666, "Kurtis", "Cobain", carnet="12345")
    print(m.clientSearch(ci=42))
    print(m.clientSearch(ci=43))
    print(m.clientSearch(firstname="kurt"))

