from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from lead_engine.engine import run_scan
import logging

log = logging.getLogger("leadgen.scheduler")

class SchedulerManager:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.job_id = "lead_scan_job"
        self._is_running = False
        self._interval_minutes = 60

    def start(self, interval_minutes: int = 60):
        if self.scheduler.get_job(self.job_id):
            self.stop()
        
        self._interval_minutes = interval_minutes
        self.scheduler.add_job(
            run_scan, # Now an async function
            trigger=IntervalTrigger(minutes=self._interval_minutes),
            id=self.job_id,
            replace_existing=True
        )
        if not self.scheduler.running:
            self.scheduler.start()
        self._is_running = True
        log.info(f"Scheduler started with interval: {interval_minutes} minutes")

    def stop(self):
        if self.scheduler.get_job(self.job_id):
            self.scheduler.remove_job(self.job_id)
        self._is_running = False
        log.info("Scheduler stopped")

    def get_status(self):
        return {
            "is_running": self._is_running,
            "interval_minutes": self._interval_minutes,
            "next_run": str(self.scheduler.get_job(self.job_id).next_run_time) if self._is_running and self.scheduler.get_job(self.job_id) else None
        }

    async def run_scan_once(self):
        log.info("Manual/Cron scan trigger started")
        await run_scan()
        log.info("Manual/Cron scan trigger finished")

scheduler_manager = SchedulerManager()
