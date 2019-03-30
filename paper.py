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
import sys
from matplotlib import rcParams
rcParams['font.family'] = 'serif'
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from topology import Topology
from simulation import Simulation
from packet import PacketSf

random.seed(42)  # for now seed is constant

# All units are SI base units
TOPOLOGY_RADIUS = 3000  # meters
GW_NUMBER = 1
PRED_TOPOLOGY_RADIUS = 5000  # meters
PRED_GW_NUMBER = 3
SIMULATION_DURATION = 3600  # seconds
PACKET_RATE = 0.01  # per second
PACKET_SIZE = 60  # bytes, header + payload, 13 + max(51 to 222)
AVERAGING = 5

# NODE_NUMBER = 100
#
# topology = Topology.create_random_topology(node_number=NODE_NUMBER, radius=TOPOLOGY_RADIUS, gw_number=GW_NUMBER)
# # topology.show()
#
# simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Random)
# simulation.run()
# simulation.show_results()
# # simulation.write_to_file('output/sim.txt')
#
# X_train, X_test, y_train, y_test = simulation.get_training_data()
#
# # classifier = svm.SVC(class_weight='balanced', gamma='auto')
# classifier = DecisionTreeClassifier(class_weight='balanced')
# classifier.fit(X_train, y_train)
# y_pred = classifier.predict(X_test)
# print(classification_report(y_test, y_pred))
# print(confusion_matrix(y_test, y_pred, labels=[1, 2, 3]))
# print ("Accuracy is {:.3f} %".format(accuracy_score(y_test,y_pred)*100))
#
# simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Smart, sfPredictor=classifier.predict)
# simulation.run()
# simulation.show_results()
#
# simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Lowest)
# simulation.run()
# simulation.show_results()


for radius in [3000, 5000, 7000, 10000]:
    for node_number in [100, 500, 1000]:
        prediction_dt_acc_averaging_sum = 0
        prediction_svm_acc_averaging_sum = 0
        topology = Topology.create_random_topology(node_number=node_number, radius=radius, gw_number=PRED_GW_NUMBER)

        for repeat in range(AVERAGING):
            simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Random)
            simulation_result = simulation.run()

            X_train, X_test, y_train, y_test = simulation.get_training_data(test_size=0.2)

            DT_classifier = DecisionTreeClassifier(class_weight='balanced')
            DT_classifier.fit(X_train, y_train)
            y_pred = DT_classifier.predict(X_test)
            prediction_dt_acc_averaging_sum += accuracy_score(y_test, y_pred) * 100

            SVM_classifier = svm.SVC(class_weight='balanced', gamma='auto')
            SVM_classifier.fit(X_train, y_train)
            y_pred = SVM_classifier.predict(X_test)
            prediction_svm_acc_averaging_sum += accuracy_score(y_test, y_pred) * 100

        print('node_number={}, radius={}'.format(node_number, radius))
        print('accuracy S={:.1f}, D={:.1f}'.format(prediction_svm_acc_averaging_sum/AVERAGING, prediction_dt_acc_averaging_sum/AVERAGING))


for radius in [3000, 5000, 7000, 10000]:
    for node_number in [100, 500, 1000]:
        prediction_dt_pdr_averaging_sum = 0
        prediction_svm_pdr_averaging_sum = 0
        lowest_pdr_averaging_sum = 0
        topology = Topology.create_random_topology(node_number=node_number, radius=radius, gw_number=PRED_GW_NUMBER)

        for repeat in range(AVERAGING):
            simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Random)
            simulation_result = simulation.run()

            X_train, X_test, y_train, y_test = simulation.get_training_data(test_size=0)

            DT_classifier = DecisionTreeClassifier(class_weight='balanced')
            DT_classifier.fit(X_train, y_train)

            SVM_classifier = svm.SVC(class_weight='balanced', gamma='auto')
            SVM_classifier.fit(X_train, y_train)

            simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Smart, sfPredictor=DT_classifier.predict)
            simulation_result = simulation.run()
            prediction_dt_pdr_averaging_sum += simulation_result.pdr

            simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Smart, sfPredictor=SVM_classifier.predict)
            simulation_result = simulation.run()
            prediction_svm_pdr_averaging_sum += simulation_result.pdr

            simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Lowest)
            simulation_result = simulation.run()
            lowest_pdr_averaging_sum += simulation_result.pdr

        print('node_number={}, radius={}'.format(node_number, radius))
        print('pdr L={:.1f}, S={:.1f}, D={:.1f}'.format(lowest_pdr_averaging_sum/AVERAGING, prediction_svm_pdr_averaging_sum/AVERAGING, prediction_dt_pdr_averaging_sum/AVERAGING))


node_number_list = range(50, 1001, 50)

plt.figure()
random_pdr_list = []
prediction_dt_pdr_list = []
prediction_svm_pdr_list = []
lowest_pdr_list = []
for node_number in node_number_list:
    random_pdr_averaging_sum = 0
    prediction_dt_pdr_averaging_sum = 0
    prediction_svm_pdr_averaging_sum = 0
    lowest_pdr_averaging_sum = 0
    sys.stdout.write('.')
    sys.stdout.flush()
    topology = Topology.create_random_topology(node_number=node_number, radius=PRED_TOPOLOGY_RADIUS, gw_number=PRED_GW_NUMBER)

    for repeat in range(AVERAGING):
        simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Random)
        simulation_result = simulation.run()
        random_pdr_averaging_sum += simulation_result.pdr

        X_train, X_test, y_train, y_test = simulation.get_training_data(test_size=0)

        DT_classifier = DecisionTreeClassifier(class_weight='balanced')
        DT_classifier.fit(X_train, y_train)

        SVM_classifier = svm.SVC(class_weight='balanced', gamma='auto')
        SVM_classifier.fit(X_train, y_train)

        simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Smart, sfPredictor=DT_classifier.predict)
        simulation_result = simulation.run()
        prediction_dt_pdr_averaging_sum += simulation_result.pdr

        simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Smart, sfPredictor=SVM_classifier.predict)
        simulation_result = simulation.run()
        prediction_svm_pdr_averaging_sum += simulation_result.pdr

        simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Lowest)
        simulation_result = simulation.run()
        lowest_pdr_averaging_sum += simulation_result.pdr

    random_pdr_list.append(float(random_pdr_averaging_sum)/AVERAGING)
    prediction_dt_pdr_list.append(float(prediction_dt_pdr_averaging_sum) / AVERAGING)
    prediction_svm_pdr_list.append(float(prediction_svm_pdr_averaging_sum) / AVERAGING)
    lowest_pdr_list.append(float(lowest_pdr_averaging_sum)/AVERAGING)

plt.plot(node_number_list, random_pdr_list, label=PacketSf.SF_Random.name)
plt.plot(node_number_list, prediction_dt_pdr_list, label='SF_Smart_DTC')
plt.plot(node_number_list, prediction_svm_pdr_list, label='SF_Smart_SVM')
plt.plot(node_number_list, lowest_pdr_list, label=PacketSf.SF_Lowest.name)
plt.xlim([0, 1000])
plt.xlabel('Number of nodes')
plt.ylabel('PDR (%)')
# plt.title('topology_radius={}, packet_rate={}, gw_number={}'.format(PRED_TOPOLOGY_RADIUS, PACKET_RATE, PRED_GW_NUMBER))
plt.grid(True)
plt.legend(loc='upper right', fontsize='small', title="SF")
plt.tight_layout()
plt.savefig('output/prediction_pdr_r{}_g{}_p{}_s{}.png'.format(PRED_TOPOLOGY_RADIUS, PRED_GW_NUMBER, PACKET_RATE, SIMULATION_DURATION), dpi=200, transparent=True)


plt.figure()
sf_list = [PacketSf.SF_7, PacketSf.SF_8, PacketSf.SF_9, PacketSf.SF_10, PacketSf.SF_11, PacketSf.SF_12, PacketSf.SF_Lowest, PacketSf.SF_Random]
for sf in sf_list:
    sys.stdout.write('\n{} '.format(sf))
    sys.stdout.flush()
    n_pdr_list = []
    for node_number in node_number_list:
        sys.stdout.write('.')
        sys.stdout.flush()
        pdr_averaging_sum = 0
        for repeat in range(AVERAGING):
            topology = Topology.create_random_topology(node_number=node_number, radius=TOPOLOGY_RADIUS, gw_number=GW_NUMBER)
            simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=sf)
            simulation_result = simulation.run()
            pdr_averaging_sum += simulation_result.pdr
        n_pdr_list.append(float(pdr_averaging_sum)/AVERAGING)
    plt.plot(node_number_list, n_pdr_list, label=sf.name)
plt.ylim(bottom=0)
plt.xlim([0, 1000])
plt.xlabel('Number of nodes')
plt.ylabel('PDR (%)')
# plt.title('topology_radius={}, packet_rate={}, gw_number=1'.format(TOPOLOGY_RADIUS, PACKET_RATE))
plt.grid(True)
plt.legend(loc='upper right', fontsize='small', title="SF", ncol=2)
plt.tight_layout()
plt.savefig('output/sf_pdr_r{}_g{}_p{}_s{}.png'.format(TOPOLOGY_RADIUS, GW_NUMBER, PACKET_RATE, SIMULATION_DURATION), dpi=200, transparent=True)


plt.figure()
gw_number_list = range(1, 5)
for gw_number in gw_number_list:
    sys.stdout.write('\n{} '.format(gw_number))
    sys.stdout.flush()
    n_pdr_list = []
    for node_number in node_number_list:
        sys.stdout.write('.')
        sys.stdout.flush()
        pdr_averaging_sum = 0
        for repeat in range(AVERAGING):
            topology = Topology.create_random_topology(node_number=node_number, radius=TOPOLOGY_RADIUS, gw_number=gw_number)
            simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Lowest)
            simulation_result = simulation.run()
            pdr_averaging_sum += simulation_result.pdr
        n_pdr_list.append(float(pdr_averaging_sum)/AVERAGING)
    plt.plot(node_number_list, n_pdr_list, label=gw_number)
plt.xlim([0, 1000])
plt.xlabel('Number of nodes')
plt.ylabel('PDR (%)')
# plt.title('topology_radius={}, packet_rate={}, sf=lowest'.format(TOPOLOGY_RADIUS, PACKET_RATE))
plt.grid(True)
plt.legend(fontsize='small', title="Number of GWs")
plt.tight_layout()
plt.savefig('output/gw_pdr_r{}_p{}_s{}.png'.format(TOPOLOGY_RADIUS, PACKET_RATE, SIMULATION_DURATION), dpi=200, transparent=True)


plt.figure()
radius_list = range(1000, 11001, 2000)
for radius in radius_list:
    sys.stdout.write('\n{} '.format(radius))
    sys.stdout.flush()
    n_pdr_list = []
    for node_number in node_number_list:
        sys.stdout.write('.')
        sys.stdout.flush()
        pdr_averaging_sum = 0
        for repeat in range(AVERAGING):
            topology = Topology.create_random_topology(node_number=node_number, radius=radius, gw_number=GW_NUMBER)
            simulation = Simulation(topology=topology, packet_rate=PACKET_RATE, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Lowest)
            simulation_result = simulation.run()
            pdr_averaging_sum += simulation_result.pdr
        n_pdr_list.append(float(pdr_averaging_sum)/AVERAGING)
    plt.plot(node_number_list, n_pdr_list, label=radius)

plt.xlim([0, 1000])
plt.xlabel('Number of nodes')
plt.ylabel('PDR (%)')
# plt.title('packet_rate={}, gw_number={}, sf=lowest'.format(PACKET_RATE, GW_NUMBER))
plt.grid(True)
plt.legend(fontsize='small', title="Radius (m)")
plt.tight_layout()
plt.savefig('output/r_pdr_g{}_p{}_s{}.png'.format(GW_NUMBER, PACKET_RATE, SIMULATION_DURATION), dpi=200, transparent=True)


plt.figure()
packet_rate_list = [0.005, 0.01, 0.02, 0.04, 0.08]
for packet_rate in packet_rate_list:
    sys.stdout.write('\n{} '.format(packet_rate))
    sys.stdout.flush()
    n_pdr_list = []
    for node_number in node_number_list:
        sys.stdout.write('.')
        sys.stdout.flush()
        pdr_averaging_sum = 0
        for repeat in range(AVERAGING):
            topology = Topology.create_random_topology(node_number=node_number, radius=TOPOLOGY_RADIUS, gw_number=GW_NUMBER)
            simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=PACKET_SIZE, simulation_duration=SIMULATION_DURATION, sf=PacketSf.SF_Lowest)
            simulation_result = simulation.run()
            pdr_averaging_sum += simulation_result.pdr
        n_pdr_list.append(float(pdr_averaging_sum)/AVERAGING)
    plt.plot(node_number_list, n_pdr_list, label=packet_rate)
plt.ylim(bottom=0)
plt.xlim([0, 1000])
plt.xlabel('Number of nodes')
plt.ylabel('PDR (%)')
# plt.title('topology_radius={}, gw_number={}, sf=lowest'.format(TOPOLOGY_RADIUS, GW_NUMBER))
plt.grid(True)
plt.legend(fontsize='small', title="Packet Rate (pps)")
plt.tight_layout()
plt.savefig('output/pr_pdr_r{}_g{}_s{}.png'.format(TOPOLOGY_RADIUS, GW_NUMBER, SIMULATION_DURATION), dpi=200, transparent=True)
