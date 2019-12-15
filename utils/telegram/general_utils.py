import os
import re
import uuid

import requests

from blaster.definitions import TEMP_DIR
from blasterutils.generaltools import log_this, logger


@log_this
def parse_regex_command(string: str, prefix: str):
    if not isinstance(string, str) or not isinstance(prefix, str):
        raise ValueError("all args must be str")
    logger.debug(f"Parsing regex command: {string}")
    args = re.findall("\s(\d+)", string)
    target_id = None

    if not re.findall(f"/{prefix}(_)[A-z]", string):
        command = prefix
        parsed_for_id = re.findall(f"/{prefix}_(\d+)", string)
        if parsed_for_id:
            target_id = int(parsed_for_id[0])
    else:
        parsed_for_id = re.findall(f"/{prefix}_\S+_(\d+)", string)
        if parsed_for_id:
            target_id = int(parsed_for_id[0])
        if target_id:
            parsed_for_command = re.findall(f"/{prefix}_(\S+)_\d+", string)
        else:
            parsed_for_command = re.findall(f"/{prefix}_(\S+)", string)
        command = parsed_for_command[0]

    return command, target_id, args


@log_this
def download_file_from_url(url):
    logger.info("Downloading file from url")
    local_filename = os.path.join(TEMP_DIR, str(uuid.uuid4()))
    r = requests.get(url, stream=True)
    with open(local_filename, "wb") as f:
        f.write(r.content)
    return local_filename
