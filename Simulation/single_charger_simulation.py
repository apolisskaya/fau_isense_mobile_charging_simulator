from random import randint
from itertools import cycle

from Models.plane_model import *

ORIGIN = (0, 0)
PLANE_HEIGHT = 20
PLANE_WIDTH = 20
MIDDLE = (PLANE_HEIGHT/2, PLANE_WIDTH/2)
NUMBER_OF_PERIPHERALS = 15
LOCATION_OF_CHARGING_STATION = ORIGIN  # the other option is to set it to the middle of the plane
PERIPHERAL_ENERGY_LOSS_MULTIPLIER = 0.5  # how fast peripherals lose energy per time unit


# go through each cluster one at a time, charging each node in the cluster, then return home
def single_charger_simulation():
    # initialize the plane
    plane = Plane(PLANE_HEIGHT, PLANE_WIDTH)
    peripherals = []
    travel_energy_used = 0
    transfer_energy_used = 0
    total_energy_used = 0

    # add a single charging station and charging node
    charging_station = ChargingStation(LOCATION_OF_CHARGING_STATION[0], LOCATION_OF_CHARGING_STATION[1], plane)
    charger = ChargingNode(LOCATION_OF_CHARGING_STATION[0], LOCATION_OF_CHARGING_STATION[1] + 1, plane,
                           charge_capacity=60, current_charge=60)

    # add a series of peripherals at random locations
    while plane.get_number_of_peripherals() < NUMBER_OF_PERIPHERALS:
        try:
            capacity = randint(10, 30)
            peripherals.append(Peripheral(randint(1, 20), randint(2, 20), plane, charge_capacity=capacity,
                                          current_charge=capacity))
        # IndexError indicates that the location is occupied. Just allow and try again
        except IndexError:
            pass

    # generate clusters
    # TODO: calculate the max allowable distance here
    maximum_cluster_radius = 5
    clusters = plane.generate_clusters(peripherals_list=peripherals,
                                       max_distance_between_point_and_centroid=maximum_cluster_radius)

    # cycle through clusters one at a time, return home, charge, go on to the next cluster
    while True:
        for cluster in cycle(clusters):
            # assume that it takes 1 point of energy per unit traveled
            travel_energy_used_this_cycle, transfer_energy_used_this_cycle = charger.charge_cluster(cluster)

            # log the amount of energy used
            travel_energy_used += travel_energy_used_this_cycle
            transfer_energy_used += transfer_energy_used_this_cycle
            total_energy_used += transfer_energy_used_this_cycle + travel_energy_used_this_cycle

            # recharge the charger, decrement the amount of charge held by all devices
            amount_needed_to_replenish = charger.charge_capacity - charger.current_charge
            charger.charge_self()
            for peripheral in plane.peripherals:
                peripheral.current_charge -= (amount_needed_to_replenish * PERIPHERAL_ENERGY_LOSS_MULTIPLIER)



single_charger_simulation()
