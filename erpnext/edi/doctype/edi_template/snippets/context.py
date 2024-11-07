import frappe
from frappe.model import Document

from erpnext.edi.doctype.edi_template.edi_template import EDITemplate

__all__ = ["get_context"]


def get_context(self: EDITemplate, doc: "Document", method: str) -> None:
	return {"doc": doc}
