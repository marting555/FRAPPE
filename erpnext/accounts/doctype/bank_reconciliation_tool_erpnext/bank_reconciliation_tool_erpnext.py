# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
import json
from erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool import get_linked_payments


class BankReconciliationToolERPNext(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.bank_statement.bank_statement import BankStatement
		from erpnext.accounts.doctype.erp_transaction.erp_transaction import ERPTransaction
		from erpnext.accounts.doctype.matching_table.matching_table import MatchingTable
		from frappe.types import DF

		bank_account: DF.Link | None
		bank_statement: DF.Table[BankStatement]
		closing_balance_as_per_bank_statement: DF.Currency
		closing_balance_as_per_erp: DF.Currency
		company: DF.Link | None
		difference_amount: DF.Currency
		erp_transaction: DF.Table[ERPTransaction]
		from_date: DF.Date | None
		from_erp_date: DF.Date | None
		from_statement_date: DF.Date | None
		matching_table: DF.Table[MatchingTable]
		opening_balance: DF.Currency
		to_date: DF.Date | None
		to_erp_date: DF.Date | None
		to_statement_date: DF.Date | None
	# end: auto-generated types
	# pass
	def validate_entries(self):
		if not self.get("erp_transaction"):
			frappe.throw(_("No records found in the ERP Transactions table"))

		if not self.get("bank_statement"):
			frappe.throw(_("No records found in the Bank Statement table"))

	def get_allocated_entry(self, pay, bnk_st, allocated_amount):
		res = frappe._dict(
			{
				"bank_transaction_id": bnk_st.get("bank_transaction_id"),
				"reference_to": pay.get("reference_doc"),
				"matched_amount": allocated_amount,
				"reference_id": pay.get("reference_id"),
			}
		)

		return res

	@frappe.whitelist()
	def allocate_entries(self, args):
		self.validate_entries()

		entries = []

		for pay in args.get("erp_transaction"):
			# Initialize unreconciled_amount for deposit/withdraw
			if flt(pay.get("deposit")) > 0 and flt(pay.get("withdraw")) == 0:
				pay["remaining_amount"] = pay["deposit"]
			elif flt(pay.get("withdraw")) > 0 and flt(pay.get("deposit")) == 0:
				pay["remaining_amount"] = pay["withdraw"]

			for bnk_st in args.get("bank_statement"):
				allocated_amount = min(
					pay.get("remaining_amount", 0), bnk_st["unallocated_amount"]
				)

				res = self.get_allocated_entry(pay, bnk_st, allocated_amount)
				# print(pay.get("name"), pay.get("doctype"))

				# if flt(pay.get("deposit")) > 0:
				# 	pay["deposit"] -= allocated_amount
				# elif flt(pay.get("withdraw")) > 0:
				# 	pay["withdraw"] -= allocated_amount
				pay["remaining_amount"] -= allocated_amount
				bnk_st["unallocated_amount"] -= allocated_amount

				entries.append(res)

				# Break if pay is fully allocated
				if pay.get("remaining_amount") == 0:
					break

		# Update the matching table
		self.set("matching_table", [])
		for entry in entries:
			if entry["matched_amount"] != 0:
				# print('rowwwww',entry["bank_transaction_id"])
				row = self.append("matching_table", {})
				row.update(entry)


@frappe.whitelist()
def get_bank_transaction(bank_account, company, from_statement_date=None, to_statement_date=None):
	if from_statement_date and to_statement_date:
		bank_transactn_list = frappe.db.get_all(
			"Bank Transaction",
			filters={
				"date": ["between", [from_statement_date, to_statement_date]],
				"bank_account": bank_account,
				"company": company,
				"status": "Unreconciled",
			},
			fields=[
				"date",
				"name",
				"deposit",
				"withdrawal",
				"description",
				"reference_number",
				"unallocated_amount",
			],
		)
	else:
		bank_transactn_list = frappe.db.get_all(
			"Bank Transaction",
			filters={"bank_account": bank_account, "company": company, "status": "Unreconciled"},
			fields=[
				"date",
				"name",
				"deposit",
				"withdrawal",
				"description",
				"reference_number",
				"unallocated_amount",
			],
		)
	if len(bank_transactn_list) == 0:
		frappe.msgprint("No records found")

	return bank_transactn_list


@frappe.whitelist()
def get_erp_transaction(bank_account, company, from_statement_date=None, to_statement_date=None):
    # Fetch unreconciled transactions
    transaction_list = frappe.db.get_all(
        "Bank Transaction", 
        filters={"bank_account": bank_account, "status": "Unreconciled"},
        fields=["name"]
    )
    
    # Get the linked account for the bank account
    account = frappe.db.get_value("Bank Account", bank_account, 'account')
    result = []

    for transaction in transaction_list:        
        # Get linked payments or journal entries
        linked_payments = get_linked_payments(
            transaction.name,
            document_types=["payment_entry", "journal_entry"],
            from_date=from_statement_date,
            to_date=to_statement_date,
            filter_by_reference_date=None,
            from_reference_date=from_statement_date,
            to_reference_date=to_statement_date
        )
        
        for payment in linked_payments:
            if payment['doctype'] == "Journal Entry":
                # Fetch journal entry accounts linked to the bank account
                je_accounts = frappe.db.get_all(
                    "Journal Entry Account",
                    filters={
                        'account': account,
                        'parent': payment['name']
                    },
                    fields=['credit_in_account_currency', 'debit_in_account_currency', 'parent', 'remaining_amount']
                )
                for je_account in je_accounts:
                    je_account['remaining_amount'] == payment['paid_amount']
                    if je_account['credit_in_account_currency'] > 0:
                        payment['bank'] = 'Credit'
                        payment['amount'] = je_account['credit_in_account_currency']
                    elif je_account['debit_in_account_currency'] > 0:
                        # je_account['remaining_amount'] == je_account['debit_in_account_currency']
                        payment['bank'] = 'Debit'
                        payment['amount'] = je_account['debit_in_account_currency']
                # print("******************************1111111**********")
                # print(payment)
                # print("*************************111111111***************")
                result.append(payment)
            else:
                # print("****************************************")
                # print(payment)
                # print("****************************************")
                payment['amount'] = frappe.db.get_value("Payment Entry", payment['name'], 'paid_amount')
                result.append(payment)
    if len(result) == 0:
        frappe.msgprint("No records found")
    return result


@frappe.whitelist()
def reconcile_bnk_transaction(bank_transaction_id, amount, name, payment_document):
	bnk_trn = frappe.get_doc("Bank Transaction", bank_transaction_id)
	# print("***********************************")
	# print("docc",bank_transaction_id)
	# print("***********************************")
	bnk_trn.append(
		"payment_entries",
		{"payment_document": payment_document, "payment_entry": name, "allocated_amount": flt(amount)},
	)
	try:
		bnk_trn.save()
		frappe.msgprint(_("Successfully Reconciled"))
	except Exception as e:
		frappe.msgprint("Please Reconcile again to ")



@frappe.whitelist()
def get_closing_bal_bnk(bank_account):
	total_credits = (
		frappe.db.sql(
			"""
		SELECT SUM(deposit)
		FROM `tabBank Transaction`
		WHERE bank_account = %s AND docstatus = 1
	""",
			(bank_account),
		)[-1][-1]
		or 0
	)

	# Sum of debits (withdrawals)
	total_debits = (
		frappe.db.sql(
			"""
		SELECT SUM(withdrawal)
		FROM `tabBank Transaction`
		WHERE bank_account = %s AND docstatus = 1
	""",
			(bank_account),
		)[-1][-1]
		or 0
	)

	print("^^^^^^^^^^^^^^^BNK^^^^^^^^^^^^^^^^^^^^^^^")
	print('cr',total_credits)
	print('deb',total_debits)
	print("^^^^^^^^^^^^^^^BNK^^^^^^^^^^^^^^^^^^^^^^^")
	
	# Calculate closing balance
	closing_balance = float(total_credits) - float(total_debits)
	return closing_balance

@frappe.whitelist()
def get_closing_bal_erp(opening_balance, bank_account, from_date, to_date):
	total_credits = (
		frappe.db.sql(
			"""
		SELECT SUM(allocated_amount)
		FROM `tabBank Transaction`
		WHERE bank_account = %s AND docstatus = 1 AND deposit > 0 AND date between %s AND %s
	""",
			(bank_account, from_date, to_date),
		)[-1][-1]
		or 0
	)

	# Sum of debits (withdrawals)
	total_debits = (
		frappe.db.sql(
			"""
		SELECT SUM(allocated_amount)
		FROM `tabBank Transaction`
		WHERE bank_account = %s AND docstatus = 1 AND withdrawal > 0 AND date between %s AND %s
	""",
			(bank_account, from_date, to_date),
		)[-1][-1]
		or 0
	)
	
	print("^^^^^^^^^^^^^^^ERP^^^^^^^^^^^^^^^^^^^^^^^")
	print('cr',total_credits)
	print('db',total_debits)
	print("^^^^^^^^^^^^^^^ERP^^^^^^^^^^^^^^^^^^^^^^^")
	# Calculate closing balance
	closing_balance = flt(opening_balance) + float(total_credits) - float(total_debits)
	return closing_balance
