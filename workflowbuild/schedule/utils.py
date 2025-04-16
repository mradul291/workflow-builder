import frappe
from frappe.utils import now_datetime
from rq import get_current_job
import os
from frappe.utils import now_datetime, format_duration
from rq.job import Job
from redis import Redis
from .logs import  update_scheduled_job
from dotenv import load_dotenv
import time

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

def send_email(email_detail, doc):
    
    """Send Email using provided email_template"""
    try:
        print("Current job Id Email", get_current_job())
        new_path = os.getenv("SITE_PATH")
        site_name = os.getenv("SITE_NAME")
        db_name = os.getenv("DB_NAME")
        
        print("Current Path",os.getcwd())
        print("New Path",new_path)
        print("Site Name",site_name)
        print("DB Name",db_name)

        print("\n")
        
        os.chdir(new_path)
        
        frappe.init(site=os.path.join(new_path, site_name))
        frappe.connect(site=os.path.join(new_path, site_name), db_name=db_name)

        started_at = now_datetime()

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
        job_id = get_current_job().id

        redis_conn = Redis()
        job = Job.fetch(job_id, connection=redis_conn)
        status = job.get_status()  # e.g., "queued", "started", "finished"
        
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

    new_path = os.getenv("SITE_PATH")
    site_name = os.getenv("SITE_NAME")
    db_name = os.getenv("DB_NAME")
    
    os.chdir(new_path)
    
    frappe.init(site=os.path.join(new_path, site_name))
    frappe.connect(site=os.path.join(new_path, site_name), db_name=db_name)
    
    started_at = now_datetime()

    try:
        
        if not action.get('assigned_user'):
            return
    
        todo = frappe.get_doc({
            "doctype": "ToDo",
            "description": doc.get('request_type') or "Action Required",
            "owner": doc.get('lead_owner'),
            "reference_type": "Lead",
            "reference_name": doc.get('name'),
            "allocated_to":action.get('assigned_user'),
            "date": now_datetime().date(),
            "assigned_by":doc.get('lead_owner')
        }).insert(ignore_permissions=True)

        frappe.db.commit()
        print("ToDo created with name:", todo.name)

        job_id = get_current_job().id

        redis_conn = Redis()
        job = Job.fetch(job_id, connection=redis_conn)
        status = job.get_status()  # e.g., "queued", "started", "finished"
        # ended_at = now_datetime()
        # status = fetch status from job
        update_scheduled_job(job_id, status, started_at)

        
        
        
    except Exception as error:
        print("error user", error)
    finally:
        frappe.destroy()



   