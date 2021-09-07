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
	end_date = get_end_date(goal, today)

	review = frappe.get_doc({
		"doctype": "Quality Review",
		"department": goal.name,
		"status": "Open",
		"date": today,
		"start_date": get_start_date(goal, end_date),
		"end_date": end_date
	})

	review.insert(ignore_permissions=True)

@frappe.whitelist()
def get_start_and_end_date(department):
	goal = frappe.get_value(
		"Quality Goal",
		department,
		["start_date", "end_date", "frequency", "monthly_frequency", "weekday"],
		as_dict=1
	)
	today = frappe.utils.getdate()
	end_date = get_end_date(goal, today)
	start_date = get_start_date(goal=goal, end_date=end_date)
	return dict(start_date=start_date, end_date=end_date)

def get_end_date(goal, today):
	dow = [
		"Sunday", "Monday", "Tuesday", "Wednesday",
		"Thursday", "Friday", "Saturday"
	]
	if goal.frequency == "Daily":
		return today

	elif goal.frequency == "Weekly":
		day_today = int(today.strftime("%w"))
		day_target = int(dow.index(goal.weekday))
		days_away = day_target - day_today

		if days_away == 0:
			return today
		elif days_away < 0:
			days_away += 7
		return today + timedelta(days=days_away - 1)
		
	elif goal.frequency == "Monthly":
		return get_monthly_interval_end_date_containing_today(
			goal.start_date, today, goal.monthly_frequency
		) - timedelta(days=1)

def get_start_date(goal, end_date):
	if goal.frequency == "Daily":
		return end_date - timedelta(days=1)
	elif goal.frequency == "Weekly":
		return end_date - timedelta(weeks=1) + timedelta(days=1)
	elif goal.frequency == "Monthly":
		y = end_date.year
		m = end_date.month
		ny = y - goal.monthly_frequency // 12
		nm = m - goal.monthly_frequency % 12
		if nm <= 0:
			nm += 12
			ny -= 1
		return date(ny, nm, end_date.day) + timedelta(days=1)

def get_monthly_interval_end_date_containing_today(start_date, today, monthly_frequency):
	from math import ceil
	temp_date = get_the_nth_day_of_the_mth_next_month(today, n=start_date.day)
	mb = months_between(start_date, temp_date)
	ni = ceil(mb / monthly_frequency)
	end_date = get_the_nth_day_of_the_mth_next_month(
		start_date, n=start_date, m=monthly_frequency * (ni - 1)
	)
	if temp_date > end_date:
		end_date = get_the_nth_day_of_the_mth_next_month(
			start_date, n=start_date, m=monthly_frequency * ni
		)
	return end_date

def get_the_nth_day_of_the_mth_next_month(d, n=1, m=1):
	m = d.month + m
	y = d.year + (m // 12)
	m = m % 12
	if m == 0:
		m = 12
		y -= 1
	return date(year=y, month=m, day=n) 

def months_between(d1, d2):
	y = abs(d2.year - d1.year)
	m = abs(d2.month + (y * 12) - d1.month)
	return m
