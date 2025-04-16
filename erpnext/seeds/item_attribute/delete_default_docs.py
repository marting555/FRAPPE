import frappe

def execute():
    frappe.delete_doc("Item Attribute", "Colour", ignore_missing=True)
    frappe.delete_doc("Item Attribute", "Size", ignore_missing=True)



