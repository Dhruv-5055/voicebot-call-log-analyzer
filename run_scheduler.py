import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import ingest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


def job():
    done, failed = ingest.ingest_folder()
    logging.info("Ingest run finished: %s imported, %s failed", done, failed)


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, "interval", seconds=30, id="ingest_folder", replace_existing=True, max_instances=1)
    logging.info("Scheduler started. Watching the incoming folder. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")