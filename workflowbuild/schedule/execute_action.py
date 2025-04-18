import frappe
from datetime import timedelta
from rq import Queue
from redis import Redis
from .logs import create_scheduled_job
import os
import json
from .utils import send_email, assign_task

def check_trigger_event(workflow_actions, doc):
    print("start path",os.getcwd())
    try:
        """Cron job to check if any workflow event is triggered and act on the configured actions"""
        print("Current Path",os.getcwd())
        
        queue = Queue(name='default', connection=Redis())

        for action in workflow_actions:

            action_type = action.get('action_type')  # Email, SMS, ToDo
            execution_days = int(action.get('execution_time') or 0)

            if action_type == "Email":
                email_template = frappe.get_doc("Email Template", action.get("email_template"))

                email_detail = {
                    "email_temp": email_template,
                    "email_id": doc.email_id,
                    "doc":doc
                }

                job = queue.enqueue_in(
                    timedelta(days=execution_days),
                    send_email(),
                    args=[email_detail]
                )
                job_args_serializable = []

                for arg in job.args:
                    try:
                        job_args_serializable.append(json.loads(json.dumps(arg, default=str)))
                    except Exception as e:
                        job_args_serializable.append(str(arg))

                job_data = {
                    "job_id": job.id,
                    "job_name": job.func_name,  # Use job.func_name instead of private _func_name
                    "timeout": job.timeout,
                    "schedule_at": job.enqueued_at or None,
                    "job_created": job.created_at,
                    "arguments": json.dumps(job_args_serializable, indent=2),
                    "status": job.get_status()
                }
                job_resp = create_scheduled_job(job_data)
                print("Email Job Scheduled:", job_resp)

            elif action_type == "SMS":
                if execution_days == 0:
                    # send_sms(action, doc)
                    pass
                else:
                    # job = queue.enqueue_in(timedelta(days=execution_days), "your.sms.function", args=[action, doc])
                    pass

            elif action_type == "ToDO":
                job = queue.enqueue_in(
                    timedelta(seconds=3),
                    assign_task(),
                    args=[action, doc]
                )
                job_args_serializable = []

                for arg in job.args:
                    try:
                        job_args_serializable.append(json.loads(json.dumps(arg, default=str)))
                    except Exception as e:
                        job_args_serializable.append(str(arg))

                job_data = {
                    "job_id": job.id,
                    "job_name": job.func_name,
                    "timeout": job.timeout,
                    "schedule_at": job.enqueued_at or None,
                    "job_created": job.created_at,
                    "arguments": json.dumps(job_args_serializable, indent=2),
                    "status": job.get_status()
                }
                job_resp = create_scheduled_job(job_data)
                print("ToDo Job Scheduled:", job_resp)

        return True

    except Exception as error:
        print("Error in check_trigger_event:", error)
        return False
