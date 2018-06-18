# For analytics we want the following measurements:

# How long the sim was able to run before any peripherals, including the charger, die
# Amount of effective energy vs total energy used per cycle
# Average charge percentage after some length of time
# (for example, say both algorithms work, but one keeps devices charged better.. more room for inaccuracies exist there)


def calculate_effective_energy_percentage(transfer_energy_used, total_energy_used):
    return transfer_energy_used / total_energy_used


def calculate_ineffective_energy_percentage(travel_energy_used, total_energy_used):
    return travel_energy_used / total_energy_used


def average_charge_percentage(peripherals_list):
    number_of_peripherals = len(peripherals_list)
    total_sum_of_percentages = sum([peripheral.charge_capacity - peripheral.current_charge
                                    for peripheral in peripherals_list])
    return total_sum_of_percentages / number_of_peripherals

