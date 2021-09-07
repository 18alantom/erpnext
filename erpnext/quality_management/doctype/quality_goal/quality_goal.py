# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from datetime import date
from frappe.model.document import Document
from erpnext.quality_management.doctype.quality_review.quality_review import create_quality_review


class QualityGoal(Document):
	def validate(self):
		if self.frequency == "Monthly" and self.monthly_frequency <= 0:
			frappe.throw(_("Monitoring frequency has to be positive number."))

	def on_submit(self):
		pass

def create_scheduled_quality_reviews():
	goals = frappe.db.sql("""
		SELECT name, start_date, frequency, weekday, monthly_frequency
		FROM `tabQuality Goal`
		WHERE %s BETWEEN start_date AND end_date
	""", frappe.utils.today(), as_dict=1)

	for goal in goals:
		should_create = get_should_create_review(goal)
		if not should_create:
			continue
		else:
			create_quality_review(goal.name)

def get_should_create_review(goal):
	weekday = frappe.utils.getdate().strftime("%A")
	start_date = date.fromisoformat(goal.start_date)
	today = date.fromisoformat(frappe.utils.today())

	if goal.frequency == "Daily":
		return True
	elif goal.frequency == "Weekly" and weekday == goal.weekday:
		return True
	elif goal.frequency == "Monthly" and \
		get_has_exact_monthly_interval_passed(start_date, today, goal.monthly_frequency):
		return True
	return False

def get_has_exact_monthly_interval_passed(start_date, end_date, monthly_frequency):
	if start_date.day != end_date.day:
		return False
	else:
		passed_interval = (end_date.year - start_date.year) * 12 \
			+ end_date.month - start_date.month
		return passed_interval % monthly_frequency == 0

@frappe.whitelist()
def get_quality_objectives_by_department(department):
	return frappe.get_list(
		"Quality Objective",
		fields=[
			"name", "uom", "target", "procedure",
			"ownership", "owner_name", "measurement",
			"data_source"
		],
		filters={"department":department}
	)
