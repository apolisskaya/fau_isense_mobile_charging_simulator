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
            dedicated_charger.current_charge -= distance_to_travel

            # decrement energy of all peripherals
            for p in peripherals:
                p.current_charge -= distance_to_travel * PERIPHERAL_ENERGY_LOSS_MULTIPLIER

            travel_energy_used += distance_to_travel
            total_energy_used += distance_to_travel
            charge_available = charger.current_charge

            # charge the dedicated charger either to full, or as much as possible
            amount_to_charge = min(charge_needed, charge_available)
            charger.charge_peripheral(dedicated_charger, amount_to_charge)
            transfer_energy_used += amount_to_charge
            total_energy_used += amount_to_charge

            # we want to decrement the length of the path from the dedicated charger first
            dedicated_charger.current_charge -= cluster.length_of_shortest_path
            # this was originally considered transfer energy but it's now travel energy
            travel_energy_used += cluster.length_of_shortest_path
            transfer_energy_used -= cluster.length_of_shortest_path

            # dedicated charger now charges the cluster
            # the transfer energy was already counted as such during the dedicated charger recharge. no need to track.
            for peripheral_index in cluster.shortest_path_through_cluster:
                peripheral = cluster.peripheral_list[peripheral_index]
                amount_of_charge_needed = peripheral.charge_capacity - peripheral.current_charge
                charge_available = dedicated_charger.current_charge
                amount_to_charge = min(amount_of_charge_needed, charge_available)
                dedicated_charger.charge_peripheral(peripheral=peripheral, amount=amount_to_charge)

            # recharge the charger, decrement the amount of charge held by all devices
            amount_needed_to_replenish = charger.charge_capacity - charger.current_charge
            charger.charge_self()
            for peripheral in peripherals:
                peripheral.current_charge -= (amount_needed_to_replenish * PERIPHERAL_ENERGY_LOSS_MULTIPLIER)

multi_charger_simulation_experimental()
