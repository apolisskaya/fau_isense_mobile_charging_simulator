import math


def get_distance_between(location_1=(0,0), location_2=(0,0)):
    """
    returns the Euclidean distance between two points in the plane
    :param location_1: ordered pair of coordinates for location 1
    :param location_2: ordered pair of coordinates for location 2
    :return: a float distance for locations 1 and 2
    """
    return math.hypot(location_2[0] - location_1[0], location_2[1] - location_1[1])