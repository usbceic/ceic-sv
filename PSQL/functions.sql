-- Base de Datos del Sistema de Ventas del CEIC
-- Hecho por Christian Oliveros

-- Funcion de Checkeo al hacer login (db_user)

CREATE TYPE check_password_type
AS (
   firstname TEXT,
   lastname TEXT,
   email TEXT,
   permission_mask INTEGER,
   profile TEXT,
   description TEXT
);

CREATE OR REPLACE FUNCTION check_password(uname TEXT, pass TEXT)
RETURNS SETOF check_password_type AS 
$check_password$
    UPDATE db_user
    SET last_login = NOW()
    WHERE username = $1 AND user_password = $2
    RETURNING firstname, lastname, email, permission_mask, profile, description;
$check_password$  
LANGUAGE SQL;