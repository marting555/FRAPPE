# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
import frappe
import unittest
from erpnext.manufacturing.doctype.manufacturing_settings.manufacturing_settings import ManufacturingSettings
from erpnext.stock.doctype.warehouse.test_warehouse import create_warehouse

class TestManufacturingSettings(unittest.TestCase):

