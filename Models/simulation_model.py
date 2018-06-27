import datetime
from Analytics.basic_analysis import *
from Services.format_service import pretty_print


class Simulation:
    def __init__(self, peripheral_list):

        self.travel_energy_used = None
        self.transfer_energy_used = None
        self.total_energy_used = None
        self.peripheral_list_after_15_cycles = None
        self.peripheral_list = peripheral_list
        self.time_of_peripheral_failures = {peripheral: None for peripheral in self.peripheral_list}
        self.peripheral_failure_count = 0
        self.time_of_earliest_failute = None
        self.start_time = datetime.datetime.now()

        self.effective_energy_percentage = None
        self.ineffective_energy_percentage = None
        self.average_charge_at_15_cycles = None
        self.time_until_earliest_failure = None

    def peripheral_failure(self, peripheral_list_index, timestamp):
        if not self.time_of_earliest_failute:
            self.time_of_earliest_failute = timestamp
        peripheral = self.peripheral_list[peripheral_list_index]
        self.time_of_peripheral_failures[peripheral] = timestamp
        # this peripheral will no longer be charged
        # TODO: should it be?
        if peripheral.charge_capacity > 0:
            self.peripheral_failure_count += 1
        peripheral.current_charge = 0
        peripheral.charge_capacity = 0

        # track how long the algorithm runs before a failure occurs
        self.time_until_earliest_failure = timestamp - self.start_time

    def calculate_average_charge_at_15_cycles(self):
        self.average_charge_at_15_cycles = average_charge_percentage(self.peripheral_list_after_15_cycles)

    def set_effective_energy_percentage(self):
        if self.transfer_energy_used and self.total_energy_used:
            self.effective_energy_percentage = calculate_effective_energy_percentage(self.transfer_energy_used,
                                                                                     self.total_energy_used)
        else:
            raise AssertionError('Please check code. Transfer and Total energy in Simulation class referenced '
                                 'before assignment.')

    def set_ineffective_energy_percentage(self):
        if self.travel_energy_used and self.total_energy_used:
            self.ineffective_energy_percentage = calculate_ineffective_energy_percentage(self.travel_energy_used,
                                                                                         self.total_energy_used)
        else:
            raise AssertionError('Please check code. Travel and Total energy in Simulation class referenced '
                                 'before assignment.')

    def set_peripheral_failure_count(self):
        total_number_of_peripherals = len(self.peripheral_list)
        failed_peripherals = 0
        for peripheral in self.peripheral_list:
            if peripheral.current_charge <= 0:
                failed_peripherals += 1

        return (failed_peripherals / total_number_of_peripherals)

    def run_analytics_on_simulation(self):
        """
        Run analysis on the results and store in the appropriate variable
        """

        self.set_effective_energy_percentage()
        self.set_ineffective_energy_percentage()
        self.calculate_average_charge_at_15_cycles()
        if self.time_of_earliest_failute:
            pretty_print('At least one peripheral failed within the 5 minute window. Algorithm may be ineffective.',
                         'red')

        print('Effective Energy Percentage: ', self.effective_energy_percentage)
        print('Ineffective Energy Percentage: ', self.ineffective_energy_percentage)
        print('Average Charge at 15 Cycles: ', self.average_charge_at_15_cycles)
        if self.time_of_earliest_failute:
            print('Running Time Until Peripheral Failure: ', self.time_of_earliest_failute - self.start_time)
        total_number_of_peripherals = len(self.peripheral_list)
        failed_peripherals = 0
        for peripheral in self.peripheral_list:
            if peripheral.current_charge <= 0:
                failed_peripherals += 1
        print('Failed Peripherals: ', failed_peripherals / total_number_of_peripherals)
