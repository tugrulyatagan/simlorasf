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
import logging
import argparse
from matplotlib import rcParams
rcParams['font.family'] = 'serif'
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from topology import Topology
from simulation import Simulation
from packet import PacketSf


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LoRa SF simulator')
    parser.add_argument('-r', '--radius', type=int, default=5000, help='topology radius in meter')
    parser.add_argument('-g', '--gateway', type=int, default=1, help='number of gateways')
    parser.add_argument('-n', '--node', type=int, default=100, help='number of nodes')
    parser.add_argument('-s', '--sf', choices=[sf.name for sf in PacketSf], default='SF_Lowest', help='spreading factor assignment method')
    parser.add_argument('-c', '--classifier', choices=['DTC', 'SVM'], default='DTC', help='smart spreading factor assignment classifier')
    parser.add_argument('-d', '--duration', type=int, default=3600, help='simulation duration in second')
    parser.add_argument('-p', '--packetRate', type=float, default=0.01, help='packet rate in packet per second')
    parser.add_argument('-z', '--packetSize', type=int, default=60, help='packet size in byte')
    parser.add_argument('-e', '--seed', type=int, help='random number generator seed')
    parser.add_argument('-l', '--event', help='events log path')
    parser.add_argument('-v', '--verbose', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='ERROR', help='verbose level')
    args = parser.parse_args()
    logging.basicConfig(level=logging.getLevelName(args.verbose), format='%(asctime)s %(levelname)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s')

    print('Parameters:')
    print('  Radius: {} meters'.format(args.radius))
    print('  Number of gateways: {}'.format(args.gateway))
    print('  Number of nodes: {}'.format(args.node))
    print('  SF assignment method: {}'.format(args.sf))
    if PacketSf[args.sf] == PacketSf.SF_Smart:
        print('  Smart SF classifier: {}'.format(args.classifier))
    print('  Simulation duration: {} seconds'.format(args.duration))
    print('  Packet rate: {} packet per second'.format(args.packetRate))
    print('  Packet size: {} bytes'.format(args.packetSize))
    print('  Random number generator seed: {}'.format(args.seed))
    print('  Events log path: {}'.format(args.event))
    print('  Verbose level: {}'.format(args.verbose))

    if args.seed:
        random.seed(args.seed)

    topology = Topology.create_random_topology(number_of_nodes=args.node, radius=args.radius, number_of_gws=args.gateway)

    sfPredictor = None
    if PacketSf[args.sf] == PacketSf.SF_Smart:
        simulation = Simulation(topology=topology, packet_rate=args.packetRate, packet_size=args.packetSize, simulation_duration=args.duration, sf=PacketSf.SF_Random)
        simulation.run()
        X_train, X_test, y_train, y_test = simulation.get_training_data(test_size=0.2)

        classifier = None
        if args.classifier == 'DTC':
            classifier = DecisionTreeClassifier(class_weight='balanced')
        elif args.classifier == 'SVM':
            classifier = svm.SVC(class_weight='balanced', gamma='auto')

        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)
        print('Training classification report:')
        print(classification_report(y_test, y_pred))
        print('Training confusion matrix:')
        print(confusion_matrix(y_test, y_pred, labels=[1, 2, 3]))
        print("Training accuracy is {:.3f} %".format(accuracy_score(y_test, y_pred) * 100))
        sfPredictor = classifier.predict

    simulation = Simulation(topology=topology, packet_rate=args.packetRate, packet_size=args.packetSize, simulation_duration=args.duration, sf=PacketSf[args.sf], sfPredictor=sfPredictor)
    simulation.run()
    simulation.show_results()
    if args.event:
        simulation.write_to_file(file_name=args.event)
