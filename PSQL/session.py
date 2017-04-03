# DB Session

from sqlalchemy.orm import sessionmaker

import db_engine 
import models

def startSession(name, password, debug=False):
	db_engine.startConnection(name, password, debug)
	models.Base.metadata.create_all(db_engine.Engine)
	return sessionmaker(bind=db_engine.Engine)

	