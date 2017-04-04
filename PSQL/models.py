# Tablas de Db
import sys
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

this = sys.modules[__name__]
this.Base = declarative_base()

# Tabla de usuarios
class User(this.Base):
    __tablename__ = 'users'

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
    __tablename__ = 'provider'

    provider_name   = Column(String, nullable=False, primary_key=True)
    phone           = Column(String)
    email           = Column(String)
    pay_information = Column(String, nullable=False)
    description     = Column(String)
    category        = Column(String)

# Tabla de productos
class Product(this.Base):
    __tablename__ = 'product'

    product_id     = Column(UUID, default=uuid_generate_v4(), primary_key=True)
    product_name   = Column(String, nullable=False)
    price          = Column(Numeric, nullable=False)
    remaining      = Column(Integer, nullable=False, default=0)
    remaining_lots = Column(Integer, nullable=False, default=0)
    available      = Column(Boolean, nullable=False, default=False)
    description    = Column(String)
    category       = Column(String)

# Tabla de lotes
class Lot(this.Base):
    __tablename__ = 'lot'

    lot_id           = Column(UUID, nullable=False, default=uuid_generate_v4(), primary_key=True)
    product_id       = Column(UUID, nullable=False, primary_key=True)
    provider_id      = Column(String, nullable=False)
    received_by      = Column(String, nullable=False)
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
    __tablename__ = 'service'

    service_id   = Column(UUID, default=uuid_generate_v4(), primary_key=True)
    service_name = Column(String, nullable=False)
    price        = Column(Numeric, nullable=False)
    available    = Column(Boolean, nullable=False, default=False)
    description  = Column(String)
    category     = Column(String)

# Tabla de clientes
class Client(this.Base):
    __tablename__ = 'client'

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
    __tablename__ = 'purchase'

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
    __tablename__ = 'checkout'

    checkout_id  = Column(UUID, nullable=False, default=uuid_generate_v4(), primary_key=True)
    purchase_id  = Column(UUID, nullable=False, primary_key=True)
    pay_date     = Column(DateTime, nullable=False, default=datetime.datetime.now())
    amount       = Column(Numeric, nullable=False)
    with_balance = Column(Boolean, nullable=False, default=False)
    description  = Column(String, nullable=False)
    payed        = Column(Boolean, nullable=False, default=False)

# Tabla de lista de productos de orden de compra
class Product_list(this.Base):
    __tablename__ = 'product_List'

    product_id  = Column(UUID, nullable=False, primary_key=True)
    purchase_id = Column(UUID, nullable=False, primary_key=True)
    price       = Column(Numeric, nullable=False, default=0)
    amount      = Column(Integer, nullable=False)
    locked      = Column(Boolean, nullable=False, default=False)
    payed       = Column(Boolean, nullable=False, default=False)

# Tabla de lista de servicios de orden de compra
class Service_list(this.Base):
    __tablename__ = 'service_list'

    service_id  = Column(UUID, nullable=False, primary_key=True)
    purchase_id = Column(UUID, nullable=False, primary_key=True)
    price       = Column(Numeric, nullable=False, default=0)
    amount      = Column(Integer, nullable=False)
    locked      = Column(Boolean, nullable=False, default=False)
    payed       = Column(Boolean, nullable=False, default=False)

# Tabla de lista de productos de orden de compra
class Reverse_product_list(this.Base):
    __tablename__ = 'reverse_product_list'

    product_id   = Column(UUID, nullable=False, primary_key=True)
    purchase_id  = Column(UUID, nullable=False, primary_key=True)
    clerk        = Column(String, nullable=False)
    reverse_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    amount       = Column(Integer, nullable=False)
    cash         = Column(Boolean, default=True)
    description  = Column(String, nullable=False)

# Tabla de reversar lista de servicios de orden de compra
class Reverse_service_list(this.Base):
    __tablename__ = 'reverse_service_list'

    service_id   = Column(UUID, nullable=False, primary_key=True)
    purchase_id  = Column(UUID, nullable=False, primary_key=True)
    clerk        = Column(String, nullable=False)
    reverse_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    amount       = Column(Integer, nullable=False)
    cash         = Column(Boolean, default=True)
    description  = Column(String, nullable=False)

# Tabla de transferencias
class Transfer(this.Base):
    __tablename__ = 'transfer'

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
    __tablename__ = 'operation_log'

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
    __tablename__ = 'valid_language'

    lang_name = Column(String, primary_key=True)

# Tabla de Libros
class Book(this.Base):
    __tablename__ = 'book'

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
    __tablename__ = 'subject'

    subject_code = Column(String, primary_key=True)
    subject_name = Column(String, nullable=False)

# Tabla de Autores
class Author(this.Base):
    __tablename__ = 'author'

    firstname       = Column(String, nullable=False, primary_key=True)
    lastname        = Column(String, nullable=False, primary_key=True)
    middlename      = Column(String, default=None, primary_key=True)
    second_lastname = Column(String, default=None, primary_key=True)
    birthdate       = Column(Date, default=None, primary_key=True)
    nationality     = Column(String, default=None, primary_key=True)

# Tabla que asocia libros con asignaturas
class Associated_with(this.Base):
    __tablename__ = 'associated'

    book_id      = Column(UUID, nullable=False, primary_key=True)
    subject_code = Column(String, nullable=False, primary_key=True)

# Tabla de Quien escribio el libro
class Written_by(this.Base):
    __tablename__ = 'written_by'

    book_id         = Column(UUID, nullable=False, primary_key=True)
    firstname       = Column(String, nullable=False, primary_key=True)
    lastname        = Column(String, nullable=False, primary_key=True)
    middlename      = Column(String, default=None, primary_key=True)
    second_lastname = Column(String, default=None, primary_key=True)
    birthdate       = Column(Date, default=None, primary_key=True)
    nationality     = Column(String, default=None, primary_key=True)

# Tabla de préstamos
class Lent_to(this.Base):
    __tablename__ = 'lent_to'

    book_id               = Column(UUID, nullable=False, primary_key=True)
    ci                    = Column(Integer, nullable=False, primary_key=True)
    lender_clerk          = Column(String, nullable=False, primary_key=True)
    start_description     = Column(String, nullable=False)
    start_time            = Column(DateTime, nullable=False, default=datetime.datetime.now())
    estimated_return_time = Column(DateTime, nullable=False)
    receiver_clerk        = Column(String, default=None)
    return_time           = Column(DateTime, default=None)
    return_description    = Column(String, default=None)