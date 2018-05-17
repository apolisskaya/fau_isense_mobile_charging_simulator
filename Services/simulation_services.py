import math

from Models.plane_model import Plane, Peripheral


def get_distance_between(location_1=(0,0), location_2=(0,0)):
    """
    returns the Euclidean distance between two points in the plane
    :param location_1: ordered pair of coordinates for location 1
    :param location_2: ordered pair of coordinates for location 2
    :return: a float distance for locations 1 and 2
    """
    return math.hypot(location_2[0] - location_1[0], location_2[1] - location_1[1])


def get_clusters(peripherals_list = [], max_distance_between_point_and_centroid = 1):
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
            # centroid already set, we want all points within the allowed distance from it
            for peripheral in peripherals_list:
                p_x, p_y = peripheral.get_location()
                if get_distance_between(location_1=(centroid_location_x, centroid_location_y), location_2=(p_x, p_y)) \
                        <= max_distance_between_point_and_centroid:
                    p = peripherals_list.pop(peripheral)
                    current_cluster_list.append(p)

            cluster_list.append(current_cluster_list)
            current_cluster_list = []

    return cluster_list