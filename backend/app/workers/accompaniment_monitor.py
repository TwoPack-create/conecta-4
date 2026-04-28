from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.services.safety_service import detonate_expired_accompaniment_sessions

scheduler: AsyncIOScheduler | None = None


async def run_accompaniment_expiration_check() -> None:
    async with AsyncSessionLocal() as session:
        await detonate_expired_accompaniment_sessions(session)


def start_scheduler() -> AsyncIOScheduler:
    global scheduler
    if scheduler is not None and scheduler.running:
        return scheduler

    settings = get_settings()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_accompaniment_expiration_check,
        trigger=IntervalTrigger(seconds=settings.accompaniment_checker_interval_seconds),
        id="accompaniment_expiration_checker",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    return scheduler


def stop_scheduler() -> None:
    global scheduler
    if scheduler is not None and scheduler.running:
        scheduler.shutdown(wait=False)
