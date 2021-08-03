import pytest
import cv2
import numpy as np

from timelapse.camera import DummyCamera


def test_successful_init_and_release():
    with DummyCamera() as cam:
        pass

    with DummyCamera(width=800, height=600) as cam:
        pass

    with DummyCamera(width=800) as cam:
        pass

    with DummyCamera(height=600) as cam:
        pass


def test_invalid_init():
    with pytest.raises(RuntimeError):
        with DummyCamera(width=-800, height=-600) as cam:
            pass

    with pytest.raises(RuntimeError):
        with DummyCamera(width=-800, height=600) as cam:
            pass

    with pytest.raises(RuntimeError):
        with DummyCamera(width=800, height=-600) as cam:
            pass


def test_width_height():
    width = 500
    height = 400
    with DummyCamera(width=width, height=height) as cam:
        assert width == cam.width()
        assert height == cam.height()


def test_capture():
    with DummyCamera() as cam:
        image = cam.capture()
        assert isinstance(image, np.ndarray)
        assert image.shape == (cam.height(), cam.width(), 3)
