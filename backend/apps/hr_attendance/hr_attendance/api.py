import frappe
from frappe import _
from frappe.utils import now_datetime, getdate

@frappe.whitelist()
def check_in(employee, lat, lon, device_id=None):
    today = getdate()
    
    # Check if attendance already exists for today
    attendance = frappe.get_all("Attendance", filters={
        "employee": employee,
        "attendance_date": today
    }, limit=1)
    
    if attendance:
        doc = frappe.get_doc("Attendance", attendance[0].name)
        if doc.check_in:
            return {"status": "error", "message": _("Already checked in today")}
    else:
        doc = frappe.new_doc("Attendance")
        doc.employee = employee
        doc.attendance_date = today
        doc.status = "Present"
    
    doc.check_in = now_datetime()
    doc.check_in_latitude = lat
    doc.check_in_longitude = lon
    doc.device_id = device_id
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return {"status": "success", "message": _("Checked in successfully"), "name": doc.name}

@frappe.whitelist()
def check_out(employee, lat, lon):
    today = getdate()
    
    attendance = frappe.get_all("Attendance", filters={
        "employee": employee,
        "attendance_date": today
    }, limit=1)
    
    if not attendance:
        return {"status": "error", "message": _("No check-in found for today")}
    
    doc = frappe.get_doc("Attendance", attendance[0].name)
    if doc.check_out:
        return {"status": "error", "message": _("Already checked out today")}
    
    doc.check_out = now_datetime()
    doc.check_out_latitude = lat
    doc.check_out_longitude = lon
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return {"status": "success", "message": _("Checked out successfully"), "name": doc.name}
