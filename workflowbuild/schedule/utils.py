import os
import frappe
from frappe.utils import now_datetime
from rq import get_current_job
from frappe.utils import now_datetime
from rq.job import Job
from redis import Redis
from .logs import  update_scheduled_job
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
new_path = os.getenv("SITE_PATH")
site_name = os.getenv("SITE_NAME")
db_name = os.getenv("DB_NAME")

os.chdir(new_path)

frappe.init(site=os.path.join(new_path, site_name))
frappe.connect(site=os.path.join(new_path, site_name), db_name=db_name)

def send_email(email_detail):
    
    """Send Email using provided email_template"""
    try:
        print("Current job Id Email", get_current_job())
        
        started_at = now_datetime()

        print("1")
        doc = email_detail.get("doc")
        if not doc:
            return
        # try:
        if not email_detail.get("email_temp") or not doc.email_id:
            return
        email_temp = email_detail.get("email_temp")
        print("2")
        # Render subject and body using Jinja and context from doc
        subject = frappe.render_template(email_temp.subject, doc)
        message = frappe.render_template(email_temp.response, doc)
        print("3")
        frappe.sendmail(
            recipients=[doc.email_id],
            subject=subject or "Notification",
            message=message,
            delayed=False
        )
        job_id = get_current_job().id
        print("4")
        redis_conn = Redis()
        job = Job.fetch(job_id, connection=redis_conn)
        status = job.get_status()  # e.g., "queued", "started", "finished"
        print("5")
        print("job.exc_info -- Email", job.exc_info)

        if status == "failed":
        # Fetch the exception info (if available) for the failed job
            exc_info = job.exc_info
            update_scheduled_job(job_id, status, started_at, exc_info)
        else:
            update_scheduled_job(job_id, status, started_at)

    except Exception as error:
        print("Error In Email Sending", error)
    finally:
        frappe.destroy()
    

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

    print("Current job Id Todo", get_current_job())

    """Create ToDo for assigned user"""
    print("User ---", action)
    started_at = now_datetime()

    try:
        
        if not action.get('assigned_user'):
            assigned_user = doc.get('email_id')
        else:
            assigned_user = action.get('assigned_user')

        todo_temp = frappe.get_doc("ToDo Template", action.get('todo_template'))
        if not todo_temp:
            return
        
        description = todo_temp.get("description")
        due_date = todo_temp.get("due_date")
        # due_date is in seconds , convert to datetime
        due_date = now_datetime() + timedelta(seconds=due_date)
        
        todo = frappe.get_doc({
            "doctype": "ToDo",
            "description": description,
            "owner": doc.get('lead_owner'),
            "reference_type": "Lead",
            "reference_name": doc.get('name'),
            "allocated_to":assigned_user,
            "date":due_date,
            "assigned_by":doc.get('lead_owner')
        }).insert(ignore_permissions=True)

        frappe.db.commit()
        print("ToDo created with name:", todo.name)

        job_id = get_current_job().id

        redis_conn = Redis()
        job = Job.fetch(job_id, connection=redis_conn)
        status = job.get_status()  # e.g., "queued", "started", "finished"
        print("job.exc_info -- TODO", job.exc_info)
        if status == "failed":
        # Fetch the exception info (if available) for the failed job
            exc_info = job.exc_info
            update_scheduled_job(job_id, status, started_at, exc_info)
        else:
            update_scheduled_job(job_id, status, started_at)

        
        
        
    except Exception as error:
        print("error user", error)
    finally:
        frappe.destroy()



   