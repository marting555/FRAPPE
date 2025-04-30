import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = fetch_vat_data(filters)

    return columns, data

def fetch_vat_data(filters):
    from_date = filters.get("from_date", "1900-01-01")
    to_date = filters.get("to_date", "2100-12-31")
    company = filters.get("company", "")

    query = """
        SELECT
            SUM(CASE WHEN si.tax_category LIKE CONCAT("%%", "21", "%%") THEN si.base_net_total ELSE 0 END) AS domestic_high_rate,
            SUM(CASE WHEN si.tax_category LIKE CONCAT("%%", "9", "%%") THEN si.base_net_total ELSE 0 END) AS domestic_low_rate,
            SUM(CASE WHEN si.tax_category LIKE CONCAT("%%", "tarief", "%%") 
                     AND si.tax_category NOT LIKE CONCAT("%%", "0", "%%") 
                     AND si.tax_category NOT LIKE CONCAT("%%", "21", "%%") 
                     AND si.tax_category NOT LIKE CONCAT("%%", "9", "%%") 
                 THEN si.base_net_total ELSE 0 END) AS domestic_other_rates,
            SUM(CASE WHEN si.tax_category LIKE CONCAT("%%", "priv", "%%") OR si.remarks LIKE CONCAT("%%", "priv", "%%") THEN si.base_net_total ELSE 0 END) AS private_use,
            SUM(CASE WHEN si.tax_category LIKE CONCAT("%%", "vrijgesteld", "%%") THEN si.base_net_total ELSE 0 END) AS exempt_sales,
            SUM(CASE WHEN stc.description LIKE CONCAT("%%", "verlegd", "%%") OR stc.account_head LIKE CONCAT("%%", "verlegd", "%%") THEN stc.base_tax_amount ELSE 0 END) AS reverse_charge,
            SUM(CASE WHEN si.incoterm IS NOT NULL AND si.incoterm LIKE CONCAT("%%", "export", "%%") THEN si.base_net_total ELSE 0 END) AS export_outside_EU,
            SUM(CASE WHEN si.tax_category LIKE CONCAT("%%", "EU", "%%") AND si.base_net_total > 0 THEN si.base_net_total ELSE 0 END) AS intra_EU_sales,
            SUM(CASE WHEN si.tax_category LIKE CONCAT("%%", "afstand", "%%") OR si.remarks LIKE CONCAT("%%", "installatie", "%%") THEN si.base_net_total ELSE 0 END) AS distance_sales_EU,
            SUM(CASE WHEN pi.tax_category LIKE CONCAT("%%", "diensten", "%%") AND pi.tax_category LIKE CONCAT("%%", "buiten", "%%") THEN pi.base_net_total ELSE 0 END) AS services_outside_EU,
            SUM(CASE WHEN pi.tax_category LIKE CONCAT("%%", "diensten", "%%") AND pi.tax_category LIKE CONCAT("%%", "EU", "%%") THEN pi.base_net_total ELSE 0 END) AS services_EU,
            SUM(pi.base_total_taxes_and_charges) AS input_tax,
            SUM(si.base_total_taxes_and_charges) AS output_tax_due,
            SUM(si.base_total_taxes_and_charges) - SUM(pi.base_total_taxes_and_charges) AS net_payable_or_refundable
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Taxes and Charges` stc ON stc.parent = si.name AND stc.parenttype = "Sales Invoice"
        LEFT JOIN `tabPurchase Invoice` pi ON pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
        WHERE si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            AND si.docstatus = 1
            AND (pi.docstatus = 1 OR pi.docstatus IS NULL)
            AND si.company = %(company)s
    """

    result = frappe.db.sql(query, {
        "from_date": from_date,
        "to_date": to_date,
        "company": company
    }, as_dict=True)

    if not result or not result[0]:
        return []

    vat = result[0]
    return [
        {"rubric": "1a", "description": _("Domestic sales with high VAT rate (21%)"), "amount": vat.domestic_high_rate},
        {"rubric": "1b", "description": _("Domestic sales with low VAT rate (9%)"), "amount": vat.domestic_low_rate},
        {"rubric": "1c", "description": _("Other VAT rates"), "amount": vat.domestic_other_rates},
        {"rubric": "1d", "description": _("Private use (privégebruik)"), "amount": vat.private_use},
        {"rubric": "1e", "description": _("Sales at 0% or exempt (vrijgesteld)"), "amount": vat.exempt_sales},
        {"rubric": "2a", "description": _("Domestic reverse charge (verlegd)"), "amount": vat.reverse_charge},
        {"rubric": "3a", "description": _("Exports outside the EU"), "amount": vat.export_outside_EU},
        {"rubric": "3b", "description": _("Intra-EU sales"), "amount": vat.intra_EU_sales},
        {"rubric": "3c", "description": _("Distance/installation sales within EU"), "amount": vat.distance_sales_EU},
        {"rubric": "4a", "description": _("Services from outside the EU"), "amount": vat.services_outside_EU},
        {"rubric": "4b", "description": _("Services from within the EU"), "amount": vat.services_EU},
        {"rubric": "5b", "description": _("Input VAT from purchases"), "amount": vat.input_tax},
        {"rubric": "5a", "description": _("Total output VAT payable"), "amount": vat.output_tax_due},
        {"rubric": "5c", "description": _("Subtotal (output VAT - input VAT)"), "amount": vat.net_payable_or_refundable},
        {"rubric": "5d", "description": _("Small business scheme deduction (KOR)"), "amount": 0.0},
        {"rubric": "5e", "description": _("Correction(s) from previous declarations"), "amount": 0.0},
        {"rubric": "5f", "description": _("Estimated for this declaration"), "amount": 0.0},
        {"rubric": "Total", "description": _("VAT Payable/Refundable"), "amount": vat.net_payable_or_refundable}
    ]

def get_columns():
    return [
        {"fieldname": "rubric", "label": _("Rubric"), "fieldtype": "Data", "width": 80},
        {"fieldname": "description", "label": _("Description"), "fieldtype": "Data", "width": 300},
        {"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency", "width": 150}
    ]