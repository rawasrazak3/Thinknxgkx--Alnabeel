import frappe

@frappe.whitelist()
def get_last_transactions(item_code):

    if not item_code:
        return []

    data = frappe.db.sql("""
        SELECT 
            pi.name as invoice,
            pi.supplier,
            pi.posting_date,
            poi.project,
            poi.cost_center,
            poi.qty,
            poi.rate,
            poi.amount,
            poi.item_tax_template,
            poi.rate as valuation_rate,
            poi.purchase_order
        FROM `tabPurchase Invoice Item` poi
        INNER JOIN `tabPurchase Invoice` pi 
            ON pi.name = poi.parent
        WHERE 
            poi.item_code = %s
            AND pi.docstatus = 1
        ORDER BY pi.posting_date DESC
        LIMIT 5
    """, (item_code,), as_dict=True)

    return data