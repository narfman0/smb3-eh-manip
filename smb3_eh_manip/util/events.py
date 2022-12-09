"""
Helper class for eventing. Currently unused.
"""
from dataclasses import asdict, dataclass
import logging

from pydispatch import dispatcher


@dataclass
class LagFramesObserved:
    current_frame: int
    observed_lag_frames: int
    observed_load_frames: int


@dataclass
class AddActionFrame:
    action_frame: int
    window: int


def listen(event_type, callback, **kwargs):
    # Listen to all events with event_type
    dispatcher.connect(callback, signal=event_type, **kwargs)


def emit(sender, event, **kwargs):
    # Emit an event with the given event_type
    logging.debug(f"Emitting {type(event).__name__} event: {asdict(event)}")
    dispatcher.send(type(event), sender, event=event, **kwargs)