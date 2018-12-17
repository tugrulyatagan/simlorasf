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
from enum import Enum
from location import Location


class PacketStatus:
    pending = 0
    transmitted = 1
    interfered = 2
    under_sensitivity = 3


class PacketSf(Enum):
    random = 0
    lowest = 1
    sf7 = 7
    sf8 = 8
    sf9 = 9
    sf10 = 10
    sf11 = 11
    sf12 = 12


class Packet:
    def __init__(self, time, sf, bandwidth, source, size, destination=0):
        self.time = time
        self.sf = sf
        self.bandwidth = bandwidth
        self.source = source
        self.destination = destination
        self.status = PacketStatus.pending
        self.size = size
        self.duration = Packet.calculate_transmission_duration(sf, size)
        self.erp = 14  # Europe ISM g1.1. g1.2 Max ERP

    def __lt__(self, other):
        return self.time < other.time

    def __repr__(self):
        return '(t={},src={},dst={},sf={},bw={},dur={},stat={},erp={})'.format(self.time, self.source, self.destination, self.sf, self.bandwidth, self.duration, self.status, self.erp)

    @staticmethod
    def calculate_transmission_duration(sf, size):
        # https://docs.exploratory.engineering/lora/dr_sf/
        # TODO, consider BW
        if sf == PacketSf.sf7:
            return (size * 8) / 5470
        elif sf == PacketSf.sf8:
            return (size * 8) / 3125
        elif sf == PacketSf.sf9:
            return (size * 8) / 1760
        elif sf == PacketSf.sf10:
            return (size * 8) / 980
        elif sf == PacketSf.sf11:
            return (size * 8) / 440
        elif sf == PacketSf.sf12:
            return (size * 8) / 250
        else:
            raise Exception()

    @staticmethod
    def get_receive_sensitivity(sf):
        # https://www.semtech.com/uploads/documents/DS_SX1276-7-8-9_W_APP_V5.pdf
        # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5038744/
        if sf == PacketSf.sf7:
            return -130
        elif sf == PacketSf.sf8:
            return -132.5
        elif sf == PacketSf.sf9:
            return -135
        elif sf == PacketSf.sf10:
            return -137.5
        elif sf == PacketSf.sf11:
            return -140
        elif sf == PacketSf.sf12:
            return -142.5
        else:
            raise Exception()

    @staticmethod
    def calculate_propagation_loss(distance):
        # Assuming f = 868 MHz and h = 15 m
        return 120.5 + 37.6 * math.log10(distance/1000)
