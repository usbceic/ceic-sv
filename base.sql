-- Base de Datos del Sistema de Ventas del CEIC
-- Hecho por Crhistian Oliveros

-- Extension para manejo de seriales unicos
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Quitar triggers si existian
DROP TRIGGER IF EXISTS purchase_integrity ON purchase;

DROP TRIGGER IF EXISTS db_user_integrity ON db_user;

DROP TRIGGER IF EXISTS lot_integrity ON lot;

DROP TRIGGER IF EXISTS lot_new_insert ON lot;

DROP TRIGGER IF EXISTS client_integrity ON client;

-- Quitar tablas si existian
DROP TABLE IF EXISTS checkout;

DROP TABLE IF EXISTS purchase;

DROP TABLE IF EXISTS client;

DROP TABLE IF EXISTS service;

DROP TABLE IF EXISTS lot;

DROP TABLE IF EXISTS product;

DROP TABLE IF EXISTS provider;

DROP TABLE IF EXISTS db_user;

-- Tabla de usuarios

CREATE TABLE db_user (
	username TEXT 
	         CONSTRAINT pk_db_user
	         PRIMARY KEY,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    lastname TEXT NOT NULL,
    email TEXT NOT NULL,
    permission_mask INTEGER NOT NULL,
    profile TEXT DEFAULT NULL,
    description TEXT,
    creation_date TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Trigger de proteccion de creation_date y last_login
CREATE OR REPLACE FUNCTION db_user_integrity()
  RETURNS trigger AS
$db_users$
BEGIN
   IF (TG_OP = 'INSERT') THEN
      NEW.creation_date := current_timestamp;
      NEW.last_login := current_timestamp;
   	  RETURN NEW;
   END IF;

   IF (TG_OP = 'UPDATE') THEN
      -- Modificacion ilegal de fecha de creacion
      IF (OLD.creation_date != NEW.creation_date) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar la fecha de registro para: % - %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.username, 
                       OLD.name || ' ' || OLD.lastname;
         NEW.creation_date := OLD.creation_date;
      END IF;
      -- Modificacion invalida de last_login
      IF (NEW.last_login < OLD.last_login OR current_timestamp < NEW.last_login) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar la fecha de ultimo login de manera invalida para: % - %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.username, 
                       OLD.name || ' ' || OLD.lastname;
         NEW.last_login := OLD.last_login;
      END IF;
      RETURN NEW;
   END IF;
END;
$db_users$  
LANGUAGE plpgsql;

CREATE TRIGGER db_user_integrity
BEFORE INSERT OR UPDATE ON db_user
FOR EACH ROW EXECUTE PROCEDURE db_user_integrity();


-- Tabla de proveedores

CREATE TABLE provider (
	name TEXT NOT NULL
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
	name TEXT NOT NULL,
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
             REFERENCES provider (name)
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

-- Trigger de proteccion de tabla lot
CREATE OR REPLACE FUNCTION lot_integrity()
  RETURNS trigger AS
$lot_integrity$
BEGIN
   IF (TG_OP = 'INSERT') THEN
      NEW.adquisition_date := current_timestamp;
      -- Solo un current a la vez
      IF (NEW.current AND NOT EXISTS (SELECT * FROM lot WHERE product_id = NEW.product_id AND current)) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado insertar un lote current a un producto que ya tiene current',
                          current_timestamp,
                          current_user;
         NEW.current := false;
      END IF;
      -- Tiene que haber por lo menos un producto en el lote
      IF (NEW.quantity < 1) THEN
         RAISE EXCEPTION '[%] - El usuario "%" ha intendado insertar un lote vacio',
                          current_timestamp,
                          current_user;
          RETURN NULL;
      END IF;
   	  RETURN NEW;
   END IF;

   IF (TG_OP = 'UPDATE') THEN
      -- Modificacion ilegal de proveedor
      IF (OLD.provider_id != NEW.provider_id) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar proveedor para el lote: %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.id;
         NEW.provider_id := OLD.provider_id;
      END IF;
      -- Modificacion ilegal de quien lo recibio
      IF (OLD.received_by != NEW.received_by) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar quien recibio para el lote: %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.id;
         NEW.received_by := OLD.received_by;
      END IF;
      -- Modificacion ilegal de fecha de adquisicion
      IF (OLD.adquisition_date != NEW.adquisition_date) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar la fecha de adquisicion para el lote: %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.id;
         NEW.adquisition_date := OLD.adquisition_date;
      END IF;
      -- Modificacion ilegal de costo
      IF (OLD.cost != NEW.cost) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar el costo para el lote: %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.id;
         NEW.cost := OLD.cost;
      END IF;
      -- Modificacion ilegal de expirable
      IF (OLD.perishable != NEW.perishable) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar expirable para el lote: %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.id;
         NEW.perishable := OLD.perishable;
      END IF;
      -- Modificacion ilegal de fecha de expiracion
      IF (OLD.expiration_date != NEW.expiration_date) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar fecha de expiracion para el lote: %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.id;
         NEW.expiration_date := OLD.expiration_date;
      END IF;
      -- Hacer cambios en caso de que cambie la cantidad
      IF (NEW.quantity != OLD.quantity) THEN
         IF (NEW.quantity < 0) THEN
            RAISE NOTICE '[%] - El usuario "%" ha intendado modificar cantidad para el lote: %. Pero es menor que 0', 
                          current_timestamp, 
                          current_user, 
                          OLD.id;
            RETURN NULL;
         ELSIF (NEW.quantity = 0) THEN
            NEW.available := false;
            NEW.current := false;
            IF (OLD.available) THEN
               UPDATE product 
               SET remaining = remaining - OLD.quantity, remaining_lots = remaining_lots - 1
               WHERE id = OLD.product_id;
            ELSE
               UPDATE product 
               SET remaining_lots = remaining_lots - 1
               WHERE id = OLD.product_id;
            END IF;
         ELSE
            UPDATE product 
            SET remaining = remaining - OLD.quantity + NEW.quantity
            WHERE id = OLD.product_id;
         END IF;  
      END IF;
      -- Solo un current a la vez
      IF (NEW.current != OLD.current AND NEW.current AND NOT EXISTS (SELECT * FROM lot WHERE product_id = NEW.product_id AND current)) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar current para el lote: %. Pero ya hay otro para el mismo producto', 
                       current_timestamp, 
                       current_user, 
                       OLD.id;
         NEW.current := false;
      END IF;
      -- Manejo de cambios de disponibilidad
      IF (NEW.available != OLD.available) THEN
         -- Si hubo ademas cambio de cantidad
         IF (OLD.quantity != NEW.quantity) THEN
            -- Solo importa el caso donde quite la disponibilidad, porque el otro caso se manejo en cambio de cantidad
            IF (NOT NEw.available) THEN
               UPDATE product 
               SET remaining = remaining - NEW.quantity 
               WHERE id = OLD.product_id;
            END IF;
         -- No hubo cambios de cantidad
         ELSE
            IF (NEW.available) THEN
               UPDATE product 
               SET remaining = remaining + NEW.quantity 
               WHERE id = OLD.product_id;
            ELSE
               UPDATE product 
               SET remaining = remaining - NEW.quantity 
               WHERE id = OLD.product_id;
            END IF;
         END IF;
         
      END IF;

      -- Precio con sentido
      IF (NEW.cost < 0) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar costo para el lote: %. Pero es menor que 0', 
                       current_timestamp, 
                       current_user, 
                       OLD.id;
         NEW.cost := OLD.cost;
      END IF;
      RETURN NEW;
   END IF;

   IF (TG_OP = 'DELETE') THEN
      IF (OLD.available) THEN
         UPDATE product 
         SET remaining = remaining - OLD.quantity, remaining_lots = remaining_lots - 1
         WHERE id = OLD.product_id;
      END IF;
      RETURN OLD;
   END IF;
END;
$lot_integrity$  
LANGUAGE plpgsql;

CREATE TRIGGER lot_integrity
BEFORE INSERT OR UPDATE OR DELETE ON lot
FOR EACH ROW EXECUTE PROCEDURE lot_integrity();

-- Trigger de automatizacion de tabla lot
CREATE OR REPLACE FUNCTION lot_new_insert()
  RETURNS trigger AS
$lot_new_insert$
BEGIN
   IF (TG_OP = 'INSERT') THEN
      IF (NEW.available) THEN
         UPDATE product 
         SET remaining = remaining + NEW.quantity, remaining_lots = remaining_lots + 1
         WHERE id = NEW.product_id;
      ELSE
         UPDATE product 
         SET remaining_lots = remaining_lots + 1
         WHERE id = NEW.product_id;
      END IF;
   	  RETURN NEW;
   END IF;
END;
$lot_new_insert$  
LANGUAGE plpgsql;

CREATE TRIGGER lot_new_insert
AFTER INSERT ON lot
FOR EACH ROW EXECUTE PROCEDURE lot_new_insert();


-- Tabla de servicios

CREATE TABLE service (
	id UUID DEFAULT uuid_generate_v4() 
	   CONSTRAINT pk_service
	   PRIMARY KEY,
	name TEXT NOT NULL,
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
	name TEXT NOT NULL,
	lastname TEXT NOT NULL,
	phone TEXT DEFAULT NULL,
	debt_permission BOOLEAN NOT NULL DEFAULT false,
	blocked BOOLEAN NOT NULL DEFAULT false,
	balance NUMERIC NOT NULL DEFAULT 0
	        CONSTRAINT exp_client_valid_balance
	        CHECK (balance >= 0 OR debt_permission),
	last_seen DATE DEFAULT NOW()
);

-- Trigger de proteccion de tabla client
CREATE OR REPLACE FUNCTION client_integrity()
  RETURNS trigger AS
$client_integrity$
BEGIN
   IF (TG_OP = 'INSERT') THEN
      NEW.last_seen := current_timestamp;
   	  RETURN NEW;
   END IF;

   IF (TG_OP = 'UPDATE') THEN
      -- Solo se puede cambiar last seen hacia adelante
      IF (OLD.last_seen != NEW.last_seen) THEN
         NEW.last_seen := current_timestamp;
      END IF;
      -- Control de no endeudarse mas
      IF (blocked AND OLD.balance > NEW.balance AND NEW.balance < 0) THEN
         RAISE EXCEPTION '[%] - El usuario "%" ha intendado el balance del cliente: %. Pero ya no se puede endeudar mas', 
                       current_timestamp, 
                       current_user, 
                       OLD.name || ' ' || OLD.lastname;
         RETURN NULL;
      END IF;
      RETURN NEW;
   END IF;
END;
$client_integrity$  
LANGUAGE plpgsql;



CREATE TRIGGER client_integrity
BEFORE INSERT OR UPDATE ON client
FOR EACH ROW EXECUTE PROCEDURE client_integrity();


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

-- Trigger de proteccion de tabla purchase
CREATE OR REPLACE FUNCTION purchase_integrity()
  RETURNS trigger AS
$purchase_integrity$
BEGIN
   IF (TG_OP = 'INSERT') THEN
      NEW.purchase_date := current_timestamp;
      NEW.total := 0;
      NEW.locked := false;
      NEW.payed := false;
   	  RETURN NEW;
   END IF;

   IF (TG_OP = 'UPDATE') THEN
      -- NO se puede modificar lo ya pagado
      IF (OLD.payed) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar la compra: %. Que ya estaba pagada.', 
                       current_timestamp, 
                       current_user, 
                       OLD.id;
         RETURN OLD;
      END IF;
      -- Modificacion Ilegal de fecha de compra
      IF (OLD.purchase_date != NEW.purchase_date) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar la fecha de compra de: %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.id;
         NEW.purchase_date := OLD.purchase_date;
      END IF;
      RETURN NEW;
   END IF;
END;
$purchase_integrity$  
LANGUAGE plpgsql;


CREATE TRIGGER purchase_integrity
BEFORE INSERT OR UPDATE ON purchase
FOR EACH ROW EXECUTE PROCEDURE purchase_integrity();


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
	       CONSTRAINT exp_balance_checkout_valid_amount
	       CHECK (amount > 0),
	with_balance BOOLEAN NOT NULL DEFAULT false,
	description TEXT NOT NULL -- Aqui va si fue con tarjeta de credito o efectivo, etc
);
