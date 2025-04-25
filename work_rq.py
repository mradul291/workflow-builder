from rq import Worker, Queue, Connection
from redis import Redis
import os
import frappe
from dotenv import load_dotenv

# List of queues to listen to (unchanged)
listen = ['default', 'email', 'sms', 'todo']
workers_count = 2  # Number of workers to start
redis_conn = Redis()

load_dotenv(os.path.join(os.path.dirname(__file__), './.env'))

site_path = os.getenv("SITE_PATH")
site_name = os.getenv("SITE_NAME")
db_name = os.getenv("DB_NAME")

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
