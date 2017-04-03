-- Base de Datos del Sistema de Ventas del CEIC
-- Hecho por Christian Oliveros

-- Quitar triggers y sus funciones
\ir remove_triggers.sql

-- Quitar funciones Generales si existen
\ir remove_functions.sql

-- Quitar tablas 
\ir remove_tables.sql

-- Quitar types y Enums
\ir remove_types.sql

-- Quitar extensiones
\ir remove_extensions.sql