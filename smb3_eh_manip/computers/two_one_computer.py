from smb3_eh_manip.video_player import VideoPlayer
from smb3_eh_manip.computers.opencv_computer import OpencvComputer
from smb3_eh_manip.settings import config


class TwoOneComputer(OpencvComputer):
    def __init__(self):
        super().__init__(
            VideoPlayer(
                "video",
                config.get("app", "two_one_video_path"),
                config.getint("app", "latency_frames"),
            )
            if config.getboolean("app", "enable_video_player")
            else None,
            config.get("app", "two_one_start_frame_image_path"),
        )