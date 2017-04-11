# DB Session

from sqlalchemy.orm import sessionmaker, scoped_session
import db_engine
import models

def startSession(name, password, debug=False, dropAll=False):
	db_engine.startConnection(name, password, debug)
	if dropAll:
		dropAllDataBase()
	models.Base.metadata.create_all(db_engine.Engine)
	return scoped_session(sessionmaker(bind=db_engine.Engine))

def duplicateSession(autoflush=True):
	if db_engine.Engine is None:
		raise Exception('No se puede Duplicar la session si no ha conexion con Engine')
	return scoped_session(sessionmaker(bind=db_engine.Engine, autoflush=autoflush))

def dropAllDataBase():
	try:
		print("PELIGRO, DROPEANDO TODAS LAS TABLAS")
		models.Base.metadata.drop_all(db_engine.Engine)
		print("TABLAS DROPEADAS")
	except Exception as e:
		print("No se logro dropear todas las tablas")
		print("Razon:", e)

		