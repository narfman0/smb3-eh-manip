import logging
import time

import cv2
import numpy as np

from smb3_eh_manip.ui.video_player import VideoPlayer
from smb3_eh_manip.util import settings


class Opencv:
    def __init__(self):
        self.player_window_title = settings.get(
            "player_window_title", fallback="data/eh/video.avi"
        )
        self.start_frame_image_path = settings.get(
            "eh_start_frame_image_path", fallback="data/eh/trigger.png"
        )
        self.start_frame_image_region = settings.get_config_region(
            "eh_start_frame_image_region"
        )
        self.video_offset_frames = settings.get_int("video_offset_frames", fallback=106)
        self.latency_ms = settings.get_int("latency_ms")
        self.show_capture_video = settings.get_boolean("show_capture_video")
        self.write_capture_video = settings.get_boolean(
            "write_capture_video", fallback=False
        )
        self.enable_video_player = settings.get_boolean("enable_video_player")
        self.offset_ewma_read_frame = settings.get_boolean(
            "offset_ewma_read_frame", fallback=False
        )
        self.ewma_tick = 0
        self.ewma_read_frame = 0

        self.reset_template = cv2.imread(
            settings.get("reset_image_path", fallback="data/reset.png")
        )
        self.template = cv2.imread(self.start_frame_image_path)
        self.capture = cv2.VideoCapture(settings.get_int("video_capture_source"))
        if not self.capture.isOpened():
            raise Exception("Cannot open camera")
        if self.write_capture_video:
            path = settings.get("write_capture_video_path", fallback="capture.avi")
            fps = float(self.capture.get(cv2.CAP_PROP_FPS)) or 60
            height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.output_video = cv2.VideoWriter(
                path, cv2.VideoWriter_fourcc(*"MPEG"), fps, (width, height)
            )
        if self.enable_video_player:
            self.video_player = VideoPlayer(
                settings.get("eh_video_path", fallback="data/eh/video.avi"),
                self.video_offset_frames,
            )
        self.reset_image_region = settings.get_config_region("reset_image_region")

    def tick(self, last_tick_duration):
        start_read_frame = time.time()
        ret, frame = self.capture.read()
        read_frame_duration = time.time() - start_read_frame
        logging.debug(f"Took {read_frame_duration}s to read frame")
        self.ewma_tick = self.ewma_tick * 0.95 + last_tick_duration * 0.05
        self.ewma_read_frame = self.ewma_read_frame * 0.95 + read_frame_duration * 0.05
        if not ret:
            raise Exception("Can't receive frame (stream end?)")
        if self.write_capture_video:
            self.output_video.write(frame)
        self.frame = frame
        if self.show_capture_video:
            cv2.imshow("capture", frame)
        _ = cv2.waitKey(1)

    def should_autoreset(self):
        return list(
            Opencv.locate_all_opencv(
                self.reset_template, self.frame, region=self.reset_image_region
            )
        )

    def reset(self):
        if self.enable_video_player:
            self.video_player.reset()

    def should_start_playing(self):
        results = list(
            Opencv.locate_all_opencv(
                self.template, self.frame, region=self.start_frame_image_region
            )
        )
        if self.show_capture_video:
            for x, y, needleWidth, needleHeight in results:
                top_left = (x, y)
                bottom_right = (x + needleWidth, y + needleHeight)
                cv2.rectangle(self.frame, top_left, bottom_right, (0, 0, 255), 5)
        if results:
            logging.info(f"Detected start frame")
            return True
        return False

    def start_playing(self):
        if self.enable_video_player:
            self.video_player.play()

    def terminate(self):
        if self.enable_video_player:
            self.video_player.terminate()
        if self.write_capture_video:
            self.output_video.release()
        self.capture.release()
        cv2.destroyAllWindows()

    @classmethod
    def locate_all_opencv(
        cls,
        needleImage,
        haystackImage,
        limit=10000,
        region=None,  # [x, y, width, height]
        confidence=float(settings.get("confidence", fallback=0.95)),
    ):
        """
        RGBA images are treated as RBG (ignores alpha channel)
        """

        confidence = float(confidence)

        needleHeight, needleWidth = needleImage.shape[:2]

        if region:
            haystackImage = haystackImage[
                region[1] : region[1] + region[3], region[0] : region[0] + region[2]
            ]
        else:
            region = (0, 0)  # full image; these values used in the yield statement
        if (
            haystackImage.shape[0] < needleImage.shape[0]
            or haystackImage.shape[1] < needleImage.shape[1]
        ):
            # avoid semi-cryptic OpenCV error below if bad size
            raise ValueError(
                "needle dimension(s) exceed the haystack image or region dimensions"
            )

        # get all matches at once, credit: https://stackoverflow.com/questions/7670112/finding-a-subimage-inside-a-numpy-image/9253805#9253805
        result = cv2.matchTemplate(haystackImage, needleImage, cv2.TM_CCOEFF_NORMED)
        match_indices = np.arange(result.size)[(result > confidence).flatten()]
        matches = np.unravel_index(match_indices[:limit], result.shape)

        if len(matches[0]) == 0:
            return

        # use a generator for API consistency:
        matchx = matches[1] + region[0]  # vectorized
        matchy = matches[0] + region[1]
        for x, y in zip(matchx, matchy):
            yield (x, y, needleWidth, needleHeight)