-- Base de Datos del Sistema de Ventas del CEIC
-- Hecho por Christian Oliveros

-- Quitar funciones Generales si existen
DROP FUNCTION IF EXISTS check_password(TEXT, TEXT);

DROP FUNCTION IF EXISTS create_db_user(TEXT, TEXT, TEXT, TEXT, TEXT, INTEGER, TEXT, TEXT);