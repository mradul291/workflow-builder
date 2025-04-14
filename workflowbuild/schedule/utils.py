import frappe
from frappe.utils import now_datetime, add_days
from datetime import timedelta
# from frappe import enqueue
import json
import os

def send_email(email_detail, doc):
    
    new_path = "/home/mycomputer/Pankaj/WorkFlow2/frappe-bench/sites"  # Replace with your desired path
    os.chdir(new_path)
    
    frappe.init(site="/home/mycomputer/Pankaj/WorkFlow2/frappe-bench/sites/workflow.local")
    frappe.connect(site="/home/mycomputer/Pankaj/WorkFlow2/frappe-bench/sites/workflow.local",db_name="_28ce801016e87d3c")

    # try:
    if not email_detail.get("email_temp") or not doc.email_id:
        return
    email_temp = email_detail.get("email_temp")
    
    # Render subject and body using Jinja and context from doc
    subject = frappe.render_template(email_temp.subject, doc)
    message = frappe.render_template(email_temp.response, doc)

    frappe.sendmail(
        recipients=[doc.email_id],
        subject=subject or "Notification",
        message=message,
        delayed=False
    )
    

def send_sms(action):
    """Send SMS using provided sms_template"""
    try:
        if not action.sms_template or not action.recipient:
            return

        message = frappe.render_template(frappe.db.get_value("SMS Template", action.sms_template, "message"), {})
        frappe.sendsms(recipients=[action.recipient], message=message)
    except Exception as error:
        print("error", error)


def assign_task(action, doc):
    """Create ToDo for assigned user"""
    print("User ---", action)

    new_path = "/home/mycomputer/Pankaj/WorkFlow2/frappe-bench/sites"  # Replace with your desired path
    os.chdir(new_path)
    
    frappe.init(site="/home/mycomputer/Pankaj/WorkFlow2/frappe-bench/sites/workflow.local")
    frappe.connect(site="/home/mycomputer/Pankaj/WorkFlow2/frappe-bench/sites/workflow.local",db_name="_28ce801016e87d3c")
    
    try:
        if not action.get('assigned_user'):
            return

        frappe.get_doc({
            "doctype": "ToDo",
            "description": doc.get('request_type') or "Action Required",
            "owner": doc.get('lead_owner'),
            "reference_type": "Lead",
            "reference_name": doc.get('name'),
            "allocated_to":action.get('assigned_user'),
            "date": now_datetime().date()
        }).insert(ignore_permissions=True)

    except Exception as error:
        print("error user", error)


