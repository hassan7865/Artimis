from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from lead_engine.engine import run_scan
import logging
from datetime import datetime, timezone
import asyncio

log = logging.getLogger("leadgen.scheduler")

class SchedulerManager:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.job_id = "lead_scan_job"
        self._is_running = False
        self._interval_minutes = 60
        self._scan_lock = asyncio.Lock()

    async def _run_scan_job(self):
        if self._scan_lock.locked():
            log.warning("Scan skipped: previous run still in progress")
            return
        async with self._scan_lock:
            await run_scan()

    def start(self, interval_minutes: int = 60):
        if self.scheduler.get_job(self.job_id):
            self.stop()
        
        self._interval_minutes = interval_minutes
        self.scheduler.add_job(
            self._run_scan_job,
            trigger=IntervalTrigger(minutes=self._interval_minutes),
            id=self.job_id,
            next_run_time=datetime.now(timezone.utc),
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
        job = self.scheduler.get_job(self.job_id)
        is_running = bool(self.scheduler.running and job)
        self._is_running = is_running
        return {
            "is_running": is_running,
            "interval_minutes": self._interval_minutes,
            "next_run": str(job.next_run_time) if job else None
        }

    async def run_scan_once(self):
        log.info("Manual/Cron scan trigger started")
        await self._run_scan_job()
        log.info("Manual/Cron scan trigger finished")

scheduler_manager = SchedulerManager()
