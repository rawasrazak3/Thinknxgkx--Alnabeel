frappe.listview_settings['Daily Labour Attendance'] = {
    onload(listview) {
        listview.page.add_actions_menu_item(__('Bulk Material Request'), () => {
            let selected = listview.get_checked_items();

            if (!selected.length) {
                frappe.msgprint(__('Please select at least one Daily Labour Attendance'));
                return;
            }

            let dla_names = selected.map(d => d.name);

            frappe.call({
                method: "alnabeel.alnabeel.doctype.daily_labour_attendance.daily_labour_attendance.create_bulk_material_request",
                args: {
                    dla_names: dla_names
                },
                callback(r) {
                    if (r.message) {
                        frappe.set_route("Form", "Material Request", r.message);
                    }
                }
            });
        });
    }
};
