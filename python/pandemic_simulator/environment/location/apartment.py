# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from dataclasses import dataclass

from ..interfaces import LocationState, ContactRate, SimTime, SimTimeTuple, LocationRule, globals, BaseLocation

__all__ = ['Apartment', 'ApartmentState']


@dataclass
class ApartmentState(LocationState):
    contact_rate: ContactRate = ContactRate(1, 1, 1, 0.7, 0.7, 0.7)
    visitor_time = SimTimeTuple(hours=tuple(range(19, 24)), days=tuple(globals.numpy_rng.randint(4, 365, 12)))


class Apartment(BaseLocation[ApartmentState]):
    state_type = ApartmentState

    def sync(self, sim_time: SimTime) -> None:
        super().sync(sim_time)
        self._state.social_gathering_event = sim_time in self._state.visitor_time

    def update_rules(self, new_rule: LocationRule) -> None:
        pass
