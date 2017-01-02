-- Base de Datos del Sistema de Ventas del CEIC
-- Hecho por Christian Oliveros

-- Funcion de Checkeo al hacer login (db_user)
DROP TYPE IF EXISTS check_password_type;

CREATE TYPE check_password_type
AS (
   name TEXT NOT NULL,
   lastname TEXT NOT NULL,
   email TEXT NOT NULL,
   permission_mask INTEGER NOT NULL,
   profile TEXT DEFAULT NULL,
   description TEXT
);

CREATE OR REPLACE FUNCTION check_password(uname TEXT, pass TEXT)
RETURNS SETOF check_password_type AS 
$check_password$
DECLARE 
passed check_password_type%ROWTYPE;
BEGIN
        UPDATE db_user
        SET last_login = NOW()
        WHERE username = $1 AND password = $2
        RETURNING name, lastname, email, permission_mask, profile, description INTO passed;

        RETURN passed;
END;
$check_password$  
LANGUAGE plpgsql;