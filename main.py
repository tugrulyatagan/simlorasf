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

import math
import random

NODE_NUMBER = 10
TOPOLOGY_RADIUS = 10000
random.seed(42)


class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def get_distance(a, b):
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


class Node:
    def __init__(self, location=None):
        if location is None:
            self.location = Location(0, 0)
        else:
            self.location = location


class Gateway:
    def __init__(self, location=None):
        if location is None:
            self.location = Location(0, 0)
        else:
            self.location = location


class Topology:
    def __init__(self):
        self.gateway_list = []
        self.node_list = []

    def write_to_file(self, file_name):
        with open(file_name, 'w') as file:
            for gateway in self.gateway_list:
                file.write('g {},{}\n'.format(gateway.location.x, gateway.location.y))
            for node in self.node_list:
                file.write('n {},{}\n'.format(node.location.x, node.location.y))

    def show(self):
        for gateway in self.gateway_list:
            print('g {},{}'.format(gateway.location.x, gateway.location.y))
        for node in self.node_list:
            print('n {},{}'.format(node.location.x, node.location.y))

    @staticmethod
    def create_random_topology(node_number, radius):
        topology = Topology()

        gateway = Gateway()
        topology.gateway_list.append(gateway)

        for n in range(node_number):
            x = random.randint(-radius, radius)
            y = random.randint(-radius, radius)
            node = Node(location=Location(x, y))
            topology.node_list.append(node)

        return topology


class Event:
    def __init__(self):
        pass


class Simulation:
    def __init__(self):
        pass


topology = Topology.create_random_topology(node_number=NODE_NUMBER, radius=TOPOLOGY_RADIUS)
topology.show()
topology.write_to_file('topology.txt')
