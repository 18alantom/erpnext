// Copyright (c) 2018, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Quality Goal", {
	department(frm, cdt, cdn) {
		const { department } = locals[cdt][cdn];
		if (!department) {
			return;
		}

		frappe.call({
			method:
				"erpnext.quality_management.doctype.quality_goal.quality_goal.get_quality_objectives_by_department",
			args: { department },
			callback(r) {
				const { message } = r;
				if (!message.length) {
					return;
				}

				frm.set_value("objectives", []);
				message.forEach((obj) => {
					let row = frm.add_child("objectives", obj);
					row.objective = obj.name;
				});
				frm.refresh_field("objectives");
			},
		});
	},
});
