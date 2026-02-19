"""
Arq worker for scrape ingestion jobs.

Run with: arq democrata_server.worker.WorkerSettings
"""
import logging
import os
from pathlib import Path
from uuid import UUID

from arq.connections import RedisSettings
from dotenv import load_dotenv

from democrata_server.adapters.scrapers import get_fetcher, get_source_config
from democrata_server.api.http.deps import get_execute_scrape_run_use_case

project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

logger = logging.getLogger(__name__)


async def run_scrape_job(ctx: dict, job_id: str, source_id: str) -> None:
    """Arq task: run scrape for source_id, updating job in Redis."""
    execute_scrape = ctx["execute_scrape_run"]
    jurisdiction = os.getenv("JURISDICTION", "au")

    config = get_source_config(source_id, jurisdiction)
    if not config:
        logger.error("Source %s not found in config", source_id)
        return

    fetcher_cls = get_fetcher(config.scraper)
    if not fetcher_cls:
        logger.error("Unknown scraper: %s", config.scraper)
        return

    fetcher = fetcher_cls()
    uuid_id = UUID(job_id)

    try:
        await execute_scrape.execute(uuid_id, config, fetcher)
        logger.info("Scrape job %s completed for source %s", job_id, source_id)
    except Exception as e:
        logger.exception("Scrape job %s failed: %s", job_id, e)


async def startup(ctx: dict) -> None:
    """Inject dependencies into worker context."""
    ctx["execute_scrape_run"] = get_execute_scrape_run_use_case()


class WorkerSettings:
    functions = [run_scrape_job]
    on_startup = startup
    redis_settings = RedisSettings.from_dsn(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    job_timeout = 3600
    max_jobs = 1
