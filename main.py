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
TOPOLOGY_RADIUS = 10000  # meters
SIMULATION_DURATION = 300  # seconds
PACKET_RATE = 1  # arrivals per second
PACKET_SIZE = 70  # should be between 51 and 222

random.seed(42)  # for now seed is constant


class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def get_distance(a, b):
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


class PacketStatus:
    pending = 0
    in_transmission = 1
    transmitted = 2
    interfered = 3
    under_sensitivity = 4


class Packet:
    def __init__(self, time, sf, source, destination=0):
        self.time = time
        self.sf = sf
        self.duration = 0.005  # s
        self.source = source
        self.destination = destination
        self.status = PacketStatus.pending


class Node:
    idCounter = 0

    def __init__(self, location):
        self.location = location
        Node.idCounter += 1
        self.id = Node.idCounter
        self.txList = []
        self.rxList = []

    @staticmethod
    def calculate_transmission_duration(self, sf, size):
        if sf == 7:
            pass
        elif sf == 8:
            pass
        elif sf == 9:
            pass
        elif sf == 10:
            pass
        elif sf == 11:
            pass
        elif sf == 12:
            pass

    def schedule_tx(self):
        if len(self.txList) == 0:
            next_time = random.expovariate(PACKET_RATE)
        else:
            next_time = self.txList[-1].time + random.expovariate(PACKET_RATE)

        if next_time > SIMULATION_DURATION:
            return

        new_packet = Packet(time=next_time, sf=12, source=self.id)
        self.txList.append(new_packet)

        print(new_packet.time)


class Gateway(Node):
    def __init__(self, location):
        Node.__init__(self, location)


class Topology:
    def __init__(self):
        self.gateway_list = []
        self.node_list = []

    def write_to_file(self, file_name):
        with open(file_name, 'w') as file:
            for gateway in self.gateway_list:
                file.write('g {} {},{}\n'.format(gateway.id, gateway.location.x, gateway.location.y))
            for node in self.node_list:
                file.write('n {} {},{}\n'.format(node.id, node.location.x, node.location.y))

    def show(self):
        for gateway in self.gateway_list:
            print('g {} {},{}'.format(gateway.id, gateway.location.x, gateway.location.y))
        for node in self.node_list:
            print('n {} {},{}'.format(node.id, node.location.x, node.location.y))

    @staticmethod
    def create_random_topology(node_number, radius):
        topology = Topology()

        gateway = Gateway(location=Location(0, 0))
        topology.gateway_list.append(gateway)

        for n in range(node_number):
            x = random.randint(-radius, radius)
            y = random.randint(-radius, radius)
            node = Node(location=Location(x, y))
            topology.node_list.append(node)

        return topology


class Simulation:
    def __init__(self, topology):
        self.eventQueue = []
        self.topology = topology

    def run(self):
        # schedule initial node transmissions
        for n in self.topology.node_list:
            n.schedule_tx()



topology = Topology.create_random_topology(node_number=NODE_NUMBER, radius=TOPOLOGY_RADIUS)
topology.show()
topology.write_to_file('topology.txt')

simulation = Simulation(topology)
simulation.run()
