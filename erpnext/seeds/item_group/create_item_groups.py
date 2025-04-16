import frappe

groups = [{
    "item_group_name": "Tất Cả Nhóm Sản Phẩm",
    "is_group": 1,
    "children": [
        {
            "item_group_name": "Trang Sức",
            "is_group": 1,
            "children": [
                {
                    "item_group_name": "Nhẫn",
                    "is_group": 1,
                    "children": [
                        {
                            "item_group_name": "Nhẫn Nam",
                            "is_group": 0,
                        },
                        {
                            "item_group_name": "Nhẫn Nam Nguyên Chiếc",
                            "is_group": 0,
                        },
                        {
                            "item_group_name": "Nhẫn Nữ",
                            "is_group": 0,
                        },
                        {
                            "item_group_name": "Nhẫn Nữ Nguyên Chiếc",
                            "is_group": 0,
                        },
                        {
                            "item_group_name": "Nhẫn Cưới",
                            "is_group": 0,
                        }
                    ]
                },
                {
                    "item_group_name": "Bông Tai",
                    "is_group": 0,
                },
                {
                    "item_group_name": "Bông Tai Nguyên Chiếc",
                    "is_group": 0,
                },
                {
                    "item_group_name": "Dây Chuyền",
                    "is_group": 1,
                    "children": [
                        {
                            "item_group_name": "Dây Chuyền Trơn",
                            "is_group": 0,
                        },
                        {
                            "item_group_name": "Dây Chuyền Charm",
                            "is_group": 0,
                        },
                        {
                            "item_group_name": "Dây Chuyền Nguyên Chiếc",
                            "is_group": 0,
                        },
                        {
                            "item_group_name": "Dây Chuyền Liền Mặt",
                            "is_group": 0,
                        }
                    ]
                }
            ]
        },
        {
            "item_group_name": "Kim Cương",
            "is_group": 1,
        },
    ]
}]

def execute():
    create_groups(groups)

def create_groups(groups_data, parent_group=None):
    for data in groups_data:
        group = create_group(data, parent_group)
        if "children" in data:
            create_groups(data["children"], group.name)

def create_group(data, parent_group=None):
    existing_name = frappe.db.get_value("Item Group", {"item_group_name": data["item_group_name"]}, "name")
    if existing_name:
        print(f"{data['item_group_name']} exists")
        return frappe.get_doc("Item Group", existing_name)

    doc_data = {
        "doctype": "Item Group",
        "item_group_name": data["item_group_name"],
        "is_group": data.get("is_group", 0),
    }
    if parent_group:
        doc_data["parent_item_group"] = parent_group

    group = frappe.get_doc(doc_data)
    group.insert()
    print(f"Created {data['item_group_name']}")
    return group
