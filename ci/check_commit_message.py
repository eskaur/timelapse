"""Module for commit message linting based on Github context"""
import os
import json
import re
import sys
from typing import List, Dict
from urllib.request import Request, urlopen


RULES = {
    "all": [
        {
            "pattern": r"fixup!",
            "required_result": False,
            "description": "Please squash all fixup commits",
        },
        {
            "pattern": r"^.{73}",
            "required_result": False,
            "description": "Please keep all lines at 72 characters or less",
        },
        {
            "pattern": r"\s$",
            "required_result": False,
            "description": "Please remove all trailing whitespace",
        },
    ]
}


def _get_commit_messages_from_pull_request(github_context: Dict) -> List[str]:
    url = github_context["event"]["pull_request"]["commits_url"]
    token = github_context["token"]
    request = Request(url)
    request.add_header("Authorization", f"token {token}")
    response = json.loads(urlopen(request).read())
    return [item["commit"]["message"] for item in response]


def _get_commit_messages_from_push(github_context: Dict) -> List[str]:
    return [commit["message"] for commit in github_context["event"]["commits"]]


def _get_commit_messages_from_github_env() -> List[str]:
    github_context = json.loads(os.environ["GITHUB_CONTEXT"])
    event_name = github_context["event_name"]
    if event_name == "pull_request":
        return _get_commit_messages_from_pull_request(github_context)
    if event_name == "push":
        return _get_commit_messages_from_push(github_context)
    raise RuntimeError(f"Unexpected event type: {event_name}")


class LintingError(Exception):
    """Class for signaling failed linting"""


def _check_line(line: str, rule: Dict) -> None:
    is_match = re.search(rule["pattern"], line) is not None
    if is_match != rule["required_result"]:
        raise LintingError(
            f'Linting error!\n{rule["description"]}\nOffending line: "{line}"'
        )


def check_message(message: str) -> None:
    """Check commit message according to rules

    Will raise LintingError if the message is to approved.
    """
    print("-" * 70)
    print("Checking the following commit message:")
    print("-" * 70)
    print(message)
    print("-" * 70)

    all_lines = message.split("\n")
    try:
        for rule in RULES["all"]:
            for line in all_lines:
                _check_line(line, rule)
    except LintingError:
        print("Not accepted!")
        raise
    else:
        print("OK")


def _main() -> None:
    print("-" * 70)
    print("Entering commit message checker")
    messages = _get_commit_messages_from_github_env()
    print(f"Found {len(messages)} commit message(s) to check.")

    try:
        for message in messages:
            check_message(message)
    except LintingError as ex:
        print("*" * 70)
        print(str(ex))
        print("*" * 70)
        sys.exit("Linting failed!")


if __name__ == "__main__":
    _main()
