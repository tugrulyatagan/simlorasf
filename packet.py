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

import math
import random
import enum


collision_snir = [
    [  6, -16, -18, -19, -19, -20],
    [-24,   6, -20, -22, -22, -22],
    [-27, -27,   6, -23, -25, -25],
    [-30, -30, -30,   6, -26, -28],
    [-33, -33, -33, -33,   6, -29],
    [-36, -36, -36, -36, -36,   6],
]

class PacketStatus:
    pending = 0
    transmitted = 1
    interfered = 2
    under_sensitivity = 3


class PacketSf(enum.Enum):
    SF_Random = 0
    SF_Lowest = 1
    SF_Predictor = 2
    SF_7 = 7
    SF_8 = 8
    SF_9 = 9
    SF_10 = 10
    SF_11 = 11
    SF_12 = 12

    @staticmethod
    def get_random():
        return PacketSf(random.randint(7, 12))


class Packet:
    def __init__(self, time, sf, source, size, destination=0):
        self.time = time
        self.sf = sf
        self.source = source
        self.destination = destination
        self.status = PacketStatus.pending
        self.size = size
        self.duration = Packet.calculate_transmission_duration(sf, size)
        self.bandwidth = 125  # TODO
        self.tx_power_dbm = 14  # dBm TODO
        self.tx_energy_j = Packet.calculate_energy(power_dbm=self.tx_power_dbm, duration=self.duration)

    def __lt__(self, other):
        return self.time < other.time

    def __repr__(self):
        return '(t={:.3f},src={},dst={},sf={},bw={},dur={:.3f},p={},e={:.4f},stat={})'.format(self.time, self.source, self.destination, self.sf.value, self.bandwidth, self.duration, self.tx_power_dbm, self.tx_energy_j, self.status)

    @staticmethod
    def calculate_transmission_duration(sf, size):
        # TODO, consider BW
        if sf == PacketSf.SF_7:
            return (size * 8) / 5470.0
        elif sf == PacketSf.SF_8:
            return (size * 8) / 3125.0
        elif sf == PacketSf.SF_9:
            return (size * 8) / 1760.0
        elif sf == PacketSf.SF_10:
            return (size * 8) / 980.0
        elif sf == PacketSf.SF_11:
            return (size * 8) / 440.0
        elif sf == PacketSf.SF_12:
            return (size * 8) / 250.0
        else:
            raise Exception()

    @staticmethod
    def get_receive_sensitivity(sf):
        # https://www.semtech.com/uploads/documents/DS_SX1276-7-8-9_W_APP_V5.pdf
        if sf == PacketSf.SF_7:
            return -130
        elif sf == PacketSf.SF_8:
            return -132.5
        elif sf == PacketSf.SF_9:
            return -135
        elif sf == PacketSf.SF_10:
            return -137.5
        elif sf == PacketSf.SF_11:
            return -140
        elif sf == PacketSf.SF_12:
            return -142.5
        else:
            raise Exception()

    @staticmethod
    def calculate_propagation_loss(distance):
        # Assuming f = 868 MHz and h = 15 m
        return 120.5 + 37.6 * math.log10(distance/1000)

    @staticmethod
    def get_lowest_sf(distance, erp=14):
        # TODO erp
        propagation_loss = Packet.calculate_propagation_loss(distance)
        if erp - propagation_loss > Packet.get_receive_sensitivity(PacketSf.SF_7):
            return PacketSf.SF_7
        elif erp - propagation_loss > Packet.get_receive_sensitivity(PacketSf.SF_8):
            return PacketSf.SF_8
        elif erp - propagation_loss > Packet.get_receive_sensitivity(PacketSf.SF_9):
            return PacketSf.SF_9
        elif erp - propagation_loss > Packet.get_receive_sensitivity(PacketSf.SF_10):
            return PacketSf.SF_10
        elif erp - propagation_loss > Packet.get_receive_sensitivity(PacketSf.SF_11):
            return PacketSf.SF_11
        else:
            return PacketSf.SF_12

    @staticmethod
    def calculate_energy(power_dbm, duration):
        return Packet.dbm_to_watt(power_dbm) * duration

    @staticmethod
    def dbm_to_watt(dbm):
        if dbm == 14:
            # Pre calculated value for commonly used tx_power_dbm
            return 0.025118864315095794
        else:
            return (10 ** (dbm/10)) / 1000.0
