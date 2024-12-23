# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

from erpnext.buying.doc_events.utility_functions import (
	create_vendor_entry,
)

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
