# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    """
    Execute the VAT declaration report to fetch VAT data for tax reporting requirements.
    """
    if not filters:
        filters = {}

    columns = get_columns()
    data = fetch_vat_data(filters)

    return columns, data


def fetch_vat_data(filters):
    """
    Fetch sales and purchase invoice data for VAT declaration
    """
    from_date = filters.get("from_date", "1900-01-01")
    to_date = filters.get("to_date", "2100-12-31")
    company = filters.get("company", "")

    # Use format strings with named placeholders to avoid % formatting issues
    query = """
        SELECT
            SUM(CASE WHEN si.tax_category LIKE CONCAT('%%', '21', '%%') THEN si.base_net_total ELSE 0 END) AS domestic_high_rate,
            SUM(CASE WHEN si.tax_category LIKE CONCAT('%%', '9', '%%') THEN si.base_net_total ELSE 0 END) AS domestic_low_rate,
            SUM(CASE WHEN si.tax_category LIKE CONCAT('%%', 'tarief', '%%') 
                AND si.tax_category NOT LIKE CONCAT('%%', '0', '%%') 
                AND si.tax_category NOT LIKE CONCAT('%%', '21', '%%') 
                AND si.tax_category NOT LIKE CONCAT('%%', '9', '%%') 
                THEN si.base_net_total ELSE 0 END) AS domestic_other_rates,
            SUM(CASE WHEN si.tax_category LIKE CONCAT('%%', '0', '%%') THEN si.base_net_total ELSE 0 END) AS domestic_zero_rate,
            SUM(CASE WHEN si.incoterm IS NOT NULL AND si.incoterm LIKE CONCAT('%%', 'export', '%%') THEN si.base_net_total ELSE 0 END) AS exports_outside_EU,
            SUM(CASE WHEN si.tax_category LIKE CONCAT('%%', 'EU', '%%') THEN si.base_net_total ELSE 0 END) AS intra_EU_sales,
            SUM(pi.base_total_taxes_and_charges) AS input_tax,
            SUM(si.base_total_taxes_and_charges) AS output_tax_due,
            SUM(si.base_total_taxes_and_charges) - SUM(pi.base_total_taxes_and_charges) AS net_payable_or_refundable
        FROM `tabSales Invoice` si
        LEFT JOIN `tabPurchase Invoice` pi
            ON pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
        WHERE si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            AND si.docstatus = 1
            AND (pi.docstatus = 1 OR pi.docstatus IS NULL)
            AND si.company = %(company)s
    """

    result = frappe.db.sql(
        query,
        {
            "from_date": from_date,
            "to_date": to_date,
            "company": company
        },
        as_dict=1
    )

    formatted_data = []
    if result and len(result) > 0:
        vat_data = result[0]

        formatted_data.extend([
            {
                "rubric": "1a",
                "description": _("Domestic sales with high VAT rate (21%)"),
                "amount": vat_data.get("domestic_high_rate", 0)
            },
            {
                "rubric": "1b",
                "description": _("Domestic sales with low VAT rate (9%)"),
                "amount": vat_data.get("domestic_low_rate", 0)
            },
            {
                "rubric": "1c",
                "description": _("Other VAT rates"),
                "amount": vat_data.get("domestic_other_rates", 0)
            },
            {
                "rubric": "2",
                "description": _("Sales taxed at 0% or not subject to VAT"),
                "amount": vat_data.get("domestic_zero_rate", 0)
            },
            {
                "rubric": "3b",
                "description": _("Exports outside the EU"),
                "amount": vat_data.get("exports_outside_EU", 0)
            },
            {
                "rubric": "3c",
                "description": _("Intra-EU sales"),
                "amount": vat_data.get("intra_EU_sales", 0)
            },
            {
                "rubric": "4",
                "description": _("Input VAT from purchases"),
                "amount": vat_data.get("input_tax", 0)
            },
            {
                "rubric": "5a",
                "description": _("Total output VAT payable"),
                "amount": vat_data.get("output_tax_due", 0)
            },
            {
                "rubric": "5c",
                "description": _("Subtotal (output VAT - input VAT)"),
                "amount": vat_data.get("net_payable_or_refundable", 0)
            }
        ])

    return formatted_data


def get_columns():
    """
    Define the columns for the VAT declaration report
    """
    return [
        {
            "fieldname": "rubric",
            "label": _("Rubric"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "description",
            "label": _("Description"),
            "fieldtype": "Data",
            "width": 300
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 150
        }
    ]
