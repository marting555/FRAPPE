import frappe
from frappe.query_builder import CustomFunction
from pypika import Case

MONTHNAME = CustomFunction('MONTHNAME', ['date'])
date_func = CustomFunction("DATE", ["date_str"])
time_func = CustomFunction("TIME", ["time_str"])

def get_data_ec(wbs, filters):
    ecd = frappe.qb.DocType("Expense Claim Detail")
    ec = frappe.qb.DocType("Expense Claim")
    wbs_table = frappe.qb.DocType("Work Breakdown Structure")
    cc = frappe.qb.DocType("Cost Center")
    p = frappe.qb.DocType("Plant")
    ect = frappe.qb.DocType("Expense Claim Type")
    eca = frappe.qb.DocType("Expense Claim Account")
    company = frappe.db.get_single_value("Global Defaults", "default_company")

    conditions_period_ec = []

    if filters.fiscal_year:
        fy = frappe.get_doc("Fiscal Year", filters.fiscal_year)
        conditions_period_ec.append(ec.posting_date.between(fy.year_start_date, fy.year_end_date))
        if filters.from_date and filters.to_date:
            conditions_period_ec.ppend(ec.posting_date.between(filters.from_date, filters.to_date))
        if not filters.from_date and not filters.to_date and filters.period:
            conditions_period_ec.append(MONTHNAME(ec.posting_date) == filters.period)
    if filters.voucher_type:
        conditions_period_ec.append(ecd.parenttype == filters.voucher_type)       
    if filters.voucher_name:
        conditions_period_ec.append(ec.name == filters.voucher_name)
    if filters.supplier:
        conditions_period_ec.append(ec.name.isin(tuple(filters.supplier)) if len(filters.supplier) > 1 else ec.name == filters.supplier[0])
    if filters.ec_type:
        conditions_period_ec.append(ecd.expense_type == filters.ec_type)
    if filters.se_type:
        conditions_period_ec.append(ec.name == filters.se_type)
    if filters.item_code:
        conditions_period_ec.append(ecd.expense_type.isin(tuple(filters.item_code)) if len(filters.item_code) > 1 else ecd.expense_type == filters.item_code[0])
    if filters.item_group:
        conditions_period_ec.append(ecd.expense_type.isin(filters.item_group) if len(filters.item_group) > 1 else ecd.expense_type == filters.item_group[0])
    if filters.purchase_order:
        conditions_period_ec.append(ecd.expense_type.isin(filters.purchase_order) if len(filters.purchase_order) > 1 else ecd.expense_type == filters.purchase_order[0])
    if filters.cost_center:
        conditions_period_ec.append(ecd.cost_center.isin(filters.cost_center) if len(filters.cost_center) > 1 else ecd.cost_center == filters.cost_center[0])
    if filters.plant:
        conditions_period_ec.append(ecd.plant.isin(filters.plant) if len(filters.plant) > 1 else ecd.plant == filters.plant[0])
        
    dr_cr_case = Case()
    dr_cr_case = dr_cr_case.when((ec.name != None), 'Dr').else_('Dr')

    gl_acc_case = Case()
    gl_acc_case = gl_acc_case.when(eca.company == filters.get('company'), eca.default_account).else_('')

    qty = Case()
    qty = qty.when(ecd.sanctioned_amount != None, ecd.sanctioned_amount).else_(0.0)

    query = (
        frappe.qb.from_(ecd)
        .left_join(ec).on(ec.name == ecd.parent)
        .left_join(wbs_table).on(wbs_table.name == ecd.work_breakdown_structure)
        .left_join(cc).on(cc.name == ecd.cost_center)
        .left_join(p).on(p.name == ecd.plant)
        .left_join(ect).on(ect.name == ecd.expense_type)
        .left_join(eca).on(eca.parent == ect.name)
        .select(
            ecd.work_breakdown_structure.as_("wbs"),
            date_func(ecd.expense_date).as_("voucher_date"),
            date_func(ecd.expense_date).as_("document_date"),
            ec.modified,
            dr_cr_case.as_("dr_cr"),
            ecd.idx,
            ec.posting_date,
            ec.custom_posting_time.as_("posting_time"),
            ec.owner.as_("user_name"),
            wbs_table.wbs_name,
            ecd.cost_center,
            ecd.description,
            ecd.business_place,
            ecd.expense_type,
            ec.employee,
            date_func(ec.custom_submit_date).as_("submit_date"),
            time_func(ec.custom_submit_date).as_("submit_time"),
            (
                Case()
                .when(eca.company == company, eca.default_account)
                .else_('')
            ).as_("gl_acc"),
            qty.as_("qty"),
            cc.cost_center_name,
            p.plant_code,
            p.name1.as_("plant_name"),
            ecd.sanctioned_amount.as_("amount"),
            ecd.parenttype.as_("voucher_type"),
            ecd.parent.as_("voucher_name")
        )
        .where(
            (ecd.work_breakdown_structure == wbs) &
            (ec.docstatus == 1)
        )
    )
    if conditions_period_ec:
        for cond in conditions_period_ec:
            query = query.where(cond)

    query = query.orderby(ec.name, ecd.idx)
    ec_data = query.run(as_dict=True)

    return ec_data

def get_data_je(wbs, filters):
    jea = frappe.qb.DocType("Journal Entry Account")
    je = frappe.qb.DocType("Journal Entry")
    wbs_table = frappe.qb.DocType("Work Breakdown Structure")
    cc = frappe.qb.DocType("Cost Center")
    p = frappe.qb.DocType("Plant")

    conditions_period_je = []

    if filters.fiscal_year:
        fy = frappe.get_doc("Fiscal Year", filters.fiscal_year)
        conditions_period_je.append(je.posting_date.between(fy.year_start_date, fy.year_end_date))
        if filters.from_date and filters.to_date:
            conditions_period_je.append(je.posting_date.between(filters.from_date, filters.to_date))
        if not filters.from_date and not filters.to_date and filters.period:
            conditions_period_je.append(MONTHNAME(je.posting_date) == filters.period)
    if filters.voucher_type:
        conditions_period_je.append(jea.parenttype == filters.voucher_type)     
    if filters.voucher_name:
        conditions_period_je.append(je.name == filters.voucher_name)
    if filters.supplier:
        conditions_period_je.append(je.name.isin(tuple(filters.supplier)) if len(filters.supplier) > 1 else je.name == filters.supplier[0])
    if filters.ec_type:
        conditions_period_je.append(je.name == filters.ec_type)
    if filters.se_type:
        conditions_period_je.append(je.name == filters.ec_type)
    if filters.item_code:
        conditions_period_je.append(jea.parenttype.isin(filters.item_code) if len(filters.item_code) > 1 else jea.parenttype == filters.item_code[0])
    if filters.item_group:
        conditions_period_je.append(jea.item_group.isin(filters.item_group) if len(filters.item_group) > 1 else jea.item_group == filters.item_group[0])
    if filters.purchase_order:
        conditions_period_je.append(jea.parenttype.isin(filters.purchase_order) if len(filters.purchase_order) > 1 else jea.parenttype == filters.purchase_order[0])
    if filters.cost_center:
        conditions_period_je.append(jea.cost_center.isin(filters.cost_center)if len(filters.cost_center) > 1 else jea.cost_center == filters.cost_center[0])
    if filters.plant:
        conditions_period_je.append(jea.plant.isin(filters.plant) if len(filters.plant) > 1 else jea.plant == filters.plant[0])

    dr_cr_case = Case()
    dr_cr_case = dr_cr_case.when(je.reversal_of.isnull(), 'Dr').when((je.reversal_of.isnotnull()), 'Cr').else_('Dr')

    qty_case = Case()
    qty_case = qty_case.when((jea.account.isnotnull()), 0).else_(0)

    amount_case = Case()
    amount_case = amount_case.when((jea.debit_in_account_currency.isnotnull()), jea.debit_in_account_currency)
    amount_case = amount_case.when(jea.credit_in_account_currency != 0.0, jea.credit_in_account_currency)
    amount_case = amount_case.else_(0.0)

    query = (
        frappe.qb.from_(jea)
        .left_join(je).on(je.name == jea.parent)
        .left_join(wbs_table).on(wbs_table.name == jea.work_breakdown_structure)
        .left_join(cc).on(cc.name == jea.cost_center)
        .left_join(p).on(p.name == jea.custom_plant)
        .select(
            jea.work_breakdown_structure.as_("wbs"),
            date_func(je.creation).as_("voucher_date"),
            je.cheque_date.as_("document_date"),
            jea.idx,
            je.cheque_no.as_("bill_no"),
            je.posting_date,
            je.custom_posting_time.as_("posting_time"),
            je.modified,
            dr_cr_case.as_("dr_cr"),
            je.owner.as_("user_name"),
            wbs_table.wbs_name,
            jea.cost_center,
            jea.custom_business_place,
            jea.account.as_("gl_acc"),
            cc.cost_center_name,
            # p.plant_code,
            # p.name1.as_("plant_name"),
            date_func(je.custom_submit_date).as_("submit_date"),
            time_func(je.custom_submit_date).as_("submit_time"),
            qty_case.as_("qty"),
            amount_case.as_("amount"),
            jea.parenttype.as_("voucher_type"),
            jea.parent.as_("voucher_name")
        )
        .where(
            (jea.work_breakdown_structure == wbs) &
            (jea.debit_in_account_currency != 0.0) &
            (je.docstatus == 1)
        )
    )

    if conditions_period_je:
        for cond in conditions_period_je:
            query = query.where(cond)

    query = query.orderby(je.name, jea.idx)

    je_data = query.run(as_dict=True)

    return je_data