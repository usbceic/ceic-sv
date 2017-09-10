# -*- encoding: utf-8 -*-

#######################################################################################################################
## DESCRIPCIÓN:
#######################################################################################################################

# Modúlo con la implementación de los tipos de datos personalizados usados para la base de datos

#######################################################################################################################
## AUTORES:
#######################################################################################################################

# Christian Oliveros, 01christianol01@gmail.com

#######################################################################################################################
## DEPENDENCIAS:
#######################################################################################################################

from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid

#######################################################################################################################
## DECLARACIÓN DE LOS TIPOS DE DATO PERSONALIZADOS
#######################################################################################################################

# http://docs.sqlalchemy.org/en/latest/core/custom_types.html?highlight=guid#backend-agnostic-guid-type
class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

    @staticmethod
    def random_value():
        return uuid.uuid4()

#######################################################################################################################
## FIN :)
#######################################################################################################################
