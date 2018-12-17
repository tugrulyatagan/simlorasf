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
from packet import PacketSf

# All units are SI base units
TOPOLOGY_RADIUS = 10000  # meters
SIMULATION_DURATION = 3600  # seconds
PACKET_RATE = 0.005  # per second
PACKET_SIZE = 60  # bytes, header + payload, 13 + max(51 to 222)
random.seed(42)  # for now seed is constant


topology = Topology.create_random_topology(node_number=10, radius=TOPOLOGY_RADIUS)
# topology.write_to_file('output/topology.txt')

simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.sf12)
simulation.run()
# simulation.write_events_to_file('output/events.txt')
simulation.show_results()

# node_number_list = range(50, 1001, 50)
# sf_list = [PacketSf.sf7, PacketSf.sf8, PacketSf.sf9, PacketSf.sf10, PacketSf.sf11, PacketSf.sf12]
# pdr_result_list = []
# for sf_index, sf in enumerate(sf_list):
#     n_result_list = []
#     for n in node_number_list:
#         topology = Topology.create_random_topology(node_number=n, radius=TOPOLOGY_RADIUS)
#         simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=sf)
#         simulation_result = simulation.run()
#         n_result_list.append(simulation_result.pdr)
#     pdr_result_list.append(n_result_list)
#     plt.plot(node_number_list, n_result_list, label=sf.name)
#
# plt.ylim(bottom=0)
# plt.xlim([0, 1000])
# plt.xlabel('Node Number', fontsize=18)
# plt.ylabel('PDR', fontsize=18)
# plt.title('topology_radius={}, packet_rate={}, simulation_duration={}'.format(TOPOLOGY_RADIUS, PACKET_RATE, SIMULATION_DURATION))
# plt.grid(True)
# plt.legend(loc='upper right', fontsize='small')
# plt.savefig('output/sf.png', dpi=200)
# plt.show()

