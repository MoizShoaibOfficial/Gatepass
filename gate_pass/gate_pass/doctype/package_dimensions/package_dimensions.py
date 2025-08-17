# Copyright (c) 2024, Mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PackageDimensions(Document):
	def before_save(self):
		self.dimensions()
  
	def dimensions(self):
		self.dimension = str(self.l) +" X "+ str(self.w) +" X "+ str(self.h)
		frappe.errprint(self.dimension)
		frappe.msgprint("👌")
		# self.dimension = str(self.l) +" X "+ str(self.w) +" X "+ str(self.h)
