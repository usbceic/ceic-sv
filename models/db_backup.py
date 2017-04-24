# -*- encoding: utf-8 -*-

###################################################################################################################################################################################
## DESCRIPCIÓN:
###################################################################################################################################################################################

# Modúlo con la implementación del backup de la base de datos de CEIC Suite
# Basado en https://gist.github.com/cuducos/5b3d98655c046099652cbaff23893844

###################################################################################################################################################################################
## AUTORES:
###################################################################################################################################################################################

# Carlos Serrada, cserradag96@gmail.com
# Christian Oliveros, 01christianol01@gmail.com
# Pablo Betancourt, pablodbc30@gmail.com

###################################################################################################################################################################################
## DEPENDENCIAS:
###################################################################################################################################################################################

from session import duplicateSession
import models

from sqlalchemy.ext.serializer import loads, dumps
from sqlalchemy.util import KeyedTuple

from queue import PriorityQueue
import re
import os
import shutil
import inspect
import datetime


def isModelClass(thing):
    if not inspect.isclass(thing):
        return False

    return thing.__module__ == "models"

def searchClass(classes, tablename):
    for class_ in classes:
        if class_[1].__tablename__ == tablename:
            return class_
    return None

class DBBackup(object):

    _bacbkup_folder_name_ = "Backup"
    _bacbkup_old_folder_name_ = _bacbkup_folder_name_ + "_Old"
    _get_dir_function = os.getcwd

    """docstring for DBBackup"""
    def __init__(self):
        super(DBBackup, self).__init__()
        self.session = duplicateSession()
        classes = inspect.getmembers(models, isModelClass)
        self.models_classes = {}
        count = 0
        for table in models.Base.metadata.sorted_tables:
            assoc_class = searchClass(classes, table.name)
            self.models_classes[assoc_class[0]] = (count, assoc_class[1])
            count += 1

    """
    Método de destrucción de la clase
     - Cierra la sesión con la base de datos
    """
    def __del__(self):
        try:
            self.session.close()
            print("Se ha cerrado correctamente la sesion de backup de base de datos")
        except:
            print("La sesion de backup de base de datos ya está cerrada")

    """
    Dumps the data from any given table using protocol 2 (for Python 2.7
    compatibility), as described in
    https://docs.python.org/3/library/pickle.html#pickle-protocols
    :param table_or_mapped_class: SQLAlchemy Table object or mapped class
    """
    def dump(self, table_or_mapped_class):
        query = self.session.query(table_or_mapped_class).all()
        return dumps(query, protocol=2)

    """
    Loads the contents into a given table (should be opened with `rb`)
    Does Not Commit Them!
    :param file_handler: file resulted from a dumps
    """
    def load(self, file_handler):
        MappedClass = self.get_mapped_class(file_handler.name)
        rows = loads(file_handler.read(), models.Base.metadata, self.session)
        for row in rows:
            if isinstance(row, KeyedTuple):
                row = MappedClass(**row._asdict())
            self.session.merge(row)

    """
    Given a dump file name, it returns the mapped class that originated it.
    :param file_path: path for a file resulted from a dumps
    :return: SQLAlchemy mapped class
    """
    def get_mapped_class(self, file_path):
        file_name = os.path.basename(file_path)
        pattern = r'^.*#.*#(?P<mapped_class_name>.*)(\.sql)$'
        match = re.search(pattern, file_name)

        if not match:
            return None

        mapped_class_name = match.group('mapped_class_name')
        return self.models_classes[mapped_class_name][1]

    """
    Método para hacer backup a toda la base de datos
    Devuelve True si logro hacer backup. 
    En caso de encontrar que el ultimo backup esta corrupto, devuelve False
    """
    def backup(self):
        print("Iniciando Backup")
        cur_dir = DBBackup._get_dir_function()
        backup_dir = os.path.join(cur_dir, DBBackup._bacbkup_folder_name_)
        backup_old_dir = os.path.join(cur_dir, DBBackup._bacbkup_old_folder_name_)

        if not os.path.exists(backup_old_dir):
            print("Carpeta de Backups Antiguo no encontrada")
            print("Creando Carpeta de Backups Antiguos")
            os.makedirs(backup_old_dir)

        # Move Old Backup
        if os.path.exists(backup_dir):
            print("Backup Antiguo Encontrado")
            file_names = os.listdir(backup_dir)
            found = False
            backup_date = ""
            for file_name in file_names:
                pattern = r'^.*#(?P<datetime>.*)#.*(\.sql)$'
                match = re.search(pattern, file_name)

                if not match:
                    continue
                else:
                    found = True
                    backup_date = match.group('datetime')
                    break

            if not found:
                print('Error de Formato con los Archivos de Backup Viejo')
                return False 
            print("Hora del Backup Antiguo:", backup_date)
            os.rename(backup_dir, os.path.join(backup_old_dir, backup_date))
            print("Backup Antiguo Movido a Carpeta de Backups Antiguos")

        os.makedirs(backup_dir)

        cur_time = str(datetime.datetime.now()).replace(':','-')
        print("Hora Actual:", cur_time)
        print("Guardando Tablas:")
        for table_name, table in self.models_classes.items():
            print("\tGuardando Tabla:", table_name)
            dump_str = self.dump(table[1])
            new_file_name = str(table[0]) + "#" + cur_time + "#" + table_name + ".sql"
            with open(os.path.join(backup_dir, new_file_name), 'wb') as f:
                f.write(dump_str)
            print("\tGuardada  Tabla:", table_name)
        print("Fin de Guardando Tablas")
        print("Backup Completado")
        return True 

    """
    Método para hacer restore a toda la db.
    Los archivos a ser cargados debieron ser creados por metodo backup
    Retorna True si logro hacer restore, False en caso contrario
    """
    def restore(self):
        print("Iniciando Restore:")
        cur_dir = DBBackup._get_dir_function()
        backup_dir = os.path.join(cur_dir, DBBackup._bacbkup_folder_name_)


        if not os.path.exists(backup_dir):
            print("\tCarpeta de Backup no encontrada, Backup Cancelado")
            return False

        file_names = os.listdir(backup_dir)
        organized_files = PriorityQueue()
        restore_date = None

        for file in file_names:

            file_path = os.path.join(backup_dir, file)

            if not os.path.isfile(file_path):
                # Skip Non Files
                continue

            pattern = r'^(?P<position>.*)#.*#.*(\.sql)$'
            match = re.search(pattern, file)

            if not match:
                continue

            if restore_date is None:
                pattern_date = r'^.*#(?P<datetime>.*)#.*(\.sql)$'
                match_date = re.search(pattern_date, file)
                restore_date = match_date.group('datetime')

            pos = match.group('position')
            organized_files.put((int(pos), file, file_path))



        print("Fecha del Backup a ser Cargado:", restore_date)
        while not organized_files.empty():
            pos, file, file_path = organized_files.get()

            try:
                print("\tCargando Archivo:", file)
                with open(file_path, 'rb') as f:
                    self.load(f)
            except Exception as e:
                print("\tError Cargando Archivo:", file)
                print("\tRazon:", e)
                print("\tHaciendo RollBack")
                self.session.rollback()
                return False

        self.session.commit()
        print("Restore Completado")
        return True

    """
    Método para borrar el último backup
    Retorna True si la carpeta no existe o  si fue borrada con éxito.
    False en caso contrario.
    """
    def deleteLastBackup(self):
        print("Borrando Carpeta de Ultimo Backup")
        cur_dir = DBBackup._get_dir_function()
        backup_dir = os.path.join(cur_dir, DBBackup._bacbkup_folder_name_)

        if not os.path.exists(backup_dir):
            print("\tCarpeta de Backup no encontrada")
            return True

        try:
            shutil.rmtree(backup_dir)
            print("Borrado Completado")
            return True
        except Exception as e:
            print("\tError borrando backup")
            print("\tRazon:", e)
            return False
        


