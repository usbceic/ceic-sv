# Tablas de Db
import sys
import datetime

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, String, DateTime, Date, Numeric, ForeignKeyConstraint, CheckConstraint
from guid import GUID

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
    lot                  = relationship("lot")
    purchase             = relationship("purchase")
    reverse_product_list = relationship("reverse_product_list")
    reverse_service_list = relationship("reverse_service_list")
    transfer             = relationship("transfer")
    operation_log        = relationship("operation_log")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.username, self.password, self.firstname, self.lastname, self.email, str(self.creation_date), str(self.last_login))
        template = "<User(username='%s', password='%s',  firstname='%s', lastname='%s', email=='%s', creation_date=='%s', last_login=='%s')>"
        return  template % kwargs

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

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.provider_name, self.phone, self.email, self.pay_information, self.description, self.category)
        template = "<Provider(provider_name='%s', phone='%s', email='%s', pay_information='%s', description=='%s', category=='%s')>"
        return  template % kwargs

# Tabla de productos
class Product(this.Base):
    # Nombre
    __tablename__ = 'product'

    # Atributos
    product_id     = Column(GUID(), primary_key=True)
    product_name   = Column(String, nullable=False)
    price          = Column(Numeric, nullable=False)
    remaining      = Column(Integer, nullable=False, default=0)
    remaining_lots = Column(Integer, nullable=False, default=0)
    available      = Column(Boolean, nullable=False, default=False)
    description    = Column(String)
    category       = Column(String)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('price >= 0', name='exp_product_valid_price'),
        CheckConstraint('remaining >= 0', name='exp_product_valid_remaining'),
        CheckConstraint('remaining_lots >= 0', name='exp_product_valid_remaining_lots'),
    )

    # Relaciones
    lot                  = relationship("lot")
    product_list         = relationship("product_list")
    reverse_product_list = relationship("reverse_product_list")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.product_id, self.product_name, self.price, self.remaining, self.remaining_lots, self.available, self.description, self.category)
        template = "<Product(product_id='%s', product_name='%s', price='%s', remaining='%s', remaining_lots=='%s', available=='%s', description=='%s', category=='%s')>"
        return  template % kwargs

# Tabla de lotes
class Lot(this.Base):
    # Nombre
    __tablename__ = 'lot'

    # Atributos
    lot_id           = Column(GUID(), nullable=False, primary_key=True)
    product_id       = Column(GUID(), nullable=False, primary_key=True)
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

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('cost >= 0', name='exp_lot_valid_cost'),
        CheckConstraint('quantity >= 0', name='exp_lot_valid_quantity'),
        CheckConstraint('NOT available OR (available AND quantity > 0)', name='exp_lot_valid_available'),
        CheckConstraint('NOT current OR (available AND current)', name='exp_lot_valid_current'),
        CheckConstraint(
            '(NOT perishable AND expiration_date IS NULL) OR (perishable AND expiration_date IS NOT NULL AND adquisition_date <= expiration_date)',
            name='exp_lot_valid_expiration_date'
        ),

        # Claves foraneas
        ForeignKeyConstraint(['product_id'], ['product.product_id'], onupdate="CASCADE", ondelete="CASCADE"),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_name'], onupdate="CASCADE"),
        ForeignKeyConstraint(['received_by'], ['users.username']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.lot_id, self.product_id, self.provider_id, self.received_by, self.cost, self.quantity, self.adquisition_date, self.perishable,
            self.expiration_date, self.available, self.current, self.description, self.category,)
        template = "<Lot(lot_id='%s', product_id='%s', provider_id='%s', received_by='%s', cost='%s',  quantity='%s',  adquisition_date='%s',  perishable='%s', "
        template += "expiration_date='%s', available='%s', current='%s', description=='%s', category=='%s')>"
        return  template % kwargs

# Tabla de servicios
class Service(this.Base):
    # Nombre
    __tablename__ = 'service'

    # Atributos
    service_id   = Column(GUID(), primary_key=True)
    service_name = Column(String, nullable=False)
    price        = Column(Numeric, nullable=False)
    available    = Column(Boolean, nullable=False, default=False)
    description  = Column(String)
    category     = Column(String)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('price >= 0', name='exp_service_valid_price'),
    )

    # Relaciones
    service_list         = relationship("service_list")
    reverse_service_list = relationship("reverse_service_list")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.service_id, self.service_name, self.price, self.available, self.description, self.category)
        template = "<Service(service_id='%s', service_name='%s', price='%s', ravailable=='%s', description=='%s', category=='%s')>"
        return  template % kwargs

# Tabla de clientes
class Client(this.Base):
    # Nombre
    __tablename__ = 'client'

    # Atributos
    ci              = Column(Integer, primary_key=True)
    carnet          = Column(String, default=None, unique=True)
    firstname       = Column(String, nullable=False)
    lastname        = Column(String, nullable=False)
    phone           = Column(String, default=None)
    debt_permission = Column(Boolean, nullable=False, default=False)
    book_permission = Column(Boolean, nullable=False, default=True)
    blocked         = Column(Boolean, nullable=False, default=False)
    balance         = Column(Numeric, nullable=False, default=0)
    last_seen       = Column(DateTime, default=datetime.datetime.now())

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('balance >= 0 OR debt_permission', name='exp_client_valid_balance'),
    )

    # Relaciones
    purchase  = relationship("purchase")
    transfer  = relationship("transfer")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.ci, self.carnet, self.firstname, self.lastname, self.phone, self.debt_permission, self.book_permission, self.blocked,
            self.balance, self.last_seen)
        template = "<Client(ci='%s', carnet='%s', firstname='%s', lastname='%s', phone=='%s', debt_permission=='%s', book_permission=='%s', "
        template += "blocked=='%s', balance=='%s', last_seen=='%s')>"
        return  template % kwargs

# Tabla de Compras
class Purchase(this.Base):
    # Nombre
    __tablename__ = 'purchase'

    # Atributos
    purchase_id   = Column(GUID(), primary_key=True)
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

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('total >= 0', name='exp_purchase_valid_total'),
        CheckConstraint('interest >= 0', name='exp_purchase_valid_interest'),
        CheckConstraint('(payed AND locked) OR NOT payed', name='exp_purchase_valid_payed'),
        CheckConstraint('(payed AND payed_date IS NOT NULL) OR (NOT payed AND payed_date IS NULL)', name='exp_purchase_valid_payed_date'),
        CheckConstraint('(payed AND payed_to IS NOT NULL) OR (NOT payed AND payed_to IS NULL)', name='exp_purchase_valid_payed_to'),

        # Claves foraneas
        ForeignKeyConstraint(['ci'], ['client.ci']),
        ForeignKeyConstraint(['clerk'], ['users.username']),
        ForeignKeyConstraint(['payed_to'], ['users.username']),
    )

    # Relaciones
    checkout     = relationship("checkout")
    product_list = relationship("product_list")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.purchase_id, self.ci, self.clerk, self.total, self.interest, self.purchase_date, self.locked, self.debt, self.payed,
            self.payed_date, self.payed_to)
        template = "<Purchase(purchase_id='%s', ci='%s', clerk='%s', total='%s', interest='%s', purchase_date=='%s', locked=='%s', debt=='%s', "
        template += "payed=='%s', payed_date=='%s', payed_to=='%s')>"
        return  template % kwargs

# Tabla de pagos de orden de compra
class Checkout(this.Base):
    # Nombre
    __tablename__ = 'checkout'

    # Atributos
    checkout_id  = Column(GUID(), nullable=False, primary_key=True)
    purchase_id  = Column(GUID(), nullable=False, primary_key=True)
    pay_date     = Column(DateTime, nullable=False, default=datetime.datetime.now())
    amount       = Column(Numeric, nullable=False)
    with_balance = Column(Boolean, nullable=False, default=False)
    description  = Column(String, nullable=False)
    payed        = Column(Boolean, nullable=False, default=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('amount > 0', name='exp_checkout_valid_amount'),

        # Claves foraneas
        ForeignKeyConstraint(['purchase_id'], ['purchase.purchase_id']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.checkout_id, self.purchase_id, self.pay_date, self.amount, self.with_balance, self.description, self.payed)
        template = "<Checkout(checkout_id='%s', purchase_id='%s', pay_date='%s', amount='%s', with_balance=='%s', description=='%s', payed=='%s')>"
        return  template % kwargs

# Tabla de lista de productos de orden de compra
class Product_list(this.Base):
    # Nombre
    __tablename__ = 'product_list'

    # Atributos
    product_id  = Column(GUID(), nullable=False, primary_key=True)
    purchase_id = Column(GUID(), nullable=False, primary_key=True)
    price       = Column(Numeric, nullable=False, default=0)
    amount      = Column(Integer, nullable=False)
    locked      = Column(Boolean, nullable=False, default=False)
    payed       = Column(Boolean, nullable=False, default=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('price > 0', name='exp_product_list_valid_price'),
        CheckConstraint('amount > 0', name='exp_product_list_valid_amount'),
        CheckConstraint('(payed AND locked) OR NOT payed', name='exp_product_list_valid_payed'),

        # Claves foraneas
        ForeignKeyConstraint(['product_id'], ['product.product_id']),
        ForeignKeyConstraint(['purchase_id'], ['purchase.purchase_id']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.product_id, self.purchase_id, self.price, self.amount, self.locked, self.payed)
        template = "<Product_list(product_id='%s', purchase_id='%s', price='%s', amount='%s', locked=='%s', payed=='%s')>"
        return  template % kwargs

# Tabla de lista de servicios de orden de compra
class Service_list(this.Base):
    # Nombre
    __tablename__ = 'service_list'

    # Atributos
    service_id  = Column(GUID(), nullable=False, primary_key=True)
    purchase_id = Column(GUID(), nullable=False, primary_key=True)
    price       = Column(Numeric, nullable=False, default=0)
    amount      = Column(Integer, nullable=False)
    locked      = Column(Boolean, nullable=False, default=False)
    payed       = Column(Boolean, nullable=False, default=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('price > 0', name='exp_service_list_valid_price'),
        CheckConstraint('amount > 0', name='exp_service_list_valid_amount'),
        CheckConstraint('(payed AND locked) OR NOT payed', name='exp_service_list_valid_payed'),

        # Claves foraneas
        ForeignKeyConstraint(['service_id'], ['service.service_id']),
        ForeignKeyConstraint(['purchase_id'], ['purchase.purchase_id']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.service_id, self.purchase_id, self.price, self.amount, self.locked, self.payed)
        template = "<Service_list(service_id='%s', purchase_id='%s', price='%s', amount='%s', locked=='%s', payed=='%s')>"
        return  template % kwargs

# Tabla de lista de productos de orden de compra
class Reverse_product_list(this.Base):
    # Nombre
    __tablename__ = 'reverse_product_list'

    # Atributos
    product_id   = Column(GUID(), nullable=False, primary_key=True)
    purchase_id  = Column(GUID(), nullable=False, primary_key=True)
    clerk        = Column(String, nullable=False)
    reverse_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    amount       = Column(Integer, nullable=False)
    cash         = Column(Boolean, default=True)
    description  = Column(String, nullable=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('amount > 0', name='exp_reverse_product_list_valid_amount'),

        # Claves foraneas
        ForeignKeyConstraint(['product_id'], ['product.product_id']),
        ForeignKeyConstraint(['purchase_id'], ['purchase.purchase_id']),
        ForeignKeyConstraint(['clerk'], ['users.username']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.product_id, self.purchase_id, self.clerk, self.reverse_date, self.amount, self.cash, self.description)
        template = "<Reverse_product_list(product_id='%s', purchase_id='%s', clerk='%s', reverse_date='%s', amount='%s', cash=='%s', description=='%s')>"
        return  template % kwargs

# Tabla de reversar lista de servicios de orden de compra
class Reverse_service_list(this.Base):
    # Nombre
    __tablename__ = 'reverse_service_list'

    # Atributos
    service_id   = Column(GUID(), nullable=False, primary_key=True)
    purchase_id  = Column(GUID(), nullable=False, primary_key=True)
    clerk        = Column(String, nullable=False)
    reverse_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    amount       = Column(Integer, nullable=False)
    cash         = Column(Boolean, default=True)
    description  = Column(String, nullable=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('amount > 0', name='exp_reverse_service_list_valid_amount'),

        # Claves foraneas
        ForeignKeyConstraint(['service_id'], ['service.service_id']),
        ForeignKeyConstraint(['purchase_id'], ['purchase.purchase_id']),
        ForeignKeyConstraint(['clerk'], ['users.username']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.product_id, self.purchase_id, self.clerk, self.reverse_date, self.amount, self.cash, self.description)
        template = "<Reverse_service_list(service_id='%s', purchase_id='%s', clerk='%s', reverse_date='%s', amount='%s', cash=='%s', description=='%s')>"
        return  template % kwargs

# Tabla de transferencias
class Transfer(this.Base):
    # Nombre
    __tablename__ = 'transfer'

    # Atributos
    transfer_id       = Column(GUID(), primary_key=True)
    ci                = Column(Integer, nullable=False)
    clerk             = Column(String, nullable=False)
    transfer_date     = Column(DateTime, nullable=False, default=datetime.datetime.now())
    amount            = Column(Integer, nullable=False)
    bank              = Column(String, nullable=False)
    confirmation_code = Column(String, nullable=False)
    description       = Column(String, nullable=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('amount > 0', name='exp_transfer_valid_amount'),

        # Claves foraneas
        ForeignKeyConstraint(['ci'], ['client.ci']),
        ForeignKeyConstraint(['clerk'], ['users.username']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.transfer_id, self.ci, self.clerk, self.transfer_date, self.amount, self.bank, self.confirmation_code, self.description)
        template = "<Transfer(transfer_id='%s', ci='%s', clerk='%s', transfer_date='%s', amount='%s', bank=='%s', confirmation_code='%s', description=='%s')>"
        return  template % kwargs

# Tabla de Registro de Operaciones de Caja
class Operation_log(this.Base):
    # Nombre
    __tablename__ = 'operation_log'

    # Atributos
    operation_log_id = Column(GUID(), primary_key=True)
    clerk            = Column(String, nullable=False)
    op_type          = Column(Integer, nullable=False)
    open_record      = Column(Boolean, default=False)
    recorded         = Column(DateTime, nullable=False, default=datetime.datetime.now())
    transfer_balance = Column(Numeric, nullable=False, default=0)
    cash_balance     = Column(Numeric, nullable=False, default=0)
    cash_total       = Column(Numeric, nullable=False)
    total_money      = Column(Numeric, nullable=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('open_record IS NULL OR (op_type = 0 OR op_type = 1 OR op_type = 2)', name='exp_operation_log_valid_open_record'),

        # Claves foraneas
        ForeignKeyConstraint(['clerk'], ['users.username']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.operation_log_id, self.clerk, self.op_type, self.open_record, self.recorded, self.transfer_balance, self.cash_balance, self.cash_total, self.total_money)
        template = "<Operation_log(operation_log_id='%s', clerk='%s', op_type='%s', open_record='%s', recorded='%s', transfer_balance=='%s', cash_balance='%s', cash_total=='%s', total_money='%s')>"
        return  template % kwargs

# Tabla de lenguajes validos
class Valid_language(this.Base):
    # Nombre
    __tablename__ = 'valid_language'

    # Atributos
    lang_name = Column(String, primary_key=True)

    # Relaciones
    book = relationship("book")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.lang_name)
        template = "<Valid_language(lang_name='%s')>"
        return  template % kwargs

# Tabla de Libros
class Book(this.Base):
    # Nombre
    __tablename__ = 'book'

    # Atributos
    book_id       = Column(GUID(), primary_key=True)
    title         = Column(String, nullable=False)
    isbn          = Column(String, default=None, unique=True)
    edition       = Column(Integer, nullable=False, default=1)
    book_year     = Column(Date, nullable=False)
    lang          = Column(String, nullable=False)
    quantity      = Column(Integer, nullable=False, default=1)
    quantity_lent = Column(Integer, nullable=False, default=0)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('edition > 0', name='exp_book_valid_edition'),
        CheckConstraint('quantity > 0', name='exp_book_valid_quantity'),
        CheckConstraint('quantity_lent >= 0', name='exp_book_valid_quantity_lent'),

        # Claves foraneas
        ForeignKeyConstraint(['lang'], ['valid_language.lang_name']),
    )

    # Relaciones
    associated_with = relationship("associated_with")
    written_by = relationship("written_by")

# Tabla de Asignaturas
class Subject(this.Base):
    # Nombre
    __tablename__ = 'subject'

    # Atributos
    subject_code = Column(String, primary_key=True)
    subject_name = Column(String, nullable=False)

    # Relaciones
    associated_with = relationship("associated_with")

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

    # Relaciones
    written_by = relationship("written_by")

# Tabla que asocia libros con asignaturas
class Associated_with(this.Base):
    # Nombre
    __tablename__ = 'associated_with'

    # Atributos
    book_id      = Column(GUID(), nullable=False, primary_key=True)
    subject_code = Column(String, nullable=False, primary_key=True)

    # Constraints
    __table_args__ = (
        # Claves foraneas
        ForeignKeyConstraint(['book_id'], ['book.book_id']),
        ForeignKeyConstraint(['subject_code'], ['subject.subject_code'], onupdate="CASCADE"),
    )

# Tabla de Quien escribio el libro
class Written_by(this.Base):
    # Nombre
    __tablename__ = 'written_by'

    # Atributos
    book_id         = Column(GUID(), nullable=False, primary_key=True)
    firstname       = Column(String, nullable=False, primary_key=True)
    lastname        = Column(String, nullable=False, primary_key=True)
    middlename      = Column(String, default=None, primary_key=True)
    second_lastname = Column(String, default=None, primary_key=True)
    birthdate       = Column(Date, default=None, primary_key=True)
    nationality     = Column(String, default=None, primary_key=True)

    # Constraints
    __table_args__ = (
        # Claves foraneas
        ForeignKeyConstraint(['book_id'], ['book.book_id']),
        ForeignKeyConstraint(
            ['firstname', 'lastname', 'middlename', 'second_lastname', 'birthdate', 'nationality'],
            ['author.firstname', 'author.lastname', 'author.middlename', 'author.second_lastname', 'author.birthdate', 'author.nationality']
        ),
    )

"""# Tabla de préstamos
class Lent_to(this.Base):
    # Nombre
    __tablename__ = 'lent_to'

    # Atributos
    book_id               = Column(GUID(), nullable=False, primary_key=True)
    ci                    = Column(Integer, nullable=False, primary_key=True)
    lender_clerk          = Column(String, nullable=False, primary_key=True)
    start_description     = Column(String, nullable=False)
    start_time            = Column(DateTime, nullable=False, default=datetime.datetime.now())
    estimated_return_time = Column(DateTime, nullable=False)
    receiver_clerk        = Column(String, default=None)
    return_time           = Column(DateTime, default=None)
    return_description    = Column(String, default=None)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('start_time <= estimated_return_time', name='exp_lent_to_valid_estimated_return_time'),
        CheckConstraint(
            '(receiver_clerk IS NULL AND return_time IS NULL) OR (receiver_clerk IS NOT NULL AND return_time IS NOT NULL AND start_time <= return_time)',
            name='exp_lent_to_valid_valid_return_time'
        ),
        CheckConstraint(
            '(receiver_clerk IS NULL AND return_description IS NULL) OR (receiver_clerk IS NOT NULL AND return_description IS NOT NULL)',
            name='exp_lent_to_valid_return_description'
        ),

        # Claves foraneas
        ForeignKeyConstraint(['book_id'], ['book.book_id']),
        ForeignKeyConstraint(['ci'], ['client.ci']),
        ForeignKeyConstraint(['lender_clerk'], ['users.username']),
        ForeignKeyConstraint(['receiver_clerk'], ['users.username']),
    )"""