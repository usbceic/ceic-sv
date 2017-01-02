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

-- Quitar tablas si existian
DROP TABLE IF EXISTS reverse_service_list;

DROP TABLE IF EXISTS reverse_product_list;

DROP TABLE IF EXISTS service_list;

DROP TABLE IF EXISTS product_list;

DROP TABLE IF EXISTS checkout;

DROP TABLE IF EXISTS purchase;

DROP TABLE IF EXISTS client;

DROP TABLE IF EXISTS service;

DROP TABLE IF EXISTS lot;

DROP TABLE IF EXISTS product;

DROP TABLE IF EXISTS provider;

DROP TABLE IF EXISTS db_user;