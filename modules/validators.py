# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación de los validadores para campos de texto de CEIC Suite

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Pablo Betancourt, pablodbc30@gmail.com

###################################################################################################################################################################################
## DEPENDENCIAS:
###################################################################################################################################################################################

import re

###################################################################################################################################################################################
## DECLARACIÓN DE LOS VALIDADORES:
###################################################################################################################################################################################

"""
Método para validar números telefonicos
	Retorna True:
		* Si el string recibido es un número telefónico válido
	Retorna False:
		* Si el string recibido NO es un número telefónico válido
"""
def validatePhoneNumber(phone):
	start58 = "^(\(\+58\)|\+58)"
	PhoneCode = "((4|2)\d{2})"
	pattern = re.compile("((" + (start58 + PhoneCode) + "|(^(0"+PhoneCode+")|\(0"+PhoneCode+"\))" + ")(\-?\d{3}\-?\d{4})$)")
	if pattern.match(phone):
		return True
	else:
		return False

"""
Método para validar correos electrónicos
	Retorna True:
		* Si el string recibido es un correo electrónico válido
	Retorna False:
		* Si el string recibido NO es un correo electrónico válido
"""
def validateEmail(email):
	pattern = re.compile("^[A-Za-z0-9][A-Za-z0-9\.\-_]*\@[A-Za-z0-9][A-Za-z0-9\.\-_]*\.\w+$")	
	if pattern.match(email):
		return True
	else:
		return False

"""
Método para validar nombres de personas (incluye nombres compuestos)
	Retorna True:
		* Si el string recibido es un nombre de persona válido
	Retorna False:
		* Si el string recibido NO es un nombre de persona válido
"""
def validateName(name):
	pattern = re.compile("^\w+((-|\ )\w+)*$")	
	if pattern.match(name):
		return True
	else:
		return False

###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################
