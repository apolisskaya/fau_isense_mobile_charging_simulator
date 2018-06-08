#!/usr/bin/env python3

from Services import requirements_service as rs
from Services.format_service import pretty_print
from Services.simulation_services import *
from Models.plane_model import *

if __name__ == "__main__":
    rs.run_requirement_check()
    pretty_print("Welcome to the FAU I-SENSE Mobile Charging Simulator.", 'blue')

    """
    To start let us assume that it takes one millisecond to travel one distance unit
    and one millisecond to transfer one unit of energy from one place to another
    
    Below is some sandbox code that should be moved elsewhere once possible
    """

    # create a 10x12 plane
    plane = Plane(10, 12)

    # add some peripherals
    p1 = Peripheral(2, 4, plane)
    p2 = Peripheral(1, 6, plane)
    p3 = Peripheral(8, 11, plane)
    p4 = Peripheral(8, 10, plane)

    # add a charging station and a charging node
    charging_station_1 = ChargingStation(1, 0, plane)
    c1 = ChargingNode(0, 0, plane)

    clusters = plane.generate_clusters([p1, p2, p3, p4], 2)
    for cluster in clusters:
        pretty_print(cluster.peripheral_list, "purple")