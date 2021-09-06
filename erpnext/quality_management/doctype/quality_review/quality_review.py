# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from datetime import timedelta, date
from frappe.model.document import Document


class QualityReview(Document):
	def validate(self):
		# fetch targets from goal
		if not self.reviews:
			for d in frappe.get_doc('Quality Goal', self.department).objectives:
				self.append('reviews', dict(
					objective = d.objective,
					target = d.target,
					uom = d.uom,
					status = "Open"
				))

		self.set_status()

	def set_status(self):
		# if any child item is failed, fail the parent
		if not len(self.reviews or []) or any([d.status=='Open' for d in self.reviews]):
			self.status = 'Open'
		elif any([d.status=='Failed' for d in self.reviews]):
			self.status = 'Failed'
		else:
			self.status = 'Passed'

def create_quality_review(goal_name):
	goal = frappe.get_doc("Quality Goal", goal_name)
	today = frappe.utils.getdate()

	review = frappe.get_doc({
		"doctype": "Quality Review",
		"department": goal.name,
		"status": "Open",
		"date": today,
		"start_date": get_start_date(goal, today),
		"end_date": today,
	})

	review.insert(ignore_permissions=True)

def get_start_date(goal, today):
	if goal.frequency == "Daily":
		return today - timedelta(days=1)
	elif goal.frequency == "Weekly":
		return today - timedelta(weeks=1)
	elif goal.frequency == "Monthly":
		y = today.year
		m = today.month
		ny = y - goal.monthly_frequency // 12
		nm = m - goal.monthly_frequency % 12
		if nm <= 0:
			nm += 12
			ny -= 1
		return date(ny, nm, today.day)
