#Querys goes here
from session import startSession

class DBManager(object):
	"""docstring for DBManager"""
	def __init__(self, name, password, debug=False):
		super(DBManager, self).__init__()
		self.session = startSession(name, password, debug)
		





# Prueba
if __name__ == '__main__':
	DBManager("sistema_ventas", "hola", True)