#!/usr/bin/env python3

import logging

import typer

from .cache import Cache
from .feed import feed_factory
from .logger import get_logger
from .notifier import notifier_factory
from .settings import get_settings

LOGGER = get_logger()


def main(
    settings_path: str = typer.Option(..., envvar="SFN_APP_SETTINGS_PATH"),
    debug: bool = typer.Option(False, envvar="SFN_APP_DEBUG"),
):
    settings = get_settings(settings_path)

    if debug or settings["debug"]:
        LOGGER.setLevel(logging.DEBUG)

    LOGGER.debug("Loaded settings from %s", settings_path)

    cache = Cache(path=settings["cache_path"])

    for name, feed_class in feed_factory.items():
        feed_url = settings["feeds"].get(name, {}).get("url")
        feed = feed_class(url=feed_url, cache=cache)
        item = feed.get(index=0)

        if not item:
            LOGGER.warn("No items found in %s", feed_url)
            continue

        LOGGER.debug(f"found {item.title}")

        for name, notifier_class in notifier_factory.items():
            notifier_url = settings["notifiers"].get(name, {}).get("url")
            notifier = notifier_class(url=notifier_url, cache=cache)
            notifier.send(item)


def run():
    typer.run(main)


if __name__ == "__main__":
    run()
