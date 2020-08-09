"""Module for Github utilities"""

import json
import os
from typing import Dict, List
from urllib.request import Request, urlopen


def _get_commit_messages_from_pull_request(github_context: Dict) -> List[str]:
    url = github_context["event"]["pull_request"]["commits_url"]
    token = github_context["token"]
    request = Request(url)
    request.add_header("Authorization", f"token {token}")
    response = json.loads(urlopen(request).read())
    return [item["commit"]["message"] for item in response]


def _get_commit_messages_from_push(github_context: Dict) -> List[str]:
    return [commit["message"] for commit in github_context["event"]["commits"]]


def get_commit_messages_from_github_env() -> List[str]:
    """Get commit messages based on env var GITHUB_CONTEXT"""

    github_context = json.loads(os.environ["GITHUB_CONTEXT"])
    event_name = github_context["event_name"]
    if event_name == "pull_request":
        return _get_commit_messages_from_pull_request(github_context)
    if event_name == "push":
        return _get_commit_messages_from_push(github_context)
    raise RuntimeError(f"Unexpected event type: {event_name}")
