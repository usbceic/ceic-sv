-- Base de Datos del Sistema de Ventas del CEIC
-- Hecho por Christian Oliveros

-- Tipo para Funcion de Checkeo al hacer login (db_user)

CREATE TYPE user_info_type
AS (
   username TEXT,
   firstname TEXT,
   lastname TEXT,
   email TEXT,
   permission_mask INTEGER,
   profile TEXT,
   description TEXT,
   creation_date TIMESTAMP,
   last_login TIMESTAMP
);