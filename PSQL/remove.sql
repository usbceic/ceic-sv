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


-- Quitar funciones
DROP FUNCTION IF EXISTS check_password(TEXT, TEXT);


-- Quitar tablas si existian
DROP TABLE IF EXISTS lent_to;

DROP TABLE IF EXISTS written_by;

DROP TABLE IF EXISTS associated_with;

DROP TABLE IF EXISTS author;

DROP TABLE IF EXISTS subject;

DROP TABLE IF EXISTS book;

DROP TABLE IF EXISTS valid_language;

DROP TABLE IF EXISTS operation_log;

DROP TABLE IF EXISTS transfer;

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


-- Quitar types
DROP TYPE IF EXISTS check_password_type;


-- Quitar extensiones
DROP EXTENSION IF EXISTS "uuid-ossp";