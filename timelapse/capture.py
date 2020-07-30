import datetime
import logging
from pathlib import Path
import time

import numpy as np
import cv2

from .common import DEFAULT_TIME_FORMAT


class Webcam:
    """Class representing a webcam"""

    def __init__(self, device_id: int = 0):
        """Initialize webcam

        Arguments:
            device_id    Device to connect to
        """
        self.camera = cv2.VideoCapture(device_id)
        if not self.camera.isOpened:
            raise RuntimeError("Failed to open camera")

    def capture(self) -> np.ndarray:
        """Capture a single color frame

        Returns:
            Numpy array with image color data [H,W,3]
        """
        is_success, frame = self.camera.read()
        if not is_success:
            raise RuntimeError("Failed to capture frame")
        return frame

    def repeated_capture(
        self,
        interval: datetime.timedelta,
        destination: Path,
        max_captures: int = 10000,
        append: bool = False,
    ):
        """Perform repeated capture and save image files to directory

        Will log to file in the destination directory
        
        Arguments:
            interval        Pause between each capture
            destination     Destination directory (will create if it does not exist)
            max_captures    Maximum number of captures before automatically stopping
            append          Allow appending to directory with existing content
        """
        if destination.is_file():
            raise RuntimeError(f"Destination is a file: {destination}")
        if destination.is_dir():
            if list(destination.glob("*")) and not append:
                raise RuntimeError(f"Destination is not empty: {destination}")
        else:
            print(f"Creating directory: {destination}")
            destination.mkdir(parents=True)

        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG,
            filename=destination / "capture.log",
            format="%(asctime)s - %(levelname)10s - %(message)s",
        )
        logging.info("Logger configured")

        # Start capturing
        logging.info("Performing camera warmup ")
        self._warmup()
        n_captures = 0
        try:
            while n_captures < max_captures:
                time.sleep(interval.total_seconds())
                try:
                    frame = self.capture()
                    logging.debug(f"Successful capture ({n_captures})")
                except Exception as ex:
                    logging.warning(f"Capture failed: {ex}")
                    continue
                timestamp = datetime.datetime.now().strftime(DEFAULT_TIME_FORMAT)
                filepath = destination / f"{timestamp}.png"
                cv2.imwrite(str(filepath), frame)
                n_captures += 1
        except Exception as ex:
            logging.error(f"Unexpected error during repeated capture: {ex}")
            raise

    def preview(self):
        """Test capture and show in OpenCV window"""
        frame = self.capture()
        cv2.imshow("Preview: Press any key to exit", frame)
        cv2.waitKey()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print("Releasing camera resource")
        self.camera.release()

    def _warmup(self):
        self.capture()
