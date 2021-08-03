"""Common logger initialization for the timelapse package.

Other modules should create its own sub-logger,
```
_logger = logging.getLogger(__name__)
```
which will inherit this global configuration.
"""

import logging
from datetime import datetime
from pathlib import Path

logfile = Path("logs") / f"timelapse_{datetime.now().strftime(r'%Y-%m-%d_%H%M%S')}.log"
logfile.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(logfile),  # Log to file
        logging.StreamHandler(),  # Log to terminal
    ],
)
logging.info("Logger configured to file: %s", logfile)
