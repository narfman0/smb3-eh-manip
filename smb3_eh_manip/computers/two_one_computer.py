from smb3_eh_manip.computers.opencv_computer import OpencvComputer
from smb3_eh_manip import settings


class TwoOneComputer(OpencvComputer):
    def __init__(self):
        super().__init__(
            "twoonevideo",
            settings.get("two_one_video_path", fallback="data/two_one/video.mp4"),
            settings.get(
                "two_one_start_frame_image_path", fallback="data/two_one/trigger.png"
            ),
        )
