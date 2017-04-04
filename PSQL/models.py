# Tablas de Db
import sys
import datetime

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, String, DateTime, Date, ForeignKey

this = sys.modules[__name__]
this.Base = declarative_base()

# Tabla de usuarios
class User(this.Base):
    # Nombre
    __tablename__ = 'users'

    # Atributos
    username        = Column(String, primary_key=True)
    password        = Column(String, nullable=False)
    firstname       = Column(String, nullable=False)
    lastname        = Column(String, nullable=False)
    email           = Column(String, nullable=False)
    permission_mask = Column(Integer, nullable=False)
    profile         = Column(String, default="")
    description     = Column(String, default="")
    creation_date   = Column(DateTime, nullable=False, default=datetime.datetime.now())
    last_login      = Column(DateTime, nullable=False, default=datetime.datetime.now())

    # Relaciones
    lot  = relationship("lot")

    def __repr__(self):
       return "<User(username='%s', password='%s',  firstname='%s', lastname='%s', email=='%s', creation_date=='%s', last_login=='%s')>" % (
                            self.username,
                            self.password,
                            self.firstname,
                            self.lastname,
                            self.email,
                            str(self.creation_date),
                            str(self.last_login)
                            )

# Tabla de proveedores
class Provider(this.Base):
    # Nombre
    __tablename__ = 'provider'

    # Atributos
    provider_name   = Column(String, nullable=False, primary_key=True)
    phone           = Column(String)
    email           = Column(String)
    pay_information = Column(String, nullable=False)
    description     = Column(String)
    category        = Column(String)

    # Relaciones
    lot  = relationship("lot")

# Tabla de productos
class Product(this.Base):
    # Nombre
    __tablename__ = 'product'

    # Atributos
    product_id     = Column(UUID, default=uuid_generate_v4(), primary_key=True)
    product_name   = Column(String, nullable=False)
    price          = Column(Numeric, nullable=False)
    remaining      = Column(Integer, nullable=False, default=0)
    remaining_lots = Column(Integer, nullable=False, default=0)
    available      = Column(Boolean, nullable=False, default=False)
    description    = Column(String)
    category       = Column(String)

    # Relaciones
    lot  = relationship("lot")

# Tabla de lotes
class Lot(this.Base):
    # Nombre
    __tablename__ = 'lot'

    # Atributos
    lot_id           = Column(UUID, nullable=False, default=uuid_generate_v4(), primary_key=True)
    product_id       = Column(UUID, nullable=False, ForeignKey('product.product_id'), primary_key=True)
    provider_id      = Column(String, nullable=False, ForeignKey('product.provider_id'))
    received_by      = Column(String, nullable=False, ForeignKey('users.username'))
    cost             = Column(Numeric, nullable=False)
    quantity         = Column(Integer, nullable=False)
    adquisition_date = Column(Date, nullable=False, default=datetime.datetime.now())
    perishable       = Column(Boolean, nullable=False, default=False)
    expiration_date  = Column(Date)
    available        = Column(Boolean, nullable=False, default=False)
    current          = Column(Boolean, nullable=False, default=False)
    description      = Column(String)
    category         = Column(String)

# Tabla de servicios
class Service(this.Base):
    # Nombre
    __tablename__ = 'service'

    # Atributos
    service_id   = Column(UUID, default=uuid_generate_v4(), primary_key=True)
    service_name = Column(String, nullable=False)
    price        = Column(Numeric, nullable=False)
    available    = Column(Boolean, nullable=False, default=False)
    description  = Column(String)
    category     = Column(String)

# Tabla de clientes
class Client(this.Base):
    # Nombre
    __tablename__ = 'client'

    # Atributos
    ci              = Column(Integer, primary_key=True)
    carnet          = Column(String, default=None)
    firstname       = Column(String, nullable=False)
    lastname        = Column(String, nullable=False)
    phone           = Column(String, default=None)
    debt_permission = Column(Boolean, nullable=False, default=False)
    book_permission = Column(Boolean, nullable=False, default=True)
    blocked         = Column(Boolean, nullable=False, default=False)
    balance         = Column(Numeric, nullable=False, default=0)
    last_seen       = Column(DateTime, default=datetime.datetime.now())

# Tabla de Compras
class Purchase(this.Base):
    # Nombre
    __tablename__ = 'purchase'

    # Atributos
    purchase_id   = Column(UUID, default=uuid_generate_v4(), primary_key=True)
    ci            = Column(Integer, nullable=False)
    clerk         = Column(String, nullable=False)
    total         = Column(Numeric, nullable=False, default=0)
    interest      = Column(Numeric, nullable=False, default=0)
    purchase_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    locked        = Column(Boolean, nullable=False, default=False)
    debt          = Column(Boolean, nullable=False, default=False)
    payed         = Column(Boolean, nullable=False, default=False)
    payed_date    = Column(DateTime, default=None)
    payed_to      = Column(String, default=None)

# Tabla de pagos de orden de compra
class Checkout(this.Base):
    # Nombre
    __tablename__ = 'checkout'

    # Atributos
    checkout_id  = Column(UUID, nullable=False, default=uuid_generate_v4(), primary_key=True)
    purchase_id  = Column(UUID, nullable=False, primary_key=True)
    pay_date     = Column(DateTime, nullable=False, default=datetime.datetime.now())
    amount       = Column(Numeric, nullable=False)
    with_balance = Column(Boolean, nullable=False, default=False)
    description  = Column(String, nullable=False)
    payed        = Column(Boolean, nullable=False, default=False)

# Tabla de lista de productos de orden de compra
class Product_list(this.Base):
    # Nombre
    __tablename__ = 'product_List'

    # Atributos
    product_id  = Column(UUID, nullable=False, primary_key=True)
    purchase_id = Column(UUID, nullable=False, primary_key=True)
    price       = Column(Numeric, nullable=False, default=0)
    amount      = Column(Integer, nullable=False)
    locked      = Column(Boolean, nullable=False, default=False)
    payed       = Column(Boolean, nullable=False, default=False)

# Tabla de lista de servicios de orden de compra
class Service_list(this.Base):
    # Nombre
    __tablename__ = 'service_list'

    # Atributos
    service_id  = Column(UUID, nullable=False, primary_key=True)
    purchase_id = Column(UUID, nullable=False, primary_key=True)
    price       = Column(Numeric, nullable=False, default=0)
    amount      = Column(Integer, nullable=False)
    locked      = Column(Boolean, nullable=False, default=False)
    payed       = Column(Boolean, nullable=False, default=False)

# Tabla de lista de productos de orden de compra
class Reverse_product_list(this.Base):
    # Nombre
    __tablename__ = 'reverse_product_list'

    # Atributos
    product_id   = Column(UUID, nullable=False, primary_key=True)
    purchase_id  = Column(UUID, nullable=False, primary_key=True)
    clerk        = Column(String, nullable=False)
    reverse_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    amount       = Column(Integer, nullable=False)
    cash         = Column(Boolean, default=True)
    description  = Column(String, nullable=False)

# Tabla de reversar lista de servicios de orden de compra
class Reverse_service_list(this.Base):
    # Nombre
    __tablename__ = 'reverse_service_list'

    # Atributos
    service_id   = Column(UUID, nullable=False, primary_key=True)
    purchase_id  = Column(UUID, nullable=False, primary_key=True)
    clerk        = Column(String, nullable=False)
    reverse_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    amount       = Column(Integer, nullable=False)
    cash         = Column(Boolean, default=True)
    description  = Column(String, nullable=False)

# Tabla de transferencias
class Transfer(this.Base):
    # Nombre
    __tablename__ = 'transfer'

    # Atributos
    transfer_id       = Column(UUID, default=uuid_generate_v4(), primary_key=True)
    ci                = Column(Integer, nullable=False)
    clerk             = Column(String, nullable=False)
    transfer_date     = Column(DateTime, nullable=False, default=datetime.datetime.now())
    amount            = Column(Integer, nullable=False)
    bank              = Column(String, nullable=False)
    confirmation_code = Column(String, nullable=False)
    description       = Column(String, nullable=False)

# Tabla de Registro de Operaciones de Caja
class Operation_log(this.Base):
    # Nombre
    __tablename__ = 'operation_log'

    # Atributos
    operation_log_id = Column(UUID, default=uuid_generate_v4(), primary_key=True)
    clerk            = Column(String, nullable=False)
    op_type          = Column(Integer, nullable=False)
    open_record      = Column(Boolean, default=False)
    recorded         = Column(DateTime, nullable=False, default=datetime.datetime.now())
    transfer_balance = Column(Numeric, nullable=False, default=0)
    cash_balance     = Column(Numeric, nullable=False, default=0)
    cash_total       = Column(Numeric, nullable=False)
    total_money      = Column(Numeric, nullable=False)

# Tabla de lenguajes validos
class Valid_language(this.Base):
    # Nombre
    __tablename__ = 'valid_language'

    # Atributos
    lang_name = Column(String, primary_key=True)

# Tabla de Libros
class Book(this.Base):
    # Nombre
    __tablename__ = 'book'

    # Atributos
    book_id       = Column(UUID, default=uuid_generate_v4(), primary_key=True)
    title         = Column(String, nullable=False)
    isbn          = Column(String, default=None)
    edition       = Column(Integer, nullable=False, default=1)
    book_year     = Column(Date, nullable=False)
    lang          = Column(String, nullable=False)
    quantity      = Column(Integer, nullable=False, default=1)
    quantity_lent = Column(Integer, nullable=False, default=0)

# Tabla de Asignaturas
class Subject(this.Base):
    # Nombre
    __tablename__ = 'subject'

    # Atributos
    subject_code = Column(String, primary_key=True)
    subject_name = Column(String, nullable=False)

# Tabla de Autores
class Author(this.Base):
    # Nombre
    __tablename__ = 'author'

    # Atributos
    firstname       = Column(String, nullable=False, primary_key=True)
    lastname        = Column(String, nullable=False, primary_key=True)
    middlename      = Column(String, default=None, primary_key=True)
    second_lastname = Column(String, default=None, primary_key=True)
    birthdate       = Column(Date, default=None, primary_key=True)
    nationality     = Column(String, default=None, primary_key=True)

# Tabla que asocia libros con asignaturas
class Associated_with(this.Base):
    # Nombre
    __tablename__ = 'associated'

    # Atributos
    book_id      = Column(UUID, nullable=False, primary_key=True)
    subject_code = Column(String, nullable=False, primary_key=True)

# Tabla de Quien escribio el libro
class Written_by(this.Base):
    # Nombre
    __tablename__ = 'written_by'

    # Atributos
    book_id         = Column(UUID, nullable=False, primary_key=True)
    firstname       = Column(String, nullable=False, primary_key=True)
    lastname        = Column(String, nullable=False, primary_key=True)
    middlename      = Column(String, default=None, primary_key=True)
    second_lastname = Column(String, default=None, primary_key=True)
    birthdate       = Column(Date, default=None, primary_key=True)
    nationality     = Column(String, default=None, primary_key=True)

# Tabla de préstamos
class Lent_to(this.Base):
    # Nombre
    __tablename__ = 'lent_to'

    # Atributos
    book_id               = Column(UUID, nullable=False, primary_key=True)
    ci                    = Column(Integer, nullable=False, primary_key=True)
    lender_clerk          = Column(String, nullable=False, primary_key=True)
    start_description     = Column(String, nullable=False)
    start_time            = Column(DateTime, nullable=False, default=datetime.datetime.now())
    estimated_return_time = Column(DateTime, nullable=False)
    receiver_clerk        = Column(String, default=None)
    return_time           = Column(DateTime, default=None)
    return_description    = Column(String, default=None)