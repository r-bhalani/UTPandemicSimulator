# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from typing import List, cast
from uuid import uuid4

import numpy as np
import random

from .interfaces import globals, Risk, Person, PersonID, PersonState, BusinessBaseLocation
from .job_counselor import JobCounselor
from .location import Apartment, Campus, Dorm, HybridCampus
from .person import Faculty, Student
from .simulator_config import PandemicSimConfig
from ..utils import cluster_into_random_sized_groups

__all__ = ['make_population']

age_group = range(2, 101)
students_age_group = range(18, 24)
faculty_age_group = range(25, 90)

def get_us_age_distribution(num_persons: int) -> List[int]:
    age_p = np.zeros(100)
    for i, age in enumerate(age_group):
        if age < 60:
            age_p[i] = globals.numpy_rng.normal(1, 0.05)
        else:
            age_p[i] = (1 + (age - 60) * (0.05 - 1) / (100 - 60)) * globals.numpy_rng.normal(1, 0.05)
    age_p /= np.sum(age_p)
    ages = [int(globals.numpy_rng.choice(np.arange(1, 101), p=age_p)) for _ in range(num_persons)]
    # print(f'Average age: {np.average(ages)}')
    return ages

# Students are uniformly distributed across all ages
def get_students_age_distribution(num_students: int) -> List[int]:
    ages = [int(globals.numpy_rng.choice(np.arange(18, 24))) for _ in range(num_students)]
    return ages

# Faculty is distributed normally across the ages of 25 -> 90
def get_faculty_age_distribution(num_faculty: int) -> List[int]:
    age_p = np.zeros(65)
    for i, age in enumerate(faculty_age_group):
        if age < 60:
            age_p[i] = globals.numpy_rng.normal(1, 0.05)
        else:
            age_p[i] = (1 + (age - 60) * (0.05 - 1) / (90 - 60)) * globals.numpy_rng.normal(1, 0.05)
    age_p /= np.sum(age_p)
    ages = [int(globals.numpy_rng.choice(np.arange(25, 90), p=age_p)) for _ in range(num_faculty)]
    # print(f'Average age: {np.average(ages)}')
    return ages

def get_university_age_distribution(num_students: int, num_faculty: int) -> List[int]:
    student_ages = get_students_age_distribution(num_students)
    faculty_ages = get_faculty_age_distribution(num_faculty)
    return np.vstack((student_ages, faculty_ages))

def infection_risk(age: int) -> Risk:
    # if age <= 24:
    #     return cast(Risk,
    #             globals.numpy_rng.choice([Risk.LOW, Risk.HIGH], p=[1 - age / students_age_group.stop, age / students_age_group.stop]))
    # else:
    return cast(Risk,
                globals.numpy_rng.choice([Risk.LOW, Risk.HIGH], p=[1 - age / faculty_age_group.stop, age / faculty_age_group.stop]))


def make_population(sim_config: PandemicSimConfig) -> List[Person]:
    """
    Creates a realistic us-age distributed population with home assignment and returns a list of persons.

    The overview of home assignment is as follows:

    a) "Only 4.5 percent of older adults live in nursing homes and
    2 percent in assisted living facilities. The majority of older adults (93.5 percent) live in the community."
    - https://www.ncbi.nlm.nih.gov/books/NBK51841/

    Select 6.5% of older adults (age > 65) and cluster them as groups of 1 or 2 and assign each
    group to a nursing home.

    b) "In 2019, there was an average of 1.93 children under 18 per family in the United States"
    - https://www.statista.com/statistics/718084/average-number-of-own-children-per-family/

    Cluster minors into 1-3 sized uniform groups and assign each group to a non-nursing home

    c) "Almost a quarter of U.S. children under the age of 18 live with one parent and no other adults (23%)"
    - https://www.pewresearch.org
        /fact-tank/2019/12/12/u-s-children-more-likely-than-children-in-other-countries-to-live-with-just-one-parent/

    one adult to 23% minor homes,
    distribute the remaining adults and retirees in the remaining minor and non-nursing homes

    :param sim_config: PandemicSimConfig instance
    :return: a list of person instances
    """
    assert globals.registry, 'No registry found. Create the repo wide registry first by calling init_globals()'
    registry = globals.registry
    numpy_rng = globals.numpy_rng

    persons: List[Person] = []
    
    # Using schools to represent the buildings on campus/classes at UT
    in_person_campus_buildings = registry.location_ids_of_type(Campus)
    print("number of campus buildings: ", len(in_person_campus_buildings))
    hybrid_campus_buildings = registry.location_ids_of_type(HybridCampus)
    print("number of hybrid buildings: ", len(hybrid_campus_buildings))

    # Shuffle and combine the two to be able to assign students to each randomly
    # Conversion to list
    l = list(in_person_campus_buildings + hybrid_campus_buildings)
    random.shuffle(l)
    campus_buildings = tuple(l)

    # ages based on the age profile of UT
    student_ages = get_students_age_distribution((int)(sim_config.num_persons * 0.95))
    faculty_ages = get_faculty_age_distribution(sim_config.num_persons - len(student_ages))
    

    # ages = np.vstack((student_ages, faculty_ages))
    # numpy_rng.shuffle(ages)
    all_homes = list(registry.location_ids_of_type(Apartment))
    numpy_rng.shuffle(all_homes)
    unassigned_homes = all_homes

    # Assign a staff member to their own homes
    clustered_faculty = cluster_into_random_sized_groups(faculty_ages, 1, 2, numpy_rng)
    print("faculty ages type: ", type(faculty_ages))
    print("unassignedc homes: ", type(unassigned_homes))
    # faculty_home_ages = [(unassigned_homes[_i], _a) for _i, _g in enumerate(faculty_ages) for _a in _g]
    faculty_homes = unassigned_homes[:len(clustered_faculty)]
    unassigned_homes = unassigned_homes[len(faculty_homes):] # remove assigned faculty homes
    
    for i in range(len(faculty_homes)):
        persons.append(Faculty(person_id=PersonID(f'faculty_{str(uuid4())}', faculty_ages[i]),
                               home=faculty_homes[i],
                               work=numpy_rng.choice(campus_buildings) if len(campus_buildings) > 0 else None,
                               regulation_compliance_prob=sim_config.regulation_compliance_prob,
                               init_state=PersonState(current_location=faculty_homes[i], risk=infection_risk(faculty_ages[i]))))
    

    # Create the students, most students live in groups of 1-4 in their apartments
    # According to university housing and dining, at full capacity, about 14% of the total student population lives in on-campus dorms
    # https://thedailytexan.com/2021/09/05/ut-austin-residence-halls-return-to-full-capacity/

    dorms = list(registry.location_ids_of_type(Dorm))
    print("num total dorms: ", len(dorms))
    num_students_in_dorms = np.ceil(len(student_ages) * 0.138).astype('int')
    students_in_dorms_ages = student_ages[:num_students_in_dorms]
    print("num students in dorms: ", len(students_in_dorms_ages))
    clustered_student_dorm_ages = cluster_into_random_sized_groups(students_in_dorms_ages, 1, 4, numpy_rng)
    # dorms_ages = [(dorms[_i], _a) for _i, _g in enumerate(clustered_student_dorm_ages) for _a in _g]
    unassigned_students = student_ages[num_students_in_dorms:]
    dorm_counter = 0
    current_dorm_idx = 0
    for i in range(len(students_in_dorms_ages)):
        # iterate into the next dorm
        # then update the number of students remaining
        if dorm_counter > 30:
            current_dorm_idx += 1
            dorm_counter = 0
        persons.append(Student(person_id=PersonID(f'student_{str(uuid4())}', students_in_dorms_ages[i]),
                               home=dorms[current_dorm_idx],
                               school=numpy_rng.choice(campus_buildings) if len(campus_buildings) > 0 else None,
                               regulation_compliance_prob=sim_config.student_compliance_prob,
                               init_state=PersonState(current_location=dorms[current_dorm_idx], risk=infection_risk(students_in_dorms_ages[i]))))
        dorm_counter += 1

    # Make the rest of the students -> assign them to off-campus apartments
    # Most students live in groups of 2-5
    remaining_student_ages = student_ages[:len(unassigned_students)]
    assert len(unassigned_homes) >= len(remaining_student_ages), 'not enough homes to assign all people'
    num_roommates  = [int(globals.numpy_rng.choice(np.arange(2, 5))) for _ in range(len(unassigned_students))]
    student_homes = unassigned_homes[:len(remaining_student_ages)]
    unassigned_homes = unassigned_homes[len(student_homes):]  # remove assigned student apartments
    # create all student apartments
    current_apt_idx = 0
    current_num_roommates = 0
    current_roommate_capacity_idx = 0
    print("remaining student ages: ", remaining_student_ages)
    print(type(remaining_student_ages))
    for i in range(len(unassigned_students)):
        if current_num_roommates > num_roommates[current_apt_idx]:
            # has exceeded capacity of this apartment -> move onto the next one
            current_apt_idx += 1
            current_num_roommates = 0
            # current_roommate_capacity_idx += 1
        persons.append(Student(person_id=PersonID(f'student_{str(uuid4())}', remaining_student_ages[i]),
                             home=student_homes[current_apt_idx],
                             school=numpy_rng.choice(campus_buildings) if len(campus_buildings) > 0 else None,
                             regulation_compliance_prob=sim_config.student_compliance_prob,
                             init_state=PersonState(current_location=student_homes[current_apt_idx], risk=infection_risk(remaining_student_ages[i]))))
        current_num_roommates += 1


    return persons
