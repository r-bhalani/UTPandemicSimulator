
from dataclasses import dataclass

from ..interfaces import LocationState, ContactRate, SimTime, SimTimeTuple, LocationRule, globals, BaseLocation

__all__ = ['Dorm', 'DormState']


@dataclass
class DormState(LocationState):
    # contact_rate is (x,y,z) where x is worker to worker, y is worker to visitor, and z is visitor to visitor
    # for dorm, contact rate for x, dorm resident to dorm resident, is much higher
    # for y, dorm resident to non dorm resident would also be high because of eating at the dining hall
    contact_rate: ContactRate = ContactRate(0, 1, 0, 0.9, 0.7, 0.3)
    visitor_time = SimTimeTuple(hours=tuple(range(19, 24)), days=tuple(globals.numpy_rng.randint(4, 365, 12)))


class Dorm(BaseLocation[DormState]):
    """Class that implements a standard Dorm location. """
    state_type = DormState

    def sync(self, sim_time: SimTime) -> None:
        super().sync(sim_time)
        self._state.social_gathering_event = sim_time in self._state.visitor_time

    def update_rules(self, new_rule: LocationRule) -> None:
        pass
