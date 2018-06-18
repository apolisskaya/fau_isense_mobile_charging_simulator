#!/usr/bin/env python3

from Services import requirements_service as rs
from Services.format_service import pretty_print
from Services.simulation_services import *
from Models.plane_model import *

if __name__ == "__main__":
    rs.run_requirement_check()
    pretty_print("Welcome to the FAU I-SENSE Mobile Charging Simulator.", 'blue')

    # we want to run both sims and record the following:
    # 1. all types of energy used and amounts
    # 2. the whole peripherals list should be returned after some number of cycles is completed
    # 3. length of time the sim is able to continue. let's say that if it runs in a stable manner for 5 minutes,
    # it works as intended.

