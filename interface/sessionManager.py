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
## PATH:
###################################################################################################################################################################################

from sys import path                        # Importación del path del sistema
from os.path import join, split, basename   # Importación de funciones para unir y separar paths con el formato del sistema

# Para cada path en el path del sistema para la aplicación
for current in path:
    if basename(current) == "interface":
        path.append(join(split(current)[0], "modules"))                          # Agregar la carpeta modules al path
        path.append(join(split(current)[0], "models"))                           # Agregar la carpeta models al path
        UIpath = join(join(current, "qt"), "ui")                                 # Declara imagen para la plantilla UI
        stylePath = join(join(join(current, "qt"), "stylesheet"), "LoginWindow") # Declarar path para los qss
        splashPath = join(join(current, "qt"), "images")                         # Declarar path para la imagen splash
        break

###################################################################################################################################################################################
## MODÚLOS:
###################################################################################################################################################################################

from sys import exit

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

# Módulo con las clases para los popUp
from popUps import errorPopUp, successPopUp, authorizationPopUp

###################################################################################################################################################################################
## CONSTANTES:
###################################################################################################################################################################################

# UI
MainUI = "login.ui"
splashName = "splash.png"

# Interfaz .ui creada con qt designer
loginWindow = loadUiType(join(UIpath, MainUI))[0]

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

        self.splash_img = QPixmap(join(splashPath, splashName))
        self.splash = QSplashScreen(self.splash_img, Qt.WindowStaysOnTopHint)

        self.sessionOn = False
        self.db = dbManager("sistema_ventas", "hola", parent=self)
        self.mail = emailManager()
        self.trayIcon = trayIcon(QIcon("interface/qt/images/logo.png"), self)
        self.trayIcon.show()

        self.userDef = False
        self.passDef = False
        self.guiExist = False

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
                if not self.guiExist:
                    self.mainWindow = adminGUI(user, self.db, self)
                    self.guiExist = True
                else: self.mainWindow.changeUser(user)
                self.back = self.mainWindow.userBn0
                self.back.clicked.connect(self.back_pressed)
                self.mainWindow.closed.connect(self.show)
                self.mainWindow.show()
                self.hide()

            else: errorPopUp("Datos incorrectos", self).exec_()

    def sendMail(self):
        if self.lineEd8.text() != "":
            email = self.lineEd8.text()
            if self.db.existUserEmail(email):
                user = self.db.getUsers(email=email)[0]
                newPass = self.db.resetPassword(user.username)
                self.mail.sendPRM(email, newPass)
                self.lineEd8.setText("")

                successPopUp("Correo de recuperación enviado", self).exec_()

                self.MainStacked.setCurrentIndex(0)

            else:
                errorPopUp("El correo no está registrado", self).exec_()

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
            flag = False
            if (self.lineEd2.text() and self.lineEd3.text() and self.lineEd4.text() and self.lineEd5.text() and self.lineEd6.text()) != "":
                if self.lineEd7.text() == self.lineEd6.text():
                    username = self.lineEd2.text()
                    if not self.db.existUser(username):

                        kwargs = {
                            "username"        : username,
                            "firstname"       : self.lineEd3.text(),
                            "lastname"        : self.lineEd4.text(),
                            "email"           : self.lineEd5.text(),
                            "password"        : self.lineEd6.text(),
                            "permission_mask" : self.db.getPermissionMask(self.cobox0.currentText())
                        }
                        flag = True

                    else:
                        errorPopUp("El usuario "+username+" ya existe",self).exec_()
                else:
                    errorPopUp("Las contraseñas no coinciden",self).exec_()
            else:
                errorPopUp("Faltan datos",self).exec_()
            if flag:
                popUp = authorizationPopUp(parent=self)
                if popUp.exec_():
                    adminUsername, adminPassword = popUp.getValues()
                    if self.db.checkPassword(adminUsername, adminPassword):
                        userRange = self.db.getUserRange(adminUsername)
                        if userRange == "Administrador" or userRange == "Dios":
                            self.db.createUser(**kwargs) # Crear usuario
                            successPopUp("Se ha creado el usuario "+username+" exitosamente",self).exec_()
                            self.MainStacked.setCurrentIndex(0)
                        else:
                            errorPopUp("El usuario "+ adminUsername +" no es administrador", self).exec_()
                    else:
                        errorPopUp("Datos incorrectos", self).exec_()

    def on_button7_pressed(self):
        if self.click():
            self.MainStacked.setCurrentIndex(0)

    def on_button8_pressed(self):
        if self.click():
            self.sendMail()

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
            if self.MainStacked.currentIndex() == 0:
                self.startSession(self.lineEd0.text(), self.lineEd1.text())
            elif self.MainStacked.currentIndex() == 1:
                print("xD")
            else:
                self.sendMail()


    def on_mainWindow_closed(self):
        self.show()

    def closeEvent(self, event):
        #event.ignore()
        #self.hide()
        event.accept()

###################################################################################################################################################################################
## MANEJADOR DEL ICONO PARA LA BARRA DE NOTIFICACIONES:
###################################################################################################################################################################################

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
