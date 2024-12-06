import os
import logging
import warnings
from typing import Any
from dotenv import load_dotenv
from curl_cffi import requests
from curl_cffi.requests.exceptions import HTTPError

from celery import Celery

from app.core.config import settings

from .search import search_main



# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(levelname)s: %(message)s",
    level=logging.INFO
)

# Load env variables
load_dotenv()

# Suppress warnings
warnings.filterwarnings(
    action="ignore",
    message=".*ssl_cert_reqs"
)

# Celery app setup
celery_app = Celery(
    'tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.beat_schedule = {
    'main-scrape': {
        'task': 'tasks.app.main',
        'schedule': "0 * * * *"
    },
}
celery_app.conf.timezone = 'UTC'
celery_app.conf.result_expires = 60
celery_app.conf.broker_connection_retry_on_startup = True

dep_env = os.getenv("DEP_ENV")


"""Task definitions"""
@celery_app.task
def main() -> bool:
    # Delete expired results
    # celery_app.control.purge()

    # Send request to API endpoint to start task
    root = "http://localhost:8000" if dep_env == 'dev' else "https://auto-nabavka.onrender.com"
    api_url = f'{root}/api/queue-tasks'

    # JSON payload
    payload = {
        "celery_auth": os.getenv("CELERY_AUTH")
    }

    # Sending the POST request to queue tasks
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        users = response.json()["users"]

        if users:
            logging.info(f"Processing {len(users)} users\n")
            for user in users:
                search.apply_async(args=[user])
            return "Tasks queued"
        else:
            return "No users found"
    
    except HTTPError as e:
        return f"Failed to send queue request: {str(e)}"

    except Exception as e:
        return f"Failed to queue tasks: {str(e)}"


@celery_app.task
def search(user_data: dict[str, int | str]) -> Any:
    results = search_main(user_data)
    return results
