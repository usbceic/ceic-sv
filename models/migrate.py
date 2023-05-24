from db_manager import dbManager
from models import *
from sqlalchemy import func

DBM = dbManager()
  ci = 26409963
  debt = '434a29ac-e361-4cc3-b2c4-43f6ba741e3c'
  purchase = 'ebfa672f-4c5a-4996-bb95-155cebda6ac7'
  query = DBM.session.query(Purchase)
"""for ci in DBM.getClientsCI():
    query = DBM.existAutoIncrease(ci, 'Lipton')
    if query is not None:
        for increase in query:
            if increase.pay_date == None:
                print(increase)
                #DBM.payIncrease(increase.increase_id)
                #print(DBM.refreshClientDebt(ci))"""
