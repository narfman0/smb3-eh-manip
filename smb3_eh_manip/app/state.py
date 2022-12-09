from dataclasses import dataclass
import logging
from typing import Optional

from smb3_eh_manip.app.lsfr import LSFR
from smb3_eh_manip.app.nohands import NoHands
from smb3_eh_manip.util import events, settings, wizard_mixins


@dataclass
class Section:
    name: str
    lag_frames: Optional[int] = None
    trigger: Optional[str] = None
    complete_frame: Optional[int] = None


@dataclass
class Category(wizard_mixins.YAMLWizard):
    sections: list[Section]

    @classmethod
    def load(cls, category_name):
        return Category.from_yaml_file(f"data/categories/{category_name}.yml")


class State:
    def __init__(self, category_name=settings.get("category", fallback="nww")):
        self.category_name = category_name
        self.enable_nohands = settings.get_boolean("enable_nohands", fallback=False)
        self.nohands = NoHands() if self.enable_nohands else None
        self.reset()
        events.listen(events.LagFramesObserved, self.handle_lag_frames_observed)

    def handle_lag_frames_observed(self, event: events.LagFramesObserved):
        self.total_observed_lag_frames += event.observed_lag_frames
        self.total_observed_load_frames += event.observed_load_frames
        if self.check_expected_lag_condition(event):
            section = self.category.sections.pop(0)
            logging.info(f"Completed {section.name}")
            self.check_and_update_nohands(event.current_frame, section)

    def check_complete_frame_condition(self, current_frame):
        active_section = self.active_section()
        if not active_section:
            return False
        complete_frame = active_section.complete_frame
        return complete_frame and complete_frame <= current_frame

    def check_expected_lag_condition(self, event: events.LagFramesObserved):
        active_section = self.active_section()
        if not active_section:
            return False
        expected_section_lag = self.active_section().lag_frames
        return (
            expected_section_lag
            and expected_section_lag >= event.observed_load_frames - 1
            and expected_section_lag <= event.observed_load_frames + 1
        )

    def check_and_update_nohands(self, current_frame, section):
        if not self.enable_nohands or section.trigger != "nohands":
            return
        nohands_window = self.nohands.calculate_optimal_window(
            section, self.lsfr.clone()
        )
        if not nohands_window:
            return
        action_frame = round(current_frame + nohands_window.action_frame)
        events.emit(self, events.AddActionFrame(action_frame, nohands_window.window))
        logging.info(
            f"NoHands at frame: {action_frame} with window: {nohands_window.window}"
        )

    def tick(self, current_frame):
        # we need to see how much time has gone by and increment RNG that amount
        lsfr_increments = (
            int(current_frame)
            - self.lsfr_frame
            - self.total_observed_lag_frames
            - self.total_observed_load_frames
        )
        self.lsfr.next_n(lsfr_increments)
        self.lsfr_frame += lsfr_increments

        if self.check_complete_frame_condition(current_frame):
            section = self.category.sections.pop(0)
            logging.debug(f"Completed {section.name}")
            self.check_and_update_nohands(current_frame, section)

    def reset(self):
        self.total_observed_lag_frames = 0
        self.total_observed_load_frames = 0
        self.lsfr_frame = 12
        self.category = Category.load(self.category_name)
        self.lsfr = LSFR()

    def active_section(self):
        if not self.category.sections:
            return None
        return self.category.sections[0]