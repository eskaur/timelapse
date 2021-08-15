"""Module for creating time-lapse videos based on captured images"""

import argparse
from pathlib import Path

from timelapse.video import create_timelapse


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create timelapse video from images",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory that holds images. When processed, these will be sorted by filename.",
    )

    parser.add_argument(
        "--fps",
        type=int,
        required=True,
        help="Frames per second in output video.",
    )

    parser.add_argument(
        "--image-filetype",
        type=str,
        required=False,
        default="png",
        help="File type of images to process.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        required=False,
        default=Path(".").resolve(),
        help="Directory to place output video file in.",
    )

    parser.add_argument(
        "--label",
        type=str,
        required=False,
        default="",
        help="Optional label for the output video file.",
    )

    return parser.parse_args()


def _validate_args(args: argparse.Namespace):

    if not args.input_dir.is_dir():
        raise RuntimeError("Provided input directory does not exist.")

    if not args.output_dir.is_dir():
        raise RuntimeError("Provided output directory does not exist.")


def _main():
    args = _args()
    _validate_args(args)

    create_timelapse(
        source=args.input_dir,
        dest=args.output_dir,
        label=args.label,
        fps=args.fps,
        source_filetype=args.image_filetype,
    )


if __name__ == "__main__":
    _main()
