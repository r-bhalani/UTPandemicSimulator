# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from dataclasses import dataclass

from ..interfaces import NonEssentialBusinessLocationState, ContactRate, SimTimeTuple, NonEssentialBusinessBaseLocation

__all__ = ['Campus', 'CampusState']


@dataclass
class CampusState(NonEssentialBusinessLocationState):
    # student to student contact rate is much higher in college setting
    # because of lecture hall size and also people studying together
    contact_rate: ContactRate = ContactRate(10, 5, 5, 0.7, 0.5, 0.5)
    # students spend much longer time on campus
    open_time: SimTimeTuple = SimTimeTuple(hours=tuple(range(8, 18)), week_days=tuple(range(0, 5)))


class Campus(NonEssentialBusinessBaseLocation[CampusState]):
    """Implements a simple school"""

    state_type = CampusState
