#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2019  Tugrul Yatagan <tugrulyatagan@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation;
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; If not, see <http://www.gnu.org/licenses/>.

import random
import math
from location import Location
from node import Node
from node import Gateway
from node import TrafficType
from packet import Packet


class Topology:
    def __init__(self):
        self.gateway_list = []
        self.node_list = []
        self.radius = 0

    def get_node(self, id):
        return self.node_list[id - len(self.gateway_list) - 1]

    def get_gateway(self, id):
        return self.gateway_list[id - 1]

    def show(self):
        print('Nodes:')
        for gateway in self.gateway_list:
            print(' {}'.format(gateway))
        for node in self.node_list:
            print(' {}'.format(node))

    def get_get_nearest_gw(self, location):
        nearestGateway = None
        nearestDistance = None
        for gateway in self.gateway_list:
            distance = Location.get_distance(gateway.location, location)
            if nearestGateway is None:
                nearestGateway = gateway
                nearestDistance = distance
            elif distance < nearestDistance:
                nearestGateway = gateway
                nearestDistance = distance
        return nearestGateway, nearestDistance

    @staticmethod
    def create_random_topology(number_of_nodes, node_traffic_proportions, radius, number_of_gws=1):
        assert 1 <= number_of_nodes <= 100000, 'unsupported number of nodes {}'.format(number_of_nodes)
        assert 10 <= radius <= 40000, 'unsupported radius {}'.format(radius)
        assert 1 <= number_of_gws <= 4, 'unsupported number of gateways {}'.format(number_of_gws)
        assert sum(node_traffic_proportions) == 1, 'invalid node traffic proportions {}'.format(node_traffic_proportions)

        topology = Topology()
        topology.radius = radius

        if number_of_gws == 1:
            topology.gateway_list.append(Gateway(location=Location(0, 0)))
        elif number_of_gws == 2:
            a = radius/2.0
            topology.gateway_list.append(Gateway(location=Location(a, 0)))
            topology.gateway_list.append(Gateway(location=Location(-a, 0)))
        elif number_of_gws == 3:
            a = radius/(2.0 + math.sqrt(3))
            b = math.sqrt(3) * a
            c = 2 * a
            topology.gateway_list.append(Gateway(location=Location(-b, -a)))
            topology.gateway_list.append(Gateway(location=Location(b, -a)))
            topology.gateway_list.append(Gateway(location=Location(0, c)))
        elif number_of_gws == 4:
            a = radius/(1.0 + math.sqrt(2))
            topology.gateway_list.append(Gateway(location=Location(a, a)))
            topology.gateway_list.append(Gateway(location=Location(a, -a)))
            topology.gateway_list.append(Gateway(location=Location(-a, a)))
            topology.gateway_list.append(Gateway(location=Location(-a, -a)))

        while len(topology.node_list) < number_of_nodes:
            x = random.randint(-radius, radius)
            y = random.randint(-radius, radius)
            if (x ** 2 + y ** 2) > (radius ** 2):
                continue

            node = Node(location=Location(x, y))
            topology.node_list.append(node)

        # Assign traffic generation types
        for type_index, proportion in enumerate(node_traffic_proportions):
            assigned = 0
            while assigned < math.floor(proportion * number_of_nodes):
                randomIndex = random.randint(0, number_of_nodes - 1)
                if topology.node_list[randomIndex].trafficType is None:
                    topology.node_list[randomIndex].trafficType = TrafficType(type_index)
                    assigned = assigned + 1
        for tx_node in topology.node_list:
            if tx_node.trafficType is None:
                tx_node.trafficType = TrafficType.Poisson

        # Find the lowest SF for nodes
        for tx_node in topology.node_list:
            _, nearestDistance = topology.get_get_nearest_gw(tx_node.location)
            tx_node.lowestSf = Packet.get_lowest_sf(distance=nearestDistance)

        return topology
