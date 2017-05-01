# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación de los métodos para manejar la sesión en la base de datos

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Christian Oliveros, 01christianol01@gmail.com

###################################################################################################################################################################################
## DEPENDENCIAS:
###################################################################################################################################################################################

import db_engine
from models import Base
from sqlalchemy.orm import sessionmaker, scoped_session

###################################################################################################################################################################################
## DECLARACIÓN DE LOS MÉTODOS PARA MANEJAR LA SESIÓN EN LA BASE DE DATOS:
###################################################################################################################################################################################

def startSession(name, password, debug=False, dropAll=False):
	db_engine.startConnection(name, password, debug)
	if dropAll:
		dropAllDataBase()
	Base.metadata.create_all(db_engine.Engine)
	return scoped_session(sessionmaker(bind=db_engine.Engine))

def duplicateSession(autoflush=True):
	if db_engine.Engine is None:
		raise Exception('No se puede Duplicar la session si no ha conexion con Engine')
	return scoped_session(sessionmaker(bind=db_engine.Engine, autoflush=autoflush))

def dropAllDataBase():
	try:
		print("PELIGRO, DROPEANDO TODAS LAS TABLAS")
		Base.metadata.drop_all(db_engine.Engine)
		print("TABLAS DROPEADAS")
	except Exception as e:
		print("No se logro dropear todas las tablas")
		print("Razon:", e)

def resetDataBase():
	dropAllDataBase()
	Base.metadata.create_all(db_engine.Engine)

###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################