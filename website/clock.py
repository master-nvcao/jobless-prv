from apscheduler.schedulers.blocking import BlockingScheduler
from website.extras import update_finished_offers
from . import db, create_app



def scheduled_tasks():
    scheduler = BlockingScheduler()

    # Schedule the task to run every day at 9:00 PM (server time)
    scheduler.add_job(update_finished_offers, 'cron', hour=00, args=[create_app(), db])

    # You can add more tasks and schedules here

    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == '__main__':
    scheduled_tasks()
