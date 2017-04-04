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
RETURNS SETOF user_info_type AS 
$check_password$
    UPDATE db_user
    SET last_login = NOW()
    WHERE username = $1 AND user_password = $2
    RETURNING username, firstname, lastname, email, permission_mask, profile, description, creation_date, last_login;
$check_password$  
LANGUAGE SQL;

-- Funcion para cambiar la contrasena de usuario y devolver su email (db_user).
-- PELIGROSO DEJAR QUE USUARIOS USEN ESTO A LO LOCO
CREATE OR REPLACE FUNCTION lost_password(uname TEXT, pass TEXT)
RETURNS SETOF TEXT AS 
$lost_password$
    UPDATE db_user
    SET user_password = $2
    WHERE username = $1
    RETURNING email;
$lost_password$  
LANGUAGE SQL;

-- Funcion para cambiar contrasena de usuario dado la contrasena anterior (db_user)
-- Devuelve true si ocurrio el cambio
-- MAS SEGURA QUE LA FUNCION ANTERIOR
CREATE OR REPLACE FUNCTION change_password(uname TEXT, oldpssw TEXT, newpssw TEXT)
RETURNS BOOLEAN AS
$change_password$
BEGIN
	UPDATE db_user
	SET user_password = $3
	WHERE username = $1 AND user_password = $2;
	RETURN FOUND;
END;
$change_password$
LANGUAGE plpgsql;

-- Funcion para actualizar informacion de usuario, Requiere su contrasena. NO CAMBIA CONTRASENA NI PERMISOS
-- Devuelve true si ocurrio el cambio
CREATE OR REPLACE FUNCTION update_user(
	username TEXT, 
	user_password TEXT, 
	firstname TEXT DEFAULT NULL, 
	lastname TEXT DEFAULT NULL, 
	email TEXT DEFAULT NULL, 
	profile TEXT DEFAULT NULL, 
	description TEXT DEFAULT NULL)
RETURNS BOOLEAN AS
$update_user$
BEGIN
	UPDATE db_user AS U
	SET firstname = COALESCE(update_user.firstname, U.firstname),
	    lastname = COALESCE(update_user.lastname, U.lastname),
	    email = COALESCE(update_user.email, U.email),
	    profile = COALESCE(update_user.profile, U.profile),
	    description = COALESCE(update_user.description, U.description)
	WHERE U.username = update_user.username AND U.user_password = update_user.user_password;
	RETURN FOUND;
END;
$update_user$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_permission_mask(username TEXT, permission_mask INTEGER)
RETURNS BOOLEAN AS
$update_permission_mask$
BEGIN
	UPDATE db_user AS U
	SET permission_mask = update_permission_mask.permission_mask
	WHERE U.username = update_permission_mask.username;
	RETURN FOUND;
END;
$update_permission_mask$
LANGUAGE plpgsql;


-- Funcion obtener la informacion de los usuarios del sistema (sin contrasena) (db_user)
CREATE OR REPLACE FUNCTION get_users_info(orderByLastLogin BOOLEAN DEFAULT true, descendingOrderByLastLogin BOOLEAN DEFAULT false)
RETURNS SETOF user_info_type AS 
$get_users_info$
BEGIN
	IF (orderByLastLogin) THEN
	   IF (NOT descendingOrderByLastLogin) THEN
	      RETURN QUERY
	      SELECT username, firstname, lastname, email, permission_mask, profile, description, creation_date, last_login
	      FROM db_user
	      ORDER BY last_login, username;
	   ELSE
	      RETURN QUERY
	      SELECT username, firstname, lastname, email, permission_mask, profile, description, creation_date, last_login
	      FROM db_user
	      ORDER BY last_login DESC, username;
	   END IF;
	ELSE
	   RETURN QUERY
	   SELECT username, firstname, lastname, email, permission_mask, profile, description, creation_date, last_login
	   FROM db_user
	   ORDER BY username;
	END IF;
END;
$get_users_info$  
LANGUAGE plpgsql;

-- Funcion ver la informacion de un usuario dado su username (db_user)
CREATE OR REPLACE FUNCTION get_user_info(uname TEXT)
RETURNS SETOF user_info_type AS 
$get_user_info$
    SELECT username, firstname, lastname, email, permission_mask, profile, description, creation_date, last_login
    FROM db_user
    WHERE username = $1;
$get_user_info$  
LANGUAGE SQL;


-- TODO hacer trigger de devoluciones por saldo (No cash)
-- TODO hacer funcion de actualizacion de cierre de turno/dia/trimestre que calcule todo 
-- (Contar entradas cash en checkout y entrada de dinero por transferencia. No contar como entrada checkout pagados con saldo)
-- (Contar salidas de dinero por devoluciones pagadas con cash)