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

import bisect
import math
import logging
from sklearn.model_selection import train_test_split
from packet import PacketStatus
from packet import PacketSf
from packet import collision_snir
from location import Location
from node import Node
from packet import Packet


class SimulationResult:
    def __init__(self):
        self.totalPacket = 0
        self.successfulPacket = 0
        self.underSensitivityPacket = 0
        self.interferencePacket = 0
        self.pdr = 0
        self.throughput = 0
        self.txEnergyConsumption = 0

    def __repr__(self):
        res  = ' Number of packets: {}\n'.format(self.totalPacket)
        res += ' Number of successfully transmitted packets: {}\n'.format(self.successfulPacket)
        res += ' Number of under sensitivity packets: {}\n'.format(self.underSensitivityPacket)
        res += ' Number of interfered packets: {}\n'.format(self.interferencePacket)
        res += ' PDR: {:.3f} %\n'.format(self.pdr)
        res += ' Network throughput: {:.3f} bps\n'.format(self.throughput)
        res += ' Total TX energy consumption: {:.3f} Joule'.format(self.txEnergyConsumption)
        return res

    def __add__(self, other):
        sumResult = SimulationResult()
        sumResult.totalPacket = self.totalPacket + other.totalPacket
        sumResult.successfulPacket = self.successfulPacket + other.successfulPacket
        sumResult.underSensitivityPacket = self.underSensitivityPacket + other.underSensitivityPacket
        sumResult.interferencePacket = self.interferencePacket + other.interferencePacket
        sumResult.pdr = self.pdr + other.pdr
        sumResult.throughput = self.throughput + other.throughput
        sumResult.txEnergyConsumption = self.txEnergyConsumption + other.txEnergyConsumption
        return sumResult


class Simulation:
    def __init__(self, topology, packet_rate, packet_size, simulation_duration, sf, sfPredictor=None):
        assert 0.0001 <= packet_rate <= 10, 'unsupported packet rate {}'.format(packet_rate)
        assert 51 <= packet_size <= 222, 'unsupported packet size {}'.format(packet_size)
        assert 10 <= simulation_duration <= 100000, 'unsupported simulation duration {}'.format(simulation_duration)

        self.eventQueue = []
        self.topology = topology
        self.packetRate = packet_rate
        self.packetSize = packet_size
        self.simulationDuration = simulation_duration
        self.simulationResult = SimulationResult()
        self.sf = sf
        self.sfPredictor = sfPredictor
        Node.idCounter = 0

    def __add_to_event_queue(self, packet):
        if packet is not None:
            bisect.insort_left(self.eventQueue, packet)

    def show_events(self):
        print('Events:')
        for event in self.eventQueue:
            print(' {}'.format(event))

    def show_results(self):
        print('Results:')
        print('{}'.format(self.simulationResult))

    def show_inputs(self):
        print('Results:')
        print('{}'.format(self.simulationResult))

    def get_training_data(self, test_size=0.2):
        assert 0 <= test_size <= 1, 'invalid test size {}'.format(test_size)

        X = []
        y = []
        for event in self.eventQueue:
            tx_node = self.topology.get_node(event.source)
            X.append([tx_node.location.x, tx_node.location.y, event.sf.value])
            y.append(event.status.value)
        return train_test_split(X, y, test_size=test_size)

    def write_to_file(self, file_name):
        with open(file_name, 'w') as file:
            file.write('Parameters:\n')
            file.write('Topology radius: {} meters\n'.format(self.topology.radius))
            file.write('Number of gateways: {}\n'.format(len(self.topology.gateway_list)))
            file.write('Number of nodes: {}\n'.format(len(self.topology.node_list)))
            file.write('SF assignment method: {}\n'.format(self.sf))
            file.write('Simulation duration: {} seconds\n'.format(self.simulationDuration))
            file.write('Packet rate: {} packet per second\n'.format(self.packetRate))
            file.write('Packet size: {} bytes\n'.format(self.packetSize))

            file.write('\nNodes:\n')
            for gateway in self.topology.gateway_list:
                file.write('{}\n'.format(gateway))
            for node in self.topology.node_list:
                file.write('{}\n'.format(node))

            file.write('\nEvents:\n')
            for event in self.eventQueue:
                file.write('{}\n'.format(event))

            file.write('\nResults:\n')
            file.write('{}\n'.format(self.simulationResult))

            # for event in self.eventQueue:
            #     tx_node = self.topology.get_node(event.source)
            #     file.write('{},{},{},{}\n'.format(tx_node.location.x, tx_node.location.x, event.sf.name, event.status.name))

    def __get_sf(self, tx_node):
        if self.sf == PacketSf.SF_Lowest:
            return tx_node.lowestSf
        elif self.sf == PacketSf.SF_Smart:
            # Xnew = [[tx_node.location.x, tx_node.location.y, tx_node.lowestSf.value]]
            # ynew = self.sfPredictor(Xnew)[0]
            # if ynew == PacketStatus.interfered.value and tx_node.lowestSf.value < 12:
            #     return PacketSf(tx_node.lowestSf.value + 1)
            # else:
            #     return tx_node.lowestSf
            for sf_pred in range(tx_node.lowestSf.value, 12+1):
                Xnew = [[tx_node.location.x, tx_node.location.y, sf_pred]]
                ynew = self.sfPredictor(Xnew)[0]
                logging.debug('sf_pred={},tx_node.lowestSf={},ynew={}'.format(sf_pred, tx_node.lowestSf, ynew))
                if ynew == PacketStatus.transmitted.value:
                    return PacketSf(sf_pred)
            logging.info('Suitable SF not found')
            return tx_node.lowestSf
        elif self.sf == PacketSf.SF_Random:
            return PacketSf.get_random()
        else:
            return self.sf

    def run(self):
        # Schedule initial node transmissions
        for tx_node in self.topology.node_list:
            tx_node.txList = []
            sf = self.__get_sf(tx_node)
            self.__add_to_event_queue(tx_node.schedule_tx(packet_rate=self.packetRate, packet_size=self.packetSize, simulation_duration=self.simulationDuration, sf=sf))

        for event_index, event in enumerate(self.eventQueue):
            tx_node = self.topology.get_node(event.source)

            rx_gw_list = []
            # Check which gateways can receive
            for gw in self.topology.gateway_list:
                distance_to_gw = Location.get_distance(tx_node.location, gw.location)
                rx_sensitivity_dbm = Packet.get_receive_sensitivity(event.sf)
                propagation_loss_dbm = Packet.calculate_propagation_loss(distance_to_gw)
                rx_signal_dbm = event.tx_power_dbm - propagation_loss_dbm
                if rx_signal_dbm < rx_sensitivity_dbm:
                    logging.info('Under sensitivity ({} - {:.3f}) < {} for {} at gw {}'.format(event.tx_power_dbm, propagation_loss_dbm, rx_sensitivity_dbm, event, gw.id))
                    pass
                else:
                    rx_gw_list.append([gw, rx_signal_dbm])

            if len(rx_gw_list) == 0:
                # No gateway received the packet
                logging.info('lost due to under sensitivity {}'.format(event))
                event.status = PacketStatus.under_sensitivity
            else:
                # Check overlapping events
                overlapping_events = []
                for previous_event_index in range(event_index - 1, 0, -1):
                    previous_event = self.eventQueue[previous_event_index]
                    if (previous_event.time + previous_event.duration) < event.time:
                        break
                    # Events are overlapping
                    overlapping_events.append(previous_event)
                    logging.info('previous {} and {} are overlapping for {:.3f} s'.format(previous_event, event, previous_event.time + previous_event.duration - event.time))

                for next_event_index in range(event_index + 1, len(self.eventQueue)):
                    next_event = self.eventQueue[next_event_index]
                    if (event.time + event.duration) < next_event.time:
                        break
                    # Events are overlapping
                    overlapping_events.append(next_event)
                    logging.info('next {} and {} are overlapping for {:.3f} s'.format(next_event, event, event.time + event.duration - next_event.time))

                if len(overlapping_events) > 0:
                    # Check interference at gateways
                    for rx_gw_index in range(len(rx_gw_list)):
                        rx_gw = rx_gw_list[rx_gw_index][0]
                        rx_signal_dbm = rx_gw_list[rx_gw_index][1]
                        cumulative_interference_energy_j = [0] * 6
                        rx_signal_energy_j = Packet.calculate_energy(rx_signal_dbm, event.duration)
                        logging.debug('event_node={},'
                              'event_sf={},'
                              'rx_gw={},'
                              'rx_signal_dbm={},'
                              'rx_signal_energy_j={}'.format(
                            event.source,
                            event.sf.value,
                            rx_gw.id,
                            rx_signal_dbm,
                            rx_signal_energy_j))

                        for interferer_event in overlapping_events:
                            if event.time > interferer_event.time:
                                # Overlap with previous event
                                overlap_duration = interferer_event.time + interferer_event.duration - event.time
                            else:
                                # Overlap with next event
                                overlap_duration = event.time + event.duration - interferer_event.time
                            interferer_node = self.topology.get_node(interferer_event.source)
                            interferer_to_gw_distance = Location.get_distance(rx_gw.location, interferer_node.location)
                            interferer_propagation_loss = Packet.calculate_propagation_loss(interferer_to_gw_distance)
                            interferer_power_dbm = interferer_event.tx_power_dbm - interferer_propagation_loss
                            interference_energy_j = Packet.calculate_energy(interferer_power_dbm, overlap_duration)

                            logging.debug('interferer_node={},'
                                  'interferer_sf={},'
                                  'interferer_gw_distance={:.3f},'
                                  'interferer_propagation_loss={:.3f},'
                                  'overlap_duration={:.3f},'
                                  'interferer_power_dbm={:.3f},'
                                  'interference_energy_j={}'.format(
                                interferer_event.source,
                                interferer_event.sf.value,
                                interferer_to_gw_distance,
                                interferer_propagation_loss,
                                overlap_duration,
                                interferer_power_dbm,
                                interference_energy_j))

                            cumulative_interference_energy_j[interferer_event.sf.value - 7] += interference_energy_j

                        for sf_index in range(len(cumulative_interference_energy_j)):
                            if cumulative_interference_energy_j[sf_index] != 0:
                                logging.debug('Cumulative interference energy={} for sf={} at gw={}'.format(cumulative_interference_energy_j[sf_index], sf_index + 7, rx_gw.id))
                                snir_isolation = collision_snir[event.sf.value-7][sf_index]
                                logging.debug('needed isolation to survive={}'.format(snir_isolation))
                                snir = 10 * math.log10( rx_signal_energy_j / cumulative_interference_energy_j[sf_index])
                                logging.debug('snir={}'.format(snir))
                                if snir >= snir_isolation:
                                    logging.info('survived {} from interference at gw={}'.format(event, rx_gw.id))
                                    pass
                                else:
                                    logging.info('interfered {} at gw={}'.format(event, rx_gw.id))
                                    rx_gw_list[rx_gw_index] = None

                if all(rx_gw is None for rx_gw in rx_gw_list):
                    logging.info('lost due to interference {}'.format(event))
                    event.status = PacketStatus.interfered

            # If packet is not interfered or under sensitivity, then transmitted
            if event.status == PacketStatus.pending:
                event.status = PacketStatus.transmitted

            logging.info('Event simulated {}'.format(event))

            # Schedule next event for this node
            sf = self.__get_sf(tx_node)
            self.__add_to_event_queue(tx_node.schedule_tx(packet_rate=self.packetRate, packet_size=self.packetSize, simulation_duration=self.simulationDuration, sf=sf))

        # Collect statistics
        cumulativeSuccessfulDataSize = 0
        cumulativeDataDuration = 0
        for event in self.eventQueue:
            self.simulationResult.txEnergyConsumption += event.tx_energy_j
            self.simulationResult.totalPacket += 1
            cumulativeDataDuration += event.duration
            if event.status == PacketStatus.under_sensitivity:
                self.simulationResult.underSensitivityPacket += 1
            elif event.status == PacketStatus.interfered:
                self.simulationResult.interferencePacket += 1
            elif event.status == PacketStatus.transmitted:
                self.simulationResult.successfulPacket += 1
                cumulativeSuccessfulDataSize += event.size
        self.simulationResult.pdr = 100 * float(self.simulationResult.successfulPacket) / self.simulationResult.totalPacket
        self.simulationResult.throughput = 8 * float(cumulativeSuccessfulDataSize) / cumulativeDataDuration
        return self.simulationResult
