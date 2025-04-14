import frappe
from frappe.utils import now_datetime, add_days
from datetime import timedelta
# from frappe import enqueue
import json
from rq import Queue
import time
from frappe.utils.background_jobs import get_queue
from redis import Redis
from .utils import send_email
from .utils import assign_task
from .utils import send_sms


# @frappe.whitelist(allow_guest=True)
def check_trigger_event(workflow_actions, doc):
    try:
        print("check trigger")
        print("check trigger")


        """Cron job to check if any workflow event is triggered and act on the configured actions"""
        # return "success"
        
        # queue = get_queue("default")
        queue = Queue(name='default', connection=Redis())

        # Queue(name='home-mycomputer-Pankaj-WorkFlow2-frappe-bench:short')
        # doc = json.loads(doc)
        queue_args = {
		"site": frappe.local.site,
		"user": frappe.session.user,
		"method": "workflowbuild.schedule.utils.send_email",
        "job_id":"Workflowbuild_schedule_trigger_event_send_email"
	    }
        print(workflow_actions)
        for action in (workflow_actions):
            print(action)
            action_type = action.get('action_type')  # Email, SMS, ToDo
            execution_days = action.get('execution_time') or 0

            # scheduled_time = now_datetime() if execution_days == 0 else add_days(now_datetime(), int(execution_days))

            if action_type == "Email":
                email_temp = frappe.get_doc("Email Template", action.email_template)
                
                email_detail = {
                    "email_temp":email_temp,
                    "email_id":doc.email_id,
                }
                job = queue.enqueue_in(timedelta(days = int(execution_days)), "workflowbuild.schedule.utils.send_email", email_detail, doc )
                print(job.id)
              
            elif action_type == "SMS":
                if int(execution_days) == 0:
                    # send_sms(action)
                    pass
                else:
                    # enqueue("workflowbuild.schedule.trigger_event.send_sms", job_id= "Workflowbuild_schedule_trigger_event_send_sms",  queue="long", now=False, action=action, doc=doc)
                    pass

            elif action_type == "ToDO":
                print("2", action_type , execution_days)
                if int(execution_days) == 0:
                    assign_task(action, doc)
                    pass
                else:
                    job = queue.enqueue_in(timedelta(days = int(execution_days)), "workflowbuild.schedule.trigger_event.assign_task", action, doc )
                    print(job.id)

                    
                    

        return True
    except Exception as error:
        print(error)


