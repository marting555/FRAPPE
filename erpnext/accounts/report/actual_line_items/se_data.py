import frappe
from pypika import Case
from frappe.query_builder import CustomFunction

MONTHNAME = CustomFunction('MONTHNAME', ['date'])
date_func = CustomFunction("DATE", ["date_str"])
time_func = CustomFunction("TIME", ["time_str"])

def get_conditions_for_se(filters):
    conditions_period_se = []
    sed = frappe.qb.DocType("Stock Entry Detail")
    se = frappe.qb.DocType("Stock Entry")

    if filters.fiscal_year:
        fy = frappe.get_doc("Fiscal Year", filters.fiscal_year)
        conditions_period_se.append(se.posting_date.between(fy.year_start_date, fy.year_end_date))
        if filters.from_date and filters.to_date:
            conditions_period_se.append(se.posting_date.between(filters.from_date, filters.to_date))
        if not filters.from_date and not filters.to_date and filters.period:
            conditions_period_se.append(MONTHNAME(se.posting_date) == filters.period)
    if filters.voucher_type:
        conditions_period_se.append(sed.parenttype == filters.voucher_type)     
    if filters.voucher_name:
        conditions_period_se.append(se.name == filters.voucher_name)
    if filters.supplier:
        conditions_period_se.append(se.supplier.isin(filters.supplier) if len(filters.supplier) > 1 else se.supplier == filters.supplier[0])
    if filters.ec_type:
        conditions_period_se.append(se.name == filters.ec_type)
    if filters.se_type:
        conditions_period_se.append(se.stock_entry_type == filters.se_type)
    if filters.item_code:
        conditions_period_se.append(sed.item_code.isin(filters.item_code) if len(filters.item_code) > 1 else sed.item_code == filters.item_code[0])
    if filters.item_group:
        conditions_period_se.append(sed.item_group.isin(filters.item_group) if len(filters.item_group) > 1 else sed.item_group == filters.item_group[0])
    if filters.purchase_order:
        conditions_period_se.append(se.stock_entry_type.isin(filters.purchase_order) if len(filters.purchase_order) > 1 else se.stock_entry_type == filters.purchase_order[0])
    if filters.cost_center:
        conditions_period_se.append(sed.cost_center.isin(filters.cost_center) if len(filters.cost_center) > 1 else sed.cost_center == filters.cost_center[0])
    if filters.plant:
        conditions_period_se.append(sed.plant.isin(filters.plant) if len(filters.plant) > 1 else sed.plant == filters.plant[0])

    return conditions_period_se

def get_data_se(wbs, filters):
    conditions_period_se = get_conditions_for_se(filters)
    item_group = frappe.qb.DocType("Item Group")
    item_def = frappe.qb.DocType("Item Default")
    sed = frappe.qb.DocType("Stock Entry Detail")
    se = frappe.qb.DocType("Stock Entry")
    wbs_table = frappe.qb.DocType("Work Breakdown Structure")
    cc = frappe.qb.DocType("Cost Center")
    p = frappe.qb.DocType("Plant")
    warehouse = frappe.qb.DocType("Warehouse")

    serv_item_subquery = (frappe.qb.from_(item_def).select(item_def.expense_account).where(item_def.parent == sed.item_code))
    account_subquery = (frappe.qb.from_(item_group).select(item_group.custom_account).where(item_group.name == sed.item_group))

    query = (
        frappe.qb.from_(sed)
        .left_join(se).on(se.name == sed.parent)
        .left_join(wbs_table).on(wbs_table.name == sed.work_breakdown_structure)
        .left_join(cc).on(cc.name == sed.cost_center)
        .left_join(p).on(p.name == sed.plant)
        .select(
            sed.work_breakdown_structure.as_("wbs"),
            sed.item_group,
            sed.uom,
            date_func(se.creation).as_("voucher_date"),
            se.custom_document_date.as_("document_date"),
            sed.idx,
            se.custom_material_slip_no.as_("bill_no"),
            se.posting_date,
            se.posting_time,
            se.supplier,
            se.supplier_name,
            se.modified,
            (
                Case()
                .when((se.stock_entry_type == 'Repack For WBS to WBS') & (sed.s_warehouse.isnotnull()), 'Cr')
                .when((se.stock_entry_type == 'Repack For WBS to WBS') & (sed.t_warehouse.isnotnull()), 'Dr')
                .when((se.stock_entry_type == 'Repack For Store Location') & (sed.s_warehouse.isnotnull()), 'Dr')
                .when((se.stock_entry_type == 'Repack For Store Location') & (sed.t_warehouse.isnotnull()), 'Cr')
                .when((se.stock_entry_type == 'Repack For WBS to Common') & (sed.s_warehouse.isnotnull()), 'Cr')
                .when((se.stock_entry_type == 'Repack For Common to WBS') & (sed.t_warehouse.isnotnull()), 'Dr')
                .when((se.stock_entry_type.isin(['Material Consumption', 'Consumption For WBS to WBS'])) & (sed.t_warehouse.isnull()), 'Cr')
                .else_('Dr')
            ).as_("dr_cr"),
            se.is_return,
            se.stock_entry_type,
            se.owner.as_("user_name"),
            wbs_table.wbs_name,
            sed.cost_center,
            sed.uom,
            sed.business_place,
            (
                Case()
                .when(((sed.s_warehouse.isnotnull()) | (sed.t_warehouse.isnotnull())) & sed.item_code.like('SERV%'), serv_item_subquery)
                .when((sed.s_warehouse.isnotnull()) | (sed.t_warehouse.isnotnull()), account_subquery)
                .else_('')
            ).as_("gl_acc"),
            sed.description,
            cc.cost_center_name,
            p.plant_code,
            p.name1.as_("plant_name"),
            date_func(se.custom_submit_date).as_("submit_date"),
            time_func(se.custom_submit_date).as_("submit_time"),
            sed.amount,
            sed.qty,
            sed.item_code,
            sed.item_name.as_("item"),
            sed.basic_rate.as_("rate"),
            sed.parenttype.as_("voucher_type"),
            sed.parent.as_("voucher_name")
        )
        .where(
            (sed.work_breakdown_structure == wbs) & 
            (se.docstatus == 1)
        )
    )
    if conditions_period_se:
        for cond in conditions_period_se:
            query = query.where(cond)

    query = query.orderby(se.name, sed.idx)

    se_data = query.run(as_dict=True)

    return se_data

def get_data_se_mc(wbs,filters):
    conditions_period_se = get_conditions_for_se(filters)
    item_def = frappe.qb.DocType("Item Default")
    sed = frappe.qb.DocType("Stock Entry Detail")
    se = frappe.qb.DocType("Stock Entry")
    wbs_table = frappe.qb.DocType("Work Breakdown Structure")
    cc = frappe.qb.DocType("Cost Center")
    p = frappe.qb.DocType("Plant")
    warehouse = frappe.qb.DocType("Warehouse")

    query = (
        frappe.qb.from_(sed)
        .left_join(se).on(se.name == sed.parent)
        .left_join(wbs_table).on(wbs_table.name == sed.work_breakdown_structure)
        .left_join(cc).on(cc.name == sed.cost_center)
        .left_join(p).on(p.name == sed.plant)
        .select(
            sed.work_breakdown_structure.as_("wbs"),
            sed.item_group,
            sed.uom,
            date_func(se.creation).as_("voucher_date"),
            se.custom_document_date.as_("document_date"),
            sed.idx,
            se.custom_material_slip_no.as_("bill_no"),
            se.posting_date,
            se.posting_time,
            se.supplier,
            se.supplier_name,
            se.modified,
            (
                Case()
                .when((se.stock_entry_type.isin(['Material Consumption', 'Consumption For WBS to WBS'])) & (sed.t_warehouse.isnull()), 'Dr')
                .else_('Cr')
            ).as_("dr_cr"),
            se.is_return,
            se.stock_entry_type,
            se.owner.as_("user_name"),
            wbs_table.wbs_name,
            sed.cost_center,
            sed.uom,
            sed.business_place,
            sed.expense_account.as_("gl_acc"),
            sed.description,
            cc.cost_center_name,
            p.plant_code,
            p.name1.as_("plant_name"),
            date_func(se.custom_submit_date).as_("submit_date"),
            time_func(se.custom_submit_date).as_("submit_time"),
            sed.amount,
            sed.qty,
            sed.item_code,
            sed.item_name.as_("item"),
            sed.basic_rate.as_("rate"),
            sed.parenttype.as_("voucher_type"),
            sed.parent.as_("voucher_name")
        )
        .where(
            (sed.work_breakdown_structure == wbs) & 
            (se.stock_entry_type.isin(['Material Consumption', 'Consumption For WBS to WBS'])) & 
            (se.docstatus == 1)
        )
    )

    if conditions_period_se:
        for cond in conditions_period_se:
            query = query.where(cond)

    query = query.orderby(se.name, sed.idx)

    se_data_mc = query.run(as_dict=True)

    return se_data_mc