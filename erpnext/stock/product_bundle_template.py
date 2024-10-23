from re import sub
import frappe

class ProductBundleTemplate:
    def __init__(self):
        self.item_code = None

    def set_item_code(self, item_code):
        if not item_code or item_code.strip() == "":
            raise ValueError("Item code cannot be empty.")
        self.item_code = item_code
        return self

    def validate(self):
        if not self.item_code or self.item_code == "":
            raise ValueError("Item code must be set.")
        return self
    
    def searchProductBundle(self):
        try:
            item_details = frappe.get_doc("Product Bundle", self.item_code)
        except frappe.DoesNotExistError:
            raise ValueError(f"Item with code {self.item_code} does not exist.")
        except Exception as e:
            raise RuntimeError(f"Error fetching item details: {e}")

        if not item_details or not hasattr(item_details, 'name'):
            return None

        subitems_list = getattr(item_details, 'items', [])
        if not isinstance(subitems_list, list):
            raise TypeError("Items list is not a valid list.")

        return {
            "item_code": item_details.name,
            "description": item_details.description,
            "subitems_list": self.get_sub_items(subitems_list)
        }

    def get_item_price(self, item_details):
        try:
            price_list_rate = frappe.db.get_value("Item Price", {"item_code": item_details.item_code}, "price_list_rate")
            if price_list_rate is None:
               price_list_rate = 0
        except Exception as e:
            raise RuntimeError(f"Error fetching item price: {e}")

        return price_list_rate
    
    def get_sub_items(self, subitems_list):
        array_subitems = []
        
        if not subitems_list or not isinstance(subitems_list, list):
            raise ValueError("Subitems list is either empty or invalid.")

        for item in subitems_list:
            if isinstance(item, dict):
                item_code = item.get("item_code")
                description = item.get("description", "No description available")
                description_visible = item.get("description_visible", "No UOM specified")
                qty = item.get("qty", 0)
            else:
                item_code = getattr(item, "item_code", None)
                description = getattr(item, "description", "No description available")
                description_visible = getattr(item, "description_visible", "No UOM specified")
                qty = getattr(item, "qty", 0)

            if not item_code:
                raise ValueError("Subitem missing item_code.")

            array_subitems.append({
                "item_code": item_code,
                "description": description,
                "description_visible": description_visible,
                "qty": qty,
                "price": self.get_item_price(item),
                "sub_items": self.get_product_bundle_sub_items(item_code)
            })
            
        return array_subitems
    
    def get_product_bundle_sub_items(self, item_code):
        try:
            item = frappe.get_doc("Item", item_code)
            items = item.get("subitems_list")
            if(not items or not isinstance(items, list)):
                return []
            sub_items = []
            for item in items:
                sub_items.append({
                    "item_code": item.item_code,
                    "description": item.item_code,
                    "stock_uom": item.get("stock_uom", ""),
                    "stock_uom_qty": item.get("qty_unit_measure", 0),
                    "price": self.get_item_price(item),
                    "options": item.get("options"),
                    "qty": item.get("qty", 0),
                    "tvs_pn": item.get("tvs_pn"),
                    "rate": item.get("rate")
                })
            return sub_items
        except Exception as e:
            raise RuntimeError(f"Error fetching subitems: {e}")