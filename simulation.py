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

import bisect
from packet import PacketStatus
from location import Location
from node import Node


class SimulationResult:
    def __init__(self):
        self.total = 0
        self.successful = 0
        self.under_sensitivity = 0
        self.interference = 0
        self.pdr = 0


class Simulation:
    def __init__(self, topology, packet_rate, packet_size, simulation_duration, sf):
        self.eventQueue = []
        self.topology = topology
        self.currentTime = 0
        self.packetRate = packet_rate
        self.packetSize = packet_size
        self.simulationDuration = simulation_duration
        self.simulationResult = SimulationResult()
        self.sf = sf
        Node.idCounter = 0

    def add_to_event_queue(self, packet):
        if packet is not None:
            bisect.insort_left(self.eventQueue, packet)

    def show_events(self):
        for event in self.eventQueue:
            print('{}'.format(event))

    def show_results(self):
        print('Results:')
        print(' Total transmission: {}'.format(self.simulationResult.total))
        print(' Successful transmission: {}'.format(self.simulationResult.successful))
        print(' Lost due to under sensitivity: {}'.format(self.simulationResult.under_sensitivity))
        print(' Lost due to interference: {}'.format(self.simulationResult.interference))
        print(' PDR: {}'.format(self.simulationResult.pdr))

    def write_events_to_file(self, file_name):
        with open(file_name, 'w') as file:
            for event in self.eventQueue:
                file.write('{}\n'.format(event))

    def run(self):
        # schedule initial node transmissions
        for tx_node in self.topology.node_list:
            self.add_to_event_queue(tx_node.schedule_tx(packet_rate=self.packetRate, packet_size=self.packetSize, simulation_duration=self.simulationDuration, sf=self.sf))

        for event_index, event in enumerate(self.eventQueue):
            tx_node = self.topology.get_node(event.source)

            rx_gw_list = []
            # Check which gateways can receive
            for gw in self.topology.gateway_list:
                distance_to_gw = Location.get_distance(tx_node.location, gw.location)
                if distance_to_gw > event.receive_radius:
                    # print('Under sensitivity for packet {} at gw {}'.format(event, gw.id))
                    pass
                else:
                    rx_gw_list.append(gw)

            if not rx_gw_list:
                # No gateway received the packet
                event.status = PacketStatus.under_sensitivity
            elif event.status == PacketStatus.pending:
                # Check overlapping events
                for next_event_index in range(event_index+1, len(self.eventQueue)):
                    next_event = self.eventQueue[next_event_index]
                    if (event.time + event.duration) < next_event.time:
                        break
                    # Events are overlapping
                    next_event_node = self.topology.get_node(next_event.source)
                    # print('{} and {} are overlapping'.format(event, next_event))

                    # Check for interference at gateways
                    for rx_gw in rx_gw_list:
                        # Measure distance between interferer and gateways
                        if event.is_interfered_by(next_event, self.topology, rx_gw.location):
                            # print('{} is interfered by {}'.format(event, next_event))
                            event.status = PacketStatus.interfered
                        else:
                            # print('{} is interfered by {}'.format(next_event, event))
                            next_event.status = PacketStatus.interfered

            if event.status == PacketStatus.pending:
                event.status = PacketStatus.transmitted

            # Schedule next event for this node
            self.add_to_event_queue(tx_node.schedule_tx(packet_rate=self.packetRate, packet_size=self.packetSize, simulation_duration=self.simulationDuration, sf=self.sf))

        # Collect statistics
        for event in self.eventQueue:
            self.simulationResult.total += 1
            if event.status == PacketStatus.under_sensitivity:
                self.simulationResult.under_sensitivity += 1
            elif event.status == PacketStatus.interfered:
                self.simulationResult.interference += 1
            elif event.status == PacketStatus.transmitted:
                self.simulationResult.successful += 1
        self.simulationResult.pdr = self.simulationResult.successful / self.simulationResult.total

        return self.simulationResult