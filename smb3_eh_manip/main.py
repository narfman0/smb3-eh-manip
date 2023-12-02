import logging
import time
from signal import signal, SIGINT
import cProfile
import pstats

from pygrabber.dshow_graph import FilterGraph

from smb3_eh_manip.app.controller import Controller
from smb3_eh_manip.util.logging import initialize_logging
from smb3_eh_manip.util import settings

LOGGER = logging.getLogger(__name__)
VERSION = open("data/version.txt", "r").read().strip()


def handler(_signum, _frame):
    global controller
    print("SIGINT or CTRL-C detected. Exiting gracefully")
    controller.terminate()
    controller = None


def print_camera_info():
    graph = FilterGraph()
    input_devices = graph.get_input_devices()
    video_capture_source = settings.get_int("video_capture_source")
    if video_capture_source == -1 or video_capture_source >= len(input_devices):
        LOGGER.info("No camera selected or invalid, please update to one of the below:")
        LOGGER.info(input_devices)
        exit()
    LOGGER.info(f"Selected video source: {input_devices[video_capture_source]}")


def main():
    global controller
    signal(SIGINT, handler)
    initialize_logging()
    LOGGER.info(f"Starting smb3 manip tool version {VERSION}")
    print_camera_info()
    with cProfile.Profile() as pr:
        try:
            controller = Controller()
            last_tick_duration = -1
            while controller is not None:
                start_time = time.time()
                controller.tick(last_tick_duration)
                last_tick_duration = time.time() - start_time
                LOGGER.debug(f"Took {last_tick_duration}s to tick")
        except:
            logging.exception("main handler exception")
            raise
        pr.print_stats()
        pr.dump_stats("stats.log")


if __name__ == "__main__":
    main()
