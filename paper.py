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
from simulation import SimulationResult
from packet import PacketSf

random.seed(42)  # for now seed is constant


class SimulationFigure():
    def __init__(self, x_axis, plot_names):
        self.x_axis = x_axis
        self.plot_names = plot_names
        self.plot_data = {}
        for plot_name in self.plot_names:
            self.plot_data[plot_name] = []

    def get_plot(self, xlabel, ylabel, ylim_bottom=None, ylim_top=None, xlim_left=None, xlim_right=None):
        plt.figure()
        for plot_name in self.plot_names:
            plt.plot(self.x_axis, self.plot_data[plot_name], label=plot_name)

        if ylim_bottom is not None:
            plt.ylim(bottom=ylim_bottom)
        if ylim_top is not None:
            plt.ylim(top=ylim_top)
        if xlim_left is not None:
            plt.xlim(left=xlim_left)
        if xlim_right is not None:
            plt.xlim(right=xlim_right)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.tight_layout()


def prediction_accuracy(averaging, number_of_gws, packet_rate, packet_size, simulation_duration, traffic_type):
    for radius in [3000, 5000, 7000, 10000]:
        for number_of_nodes in [100, 500, 1000]:
            prediction_dt_acc_averaging_sum = 0
            prediction_svm_acc_averaging_sum = 0
            topology = Topology.create_random_topology(number_of_nodes=number_of_nodes, radius=radius, number_of_gws=number_of_gws, node_traffic_proportions=traffic_type)

            for repeat in range(averaging):
                simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Random)
                simulation_result = simulation.run()
                # simulation.show_results()
                # simulation.write_to_file('output/sim_r{}_n{}_g{}_p{}_s{}.png'.format(radius, number_of_nodes, number_of_gws, packet_rate, simulation_duration))

                X_train, X_test, y_train, y_test = simulation.get_training_data(test_size=0.2)

                DT_classifier = DecisionTreeClassifier(class_weight='balanced')
                DT_classifier.fit(X_train, y_train)
                y_pred = DT_classifier.predict(X_test)
                prediction_dt_acc_averaging_sum += accuracy_score(y_test, y_pred) * 100
                # print(classification_report(y_test, y_pred))
                # print(confusion_matrix(y_test, y_pred, labels=[1, 2, 3]))

                SVM_classifier = svm.SVC(class_weight='balanced', gamma='auto')
                SVM_classifier.fit(X_train, y_train)
                y_pred = SVM_classifier.predict(X_test)
                prediction_svm_acc_averaging_sum += accuracy_score(y_test, y_pred) * 100
                # print(classification_report(y_test, y_pred))
                # print(confusion_matrix(y_test, y_pred, labels=[1, 2, 3]))

            print('number_of_nodes={}, radius={}'.format(number_of_nodes, radius))
            print('accuracy SVM={:.1f}, DTC={:.1f}'.format(prediction_svm_acc_averaging_sum / averaging, prediction_dt_acc_averaging_sum / averaging))


def prediction_pdr(averaging, number_of_gws, packet_rate, packet_size, simulation_duration, traffic_type):
    for radius in [3000, 5000, 7000, 10000]:
        for number_of_nodes in [100, 500, 1000]:
            prediction_dt_pdr_averaging_sum = 0
            prediction_svm_pdr_averaging_sum = 0
            lowest_pdr_averaging_sum = 0
            topology = Topology.create_random_topology(number_of_nodes=number_of_nodes, radius=radius, number_of_gws=number_of_gws, node_traffic_proportions=traffic_type)

            for repeat in range(averaging):
                simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Random)
                simulation_result = simulation.run()

                X_train, X_test, y_train, y_test = simulation.get_training_data(test_size=0)

                DT_classifier = DecisionTreeClassifier(class_weight='balanced')
                DT_classifier.fit(X_train, y_train)

                SVM_classifier = svm.SVC(class_weight='balanced', gamma='auto')
                SVM_classifier.fit(X_train, y_train)

                simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Smart, sfPredictor=DT_classifier.predict)
                simulation_result = simulation.run()
                prediction_dt_pdr_averaging_sum += simulation_result.pdr

                simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Smart, sfPredictor=SVM_classifier.predict)
                simulation_result = simulation.run()
                prediction_svm_pdr_averaging_sum += simulation_result.pdr

                simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Lowest)
                simulation_result = simulation.run()
                lowest_pdr_averaging_sum += simulation_result.pdr

            print('number_of_nodes={}, radius={}'.format(number_of_nodes, radius))
            print('pdr L={:.1f}, SWM={:.1f}, DTC={:.1f}'.format(lowest_pdr_averaging_sum / averaging, prediction_svm_pdr_averaging_sum / averaging, prediction_dt_pdr_averaging_sum / averaging))


def plot_prediction(number_of_nodes_list, averaging, topology_radius, number_of_gws, packet_rate, packet_size, simulation_duration, traffic_type):
    prediction_name_list = [PacketSf.SF_Random.name, 'SF_Smart_DTC', 'SF_Smart_SVM', PacketSf.SF_Lowest.name]
    prediction_pdr_figure = SimulationFigure(number_of_nodes_list, prediction_name_list)
    prediction_energy_figure = SimulationFigure(number_of_nodes_list, prediction_name_list)
    for number_of_nodes in number_of_nodes_list:
        random_simulation_result_sum = SimulationResult()
        prediction_dt_simulation_result_sum = SimulationResult()
        prediction_svm_simulation_result_sum = SimulationResult()
        lowest_simulation_result_sum = SimulationResult()
        sys.stdout.write('.')
        sys.stdout.flush()
        topology = Topology.create_random_topology(number_of_nodes=number_of_nodes, radius=topology_radius, number_of_gws=number_of_gws, node_traffic_proportions=traffic_type)

        for repeat in range(averaging):
            simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Random)
            random_simulation_result_sum += simulation.run()

            X_train, X_test, y_train, y_test = simulation.get_training_data(test_size=0)

            DT_classifier = DecisionTreeClassifier(class_weight='balanced')
            DT_classifier.fit(X_train, y_train)

            SVM_classifier = svm.SVC(class_weight='balanced', gamma='auto')
            SVM_classifier.fit(X_train, y_train)

            simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Smart, sfPredictor=DT_classifier.predict)
            prediction_dt_simulation_result_sum += simulation.run()

            simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Smart, sfPredictor=SVM_classifier.predict)
            prediction_svm_simulation_result_sum += simulation.run()

            simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Lowest)
            lowest_simulation_result_sum += simulation.run()

        prediction_pdr_figure.plot_data[PacketSf.SF_Random.name].append(float(random_simulation_result_sum.pdr) / averaging)
        prediction_pdr_figure.plot_data['SF_Smart_DTC'].append(float(prediction_dt_simulation_result_sum.pdr) / averaging)
        prediction_pdr_figure.plot_data['SF_Smart_SVM'].append(float(prediction_svm_simulation_result_sum.pdr) / averaging)
        prediction_pdr_figure.plot_data[PacketSf.SF_Lowest.name].append(float(lowest_simulation_result_sum.pdr) / averaging)

        prediction_energy_figure.plot_data[PacketSf.SF_Random.name].append(float(random_simulation_result_sum.txEnergyConsumption) / averaging)
        prediction_energy_figure.plot_data['SF_Smart_DTC'].append(float(prediction_dt_simulation_result_sum.txEnergyConsumption) / averaging)
        prediction_energy_figure.plot_data['SF_Smart_SVM'].append(float(prediction_svm_simulation_result_sum.txEnergyConsumption) / averaging)
        prediction_energy_figure.plot_data[PacketSf.SF_Lowest.name].append(float(lowest_simulation_result_sum.txEnergyConsumption) / averaging)

    prediction_pdr_figure.get_plot(xlabel='Number of nodes', ylabel='PDR (%)', xlim_left=0, xlim_right=1000)
    plt.legend(loc='upper right', fontsize='small', title='SF')
    plt.savefig('output/prediction_pdr_r{}_g{}_p{}_s{}.png'.format(topology_radius, number_of_gws, packet_rate, simulation_duration), dpi=200, transparent=True)

    prediction_energy_figure.get_plot(xlabel='Number of nodes', ylabel='Transmit energy consumption (J)', xlim_left=0, xlim_right=1000)
    plt.legend(loc='upper left', fontsize='small', title='SF')
    plt.savefig('output/prediction_energy_r{}_g{}_p{}_s{}.png'.format(topology_radius, number_of_gws, packet_rate, simulation_duration), dpi=200, transparent=True)


def plot_sf(number_of_nodes_list, averaging, topology_radius, number_of_gws, packet_rate, packet_size, simulation_duration, traffic_type):
    sf_list = [PacketSf.SF_7, PacketSf.SF_8, PacketSf.SF_9, PacketSf.SF_10, PacketSf.SF_11, PacketSf.SF_12, PacketSf.SF_Lowest, PacketSf.SF_Random]
    sf_pdr_figure = SimulationFigure(number_of_nodes_list, [sf.name for sf in sf_list])
    sf_energy_figure = SimulationFigure(number_of_nodes_list, [sf.name for sf in sf_list])

    for sf in sf_list:
        sys.stdout.write('\n{} '.format(sf))
        sys.stdout.flush()
        for number_of_nodes in number_of_nodes_list:
            sys.stdout.write('.')
            sys.stdout.flush()
            simulation_result_sum = SimulationResult()
            for repeat in range(averaging):
                topology = Topology.create_random_topology(number_of_nodes=number_of_nodes, radius=topology_radius, number_of_gws=number_of_gws, node_traffic_proportions=traffic_type)
                simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=sf)
                simulation_result_sum += simulation.run()
            sf_pdr_figure.plot_data[sf.name].append(float(simulation_result_sum.pdr) / averaging)
            sf_energy_figure.plot_data[sf.name].append(float(simulation_result_sum.txEnergyConsumption) / averaging)

    sf_pdr_figure.get_plot(xlabel='Number of nodes', ylabel='PDR (%)', ylim_bottom=0, xlim_left=0, xlim_right=1000)
    plt.legend(loc='upper right', fontsize='small', title='SF', ncol=2)
    plt.savefig('output/sf_pdr_r{}_g{}_p{}_s{}.png'.format(topology_radius, number_of_gws, packet_rate, simulation_duration), dpi=200, transparent=True)

    sf_energy_figure.get_plot(xlabel='Number of nodes', ylabel='Transmit energy consumption (J)', ylim_bottom=0, xlim_left=0, xlim_right=1000)
    plt.legend(loc='upper left', fontsize='small', title='SF', ncol=2)
    plt.savefig('output/sf_energy_r{}_g{}_p{}_s{}.png'.format(topology_radius, number_of_gws, packet_rate, simulation_duration), dpi=200, transparent=True)


def plot_gw(number_of_nodes_list, averaging, topology_radius, packet_rate, packet_size, simulation_duration, traffic_type):
    number_of_gws_list = range(1, 5)
    gw_pdr_figure = SimulationFigure(number_of_nodes_list, number_of_gws_list)
    gw_energy_figure = SimulationFigure(number_of_nodes_list, number_of_gws_list)

    for number_of_gws in number_of_gws_list:
        sys.stdout.write('\n{} '.format(number_of_gws))
        sys.stdout.flush()
        for number_of_nodes in number_of_nodes_list:
            sys.stdout.write('.')
            sys.stdout.flush()
            simulation_result_sum = SimulationResult()
            for repeat in range(averaging):
                topology = Topology.create_random_topology(number_of_nodes=number_of_nodes, radius=topology_radius, number_of_gws=number_of_gws, node_traffic_proportions=traffic_type)
                simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Lowest)
                simulation_result_sum += simulation.run()
            gw_pdr_figure.plot_data[number_of_gws].append(float(simulation_result_sum.pdr) / averaging)
            gw_energy_figure.plot_data[number_of_gws].append(float(simulation_result_sum.txEnergyConsumption) / averaging)

    gw_pdr_figure.get_plot(xlabel='Number of nodes', ylabel='PDR (%)', xlim_left=0, xlim_right=1000)
    plt.legend(fontsize='small', title='Number of GWs')
    plt.savefig('output/gw_pdr_r{}_p{}_s{}.png'.format(topology_radius, packet_rate, simulation_duration), dpi=200, transparent=True)

    gw_energy_figure.get_plot(xlabel='Number of nodes', ylabel='Transmit energy consumption (J)',  xlim_left=0, xlim_right=1000)
    plt.legend(fontsize='small', title='Number of GWs')
    plt.savefig('output/gw_energy_r{}_p{}_s{}.png'.format(topology_radius, packet_rate, simulation_duration), dpi=200, transparent=True)


def plot_r(number_of_nodes_list, averaging, number_of_gws, packet_rate, packet_size, simulation_duration, traffic_type):
    radius_list = range(1000, 11001, 2000)
    r_pdr_figure = SimulationFigure(number_of_nodes_list, radius_list)
    r_energy_figure = SimulationFigure(number_of_nodes_list, radius_list)

    for radius in radius_list:
        sys.stdout.write('\n{} '.format(radius))
        sys.stdout.flush()
        for number_of_nodes in number_of_nodes_list:
            sys.stdout.write('.')
            sys.stdout.flush()
            simulation_result_sum = SimulationResult()
            for repeat in range(averaging):
                topology = Topology.create_random_topology(number_of_nodes=number_of_nodes, radius=radius, number_of_gws=number_of_gws, node_traffic_proportions=traffic_type)
                simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Lowest)
                simulation_result_sum += simulation.run()
            r_pdr_figure.plot_data[radius].append(float(simulation_result_sum.pdr) / averaging)
            r_energy_figure.plot_data[radius].append(float(simulation_result_sum.txEnergyConsumption) / averaging)

    r_pdr_figure.get_plot(xlabel='Number of nodes', ylabel='PDR (%)', xlim_left=0, xlim_right=1000)
    plt.legend(fontsize='small', title='Radius (m)')
    plt.savefig('output/r_pdr_g{}_p{}_s{}.png'.format(number_of_gws, packet_rate, simulation_duration), dpi=200, transparent=True)

    r_energy_figure.get_plot(xlabel='Number of nodes', ylabel='Transmit energy consumption (J)', xlim_left=0, xlim_right=1000)
    plt.legend(fontsize='small', title='Radius (m)')
    plt.savefig('output/r_energy_g{}_p{}_s{}.png'.format(number_of_gws, packet_rate, simulation_duration), dpi=200, transparent=True)


def plot_pr(number_of_nodes_list, averaging, topology_radius, number_of_gws, packet_size, simulation_duration, traffic_type):
    packet_rate_list = [0.005, 0.01, 0.02, 0.04, 0.08]
    pr_pdr_figure = SimulationFigure(number_of_nodes_list, packet_rate_list)
    pr_energy_figure = SimulationFigure(number_of_nodes_list, packet_rate_list)

    for packet_rate in packet_rate_list:
        sys.stdout.write('\n{} '.format(packet_rate))
        sys.stdout.flush()
        for number_of_nodes in number_of_nodes_list:
            sys.stdout.write('.')
            sys.stdout.flush()
            simulation_result_sum = SimulationResult()
            for repeat in range(averaging):
                topology = Topology.create_random_topology(number_of_nodes=number_of_nodes, radius=topology_radius, number_of_gws=number_of_gws, node_traffic_proportions=traffic_type)
                simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Lowest)
                simulation_result_sum += simulation.run()
            pr_pdr_figure.plot_data[packet_rate].append(float(simulation_result_sum.pdr) / averaging)
            pr_energy_figure.plot_data[packet_rate].append(float(simulation_result_sum.txEnergyConsumption) / averaging)

    pr_pdr_figure.get_plot(xlabel='Number of nodes', ylabel='PDR (%)', ylim_bottom=0, xlim_left=0, xlim_right=1000)
    plt.legend(fontsize='small', title='Packet Rate (pps)')
    plt.savefig('output/pr_pdr_r{}_g{}_s{}.png'.format(topology_radius, number_of_gws, simulation_duration), dpi=200, transparent=True)

    pr_energy_figure.get_plot(xlabel='Number of nodes', ylabel='Transmit energy consumption (J)', ylim_bottom=0, xlim_left=0, xlim_right=1000)
    plt.legend(fontsize='small', title='Packet Rate (pps)')
    plt.savefig('output/pr_energy_r{}_g{}_s{}.png'.format(topology_radius, number_of_gws, simulation_duration), dpi=200, transparent=True)


def plot_trfc(number_of_nodes_list, averaging, topology_radius, number_of_gws, packet_rate, packet_size, simulation_duration):
    traffic_type_list = [(1, 0), (0.8, 0.2), (0.5, 0.5), (0.2, 0.8), (0, 1)]
    trfc_pdr_figure = SimulationFigure(number_of_nodes_list, traffic_type_list)
    trfc_energy_figure = SimulationFigure(number_of_nodes_list, traffic_type_list)

    for traffic_type in traffic_type_list:
        sys.stdout.write('\n{} '.format(traffic_type))
        sys.stdout.flush()
        for number_of_nodes in number_of_nodes_list:
            sys.stdout.write('.')
            sys.stdout.flush()
            simulation_result_sum = SimulationResult()
            for repeat in range(averaging):
                topology = Topology.create_random_topology(number_of_nodes=number_of_nodes, radius=topology_radius, number_of_gws=number_of_gws, node_traffic_proportions=traffic_type)
                simulation = Simulation(topology=topology, packet_rate=packet_rate, packet_size=packet_size, simulation_duration=simulation_duration, sf=PacketSf.SF_Lowest)
                simulation_result_sum += simulation.run()
            trfc_pdr_figure.plot_data[traffic_type].append(float(simulation_result_sum.pdr) / averaging)
            trfc_energy_figure.plot_data[traffic_type].append(float(simulation_result_sum.txEnergyConsumption) / averaging)

    trfc_pdr_figure.get_plot(xlabel='Number of nodes', ylabel='PDR (%)', xlim_left=0, xlim_right=1000)
    plt.legend(fontsize='small', title='Traffic types')
    plt.savefig('output/trfc_pdr_r{}_g{}_p{}_s{}.png'.format(topology_radius, number_of_gws, packet_rate, simulation_duration), dpi=200, transparent=True)

    trfc_energy_figure.get_plot(xlabel='Number of nodes', ylabel='Transmit energy consumption (J)', xlim_left=0, xlim_right=1000)
    plt.legend(fontsize='small', title='Traffic types')
    plt.savefig('output/trfc_energy_r{}_g{}_p{}_s{}.png'.format(topology_radius, number_of_gws, packet_rate, simulation_duration), dpi=200, transparent=True)


# All units are SI base units
TOPOLOGY_RADIUS = 3000  # meters
NUMBER_OF_GWS = 1
PRED_TOPOLOGY_RADIUS = 5000  # meters
PRED_NUMBER_OF_GWS = 3
SIMULATION_DURATION = 360  # seconds
PACKET_RATE = 0.01  # per second
PACKET_SIZE = 60  # bytes, header + payload, 13 + max(51 to 222)
TRAFFIC_TYPE = (1, 0)  # poisson, periodic
AVERAGING = 5
NUMBER_OF_NODES_LIST = range(50, 1001, 50)


prediction_accuracy(averaging=AVERAGING,
        number_of_gws=PRED_NUMBER_OF_GWS,
        packet_rate=PACKET_RATE,
        packet_size=PACKET_SIZE,
        simulation_duration=SIMULATION_DURATION,
        traffic_type=TRAFFIC_TYPE)

prediction_pdr(averaging=AVERAGING,
        number_of_gws=PRED_NUMBER_OF_GWS,
        packet_rate=PACKET_RATE,
        packet_size=PACKET_SIZE,
        simulation_duration=SIMULATION_DURATION,
        traffic_type=TRAFFIC_TYPE)

plot_prediction(number_of_nodes_list=NUMBER_OF_NODES_LIST,
        averaging=AVERAGING,
        topology_radius=PRED_TOPOLOGY_RADIUS,
        number_of_gws=PRED_NUMBER_OF_GWS,
        packet_rate=PACKET_RATE,
        packet_size=PACKET_SIZE,
        simulation_duration=SIMULATION_DURATION,
        traffic_type=TRAFFIC_TYPE)

plot_sf(number_of_nodes_list=NUMBER_OF_NODES_LIST,
        averaging=AVERAGING,
        topology_radius=TOPOLOGY_RADIUS,
        number_of_gws=NUMBER_OF_GWS,
        packet_rate=PACKET_RATE,
        packet_size=PACKET_SIZE,
        simulation_duration=SIMULATION_DURATION,
        traffic_type=TRAFFIC_TYPE)

plot_gw(number_of_nodes_list=NUMBER_OF_NODES_LIST,
        averaging=AVERAGING,
        topology_radius=TOPOLOGY_RADIUS,
        packet_rate=PACKET_RATE,
        packet_size=PACKET_SIZE,
        simulation_duration=SIMULATION_DURATION,
        traffic_type=TRAFFIC_TYPE)

plot_r(number_of_nodes_list=NUMBER_OF_NODES_LIST,
        averaging=AVERAGING,
        number_of_gws=NUMBER_OF_GWS,
        packet_rate=PACKET_RATE,
        packet_size=PACKET_SIZE,
        simulation_duration=SIMULATION_DURATION,
        traffic_type=TRAFFIC_TYPE)

plot_pr(number_of_nodes_list=NUMBER_OF_NODES_LIST,
        averaging=AVERAGING,
        topology_radius=TOPOLOGY_RADIUS,
        number_of_gws=NUMBER_OF_GWS,
        packet_size=PACKET_SIZE,
        simulation_duration=SIMULATION_DURATION,
        traffic_type=TRAFFIC_TYPE)

plot_trfc(number_of_nodes_list=NUMBER_OF_NODES_LIST,
        averaging=AVERAGING,
        topology_radius=TOPOLOGY_RADIUS,
        number_of_gws=NUMBER_OF_GWS,
        packet_rate=PACKET_RATE,
        packet_size=PACKET_SIZE,
        simulation_duration=SIMULATION_DURATION)
