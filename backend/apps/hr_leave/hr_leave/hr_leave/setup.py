import frappe

def setup_leave_workflow():
    # 1. Create Workflow States
    states = ["Open", "Pending", "Approved", "Rejected"]
    for state in states:
        if not frappe.db.exists("Workflow State", state):
            frappe.get_doc({
                "doctype": "Workflow State",
                "workflow_state_name": state
            }).insert()
    
    # 2. Create Workflow Action Master
    actions = ["Submit", "Approve", "Reject"]
    for action in actions:
        if not frappe.db.exists("Workflow Action Master", action):
            frappe.get_doc({
                "doctype": "Workflow Action Master",
                "workflow_action_name": action
            }).insert()

    # 3. Create Workflow
    if not frappe.db.exists("Workflow", "Leave Approval"):
        doc = frappe.get_doc({
            "doctype": "Workflow",
            "workflow_name": "Leave Approval",
            "document_type": "Leave Request",
            "workflow_state_field": "status",
            "is_active": 1,
            "states": [
                {"state": "Open", "doc_status": "0", "allow_edit": "Employee"},
                {"state": "Pending", "doc_status": "0", "allow_edit": "HR Admin"},
                {"state": "Approved", "doc_status": "1", "allow_edit": "HR Admin"},
                {"state": "Rejected", "doc_status": "0", "allow_edit": "HR Admin"}
            ],
            "transitions": [
                {
                    "state": "Open",
                    "action": "Submit",
                    "next_state": "Pending",
                    "allowed": "Employee"
                },
                {
                    "state": "Pending",
                    "action": "Approve",
                    "next_state": "Approved",
                    "allowed": "HR Admin"
                },
                {
                    "state": "Pending",
                    "action": "Reject",
                    "next_state": "Rejected",
                    "allowed": "HR Admin"
                }
            ]
        })
        doc.insert()
        print("Leave Approval Workflow created.")
    else:
        print("Leave Approval Workflow already exists.")
    frappe.db.commit()

if __name__ == "__main__":
    setup_leave_workflow()
