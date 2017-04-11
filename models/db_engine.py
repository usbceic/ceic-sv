# Configuracion del Motor de DB
import sys
from sqlalchemy import create_engine

this = sys.modules[__name__]

this.Engine = None

def startConnection(name, password, debug=False):
	if this.Engine is None:
		print("Iniciando Engine")
		name = str(name)
		password = str(password)
		conn_string = 'postgresql://'+ name + ':' + password + '@localhost/ceicsv'
		this.Engine = create_engine(conn_string, echo=debug)
		this.Engine.connect()
	else:
		print("Engine Ya Iniciado")
