# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class VendorRegistration(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_number: DF.Data | None
		account_type: DF.Literal["", "Savings A/c", "Current A/c"]
		address_line_1: DF.Data | None
		address_line_2: DF.Data | None
		amended_from: DF.Link | None
		amount: DF.Currency
		are_you_registered_as_msme: DF.Literal["", "Yes", "No"]
		at_contact: DF.Data | None
		at_designation: DF.Data | None
		at_name: DF.Data | None
		attach_article_of_association: DF.Attach | None
		attach_cancelled_cheque: DF.Attach | None
		attach_certificate_of_incorporation: DF.Attach | None
		attach_gst_registration: DF.Attach | None
		attach_iso_certificate_if_any: DF.Attach | None
		attach_itr_acknowledgement: DF.Attach | None
		attach_last_3_years_annual_report: DF.Attach | None
		attach_memorandum_of_association: DF.Attach | None
		attach_msme_certificate: DF.Attach | None
		attach_pan: DF.Attach | None
		attach_tan: DF.Attach | None
		bank_name: DF.Link | None
		billing_currency: DF.Link | None
		branch_address: DF.Data | None
		branch_name: DF.Data | None
		brand_nametrademark: DF.Data | None
		bt_contact: DF.Data | None
		bt_name: DF.Data | None
		certificate_no: DF.Data | None
		city: DF.Data | None
		corporatelimited_liability_identification_no_cinllin: DF.Data | None
		country: DF.Link | None
		country_of_tax_residence: DF.Data | None
		date_last: DF.Date | None
		date_of_incorporation: DF.Date | None
		declaration_incase_msme_not_applicable: DF.Check
		designation: DF.Data | None
		email_at: DF.Data | None
		email_bt: DF.Data | None
		employee_strength_slab: DF.Literal["", "0 to 10", "11 to 50", "51 to 100", "101 to 200", "201 to 500", "501 to 1000", "Above 1000"]
		entity_type: DF.Literal["Public limited Company", "Private limited Company", "Joint venture Company", "One person Company", "Section 8 Company", "Limited Liability Partnership", "Partnership Firm", "Sole Proprietorship", "Non-government organization (NGO)", "Association of Person/ Body of Individual", "Local Authority", "Artificial Juridical Person"]
		form_10f_generated_on_indian_income_tax_portal: DF.Data | None
		from_date: DF.Date | None
		gst_no: DF.Data | None
		gst_registered: DF.Literal["", "Yes", "No"]
		gst_registration_category: DF.Literal["", "Registered Regular", "Registered Composition", "Unregistered", "SEZ", "Overseas", "Deemed Export", "UIN Holders", "Tax Deductor"]
		i_agree: DF.Check
		ifsc_code: DF.Data | None
		itr_filed_for_latest_financial_year: DF.Literal["", "Yes", "No"]
		ldc_upload: DF.Attach | None
		lower_tds_deduction_applicable: DF.Literal["", "Yes", "No"]
		msme_certificate_no: DF.Data | None
		msme_type: DF.Literal["", "Micro", "Small", "Medium"]
		name_last: DF.Data | None
		nationality: DF.Literal["", "Indian", "Foreign"]
		nature_of_business: DF.Data | None
		other_bank: DF.Data | None
		pan_applicable: DF.Literal["", "Yes", "No"]
		pan_mention_no_here: DF.Data | None
		panaadhar_linking_doc: DF.Attach | None
		panaadhar_linking_status: DF.Literal["", "Yes", "No"]
		partnership_deed_incase_of_firms: DF.Attach | None
		pe_certificate: DF.Attach | None
		pincodezip: DF.Data | None
		rate: DF.Percent
		spoc: DF.Data | None
		spoc_email: DF.Link | None
		state: DF.Literal["", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Delhi", "Puducherry", "Other Territories"]
		supplier_group: DF.Link | None
		swift_code: DF.Data | None
		tan: DF.Literal["", "Yes", "No"]
		tan_mention_no_here: DF.Data | None
		tax_identification_number_tin: DF.Data | None
		tax_residency_certificate_trc: DF.Data | None
		tax_withholding_category: DF.Link | None
		tds_section: DF.Data | None
		title: DF.Data | None
		to_date: DF.Date | None
		turnover_slab_in_inr: DF.Literal["", "Upto 20 Lakhs", "20 Lakhs to 1 Crores", "1.1 Crores to 5 Crores", "5.1 Crores to 10 Crores", "10.1 Crores to 50 Crores", "50.1 Crores to 100 Crores", "100.1 Crores to 500 Crores", "500.1 Crores to 1000 Crores"]
		vendor_name: DF.Data | None
		website: DF.Data | None
	# end: auto-generated types
	def validate(self):
		create_vendor_entry(self)

def create_vendor_entry(self):
	if self.docstatus == 1:
		supplier = frappe.db.exists("Supplier", self.vendor_name)
		if not supplier:
			# create supplier
			supplier = create_supplier(self)
			# create address
			address = create_address(self, supplier)
			# create contact
			contact = create_contact(self, supplier)
			# create bank account
			bank_acc = create_bank_account(self)
			# create LDC entry
			if self.lower_tds_deduction_applicable == "Yes":
				ldc_entry = create_ldc(self, supplier)
				if ldc_entry:
					frappe.msgprint(
						_(
							"The following documents are created <br><ol><li>Supplier: {0}</li><li>Address: {1}</li><li>Contact: {2}</li><li>Bank: {3}</li></li><li>LDC: {4}</li></ol>"
						).format(supplier, address, contact, bank_acc, ldc_entry)
					)
			else:
				frappe.msgprint(
					_(
						"The following documents are created <br><ol><li>Supplier: {0}</li><li>Address: {1}</li><li>Contact: {2}</li><li>Bank: {3}</li></ol>"
					).format(supplier, address, contact, bank_acc)
				)
		else:
			frappe.throw(_("Supplier already exists in the system"))

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

def create_supplier(vendor_registration_doc):
	try:
		supplier = frappe.new_doc("Supplier")
		supplier.supplier_name = vendor_registration_doc.vendor_name
		supplier.supplier_type = "Company"
		supplier.custom_entity_type = vendor_registration_doc.entity_type
		supplier.custom_brand_name_trademark = vendor_registration_doc.brand_nametrademark
		supplier.custom_nature_of_business_short_description = vendor_registration_doc.nature_of_business
		supplier.custom_spoc_email = vendor_registration_doc.spoc_email
		supplier.custom_spoc = vendor_registration_doc.spoc
		# supplier.custom_spoc_contact_no = vendor_registration_doc.spoc_contact_no
		supplier.custom_date_of_incorporation = vendor_registration_doc.date_of_incorporation
		supplier.default_currency = vendor_registration_doc.billing_currency
		supplier.custom_employee_strength_slab = vendor_registration_doc.employee_strength_slab
		supplier.custom_turnover_slab_in_inr = vendor_registration_doc.turnover_slab_in_inr
		supplier.custom_nationality = vendor_registration_doc.nationality
		supplier.custom_website = vendor_registration_doc.website
		supplier.custom_name = vendor_registration_doc.name_last
		supplier.custom_place = vendor_registration_doc.title
		# supplier.tax_category = vendor_registration_doc.tax_category
		# supplier.custom_gst_registered = vendor_registration_doc.gst_registered
		supplier.gstin = vendor_registration_doc.gst_no
		supplier.gst_category = vendor_registration_doc.gst_registration_category
		supplier.tax_withholding_category = vendor_registration_doc.tax_withholding_category
		supplier.msme_applicable = vendor_registration_doc.are_you_registered_as_msme
		supplier.msme_certificate = vendor_registration_doc.msme_certificate_no
		supplier.custom_msme_type = vendor_registration_doc.msme_type
		supplier.custom_pan_applicable = vendor_registration_doc.pan_applicable
		supplier.custom_panaadhar_linking_status = vendor_registration_doc.are_you_registered_as_msme
		supplier.custom_tan = vendor_registration_doc.tan
		supplier.pan = vendor_registration_doc.pan_mention_no_here
		supplier.custom_tan_mention_no_here = vendor_registration_doc.tan_mention_no_here
		supplier.custom_from_date = vendor_registration_doc.from_date
		supplier.custom_to_date = vendor_registration_doc.to_date
		supplier.supplier_group = vendor_registration_doc.supplier_group
		# supplier.custom_declaration_incase_e_invoice_not_applicable = (
		# 	vendor_registration_doc.declaration_incase_e_invoice_not_applicable
		# )
		supplier.custom_declaration_incase_msme_not_applicable = (
			vendor_registration_doc.declaration_incase_msme_not_applicable
		)
		# supplier.custom_is_e_invoice_applicable = vendor_registration_doc.is_e_invoice_applicable
		supplier.custom_itr_filed_for_latest_financial_year = (
			vendor_registration_doc.itr_filed_for_latest_financial_year
		)
		supplier.custom_lower_tds_deduction_applicable = (
			vendor_registration_doc.lower_tds_deduction_applicable
		)
		supplier.custom_amount = vendor_registration_doc.amount
		supplier.custom_pan_applicable = vendor_registration_doc.pan_applicable
		supplier.custom_attach_gst_registration_ = vendor_registration_doc.attach_gst_registration
		supplier.custom_attach_pan = vendor_registration_doc.attach_pan
		supplier.custom_panaadhar_linking_doc = vendor_registration_doc.panaadhar_linking_doc
		supplier.custom_attach_tan = vendor_registration_doc.attach_tan
		supplier.custom_attach_itr_acknowledgement = vendor_registration_doc.attach_itr_acknowledgement
		supplier.custom_pe_certificate = vendor_registration_doc.pe_certificate
		supplier.custom_ldc_upload = vendor_registration_doc.ldc_upload
		supplier.custom_attach_msme_certificate = vendor_registration_doc.attach_msme_certificate
		supplier.custom_attach_certificate_of_incorporation = (
			vendor_registration_doc.attach_certificate_of_incorporation
		)
		supplier.custom_attach_memorandum_of_association = (
			vendor_registration_doc.attach_memorandum_of_association
		)
		supplier.custom_attach_last_3_years_annual_report = (
			vendor_registration_doc.attach_last_3_years_annual_report
		)
		supplier.custom_attach_article_of_association = (
			vendor_registration_doc.attach_article_of_association
		)
		supplier.custom_attach_iso_certificate_if_any = (
			vendor_registration_doc.attach_iso_certificate_if_any
		)
		supplier.custom_country_of_tax_residence = vendor_registration_doc.country_of_tax_residence
		supplier.custom_tax_identification_number_tin = (
			vendor_registration_doc.tax_identification_number_tin
		)
		supplier.custom_tax_residency_certificate_trc = (
			vendor_registration_doc.tax_residency_certificate_trc
		)
		supplier.custom_form_10f_generated_on_indian_income_tax_portal = (
			vendor_registration_doc.form_10f_generated_on_indian_income_tax_portal
		)
		supplier.custom_i_agree = vendor_registration_doc.i_agree
		supplier.custom_date_last = vendor_registration_doc.date_last
		supplier.save(ignore_permissions=True)
		return supplier
	except Exception as e:
		frappe.throw(_("Supplier cannot be created due to the following error <br>{0}").format(e))


def create_address(vendor_registration_doc, supplier):
	try:
		address = frappe.new_doc("Address")
		address.address_title = vendor_registration_doc.vendor_name
		address.address_type = "Billing"
		address.address_line1 = vendor_registration_doc.address_line_1
		address.address_line2 = vendor_registration_doc.address_line_2
		address.email_id = vendor_registration_doc.email_bt
		address.city = vendor_registration_doc.city
		address.state = vendor_registration_doc.state
		address.country = vendor_registration_doc.country
		address.pincode = vendor_registration_doc.pincodezip
		address.gstin = vendor_registration_doc.gst_no
		address.append(
			"links", {"link_doctype": "Supplier", "link_name": supplier, "link_title": supplier}
		)
		address.save(ignore_permissions=True)

		supplier.supplier_primary_address = address
		supplier.save(ignore_permissions=True)
		return address
	except Exception as e:
		frappe.throw(_("Address cannot be created due to the following error <br>{0}").format(e))


def create_contact(vendor_registration_doc, supplier):
	try:
		contact_bt, contact_at = "", ""
		if vendor_registration_doc.bt_name and (
			vendor_registration_doc.email_bt or vendor_registration_doc.bt_contact
		):
			contact_bt = frappe.new_doc("Contact")
			contact_bt.first_name = vendor_registration_doc.bt_name
			contact_bt.company_name = vendor_registration_doc.brand_nametrademark
			contact_bt.designation = vendor_registration_doc.designation
			contact_bt.custom_type = "Business Team"
			contact_bt.is_primary_contact = 1
			contact_bt.append("email_ids", {"email_id": vendor_registration_doc.email_bt, "is_primary": 1})
			contact_bt.append(
				"phone_nos",
				{
					"phone": vendor_registration_doc.bt_contact,
					"is_primary_phone": 1,
					"is_primary_mobile_no": 1,
				},
			)
			contact_bt.append(
				"links", {"link_doctype": "Supplier", "link_name": supplier, "link_title": supplier}
			)
			contact_bt.save(ignore_permissions=True)

			supplier.supplier_primary_contact = contact_bt
			supplier.save(ignore_permissions=True)

		if vendor_registration_doc.at_name and (
			vendor_registration_doc.email_at or vendor_registration_doc.at_contact
		):
			contact_at = frappe.new_doc("Contact")
			contact_at.first_name = vendor_registration_doc.at_name
			contact_at.company_name = vendor_registration_doc.brand_nametrademark
			contact_at.designation = vendor_registration_doc.at_designation
			contact_at.custom_type = "Account Team"
			contact_at.append("email_ids", {"email_id": vendor_registration_doc.email_at, "is_primary": 1})
			if vendor_registration_doc.at_contact:
				contact_at.append(
					"phone_nos",
					{
						"phone": vendor_registration_doc.at_contact,
						"is_primary_phone": 1,
						"is_primary_mobile_no": 0,
					},
				)
			contact_at.append(
				"links", {"link_doctype": "Supplier", "link_name": supplier, "link_title": supplier}
			)
			contact_at.save(ignore_permissions=True)

		contact = str(contact_bt) + (" and " if contact_at else " ") + str(contact_at)
		return contact
	except Exception as e:
		frappe.throw(_("Contact cannot be created due to the following error <br>{0}").format(e))


def create_bank_account(vendor_registration_doc):
	try:
		bank = frappe.new_doc("Bank Account")
		bank.account_name = vendor_registration_doc.vendor_name
		bank.bank = vendor_registration_doc.bank_name
		bank.company = "Kotak Education Foundation"
		bank.party_type = "Supplier"
		bank.party = vendor_registration_doc.vendor_name
		bank.account_type = vendor_registration_doc.account_type
		bank.bank_account_no = vendor_registration_doc.account_number
		bank.branch_code = vendor_registration_doc.branch_name
		bank.custom_branch_address = vendor_registration_doc.branch_address
		bank.custom_swift_code = vendor_registration_doc.swift_code
		bank.custom_ifsc_code = vendor_registration_doc.ifsc_code
		bank.custom_attach_cancelled_cheque = vendor_registration_doc.attach_cancelled_cheque
		bank.save(ignore_permissions=True)
		return bank
	except Exception as e:
		frappe.throw(_("Bank Account cannot be created due to the following error <br>{0}").format(e))