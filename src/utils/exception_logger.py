import logging
import traceback
from datetime import datetime
import os
from src.utils.paths import get_data_dir

# Configure logging dynamically inside the persistent data directory
log_dir = os.path.join(get_data_dir(), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.normpath(os.path.join(log_dir, "error.log"))

logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_exception(e: Exception) -> None:
    """
    Logs an exception with timestamp and traceback to data/logs/error.log.
    
    Args:
        e: The exception to log.
    """
    error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
    logging.error(error_msg)
    print(f"ERROR: {error_msg}")

