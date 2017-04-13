# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación del manejador de inicio de sesión.

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Christian Oliveros, 01christianol01@gmail.com
# Pablo Betancourt, pablodbc30@gmail.com

###################################################################################################################################################################################
## MODÚLOS:
###################################################################################################################################################################################

from sys import exit

# Importación de la función para obtener el path actual
from os import getcwd

# Importación de función para unir paths con el formato del sistema
from os.path import join

# Módulo que contiene los recursos de la interfaz
import gui_rc

# Módulo con las herramientas parar trabajar los archivos .ui
from PyQt4.uic import loadUiType

# Módulo con procedimientos de Qt
from PyQt4.QtGui import QMainWindow, QDialog, QApplication, QLineEdit, QCursor, QSplashScreen, QPixmap, QSystemTrayIcon, QIcon, QMenu, QAction

# Módulo con estructuras de Qt
from PyQt4.QtCore import Qt, QMetaObject, pyqtSignal

# Manejador de la base de datos
from db_manager import dbManager

# Manejador de la ventana principal del programa
from guiManager import adminGUI

# Manejador de correo electrónico
from emailManager import emailManager, googleServer

###################################################################################################################################################################################
## CONSTANTES:
###################################################################################################################################################################################

# Paths
UIpath = join(getcwd(), "interface/qt/ui/")
stylePath = join(getcwd(), "interface/qt/stylesheet/")
splashPath = join(getcwd(), "interface/qt/images/splash.png")

# UI
MainUI = "login.ui"

# Interfaz .ui creada con qt designer
loginWindow = loadUiType(UIpath+MainUI)[0]
dialog0 = loadUiType(UIpath+"dialog0.ui")[0]
dialog1 = loadUiType(UIpath+"dialog1.ui")[0]

###################################################################################################################################################################################
## MANEJADOR DE LA INTERFAZ GRÁFICA:
###################################################################################################################################################################################

class loginGUI(QMainWindow, loginWindow):
    #==============================================================================================================================================================================
    # Constructor de la clase
    #==============================================================================================================================================================================

    def __init__(self, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Iniciar y configurar la interfaz y la base de datos
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Interfaz
        super(loginGUI, self).__init__(parent)
        self.setupUi(self)

        self.splash_img = QPixmap(splashPath)
        self.splash = QSplashScreen(self.splash_img, Qt.WindowStaysOnTopHint)

        self.sessionOn = False
        self.db = dbManager("sistema_ventas", "hola", parent=self)
        self.mail = emailManager(googleServer, "ceicsvoficial@gmail.com", "pizzabrownie")
        self.trayIcon = trayIcon(QIcon("interface/qt/images/logo.png"), self)
        self.trayIcon.show()

        self.userDef = False
        self.passDef = False

        self.center()

        self.setupPage0()
        self.setupPage1()
        self.setupPage2()

        self.setMinimumSize(self.sizeHint())

        # Se conectan los botones entre otras cosas con algunos de los métodos definidos a continuación
        QMetaObject.connectSlotsByName(self)

        # Variable de control para los QPushButton
        self.clicked = False

        # Se establece la pagina de inicio de sesión por defecto
        self.MainStacked.setCurrentIndex(0)

    def click(self):
        if self.clicked:
            self.clicked = False
            return True
        else:
            self.clicked = True
            return False

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def startSession(self, user, password):
        if self.userDef and self.passDef:
            if self.db.checkPassword(user, password):
                self.lineEd0.setText("")
                self.lineEd1.setText("")
                self.footer.setFocus()
                self.mainWindow = adminGUI(user, self.db, self)
                self.back = self.mainWindow.userBn0
                self.back.clicked.connect(self.back_pressed)
                self.mainWindow.closed.connect(self.show)
                self.mainWindow.show()
                self.hide()

            else: dialog0GUI(self).exec_()

    def setupPage0(self):
        self.lineEd0.setPlaceholderText("Usuario")
        self.lineEd1.setPlaceholderText("Contraseña")
        self.footer.setFocus()

    def setupPage1(self):
        self.lineEd2.setPlaceholderText("Usuario")
        self.lineEd3.setPlaceholderText("Nombre")
        self.lineEd4.setPlaceholderText("Apellido")
        self.lineEd5.setPlaceholderText("Correo electrónico")
        self.lineEd6.setPlaceholderText("Contraseña")
        self.lineEd7.setPlaceholderText("Confirmar contraseña")

    def setupPage2(self):
        self.lineEd8.setPlaceholderText("Correo asociado a su cuenta")

    def on_button3_pressed(self):
        if self.click():
            self.MainStacked.setCurrentIndex(2)

    def on_button4_pressed(self):
        if self.click():
            self.startSession(self.lineEd0.text(), self.lineEd1.text())

    def on_button5_pressed(self):
        if self.click():
            self.MainStacked.setCurrentIndex(1)

    def on_button6_pressed(self):
        if self.click():
            dialog1GUI(self).exec_()

    def on_button7_pressed(self):
        if self.click():
            self.MainStacked.setCurrentIndex(0)

    def on_button9_pressed(self):
        if self.click():
            self.MainStacked.setCurrentIndex(0)

    def back_pressed(self):
        self.mainWindow.close()
        self.show()

    def on_lineEd0_textChanged(self):
        if self.lineEd0.text() == "": self.userDef = False
        else: self.userDef = True

    def on_lineEd0_returnPressed(self):
        self.lineEd1.setFocus()

    def on_lineEd1_textChanged(self):
        if self.lineEd1.text() == "": self.passDef = False
        else: self.passDef = True

    def mousePressEvent(self, QMouseEvent):
        position = QMouseEvent.pos().y()
        if position >= 425 or position <= 369 or 391 <= position <= 403: self.footer.setFocus()

    def mouseReleaseEvent(self, QMouseEvent):
        position = QCursor().pos().y()
        if position >= 425 or position <= 369 or 391 <= position <= 403: self.footer.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.startSession(self.lineEd0.text(), self.lineEd1.text())
            if self.lineEd8.text() != "":
                self.mail.sendPRM(self.lineEd8.text(), "El Juego")
                self.lineEd8.setText("")

    def on_mainWindow_closed(self):
        self.show()

    def closeEvent(self, event):
        #event.ignore()
        #self.hide()
        event.accept()

class dialog0GUI(QDialog, dialog0):
    #==============================================================================================================================================================================
    # Constructor de la clase
    #==============================================================================================================================================================================

    def __init__(self, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Iniciar y configurar la interfaz y la base de datos
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Interfaz
        super(dialog0GUI, self).__init__(parent)
        self.setupUi(self)


    def click(self):
        if self.clicked:
            self.clicked = False
            return True
        else:
            self.clicked = True
            return False

    def on_dpbutton0_pressed(self): self.accept()

class dialog1GUI(QDialog, dialog1):
    #==============================================================================================================================================================================
    # Constructor de la clase
    #==============================================================================================================================================================================

    def __init__(self, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Iniciar y configurar la interfaz y la base de datos
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # Interfaz
        super(dialog1GUI, self).__init__(parent)
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint)
        self.clicked = False

        # Definición de click sobre un QPushButton
    def click(self):
        if self.clicked:
            self.clicked = False
            return True
        else:
            self.clicked = True
            return False

    def on_dpbutton2_pressed(self): self.accept()

# Icono en la barra de notificaciones
class trayIcon(QSystemTrayIcon):

    # Constructor
    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.parent = parent
        self.menu = QMenu(self.parent)
        self.setContextMenu(self.menu)

        finish = QAction("Mostrar", self)
        finish.triggered.connect(self.parent.show)
        self.menu.addAction(finish)

        # Opción para terminar el programa
        kill = QAction("Salir", self)
        kill.triggered.connect(self.killApp)
        self.menu.addAction(kill)

    # Función para terminar el programa
    def killApp(self):
        self.parent.hide()
        self.parent.alive = False
        exit(0)

###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################
