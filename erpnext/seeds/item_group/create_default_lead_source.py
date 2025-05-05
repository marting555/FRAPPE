import frappe

groups = [
    {
        "channel": "google",
        "page_id": "",
        "source_name": "GG - Mail CSKH"   
    },
    {
        "channel": "call-center",
        "page_id": "",
        "source_name": "Call Center StringX"   
    },
    {
        "channel": "google",
        "page_id": "",
        "source_name": "GG - Form Website Jemmia.vn"   
    },
    {
        "channel": "zalo",
        "page_id": "",
        "source_name": "ZNS - Jemmia Kiệt Hột Xoàn"   
    },
    {
        "channel": "zalo",
        "page_id": "",
        "source_name": "ZNS - Jemmia Anh Kim Cương"   
    },
    {
        "channel": "zalo",
        "page_id": "",
        "source_name": "ZNS - Jemmia Quý Tử Hột Xoàn"   
    },
    {
        "channel": "zalo",
        "page_id": "",
        "source_name": "ZNS - Jemmia Diamond"   
    },
    {
        "channel": "tiktok",
        "page_id": "",
        "source_name": "TT - Bà Cô GIA"   
    },
    {
        "channel": "tiktok",
        "page_id": "",
        "source_name": "TT - Quý Tử Hột Xoàn"   
    },
    {
        "channel": "facebook",
        "page_id": "",
        "source_name": "FB - Jemmia Diamond"   
    },
    {
        "channel": "facebook",
        "page_id": "",
        "source_name": "FB - Quý Tử Hột Xoàn"   
    },
    {
        "channel": "facebook",
        "page_id": "",
        "source_name": "FB - Anh Kim Cương"   
    },
    {
        "channel": "facebook",
        "page_id": "",
        "source_name": "FB - Kiệt Hột Xoàn"   
    },
    {
        "channel": "facebook",
        "page_id": "",
        "source_name": "FB - Jemmia Diamond - Hà Nội"   
    },
    {
        "channel": "facebook",
        "page_id": "",
        "source_name": "FB - Jemmia Love Jewelry"   
    },
    {
        "channel": "instagram",
        "page_id": "",
        "source_name": "IG - Jemmia Love Jewelry"   
    },
    {
        "channel": "instagram",
        "page_id": "",
        "source_name": "IG - Jemmia Diamond"   
    },
    {
        "channel": "tiktok",
        "page_id": "",
        "source_name": "TT - Jemmia Hột Xoàn"   
    },  
    {
        "channel": "tiktok",
        "page_id": "",
        "source_name": "TT - Anh Kim Cương"   
    },  
]

def execute():
    create_groups(groups)

def create_groups(groups_data):
    for data in groups_data:
        create_group(data)

def create_group(data):
    existing_name = frappe.db.get_value("Lead Source", {"source_name": data["source_name"]}, "name")
    if existing_name:
        print(f"{data['source_name']} exists")
        return frappe.get_doc("Lead Source", existing_name)

    doc_data = {
        "doctype": "Lead Source",
        "source_name": data["source_name"],
        "pancake_page_id": data["page_id"],
        "pancake_platform": data["channel"]
    }

    group = frappe.get_doc(doc_data)
    group.insert()
    group.reload()
    print(f"Created {group.get("name")} {group.get("source_name")}")
    return group
