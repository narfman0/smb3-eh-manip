"""
We want to have a manip such that with a second or so upon reaching the map
with the hands, we provide an audio cue where the player only holds left to
go over the hands unscathed with a window of >2 frames (preferably 3).

The time wasted holding left is about 24 frames. The time to wait between
coming out of the pipe and holding left is ideally <30 frames.

This class watches for level changes and times when the hands should occur.
A higher level class should be keeping track of what levels we have beaten.
"""
import logging

from smb3_eh_manip.util import settings

INTRA_PIPE_DURATION = 197
POST_PIPE_TO_CONTROL_DURATION = 56
# When we go in the pipe before hands, we want to start calculating which
# is a good frame to hold left. This is the minimum time between entering
# the pipe and having control of mario on the overworld, minus pipe
# transition lag frames.
SECTION_TRIGGER_TO_OVERWORLD_CONTROL = (
    INTRA_PIPE_DURATION + POST_PIPE_TO_CONTROL_DURATION
)
# when holding left exiting the pipe, the frame# from origin to specific hand
TO_HAND1_CHECK_FRAME_DURATION = 18
TO_HAND2_CHECK_FRAME_DURATION = 40
TO_HAND3_CHECK_FRAME_DURATION = 17

# How many frames does the window have to be before pressing left?
# 3 is ideal if it happens within a second, otherwise 2 frames likely
LEFT_PRESS_WINDOW = settings.get_int("nohands_left_press_window", fallback=1)
# We cant look 10s in the future, so let's default this as a reasonable
# couple seconds or so.
MAXIMUM_FRAMES_TO_LOOK_FORWARD = settings.get_int(
    "nohands_max_frames_to_look_forward", fallback=120
)

# *: upon using the start/end pipe, identify frame windows in the
# second after exiting the pipe to trigger audio cue
# *: trigger audio cue :D

TRIGGER_SECTION_NAME = settings.get(
    "nohands_trigger_section_name", fallback="8 first pipe enter"
)


class NoHands:
    def section_completed(self, section, seed_lsfr):
        if section.name is TRIGGER_SECTION_NAME:
            candidate_frame_offsets = []
            lsfr = seed_lsfr.clone()
            lsfr.next_n(SECTION_TRIGGER_TO_OVERWORLD_CONTROL)
            current_window = 0
            for frame_offset in range(MAXIMUM_FRAMES_TO_LOOK_FORWARD):
                lsfr_experiment = lsfr.clone()
                lsfr_experiment.next_n(TO_HAND1_CHECK_FRAME_DURATION)
                breakpoint()
                if lsfr_experiment.hand_check():
                    current_window = 0
                    continue
                lsfr_experiment.next_n(TO_HAND2_CHECK_FRAME_DURATION)
                if lsfr_experiment.hand_check():
                    current_window = 0
                    continue
                lsfr_experiment.next_n(TO_HAND3_CHECK_FRAME_DURATION)
                if lsfr_experiment.hand_check():
                    current_window = 0
                    continue
                current_window += 1
                candidate_frame_offsets.append([frame_offset, current_window])
            return candidate_frame_offsets
