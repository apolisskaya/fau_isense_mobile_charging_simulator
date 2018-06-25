#!/usr/bin/env python3

from Services import requirements_service as rs
from Services.format_service import pretty_print
from Simulation.single_charger_simulation import SingleChargerSim
from Analytics.basic_analysis import *

if __name__ == "__main__":
    rs.run_requirement_check()
    pretty_print("Welcome to the FAU I-SENSE Mobile Charging Simulator.", 'blue')

    # we want to run both sims and record the following:
    # 1. all types of energy used and amounts
    # 2. the whole peripherals list should be returned after some number of cycles is completed
    # 3. length of time the sim is able to continue. let's say that if it runs in a stable manner for 5 minutes,
    # it works as intended.

    single_charger_simulation = SingleChargerSim.single_charger_simulation().\
        run_analytics_on_simulation()
    print(single_charger_simulation)
    # multi_charger_simulation = Simulation.multi_charger_simulation_experimental.\
    #     multi_charger_simulation_experimental().run_analytics_on_simulation()

    # we should now have the analytics available in these two variables for recording/display