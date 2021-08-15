"""Module for creating timelapse videos from images"""

import datetime
from pathlib import Path

import cv2
import numpy as np

from timelapse.common import DEFAULT_TIME_FORMAT


def _get_image_width_height(file_path: Path) -> tuple:
    image = cv2.imread(str(file_path))
    return image.shape[1], image.shape[0]


def _get_datetime_from_file(file_path: Path) -> datetime.datetime:
    name = file_path.with_suffix("").name
    return datetime.datetime.strptime(name, DEFAULT_TIME_FORMAT)


def _make_timestamp_string(file_path: Path) -> str:
    dtime = _get_datetime_from_file(file_path)
    return dtime.strftime(r"%Y-%m-%d %H:%M:%S")


def _make_duration_string(timedelta: datetime.timedelta):
    days = timedelta.days
    hours, seconds = divmod(timedelta.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days:3} days, {hours:2} hours, {minutes:2} minutes, {seconds:2} seconds"


def _add_stamp(image: np.ndarray, stamp: str, color: tuple = (0, 0, 255)):
    cv2.putText(
        img=image,
        text=stamp,
        org=(20, 20),
        fontFace=cv2.FONT_HERSHEY_PLAIN,
        fontScale=1,
        color=color,
        thickness=1,
        lineType=cv2.LINE_AA,
    )


def _make_video_filename(
    first_timestamp: datetime.datetime,
    last_timestamp: datetime.datetime,
    label: str,
    speedup_factor: float,
):
    timestamp_pattern = r"%Y%m%d"
    return (
        "timelapse_"
        + ("" if not label else f"{label}_")
        + first_timestamp.strftime(timestamp_pattern)
        + "-"
        + last_timestamp.strftime(timestamp_pattern)
        + f"_{int(speedup_factor)}x"
        + ".avi"
    )


def create_timelapse(
    source: Path,
    dest: Path,
    fps: int,
    label: str = "",
    source_filetype: str = "png",
    verbose=True,
) -> Path:
    """Create time-lapse video based on source directory with time stamped images

    Video file will be saved to the source directory.

    Arguments:
        source              Path to directory with images
        dest                Path to directory for output video file
        fps                 Frames per second
        label               Optional label for the output video file
        source_filetype     File type to use as source images
        verbose             Verbosity (will not print if False)
    Returns
        Path to the created video
    """

    if not source.is_dir():
        raise RuntimeError(f"Directory does not exist: {source}")

    files = sorted(source.glob(f"*.{source_filetype}"), key=lambda path: path.name)
    if not files:
        raise RuntimeError(f"Could not find any {source_filetype} files in {source}.")

    first_timestamp = _get_datetime_from_file(files[0])
    last_timestamp = _get_datetime_from_file(files[-1])
    real_dt = last_timestamp - first_timestamp
    video_dt = datetime.timedelta(seconds=len(files) / fps)
    speedup_factor = real_dt / video_dt

    dest_file = dest / _make_video_filename(
        first_timestamp=first_timestamp,
        last_timestamp=last_timestamp,
        label=label,
        speedup_factor=speedup_factor,
    )

    size = _get_image_width_height(files[0])
    out = cv2.VideoWriter(str(dest_file), cv2.VideoWriter_fourcc(*"MJPG"), fps, size)

    try:
        for image_file in files:
            if verbose:
                print(f"Processing file: {image_file}")
            stamp = _make_timestamp_string(image_file)
            image = cv2.imread(str(image_file))
            _add_stamp(image, stamp)
            out.write(image)
    finally:
        out.release()

    if verbose:
        print("-" * 70)
        print(f"Successfully created video: {dest_file}")
        print("-" * 70)
        print(f"Real time:    {_make_duration_string(real_dt)}")
        print(f"Video length: {_make_duration_string(video_dt)}")
        print(f"Time ratio: {speedup_factor:.2f}")
        print(f"{len(files)} frames at {fps} FPS")

    return dest_file
