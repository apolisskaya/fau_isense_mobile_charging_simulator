#!/usr/bin/env python3

from Services import requirements_service as rs
from Services.format_service import pretty_print
from Simulation.single_charger_simulation import SingleChargerSim
from Simulation.multi_charger_simulation_experimental import MultiChargerSim

if __name__ == "__main__":
    rs.run_requirement_check()
    pretty_print("Welcome to the FAU I-SENSE Mobile Charging Simulator.", 'blue')

    # we want to run both sims and record the following:
    # 1. all types of energy used and amounts
    # 2. the whole peripherals list should be returned after some number of cycles is completed
    # 3. length of time the sim is able to continue. let's say that if it runs in a stable manner for 5 minutes,
    # it works as intended.

    print('single charge with comm:')
    single_charge_with_communication = SingleChargerSim().single_charger_simulation_with_communication(10).\
        run_analytics_on_simulation()
    print('multi with comm:')
    multi_with_communication = MultiChargerSim().multi_charger_simulation_experimental_with_communication(10).\
        run_analytics_on_simulation()
    print('single without:')
    single_charger_simulation = SingleChargerSim().single_charger_simulation().run_analytics_on_simulation()
    print('multi without:')
    multi_charger_simulation = MultiChargerSim().multi_charger_simulation_experimental().run_analytics_on_simulation()

    # TODO: next step will be visualization of this data and possibly hosting it on Heroku
