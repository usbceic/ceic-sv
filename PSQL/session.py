# DB Session

from sqlalchemy.orm import sessionmaker, scoped_session
import db_engine
import models

def startSession(name, password, debug=False, dropAll=False):
	db_engine.startConnection(name, password, debug)
	if dropAll:
		print("PELIGRO, DROPEANDO TODAS LAS TABLAS")
		models.Base.metadata.drop_all(db_engine.Engine)
	models.Base.metadata.create_all(db_engine.Engine)
	return scoped_session(sessionmaker(bind=db_engine.Engine))

