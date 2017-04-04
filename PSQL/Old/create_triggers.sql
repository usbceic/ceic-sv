-- Base de Datos del Sistema de Ventas del CEIC
-- Hecho por Christian Oliveros

-- Tabla usuarios (db_user)
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
                       OLD.firstname || ' ' || OLD.lastname;
         NEW.creation_date := OLD.creation_date;
      END IF;
      -- Modificacion invalida de last_login
      IF (NEW.last_login < OLD.last_login OR current_timestamp < NEW.last_login) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar la fecha de ultimo login de manera invalida para: % - %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.username, 
                       OLD.firstname || ' ' || OLD.lastname;
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


-- Tabla de lotes (lot)
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

-- Tabla de clientes (client)
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
                       OLD.firstname || ' ' || OLD.lastname;
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


-- Tabla de Compras (purchase)
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
      IF (NEW.debt AND NOT (SELECT debt_permission FROM client WHERE ci = NEW.ci)) THEN
         RAISE EXCEPTION '[%] - El usuario "%" ha intendado insertar una compra marcada como deuda para un usuario que no puede tener deudas.', 
                       current_timestamp, 
                       current_user;
         RETURN NULL;
      END IF;      
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
     
      -- Solo deudas a clientes con permiso de deuda
      IF (NOT OLD.debt AND NEW.debt AND NOT (SELECT debt_permission FROM client WHERE ci = NEW.ci)) THEN
         RAISE EXCEPTION '[%] - El usuario "%" ha intendado insertar una compra marcada como deuda para un usuario que no puede tener deudas.', 
                       current_timestamp, 
                       current_user;
         RETURN NULL;
      END IF; 

      RETURN NEW;
   END IF;
END;
$purchase_integrity$  
LANGUAGE plpgsql;


CREATE TRIGGER purchase_integrity
BEFORE INSERT OR UPDATE ON purchase
FOR EACH ROW EXECUTE PROCEDURE purchase_integrity();

-- Trigger de lockdown de pago o lock de compra
CREATE OR REPLACE FUNCTION purchase_lockdown()
  RETURNS trigger AS
$purchase_lockdown$
BEGIN
   IF (TG_OP = 'UPDATE') THEN
      -- Bloquear las listas de Compras de lo Bloqueado
      IF (NOT OLD.locked AND NEW.locked) THEN
         UPDATE product_list
         SET locked = true
         WHERE purchase_id = OLD.id;

         UPDATE service_list
         SET locked = true
         WHERE purchase_id = OLD.id;
      END IF;

      -- Bloquear las listas de Compras de lo Pagado y el Checkout
      IF (NOT OLD.payer AND NEW.payed) THEN
         UPDATE product_list
         SET locked = true, payed = true
         WHERE purchase_id = OLD.id;

         UPDATE service_list
         SET locked = true, payed = true
         WHERE purchase_id = OLD.id;

         UPDATE checkout
         SET payed = true
         WHERE purchase_id = OLD.id;
      END IF;

      RETURN NEW;
   END IF;
END;
$purchase_lockdown$  
LANGUAGE plpgsql;

CREATE TRIGGER purchase_lockdown
AFTER UPDATE ON purchase
FOR EACH ROW EXECUTE PROCEDURE purchase_lockdown();

-- Trigger de validacion de pago de compra
CREATE OR REPLACE FUNCTION purchase_payed_validation()
  RETURNS trigger AS
$purchase_payed_validation$
BEGIN
   IF (TG_OP = 'UPDATE') THEN
      IF (OLD.payed != NEW.payed AND NEW.payed) THEN
         CREATE TEMPORARY TABLE temp_purchase_info
         (SELECT * FROM checkout WHERE purchase_id = OLD.id) 
         ON COMMIT DROP;

         IF ( (SELECT SUM(amount) FROM temp_purchase_info) != OLD.total * (1 + OLD.interest)) THEN
            RAISE NOTICE '[%] - El usuario "%" ha intendado marcar como pagada la compra "%" pero no la ha pagado correctamente.', 
                             current_timestamp, 
                             current_user
                             OLD.id;
            NEW.payed := false;
         END IF;
      END IF;
      RETURN NEW;
   END IF;
END;
$purchase_payed_validation$  
LANGUAGE plpgsql;

-- TODO terminar y arreglar esto


-- Tabla de pagos de orden de compra (checkout)
-- Trigger de evitar modificaciones ilegales a checkout y si es pagable contra el balance
CREATE OR REPLACE FUNCTION checkout_integrity()
  RETURNS trigger AS
$checkout_integrity$
BEGIN
   IF (TG_OP = 'INSERT') THEN
      NEW.payed = false;
      IF (NEW.amount <= 0 ) THEN
         RAISE EXCEPTION 'No se pueden insertar pagos negativos';
         RETURN NULL;
      END IF;
      IF (NEW.with_balance) THEN
         CREATE TEMPORARY TABLE temp_checkout_info
         (SELECT c.balance, p.id 
         	FROM client c 
         	JOIN purchase p 
         	ON c.ci = p.ci 
         	WHERE p.id = NEW.purchase_id)
         ON COMMIT DROP;
         -- Tiene que tener dinero
         IF ( (SELECT balance FROM temp_checkout_info WHERE id = NEW.purchase_id) - NEW.amount < 0)
            RAISE EXCEPTION '[%] - El usuario "%" ha intendado insertar un checkout de balance contra un usuario que no tiene fondos suficientes.', 
                          current_timestamp, 
                          current_user;
            RETURN NULL;
         END IF;
      END IF;
      RETURN NEW;
   END IF;
   IF (TG_OP = 'UPDATE') THEN
      -- No es modificable si ya fue pagado
      IF (OLD.payed) THEN
         RETURN OLD;
      END IF;
      IF (NEW.amount <= 0) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar el checkout "%" para tener un amount negativo.', 
                          current_timestamp, 
                          current_user
                          OLD.id || ' ' ||OLD.purchase_id;
         NEW.amount := OLD.amount;
      END IF;
      IF (NEW.with_balance AND NOT OLD.with_balance) THEN
         CREATE TEMPORARY TABLE temp_checkout_info
         (SELECT c.balance, p.id 
         	FROM client c 
         	JOIN purchase p 
         	ON c.ci = p.ci 
         	WHERE p.id = NEW.purchase_id)
         ON COMMIT DROP;
         -- Tiene que tener dinero
         IF ( (SELECT balance FROM temp_checkout_info WHERE id = NEW.purchase_id) - NEW.amount < 0)
            RAISE NOTICE '[%] - El usuario "%" ha intendado modificar el "%" checkout de balance contra un usuario que no tiene fondos suficientes.', 
                          current_timestamp, 
                          current_user
                          OLD.id || ' ' ||OLD.purchase_id;
            NEW.with_balance := false;
         END IF;
      END IF;
      RETURN NEW;
   END IF;
END;
$checkout_integrity$  
LANGUAGE plpgsql;

-- TODO terminar y arreglar esto

CREATE TRIGGER checkout_integrity
BEFORE INSERT OR UPDATE ON checkout
FOR EACH ROW EXECUTE PROCEDURE checkout_integrity();

-- Tabla de lista de productos de orden de compra (product_list)
-- Trigger de integridad a lista de productos
CREATE OR REPLACE FUNCTION product_list_integrity()
  RETURNS trigger AS
$product_list_integrity$
BEGIN
   IF (TG_OP = 'INSERT') THEN
      NEW.locked = false;
      NEW.payed = false;
      RETURN NEW;
   END IF;
   IF (TG_OP = 'UPDATE') THEN
      -- No es modificable si ya fue pagado
      IF (OLD.payed) THEN
         RETURN OLD;
      END IF;
      IF (OLD.product_id != NEW.product_id) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar el producto de product_list: %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.purchase_id || ' ' || OLD.product_id;
         NEW.product_id := OLD.product_id;
      END IF;
      IF (OLD.purchase_id != NEW.purchase_id) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar el purchase_id de product_list: %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.purchase_id || ' ' || OLD.product_id;
         NEW.purchase_id := OLD.purchase_id;
      END IF;
      -- Bloquear las listas de Compras de lo Bloqueado
      IF (OLD.locked AND OLD.amount != NEW.amount) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar la cantidad de product_list: %. Que esta bloqueado', 
                       current_timestamp, 
                       current_user, 
                       OLD.purchase_id || ' ' || OLD.product_id;
         NEW.amount := OLD.amount;
      END IF;
      RETURN NEW;
   END IF;
END;
$product_list_integrity$  
LANGUAGE plpgsql;

CREATE TRIGGER product_list_integrity
BEFORE INSERT OR UPDATE ON product_list
FOR EACH ROW EXECUTE PROCEDURE product_list_integrity();

-- Tabla de lista de servicios de orden de compra (service_list)
-- Trigger de integridad a lista de productos
CREATE OR REPLACE FUNCTION service_list_integrity()
  RETURNS trigger AS
$service_list_integrity$
BEGIN
   IF (TG_OP = 'INSERT') THEN
      NEW.locked = false;
      NEW.payed = false;
      RETURN NEW;
   END IF;
   IF (TG_OP = 'UPDATE') THEN
      -- No es modificable si ya fue pagado
      IF (OLD.payed) THEN
         RETURN OLD;
      END IF;
      IF (OLD.service_id != NEW.service_id) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar el producto de product_list: %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.purchase_id || ' ' || OLD.service_id;
         NEW.service_id := OLD.service_id;
      END IF;
      IF (OLD.purchase_id != NEW.purchase_id) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar el purchase_id de product_list: %.', 
                       current_timestamp, 
                       current_user, 
                       OLD.purchase_id || ' ' || OLD.service_id;
         NEW.purchase_id := OLD.purchase_id;
      END IF;
      -- Bloquear las listas de Compras de lo Bloqueado
      IF (OLD.locked AND OLD.amount != NEW.amount) THEN
         RAISE NOTICE '[%] - El usuario "%" ha intendado modificar la cantidad de product_list: %. Que esta bloqueado', 
                       current_timestamp, 
                       current_user, 
                       OLD.purchase_id || ' ' || OLD.service_id;
         NEW.amount := OLD.amount;
      END IF;
      RETURN NEW;
   END IF;
END;
$service_list_integrity$  
LANGUAGE plpgsql;

CREATE TRIGGER service_list_integrity
BEFORE INSERT OR UPDATE ON service_list
FOR EACH ROW EXECUTE PROCEDURE service_list_integrity();


-- TODO hacer trigger de reverse_list y de transfer. Trigger de integridad de operation_log. Trigger de revisar si es posible prestar libro a cliente