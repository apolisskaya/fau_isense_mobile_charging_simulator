from random import randint
from itertools import cycle

from Models.plane_model import *
from Services import simulation_services

ORIGIN = (0, 0)
PLANE_HEIGHT = 20
PLANE_WIDTH = 20
MIDDLE = (PLANE_HEIGHT/2, PLANE_WIDTH/2)
NUMBER_OF_PERIPHERALS = 15
LOCATION_OF_CHARGING_STATION = ORIGIN  # the other option is to set it to the middle of the plane
PERIPHERAL_ENERGY_LOSS_MULTIPLIER = 0.5  # how fast peripherals lose energy per time unit


# go through each cluster one at a time, charging each node in the cluster, then return home
def multi_charger_simulation_experimental():
    # initialize the plane
    plane = Plane(PLANE_HEIGHT, PLANE_WIDTH)
    peripherals = []
    travel_energy_used = 0
    transfer_energy_used = 0
    total_energy_used = 0

    # add a single master charging station and master charging node
    charging_station = ChargingStation(LOCATION_OF_CHARGING_STATION[0], LOCATION_OF_CHARGING_STATION[1], plane)
    charger = ChargingNode(LOCATION_OF_CHARGING_STATION[0], LOCATION_OF_CHARGING_STATION[1] + 1, plane,
                           charge_capacity=80, current_charge=80)

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

    # instantiate a dedicated charger for each cluster
    dedicated_charger_list = []
    for cluster in clusters:
        dedicated_charger = ChargingNode(plane=plane, x_location=cluster.x_location,
                                         y_location=cluster.y_location, charge_capacity=60,
                                         current_charge=60)
        cluster.set_dedicated_charger(dedicated_charger)
        dedicated_charger_list.append(dedicated_charger)

    # grab the shortest hamiltonian path through the clusters if we need it
    length_of_path_through_clusters, shortest_path_through_clusters = \
        simulation_services.traveling_salesman(Cluster(id=-1, peripheral_list=dedicated_charger_list))

    # cycle through clusters one at a time, return home, charge, go on to the next cluster
    while True:
        for cluster in cycle(clusters):
            dedicated_charger = cluster.dedicated_charger
            charge_needed = dedicated_charger.get_charge_needed()
            distance_to_travel = 2 * simulation_services.get_distance_between(charger.get_location(),
                                                                             dedicated_charger.get_location())
            dedicated_charger -= distance_to_travel
            travel_energy_used += distance_to_travel
            charge_available = charger.current_charge

            # charge the dedicated charger either to full, or as much as possible
            amount_to_charge = min(charge_needed, charge_available)
            charger.charge_peripheral(dedicated_charger, amount_to_charge)
            transfer_energy_used += amount_to_charge

            # TODO: finish from here, the rest should be edited/removed/replaced

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



multi_charger_simulation_experimental()
