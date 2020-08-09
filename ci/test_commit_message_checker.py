"""Module for testing the commit message linter"""
import pytest
from check_commit_message import check_message, LintingError


APPROVED = [
    """This is a header. Nothing else.""",
    """This is a header.

This is the body of the commit message.
It has another line here.""",
]

NOT_APPROVED = [
    """This is a header with trailing whitespace """,
    """This is a header that is too long""" * 3,
    """fixup! Original commit header""",
]


def test_approved_messages():
    """Check that approved messages pass the checks"""
    for message in APPROVED:
        check_message(message)


def test_not_approved_message():
    """Check that not-approved messages fail the checks"""
    for message in NOT_APPROVED:
        with pytest.raises(LintingError):
            check_message(message)
