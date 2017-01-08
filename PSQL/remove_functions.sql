-- Base de Datos del Sistema de Ventas del CEIC
-- Hecho por Christian Oliveros

-- Quitar funciones Generales si existen
DROP FUNCTION IF EXISTS get_user_info(TEXT);

DROP FUNCTION IF EXISTS get_users_info(BOOLEAN, BOOLEAN);

DROP FUNCTION IF EXISTS change_password(TEXT, TEXT, TEXT);

DROP FUNCTION IF EXISTS lost_password(TEXT, TEXT);

DROP FUNCTION IF EXISTS check_password(TEXT, TEXT);

DROP FUNCTION IF EXISTS create_db_user(TEXT, TEXT, TEXT, TEXT, TEXT, INTEGER, TEXT, TEXT);