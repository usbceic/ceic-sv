#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#####################################################################################
## DESCRIPCIÓN:
#####################################################################################

# Sistema de Ventas CEICSV

#####################################################################################
## AUTORES:
#####################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Christian Oliveros, 01christianol01@gmail.com
# José Acevedo, joseluisacevedo1995@gmail.com
# David Cabeza, cabezadavide@gmail.com

#####################################################################################
## MODÚLOS:
#####################################################################################

import sys
from admin_gui import *

#####################################################################################
## PROGRAMA PRINCIPAL:
#####################################################################################

if __name__ == '__main__':
    # Inicializar interfaz:
    app = QApplication(sys.argv)

    # Se añaden las fuentes tipográficas necesarias:
    QFontDatabase.addApplicationFont('qt/fonts/OpenSans-Bold.ttf')

    # Se crea la ventana y se muestra hasta que el usuario la cierre
    window = sistema_window()
    window.show()
    sys.exit(app.exec_())

#####################################################################################
## FIN :)
#####################################################################################
