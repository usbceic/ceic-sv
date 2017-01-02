-- Base de Datos del Sistema de Ventas del CEIC
-- Hecho por Christian Oliveros

-- Tipo para Funcion de Checkeo al hacer login (db_user)

CREATE TYPE check_password_type
AS (
   firstname TEXT,
   lastname TEXT,
   email TEXT,
   permission_mask INTEGER,
   profile TEXT,
   description TEXT
);