import logging

logging.basicConfig()
logger = logging.getLogger(__name__)


def set_debugging(debug):
    if debug:
        global logger
        logger = logging.getLogger("django")
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s:%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)


__all__ = ['logger']
