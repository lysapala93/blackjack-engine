import logging

# configure base logger
logger = logging.getLogger("blackjack")
logger.setLevel(logging.INFO)

# Console Handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Format for logs
formatter = logging.Formatter(
    "[%(asctime)s.%(msecs)03d]      [%(levelname)-8s]      %(filename)-24s| %(funcName)-27s:  %(lineno)-5d|   %(message)s"
)
ch.setFormatter(formatter)

# Handler zum Logger hinzufügen
logger.addHandler(ch)
