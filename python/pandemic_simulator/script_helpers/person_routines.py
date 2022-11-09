# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

"""This helper module contains a few standard routines for persons in the simulator."""

from typing import Sequence, Type

from ..environment import LocationID, PersonRoutine, HairSalon, Party, Restaurant, Bar, \
    GroceryStore, RetailStore, triggered_routine, weekend_routine, social_routine, mid_day_during_week_routine, \
    PersonRoutineAssignment, Person, Student, Faculty, Location

__all__ = ['DefaultPersonRoutineAssignment']

"""
References:
https://www.touchbistro.com/blog/how-diners-choose-restaurants/

"""


class DefaultPersonRoutineAssignment(PersonRoutineAssignment):
    """A default person routine assignment"""

    @property
    def required_location_types(self) -> Sequence[Type[Location]]:
        return HairSalon, Restaurant, Bar, GroceryStore, RetailStore

    @staticmethod
    def get_student_routines(home_id: LocationID, age: int) -> Sequence[PersonRoutine]:
        routines = [
            # triggered_routine(home_id, HairSalon, 30),
            # weekend_routine(home_id, Restaurant, explore_probability=0.5),
            triggered_routine(None, GroceryStore, 7),
            triggered_routine(None, RetailStore, 7),

            # For social locations -> increased explore probability 
            triggered_routine(None, Restaurant, 3, explore_probability=0.75),
            weekend_routine(home_id, Bar, explore_probability=0.6),
            weekend_routine(home_id, Party, explore_probability=0.8),
            social_routine(home_id)
        ]
        return routines


    @staticmethod
    def get_faculty_during_work_routines(work_id: LocationID) -> Sequence[PersonRoutine]:
        routines = [
            mid_day_during_week_routine(work_id, Restaurant),  # ~cafeteria  during work
        ]

        return routines

    @staticmethod
    def get_faculty_outside_work_routines(home_id: LocationID) -> Sequence[PersonRoutine]:
        routines = [
            triggered_routine(None, GroceryStore, 7),
            triggered_routine(None, RetailStore, 7),
            weekend_routine(None, Restaurant, explore_probability=0.7),
            triggered_routine(home_id, Bar, 3, explore_probability=0.5),
            social_routine(home_id)
        ]
        return routines

    def assign_routines(self, persons: Sequence[Person]) -> None:
        for p in persons:
            if isinstance(p, Student):
                p.set_outside_school_routines(self.get_student_routines(p.home, p.id.age))
            elif isinstance(p, Faculty):
                p.set_during_work_routines(self.get_faculty_during_work_routines(p.work))
                p.set_outside_work_routines(self.get_faculty_outside_work_routines(p.home))
