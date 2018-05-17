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
        if self.plane[x_coord][y_coord] != 0:
            return True
        return False

    def add_peripheral(self, peripheral):
        self.peripherals.append(peripheral)

    def add_charger(self, charger):
        self.chargers.append(charger)

    def add_charging_station(self, charging_station):
        self.charging_stations.append(charging_station)


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

    def charge_device(self, source):
        # TODO: figure out how to do this smoothly..
        pass


class ChargingNode(Peripheral):
    def __init__(self, x_location, y_location, plane, charge_capacity=0, current_charge=0):
        super(Peripheral, self).__init__(x_location, y_location, plane, charge_capacity, current_charge)
        self.plane.add_charger(self)


class ChargingStation():
    def __init__(self, x_location, y_location, plane):
        # double checking that the location is available
        if plane.plane[x_location][y_location] != 0:
            raise IndexError
        self.x_location = x_location
        self.y_location = y_location
        # we want a weak reference available here
        self.plane = plane
        self.plane.add_charging_station(self)