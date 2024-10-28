import frappe
import unittest

test_records = frappe.get_test_records("Customer Group")

class TestCustomerGroup(unittest.TestCase):
    def setUp(self):
        self.customer_group_name = "_Test Customer Group"

        # Check if Customer Group already exists
        if not frappe.db.exists("Customer Group", self.customer_group_name):
            # Create new Customer Group if it doesn't exist
            self.customer_group = frappe.get_doc({
                "doctype": "Customer Group",
                "customer_group_name": self.customer_group_name,
                "is_group": 0
            })
            self.customer_group.insert()
        else:
            # Fetch the existing Customer Group if it exists
            self.customer_group = frappe.get_doc("Customer Group", self.customer_group_name)

    def test_customer_group_creation(self):
        self.assertEqual(self.customer_group.customer_group_name, self.customer_group_name, "Customer Group name does not match.")
        self.assertFalse(self.customer_group.is_group, "Customer Group should not be a group.")

    def tearDown(self):
        frappe.delete_doc("Customer Group", self.customer_group.name)