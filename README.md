***
**CEIC Suite**
==============================
***

* Sistema de Ventas del Centro de Estudiantes de Ingeniería de la Computación
* Este sistema mantiene centralizadas todas las operaciones de ventas y servicios que ofrece el centro de estudiantes.


***
Estado actual del proyecto
-------------
***

El proyecto aun está en fase beta.

* A nivel de base de datos:
    - Todo el modelo está comentado y se tiene el esquema de la base digitalizado en extensiones ".svg" y ".png"
    - Todo el archivo de creación del modelo y comunicación entre el ORM (SQLAlchemy) y la base de datos como tal, están listos.
    - Todos los CRUDs para la parte de ventas estan listos.
    - Todos los triggers para la parte de ventas estan listos.
    - Para la parte de prestamos de libros, faltan todos los CRUDs, así como los triggers pertinentes.



* A nivel de interfaz:
    - Todo el código esta comentado
    - Todas las vistas de la ventana de inicio están listas, con sus debidas verificaciones y mensajes de alerta.
    - La vista de caja esta completamente funcional con verfificaciones y mensajes de alerta.
    - La vista de ventas esta completamente funcional con verfificaciones y mensajes de alerta.
    - La vista de inventario esta completamente funcional con verfificaciones y mensajes de alerta.
    - La vista de proveedores esta completamente funcional con verfificaciones y mensajes de alerta.
    - La vista de clientes esta completamente funcional con verfificaciones y mensajes de alerta.
    - La vista de recargas de saldo esta completamente funcional con verfificaciones y mensajes de alerta.
    - La vista de usuarios esta completamente funcional con verfificaciones y mensajes de alerta.
    - La vista de configuraciones esta completamente funcional con verfificaciones y mensajes de alerta.
    - La vista de ayuda esta completamente funcional con verfificaciones y mensajes de alerta.
    - Falta conectar toda la vista para consultar estadísticas (100% seguro que quedará para el futuro).
    - Falta conectar la vista para prestamos de libros.
    - Falta conectar la vista de la biblioteca.
    - Faltan pulir detalles y establecer atajos de teclado.



* General:
    - Aun no se cuenta con un instalador pero se tiene un script para facilitar el proceso de instalación de las dependencias (solo para distribuciones basadas en Debian).
    - Aun no se tiene el sistema de licencias para poder comercializar el producto.
    - Falta definir la liscencia y otros aspectos legales.
    - Falta el manual de usuario.


***
Requisitos
-------------
***

* Sistemas operativos soportados:
    - Ubuntu 13.04 o superior
    - Windows XP o superior
* Sistema operativo recomendado: Ubuntu 16.04
* Escala de pantalla optima: 0.875
* Resolución de pantalla mínima: 860x710
* Resolución de pantalla recomendada: 1440x900
* Instalar Python 3.4.x con las siguientes librerias:
    - PyQt4
    - SQLAlchemy
    - psycopg2
    - passlib
    - bcrypt
* Instalar PostgreSQL 9.4.x o superior
* Instalar las fuentes tipográficas incluidas en este software


***
Como configurar y correr la aplicación
-------------
***

* Esta aplicación trabaja con Python, Qt y PostgreSQL
* Vaya a la carpeta 'doc' y ejecute el script de instalación de dependencias:

```
#!shell
cd doc
chmod +x installScript.sh
sudo ./installScript.sh
```

* Para correr la aplicación mediante la consola utilizar el comando:

```
#!shell
python3 ceic_suite.py
```

***
Información de contacto
-------------
***

* Coordinación de Tecnología y colaboradores del Centro de Estudiantes de Ing. Computación

* Carlos Serrada, cserradag96@gmail.com
* Christian Oliveros, 01christianol01@gmail.com
* Pablo Betancourt, pablodbc30@gmail.com