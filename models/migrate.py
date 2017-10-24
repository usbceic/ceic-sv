from db_manager import dbManager
from models import *
from sqlalchemy import func

DBM = dbManager()
for product in DBM.getProducts(product_id = True, product_name = True, price = True):
    product_id, product_name, price = product

    query = DBM.session.query(Purchase.ci, Product_list.price, func.sum(Product_list.amount).label("amount"))\
        .join(Debt, Purchase.purchase_id == Debt.purchase_id)\
        .join(Product_list, Purchase.purchase_id == Product_list.purchase_id)\
        .filter(Debt.pay_date == None, Product_list.product_id == product_id)\
        .group_by(Purchase.ci, Product_list.price)\
        .all()

    for res in query:
        if (price > float(res.price)):
            kwargs = (product_name, str(res.price), str(price))
            description = "Ajuste automatico por cambio de precio del producto %s (de %s a %s)."
            DBM.createIncrease(res.ci, "usbceic", (float(price)-float(res.price))*int(res.amount), description % kwargs)
