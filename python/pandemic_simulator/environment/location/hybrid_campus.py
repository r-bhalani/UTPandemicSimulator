# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from dataclasses import dataclass

from ..interfaces import NonEssentialBusinessLocationState, ContactRate, SimTimeTuple, NonEssentialBusinessBaseLocation

__all__ = ['HybridCampus', 'HybridCampusState']


# Classes/buildings that are no longer in-person during high COVID restriction stages
@dataclass
class HybridCampusState(NonEssentialBusinessLocationState):
    # student to student contact rate is much higher in college setting
    # because of lecture hall size and also people studying together
    contact_rate: ContactRate = ContactRate(5, 1, 0, 0.7, 0., 0.1)
    # students spend much longer time on campus
    open_time: SimTimeTuple = SimTimeTuple(hours=tuple(range(8, 18)), week_days=tuple(range(0, 5)))


class HybridCampus(NonEssentialBusinessBaseLocation[HybridCampusState]):
    """Implements a simple school"""

    state_type = HybridCampusState
