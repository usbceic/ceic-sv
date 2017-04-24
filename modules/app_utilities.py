# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación de una funciones de utilidad variable

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Christian Oliveros, 01christianol01@gmail.com

###################################################################################################################################################################################
## FUNCIONES:
###################################################################################################################################################################################

# Devuelve un string con el stylesheet especificado por el parametro name
def getStyle(path):
    file = open(path, "r")
    style = file.read()
    file.close()
    return style

# Función para dar formato natural a una cantidad
def naturalFormat(amount, extension = None):
    if (isinstance(amount, str) and amount == ""): return "0"

    tmp = str(amount).split(".")
    integer = tmp[0]
    if len(tmp) < 2: decimal = ""
    else: decimal = tmp[1]

    for i in range(len(integer)-3, 0, -3):
        integer = integer[:i] + "." + integer[i:]

    legalTender = integer
    if decimal != "0": legalTender += ("," + decimal)
    if extension != None: legalTender += extension

    return legalTender

"""
Método que devuelve 0 si el objeto pasado es none, caso contrario devuelve el objeto
"""
def noneToZero(thing):
    if thing is None:
        return 0
    else:
        return thing

###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################
