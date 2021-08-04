"""Module for launching timelapse capture from the command line"""

import argparse
from datetime import timedelta
from pathlib import Path

from timelapse.camera import Webcam
from timelapse.capture import repeated_capture


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch a timelapse recording")

    parser.add_argument(
        "--destination",
        type=Path,
        required=True,
        help="Directory for saving captured images",
    )

    parser.add_argument(
        "--interval-minutes",
        type=int,
        required=True,
        help="Minutes between each capture",
    )

    return parser.parse_args()


def _main():
    args = _args()

    with Webcam() as camera:
        repeated_capture(
            camera=camera,
            interval=timedelta(minutes=args.interval_minutes),
            destination=args.destination,
        )


if __name__ == "__main__":
    _main()
