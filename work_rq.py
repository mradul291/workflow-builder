from rq import Worker, Queue, Connection
from redis import Redis
import os
import frappe

# List of queues to listen to (unchanged)
listen = ['default', 'email', 'sms', 'todo']
workers_count = 2  # Number of workers to start
redis_conn = Redis()

site_path = os.environ.get("SITE_PATH", "/home/mycomputer/Pankaj/WorkFlow2/frappe-bench/sites")
site_name = os.environ.get("SITE_NAME", "workflow.local")
db_name = os.environ.get("DB_NAME", "workflow.local")

os.chdir(site_path)
frappe.init(site=os.path.join(site_path, site_name))
frappe.connect(site=os.path.join(site_path, site_name), db_name=db_name)

def start_worker():
    # Start two workers listening to the same queues with with_scheduler=True
    for _ in range(workers_count):  # We want to start two workers
        with Connection(redis_conn):
            worker = Worker(map(Queue, listen))  # Listen to the queues
            worker.work(with_scheduler=True)  # Keep with_scheduler=True as per your request

if __name__ == '__main__':
    start_worker()
