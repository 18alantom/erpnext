// Copyright (c) 2018, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Quality Review', {
	department(frm) {
		frappe.call({
			"method": "frappe.client.get",
			args: {
				doctype: "Quality Goal",
				name: frm.doc.department
			},
			callback: function(data){
				frm.fields_dict.reviews.grid.remove_all();
				let objectives = data.message.objectives;
				for (var i in objectives) {
					frm.add_child("reviews");
					frm.fields_dict.reviews.get_value()[i].objective = objectives[i].objective;
					frm.fields_dict.reviews.get_value()[i].target = objectives[i].target;
					frm.fields_dict.reviews.get_value()[i].uom = objectives[i].uom;
				}
				frm.refresh();
			}
		});
	},
});


frappe.ui.form.on('Quality Review Objective', {
	achieved(frm, cdt, cdn) {
		const {target, achieved} = locals[cdt][cdn]
		if(achieved < target) {
			frappe.model.set_value(cdt, cdn, 'status', 'Failed')
			frappe.model.set_value('Quality Review', frm.doc.name, 'status', 'Failed')
		} else {
			frappe.model.set_value(cdt, cdn, 'status', 'Passed')
		}

		check_all_status_and_set(frm)
	},
	status(frm) {
		check_all_status_and_set(frm)
	}
})

function check_all_status_and_set(frm) {
	const status_list = frm.doc.reviews.map(({status}) => status)
	const open_statuses = status_list.filter((s) => s === 'Open').length
	const failed_statuses = status_list.filter((s) => s === 'Failed').length

	if(open_statuses > 0) {
		frappe.model.set_value('Quality Review', frm.doc.name, 'status', 'Open')
	} else if(failed_statuses > 0) {
		frappe.model.set_value('Quality Review', frm.doc.name, 'status', 'Failed')
	} else {
		frappe.model.set_value('Quality Review', frm.doc.name, 'status', 'Passed')
	}
}
