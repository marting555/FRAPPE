# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.integrations.utils import make_post_request
import json



class QueueSettings(Document):
	def on_update(self): 
		print(self.cars_per_day)
		if self.aws_url:
			url = f"{self.aws_url}/queue-settings/updated"
			make_post_request(
				url,
				headers={"Content-Type": "application/json"},
				data=json.dumps(self.as_dict(convert_dates_to_str=True)),
			)
	pass
