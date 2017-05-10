# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación del modelo para la base de datos

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Christian Oliveros, 01christianol01@gmail.com
# Pablo Betancourt, pablodbc30@gmail.com

###################################################################################################################################################################################
## DEPENDENCIAS:
###################################################################################################################################################################################

import sys
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, String, DateTime, Date, Numeric, ForeignKeyConstraint, CheckConstraint, UniqueConstraint, ForeignKey
from custom_types import GUID

###################################################################################################################################################################################
## DECLARACIÓN DEL MODELO:
###################################################################################################################################################################################

this = sys.modules[__name__]
this.Base = declarative_base()

#==================================================================================================================================================================================
# TABLA DE USUARIOS
#==================================================================================================================================================================================
class User(this.Base):
    # Nombre
    __tablename__ = 'users'

    # Atributos
    username        = Column(String, primary_key=True)
    password        = Column(String, nullable=False)
    firstname       = Column(String, nullable=False)
    lastname        = Column(String, nullable=False)
    email           = Column(String, nullable=False, unique=True)
    permission_mask = Column(Integer, nullable=False)
    profile         = Column(String, default="")
    active          = Column(Boolean, nullable=False, default=True)
    creation_date   = Column(DateTime, nullable=False, default=datetime.now)
    last_login      = Column(DateTime, nullable=False, default=datetime.now)

    # Relaciones
    lot                    = relationship("Lot")
    purchase_clerk         = relationship("Purchase", foreign_keys="Purchase.clerk")
    reverse_product_list   = relationship("Reverse_product_list")
    reverse_service_list   = relationship("Reverse_service_list")
    increase               = relationship("Increase")
    transfer               = relationship("Transfer")
    deposit                = relationship("Deposit")
    operation_log          = relationship("Operation_log")
    lent_to_lender_clerk   = relationship("Lent_to", foreign_keys="Lent_to.lender_clerk")
    lent_to_receiver_clerk = relationship("Lent_to", foreign_keys="Lent_to.receiver_clerk")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.username, self.password, self.firstname, self.lastname, self.email, str(self.creation_date), str(self.last_login))
        template = "<User(username='%s', password='%s',  firstname='%s', lastname='%s', email=='%s', creation_date=='%s', last_login=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE PROVEEDORES
#==================================================================================================================================================================================
class Provider(this.Base):
    # Nombre
    __tablename__ = 'provider'

    # Atributos
    provider_name   = Column(String, nullable=False, primary_key=True)
    phone           = Column(String)
    email           = Column(String)
    pay_information = Column(String)
    description     = Column(String)
    active          = Column(Boolean, nullable=False, default=True)
    creation_date   = Column(DateTime, nullable=False, default=datetime.now)

    # Relaciones
    lot  = relationship("Lot")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.provider_name, self.phone, self.email, self.pay_information, self.description)
        template = "<Provider(provider_name='%s', phone='%s', email='%s', pay_information='%s', description=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE PRODUCTOS
#==================================================================================================================================================================================
class Product(this.Base):
    # Nombre
    __tablename__ = 'product'

    # Atributos
    product_id     = Column(GUID, primary_key=True, default=GUID.random_value)
    product_name   = Column(String, nullable=False, unique=True)
    price          = Column(Numeric, nullable=False)
    creation_date  = Column(DateTime, nullable=False, default=datetime.now)
    remaining      = Column(Integer, nullable=False, default=0)
    remaining_lots = Column(Integer, nullable=False, default=0)
    available      = Column(Boolean, nullable=False, default=False)
    category       = Column(String)
    active         = Column(Boolean, nullable=False, default=True)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('price >= 0', name='exp_product_valid_price'),
        CheckConstraint('remaining >= 0', name='exp_product_valid_remaining'),
        CheckConstraint('remaining_lots >= 0', name='exp_product_valid_remaining_lots'),
    )

    # Relaciones
    lot                  = relationship("Lot")
    product_list         = relationship("Product_list")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.product_id), self.product_name, str(self.price), str(self.creation_date), str(self.remaining), str(self.remaining_lots), str(self.available), self.category)
        template = "<Product(product_id='%s', product_name='%s', price='%s', creation_date='%s', remaining='%s', remaining_lots=='%s', available=='%s', category=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE LOTES
#==================================================================================================================================================================================
class Lot(this.Base):
    # Nombre
    __tablename__ = 'lot'

    # Atributos
    lot_id           = Column(GUID, nullable=False, primary_key=True, default=GUID.random_value)
    product_id       = Column(GUID, nullable=False)
    provider_id      = Column(String, nullable=False)
    received_by      = Column(String, nullable=False)
    cost             = Column(Numeric, nullable=False)
    quantity         = Column(Integer, nullable=False)
    remaining        = Column(Integer, nullable=False)
    adquisition_date = Column(Date, nullable=False, default=datetime.now)
    perishable       = Column(Boolean, nullable=False, default=False)
    expiration_date  = Column(Date)
    available        = Column(Boolean, nullable=False, default=True)
    current          = Column(Boolean, nullable=False, default=False)

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
        kwargs = (str(self.lot_id), str(self.product_id), self.provider_id, self.received_by, str(self.cost), str(self.quantity), str(self.adquisition_date), str(self.perishable),
            str(self.expiration_date), str(self.available), str(self.current))
        template = "<Lot(lot_id='%s', product_id='%s', provider_id='%s', received_by='%s', cost='%s',  quantity='%s',  adquisition_date='%s',  perishable='%s', "
        template += "expiration_date='%s', available='%s', current='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE SERVICIOS
#==================================================================================================================================================================================
class Service(this.Base):
    # Nombre
    __tablename__ = 'service'

    # Atributos
    service_id   = Column(GUID, primary_key=True, default=GUID.random_value)
    service_name = Column(String, nullable=False, unique=True)
    price        = Column(Numeric, nullable=False)
    available    = Column(Boolean, nullable=False, default=False)
    description  = Column(String, default="")
    category     = Column(String, default="")
    active       = Column(Boolean, nullable=False, default=True)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('price >= 0', name='exp_service_valid_price'),
    )

    # Relaciones
    service_list = relationship("Service_list")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.service_id), self.service_name, str(self.price), str(self.available), self.description, self.category)
        template = "<Service(service_id=='%s', service_name=='%s', price=='%s', available=='%s', description=='%s', category=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE CLIENTES
#==================================================================================================================================================================================
class Client(this.Base):
    # Nombre
    __tablename__ = 'client'

    # Atributos
    ci              = Column(Integer, primary_key=True)
    firstname       = Column(String, nullable=False)
    lastname        = Column(String, nullable=False)
    phone           = Column(String)
    email           = Column(String)
    debt_permission = Column(Boolean, nullable=False, default=False)
    book_permission = Column(Boolean, nullable=False, default=True)
    blocked         = Column(Boolean, nullable=False, default=False)
    balance         = Column(Numeric, nullable=False, default=0)
    debt            = Column(Numeric, nullable=False, default=0)
    last_seen       = Column(DateTime, default=datetime.now)
    active          = Column(Boolean, nullable=False, default=True)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('balance >= 0 OR debt_permission', name='exp_client_valid_balance'),
        CheckConstraint('debt = 0 OR debt_permission', name='exp_client_valid_debt'),
    )

    # Relaciones
    purchase  = relationship("Purchase")
    increase  = relationship("Increase")
    transfer  = relationship("Transfer")
    deposit   = relationship("Deposit")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.ci), self.firstname, self.lastname, self.phone, self.email, str(self.debt_permission), str(self.book_permission), str(self.blocked),
            str(self.balance), str(self.debt), str(self.last_seen))
        template = "<Client(ci=='%s', firstname=='%s', lastname=='%s', phone=='%s', email=='%s', debt_permission=='%s', book_permission=='%s', "
        template += "blocked=='%s', balance=='%s', debt=='%s', last_seen=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE COMPRAS
#==================================================================================================================================================================================
class Purchase(this.Base):
    # Nombre
    __tablename__ = 'purchase'

    # Atributos
    purchase_id   = Column(GUID, primary_key=True, default=GUID.random_value)
    ci            = Column(Integer, nullable=False)
    clerk         = Column(String, nullable=False)
    total         = Column(Numeric, nullable=False, default=0)
    interest      = Column(Numeric, nullable=False, default=0)
    purchase_date = Column(DateTime, nullable=False, default=datetime.now)
    payed         = Column(Boolean, nullable=False, default=False)
    payed_date    = Column(DateTime, default=None)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('total >= 0', name='exp_purchase_valid_total'),
        CheckConstraint('interest >= 0', name='exp_purchase_valid_interest'),
        CheckConstraint('(payed AND payed_date IS NOT NULL) OR (NOT payed AND payed_date IS NULL)', name='exp_purchase_valid_payed_date'),

        # Claves foraneas
        ForeignKeyConstraint(['ci'], ['client.ci']),
        ForeignKeyConstraint(['clerk'], ['users.username']),
    )

    # Relaciones
    product_list = relationship("Product_list")
    service_list = relationship("Service_list")
    checkout     = relationship("Checkout")
    debt         = relationship("Debt")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.purchase_id), str(self.ci), self.clerk, str(self.total), str(self.interest), str(self.purchase_date), str(self.payed), str(self.payed_date))
        template = "<Purchase(purchase_id='%s', ci='%s', clerk='%s', total='%s', interest='%s', purchase_date=='%s', payed=='%s', payed_date=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE LISTA DE PRODUCTOS DE ORDEN DE COMPRA
#==================================================================================================================================================================================
class Product_list(this.Base):
    # Nombre
    __tablename__ = 'product_list'

    # Atributos
    product_id  = Column(GUID, nullable=False, primary_key=True)
    purchase_id = Column(GUID, nullable=False, primary_key=True)
    price       = Column(Numeric, nullable=False, default=0)
    amount      = Column(Integer, nullable=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('price > 0', name='exp_product_list_valid_price'),
        CheckConstraint('amount > 0', name='exp_product_list_valid_amount'),

        # Claves foraneas
        ForeignKeyConstraint(['product_id'], ['product.product_id']),
        ForeignKeyConstraint(['purchase_id'], ['purchase.purchase_id']),
    )

    # Relaciones
    reversed_product_list = relationship("Reverse_product_list", uselist=False, back_populates="product_list")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.product_id), str(self.purchase_id), str(self.price), str(self.amount))
        template = "<Product_list(product_id='%s', purchase_id='%s', price='%s', amount='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE SERVICIOS DE ORDEN DE COMPRA
#==================================================================================================================================================================================
class Service_list(this.Base):
    # Nombre
    __tablename__ = 'service_list'

    # Atributos
    service_id  = Column(GUID, nullable=False, primary_key=True)
    purchase_id = Column(GUID, nullable=False, primary_key=True)
    price       = Column(Numeric, nullable=False, default=0)
    amount      = Column(Integer, nullable=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('price > 0', name='exp_service_list_valid_price'),
        CheckConstraint('amount > 0', name='exp_service_list_valid_amount'),

        # Claves foraneas
        ForeignKeyConstraint(['service_id'], ['service.service_id']),
        ForeignKeyConstraint(['purchase_id'], ['purchase.purchase_id']),
    )

    # Relaciones
    reversed_service_list = relationship("Reverse_service_list", uselist=False, back_populates="service_list")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.service_id), str(self.purchase_id), str(self.price), str(self.amount))
        template = "<Service_list(service_id='%s', purchase_id='%s', price='%s', amount='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE PAGOS DE ORDEN DE COMPRA
#==================================================================================================================================================================================
class Checkout(this.Base):
    # Nombre
    __tablename__ = 'checkout'

    # Atributos
    checkout_id  = Column(GUID, nullable=False, primary_key=True, default=GUID.random_value)
    purchase_id  = Column(GUID, nullable=False)
    pay_date     = Column(DateTime, nullable=False, default=datetime.now)
    amount       = Column(Numeric, nullable=False)
    with_balance = Column(Boolean, nullable=False, default=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('amount > 0', name='exp_checkout_valid_amount'),

        # Claves foraneas
        ForeignKeyConstraint(['purchase_id'], ['purchase.purchase_id']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.checkout_id), str(self.purchase_id), str(self.pay_date), str(self.amount), str(self.with_balance))
        template = "<Checkout(checkout_id='%s', purchase_id='%s', pay_date='%s', amount='%s', with_balance=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE DEUDAS
#==================================================================================================================================================================================
class Debt(this.Base):
    # Nombre
    __tablename__ = 'debt'

    # Atributos
    debt_id     = Column(GUID, nullable=False, primary_key=True, default=GUID.random_value)
    purchase_id = Column(GUID, nullable=False)
    pay_date    = Column(DateTime)
    amount      = Column(Numeric, nullable=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('amount > 0', name='exp_debt_valid_amount'),

        # Claves foraneas
        ForeignKeyConstraint(['purchase_id'], ['purchase.purchase_id']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.debt_id), str(self.purchase_id), str(self.pay_date), str(self.amount))
        template = "<Debt(debt_id='%s', purchase_id='%s', pay_date='%s', amount='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE INCREMENTOS EN DEUDAS
#==================================================================================================================================================================================
class Increase(this.Base):
    # Nombre
    __tablename__ = 'increase'

    # Atributos
    increase_id   = Column(GUID, nullable=False, primary_key=True, default=GUID.random_value)
    ci            = Column(Integer, nullable=False)
    clerk         = Column(String, nullable=False)
    amount        = Column(Numeric, nullable=False)
    creation_date = Column(DateTime, nullable=False, default=datetime.now)
    pay_date      = Column(DateTime)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('amount > 0', name='exp_increase_valid_amount'),

        # Claves foraneas
        ForeignKeyConstraint(['ci'], ['client.ci']),
        ForeignKeyConstraint(['clerk'], ['users.username']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.increase_id), str(self.ci), str(self.clerk), str(self.amount), str(self.creation_date), str(self.pay_date))
        template = "<Increase(increase_id='%s', ci='%s', clerk='%s',, amount='%s', creation_date='%s', pay_date='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE DEVOLUCIONES PARA LISTA DE PRODUCTOS DE ORDEN DE COMPRA
#==================================================================================================================================================================================
class Reverse_product_list(this.Base):
    # Nombre
    __tablename__ = 'reverse_product_list'

    # Atributos
    product_id   = Column(GUID, nullable=False, primary_key=True)
    purchase_id  = Column(GUID, nullable=False, primary_key=True)
    clerk_id     = Column(String, nullable=False)
    reverse_date = Column(DateTime, nullable=False, default=datetime.now)
    amount       = Column(Integer, nullable=False)
    cash         = Column(Boolean, default=True)
    cash_amount  = Column(Numeric, nullable=False, default=0.0)
    description  = Column(String, nullable=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('amount > 0', name='exp_reverse_product_list_valid_amount'),
        CheckConstraint('(cash_amount >= 0 AND cash) OR (cash_amount = 0 AND NOT cash)', name='exp_reverse_product_list_valid_cash_amount'),

        # Claves foraneas
        ForeignKeyConstraint(['product_id', 'purchase_id'], ['product_list.product_id', 'product_list.purchase_id']),
        ForeignKeyConstraint(['clerk_id'], ['users.username']),
    )

    # Relaciones
    product_list = relationship("Product_list", back_populates="reversed_product_list")
    clerk = relationship("User", back_populates="reverse_product_list")


    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.product_id), str(self.purchase_id), self.clerk, str(self.reverse_date), str(self.amount), str(self.cash), self.description, str(self.cash_amount))
        template = "<Reverse_product_list(product_id='%s', purchase_id='%s', clerk='%s', reverse_date='%s', amount='%s', cash=='%s', description=='%s', cash_amount=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE DEVOLUCIONES PARA LISTA DE SERVICIOS DE ORDEN DE COMPRA
#==================================================================================================================================================================================
class Reverse_service_list(this.Base):
    # Nombre
    __tablename__ = 'reverse_service_list'

    # Atributos
    service_id   = Column(GUID, nullable=False, primary_key=True)
    purchase_id  = Column(GUID, nullable=False, primary_key=True)
    clerk_id     = Column(String, nullable=False)
    reverse_date = Column(DateTime, nullable=False, default=datetime.now)
    amount       = Column(Integer, nullable=False)
    cash         = Column(Boolean, default=True)
    cash_amount  = Column(Numeric, nullable=False, default=0.0)
    description  = Column(String, nullable=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('amount > 0', name='exp_reverse_service_list_valid_amount'),
        CheckConstraint('(cash_amount >= 0 AND cash) OR (cash_amount = 0 AND NOT cash)', name='exp_reverse_service_list_valid_cash_amount'),

        # Claves foraneas
        ForeignKeyConstraint(['service_id', 'purchase_id'], ['service_list.service_id', 'service_list.purchase_id']),
        ForeignKeyConstraint(['clerk_id'], ['users.username']),
    )

    # Relaciones
    service_list = relationship("Service_list", back_populates="reversed_service_list")
    clerk = relationship("User", back_populates="reverse_service_list")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.product_id), str(self.purchase_id), self.clerk, str(self.reverse_date), str(self.amount), str(self.cash), self.description, str(self.cash_amount))
        template = "<Reverse_service_list(service_id='%s', purchase_id='%s', clerk='%s', reverse_date='%s', amount='%s', cash=='%s', description=='%s', cash_amount=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE TRANSFERENCIAS
#==================================================================================================================================================================================
class Transfer(this.Base):
    # Nombre
    __tablename__ = 'transfer'

    # Atributos
    transfer_id       = Column(GUID, primary_key=True, default=GUID.random_value)
    ci                = Column(Integer, nullable=False)
    clerk             = Column(String, nullable=False)
    transfer_date     = Column(DateTime, nullable=False, default=datetime.now)
    amount            = Column(Numeric, nullable=False)
    bank              = Column(String, nullable=False)
    confirmation_code = Column(String, nullable=False)
    description       = Column(String, nullable=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('amount > 0', name='exp_transfer_valid_amount'),

        # Uniques
        UniqueConstraint('bank', 'confirmation_code'),

        # Claves foraneas
        ForeignKeyConstraint(['ci'], ['client.ci']),
        ForeignKeyConstraint(['clerk'], ['users.username']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.transfer_id), str(self.ci), self.clerk, str(self.transfer_date), str(self.amount), self.bank, self.confirmation_code, self.description)
        template = "<Transfer(transfer_id='%s', ci='%s', clerk='%s', transfer_date='%s', amount='%s', bank=='%s', confirmation_code='%s', description=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE DEPÓSITOS
#==================================================================================================================================================================================
class Deposit(this.Base):
    # Nombre
    __tablename__ = 'deposit'

    # Atributos
    deposit_id        = Column(GUID, primary_key=True, default=GUID.random_value)
    ci                = Column(Integer, nullable=False)
    clerk             = Column(String, nullable=False)
    deposit_date      = Column(DateTime, nullable=False, default=datetime.now)
    amount            = Column(Numeric, nullable=False)
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
        kwargs = (str(self.deposit_id), str(self.ci), self.clerk, str(self.deposit_date), str(self.amount), self.description)
        template = "<Deposit(deposit_id='%s', ci='%s', clerk='%s', deposit_date='%s', amount='%s', description=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE REGISTRO DE OPERACIONES DE CAJA
#==================================================================================================================================================================================
class Operation_log(this.Base):
    # Nombre
    __tablename__ = 'operation_log'

    # Atributos
    operation_log_id = Column(GUID, primary_key=True, default=GUID.random_value)
    clerk            = Column(String, nullable=False)
    op_type          = Column(Integer, nullable=False)
    open_record      = Column(Boolean, default=None)
    recorded         = Column(DateTime, nullable=False, default=datetime.now)
    transfer_balance = Column(Numeric, nullable=False, default=0)
    cash_balance     = Column(Numeric, nullable=False, default=0)
    cash_total       = Column(Numeric, nullable=False)
    total_money      = Column(Numeric, nullable=False)
    description      = Column(String, nullable=False)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('open_record IS NULL OR (op_type = 0 OR op_type = 1 OR op_type = 2)', name='exp_operation_log_valid_open_record'),

        # Claves foraneas
        ForeignKeyConstraint(['clerk'], ['users.username']),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.operation_log_id), self.clerk, str(self.op_type), str(self.open_record), str(self.recorded), str(self.transfer_balance),
            str(self.cash_balance), str(self.cash_total), str(self.total_money), self.description)
        template = "<Operation_log(operation_log_id='%s', clerk='%s', op_type='%s', open_record='%s', recorded='%s', transfer_balance=='%s', "
        template += "cash_balance='%s', cash_total=='%s', total_money='%s', description='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE MONEDAS / BILLETES DE PAGO
#==================================================================================================================================================================================
class Legal_tender(this.Base):
    # Nombre
    __tablename__ = 'legal_tender'

    amount = Column(Numeric, nullable=False, primary_key=True)

    # Constraints
    __table_args__ = (
        # Verificaciones
        CheckConstraint('amount > 0', name='exp_legal_tender_amount'),
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        return "<Legal_tender(amount='%s')>" % (str(self.amount))

#==================================================================================================================================================================================
# Tabla QUE ASOCIA LIBROS CON ASIGNATURAS
#==================================================================================================================================================================================
class Associated_with(this.Base):
    # Nombre
    __tablename__ = 'associated_with'

    # Atributos
    book_id      = Column(GUID, ForeignKey('book.book_id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False, primary_key=True)
    subject_code = Column(String, ForeignKey('subject.subject_code', onupdate="CASCADE", ondelete="CASCADE"), nullable=False, primary_key=True)

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.book_id), self.subject_code)
        template = "<Associated_with(book_id='%s', subject_code='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE QUIEN ESCRIBIO UN LIBRO
#==================================================================================================================================================================================
class Written_by(this.Base):
    # Nombre
    __tablename__ = 'written_by'

    # Atributos
    book_id         = Column(GUID, nullable=False, primary_key=True)
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

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.book_id), self.firstname, self.lastname, self.middlename, self.second_lastname, str(self.birthdate), self.nacionality)
        template = "<Written_by(book_id='%s', firstname='%s', lastname='%s', middlename='%s', second_lastname='%s', birthdate='%s', nacionality=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE LENGUAJES VÁLIDOS
#==================================================================================================================================================================================
class Valid_language(this.Base):
    # Nombre
    __tablename__ = 'valid_language'

    # Atributos
    lang_name = Column(String, primary_key=True)

    # Relaciones
    book = relationship("Book")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.lang_name)
        template = "<Valid_language(lang_name='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE LIBROS
#==================================================================================================================================================================================
class Book(this.Base):
    # Nombre
    __tablename__ = 'book'

    # Atributos
    book_id       = Column(GUID, primary_key=True, default=GUID.random_value)
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
    subjects = relationship("Subject", secondary="associated_with", back_populates="books")
    written_by = relationship("Author", secondary="written_by", back_populates="books")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.book_id), self.title, self.isbn, str(self.edition), str(self.book_year), self.lang, str(self.quantity), str(self.quantity_lent))
        template = "<Book(book_id='%s', title='%s', isbn='%s', edition='%s', book_year='%s', lang=='%s', quantity='%s', quantity_lent=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE ASIGNATURAS
#==================================================================================================================================================================================
class Subject(this.Base):
    # Nombre
    __tablename__ = 'subject'

    # Atributos
    subject_code = Column(String, primary_key=True)
    subject_name = Column(String, nullable=False)

    # Relaciones
    books = relationship("Book", secondary="associated_with", back_populates="subjects")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.subject_code, self.subject_name)
        template = "<Subject(subject_code='%s', subject_name='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE AUTORES
#==================================================================================================================================================================================
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
    books = relationship("Book", secondary="written_by", back_populates="written_by")

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (self.firstname, self.lastname, self.middlename, self.second_lastname, str(self.birthdate), self.nacionality)
        template = "<Author(firstname='%s', lastname='%s', middlename='%s', second_lastname='%s', birthdate='%s', nacionality=='%s')>"
        return  template % kwargs

#==================================================================================================================================================================================
# TABLA DE PRÉSTAMOS
#==================================================================================================================================================================================
class Lent_to(this.Base):
    # Nombre
    __tablename__ = 'lent_to'

    # Atributos
    book_id               = Column(GUID, nullable=False, primary_key=True)
    ci                    = Column(Integer, nullable=False, primary_key=True)
    lender_clerk          = Column(String, nullable=False, primary_key=True)
    start_description     = Column(String, nullable=False, primary_key=True)
    start_time            = Column(DateTime, nullable=False, default=datetime.now, primary_key=True)
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
    )

    # Representación de una instancia de la clase
    def __repr__(self):
        kwargs = (str(self.book_id), str(self.ci), self.lender_clerk, self.start_description, str(self.start_time), str(self.estimated_return_time),
            self.receiver_clerk, str(self.return_time), self.return_description)
        template = "<Written_by(book_id='%s', ci='%s', lender_clerk='%s', start_description='%s', start_time='%s', estimated_return_time='%s', "
        template += "receiver_clerk=='%s', return_time=='%s', return_description=='%s')>"
        return  template % kwargs
