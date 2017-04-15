#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from re import findall
from os import listdir, mkdir
from os.path import isfile, isdir, join

# Constantes
genPath = ""
palettePath = "palette/"
hexColor = '#[0-9A-F]{6}'
savePath0 = "MainWindow/"
savePath1 = "LoginWindow/"

# Instrucciones
print("\nPara generar un stylesheet para MainWindow ingrese 0")
print("Para generar un stylesheet para LoginWindow ingrese 1\n")

# Bucle par que el usuario marque una opcion válida
while True:
    op = int(input("Selección: "))
    if op == 0:
        genName = "main-gen.qss"
        savePath = savePath0
    elif op == 1:
        genName = "login-gen.qss"
        savePath = savePath1
    else:
        continue

    # Verificar que exista carpeta de salida
    if not isdir(savePath): mkdir(savePath)

    break

try:
    # Leer archivo generador
    file = open(genPath+genName, 'r')
    stylesheet = file.read()
    file.close()

    # Leer paletas de colores
    palettes = [palette for palette in listdir(palettePath) if isfile(join(palettePath, palette))]

    print("")
    for paletteName in palettes:

        # Leer paleta de colores
        file = open(palettePath+paletteName, 'r')
        palette = file.read()
        file.close()

        # Buscar colores
        colors = findall(hexColor, palette)

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
        new = open(savePath+newName, 'w')
        new.write(tmp)
        new.close()
        print("Se ha creado el archivo "+newName+" satisfactoreamente.")
    print("")

except FileNotFoundError:
    print("\nERROR: No se pudo encontrar el archivo: '"+genPath+genName+"'.\n")

except:
    print("\nHa ocurrido un error inesperado.\n")
