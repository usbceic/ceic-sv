# -*- encoding: utf-8 -*-

####################################################################################################################################
## DESCRIPCIÓN:
####################################################################################################################################

# Modúlo con la implementación del manejador de correo electrónico.

####################################################################################################################################
## AUTORES:
####################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com

###################################################################################################################################################################################
## PATH:
###################################################################################################################################################################################

from sys import path                        # Importación del path del sistema
from os.path import join, basename          # Importación de funciones para manipular paths con el formato del sistema

# Para cada path en el path del sistema para la aplicación
for current in path:
    if basename(current) == "modules":
        templatesPath = join(current, "templates")  # Declarar path para los templates
        break

####################################################################################################################################
## MODÚLOS:
####################################################################################################################################

# Libreria para facilitar el envio de correos electrónicos
from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError as AuthenticationError

# Libreria para identificar errores con la conexión a internet
from socket import gaierror as NetworkError

####################################################################################################################################
## CONSTANTES:
####################################################################################################################################

# Correo electrónico por defecto
defaultEmail = "ceicsvoficial@gmail.com" # Dirección
defaultPass  = "pizzabrownie"            # Contraseña

# Servidores
googleServer  = "smtp.gmail.com"
yahooServer   = "smtp.mail.yahoo.com"
outlookServer = "smtp.live.com"

# Puerto
tlsPort = "587" # Modo sin encryptación..
sslPort = "465" # Modo con encryptación... Para que la app sea identificada como CEIC Suite hay que comprar el certificado SSL

####################################################################################################################################
## MANEJADOR DE CORREO ELECTRÓNICO:
####################################################################################################################################

class emailManager():
    #==============================================================================================================================================================================
    # CONSTRUCTOR DE LA CLASE
    #==============================================================================================================================================================================

    def __init__(self, server=googleServer, mail=defaultEmail, password=defaultPass):

        #---------------------------------------------------------------------------------------------------------------------------
        # CAMPOS DE CORREO
        #---------------------------------------------------------------------------------------------------------------------------

        self.fromMail = "CEIC Suite <" + mail + ">"
        self.firm = self.getFirm()

        #---------------------------------------------------------------------------------------------------------------------------
        # DATOS DEL REMITENTE
        #---------------------------------------------------------------------------------------------------------------------------

        self.serverDir = server
        self.usermail  = mail
        self.password  = password

    #===============================================================================================================================
    # PROCEDIMIENTOS DE LA CLASE (MÉTODOS)
    #===============================================================================================================================

    # Cargar plantilla para el contenido del correo
    def getTemplate(self, number):
        try:
            file = open(join(templatesPath, "template"+str(number)+".txt"), mode = "r")
            lines, template = file.read(), ""
            for line in lines: template += line.split("\n")[0]
            file.close()
            print("Se ha cargado la plantilla satisfactoriamente")
            return template

        except IOError: print("ERROR: NO se encontró el archivo: template"+ str(number) + ".txt")
        except: print("Ha ocurrido un error desconocido al intentar leer el archivo: template"+ str(number) + ".txt")

    # Cargar firma
    def getFirm(self):
        try:
            file = open(join(templatesPath, "firm.txt"), mode = "r")
            lines, firm = file.read(), ""
            for line in lines: firm += line.split("\n")[0]
            file.close()
            print("Se ha cargado la firma satisfactoriamente")
            return firm

        except IOError: print("ERROR: NO se encontró el archivo: firm.txt")
        except: print("Ha ocurrido un error desconocido al intentar leer el archivo: firm.txt")

    # Métodos para enviar correos
    def sendMail(self, toMail, toSend, sslMode = True):
        try:
            # Conectar con el servidor
            if sslMode: server = SMTP_SSL(self.serverDir + ":" + sslPort)
            else:
                server = SMTP(self.serverDir + ":" + tlsPort)
                server.starttls()

            # Iniciar sesión en el servidor
            server.login(self.usermail, self.password)

            # Mandar el correo
            server.sendmail(self.fromMail, toMail, toSend.encode("utf8"))

            # Salir del servidor
            server.quit()

            # Confirmar que todo salio bien :)
            print("Se ha enviado el correo satisfactoriamente")
            return True

        except AuthenticationError: print("ERROR: No se pudo iniciar sesión en el servidor.")
        except NetworkError: print("ERROR: No se pudo conectar con el servidor.")
        except: print("ERROR: No se pudo enviar el correo.")

        return False

    # Método para enviar correo de recuperación de contraseña o PRM (Password Recovery Mail)
    def sendPRM(self, toMail, password):
        emailForm = "From: %s\nTo: %s\nSubject: %s\n%s\n\nContraseña: %s\n\n%s\n"          # Forma del correo
        subject = "CEIC Suite - Recuperación de contraseña"                                # Asunto
        template = self.getTemplate(0)                                                     # Mensaje
        toSend = emailForm%(self.fromMail, toMail, subject, template, password, self.firm) # Construir correo
        return self.sendMail(toMail, toSend)                                               # Enviar correo

####################################################################################################################################
## FIN :)
####################################################################################################################################