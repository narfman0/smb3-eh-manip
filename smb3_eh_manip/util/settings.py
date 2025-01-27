from configparser import ConfigParser
import logging

LOGGER = logging.getLogger(__name__)
config = ConfigParser()
result = config.read("config.ini")
if not result:
    LOGGER.warning("Failed to read config.ini! Using sample.")
    config.read("config.ini.sample")

DEFAULT_DOMAIN = "app"
NES_FRAMERATE = config.getfloat(DEFAULT_DOMAIN, "nes_framerate", fallback=60.0988139)
NES_MS_PER_FRAME = 1000.0 / NES_FRAMERATE
FREQUENCY = 24


def get(name, domain=DEFAULT_DOMAIN, fallback=None):
    return config.get(domain, name, fallback=fallback)


def get_boolean(name, domain=DEFAULT_DOMAIN, fallback=None):
    return config.getboolean(domain, name, fallback=fallback)


def get_int(name, domain=DEFAULT_DOMAIN, fallback=None):
    return config.getint(domain, name, fallback=fallback)


def get_float(name, domain=DEFAULT_DOMAIN, fallback=None):
    return config.getfloat(domain, name, fallback=fallback)


def get_config_region(name, domain=DEFAULT_DOMAIN, fallback=None):
    """Parse a region str from ini"""
    return get_list(name, domain=domain, fallback=fallback)


def get_frame_windows(name, domain=DEFAULT_DOMAIN, fallback=None):
    """Parse a frame windows str from ini"""
    frame_windows = config.get(domain, name, fallback=fallback)
    if frame_windows:
        return list(
            map(lambda str: list(map(int, str.split("-"))), frame_windows.split(","))
        )
    return None


def get_list(name, domain=DEFAULT_DOMAIN, fallback=None):
    """Parse a region str from ini"""
    list_str = config.get(domain, name, fallback=fallback)
    if list_str:
        return list(map(int, list_str.split(",")))
    return None


def get_action_frames():
    frames = get_list("eh_action_frames")
    return (
        frames
        if frames
        else [
            270,
            390,
            510,
            1925,
            15880,
            16000,
            16120,
            16876,
            18046,
            18654,
            19947,
            20611,
            22669,
        ]
    )


def set(name, value, domain=DEFAULT_DOMAIN):
    return config.set(domain, name, value)


ACTION_FRAMES = get_action_frames()
