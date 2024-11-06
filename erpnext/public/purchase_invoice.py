import frappe
from frappe import _

def on_submit(self, method):
    total = self.grand_total
    doc = frappe.get_doc("Work Breakdown Structure",self.custom_work_breakdown_structure)
    doc.actual_overall_budget += total
    doc.save()

def before_submit(self, method):
    data_from = frappe.new_doc("Budget Entry")
    data_from.voucher_type = self.doctype  # This sets it to the current doctype name
    data_from.project = self.custom_project
    data_from.company = self.company
    data_from.posting_date = self.transaction_date
    data_from.document_date = self.transaction_date
    data_from.wbs = self.custom_work_breakdown_structure
    data_from.wbs_name = self.custom_wbs_name
    data_from.voucher_no = self.self.name
    
    data_from.committed_overall_debit = self.custom_total
    data_from.insert()