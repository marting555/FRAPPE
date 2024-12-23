import frappe
from frappe import _


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
		supplier.tax_category = vendor_registration_doc.tax_category
		supplier.custom_gst_registered = vendor_registration_doc.gst_registered
		supplier.custom_gst_no = vendor_registration_doc.gst_no
		supplier.custom_gst_registration_category = vendor_registration_doc.gst_registration_category
		supplier.tax_withholding_category = vendor_registration_doc.tax_withholding_category
		supplier.custom_are_you_registered_as_msme = vendor_registration_doc.are_you_registered_as_msme
		supplier.custom_msme_certificate_no = vendor_registration_doc.msme_certificate_no
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
		address.custom_gst_no = vendor_registration_doc.gst_no
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
