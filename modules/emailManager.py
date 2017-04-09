# -*- encoding: utf-8 -*-

####################################################################################################################################
## DESCRIPCIÓN:
####################################################################################################################################

# Modúlo con la implementación del manejador de correo electrónico.

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

# Importación de la función para obtener el path actual
from os import getcwd

# Importación de función para unir paths con el formato del sistema
from os.path import join  as join

# Libreria para facilitar el envio de correos electrónicos
from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError as AuthenticationError

# Libreria para identificar errores con la conexión a internet
from socket import gaierror as NetworkError

####################################################################################################################################
## CONSTANTES:
####################################################################################################################################

# Paths
templatesPath = join(getcwd(), "modules/templates")

# Servidores
googleServer = "smtp.gmail.com"
yahooServer = "smtp.mail.yahoo.com"
outlookServer = "smtp.live.com"

# Puerto
tlsPort = "587" # Modo sin encryptación.. se usará por defecto
sslPort = "465" # Para usar el modo de encryptación ssl hay que comprar el certificado ssl,pero hay patria... :(

####################################################################################################################################
## MANEJADOR DE CORREO ELECTRÓNICO:
####################################################################################################################################

class emailManager():
    def __init__(self, server, mail, password):

        #---------------------------------------------------------------------------------------------------------------------------
        # Atributos:
        #---------------------------------------------------------------------------------------------------------------------------

        # Campos del correo
        self.fromMail = "CEICSV <" + mail + ">"
        self.emailForm = "From: %s\nTo: %s\nSubject: %s\n%s\n\nClave temporal: %s\n\n%s\n"
        self.subjectPRM = "Recuperación de contraseña CEICSV"
        self.msgPRM = self.getMsg(0)
        self.firm = self.getFirm()

        # Datos del remitente
        self.serverDir = server
        self.usermail = mail
        self.password = password

    #-------------------------------------------------------------------------------------------------------------------------------
    # Procedimientos de la clase (Métodos)
    #-------------------------------------------------------------------------------------------------------------------------------

    # Leer mensaje
    def getMsg(self, number):
        try:
            file = open(join(templatesPath, "msg"+str(number)+".txt"), encoding = 'utf-8', mode = "r")
            lines, msg = file.read(), ""
            for line in lines: msg += line.split("\n")[0]
            file.close()
            return msg

        except IOError: print("ERROR: NO se encontró el archivo: msg"+ str(number) + ".txt")
        except: print("Ha ocurrido un error desconocido al intentar leer el archivo: msg"+ str(number) + ".txt")

    # Leer firma
    def getFirm(self):
        try:
            file = open(join(templatesPath, "firm.txt"), encoding = 'utf-8', mode = "r")
            lines, firm = file.read(), ""
            for line in lines: firm += line.split("\n")[0]
            file.close()
            return firm

        except IOError: print("ERROR: NO se encontró el archivo: firm.txt")
        except: print("Ha ocurrido un error desconocido al intentar leer el archivo: firm.txt")

    # Enviar correo de recuperación de contraseña o PRM (Password Recovery Mail)
    def sendPRM(self, toMail, code, sslMode = False):
        try:
            # Conectar con el servidor
            if sslMode: server = SMTP_SSL(self.serverDir + ":" + sslPort)
            else:
                server = SMTP(self.serverDir + ":" + tlsPort)
                server.starttls()

            # Iniciar sesión en el servidor
            server.login(self.usermail, self.password)

            # Crear correo
            PRM = self.emailForm%(self.fromMail, toMail, self.subjectPRM, self.msgPRM, code, self.firm)

            # Mandar el correo
            server.sendmail(self.fromMail, toMail, PRM.encode("utf-8"))

            # Salir del servidor
            server.quit()

        except AuthenticationError: print("ERROR: No se pudo iniciar sesión en el servidor.")
        except NetworkError: print("ERROR: No se pudo conectar con el servidor.")
        except: print("ERROR: No se pudo enviar el correo.")

####################################################################################################################################
## FIN :)
####################################################################################################################################