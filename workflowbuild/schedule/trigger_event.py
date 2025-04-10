import frappe
from frappe.utils import now_datetime, add_days
from frappe import enqueue
import json


@frappe.whitelist(allow_guest=True)
def check_trigger_event(workflow_actions, doc):
    """Cron job to check if any workflow event is triggered and act on the configured actions"""
    # return "success"
    workflow_actions = json.loads(workflow_actions)
    doc = json.loads(doc)
    print("DOC --- \n",doc)
    for action in workflow_actions:
        print(action)
        action_type = action.get('action_type')  # Email, SMS, ToDo
        execution_days = action.get('execution_time') or 0

        scheduled_time = now_datetime() if execution_days == 0 else add_days(now_datetime(), int(execution_days))

        if action_type == "Email":
            if int(execution_days) == 0:
                send_email(action, doc)
            else:
                enqueue("workflowapp.schedule.trigger_event.send_email", job_id= "workflowapp_schedule_trigger_event_send_email", queue="long", action=action , doc=doc)

        elif action_type == "SMS":
            if int(execution_days) == 0:
                send_sms(action)
            else:
                enqueue("workflowapp.schedule.trigger_event.send_sms", job_id= "workflowapp_schedule_trigger_event_send_sms",  queue="long", action=action, doc=doc)

        elif action_type == "ToDO":
            print("2", action_type , execution_days)
            if int(execution_days) == 0:
                print("2.1")
                assign_task(action, doc)
            else:
                print("2.2")
                enqueue("workflowapp.schedule.trigger_event.assign_task", job_id= "workflowapp_schedule_trigger_event_assign_task",queue="long", action=action, doc=doc)

    return True

import frappe

def send_email(action, doc):
    """Send email using provided email_template"""

    try:
        if not action.get('email_template') or not doc.get("email_id"):
            return

        email_temp = frappe.get_doc("Email Template", action.get('email_template'))

        # Render subject and body using Jinja and context from doc
        subject = frappe.render_template(email_temp.subject, doc)
        message = frappe.render_template(email_temp.response, doc)

        frappe.sendmail(
            recipients=[doc.get('email_id')],
            subject=subject or "Notification",
            message=message,
            delayed=False
        )
    except Exception as error:
        frappe.log_error(frappe.get_traceback(), "Error sending email")
        print("error email", error)



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


