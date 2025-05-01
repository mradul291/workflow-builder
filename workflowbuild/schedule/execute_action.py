import frappe
from datetime import timedelta
from rq import Queue
from redis import Redis
from .logs import create_scheduled_job
import os
import json

def check_trigger_event(workflow_actions, doc):
    print("start path",os.getcwd())
    try:
        """Cron job to check if any workflow event is triggered and act on the configured actions"""
        print("Current Path",os.getcwd())
        
        
        for action in workflow_actions:

            action_type = action.get('action_type')  # Email, SMS, ToDo
            execution_days = int(action.get('execution_time') or 0)

            if action_type == "Email":
                queue_email = Queue(name='email', connection=Redis())
                email_template = frappe.get_doc("Email Template", action.get("email_template"))

                email_detail = {
                    "email_temp": email_template,
                    "email_id": doc.email_id,
                    "doc":doc
                }

                job = queue_email.enqueue_in(
                    timedelta(seconds=int(execution_days)),
                    "workflowbuild.schedule.utils.send_email",
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
                queue_sms = Queue(name='sms', connection=Redis())
                job = queue_sms.enqueue_in(
                    timedelta(seconds=int(execution_days)),
                    "workflowbuild.schedule.utils.sends_sms",
                    args=[action,doc]
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
                print("SMS Job Scheduled:", job_resp)


            elif action_type == "ToDO":
                queue_todo = Queue(name='todo', connection=Redis())
                job = queue_todo.enqueue_in(
                    timedelta(seconds=int(execution_days)),
                    "workflowbuild.schedule.utils.assign_task",
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
