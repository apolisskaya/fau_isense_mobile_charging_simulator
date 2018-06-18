class Plane:
    def __init__(self, x_axis_size, y_axis_size):
        """
        initialize a new Plane object that the simulation must operate within
        :param x_axis_size: the length of side of the plane parallel to the x-axis in the plane
        :param y_axis_size: the length of the side of the plane parallel to the y-axis in the plane
        """
        # 2d array must have width and height of integer sizes
        if not isinstance(x_axis_size, int) or not isinstance(y_axis_size, int):
            raise TypeError
        self.x_axis_size = x_axis_size
        self.y_axis_size = y_axis_size
        self.plane = [[0 for _ in range(y_axis_size)] for _ in range(x_axis_size)]
        self.chargers = []
        self.charging_stations = []
        self.peripherals = []
        self.cluster_list = None

    def get_number_of_peripherals(self):
        return len(self.peripherals)

    def get_width(self):
        return self.x_axis_size

    def get_length(self):
        return self.y_axis_size

    def get_coord(self, x_coord, y_coord):
        if self.plane[x_coord][y_coord] != 0:
            return self.plane[x_coord][y_coord]
        else:
            return 0

    def is_occupied(self, x_coord, y_coord):
        """
        check whether or not a given coordinate is occupied
        """
        if self.plane[x_coord][y_coord] != 0:
            return True
        return False

    def add_peripheral(self, peripheral):
        self.peripherals.append(peripheral)

    def add_charger(self, charger):
        self.chargers.append(charger)

    def add_charging_station(self, charging_station):
        self.charging_stations.append(charging_station)

    def generate_clusters(self, peripherals_list=[], max_distance_between_point_and_centroid=1):
        """
        generate a series of clusters that the charging node can operate on
        :param pheripherals_list: list of peripheral objects in the plane
        :param max_distance_between_point_and_centroid: maximum radius of the cluster
        :return: a list of lists of peripherals. each list is a different cluster.'

        note: this is a preliminary algorithm. it will return clusters, but they may not be of maximum size
        """

        # no peripherals in the plane
        if len(peripherals_list) == 0:
            return []

        cluster_list = []
        centroid_set = False
        current_cluster_list = []
        centroid_location_x = 0
        centroid_location_y = 0
        id = 0
        # clear previous cluster list, if one exists
        if not self.cluster_list:
            self.cluster_list = None

        while len(peripherals_list) > 0:
            if not centroid_set:
                # grab the next available peripheral and begin populating the new cluster
                centroid = peripherals_list.pop()
                if type(centroid) != Peripheral:
                    raise TypeError
                centroid_set = True
                current_cluster_list.append(centroid)
                centroid_location_x, centroid_location_y = centroid.get_location()
                # we just removed the last peripheral, no need to check for adjacent points
                if len(peripherals_list) == 0:
                    cluster_list.append(Cluster(peripheral_list=current_cluster_list, id=id))
            else:
                from Services.simulation_services import get_distance_between
                # centroid already set, we want all points within the allowed distance from it
                for peripheral in peripherals_list:
                    p_x, p_y = peripheral.get_location()
                    if get_distance_between(location_1=(centroid_location_x, centroid_location_y),
                                            location_2=(p_x, p_y)) \
                            <= max_distance_between_point_and_centroid:
                        p = peripherals_list.pop(peripherals_list.index(peripheral))
                        current_cluster_list.append(p)

                cluster_list.append(Cluster(peripheral_list=current_cluster_list, id=id))
                id += 1
                current_cluster_list = []
                centroid_set = False

        # update the model with the new cluster list
        self.cluster_list = cluster_list

        # the order of elements in a list persists, so we know that the first element of every cluster is the centroid
        # that is what will be used later in the sim

        return cluster_list

    def get_cluster_by_id(self, cluster_id):
        if not self.cluster_list:
            raise IndexError('Cluster list has not been initialized before use. Check your code.')

        for cluster in self.cluster_list:
            # support cluster lookup when data types don't match
            if str(cluster.get_id()) == str(cluster_id):
                return cluster

        # no such cluster exists
        return None


class Peripheral:
    def __init__(self, x_location, y_location, plane, charge_capacity=0, current_charge=0):
        # double checking that the location is available
        if plane.plane[x_location][y_location] != 0:
            raise IndexError
        self.x_location = x_location
        self.y_location = y_location
        self.charge_capacity = charge_capacity
        self.current_charge = current_charge
        self.plane = plane
        # other classes inherit from here
        if type(self) == Peripheral:
            self.plane.add_peripheral(self)

    def get_location(self):
        """
        return the ordered pair of coordinates where the peripheral is located
        """
        return self.x_location, self.y_location

    def get_current_charge(self):
        return self.current_charge

    def get_charge_capacity(self):
        return self.charge_capacity

    def get_charge_needed(self):
        return self.charge_capacity - self.current_charge

    def charge_device(self, source, amount):
        """
        execute a call to charge_peripheral method of charging node class
        :param source: source charging node
        :param amount: amount of energy to be transferred
        """
        source.charge_peripheral(source, self, amount)

    def get_plane(self):
        return self.plane


class ChargingNode(Peripheral):
    def __init__(self, x_location, y_location, plane, charge_capacity=0, current_charge=0):
        super(Peripheral, self).__init__()
        self.x_location = x_location
        self.y_location = y_location
        self.plane = plane
        self.charge_capacity = charge_capacity
        self.current_charge = current_charge
        self.plane.add_charger(self)

    def charge_self(self):
        # TODO: this needs to be altered to allow for partial charges between trips maybe?
        self.current_charge = self.charge_capacity

    def charge_peripheral(self, peripheral, amount):
        """
        charges peripheral device and removes that charge from the charger
        we assume that checks regarding how much to charge have already been done
        :param peripheral: the peripheral being charged
        :param amount: the amount of energy being transferred
        """
        if type(peripheral) is not Peripheral:
            raise TypeError
        if type(amount) is not float or int:
            raise TypeError

        self.current_charge -= amount
        peripheral.current_charge += amount

    def charge_cluster(self, cluster):
        from Simulation.single_charger_simulation import PERIPHERAL_ENERGY_LOSS_MULTIPLIER

        travel_energy_used = 0
        transfer_energy_used = 0
        all_peripherals = cluster.plane.peripherals

        # first we deduct the energy to travel to the cluster
        from Services.simulation_services import get_distance_between
        amount_needed_to_travel_to_cluster = get_distance_between(location_1=(self.x_location, self.y_location),
                                                                  location_2=(cluster.x_location, cluster.y_location))
        self.current_charge -= amount_needed_to_travel_to_cluster
        travel_energy_used += amount_needed_to_travel_to_cluster

        # all peripherals in the plane lose charge during initial travel time
        for peripheral in all_peripherals:
            peripheral.current_charge -= (amount_needed_to_travel_to_cluster * PERIPHERAL_ENERGY_LOSS_MULTIPLIER)

        # for now assume charger travels to all peripherals regardless of whether or not it charges them
        self.current_charge -= cluster.length_of_shortest_path
        travel_energy_used += cluster.length_of_shortest_path

        final_peripheral_in_cluster = cluster.peripheral_list[cluster.shortest_path_through_cluster[-1]]
        amount_needed_to_return_home = get_distance_between(location_1=(final_peripheral_in_cluster.x_location,
                                                                        final_peripheral_in_cluster.y_location),
                                                            location_2=(self.x_location, self.y_location))

        # now we charge the peripherals along the shortest path
        for peripheral_index in cluster.shortest_path_through_cluster:
            peripheral = cluster.peripheral_list[peripheral_index]
            amount_of_charge_needed = peripheral.charge_capacity - peripheral.current_charge
            charge_available = self.current_charge - amount_needed_to_return_home

            amount_to_charge = min(amount_of_charge_needed, charge_available)
            self.charge_peripheral(peripheral=peripheral, amount=amount_to_charge)

            # while charging, decrement all other peripherals but not the one being charged TODO: decrement all??
            for p in all_peripherals:
                if p is not peripheral:
                    p.current_charge -= (amount_to_charge * PERIPHERAL_ENERGY_LOSS_MULTIPLIER)

            transfer_energy_used += amount_to_charge
            if self.current_charge == amount_needed_to_return_home:
                break

        # charger goes back home now
        self.current_charge -= amount_needed_to_return_home
        travel_energy_used += amount_needed_to_return_home

        # all peripherals in the plane lose charge during this time
        for peripheral in all_peripherals:
            peripheral.current_charge -= (amount_needed_to_return_home * PERIPHERAL_ENERGY_LOSS_MULTIPLIER)

        return travel_energy_used, transfer_energy_used


class ChargingStation:
    def __init__(self, x_location, y_location, plane):
        # double checking that the location is available
        if plane.plane[x_location][y_location] != 0:
            raise IndexError
        self.x_location = x_location
        self.y_location = y_location
        # we want a weak reference available here
        self.plane = plane
        self.plane.add_charging_station(self)

    def get_location(self):
        """
        return the ordered pair of coordinates where the peripheral is located
        """
        return self.x_location, self.y_location


class Cluster:
    def __init__(self, peripheral_list, id):
        self.id = id
        self.peripheral_list = peripheral_list
        self.size = len(peripheral_list)
        if self.size > 0:
            self.x_location, self.y_location = self.peripheral_list[0].get_location()
        else:
            self.x_location = 0
            self.y_location = 0
        # we assume that all clusters must be in the same plane for now
        self.plane = self.peripheral_list[0].get_plane()
        from Services import simulation_services
        self.length_of_shortest_path, self.shortest_path_through_cluster = \
            simulation_services.traveling_salesman(self)
        self.dedicated_charger = None  # used in experimental multi charger algorithm
        self.diameter = max(max(row) for row in simulation_services.get_distance_matrix(self))

    def get_location(self):
        return self.x_location, self.y_location

    def get_size(self):
        return self.size

    def get_peripherals(self):
        return self.peripheral_list

    def get_id(self):
        return self.id

    def set_dedicated_charger(self, charger):
        self.dedicated_charger = charger
