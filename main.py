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
import matplotlib.pyplot as plt
from topology import Topology
from simulation import Simulation

# All units are SI base units
NODE_NUMBER = 10
TOPOLOGY_RADIUS = 10500  # meters
SIMULATION_DURATION = 3600  # seconds
PACKET_RATE = 0.005  # per second
PACKET_SIZE = 60  # bytes, header + payload, 13 + max(51 to 222)
random.seed(42)  # for now seed is constant


# topology = Topology.create_random_topology(node_number=NODE_NUMBER, radius=TOPOLOGY_RADIUS)
# # topology.write_to_file('output/topology.txt')
#
# simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION)
# simulation.run()
# # simulation.write_events_to_file('output/events.txt')
# simulation.show_results()

node_number_list = range(50, 1000, 50)
results = []
for n in node_number_list:
    topology = Topology.create_random_topology(node_number=n, radius=TOPOLOGY_RADIUS)
    simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION)
    results.append(simulation.run())

pdr_list = [result.pdr for result in results]

plt.plot(node_number_list, pdr_list)
plt.show()
