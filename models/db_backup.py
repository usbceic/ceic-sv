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

import models

from sqlalchemy.ext.serializer import loads, dumps
from sqlalchemy.util import KeyedTuple

import re
import os
import inspect
import datetime


def isModelClass(thing):
    if not inspect.isclass(thing):
        return False

    return thing.__module__ == "models"



class DBBackup(object):
    """docstring for DBBackup"""
    def __init__(self, session):
        super(DBBackup, self).__init__()
        self.session = session
        self.models_classes = dict(inspect.getmembers(models, isModelClass))

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
    :param file_handler: file resulted from a dumps
    """
    def load(self, file_handler):
        MappedClass = self.get_mapped_class(file_handler.name)
        rows = loads(file_handler.read(), models.Base.metadata, self.session)
        for row in rows:
            if isinstance(row, KeyedTuple):
                row = MappedClass(**row._asdict())
            self.session.merge(row)
            self.session.commit()

    """
    Given a dump file name, it returns the mapped class that originated it.
    :param file_path: path for a file resulted from a dumps
    :return: SQLAlchemy mapped class
    """
    def get_mapped_class(self, file_path):
        file_name = os.path.basename(file_path)
        pattern = r'^.*-(?P<mapped_class_name>.*)(\.sql)$'
        match = re.search(pattern, file_name)

        if not match:
            return None

        mapped_class_name = match.group('mapped_class_name')
        return self.models_classes[mapped_class_name]


    def backup(self):
        cur_dir = os.getcwd()
        backup_dir = os.path.join(cur_dir, "Backup")
        backup_old_dir = os.path.join(cur_dir, "Backup_Old")

        if not os.path.exists(backup_old_dir):
            os.makedirs(backup_old_dir)

        # Move Old Backup
        if os.path.exists(backup_dir):
            file_names = os.listdir(backup_dir)
            found = False
            backup_date = ""
            for file_name in file_names:
                pattern = r'^(?P<datetime>.*)-.*(\.sql)$'
                match = re.search(pattern, file_name)

                if not match:
                    continue

                found = True
                backup_date = match.group('datetime')

            if not found:
                raise Exception('Error de Formato con los Archivos de Backup') 

            os.rename(backup_dir, os.path.join(backup_old_dir, backup_date))

        os.makedirs(backup_dir)

        cur_time = str(datetime.datetime.now())

        for table_name, table in self.models_classes.items():
            dump_str = self.dump(table)
            new_file_name = cur_time + "-" + table_name + ".sql"
            with open(os.path.join(backup_dir, new_file_name), 'wb') as f:
                f.write(dump_str)




