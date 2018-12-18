#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2018  Tugrul Yatagan <tugrulyatagan@gmail.com>
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
from location import Location
from node import Node
from node import Gateway
from packet import Packet


class Topology:
    def __init__(self):
        self.gateway_list = []
        self.node_list = []

    def get_node(self, id):
        return self.node_list[id - len(self.gateway_list) - 1]

    def get_gateway(self, id):
        return self.gateway_list[id - 1]

    def write_to_file(self, file_name):
        with open(file_name, 'w') as file:
            for gateway in self.gateway_list:
                file.write('{}\n'.format(gateway))
            for node in self.node_list:
                file.write('{}\n'.format(node))

    def show(self):
        for gateway in self.gateway_list:
            print('{}'.format(gateway))
        for node in self.node_list:
            print('{}'.format(node))

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
    def create_random_topology(node_number, radius):
        topology = Topology()

        gateway = Gateway(location=Location(0, 0))
        topology.gateway_list.append(gateway)

        while len(topology.node_list) < node_number:
            x = random.randint(-radius, radius)
            y = random.randint(-radius, radius)
            if (x ** 2 + y ** 2) > (radius ** 2):
                continue
            node = Node(location=Location(x, y))
            topology.node_list.append(node)

        # Find lowest SF for nodes
        for tx_node in topology.node_list:
            _, nearestDistance = topology.get_get_nearest_gw(tx_node.location)
            tx_node.lowestSf = Packet.get_lowest_sf(distance=nearestDistance)

        return topology