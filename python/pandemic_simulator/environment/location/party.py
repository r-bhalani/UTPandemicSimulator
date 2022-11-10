from dataclasses import dataclass

from ..interfaces import LocationState, ContactRate, SimTime, SimTimeTuple, LocationRule, globals, BaseLocation

__all__ = ['Party', 'PartyState']


@dataclass
class PartyState(LocationState):
    contact_rate: ContactRate = ContactRate(30, 30, 30, 0.9, 0.9, 0.9)
    visitor_time = SimTimeTuple(hours=tuple(range(22, 4)), days=tuple(globals.numpy_rng.randint(5, 365, 12)))
    social_gathering_event: bool = True


class Party(BaseLocation[PartyState]):
    state_type = PartyState

    def sync(self, sim_time: SimTime) -> None:
        super().sync(sim_time)
        self._state.social_gathering_event = sim_time in self._state.visitor_time

    def update_rules(self, new_rule: LocationRule) -> None:
        pass