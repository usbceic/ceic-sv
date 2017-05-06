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

currentPath = getcwd()
palettePath = join(currentPath, "palettes")
foldersName = ["MainWindow", "LoginWindow", "errorPopUp", "warningPopUp", "successPopUp", "confirmationPopUp", "authorizationPopUp"]
regexColor  = '#[0-9A-F]{6}'

###################################################################################################################################################################################
## SCRIPT:
###################################################################################################################################################################################

if __name__ == '__main__':

    # Instrucciones
    print("\nPara generar un stylesheet para MainWindow ingrese 0")
    print("Para generar un stylesheet para LoginWindow ingrese 1")
    print("Para generar un stylesheet para errorPopUp ingrese 2")
    print("Para generar un stylesheet para warningPopUp ingrese 3")
    print("Para generar un stylesheet para successPopUp ingrese 4")
    print("Para generar un stylesheet para confirmationPopUp ingrese 5")
    print("Para generar un stylesheet para authorizationPopUp ingrese 6\n")

    # Bucle par que el usuario marque una opcion válida
    while True:
        op = int(input("Selección: "))

        # Si escogió MainWindow
        if op == 0:
            template = "main-gen.qss"
            savePath = join(currentPath, foldersName[0])

        # Si escogió LoginWindow
        elif op == 1:
            template = "login-gen.qss"
            savePath = join(currentPath, foldersName[1])

        # Si escogió errorPopUp
        elif op == 2:
            template = "error-popup-gen.qss"
            savePath = join(currentPath, foldersName[2])

        # Si escogió warningPopUp
        elif op == 3:
            template = "warning-popup-gen.qss"
            savePath = join(currentPath, foldersName[3])

        # Si escogió successPopUp
        elif op == 4:
            template = "success-popup-gen.qss"
            savePath = join(currentPath, foldersName[4])

        # Si escogió confirmationPopUp
        elif op == 5:
            template = "confirmation-popup-gen.qss"
            savePath = join(currentPath, foldersName[5])

        # Si escogió authorizationPopUp
        elif op == 6:
            template = "authorization-popup-gen.qss"
            savePath = join(currentPath, foldersName[6])

        # Si escogió una opción inválida
        else: continue

        # Si no exite la carpeta de salida, se crea
        if not isdir(savePath): mkdir(savePath)

        # Romper bucle
        break

    try:
        # Leer archivo generador
        file = open(join(currentPath, template), 'r')
        stylesheet = file.read()
        file.close()

        # Leer paletas de colores
        palettes = [palette for palette in listdir(palettePath) if isfile(join(palettePath, palette))]

        print("")
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
## FIN :)
###################################################################################################################################################################################