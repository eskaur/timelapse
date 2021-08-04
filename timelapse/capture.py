"""Module for capturing images to be used for time-lapse videos"""

import datetime
import logging
import time
from pathlib import Path
from tempfile import TemporaryDirectory

import cv2
import numpy as np

from timelapse.camera import Camera
from timelapse.common import DEFAULT_TIME_FORMAT


_logger = logging.getLogger(__name__)


def _save_image(image: np.ndarray, filepath: Path):
    cv2.imwrite(str(filepath), image)


def _get_image_save_size(camera: Camera, save_extension: str):
    with TemporaryDirectory() as tmpdir:
        tmpfilepath = Path(tmpdir) / ("test" + save_extension)
        _save_image(image=camera.capture(), filepath=tmpfilepath)
        size_bytes = tmpfilepath.stat().st_size
    return size_bytes


def _get_megabytes_per_day(
    camera: Camera, interval: datetime.timedelta, save_extension
):
    bytes_per_capture = _get_image_save_size(camera, save_extension)
    captures_per_day = datetime.timedelta(days=1) / interval
    return bytes_per_capture * captures_per_day / 1e6


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
    save_extension = ".png"

    megabytes_per_day = _get_megabytes_per_day(camera, interval, save_extension)
    _logger.info("These settings will accumulate %.2f MB per day", megabytes_per_day)

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
            filepath = destination / (timestamp + save_extension)
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
