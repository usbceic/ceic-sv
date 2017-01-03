# -*- encoding: utf-8 -*-

####################################################################################################################################
## DESCRIPCIÓN:
####################################################################################################################################

# Modúlo con la implementación del manejador de inicio de sesión.

####################################################################################################################################
## AUTORES:
####################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Christian Oliveros, 01christianol01@gmail.com
# José Acevedo, joseluisacevedo1995@gmail.com
# David Cabeza, cabezadavide@gmail.com
# Pablo Betancourt, pablodbc30@gmail.com

####################################################################################################################################
## MODÚLOS:
####################################################################################################################################

# Módulo que contiene los recursos de la interfaz
import gui_rc

# Módulo con las herramientas parar trabajar los archivos .ui
from PyQt4.uic import loadUiType

# Módulo con procedimientos de Qt
from PyQt4.QtGui import QMainWindow, QDialog, QApplication, QLineEdit, QCursor, QSplashScreen, QPixmap

# Módulo con estructuras de Qt
from PyQt4.QtCore import Qt, QMetaObject, QEvent, pyqtSignal, QTimer

# Manejador de la base de datos
from DBManager import DBManager

# Manejador de la ventana principal del programa
from guiManager import adminGUI

# Manejador de correo electrónico
from emailManager import emailManager, googleServer

####################################################################################################################################
## CONSTANTES:
####################################################################################################################################

# Paths
UIpath = "qt/ui/"
stylePath = "qt/stylesheet/"

# UI
MainUI = "login.ui"

# Interfaz .ui creada con qt designer
loginWindow = loadUiType(UIpath+MainUI)[0]
dialog0 = loadUiType(UIpath+"dialog0.ui")[0]
dialog1 = loadUiType(UIpath+"dialog1.ui")[0]

####################################################################################################################################
## MANEJADOR DE LA INTERFAZ GRÁFICA:
####################################################################################################################################

class loginGUI(QMainWindow, loginWindow):
    #closed = pyqtSignal()

    #-------------------------------------------------------------------------------------------------------------------------------
    # Constructor de la clase
    #-------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, parent=None):
        #---------------------------------------------------------------------------------------------------------------------------
        # Iniciar y configurar la interfaz y la base de datos
        #---------------------------------------------------------------------------------------------------------------------------

        # Interfaz
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.splash_img = QPixmap("qt/images/splash.png")
        self.splash = QSplashScreen(self.splash_img, Qt.WindowStaysOnTopHint)

        self.sessionOn = False
        self.db = DBManager("carlos", "curtis", True)
        self.mail = emailManager(googleServer, "ceicsvoficial@gmail.com", "pizzabrownie")

        self.userDef = False
        self.passDef = False

        self.center()

        self.setupPage0()
        self.setupPage1()
        self.setupPage2()

        # Se connectan los botones entre otras cosas con algunos de los métodos definidos a continuación
        QMetaObject.connectSlotsByName(self)

        # Variable de control para los QPushButton
        self.clicked = False

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
            if self.db.checkUser(user, password):
                self.lineEd0.setText("")
                self.lineEd1.setText("")
                self.ceicsvlb.setFocus()
                self.mainWindow = adminGUI(self.db, self)
                self.back = self.mainWindow.userBn0
                self.back.clicked.connect(self.back_pressed)
                self.mainWindow.closed.connect(self.show)
                self.mainWindow.show()
                self.hide()

            else: dialog0GUI().exec_()


    def setupPage0(self):
        self.lineEd0.setPlaceholderText("Usuario")
        self.lineEd1.setPlaceholderText("Contraseña")
        self.ceicsvlb.setFocus()

    def setupPage1(self):
        self.lineEd2.setPlaceholderText("Usuario")
        self.lineEd3.setPlaceholderText("Nombre")
        self.lineEd4.setPlaceholderText("Apellido")
        self.lineEd5.setPlaceholderText("Número de teléfono")
        self.lineEd6.setPlaceholderText("Correo electrónico")
        self.lineEd7.setPlaceholderText("Contraseña")
        self.lineEd8.setPlaceholderText("Confirmar contraseña")

    def setupPage2(self):
        self.lineEd9.setPlaceholderText("Correo asociado a su cuenta")
        self.lineEd10.setPlaceholderText("Nombre de usuario")
        self.lineEd11.setPlaceholderText("Nueva contraseña")
        self.lineEd12.setPlaceholderText("Confirmar contraseña")
        self.lineEd13.setPlaceholderText("Administrador o Master")
        self.lineEd14.setPlaceholderText("Contraseña")

    def on_pubutton3_pressed(self):
        if self.click():
            self.MainStacked.setCurrentIndex(2)

    def on_pubutton4_pressed(self):
        if self.click():
            self.startSession(self.lineEd0.text(), self.lineEd1.text())

    def on_pubutton5_pressed(self):
        if self.click():
            self.MainStacked.setCurrentIndex(1)

    def on_pubutton7_pressed(self):
        if self.click():
            dialog1GUI().exec_()

    def on_pubutton8_pressed(self):
        if self.click():
            self.MainStacked.setCurrentIndex(0)

    def on_pubutton9_pressed(self):
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
        if position >= 425 or position <= 369 or 391 <= position <= 403: self.ceicsvlb.setFocus()

    def mouseReleaseEvent(self, QMouseEvent):
        position = QCursor().pos().y()
        if position >= 425 or position <= 369 or 391 <= position <= 403: self.ceicsvlb.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.startSession(self.lineEd0.text(), self.lineEd1.text())
            if self.lineEd9.text() != "":
                self.mail.sendPRM("cserradag96@gmail.com", "El Juego")
                self.lineEd9.setText("")

    def on_mainWindow_closed(self):
        self.show()

class dialog0GUI(QDialog, dialog0):
    #-------------------------------------------------------------------------------------------------------------------------------
    # Constructor de la clase
    #-------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, parent=None):
        #---------------------------------------------------------------------------------------------------------------------------
        # Iniciar y configurar la interfaz y la base de datos
        #---------------------------------------------------------------------------------------------------------------------------

        # Interfaz
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

class dialog1GUI(QDialog, dialog1):
    #-------------------------------------------------------------------------------------------------------------------------------
    # Constructor de la clase
    #-------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, parent=None):
        #---------------------------------------------------------------------------------------------------------------------------
        # Iniciar y configurar la interfaz y la base de datos
        #---------------------------------------------------------------------------------------------------------------------------

        # Interfaz
        QMainWindow.__init__(self, parent)
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

####################################################################################################################################
## FIN :)
####################################################################################################################################
