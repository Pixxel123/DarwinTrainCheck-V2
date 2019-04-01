from apscheduler.schedulers.blocking import BlockingScheduler
from helper import status_check

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes='1')
def update_status_checker():
    status_check()


sched.start()
