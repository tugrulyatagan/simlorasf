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
import bisect

# All units are SI base units

NODE_NUMBER = 10
TOPOLOGY_RADIUS = 10000  # meters
SIMULATION_DURATION = 15  # seconds
PACKET_RATE = 0.5  # arrivals per second
PACKET_SIZE = 70  # should be between 51 and 222

random.seed(42)  # for now seed is constant


class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return '({},{})'.format(self.x, self.y)

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
    def __init__(self, time, sf, channel, source, destination=0):
        self.time = time
        self.sf = sf
        self.channel = channel
        self.source = source
        self.destination = destination
        self.status = PacketStatus.pending
        self.duration = self.calculate_transmission_duration()
        self.receive_radius = self.calculate_receive_radius()
        self.interference_radius = self.calculate_interference_radius()

    def __lt__(self, other):
        return self.time < other.time

    def __repr__(self):
        return '(t={},src={},dst={},sf={},dur={},stat={})'.format(self.time, self.source, self.destination, self.sf, self.duration, self.status)

    def calculate_transmission_duration(self):
        # TODO
        if self.sf == 7:
            pass
        elif self.sf == 8:
            pass
        elif self.sf == 9:
            pass
        elif self.sf == 10:
            pass
        elif self.sf == 11:
            pass
        elif self.sf == 12:
            pass
        return 0.1

    def calculate_receive_radius(self):
        # TODO
        if self.sf == 7:
            pass
        elif self.sf == 8:
            pass
        elif self.sf == 9:
            pass
        elif self.sf == 10:
            pass
        elif self.sf == 11:
            pass
        elif self.sf == 12:
            pass
        return 3000

    def calculate_interference_radius(self):
        # TODO
        return 3500


class Node:
    idCounter = 0

    def __init__(self, location):
        self.location = location
        Node.idCounter += 1
        self.id = Node.idCounter
        self.txList = []

    def schedule_tx(self):
        # Poisson interval
        if len(self.txList) == 0:
            next_time = random.expovariate(PACKET_RATE)
        else:
            next_time = self.txList[-1].time + random.expovariate(PACKET_RATE)

        if next_time > SIMULATION_DURATION:
            return None

        new_packet = Packet(time=next_time, sf=12, channel=10, source=self.id)
        self.txList.append(new_packet)

        return new_packet


class Gateway(Node):
    def __init__(self, location):
        Node.__init__(self, location)


class Topology:
    def __init__(self):
        self.gateway_list = []
        self.node_list = []

    def get_node(self, id):
        return self.node_list[id - len(self.gateway_list) - 1]

    def write_to_file(self, file_name):
        with open(file_name, 'w') as file:
            for gateway in self.gateway_list:
                file.write('g {} {}\n'.format(gateway.id, gateway.location))
            for node in self.node_list:
                file.write('n {} {}\n'.format(node.id, node.location))

    def show(self):
        for gateway in self.gateway_list:
            print('g {} {}'.format(gateway.id, gateway.location))
        for node in self.node_list:
            print('n {} {}'.format(node.id, node.location))

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
        self.currentTime = 0

    def add_to_event_queue(self, packet):
        if packet is not None:
            bisect.insort_left(self.eventQueue, packet)

    def show_events(self):
        for event in self.eventQueue:
            print('{}'.format(event))

    def write_events_to_file(self, file_name):
        with open(file_name, 'w') as file:
            for event in self.eventQueue:
                file.write('{}\n'.format(event))

    def run(self):
        # schedule initial node transmissions
        for tx_node in self.topology.node_list:
            self.add_to_event_queue(tx_node.schedule_tx())

        for event_index, event in enumerate(self.eventQueue):
            tx_node = self.topology.get_node(event.source)
            event.status = PacketStatus.under_sensitivity

            # Check for interference
            for next_event_index in range(event_index+1, len(self.eventQueue)):
                next_event = self.eventQueue[next_event_index]
                if (event.time + event.duration) < next_event.time:
                    break
                # Events are overlapping
                next_event_node = self.topology.get_node(next_event.source)
                print('[{} @ {}] and [{} @ {}] are overlapping'.format(event, tx_node.location, next_event, next_event_node.location))

                # Measure distance between tx nodes
                distance_between_nodes = Location.get_distance(tx_node.location, next_event_node.location)
                if distance_between_nodes < event.interference_radius or distance_between_nodes < next_event.interference_radius:
                    print('Interference!!! Distance between {} and {} is {}'.format(tx_node.location, next_event_node.location, distance_between_nodes))
                    event.status = PacketStatus.interfered
                    next_event.status = PacketStatus.interfered

            # Check for under sensitivity
            for gw in self.topology.gateway_list:
                distance_to_gw = Location.get_distance(tx_node.location, gw.location)
                if distance_to_gw < event.receive_radius:
                    print('Gateway {} has received the packet {}'.format(gw.id, event))
                    event.status = PacketStatus.transmitted
                else:
                    print('Under sensitivity')


            self.add_to_event_queue(tx_node.schedule_tx())


topology = Topology.create_random_topology(node_number=NODE_NUMBER, radius=TOPOLOGY_RADIUS)
# topology.show()
topology.write_to_file('topology.txt')

simulation = Simulation(topology)
simulation.run()
# simulation.show_events()
simulation.write_events_to_file('events.txt')
