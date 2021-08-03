"""Module holding camera functionality"""
import logging

import cv2
import numpy as np

_logger = logging.getLogger(__name__)


class Camera:
    """Base class for all cameras"""

    def __init__(self):
        _logger.info("Initializing camera: %s", self)
        self.frame_counter = 0
        self._width = None
        self._height = None

    def capture(self) -> np.ndarray:
        """Capture a single color frame

        Returns:
            Numpy array with image color data [H,W,3].
        """
        self.frame_counter += 1
        _logger.info("Capturing frame: %s", self.frame_counter)
        return self._capture()

    def preview(self) -> None:
        """Test capture and show in OpenCV window."""
        frame = self.capture()
        cv2.imshow("Preview: Press any key to exit", frame)
        cv2.waitKey()

    def width(self) -> int:
        """Get width of images taken by this camera.

        Returns:
            Pixel width as integer
        """
        return self._width

    def height(self) -> int:
        """Get height of images taken by this camera.

        Returns:
            Pixel height as integer
        """
        return self._height

    def _capture(self) -> np.ndarray:
        raise NotImplementedError

    def _release(self):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _logger.info("Releasing camera resources for: %s", self)
        self._release()


class DummyCamera(Camera):
    """Camera for testing. Returns dummy-images"""

    def __init__(self, width=800, height=600):
        super().__init__()
        if width <= 0 or height <= 0:
            raise RuntimeError("Both width and height must be nonzero and positive.")
        self._width = width
        self._height = height
        _logger.info("Set resolution: W:%s, H:%s", self.width(), self.height())

    def _capture(self) -> np.ndarray:
        image = np.zeros((self.height(), self.width(), 3))
        image[:, :, :] = 50
        cv2.putText(
            image,
            f"Frame: {self.frame_counter}",
            (self.height() // 2, self.width() // 2),
            fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=1,
        )
        return image

    def _release(self):
        pass


class Webcam(Camera):
    """Class representing a real webcam"""

    def __init__(self, device_id: int = 0):
        """Initialize webcam

        Arguments:
            device_id    Device to connect to
        """
        super().__init__()
        self._camera = cv2.VideoCapture(device_id)
        if not self._camera.isOpened:
            raise RuntimeError("Failed to open camera")

        self._height, self._width, _ = self._capture().shape
        _logger.info("Detected resolution: W:%s, H:%s", self.width(), self.height())

    def _capture(self) -> np.ndarray:
        is_success, frame = self._camera.read()
        if not is_success:
            raise RuntimeError("Failed to capture frame")
        return frame

    def _release(self):
        self._camera.release()
