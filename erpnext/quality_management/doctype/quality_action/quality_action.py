# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from operator import itemgetter
from frappe.model.document import Document


class QualityAction(Document):
	def validate(self):
		self.status = 'Open' if any([d.status=='Open' for d in self.resolutions]) else 'Completed'
		self.validate_objective()

	def validate_objective(self):
		allowed_objectives = frappe.db.sql("""
			SELECT objective FROM `tabQuality Review Objective`
			WHERE parent=%s
		""", self.review)
		allowed_objectives = list(map(itemgetter(0), allowed_objectives))

		if self.objective not in allowed_objectives:
			frappe.throw(_("Objective: {0} is not present in Review: {1}")
				.format(self.objective, self.review))
