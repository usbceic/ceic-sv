# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación del manejador de inicio de sesión.

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Pablo Betancourt, pablodbc30@gmail.com

###################################################################################################################################################################################
## PATH:
###################################################################################################################################################################################

from sys import path                            # Importación del path del sistema
from os.path import join, dirname, basename     # Importación de funciones para manipular paths con el formato del sistema

# Para cada path en el path del sistema para la aplicación
for current in path:
    if basename(current) == "interface":
        path.append(join(dirname(current), "modules"))                           # Agregar la carpeta modules al path
        path.append(join(dirname(current), "models"))                            # Agregar la carpeta models al path
        UIpath = join(join(current, "qt"), "ui")                                 # Declara imagen para la plantilla UI
        stylePath = join(join(join(current, "qt"), "stylesheet"), "LoginWindow") # Declarar path para los qss
        splashPath = join(join(current, "qt"), "images")                         # Declarar path para la imagen splash
        break

###################################################################################################################################################################################
## MODÚLOS:
###################################################################################################################################################################################

# Módulo que contiene los recursos de la interfaz
import gui_rc

# Módulo con las herramientas parar trabajar los archivos .ui
from PyQt4.uic import loadUiType

# Módulo con procedimientos de Qt
from PyQt4.QtGui import QMainWindow, QApplication, QCursor, QSplashScreen, QPixmap, QIcon

# Módulo con estructuras de Qt
from PyQt4.QtCore import Qt, QMetaObject, pyqtSignal

# Manejador de la base de datos
from db_manager import dbManager

# Manejador de la ventana principal del programa
from guiManager import guiManager

# Manejador de correo electrónico
from emailManager import emailManager

# Manejador del icono de la barra de notificaciones
from trayIcon import trayIcon

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
## MANEJADOR DE LA INTERFAZ GRÁFICA DE LA VENTANA INICIAL:
###################################################################################################################################################################################

class sessionManager(QMainWindow, loginWindow):
    sessionClosed = pyqtSignal() # Señal para saber si se cerró la ventana
    sessionAlive  = pyqtSignal() # Señal para saber si se cerró la ventana

    #==============================================================================================================================================================================
    # CONSTRUCTOR DE LA CLASE
    #==============================================================================================================================================================================

    def __init__(self, parent=None):
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # INICIAR Y CONFIGURAR LA INSTANCIA
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        super(sessionManager, self).__init__(parent)  # Construcción de la instancia
        self.setupUi(self)                            # Configuración de la plantilla

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # INICIAR LOS MANEJADORES PARA LA BASE DE DATOS Y EL CORREO ELECTRÓNICO
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        self.db = dbManager("sistema_ventas", "hola", parent=self)  # Iniciar el manejador de la base de datos
        self.mail = emailManager()                                  # Iniciar el manejador del correo electrónico

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # CREAR Y DESPLEGAR LA IMAGEN SPLASH
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        self.splash_img = QPixmap(join(splashPath, splashName))               # Cargar imagen para la pantalla Splash
        self.splash = QSplashScreen(self.splash_img, Qt.WindowStaysOnTopHint) # Crear la pantalla Splash

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # CONECTAR E INICIAR EL ICONO DE LA BARRA DE NOTIFICACIONES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        self.trayIcon = trayIcon(QIcon("interface/qt/images/logo.png"), self)   # Crear el icono de la barra de notificaciones
        self.trayIcon.show()                                                    # Mostrar el icono de la barra de notificaciones

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # VARIABLES PARA FACILITAR EL USO DE VARIOS MÉTODOS DE LA CLASE
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        self.clicked = False       # Variable de control para los QPushButton
        self.userDef = False       # Variable para saber si ya se definio un usuario para iniciar sesión
        self.passDef = False       # Variable para saber si ya se definio una contraseña para iniciar sesión
        self.guiExist = False      # Variable para saber si ya se creó la ventana principal previamente
        self.isOpenSession = False #

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # CARGAR CONFIGURACIONES INICIALES
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        QMetaObject.connectSlotsByName(self)  # Se conectan los botones entre otras cosas con algunos de los métodos definidos a continuación
        self.generalSetup()                   # Aplicar configuraciones generales de la interfaz

    #==============================================================================================================================================================================
    # CONFIGURACIONES DE LA VENTANA
    #==============================================================================================================================================================================

    # Método para centrar la ventana
    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    # Configuración inicial para la vista de inicio de sesión
    def setupPage0(self):
        self.lineEd0.setPlaceholderText("Usuario")
        self.lineEd1.setPlaceholderText("Contraseña")
        self.footer.setFocus()

    # Configuración inicial para la vista de registro de usuario
    def setupPage1(self):
        self.lineEd2.setPlaceholderText("Usuario")
        self.lineEd3.setPlaceholderText("Nombre")
        self.lineEd4.setPlaceholderText("Apellido")
        self.lineEd5.setPlaceholderText("Correo electrónico")
        self.lineEd6.setPlaceholderText("Contraseña")
        self.lineEd7.setPlaceholderText("Confirmar contraseña")

    # Configuración inicial para la vista de recuperación de contraseña
    def setupPage2(self):
        self.lineEd8.setPlaceholderText("Correo asociado a su cuenta")

    # Método para aplicar la configuración inicial a toda la ventana
    def generalSetup(self):
        self.setMinimumSize(self.sizeHint()) # Configurar tamaño de la ventana
        self.center()                        # Centrar ventana
        self.setupPage0()                    # Configurar vista de inicio de sesión
        self.setupPage1()                    # Configurar vista de registro de usuario
        self.setupPage2()                    # Configurar vista de recuperación de contraseña
        self.MainStacked.setCurrentIndex(0)  # Se establece la pagina de inicio de sesión por defecto

    #==============================================================================================================================================================================
    # MÉTODOS GENERALES MULTIPROPÓSITOS
    #==============================================================================================================================================================================

    # Definición de click sobre un QPushButton
    def click(self):
        if self.clicked:
            self.clicked = False
            return True
        else:
            self.clicked = True
            return False

    #==============================================================================================================================================================================
    # VISTA DE INICIO DE SESIÓN
    #==============================================================================================================================================================================

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para iniciar sesión
    def startSession(self, user, password):
        if self.userDef and self.passDef:
            if self.db.checkPassword(user, password):
                self.lineEd0.setText("")
                self.lineEd1.setText("")
                self.footer.setFocus()
                if not self.guiExist:
                    self.mainWindow = guiManager(user, self.db, self)
                    self.closeSession = self.mainWindow.userBn0
                    self.closeSession.clicked.connect(self.closeSession_pressed)
                    self.mainWindow.closed.connect(self.on_mainWindow_closed)
                    self.guiExist = True
                else: self.mainWindow.changeUser(user)
                self.isOpenSession = True
                self.mainWindow.show()
                self.hide()

            else: errorPopUp("Datos incorrectos", self).exec_()

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Boton para ir a la vista de olvide mi contraseña
    def on_button3_pressed(self):
        if self.click():
            self.MainStacked.setCurrentIndex(2)
            self.header.setIcon(QIcon(':/login/conf'))

    # Boton para iniciar sesión
    def on_button4_pressed(self):
        if self.click():
            self.startSession(self.lineEd0.text(), self.lineEd1.text())

    # Boton para ir a la vista de registro
    def on_button5_pressed(self):
        if self.click():
            self.MainStacked.setCurrentIndex(1)
            self.header.setIcon(QIcon(':/login/camera'))

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CAMPOS DE TEXTO
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Cambio de texto en el lineEdit para el nombre de usuario
    def on_lineEd0_textChanged(self):
        if self.lineEd0.text() == "": self.userDef = False
        else: self.userDef = True

    # Presionar enter estando en el lineEdit para el nombre de usuario
    def on_lineEd0_returnPressed(self):
        self.lineEd1.setFocus()

    # Cambio de texto en el lineEdit para la contraseña
    def on_lineEd1_textChanged(self):
        if self.lineEd1.text() == "": self.passDef = False
        else: self.passDef = True

    #==============================================================================================================================================================================
    # VISTA DE RECUPERACIÓN DE CONTRASEÑA
    #==============================================================================================================================================================================

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MÉTODOS ESPECIALES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Método para enviar un email
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

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Boton para volver a la vista de inicio de sesión
    def on_button7_pressed(self):
        if self.click():
            self.MainStacked.setCurrentIndex(0)
            self.header.setIcon(QIcon(':/login/users'))

    # Botón para enviar el correo de recuperación de contraseña
    def on_button8_pressed(self):
        if self.click():
            self.sendMail()

    #==============================================================================================================================================================================
    # VISTA DE REGISTRO DE USUARIO
    #==============================================================================================================================================================================

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BOTONES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Boton para crear un usuario
    def on_button6_pressed(self):
        if self.click():
            flag = False

            username   = self.lineEd2.text()
            firstname  = self.lineEd3.text()
            lastname   = self.lineEd4.text()
            email      = self.lineEd5.text()
            password   = self.lineEd6.text()
            rePassword = self.lineEd7.text()
            if (username and firstname and lastname and email and password) != "":
                if validateName(firstname):
                    if validateName(lastname):
                        if(validateEmail(email)):
                            if password == rePassword:
                                if not self.db.existUser(username):
                                    kwargs = {
                                        "username"        : username,
                                        "firstname"       : firstname,
                                        "lastname"        : lastname,
                                        "email"           : email,
                                        "password"        : password,
                                        "permission_mask" : self.db.getPermissionMask(self.cobox0.currentText())
                                    }
                                    flag = True

                                else:
                                    errorPopUp("El usuario "+username+" ya existe",self).exec_()
                            else:
                                errorPopUp("Las contraseñas no coinciden",self).exec_()
                        else:
                            errorPopUp("Formato incorrecto de correo",self).exec_()
                    else:
                        errorPopUp("Formato incorrecto para apellido",self).exec_()
                else:
                    errorPopUp("Formato incorrecto para nombre",self).exec_()
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

    # Boton para descartar el registro
    def on_button9_pressed(self):
        if self.click():
            self.MainStacked.setCurrentIndex(0)
            self.header.setIcon(QIcon(':/login/users'))

    #==============================================================================================================================================================================
    # EVENTOS
    #==============================================================================================================================================================================

    # Manejador de eventos al presionar con el mouse
    def mousePressEvent(self, QMouseEvent):
        position = QMouseEvent.pos().y()
        if position >= 425 or position <= 369 or 391 <= position <= 403: self.footer.setFocus()

    # No recuerdo bien que hace, pero es tan importante como el anterior xD
    def mouseReleaseEvent(self, QMouseEvent):
        position = QCursor().pos().y()
        if position >= 425 or position <= 369 or 391 <= position <= 403: self.footer.setFocus()

    # Manejador de eventos por teclado
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            if self.MainStacked.currentIndex() == 0:
                self.startSession(self.lineEd0.text(), self.lineEd1.text())
            elif self.MainStacked.currentIndex() == 1:
                print("xD")
            else:
                self.sendMail()

    # Acciones a tomar cuando el usuario cierra la sesión
    def closeSession_pressed(self):
        self.isOpenSession = False
        self.mainWindow.close()
        self.show()

    # Acciones a tomar cuando se cierra la ventana principal
    def on_mainWindow_closed(self):
        if self.isOpenSession: self.sessionAlive.emit()
        else: self.sessionClosed.emit()

    # Acciones que tomar al intentar cerra la ventana de inicio
    def closeEvent(self, event):
        event.accept()
###################################################################################################################################################################################
## FIN :)
###################################################################################################################################################################################