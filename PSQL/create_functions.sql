-- Base de Datos del Sistema de Ventas del CEIC
-- Hecho por Christian Oliveros

-- Funcion de Creacion de Usuario (db_user)
CREATE OR REPLACE FUNCTION create_db_user(uname TEXT, pass TEXT, firstname TEXT, lastname TEXT, email TEXT, permission_mask INTEGER, profile TEXT DEFAULT NULL, description TEXT DEFAULT NULL)
RETURNS VOID AS 
$create_db_user$
    INSERT INTO db_user 
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW());
$create_db_user$  
LANGUAGE SQL;

-- Funcion de Checkeo al hacer login (db_user)
CREATE OR REPLACE FUNCTION check_password(uname TEXT, pass TEXT)
RETURNS SETOF check_password_type AS 
$check_password$
    UPDATE db_user
    SET last_login = NOW()
    WHERE username = $1 AND user_password = $2
    RETURNING firstname, lastname, email, permission_mask, profile, description;
$check_password$  
LANGUAGE SQL;

-- Funcion para cambiar la contrasena de usuario y devolver su email (db_user)
CREATE OR REPLACE FUNCTION lost_password(uname TEXT, pass TEXT)
RETURNS SETOF TEXT AS 
$lost_password$
    UPDATE db_user
    SET user_password = $2
    WHERE username = $1
    RETURNING email;
$lost_password$  
LANGUAGE SQL;

-- TODO hacer trigger de devoluciones por saldo (No cash)
-- TODO hacer funcion de actualizacion de cierre de turno/dia/trimestre que calcule todo 
-- (Contar entradas cash en checkout y entrada de dinero por transferencia. No contar como entrada checkout pagados con saldo)
-- (Contar salidas de dinero por devoluciones pagadas con cash)