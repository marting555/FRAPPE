import frappe

from erpnext.deprecation_dumpster import deprecated


def get_leaderboards():
	leaderboards = {
		"Customer": {
			"fields": [
				{"fieldname": "total_sales_amount", "fieldtype": "Currency"},
				"total_qty_sold",
				{"fieldname": "outstanding_amount", "fieldtype": "Currency"},
			],
			"method": "erpnext.startup.leaderboard.get_all_customers",
			"icon": "customer",
		},
		"Item": {
			"fields": [
				{"fieldname": "total_sales_amount", "fieldtype": "Currency"},
				"total_qty_sold",
				{"fieldname": "total_purchase_amount", "fieldtype": "Currency"},
				"total_qty_purchased",
				"available_stock_qty",
				{"fieldname": "available_stock_value", "fieldtype": "Currency"},
			],
			"method": "erpnext.startup.leaderboard.get_all_items",
			"icon": "stock",
		},
		"Supplier": {
			"fields": [
				{"fieldname": "total_purchase_amount", "fieldtype": "Currency"},
				"total_qty_purchased",
				{"fieldname": "outstanding_amount", "fieldtype": "Currency"},
			],
			"method": "erpnext.startup.leaderboard.get_all_suppliers",
			"icon": "buying",
		},
		"Sales Partner": {
			"fields": [
				{"fieldname": "total_sales_amount", "fieldtype": "Currency"},
				{"fieldname": "total_commission", "fieldtype": "Currency"},
			],
			"method": "erpnext.startup.leaderboard.get_all_sales_partner",
			"icon": "hr",
		},
		"Sales Person": {
			"fields": [{"fieldname": "total_sales_amount", "fieldtype": "Currency"}],
			"method": "erpnext.startup.leaderboard.get_all_sales_person",
			"icon": "customer",
		},
	}

	return leaderboards


@frappe.whitelist()
def get_all_customers(date_range, company, field, limit=None):
	filters = [["docstatus", "=", "1"], ["company", "=", company]]
	from_date, to_date = parse_date_range(date_range)
	if field == "outstanding_amount":
		if from_date and to_date:
			filters.append(["posting_date", "between", [from_date, to_date]])

		return frappe.get_list(
			"Sales Invoice",
			fields=["customer as name", "sum(outstanding_amount) as value"],
			filters=filters,
			group_by="customer",
			order_by="value desc",
			limit=limit,
		)
	else:
		if field == "total_sales_amount":
			select_field = "base_net_total"
		elif field == "total_qty_sold":
			select_field = "total_qty"

		if from_date and to_date:
			filters.append(["transaction_date", "between", [from_date, to_date]])

		return frappe.get_list(
			"Sales Order",
			fields=["customer as name", f"sum({select_field}) as value"],
			filters=filters,
			group_by="customer",
			order_by="value desc",
			limit=limit,
		)


@frappe.whitelist()
def get_all_items(date_range, company, field, limit=None):
    if limit is not None:
        limit = int(limit)  
        
    if field in ("available_stock_qty", "available_stock_value"):
        # Fetch initial quantity and total quantity sold
        item_details = frappe.db.get_all(
            "Item",
            fields=["name", "valuation_rate as price"],
            filters={"disabled": 0},
        )

        # Fetch total quantity sold for each item
        filters = [["docstatus", "=", "1"], ["company", "=", company]]
        from_date, to_date = parse_date_range(date_range)
        if from_date and to_date:
            filters.append(["posting_date", "between", [from_date, to_date]])

        # Query Sales Invoice
        sales_invoice_items = frappe.get_list(
            "Sales Invoice",
            fields=[
                "`tabSales Invoice Item`.item_code as name",
                "sum(`tabSales Invoice Item`.stock_qty) as total_qty_sold",
            ],
            filters=filters,
            group_by="`tabSales Invoice Item`.item_code",
        )

        # Query POS Invoice
        pos_invoice_items = frappe.get_list(
            "POS Invoice",
            fields=[
                "`tabPOS Invoice Item`.item_code as name",
                "sum(`tabPOS Invoice Item`.stock_qty) as total_qty_sold",
            ],
            filters=filters,
            group_by="`tabPOS Invoice Item`.item_code",
        )

        # Combine results
        from collections import defaultdict
        total_qty_sold = defaultdict(float)
        for item in sales_invoice_items + pos_invoice_items:
            total_qty_sold[item["name"]] += item["total_qty_sold"]

        # Fetch initial quantity from Bin
        bin_data = frappe.db.get_all(
            "Bin",
            fields=["item_code", "sum(actual_qty) as initial_qty"],
            group_by="item_code",
        )
        initial_qty = {item["item_code"]: item["initial_qty"] for item in bin_data}

        # Calculate available stock qty and value
        results = []
        for item in item_details:
            item_code = item["name"]
            initial = initial_qty.get(item_code, 0)
            sold = total_qty_sold.get(item_code, 0)
            available_qty = initial - sold

            if field == "available_stock_qty":
                results.append({"name": item_code, "value": available_qty})
            elif field == "available_stock_value":
                price = item["price"]
                results.append({"name": item_code, "value": available_qty * price})

        # Sort and limit results
        results.sort(key=lambda x: x["value"], reverse=True)
        if limit:
            results = results[:limit]

        return results

    else:
        # Existing logic for other fields
        if field == "total_sales_amount":
            select_field = "base_net_amount"
        elif field == "total_purchase_amount":
            select_field = "base_net_amount"
        elif field == "total_qty_sold":
            select_field = "stock_qty"
        elif field == "total_qty_purchased":
            select_field = "stock_qty"

        filters = [["docstatus", "=", "1"], ["company", "=", company]]
        from_date, to_date = parse_date_range(date_range)
        if from_date and to_date:
            filters.append(["posting_date", "between", [from_date, to_date]])

        # Query Sales Invoice
        sales_invoice_items = frappe.get_list(
            "Sales Invoice",
            fields=[
                "`tabSales Invoice Item`.item_code as name",
                f"sum(`tabSales Invoice Item`.{select_field}) as value",
            ],
            filters=filters,
            order_by="value desc",
            group_by="`tabSales Invoice Item`.item_code",
            limit=limit,
        )

        # Query POS Invoice
        pos_invoice_items = frappe.get_list(
            "POS Invoice",
            fields=[
                "`tabPOS Invoice Item`.item_code as name",
                f"sum(`tabPOS Invoice Item`.{select_field}) as value",
            ],
            filters=filters,
            order_by="value desc",
            group_by="`tabPOS Invoice Item`.item_code",
            limit=limit,
        )

        # Combine results
        from collections import defaultdict
        aggregated_items = defaultdict(float)
        for item in sales_invoice_items + pos_invoice_items:
            aggregated_items[item["name"]] += item["value"]

        # Convert to list of dictionaries
        result = [{"name": k, "value": v} for k, v in aggregated_items.items()]

        # Sort by value in descending order
        result.sort(key=lambda x: x["value"], reverse=True)

        # Apply limit
        if limit:
            result = result[:limit]

        return result

@frappe.whitelist()
def get_all_suppliers(date_range, company, field, limit=None):
	filters = [["docstatus", "=", "1"], ["company", "=", company]]
	from_date, to_date = parse_date_range(date_range)

	if field == "outstanding_amount":
		if from_date and to_date:
			filters.append(["posting_date", "between", [from_date, to_date]])

		return frappe.get_list(
			"Purchase Invoice",
			fields=["supplier as name", "sum(outstanding_amount) as value"],
			filters=filters,
			group_by="supplier",
			order_by="value desc",
			limit=limit,
		)
	else:
		if field == "total_purchase_amount":
			select_field = "base_net_total"
		elif field == "total_qty_purchased":
			select_field = "total_qty"

		if from_date and to_date:
			filters.append(["transaction_date", "between", [from_date, to_date]])

		return frappe.get_list(
			"Purchase Order",
			fields=["supplier as name", f"sum({select_field}) as value"],
			filters=filters,
			group_by="supplier",
			order_by="value desc",
			limit=limit,
		)


@frappe.whitelist()
def get_all_sales_partner(date_range, company, field, limit=None):
	if field == "total_sales_amount":
		select_field = "base_net_total"
	elif field == "total_commission":
		select_field = "total_commission"

	filters = [["docstatus", "=", "1"], ["company", "=", company], ["sales_partner", "is", "set"]]
	from_date, to_date = parse_date_range(date_range)
	if from_date and to_date:
		filters.append(["transaction_date", "between", [from_date, to_date]])

	return frappe.get_list(
		"Sales Order",
		fields=[
			"sales_partner as name",
			f"sum({select_field}) as value",
		],
		filters=filters,
		group_by="sales_partner",
		order_by="value DESC",
		limit=limit,
	)


@frappe.whitelist()
def get_all_sales_person(date_range, company, field=None, limit=0):
	filters = [
		["docstatus", "=", "1"],
		["company", "=", company],
		["Sales Team", "sales_person", "is", "set"],
	]
	from_date, to_date = parse_date_range(date_range)
	if from_date and to_date:
		filters.append(["transaction_date", "between", [from_date, to_date]])

	return frappe.get_list(
		"Sales Order",
		fields=[
			"`tabSales Team`.sales_person as name",
			"sum(`tabSales Team`.allocated_amount) as value",
		],
		filters=filters,
		group_by="`tabSales Team`.sales_person",
		order_by="value desc",
		limit=limit,
	)


@deprecated(f"{__name__}.get_date_condition", "unknown", "v16", "No known instructions.")
def get_date_condition(date_range, field):
	date_condition = ""
	if date_range:
		date_range = frappe.parse_json(date_range)
		from_date, to_date = date_range
		date_condition = f"and {field} between {frappe.db.escape(from_date)} and {frappe.db.escape(to_date)}"
	return date_condition


def parse_date_range(date_range):
	if date_range:
		date_range = frappe.parse_json(date_range)
		return date_range[0], date_range[1]

	return None, None
