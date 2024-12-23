import frappe
from frappe import _


def create_ldc(doc, supplier):
	try:
		ldc_doc = frappe.new_doc("Lower Deduction Certificate")
		ldc_doc.supplier = supplier
		ldc_doc.valid_from = doc.from_date
		ldc_doc.valid_upto = doc.to_date
		ldc_doc.certificate_no = doc.certificate_no
		ldc_doc.rate = doc.rate
		ldc_doc.certificate_limit = doc.amount
		ldc_doc.company = frappe.db.get_value("Company", ["name"])
		ldc_doc.fiscal_year = frappe.db.get_value("Fiscal Year", {"disabled": 0}, ["name"])
		ldc_doc.custom_ldc_upload = doc.ldc_upload
		ldc_doc.pan_no = doc.pan_mention_no_here
		ldc_doc.tax_withholding_category = doc.tax_withholding_category
		ldc_doc.save(ignore_permissions=True)
		return ldc_doc
	except Exception as e:
		frappe.throw(_("ldc_doc cannot be created due to the following error <br>{0}").format(e))
