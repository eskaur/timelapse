"""Module for testing the commit message linter"""
from pathlib import Path
from typing import List
import pytest
from .check_commit_message import check_message, LintingError


def _get_messages_from_file(file_name: str) -> List[str]:

    separator = "\n" + "*" * 72 + "\n"
    file_path = Path(__file__).parent / file_name
    with open(file_path, "r") as file_obj:
        messages = file_obj.read().split(separator)
    return messages


def test_approved_messages():
    """Check that approved messages pass the checks"""

    messages = _get_messages_from_file("approved_commit_messages.txt")
    print(f"Found {len(messages)} approved messages to check")
    assert len(messages) == 4, "Did not find the expected number of examples"

    for message in messages:
        check_message(message)


def test_disapproved_messages():
    """Check that disapproved messages fail the checks"""

    messages = _get_messages_from_file("disapproved_commit_messages.txt")
    print(f"Found {len(messages)} disapproved messages to check")
    assert len(messages) == 13, "Did not find the expected number of examples"

    for message in messages:
        with pytest.raises(LintingError):
            check_message(message)
