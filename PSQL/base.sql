-- Base de Datos del Sistema de Ventas del CEIC
-- Hecho por Christian Oliveros

-- Extension para manejo de seriales unicos
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de usuarios
CREATE TABLE db_user (
	username TEXT 
	         CONSTRAINT pk_db_user
	         PRIMARY KEY,
    user_password TEXT NOT NULL,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    email TEXT NOT NULL,
    permission_mask INTEGER NOT NULL,
    profile TEXT DEFAULT NULL,
    description TEXT,
    creation_date TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Tabla de proveedores
CREATE TABLE provider (
	provider_name TEXT NOT NULL
	     CONSTRAINT pk_provider
	     PRIMARY KEY,
	phone TEXT,
	email TEXT,
	pay_information TEXT NOT NULL,
	description TEXT,
	category TEXT
);


-- Tabla de productos
CREATE TABLE product (
	id UUID DEFAULT uuid_generate_v4() 
	   CONSTRAINT pk_product
	   PRIMARY KEY,
	product_name TEXT NOT NULL,
	price NUMERIC NOT NULL
	      CONSTRAINT exp_product_valid_price
	      CHECK (price >= 0),
	remaining INTEGER NOT NULL DEFAULT 0
	          CONSTRAINT exp_product_valid_remaining
	          CHECK (remaining >= 0),
	remaining_lots INTEGER NOT NULL DEFAULT 0
	          CONSTRAINT exp_product_valid_remaining_lots
	          CHECK (remaining_lots >= 0),
	available BOOLEAN NOT NULL DEFAULT false,
	description TEXT,
	category TEXT
);


-- Tabla de lotes
CREATE TABLE lot (
	id UUID NOT NULL DEFAULT uuid_generate_v4(),
	product_id UUID NOT NULL
	           CONSTRAINT fk_lot_product
	           REFERENCES product (id)
	           ON DELETE CASCADE
	           ON UPDATE CASCADE,
	CONSTRAINT pk_lot
	PRIMARY KEY (id, product_id),
    provider_id TEXT NOT NULL
             CONSTRAINT fk_lot_provider
             REFERENCES provider (provider_name)
             ON UPDATE CASCADE,
    received_by TEXT NOT NULL
                CONSTRAINT fk_lot_db_user
                REFERENCES db_user (username),
    cost NUMERIC NOT NULL
         CONSTRAINT exp_lot_valid_cost
         CHECK (cost >= 0),
	quantity INTEGER NOT NULL
	         CONSTRAINT exp_lot_valid_quantity
	         CHECK (quantity >= 0),
    adquisition_date DATE NOT NULL DEFAULT NOW(),
    perishable BOOLEAN NOT NULL DEFAULT false,
    expiration_date DATE
                    CONSTRAINT exp_lot_valid_expiration_date
                    CHECK ((NOT perishable AND expiration_date IS NULL) OR (perishable AND expiration_date IS NOT NULL AND adquisition_date <= expiration_date)),
    available BOOLEAN NOT NULL DEFAULT false
              CONSTRAINT exp_lot_valid_available
              CHECK(NOT available OR (available AND quantity > 0)),
    current BOOLEAN NOT NULL DEFAULT false
            CONSTRAINT exp_lot_valid_current
            CHECK (NOT current OR (available AND current)),
    description TEXT,
	category TEXT
);

-- Tabla de servicios
CREATE TABLE service (
	id UUID DEFAULT uuid_generate_v4() 
	   CONSTRAINT pk_service
	   PRIMARY KEY,
	service_name TEXT NOT NULL,
	price NUMERIC NOT NULL
	      CONSTRAINT exp_service_valid_price
	      CHECK (price >= 0),
	available BOOLEAN NOT NULL DEFAULT false,
	description TEXT,
	category TEXT
);


-- Tabla de clientes
CREATE TABLE client (
	ci INTEGER 
	   CONSTRAINT pk_client
	   PRIMARY Key,
	carnet TEXT DEFAULT NULL
	       CONSTRAINT ak_client
	       UNIQUE,
	firstname TEXT NOT NULL,
	lastname TEXT NOT NULL,
	phone TEXT DEFAULT NULL,
	debt_permission BOOLEAN NOT NULL DEFAULT false,
	book_permission BOOLEAN NOT NULL DEFAULT true,
	blocked BOOLEAN NOT NULL DEFAULT false,
	balance NUMERIC NOT NULL DEFAULT 0
	        CONSTRAINT exp_client_valid_balance
	        CHECK (balance >= 0 OR debt_permission),
	last_seen DATE DEFAULT NOW()
);

-- Tabla de Compras
CREATE TABLE purchase (
	id UUID DEFAULT uuid_generate_v4() 
	   CONSTRAINT pk_purchase
	   PRIMARY KEY,
	ci INTEGER NOT NULL
	   CONSTRAINT fk_purchase_client
	   REFERENCES client (ci),
	clerk TEXT NOT NULL
	      CONSTRAINT fk_purchase_db_user
	      REFERENCES db_user (username),
	total NUMERIC NOT NULL DEFAULT 0
	      CONSTRAINT exp_purchase_valid_total
	      CHECK (total >= 0),
	-- Calculo del interes es el siguiente TotalPagar = total * (1 + interest)
	interest NUMERIC NOT NULL DEFAULT 0
	         CONSTRAINT exp_purchase_interest
	         CHECK (interest >= 0),
	purchase_date TIMESTAMP NOT NULL DEFAULT NOW(),
	locked BOOLEAN NOT NULL DEFAULT false,
	debt BOOLEAN NOT NULL DEFAULT false,
	payed BOOLEAN NOT NULL DEFAULT false
	      CONSTRAINT exp_purchase_valid_payed
	      CHECK ((payed AND locked) OR NOT payed),
	payed_date TIMESTAMP DEFAULT NULL
	           CONSTRAINT exp_purchase_valid_payed_date
	           CHECK ((payed AND payed_date IS NOT NULL) OR (NOT payed AND payed_date IS NULL)),
	payed_to TEXT DEFAULT NULL
	            CONSTRAINT fk_purchase_db_user_payed_to
	            REFERENCES db_user (username)
	            CONSTRAINT exp_purchase_valid_payed_to
	            CHECK ((payed AND payed_to IS NOT NULL) OR (NOT payed AND payed_to IS NULL))
);

-- Tabla de pagos de orden de compra
CREATE TABLE checkout (
	id UUID NOT NULL DEFAULT uuid_generate_v4(),
	purchase_id UUID NOT NULL
	            CONSTRAINT fk_checkout_purchase
	            REFERENCES purchase (id),
	CONSTRAINT pk_checkout
	PRIMARY KEY (id, purchase_id),
	pay_date TIMESTAMP NOT NULL DEFAULT NOW(),
	amount NUMERIC NOT NULL
	       CONSTRAINT exp_checkout_valid_amount
	       CHECK (amount > 0),
	with_balance BOOLEAN NOT NULL DEFAULT false,
	description TEXT NOT NULL, -- Aqui va si fue con tarjeta de credito o efectivo, etc,
	payed BOOLEAN NOT NULL DEFAULT false
);

-- Tabla de lista de productos de orden de compra
CREATE TABLE product_list (
	product_id UUID NOT NULL 
	           CONSTRAINT fk_product_list_product
	           REFERENCES product (id),
	purchase_id UUID NOT NULL
	            CONSTRAINT fk_product_list_purchase
	            REFERENCES purchase (id),
	CONSTRAINT pk_product_list
	PRIMARY KEY (product_id, purchase_id),
	price NUMERIC NOT NULL DEFAULT 0
	      CONSTRAINT exp_product_list_valid_price
	      CHECK (price > 0),
	amount INTEGER NOT NULL
           CONSTRAINT exp_product_list_valid_amount
           CHECK (amount > 0),
    locked BOOLEAN NOT NULL DEFAULT false,
    payed BOOLEAN NOT NULL DEFAULT false
	      CONSTRAINT exp_product_list_valid_payed
	      CHECK ((payed AND locked) OR NOT payed)
);

-- Tabla de lista de servicios de orden de compra
CREATE TABLE service_list (
	service_id UUID NOT NULL 
	           CONSTRAINT fk_service_list_service
	           REFERENCES service (id),
	purchase_id UUID NOT NULL
	            CONSTRAINT fk_service_list_purchase
	            REFERENCES purchase (id),
	CONSTRAINT pk_service_list
	PRIMARY KEY (service_id, purchase_id),
	price NUMERIC NOT NULL DEFAULT 0
	      CONSTRAINT exp_service_list_valid_price
	      CHECK (price > 0),
	amount INTEGER NOT NULL
           CONSTRAINT exp_service_list_valid_amount
           CHECK (amount > 0),
    locked BOOLEAN NOT NULL DEFAULT false,
    payed BOOLEAN NOT NULL DEFAULT false
	      CONSTRAINT exp_service_list_valid_payed
	      CHECK ((payed AND locked) OR NOT payed)
);

-- Tabla de lista de productos de orden de compra
CREATE TABLE reverse_product_list (
	product_id UUID NOT NULL,
	purchase_id UUID NOT NULL,
	CONSTRAINT fk_reverse_product_list_service_list
	FOREIGN KEY (product_id, purchase_id)
	REFERENCES  product_list(product_id, purchase_id),
	CONSTRAINT pk_reverse_product_list
	PRIMARY KEY (product_id, purchase_id),
	clerk TEXT NOT NULL
	      CONSTRAINT fk_reverse_product_list_db_user
	      REFERENCES db_user (username),
	reverse_date TIMESTAMP NOT NULL DEFAULT NOW(),
	-- Cantidad del producto que fue retornada. Para calculos de dinero devuelto
	amount INTEGER NOT NULL
           CONSTRAINT exp_product_list_valid_amount
           CHECK (amount > 0),
    -- Si el dinero devuelo fue en efectivo de caja
    cash BOOLEAN DEFAULT true,
    description TEXT NOT NULL	
);

-- Tabla de reversar lista de servicios de orden de compra
CREATE TABLE reverse_service_list (
	service_id UUID NOT NULL,
	purchase_id UUID NOT NULL,
	CONSTRAINT fk_reverse_service_list_service_list
	FOREIGN KEY (service_id, purchase_id)
	REFERENCES  service_list(service_id, purchase_id),
	CONSTRAINT pk_reverse_service_list
	PRIMARY KEY (service_id, purchase_id),
	clerk TEXT NOT NULL
	      CONSTRAINT fk_reverse_service_list_db_user
	      REFERENCES db_user (username),
	reverse_date TIMESTAMP NOT NULL DEFAULT NOW(),
	-- Cantidad del servicio que fue retornada. Para calculos de dinero devuelto
	amount INTEGER NOT NULL
           CONSTRAINT exp_reverse_service_list_valid_amount
           CHECK (amount > 0),
    -- Si el dinero devuelo fue en efectivo de caja
    cash BOOLEAN DEFAULT true,
    description TEXT NOT NULL
);

-- Tabla de transferencias
CREATE TABLE transfer (
	id UUID DEFAULT uuid_generate_v4()
	   CONSTRAINT pk_transfer
	   PRIMARY KEY,
	ci INTEGER NOT NULL
	   CONSTRAINT fk_transfer_client
	   REFERENCES client (ci),
	clerk TEXT NOT NULL
	      CONSTRAINT fk_transfer_db_user
	      REFERENCES db_user (username),
	transfer_date TIMESTAMP NOT NULL DEFAULT NOW(),
	amount INTEGER NOT NULL
           CONSTRAINT exp_transfer_valid_amount
           CHECK (amount > 0),
    bank TEXT NOT NULL,
    confirmation_code TEXT NOT NULL,
    description TEXT NOT NULL
);

-- Tabla de Registro de Operaciones de Caja
CREATE TABLE operation_log (
	id UUID DEFAULT uuid_generate_v4()
	   CONSTRAINT pk_operation_log
	   PRIMARY KEY,
	clerk TEXT NOT NULL
	      CONSTRAINT fk_operation_log_db_user
	      REFERENCES db_user (username),
	-- op_type
	-- 0 es Apertura/Cierre de trimestre
	-- 1 es Apertura/Cierre de Dia
	-- 2 es Apertura/Cierre de Turno de Persona
	-- 3 es Correcion
	-- 4 es Retiro/Devolucion de Dinero (Si se tomo de caja marcar de ahi como menos dinero, ademas del balance negativo)
	op_type INTEGER NOT NULL,
	open_record BOOLEAN DEFAULT false
	            CONSTRAINT exp_operation_log_valid_open_record
	            CHECK (open_record IS NULL OR (op_type = 0 OR op_type = 1 OR op_type = 2)),
	recorded TIMESTAMP NOT NULL DEFAULT NOW(),
	-- Movimientos por transferencia / Dinero no en Caja ya contabilizado
	transfer_balance NUMERIC NOT NULL DEFAULT 0,
	-- Movimientos en efectivo
	cash_balance NUMERIC NOT NULL DEFAULT 0,
	-- Efectivo actual en caja
	cash_total NUMERIC NOT NULL,
	-- Dinero desde el comienzo de trimestre
	total_money NUMERIC NOT NULL
);


-- Tabla de lenguajes validos
CREATE TABLE valid_language (
	lang_name TEXT 
	          CONSTRAINT pk_valid_language
	          PRIMARY KEY
);

-- Tabla de Libros
CREATE TABLE book (
	id UUID DEFAULT uuid_generate_v4()
	   CONSTRAINT pk_book
	   PRIMARY KEY,
	title TEXT NOT NULL,
	isbn TEXT DEFAULT NULL
	     CONSTRAINT ak_book
	     UNIQUE,
	edition INTEGER NOT NULL DEFAULT 1
	        CONSTRAINT exp_book_valid_edition
	        CHECK (edition > 0),
	book_year DATE NOT NULL,
	lang TEXT NOT NULL
	     CONSTRAINT fk_book_valid_language
	     REFERENCES valid_language (lang_name),
	quantity INTEGER NOT NULL DEFAULT 1
	         CONSTRAINT exp_book_valid_quantity
	         CHECK (quantity > 0),
	quantity_lent INTEGER NOT NULL DEFAULT 0
	              CONSTRAINT exp_book_valid_quantity_lent
	              CHECK (quantity_lent >= 0)
);

-- Tabla de Asignaturas
CREATE TABLE subject (
	subject_code TEXT
	             CONSTRAINT pk_subject
	             PRIMARY KEY,
	subject_name TEXT NOT NULL
);

-- Tabla de Autores
CREATE TABLE author (
	firstname TEXT NOT NULL,
	lastname TEXT NOT NULL,
	middlename TEXT DEFAULT NULL,
	second_lastname TEXT DEFAULT NULL,
	birthdate DATE DEFAULT NULL,
	nationality TEXT DEFAULT NULl,
	CONSTRAINT pk_author
	PRIMARY KEY (firstname, lastname, middlename, second_lastname, birthdate, nationality)
);

-- Tabla que asocia libros con asignaturas
CREATE TABLE associated_with (
	book_id UUID NOT NULL
	        CONSTRAINT fk_associated_with_book
	        REFERENCES book (id),
	subject_code TEXT NOT NULL
	             CONSTRAINT fk_associated_with_subject
	             REFERENCES subject (subject_code)
	             ON UPDATE CASCADE,
	CONSTRAINT pk_associated_with
	PRIMARY KEY (book_id, subject_code)
);


-- Tabla de Quien escribio el libro
CREATE TABLE written_by (
	book_id UUID NOT NULL
	        CONSTRAINT fk_written_by_book
	        REFERENCES book (id),
	firstname TEXT NOT NULL,
	lastname TEXT NOT NULL,
	middlename TEXT DEFAULT NULL,
	second_lastname TEXT DEFAULT NULL,
	birthdate DATE DEFAULT NULL,
	nationality TEXT DEFAULT NULl,
	CONSTRAINT fk_written_by_author
	FOREIGN KEY (firstname, lastname, middlename, second_lastname, birthdate, nationality)
	REFERENCES author (firstname, lastname, middlename, second_lastname, birthdate, nationality),
	CONSTRAINT pk_written_by
	PRIMARY KEY (book_id, firstname, lastname, middlename, second_lastname, birthdate, nationality)
);


CREATE TABLE lent_to (
	book_id UUID NOT NULL
	        CONSTRAINT fk_lent_to_book
	        REFERENCES book (id),
	ci INTEGER NOT NULL
	   CONSTRAINT fk_lent_to_client
	   REFERENCES client (ci),
	lender_clerk TEXT NOT NULL
	      CONSTRAINT fk_lent_to_db_user_lender
	      REFERENCES db_user (username),
	-- Condiciones del Libro principalmente
	start_description TEXT NOT NULL,
	start_time TIMESTAMP NOT NULL DEFAULT NOW(),
	estimated_return_time TIMESTAMP NOT NULL
	                      CONSTRAINT exp_lent_to_valid_estimated_return_time
	                      CHECK (start_time <= estimated_return_time),
	receiver_clerk TEXT DEFAULT NULL
	      CONSTRAINT fk_lent_to_db_user_receiver
	      REFERENCES db_user (username),
	return_time TIMESTAMP DEFAULT NULL
	            CONSTRAINT exp_lent_to_valid_return_time
	            CHECK ((receiver_clerk IS NULL AND return_time IS NULL) OR (receiver_clerk IS NOT NULL AND return_time IS NOT NULL AND start_time <= return_time)),
	-- Condiciones del Libro principalmente
	return_description TEXT DEFAULT NULL
	                   CONSTRAINT exp_lent_to_valid_return_description
	                   CHECK ((receiver_clerk IS NULL AND return_description IS NULL) OR (receiver_clerk IS NOT NULL AND return_description IS NOT NULL))
);