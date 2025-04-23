# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HandleParts(Document):
    pass


@frappe.whitelist()
def update_transmission_codes(items):
    """
    Update transmission codes for items
    :param items: List of dictionaries containing tvs_pn_new, tvs_pn_rebuild, and bakcodes
    :return: Dictionary with success message and list of failed items
    """
    failed_items = []
    updated_items = []

    try:
        for item in items:
            tvs_pn_new = item.get('tvs_pn_new')
            tvs_pn_rebuild = item.get('tvs_pn_rebuild')
            bakcodes = item.get('bakcodes')

            if not bakcodes:
                if tvs_pn_new:
                    failed_items.append(tvs_pn_new)
                if tvs_pn_rebuild:
                    failed_items.append(tvs_pn_rebuild)
                continue

            # Transform bakcodes into required format
            transmission_codes = [{"transmission_code": code} for code in bakcodes]

            # Update item with tvs_pn_new
            try:
                if tvs_pn_new:
                    doc = frappe.get_doc('Item', tvs_pn_new)
                    doc.transmission_code_list = []  # Clear existing codes
                    for code in transmission_codes:
                        doc.append('transmission_code_list', code)
                    doc.save()
                    updated_items.append(tvs_pn_new)
            except Exception as e:
                print(f"Error updating {tvs_pn_new}: {str(e)}")
                failed_items.append(tvs_pn_new)

            # Update item with tvs_pn_rebuild
            try:
                if tvs_pn_rebuild:
                    doc = frappe.get_doc('Item', tvs_pn_rebuild)
                    doc.transmission_code_list = []  # Clear existing codes
                    for code in transmission_codes:
                        doc.append('transmission_code_list', code)
                    doc.save()
                    updated_items.append(tvs_pn_rebuild)
            except Exception as e:
                print(f"Error updating {tvs_pn_rebuild}: {str(e)}")
                failed_items.append(tvs_pn_rebuild)

        frappe.db.commit()
        return {
            "message": "Process completed",
            "updated_items": updated_items,
            "failed_items": failed_items
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.throw(f"Error in update process: {str(e)}")
