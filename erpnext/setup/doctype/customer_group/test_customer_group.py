# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

test_ignore = ["Price List"]


import frappe
import unittest

test_records = frappe.get_test_records("Customer Group")

class TestCustomerGroup(unittest.TestCase):
    def setUp(self):
        self.customer_group_name = "Test Customer Group 5"
        self.customer_group = frappe.get_doc({
            "doctype": "Customer Group",
            "customer_group_name": self.customer_group_name,
            "is_group": 0
        })
        self.customer_group.insert()

    def test_customer_group_creation(self):
        self.assertEqual(self.customer_group.customer_group_name, self.customer_group_name, "Customer Group name does not match.")
        self.assertFalse(self.customer_group.is_group, "Customer Group should not be a group.")

    def tearDown(self):
        frappe.delete_doc("Customer Group", self.customer_group.name)