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
            else:
                from Services.simulation_services import get_distance_between
                # centroid already set, we want all points within the allowed distance from it
                for peripheral in peripherals_list:
                    p_x, p_y = peripheral.get_location()
                    if get_distance_between(location_1=(centroid_location_x, centroid_location_y),
                                            location_2=(p_x, p_y)) \
                            <= max_distance_between_point_and_centroid:
                        p = peripherals_list.pop(peripheral)
                        current_cluster_list.append(p)

                cluster_list.append(Cluster(peripheral_list=current_cluster_list, id=len(cluster_list)))
                current_cluster_list = []

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
        super(Peripheral, self).__init__(x_location, y_location, plane, charge_capacity, current_charge)
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
        self.shortest_path_through_cluster = simulation_services.traveling_salesman(self)

        # TODO: to get the diameter we need the maximum distance between any two points in the cluster

    def get_location(self):
        return self.x_location, self.y_location

    def get_size(self):
        return self.size

    def get_peripherals(self):
        return self.peripheral_list

    def get_id(self):
        return self.id
