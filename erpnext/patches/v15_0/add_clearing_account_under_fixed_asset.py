import frappe


def execute():
	account_name = "Clearing Account"
	account_type = "Fixed Asset"
	parent_group = "Fixed Assets"
	is_group = 0

	companies = frappe.get_all("Company", fields=["name"])

	for company in companies:
		if not frappe.db.exists("Account", {"account_name": account_name, "company": company.name}):
			parent_account = frappe.get_value(
				"Account", {"account_name": parent_group, "company": company.name}, "name"
			)

			account = frappe.get_doc(
				{
					"doctype": "Account",
					"account_name": account_name,
					"company": company.name,
					"is_group": is_group,
					"account_type": account_type,
					"root_type": "Asset",
					"parent_account": parent_account,
				}
			)

			account.insert(ignore_permissions=True)

			frappe.db.set_value("Company", company, "asset_clearing_account", account.name)

			aca = frappe.qb.DocType("Asset Category Account")
			(
				frappe.qb.update(aca)
				.set(aca.asset_clearing_account, account.name)
				.where((aca.company_name == company.name) & (aca.asset_clearing_account.isnull()))
			).run()
