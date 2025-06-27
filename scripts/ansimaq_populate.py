import frappe

def run():
    frappe.get_doc({
        "doctype": "Customer",
        "customer_name": "Ansimaq S.A.",
        "customer_type": "Company",
    }).insert()

    frappe.get_doc({
        "doctype": "Item",
        "item_code": "ANS-001",
        "item_name": "Servicio Demo",
        "stock_uom": "Unit",
    }).insert()

    invoice = frappe.get_doc({
        "doctype": "Sales Invoice",
        "customer": "Ansimaq S.A.",
        "items": [{"item_code": "ANS-001", "qty": 1, "rate": 100}],
    })
    invoice.insert()
    frappe.db.commit()


