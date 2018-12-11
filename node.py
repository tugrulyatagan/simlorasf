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
from packet import Packet

class Node:
    idCounter = 0

    def __init__(self, location):
        self.location = location
        Node.idCounter += 1
        self.id = Node.idCounter
        self.txList = []

    def schedule_tx(self, packet_rate, packet_size, simulation_duration, sf):
        # Poisson interval
        if len(self.txList) == 0:
            next_time = random.expovariate(packet_rate)
        else:
            next_time = self.txList[-1].time + random.expovariate(packet_rate)

        if next_time > simulation_duration:
            return None

        new_packet = Packet(time=next_time, sf=sf, bandwidth=125, source=self.id, size=packet_size)
        self.txList.append(new_packet)

        return new_packet


class Gateway(Node):
    def __init__(self, location):
        Node.__init__(self, location)