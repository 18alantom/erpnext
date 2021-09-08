// Copyright (c) 2018, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Quality Action', {

});

frappe.ui.form.on("Quality Action Resolution", {
	status(frm) {
		check_all_status_and_set(frm);
	},
});

function check_all_status_and_set(frm) {
	const open_statuses = frm.doc.resolutions
		.map(({ status }) => status)
		.filter((s) => s === "Open").length;

	if (open_statuses > 0) {
		frm.doc.status = "Open";
	} else {
		frm.doc.status = "Completed";
	}
	frm.refresh_field("status");
}
