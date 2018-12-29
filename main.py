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
# import matplotlib.pyplot as plt
from topology import Topology
from simulation import Simulation
from packet import PacketSf
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


# All units are SI base units
TOPOLOGY_RADIUS = 8000  # meters
NODE_NUMBER = 500
GW_NUMBER = 1
SIMULATION_DURATION = 36000  # seconds
PACKET_RATE = 0.01  # per second
PACKET_SIZE = 60  # bytes, header + payload, 13 + max(51 to 222)
AVERAGING = 5
random.seed(42)  # for now seed is constant


topology = Topology.create_random_topology(node_number=NODE_NUMBER, radius=TOPOLOGY_RADIUS, gw_number=GW_NUMBER)
# topology.show()

simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.random)
simulation.run()
simulation.show_results()
# simulation.write_to_file('output/sim.txt')

X_train, X_test, y_train, y_test = simulation.get_training_data()
classifier = DecisionTreeClassifier()
# classifier = DecisionTreeClassifier(criterion = "gini", random_state = 100,max_depth=3, min_samples_leaf=5)
# classifier = DecisionTreeClassifier(criterion = "entropy", random_state = 100, max_depth = 3, min_samples_leaf = 5)
classifier.fit(X_train, y_train)
y_pred = classifier.predict(X_test)
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred, labels=[1,2,3]))
print ("Accuracy is {:.3f} %".format(accuracy_score(y_test,y_pred)*100))

simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.predictor, sfPredictor=classifier.predict)
simulation.run()
simulation.show_results()

simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.predictor, sfPredictor=classifier.predict)
simulation.run()
simulation.show_results()

simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.lowest)
simulation.run()
simulation.show_results()



# node_number_list = range(50, 1001, 50)
#
# plt.figure()
# sf_list = [PacketSf.sf7, PacketSf.sf8, PacketSf.sf9, PacketSf.sf10, PacketSf.sf11, PacketSf.sf12, PacketSf.lowest, PacketSf.random]
# for sf in sf_list:
#     n_pdr_list = []
#     for node_number in node_number_list:
#         pdr_averaging_sum = 0
#         for repeat in range(AVERAGING):
#             topology = Topology.create_random_topology(node_number=node_number, radius=TOPOLOGY_RADIUS)
#             simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=sf)
#             simulation_result = simulation.run()
#             pdr_averaging_sum += simulation_result.pdr
#         n_pdr_list.append(float(pdr_averaging_sum)/AVERAGING)
#     plt.plot(node_number_list, n_pdr_list, label=sf.name)
# plt.ylim(bottom=0)
# plt.xlim([0, 1000])
# plt.xlabel('Node Number', fontsize=18)
# plt.ylabel('PDR (%)', fontsize=18)
# plt.title('topology_radius={}, packet_rate={}, gw_number=1'.format(TOPOLOGY_RADIUS, PACKET_RATE))
# plt.grid(True)
# plt.legend(loc='upper right', fontsize='small', title="SF")
# plt.savefig('output/sf_pdr.png', dpi=200)
#
# plt.figure()
# gw_number_list = range(1, 5)
# for gw_number in gw_number_list:
#     n_pdr_list = []
#     for node_number in node_number_list:
#         pdr_averaging_sum = 0
#         for repeat in range(AVERAGING):
#             topology = Topology.create_random_topology(node_number=node_number, radius=TOPOLOGY_RADIUS, gw_number=gw_number)
#             simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.lowest)
#             simulation_result = simulation.run()
#             pdr_averaging_sum += simulation_result.pdr
#         n_pdr_list.append(float(pdr_averaging_sum)/AVERAGING)
#     plt.plot(node_number_list, n_pdr_list, label=gw_number)
# plt.ylim(bottom=0)
# plt.xlim([0, 1000])
# plt.xlabel('Node Number', fontsize=18)
# plt.ylabel('PDR (%)', fontsize=18)
# plt.title('topology_radius={}, packet_rate={}, sf=lowest'.format(TOPOLOGY_RADIUS, PACKET_RATE))
# plt.grid(True)
# plt.legend(fontsize='small', title="GW Number")
# plt.savefig('output/gw_pdr.png', dpi=200)
#
# plt.figure()
# radius_list = range(1000, 11001, 2000)
# for radius in radius_list:
#     n_pdr_list = []
#     for node_number in node_number_list:
#         pdr_averaging_sum = 0
#         for repeat in range(AVERAGING):
#             topology = Topology.create_random_topology(node_number=node_number, radius=radius)
#             simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.lowest)
#             simulation_result = simulation.run()
#             pdr_averaging_sum += simulation_result.pdr
#         n_pdr_list.append(float(pdr_averaging_sum)/AVERAGING)
#     plt.plot(node_number_list, n_pdr_list, label=radius)
#
# plt.ylim(bottom=0)
# plt.xlim([0, 1000])
# plt.xlabel('Node Number', fontsize=18)
# plt.ylabel('PDR (%)', fontsize=18)
# plt.title('packet_rate={}, gw_number=1, sf=lowest'.format(PACKET_RATE))
# plt.grid(True)
# plt.legend(fontsize='small', title="Radius (m)")
# plt.savefig('output/r_pdr.png', dpi=200)
#
# plt.figure()
# packet_rate_list = [0.005, 0.01, 0.02, 0.04, 0.08]
# for packet_rate in packet_rate_list:
#     n_pdr_list = []
#     for node_number in node_number_list:
#         pdr_averaging_sum = 0
#         for repeat in range(AVERAGING):
#             topology = Topology.create_random_topology(node_number=node_number, radius=TOPOLOGY_RADIUS)
#             simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.lowest)
#             simulation_result = simulation.run()
#             pdr_averaging_sum += simulation_result.pdr
#         n_pdr_list.append(float(pdr_averaging_sum)/AVERAGING)
#     plt.plot(node_number_list, n_pdr_list, label=packet_rate)
# plt.ylim(bottom=0)
# plt.xlim([0, 1000])
# plt.xlabel('Node Number', fontsize=18)
# plt.ylabel('PDR (%)', fontsize=18)
# plt.title('topology_radius={}, gw_number=1, sf=lowest'.format(TOPOLOGY_RADIUS))
# plt.grid(True)
# plt.legend(fontsize='small', title="Packet Rate (/sec)")
# plt.savefig('output/pr_pdr.png', dpi=200)
