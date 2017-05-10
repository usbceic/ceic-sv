#!/usr/bin/python3
# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Script para generar hojas de estilo para las ventanas y dialogos de CEIC Suite

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com

###################################################################################################################################################################################
## MODÚLOS:
###################################################################################################################################################################################

from re import findall                      # Función para matchear expresiones regulares
from os import getcwd, listdir, mkdir       # Funciones para el manejo básico de directorios y archivos
from os.path import isfile, isdir, join     # Funciones para manejos de paths y otras cosas útiles xd

###################################################################################################################################################################################
## CONSTANTES:
###################################################################################################################################################################################

currentPath  = getcwd()
palettePath  = join(currentPath, "palettes")
objectNames  = ["MainWindow", "LoginWindow", "errorPopUp", "warningPopUp", "successPopUp", "confirmationPopUp", "authorizationPopUp", "detailsPopUp"]
templatesID  = ["main", "login", "error-popup", "warning-popup", "success-popup", "confirmation-popup", "authorization-popup", "details-popup"]
templatesExt = "-gen.qss"
regexColor   = '#[0-9A-F]{6}'

###################################################################################################################################################################################
## PROCEDIMIENTOS:
###################################################################################################################################################################################

# Procedimiento para generar e imprimir las instrucciones del script
def printInstructions():
    instructions = "\n"
    for i in range(len(objectNames)):
        instructions += "Para generar un stylesheet para " + objectNames[i] + " ingrese " + str(i) + "\n"
    instructions += "Para generar stylesheets para todas las plantillas ingrese " + str(len(objectNames)) + "\n"
    print(instructions)

# Procedimiento para generar stylesheets
def genStyleSheets(num):
    try:
        # Calcular datos
        objectName = objectNames[num]
        template   = templatesID[num]+templatesExt
        savePath   = join(currentPath, objectName)

        # Avisar al usuario que stylesheets se generarán
        print("\nGenerando stylesheets para " + objectName)

        # Crear la carpeta de salida si no existe
        if not isdir(savePath): mkdir(savePath)

        # Leer archivo generador
        file = open(join(currentPath, template), 'r')
        stylesheet = file.read()
        file.close()

        # Leer paletas de colores
        palettes = [palette for palette in listdir(palettePath) if isfile(join(palettePath, palette))]

        for paletteName in palettes:

            # Leer paleta de colores
            file = open(join(palettePath, paletteName), 'r')
            palette = file.read()
            file.close()

            # Buscar colores
            colors = findall(regexColor, palette)

            # Se copia el stylesheet temporalmente
            tmp = stylesheet

            # Reemplazar valores
            tmp = tmp.replace("dark-primary-color", colors[0])
            tmp = tmp.replace("default-primary-color", colors[1])
            tmp = tmp.replace("light-primary-color", colors[2])
            tmp = tmp.replace("text-primary-color", colors[3])
            tmp = tmp.replace("accent-color", colors[4])
            tmp = tmp.replace("primary-text-color", colors[5])
            tmp = tmp.replace("secondary-text-color", colors[6])
            tmp = tmp.replace("divider-color", colors[7])

            # Guardar archivo generado
            aux = paletteName.split("-")
            key = ""
            for i in range(len(aux)//2):
                key += aux[i]
                if i < len(aux)//2-1: key += "-"
            newName = key+".qss"
            new = open(join(savePath, newName), 'w')
            new.write(tmp)
            new.close()
            print("Se ha creado el archivo " + newName + " satisfactoreamente.")
        print("")

    # Capturador de errores por archivos inexistentes
    except FileNotFoundError:
        print("\nERROR: No se pudo encontrar el archivo: '" + join(currentPath, template) + "'.\n")

    # Capturador de errores desconocidos
    except:
        print("\nHa ocurrido un error inesperado.\n")

###################################################################################################################################################################################
## SCRIPT:
###################################################################################################################################################################################

if __name__ == '__main__':

    # Instrucciones
    printInstructions()

    # Bucle par que el usuario marque una opcion válida
    while True:
        option = int(input("Selección: "))

        # Crear stylesheets para un elemento
        if 0 <= option < len(objectNames):
            genStyleSheets(option)

        # Crear stylesheets para todos los elementos
        elif option == len(objectNames):
            for i in range(len(templatesID)): genStyleSheets(i)

        # Volver a preguntar si escogió una opción inválida
        else: continue

        # Finalizar
        break

###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################