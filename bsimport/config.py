"""This module generates the config file for bsimport."""
# bsimport/config.py

import configparser
import typer

from pathlib import Path
from typing import List, Optional, Tuple

from bsimport import (
    CONF_WRITE_ERROR, CONF_DIR_ERROR, CONF_FILE_ERROR,
    EMPTY_FILE_ERROR, NO_FILE_ERROR,
    SUCCESS, __app_name__
)


# Returns /home/user/.config/rptodo
CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"


def init_app(
    id: str,
    secret: str,
    url: str
) -> Tuple[int, str]:

    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
        return CONF_DIR_ERROR, ""

    try:
        CONFIG_FILE_PATH.touch(exist_ok=True)
    except OSError:
        return CONF_FILE_ERROR, ""

    if not url.startswith('http'):
        url = f"http://{url}"

    config_parser = configparser.ConfigParser()
    config_parser['General'] = {
        'token_id': id,
        'token_secret': secret,
        'url': url
    }

    try:
        with CONFIG_FILE_PATH.open('w') as file:
            config_parser.write(file)
    except OSError:
        return CONF_WRITE_ERROR, ""
    return SUCCESS, str(CONFIG_FILE_PATH)


def read_config() -> Tuple[int, List[str]]:

    if not CONFIG_FILE_PATH.exists():
        return NO_FILE_ERROR, []

    config = configparser.ConfigParser()

    config.read(CONFIG_FILE_PATH)

    try:
        gen = config['General']
    except KeyError:
        return EMPTY_FILE_ERROR, []

    id = gen['token_id']
    secret = gen['token_secret']
    url = gen['url']

    return SUCCESS, [id, secret, url]


def modify_config(
    id: Optional[str],
    secret: Optional[str],
    url: Optional[str]
) -> Tuple[int, str]:
    """
    Update the config file.

    :param id:
        The token ID.
    :type id: Optional[str]
    :param secret:
        The token secret.
    :type secret: Optional[str]
    :param url:
        The instance's URL.
    :type url: Optional[str]

    :return:
        A return code and a message to the user.
    :rtype: int
    """

    if not CONFIG_FILE_PATH.exists():
        return NO_FILE_ERROR, ""

    config = configparser.ConfigParser()

    config.read(CONFIG_FILE_PATH)

    res = "Successfully updated "
    items = list()

    if id:
        config['General']['token_id'] = id
        items.append("id")
    if secret:
        config['General']['token_secret'] = secret
        items.append("secret")
    if url:
        config['General']['url'] = url
        items.append("url")

    res += ", ".join(items)

    try:
        with CONFIG_FILE_PATH.open('w') as file:
            config.write(file)
    except OSError:
        return CONF_WRITE_ERROR, ""

    return SUCCESS, res
