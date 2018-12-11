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
        self.duration = self.calculate_transmission_duration()
        self.receive_radius = self.calculate_receive_radius()

    def __lt__(self, other):
        return self.time < other.time

    def __repr__(self):
        return '(t={},src={},dst={},sf={},bw={},dur={},stat={},rcv={})'.format(self.time, self.source, self.destination, self.sf, self.bandwidth, self.duration, self.status, self.receive_radius)

    def calculate_transmission_duration(self):
        # https://docs.exploratory.engineering/lora/dr_sf/
        # TODO, consider BW
        if self.sf == PacketSf.sf7:
            return (self.size * 8) / 5470
        elif self.sf == PacketSf.sf8:
            return (self.size * 8) / 3125
        elif self.sf == PacketSf.sf9:
            return (self.size * 8) / 1760
        elif self.sf == PacketSf.sf10:
            return (self.size * 8) / 980
        elif self.sf == PacketSf.sf11:
            return (self.size * 8) / 440
        elif self.sf == PacketSf.sf12:
            return (self.size * 8) / 250
        else:
            raise Exception()

    def calculate_receive_radius(self):
        # TODO
        if self.sf == PacketSf.sf7:
            return 1250
        elif self.sf == PacketSf.sf8:
            return 2500
        elif self.sf == PacketSf.sf9:
            return 3750
        elif self.sf == PacketSf.sf10:
            return 5000
        elif self.sf == PacketSf.sf11:
            return 7500
        elif self.sf == PacketSf.sf12:
            return 10000
        else:
            raise Exception()

    def is_interfered_by(self, interferer_packet, topology, target_location):
        interferer_location = topology.get_node(interferer_packet.source).location
        my_location = topology.get_node(self.source).location

        interferer_distance = Location.get_distance(interferer_location, target_location)
        my_distance = Location.get_distance(my_location, target_location)

        # TODO
        if interferer_distance > my_distance + 2000:
            return False
        else:
            return True
