import frappe


def execute():
	update_delivery_note()
	update_pick_list_items()


def update_delivery_note():
	delivery_notes = frappe.get_all(
		"Delivery Note",
		fields=["name", "pick_list"],
		filters={"pick_list": ("is", "set")},
	)

	for delivery_note in delivery_notes:
		frappe.db.set_value(
			"Delivery Note Item",
			{"parent": delivery_note.name},
			"against_pick_list",
			delivery_note.pick_list,
		)


def update_pick_list_items():
	PICK_LIST = frappe.qb.DocType("Pick List")
	PICK_LIST_ITEM = frappe.qb.DocType("Pick List Item")

	pick_lists = (
		frappe.qb.from_(PICK_LIST)
		.select(PICK_LIST.name)
		.where(PICK_LIST.status == "Completed")
		.run(pluck="name")
	)

	if not pick_lists:
		return

	frappe.qb.update(PICK_LIST_ITEM).set(PICK_LIST_ITEM.delivered_qty, PICK_LIST_ITEM.picked_qty).where(
		PICK_LIST_ITEM.parent.isin(pick_lists)
	).run()
