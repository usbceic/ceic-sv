# -*- encoding: utf-8 -*-

#######################################################################################################################
## DESCRIPCIÓN:
#######################################################################################################################

# Modúlo con la implementación de una función para generar strings psudo-aleatorios

#######################################################################################################################
## AUTORES:
#######################################################################################################################

# Carlos Serrada, cserradag96@gmail.com

#######################################################################################################################
## DEPENDENCIAS:
#######################################################################################################################

from string import ascii_uppercase, ascii_lowercase, digits
from random import choice, sample
from passlib.hash import bcrypt
from time import time

#######################################################################################################################
## DECLARACIÓN DE LA FUNCIÓN PARA GENERAR LOS STRINGS:
#######################################################################################################################

def str_random(length=8):
    alphabet = ascii_uppercase + ascii_lowercase + digits + str(int(round(time() * 1000))) # Crear alphabeto
    alphabet = sample(alphabet, len(alphabet))                                             # Reordenar alphabeto
    alphabet = "".join([choice(alphabet) for i in range(length)])                          # Seleccionar caracteres pseudo-aleatoreamente
    alphabet = bcrypt.hash(alphabet)                                                       # Hashear con bcrypt
    return "".join([choice(alphabet) for i in range(length)])                              # Seleccionar caracteres pseudo-aleatoreamente

#######################################################################################################################
## FIN :)
#######################################################################################################################
