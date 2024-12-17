import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Coalesce


def execute():
	if frappe.db.has_column("GL Entry", "asset"):
		process_asset_submission_entries()
		process_asset_repair_entries()
		process_asset_related_journal_entries()  # Revaluation and Depreciation
		process_asset_capitalization_entries()


def process_asset_submission_entries():
	gl_entry = DocType("GL Entry")
	asset = DocType("Asset")

	query = (
		frappe.qb.update(gl_entry)
		.join(asset)
		.on(gl_entry.voucher_no == asset.name)
		.set(gl_entry.asset, Coalesce(asset.name, ""))
		.where((gl_entry.voucher_type == "Asset") & (gl_entry.debit > 0) & (gl_entry.is_cancelled == 0))
	)
	query.run()


def process_asset_repair_entries():
	# nosemgrep
	frappe.db.sql(
		"""
        UPDATE `tabGL Entry` AS gl
        INNER JOIN `tabAsset Repair` AS ar
            ON gl.voucher_no = ar.name
        SET gl.asset = ar.asset
        WHERE gl.voucher_type = 'Asset Repair'
          AND gl.debit > 0
        """
	)


def process_asset_related_journal_entries():
	gl_entry = DocType("GL Entry")
	asset = DocType("Asset")

	query = (
		frappe.qb.update(gl_entry)
		.join(asset)
		.on(gl_entry.against_voucher == asset.name)
		.set(gl_entry.asset, Coalesce(asset.name, ""))
		.where((gl_entry.voucher_type == "Journal Entry") & (gl_entry.against_voucher_type == "Asset"))
	)
	query.run()


def process_asset_capitalization_entries():
	# nosemgrep
	frappe.db.sql(
		"""
        UPDATE `tabGL Entry` AS gl
        INNER JOIN `tabAsset Capitalization Asset Item` AS acai
            ON gl.voucher_no = acai.parent
            AND gl.account = acai.fixed_asset_account
        INNER JOIN `tabAsset` AS asset
            ON acai.asset = asset.name
            AND gl.credit = asset.gross_purchase_amount
        SET gl.asset = acai.asset
        WHERE gl.voucher_type = 'Asset Capitalization'
          AND gl.credit > 0
        """
	)
