import frappe



def execute():
    doc = frappe.get_doc("Item Attribute", "jewelry.color")
    print(doc)
    print(doc.__dict__)