"""Module for capturing images to be used for time-lapse videos"""

import datetime
import logging
import time
from pathlib import Path

import cv2

from timelapse.camera import Camera
from timelapse.common import DEFAULT_TIME_FORMAT


_logger = logging.getLogger(__name__)


def repeated_capture(
    camera: Camera,
    interval: datetime.timedelta,
    destination: Path,
    max_captures: int = 10000,
    append: bool = False,
):
    """Perform repeated capture and save image files to directory

    Will log to file in the destination directory

    Arguments:
        camera          timelapse.Camera to use when capturing images
        interval        Pause between each capture
        destination     Destination directory (will create if it does not exist)
        max_captures    Maximum number of captures before automatically stopping
        append          Allow appending to directory with existing content
    """
    _logger.info("Starting timelapse loop with directory: %s", destination)

    if destination.is_file():
        raise RuntimeError(f"Destination is a file: {destination}")
    if destination.is_dir():
        if list(destination.glob("*")) and not append:
            raise RuntimeError(f"Destination is not empty: {destination}")
        _logger.info("Directory already exists.")
    else:
        _logger.info("Directory does not exist. Creating.")
        destination.mkdir(parents=True)

    try:
        for _ in range(max_captures):
            time.sleep(interval.total_seconds())
            try:
                image = camera.capture()
            except Exception as ex:  # pylint: disable=broad-except
                _logger.warning("Capture failed: %s", ex)
                continue

            timestamp = datetime.datetime.now().strftime(DEFAULT_TIME_FORMAT)
            filepath = destination / f"{timestamp}.png"
            cv2.imwrite(str(filepath), image)

    except KeyboardInterrupt:
        _logger.info("Capturing stopped manually by user")
        raise
    except Exception as ex:
        _logger.error("Unexpected error during repeated capture: %s", ex)
        raise
    except:
        _logger.error("Unexpected error during repeated capture")
        raise

    _logger.info("Finished automatically after reaching %s captures", max_captures)
