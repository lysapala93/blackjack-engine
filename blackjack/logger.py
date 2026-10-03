import logging

# configure base logger
logger = logging.getLogger("blackjack")
# Level stays unset so the effective level is inherited from the root logger.
# This lets tools such as pytest (`--log-level=DEBUG`) control verbosity.
logger.setLevel(logging.NOTSET)

# Console Handler
ch = logging.StreamHandler()
ch.setLevel(logging.NOTSET)

# Format for logs
formatter = logging.Formatter(
    "[%(asctime)s.%(msecs)03d]      [%(levelname)-8s]      %(filename)-24s| %(funcName)-27s:  %(lineno)-5d|   %(message)s"
)
ch.setFormatter(formatter)

# Handler zum Logger hinzufügen
logger.addHandler(ch)

DEFAULT_LEVEL = logging.INFO


def configure_logging(level: int | str = DEFAULT_LEVEL) -> None:
    """Pin the ``blackjack`` logger to an explicit level.

    Applications (such as the CLI) call this on start-up. Library and test
    usage should leave it alone so the root logger level applies.
    """
    logger.setLevel(level)
