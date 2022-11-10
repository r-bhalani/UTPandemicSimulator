# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from tqdm import trange

import pandemic_simulator as ps


def run_pandemic_sim() -> None:
    """Here we execute the simulator using austin regulations, a small town config and default person routines."""

    print('\nA tutorial that runs the simulator using UT regulations during the pandemic and default person routines', flush=True)

    # init globals
    ps.init_globals(seed=1)

    # select a simulator config
    sim_config = ps.sh.ut_config

    # make sim
    sim = ps.env.PandemicSim.from_config(sim_config)

    # setup viz to show plots
    viz = ps.viz.SimViz.from_config(sim_config)

    # impose a regulation
    sim.impose_regulation(regulation=ps.sh.ut_regulations[0])  # stage 0

    # run regulation steps in the simulator
    for _ in trange(75, desc='Simulating warmup'):
        sim.step_day()
        viz.record(sim.state)
    
    sim.impose_regulation(regulation=ps.sh.ut_regulations[1])  # stage 0

    # run regulation steps in the simulator
    for _ in trange(10, desc='Simulating warmup'):
        sim.step_day()
        viz.record(sim.state)
    
    sim.impose_regulation(regulation=ps.sh.ut_regulations[2])  # stage 0

    # run regulation steps in the simulator
    for _ in trange(10, desc='Simulating warmup'):
        sim.step_day()
        viz.record(sim.state)
    
    sim.impose_regulation(regulation=ps.sh.ut_regulations[3])  # stage 0

    # run regulation steps in the simulator
    for _ in trange(10, desc='Simulating warmup'):
        sim.step_day()
        viz.record(sim.state)

    # impose a regulation
    # sim.impose_regulation(regulation=ps.sh.ut_regulations[0])  # stage 4

    # # run regulation steps in the simulator
    # for _ in trange(100, desc='Simulating Fall 2020'):
    #     sim.step_day()
    #     viz.record(sim.state)

    # impose a regulation
    sim.impose_regulation(regulation=ps.sh.ut_regulations[3])  # stage 3

    # run regulation steps in the simulator
    for _ in trange(100, desc='Simulating Spring 2021'):
        sim.step_day()
        viz.record(sim.state)


    # impose a regulation
    sim.impose_regulation(regulation=ps.sh.ut_regulations[3])  # stage 2

    # run regulation steps in the simulator
    for _ in trange(100, desc='Simulating Fall 2021'):
        sim.step_day()
        viz.record(sim.state)


    # impose a regulation
    sim.impose_regulation(regulation=ps.sh.ut_regulations[1])  # stage 1

    # run regulation steps in the simulator
    for _ in trange(100, desc='Simulating Spring 2022'):
        sim.step_day()
        viz.record(sim.state)


    # impose a regulation
    sim.impose_regulation(regulation=ps.sh.ut_regulations[0])  # stage 0

    # run regulation steps in the simulator
    for _ in trange(100, desc='Simulating Fall 2022'):
        sim.step_day()
        viz.record(sim.state)
    

    # generate plots
    viz.plot()


if __name__ == '__main__':
    run_pandemic_sim()
