from random import randint
from itertools import cycle
import datetime

from Models.plane_model import *
from Models.simulation_model import Simulation


class SingleChargerSim:

    ORIGIN = (0, 0)
    PLANE_HEIGHT = 20
    PLANE_WIDTH = 20
    MIDDLE = (PLANE_HEIGHT / 2, PLANE_WIDTH / 2)
    NUMBER_OF_PERIPHERALS = 15
    LOCATION_OF_CHARGING_STATION = ORIGIN  # the other option is to set it to the middle of the plane
    PERIPHERAL_ENERGY_LOSS_MULTIPLIER = 0.005  # how fast peripherals lose energy per time unit
    DEBUG = False

    def __init__(self):
        self.plane = Plane(SingleChargerSim.PLANE_HEIGHT, SingleChargerSim.PLANE_WIDTH)
        self.peripherals = []
        self.travel_energy_used = 0
        self.transfer_energy_used = 0
        self.total_energy_used = 0
        self.cycles = 0
        self.start_time = datetime.datetime.now()
        self.running_sim = True

    # go through each cluster one at a time, charging each node in the cluster, then return home
    def single_charger_simulation(self):

        # add a single charging station and charging node
        charging_station = ChargingStation(SingleChargerSim.LOCATION_OF_CHARGING_STATION[0],
                                           SingleChargerSim.LOCATION_OF_CHARGING_STATION[1], self.plane)
        charger = ChargingNode(SingleChargerSim.LOCATION_OF_CHARGING_STATION[0],
                               SingleChargerSim.LOCATION_OF_CHARGING_STATION[1] + 1, self.plane,
                               charge_capacity=60, current_charge=60)

        # add a series of peripherals at random locations
        while self.plane.get_number_of_peripherals() < SingleChargerSim.NUMBER_OF_PERIPHERALS:
            try:
                capacity = randint(10, 30)
                self.peripherals.append(Peripheral(randint(1, 20), randint(2, 20), self.plane, charge_capacity=capacity,
                                                   current_charge=capacity))
            # IndexError indicates that the location is occupied. Just allow and try again
            except IndexError:
                pass

        # instantiate simulation object for analysis purposes
        simulation = Simulation(self.peripherals)

        # generate clusters
        # TODO: calculate the max allowable distance here
        maximum_cluster_radius = 5
        clusters = self.plane.generate_clusters(peripherals_list=self.peripherals,
                                                max_distance_between_point_and_centroid=maximum_cluster_radius)

        # cycle through clusters one at a time, return home, charge, go on to the next cluster
        while self.running_sim:
            for cluster in cycle(clusters):
                # assume that it takes 1 point of energy per unit traveled
                travel_energy_used_this_cycle, transfer_energy_used_this_cycle = charger.charge_cluster(cluster)

                # log the amount of energy used
                self.travel_energy_used += travel_energy_used_this_cycle
                self.transfer_energy_used += transfer_energy_used_this_cycle
                self.total_energy_used += transfer_energy_used_this_cycle + travel_energy_used_this_cycle

                # recharge the charger, decrement the amount of charge held by all devices
                amount_needed_to_replenish = charger.charge_capacity - charger.current_charge
                charger.charge_self()

                # decrement energy of all peripherals while charging
                for peripheral in self.peripherals:
                    peripheral.current_charge -= (amount_needed_to_replenish *
                                                  SingleChargerSim.PERIPHERAL_ENERGY_LOSS_MULTIPLIER)

                    # check whether any peripherals are dead, one at a time
                    if peripheral.current_charge <= 0:
                        simulation.peripheral_failure(peripheral_list_index=self.peripherals.index(peripheral),
                                                      timestamp=datetime.datetime.now())

                self.cycles += 1
                if self.cycles == 15 * len(clusters):
                    # shallow copy of the list at 15 minutes
                    simulation.peripheral_list_after_15_cycles = self.peripherals[:]
                    simulation.calculate_average_charge_at_15_cycles()

                # don't keep going if we are just debugging
                if SingleChargerSim.DEBUG and self.cycles == 5 * len(clusters):
                    self.running_sim = False
                    break

                # stop running the sim at 5 minutes
                if datetime.datetime.now() - self.start_time >= datetime.timedelta(minutes=5):
                    self.running_sim = False
                    break

        # record energy used
        simulation.total_energy_used = self.total_energy_used
        simulation.transfer_energy_used = self.transfer_energy_used
        simulation.travel_energy_used = self.travel_energy_used

        return simulation
