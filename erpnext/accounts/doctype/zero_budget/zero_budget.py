# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from typing import TYPE_CHECKING, Optional
from frappe import _
from frappe.utils import now
from frappe.model.document import Document

class ZeroBudget(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.accounts.doctype.zero_budget_item.zero_budget_item import ZeroBudgetItem
        from frappe.types import DF

        amended_from: DF.Link | None
        budget_entry: DF.Link | None
        company: DF.Link | None
        posting_date: DF.Date | None
        project: DF.Link | None
        total: DF.Currency
        zero_budget_item: DF.Table[ZeroBudgetItem]
    # end: auto-generated types
    import frappe
from frappe.model.document import Document

class ZeroBudget(Document):
    def on_submit(self):
        for item in self.zero_budget_item:
            data = frappe.new_doc("Budget Entry")
            data.name = self.name
            data.project = self.project
            data.company = self.company
            data.posting_date = self.posting_date
            # data.document_date = self.document_date

            if item.wbs_name:
                data.wbs_name = item.wbs_name

            if item.wbs_element:
                data.wbs = item.wbs_element

            if item.wbs_level:
                data.wbs_level = item.wbs_level

            if item.zero_budget:
                data.overall_credit = item.zero_budget
            
            data.voucher_no = self.name
            data.voucher_type = "Zero Budget"
            data.voucher_submit_date = now()

            data.insert()
            data.submit()
    def on_cancel(self):
        self.flags.ignore_links = True
        print("on cancel")

    def before_cancel(self):
        print("rrrrrrrrrrrrrrrr")
        update_wbs(self)
        create_cancelled_budget_entries(self)


    def before_save(self):
        # print("rrrrrrrrrrrrrrrr")
        if frappe.db.exists("Zero Budget", {"project": self.project, "docstatus": ["!=", 2]}):
            frappe.throw(_(f"There already exists one Zero Budget with project {self.project}"))
 
        for row in self.zero_budget_item:
            doc = frappe.get_doc("Work Breakdown Structure",row.wbs_element)
            doc.original_budget = row.zero_budget
            doc.overall_budget = row.zero_budget
            doc.save()

    def validate(self):
        for row in self.zero_budget_item:
            is_locked = frappe.db.get_value("Work Breakdown Structure",row.wbs_element,"locked")
            if is_locked:
                frappe.throw(_(f"WBS {row.wbs_element} is locked"))



# Type checking for better IDE support and type hints
if TYPE_CHECKING:
    from erpnext.accounts.doctype.zero_budget_item.zero_budget_item import ZeroBudgetItem
    from frappe.types import DF

    company: Optional[DF.Link] = None
    document_date: Optional[DF.Date] = None
    posting_date: Optional[DF.Date] = None
    project: Optional[DF.Link] = None
    zero_budget_item: DF.Table[ZeroBudgetItem]


import frappe

@frappe.whitelist(allow_guest=True)
def work_breakdown_structure(project):
    print("Project : ",project)
    # Fetch WBS records linked to the specified project
    wbs = frappe.get_all(
        "Work Breakdown Structure",
        fields=["name", "wbs_name", "wbs_level", "overall_budget", "gl_account", "available_budget"],
        filters={"project": project,"docstatus":1}  # Only filter by project
    )
    return wbs

def update_wbs(self):
    for row in self.zero_budget_item:
        wbs = frappe.get_doc("Work Breakdown Structure",row.wbs_element)
        wbs.original_budget -= row.zero_budget
        wbs.save()

def create_cancelled_budget_entries(self):
    for item in self.zero_budget_item:
        budget_entry = frappe.new_doc("Budget Entry")
        budget_entry.name = self.name
        budget_entry.project = self.project
        budget_entry.company = self.company
        budget_entry.posting_date = self.posting_date
        # budget_entry.document_date = self.document_date

        if item.wbs_name:
            budget_entry.wbs_name = item.wbs_name

        if item.wbs_element:
            budget_entry.wbs = item.wbs_element

        if item.wbs_level:
            budget_entry.wbs_level = item.wbs_level

        if item.zero_budget:
            budget_entry.overall_debit = item.zero_budget
        
        budget_entry.voucher_no = self.name
        budget_entry.voucher_type = "Zero Budget"
        budget_entry.voucher_submit_date = now()

        budget_entry.insert()
        budget_entry.submit()

def unlink_budget_entry(self):
    print(11111111111111111111111111)
    budget_entries = frappe.get_all("Budget Entry", filters={"voucher_no": self.name}, fields=["name"])
    for budget_entry in budget_entries:
        print(budget_entry)
        frappe.db.set_value('Budget Entry', budget_entry.name, 'voucher_no', None)
    frappe.db.commit()  # Ensure changes are committed
