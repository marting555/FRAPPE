# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

class BudgetAmendment(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.accounts.doctype.budget_amendment_items.budget_amendment_items import BudgetAmendmentItems
        from frappe.types import DF

        amended_from: DF.Link | None
        budget_amendment_items: DF.Table[BudgetAmendmentItems]
        company: DF.Data | None
        posting_date: DF.Data | None
        project: DF.Link | None
        project_name: DF.Data | None
        total_decrement_budget: DF.Data | None
        total_increment_budget: DF.Data | None
        total_overall_budget: DF.Data | None

    def on_submit(self):
        update_original_budget(self,"Submit")
        # for item in self.budget_amendment_items:
        #     budget_entry = frappe.new_doc("Budget Entry")
        #     budget_entry.name = self.name
        #     budget_entry.project = self.project
        #     budget_entry.company = self.company
        #     budget_entry.posting_date = self.posting_date
        #     # budget_entry.document_date = self.document_date

        #     if item.wbs_name:
        #         budget_entry.wbs_name = item.wbs_name

        #     if item.wbs_element:
        #         budget_entry.wbs = item.wbs_element

        #     if item.level:
        #         budget_entry.wbs_level = item.level

        #     if item.increment_budget:
        #         budget_entry.overall_credit = item.increment_budget
            
        #     if item.decrement_budget:
        #         budget_entry.overall_debit = item.decrement_budget
            
        #     budget_entry.voucher_no = self.name
        #     budget_entry.voucher_type = "Budget Amendment"
        #     budget_entry.voucher_submit_date = now()

        #     budget_entry.insert()
        #     budget_entry.submit()

        # update_wbs(self)

    def on_cancel(self):
        self.flags.ignore_links = True

    def before_cancel(self):
        update_original_budget(self,"Cancel")

# def update_wbs(self):
#     for row in self.budget_amendment_items:
#         wbs = frappe.get_doc("Work Breakdown Structure",row.wbs_element)
#         if row.increment_budget:
#             wbs.overall_budget += row.increment_budget
#         elif row.decrement_budget:
#             wbs.overall_budget -= row.decrement_budget
#         wbs.save()

# def create_cancelled_budget_entries(self):
#     for item in self.budget_amendment_items:
#         budget_entry = frappe.new_doc("Budget Entry")
#         budget_entry.name = self.name
#         budget_entry.project = self.project
#         budget_entry.company = self.company
#         budget_entry.posting_date = self.posting_date
#         # budget_entry.document_date = self.document_date

#         if item.wbs_name:
#             budget_entry.wbs_name = item.wbs_name

#         if item.wbs_element:
#             budget_entry.wbs = item.wbs_element

#         if item.level:
#             budget_entry.wbs_level = item.level

#         if item.increment_budget:
#             budget_entry.overall_debit = item.increment_budget
        
#         if item.decrement_budget:
#             budget_entry.overall_credit = item.decrement_budget
        
#         budget_entry.voucher_no = self.name
#         budget_entry.voucher_type = "Budget Amendment"
#         budget_entry.voucher_submit_date = now()

#         budget_entry.insert()
#         budget_entry.submit()

#     update_wbs_after_cancellation(self)

# def update_wbs_after_cancellation(self):
#     for row in self.budget_amendment_items:
#         wbs = frappe.get_doc("Work Breakdown Structure",row.wbs_element)
#         if row.increment_budget:
#             wbs.overall_budget -= row.increment_budget
#         elif row.decrement_budget:
#             wbs.overall_budget += row.decrement_budget
#         wbs.save()

def update_original_budget(self,event):
    wbs_dict = []
    wbs_list = []
    if self.budget_amendment_items:
        for row in self.budget_amendment_items:
            if row.get("wbs_element") not in wbs_list:
                wbs_list.append(row.get("wbs_element"))
    if wbs_list:
        for i in wbs_list:
            wbs_dict.append({
                "wbs_id": i,
                "voucher_name":"",
                "voucher_type":"",
            })

    for row in self.budget_amendment_items:
        amount = row.get("total")
        if row.get("wbs_element"):
            for j in wbs_dict:
                if row.get("wbs_element") == j.get("wbs_id"):
                    j.update({
                        "amount": row.get("total"),
                        "wbs_name": frappe.db.get_value("Work Breakdown Structure",row.get("wbs_element"), "wbs_name"),
                        "wbs_level":row.get("level"),
                        "txn_date":self.posting_date,
                        "voucher_type":self.doctype,
                        "voucher_name":self.name,
                        "increment_budget": row.get("increment_budget"),
                        "decrement_budget": row.get("decrement_budget")
                    })
            wbs_curr_doc = frappe.get_doc("Work Breakdown Structure",row.get("wbs_element"))
            if event == "Submit":
                wbs_curr_doc.overall_budget = wbs_curr_doc.overall_budget + amount

                wbs_curr_doc.assigned_overall_budget = wbs_curr_doc.actual_overall_budget + wbs_curr_doc.committed_overall_budget
                wbs_curr_doc.available_budget = wbs_curr_doc.overall_budget - wbs_curr_doc.assigned_overall_budget
                if wbs_curr_doc.locked:
                    frappe.throw(
                        "Transaction Not Allowed for  WBS Element - {0} as this WBS is locked !".format(wbs_curr_doc.name)
                    )
            elif event == "Cancel":
                wbs_curr_doc.overall_budget = wbs_curr_doc.overall_budget - amount

                wbs_curr_doc.assigned_overall_budget = wbs_curr_doc.actual_overall_budget + wbs_curr_doc.committed_overall_budget
                wbs_curr_doc.available_budget = wbs_curr_doc.overall_budget - wbs_curr_doc.assigned_overall_budget
                if wbs_curr_doc.locked:
                    frappe.throw(
                        "Transaction Not Allowed for  WBS Element - {0} as this WBS is locked !".format(wbs_curr_doc.name)
                    )
            wbs_curr_doc.save(ignore_permissions=True)

    if wbs_dict:
        for i in wbs_dict:
            create_budget_entry(self,i,event,self.company) 
    
def create_budget_entry(self,row,event,company):
    if row.get("wbs_id"):
        bgt_ent = frappe.new_doc("Budget Entry")
        bgt_ent.project = self.project
        bgt_ent.wbs = row.get("wbs_id")
        bgt_ent.wbs_name = row.get("wbs_name")
        bgt_ent.wbs_level = row.get("wbs_level")
        bgt_ent.company = company
        bgt_ent.posting_date = self.posting_date
        if event == "Submit":
            bgt_ent.overall_credit = row.get("amount")            
        elif event == "Cancel":
            bgt_ent.overall_debit = row.get("amount")   

        bgt_ent.voucher_type = "Budget Amendment"
        bgt_ent.voucher_no = self.name
        bgt_ent.voucher_submit_date = now()
        bgt_ent.save(ignore_permissions=True)
        bgt_ent.submit()
