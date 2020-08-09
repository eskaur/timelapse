"""Module for commit message linting based on Github context"""
import re
from typing import Dict
from .github_utils import get_commit_messages_from_github_env


RULES = {
    "all": [
        {
            "pattern": r"fixup!",
            "required_match_result": False,
            "description": "Please squash all fixup commits",
        },
        {
            "pattern": r"^.{73}",
            "required_match_result": False,
            "description": "Please keep normal lines at 72 characters or less",
        },
        {
            "pattern": r"\s$",
            "required_match_result": False,
            "description": "Please remove all trailing whitespace",
        },
    ],
    "header": [
        {
            "pattern": r"^[A-Z]",
            "required_match_result": True,
            "description": "Header must start with a capital letter",
        },
        {
            "pattern": r"\.$",
            "required_match_result": False,
            "description": "Header may not end with a period",
        },
    ],
}

# Line blocks starting and ending with lines matching this are not checked:
EXEMPTION_BLOCK_PATTERN = r"^```"
# Lines matching one of these patterns are not checked:
EXEMPTION_PATTERNS = [r"^\w+:\/\/"]


class LintingError(Exception):
    """Class for signaling failed linting"""


def _check_structure(message: str) -> None:

    lines = message.split("\n")

    if len(lines) <= 2:
        raise LintingError("Message must have at least three lines")
    if not lines[0].strip():
        raise LintingError("First line cannot be empty.")
    if lines[1].strip():
        raise LintingError("Second line must be empty.")
    if not lines[2].strip():
        raise LintingError("Third line cannot be empty.")

    if not lines[-1].strip():
        raise LintingError("Final line cannot be empty.")


def _check_line(line: str, rule: Dict) -> None:

    for exemption_pattern in EXEMPTION_PATTERNS:
        if re.search(exemption_pattern, line):
            # Line is exempt from further checks
            break
    else:
        is_match = re.search(rule["pattern"], line) is not None
        if is_match != rule["required_match_result"]:
            raise LintingError(
                f'Linting error!\n{rule["description"]}\nOffending line: "{line}"'
            )


def check_message(message: str) -> None:
    """Check commit message according to rules

    Will raise LintingError if the message is to approved.
    """
    print("-" * 72)
    print("Checking the following commit message:")
    print("-" * 72)
    print(message)
    print("-" * 72)

    _check_structure(message)
    lines = message.split("\n")

    for rule in RULES["header"]:
        _check_line(lines[0], rule)

    do_check = True
    try:
        for rule in RULES["all"]:
            for line in lines:
                if re.search(EXEMPTION_BLOCK_PATTERN, line) is not None:
                    do_check = not do_check
                if do_check:
                    _check_line(line, rule)
    except LintingError:
        print("Not accepted!")
        raise
    else:
        print("OK")


def test_commit_messages_from_github_env() -> None:
    """Test all commit messages based on Github context"""

    print("-" * 72)
    print("Entering commit message checker")
    messages = get_commit_messages_from_github_env()
    print(f"Found {len(messages)} commit message(s) to check.")

    for message in messages:
        check_message(message)
