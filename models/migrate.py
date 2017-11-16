from db_manager import dbManager
from models import *
from sqlalchemy import func

DBM = dbManager()
"""for ci in DBM.getClientsCI():
    query = DBM.existAutoIncrease(ci, 'Lipton')
    if query is not None:
        for increase in query:
            if increase.pay_date == None:
                print(increase)
                #DBM.payIncrease(increase.increase_id)
                #print(DBM.refreshClientDebt(ci))"""
