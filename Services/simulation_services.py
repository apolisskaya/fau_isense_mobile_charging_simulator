import math, itertools


def get_distance_between(location_1=(0, 0), location_2=(0, 0)):
    """
    returns the Euclidean distance between two points in the plane
    :param location_1: ordered pair of coordinates for location 1
    :param location_2: ordered pair of coordinates for location 2
    :return: a float distance for locations 1 and 2
    """
    return math.hypot(location_2[0] - location_1[0], location_2[1] - location_1[1])


def traveling_salesman(cluster):
    """
    We want a minimum weight Hamiltonian path through the peripherals in this cluster
    However, it seems that we have stumbled upon a NP-Hard problem
    :param cluster: the cluster we want to move throughout
    :return: a Hamiltonian (possibly) path through the cluster
    """
    from Models.plane_model import Cluster
    if type(cluster) is not Cluster:
        raise TypeError('Non-cluster object passed to traveling_salesman in Services/simulation_'
                        'services.py\nCheck your code.')

    distance_matrix = get_distance_matrix(cluster)
    shortest_hamiltonian_path = held_karp(distance_matrix)

    return shortest_hamiltonian_path


def get_distance_matrix(cluster):
    """
    Create a distance matrix for the nodes in a cluster
    :param cluster: the cluster of nodes we are interested in traveling through
    :return: a list of lists forming a distance matrix
    """
    distance_matrix = []
    nodes = cluster.get_peripherals()

    for r in range(cluster.get_size()):
        row = []
        for node in nodes:
            row.append(get_distance_between(location_1=(nodes[r].get_location()), location_2=node.get_location()))
        distance_matrix.append(row)

    return distance_matrix


def held_karp(distance_matrix):
    """
    An implementation of the Held-Karp Algorithm to solve the Traveling Salesman Problem
    :param distance_matrix: a distance matrix of the nodes in the plane
    This should be a list of lists, each of the same size
    Runtime should be O(n^2 * 2^n)
    :return: the path and its cost
    adapted from CarlEkerot github
    """

    # first some error checking
    number_of_nodes = get_size_of_square_matrix(distance_matrix)
    if type(number_of_nodes) is not int:
        raise TypeError('Distance matrix is incorrectly formed. Check your input and try again.')

    # if we only have one node, no need for all this
    if number_of_nodes == 1:
        return 0, [0]

    C = {}

    for k in range(1, number_of_nodes):
        C[(1 << k, k)] = (distance_matrix[0][k], 0)

    for subset_size in range(2, number_of_nodes):
        for subset in itertools.combinations(range(1, number_of_nodes), subset_size):
            bits = 0
            for bit in subset:
                bits |= 1 << bit

            for k in subset:
                prev = bits & ~(1 << k)
                res = []
                for m in subset:
                    if m == 0 or m == k:
                        continue
                    res.append((C[(prev, m)][0] + distance_matrix[m][k], m))
                C[(bits, k)] = min(res)

    bits = (2**number_of_nodes - 1) - 1
    res = []

    for k in range(1, number_of_nodes):
        res.append((C[(bits, k)][0] + distance_matrix[k][0], k))
    opt, parent = min(res)

    path = []
    for i in range(number_of_nodes - 1):
        path.append(parent)
        new_bits = bits & ~(1 << parent)
        _, parent = C[(bits, parent)]
        bits = new_bits

    path.append(0)

    return opt, list(reversed(path))


def get_size_of_square_matrix(matrix):
    """
    Check whether or not a matrix is square.
    :param matrix: some list of lists, a matrix
    :return: the length/width of the matrix, or False
    """

    if type(matrix) is not list:
        raise TypeError('Distance matrix must be a list of lists. Check your input and try again.')

    n = len(matrix)
    for row in matrix:
        if len(row) != n:
            return False

    return n
