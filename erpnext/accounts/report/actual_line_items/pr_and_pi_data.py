import frappe
from frappe.query_builder import CustomFunction
from pypika import Case

MONTHNAME = CustomFunction('MONTHNAME', ['date'])
date_func = CustomFunction("DATE", ["date_str"])
time_func = CustomFunction("TIME", ["time_str"])

def get_data_pr(wbs, filters):
    pri = frappe.qb.DocType("Purchase Receipt Item")
    pr = frappe.qb.DocType("Purchase Receipt")
    p = frappe.qb.DocType("Plant")
    wh = frappe.qb.DocType("Warehouse")
    poi = frappe.qb.DocType("Purchase Order Item")
    item_def = frappe.qb.DocType("Item Default")
    item_group = frappe.qb.DocType("Item Group")

    conditions_period_pr = []
    if filters.fiscal_year:
        fy = frappe.get_doc("Fiscal Year", filters.fiscal_year)
        conditions_period_pr.append(pr.posting_date.between(fy.year_start_date, fy.year_end_date))
        if filters.from_date and filters.to_date:
            conditions_period_pr.append(pr.posting_date.between(filters.from_date, filters.to_date))
        if not filters.from_date and not filters.to_date and filters.period:
            conditions_period_pr.append(MONTHNAME(pr.posting_date) == filters.period)
    if filters.voucher_type:
        conditions_period_pr.append(pri.parenttype == filters.voucher_type)
    if filters.voucher_name:
        conditions_period_pr.append(pr.name == filters.voucher_name)
    if filters.supplier:
        conditions_period_pr.append(pr.supplier.isin(filters.supplier) if len(filters.supplier) > 1 else pr.supplier == filters.supplier[0])
    if filters.ec_type:
        conditions_period_pr.append(pr.name == filters.ec_type)
    if filters.se_type:
        conditions_period_pr.append(pr.name == filters.se_type)
    if filters.item_code:
        conditions_period_pr.append(pri.item_code.isin(filters.item_code) if len(filters.item_code) > 1 else pri.item_code == filters.item_code[0])
    if filters.item_group:
        conditions_period_pr.append(pri.item_group.isin(filters.item_group) if len(filters.item_group) > 1 else pri.item_group == filters.item_group[0])
    if filters.purchase_order:
        conditions_period_pr.append(pri.purchase_order.isin(filters.purchase_order) if len(filters.purchase_order) > 1 else pri.purchase_order == filters.purchase_order[0])
    # if filters.cost_center:
    #     conditions_period_pr.append(pri.cost_center.isin(filters.cost_center) if len(filters.cost_center) > 1 else pri.cost_center == filters.cost_center[0])
    # if filters.plant:
    #     conditions_period_pr.append(pri.plant.isin(filters.plant) if len(filters.plant) > 1 else pri.plant == filters.plant[0])

    dr_cr_case = Case()
    dr_cr_case = dr_cr_case.when(pr.is_return == 0, 'Dr').else_('Cr')
    serv_item_subquery = (frappe.qb.from_(item_def).select(item_def.expense_account).where(item_def.parent == pri.item_code))

    query = (
        frappe.qb.from_(pri)
        .left_join(pr).on(pr.name == pri.parent)
        # .left_join(p).on(p.name == pri.plant)
        .left_join(wh).on(wh.name == pri.warehouse)
        .left_join(poi).on(poi.name == pri.purchase_order_item)
        .left_join(item_group).on(item_group.name == pri.item_group)
        .select(
            pri.work_breakdown_structure.as_("wbs"),
            pri.item_code,
            pri.item_group,
            pri.uom,
            date_func(pr.creation).as_("voucher_date"),
            # pr.supplier_delivery_note_date.as_("document_date"),
            pr.supplier_delivery_note.as_("bill_no"),
            pr.supplier,
            pr.supplier_name,
            # pr.posting_date,
            # pr.posting_time,
            # pr.modified,
            # pr.owner.as_("user_name"),
            # date_func(pr.custom_submit_date).as_("submit_date"),
            # time_func(pr.custom_submit_date).as_("submit_time"),
            # dr_cr_case.as_("dr_cr"),
            # pr.is_return,
            # pri.idx,
            # pri.wbs_name,
            # pri.uom,
            # pri.cost_center,
            # pri.cost_center_name,
            # pri.description,
            # pri.purchase_order,
            # pri.business_place,
            # poi.idx.as_("purchase_order_item_no"),
            # (Case()
            #     .when(pri.item_code.like('SERV%'), serv_item_subquery)
            #     .else_(item_group.custom_account)
            # ).as_("gl_acc"),
            # p.plant_code,
            # p.name1.as_("plant_name"),
            # pri.item_name.as_("item"),
            # (pri.qty - pri.custom_billed_qty).as_("qty"),
            # pri.net_rate.as_("rate"),
            # ((pri.qty - pri.custom_billed_qty) * pri.net_rate).as_("amount"),
            # pri.parenttype.as_("voucher_type"),
            # pri.parent.as_("voucher_name")
        )
        # .where(
        #     (pri.work_breakdown_structure == wbs) &
        #     (pr.docstatus == 1) &
        #     (~pri.item_code.like('SERV%'))
        # )
    )
    if conditions_period_pr:
        for cond in conditions_period_pr:
            query = query.where(cond)

    query = query.orderby(pr.name, pri.idx)
    pr_data = query.run(as_dict=True)

    return pr_data

def get_data_pi(wbs, filters):
    pri = frappe.qb.DocType("Purchase Invoice Item")
    pi = frappe.qb.DocType("Purchase Invoice")
    wbs_doc = frappe.qb.DocType("Work Breakdown Structure")
    # cc = frappe.qb.DocType("Cost Center")
    # p = frappe.qb.DocType("Plant")
    wh = frappe.qb.DocType("Warehouse")
    poi = frappe.qb.DocType("Purchase Order Item")
    item_def = frappe.qb.DocType("Item Default")
    item_group = frappe.qb.DocType("Item Group")

    conditions_period_pi = []
    # if filters.fiscal_year:
    #     fy = frappe.get_doc("Fiscal Year", filters.fiscal_year)
    #     conditions_period_pi.append(pi.posting_date.between(fy.year_start_date, fy.year_end_date))
    #     if filters.from_date and filters.to_date:
    #         conditions_period_pi.append(pi.posting_date.between(filters.from_date, filters.to_date))
    #     if not filters.from_date and not filters.to_date and filters.period:
    #         conditions_period_pi.append(MONTHNAME(pi.posting_date) == filters.period)
    # if filters.voucher_type:
    #     conditions_period_pi.append(pri.parenttype == filters.voucher_type)          
    # if filters.voucher_name:
    #     conditions_period_pi.append(pi.name == filters.voucher_name)
    # if filters.supplier:
    #     conditions_period_pi.append(pi.supplier.isin(filters.supplier) if len(filters.supplier) > 1 else pi.supplier == filters.supplier[0])
    # if filters.ec_type:
    #     conditions_period_pi.append(pi.name == filters.ec_type)
    # if filters.se_type:
    #     conditions_period_pi.append(pi.name == filters.se_type)
    # if filters.item_code:
    #     conditions_period_pi.append(pri.item_code.isin(filters.item_code) if len(filters.item_code) > 1 else pri.item_code == filters.item_code[0])
    # if filters.item_group:
    #     conditions_period_pi.append(pri.item_group.isin(filters.item_group) if len(filters.item_group) > 1 else pri.item_group == filters.item_group[0])
    # if filters.purchase_order:
    #     conditions_period_pi.append(pri.purchase_order.isin(filters.purchase_order) if len(filters.purchase_order) > 1 else pri.purchase_order == filters.purchase_order[0])
    # if filters.cost_center:
    #     conditions_period_pi.append(pri.cost_center.isin(filters.cost_center) if len(filters.cost_center) > 1 else pri.cost_center == filters.cost_center[0])
    # if filters.plant:
    #     conditions_period_pi.append(pri.plant.isin(filters.plant) if len(filters.plant) > 1 else pri.plant == filters.plant[0])

    dr_cr_case = Case()
    dr_cr_case = dr_cr_case.when(pi.is_return == 0, 'Dr').else_('Cr')
    serv_item_subquery = (frappe.qb.from_(item_def).select(item_def.expense_account).where(item_def.parent == pri.item_code))

    query = (
        frappe.qb.from_(pri)
        .left_join(pi).on(pi.name == pri.parent)
        .left_join(wbs_doc).on(wbs_doc.name == pri.work_breakdown_structure)
        # .left_join(cc).on(cc.name == pri.cost_center)
        # .left_join(p).on(p.name == pri.plant)
        .left_join(wh).on(wh.name == pri.warehouse)
        .left_join(poi).on(poi.name == pri.po_detail)
        .left_join(item_group).on(item_group.name == pri.item_group)
        .select(
            pri.work_breakdown_structure.as_("wbs"),
            pri.item_group,
            pri.uom,
            date_func(pi.creation).as_("voucher_date"),
            pi.bill_date.as_("document_date"),
            pri.idx,
            pi.bill_no,
            pi.posting_date,
            pi.posting_time,
            pi.supplier,
            pi.supplier_name,
            # pi.owner.as_("user_name"),
            # pi.modified,
            # dr_cr_case.as_("dr_cr"),
            # pi.is_return,
            # wbs_doc.wbs_name,
            # # pri.cost_center,
            # pri.description,
            # pri.business_place,
            # cc.cost_center_name,
            # pri.purchase_order,
            # poi.idx.as_("purchase_order_item_no"),
            # p.plant_code,
            # p.name1.as_("plant_name"),
            # date_func(pi.custom_submit_date).as_("submit_date"),
            # time_func(pi.custom_submit_date).as_("submit_time"),
            # pri.qty,
            # pri.item_code,
            # pri.item_name.as_("item"),
            # pri.net_rate.as_("rate"),
            # pri.net_amount.as_("amount"),
            # pri.parenttype.as_("voucher_type"),
            # pri.parent.as_("voucher_name"),
            # (Case()
            #     .when(pri.item_code.like('SERV%'), serv_item_subquery)
            #     .else_(item_group.custom_account)
            # ).as_("gl_acc"),
        )
        .where(
            (pri.work_breakdown_structure == wbs) &
            (pi.docstatus == 1)
        )
    )
    if conditions_period_pi:
        for cond in conditions_period_pi:
            query = query.where(cond)

    query = query.orderby(pi.name, pri.idx)
    pi_data = query.run(as_dict=True)

    return pi_data