-- Base de Datos del Sistema de Ventas del CEIC
-- Hecho por Christian Oliveros

-- Quitar triggers si existian
DROP TRIGGER IF EXISTS service_list_integrity ON service_list;

DROP TRIGGER IF EXISTS product_list_integrity ON product_list;

DROP TRIGGER IF EXISTS checkout_integrity ON checkout;

DROP TRIGGER IF EXISTS purchase_lockdown ON purchase;

DROP TRIGGER IF EXISTS purchase_integrity ON purchase;

DROP TRIGGER IF EXISTS db_user_integrity ON db_user;

DROP TRIGGER IF EXISTS lot_integrity ON lot;

DROP TRIGGER IF EXISTS lot_new_insert ON lot;

DROP TRIGGER IF EXISTS client_integrity ON client;

-- Quitar Funciones de Triggers si existen
DROP FUNCTION IF EXISTS service_list_integrity();

DROP FUNCTION IF EXISTS product_list_integrity();

DROP FUNCTION IF EXISTS checkout_integrity();

DROP FUNCTION IF EXISTS purchase_payed_validation();

DROP FUNCTION IF EXISTS purchase_lockdown();

DROP FUNCTION IF EXISTS purchase_integrity();

DROP FUNCTION IF EXISTS client_integrity();

DROP FUNCTION IF EXISTS lot_new_insert();

DROP FUNCTION IF EXISTS lot_integrity();

DROP FUNCTION IF EXISTS db_user_integrity();