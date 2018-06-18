import datetime


class Simulation:
    def __init__(self, peripheral_list):

        self.travel_energy_used = None
        self.transfer_energy_used = None
        self.total_energy_used = None
        self.peripheral_list_after_15_cycles = None
        self.peripheral_list = peripheral_list
        self.time_of_peripheral_failures = {peripheral: None for peripheral in self.peripheral_list}
        self.time_of_earliest_failute = None
        self.start_time = datetime.datetime.now()

    def peripheral_failure(self, peripheral_list_index, timestamp):
        if not self.time_of_earliest_failute:
            self.time_of_earliest_failute = timestamp
        peripheral = self.peripheral_list[peripheral_list_index]
        self.time_of_peripheral_failures[peripheral] = timestamp
        # this peripheral will no longer be charged
        # TODO: should it be?
        peripheral.current_charge = 0
        peripheral.charge_capacity = 0