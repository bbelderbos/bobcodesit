"""
Script to post new code snippets bobcodesit repo -> Codeimag.es API
"""
import datetime
import os
import pathlib
import sys
import typing

import dotenv
import requests

dotenv.load_dotenv()

CODEIMAGES_USER = os.environ["CODEIMAGES_USER"]
CODEIMAGES_PASSWORD = os.environ["CODEIMAGES_PASSWORD"]
DEBUG = os.environ.get("DEBUG", False)
LIVE_SITE = "https://pybites-codeimages.herokuapp.com"
BASE_URL = "http://localhost:8000" if DEBUG else LIVE_SITE
TOKEN_URL = f"{BASE_URL}/token"
CREATE_TIP_URL = f"{BASE_URL}/create"
TIPS_DIR = pathlib.Path("notes")


class Tip(typing.NamedTuple):
    title: str
    description: str
    code: str


def get_token(user, password):
    """
    Perform authentication against CodeImages API obtaining an access
    token which can be used to make post requests (create tip images).
    """
    payload = {"username": user, "password": password}
    resp = requests.post(TOKEN_URL, data=payload)
    data = resp.json()

    if "access_token" not in data:
        sys.exit(data["detail"])

    return data["access_token"]


def _extract_dt(tip_file: pathlib.Path) -> datetime.datetime:
    """
    Get a relative note md file path and convert the file name, which
    is a timestamp, to a datetime.
    """
    return datetime.datetime.strptime(tip_file.stem, "%Y%m%d%H%M%S")


def get_latest_tips(
    *, look_hours_back: int = 24, tips_dir: pathlib.Path = TIPS_DIR
) -> list[pathlib.Path]:
    """
    Looks at notes directory and retrieves the md note files that were
    made in the last 24 hours (or whatever look_hours_back gets set to)
    """
    goback_limit = datetime.datetime.now() - datetime.timedelta(hours=look_hours_back)
    latest_tips = [
        tip_file
        for tip_file in tips_dir.glob("*.md")
        if _extract_dt(tip_file) >= goback_limit
    ]
    return latest_tips


def parse_tip_file(tip_file: pathlib.Path) -> Tip:
    """
    A tip note file is structured like this:
    # title

    Description (usually single line, could be more) ...

    ```
    code block
    ```

    #one_or_more_tags
    """
    lines = tip_file.read_text().splitlines()
    title = lines[0].lstrip("# ")
    start_description_line = 2

    code_block_indices = [i for i, line in enumerate(lines) if line.strip() == "```"]
    if code_block_indices:
        # if there are multiple code blocks, take the first one
        if len(code_block_indices) > 2:
            code_block_indices = code_block_indices[:2]

        start_line, end_line = code_block_indices

        description = "\n".join(lines[start_description_line:start_line]).strip()
        code = "\n".join(lines[start_line + 1: end_line]).strip()
    else:
        description = "\n".join(lines[start_description_line:len(lines)]).strip()
        code = ""

    return Tip(title=title, description=description, code=code)


def main(args):
    try:
        user, password, *_ = args
    except ValueError:
        user, password = CODEIMAGES_USER, CODEIMAGES_PASSWORD

    token = get_token(user, password)
    headers = {"Authorization": f"Bearer {token}"}

    latest_tips = get_latest_tips()

    for tip_file in latest_tips:
        tip = parse_tip_file(tip_file)

        payload = {
            "title": tip.title,
            "code": tip.code,
            "description": tip.description,
        }

        print(f"Posting tip {tip.title}")
        response = requests.post(CREATE_TIP_URL, json=payload, headers=headers)
        print(f"API response code: {response.status_code}")

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            print(f"Error: {exc}")
        else:
            print("OK")


if __name__ == "__main__":
    main(sys.argv[1:])
