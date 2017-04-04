# Tablas de Db
import sys
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

this = sys.modules[__name__]
this.Base = declarative_base()


class User(this.Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)

    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)

    email = Column(String, nullable=False)

    permission_mask = Column(Integer, nullable=False)

    profile = Column(String, default="")
    description = Column(String, default="")

    creation_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    last_login = Column(DateTime, nullable=False, default=datetime.datetime.now())



    def __repr__(self):
       return "<User(username='%s', password='%s',  firstname='%s', lastname='%s', email=='%s', creation_date=='%s', last_login=='%s')>" % (
                            self.username,
                            self.password,
                            self.firstname,
                            self.lastname,
                            self.email,
                            str(self.creation_date),
                            str(self.last_login)
                            )
