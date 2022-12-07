from dataclasses import dataclass
import logging

from smb3_eh_manip.app.lsfr import LSFR
from smb3_eh_manip.app.nohands import NoHands
from smb3_eh_manip.util import events, settings, wizard_mixins


@dataclass
class Section:
    name: str
    lag_frames: int


@dataclass
class Category(wizard_mixins.YAMLWizard):
    sections: list[Section]

    @classmethod
    def load(cls, category_name=settings.get("category", fallback="nww")):
        return Category.from_yaml_file(f"data/categories/{category_name}.yml")


class State:
    def __init__(self):
        self.nohands = NoHands()
        self.reset()
        events.listen(events.LagFramesObserved, self.handle_lag_frames_observed)

    def handle_lag_frames_observed(self, event: events.LagFramesObserved):
        self.total_observed_lag_frames += event.observed_lag_frames
        self.total_observed_load_frames += event.observed_load_frames
        if not self.category.sections:
            return
        expected_lag = self.active_section().lag_frames
        if (
            expected_lag >= event.observed_load_frames - 1
            and expected_lag <= event.observed_load_frames + 1
        ):
            section = self.category.sections.pop(0)
            logging.info(f"Completed {section.name}")
            if settings.get_boolean("nohands", fallback=False):
                optimal_action_frame_offset = self.nohands.section_completed(
                    section, self.lsfr.clone()
                )
                if optimal_action_frame_offset:
                    action_frame = round(
                        event.current_frame + optimal_action_frame_offset[0]
                    )
                    events.emit(
                        events.AddActionFrame,
                        self,
                        event=events.AddActionFrame(action_frame),
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

    def reset(self):
        self.total_observed_lag_frames = 0
        self.total_observed_load_frames = 0
        self.lsfr_frame = 12
        self.category = Category.load()
        self.lsfr = LSFR()

    def active_section(self):
        return self.category.sections[0]
