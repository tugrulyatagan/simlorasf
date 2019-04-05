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
import enum
from packet import Packet


@enum.unique
class TrafficType(enum.Enum):
    Poisson = 0
    Periodic = 1


class Node:
    idCounter = 0

    def __init__(self, location):
        self.location = location
        Node.idCounter += 1
        self.id = Node.idCounter
        self.txList = []
        self.lowestSf = None
        self.predictedSf = None
        self.trafficType = None

    def __repr__(self):
        if self.__class__ == Gateway:
            return 'g {:>3} {}'.format(self.id, self.location)
        else:
            return 'n {:>3} {} {:>2} {}'.format(self.id, self.location, self.lowestSf.name, self.trafficType.name)

    def schedule_tx(self, packet_rate, packet_size, simulation_duration, sf):
        # Poisson interval
        if len(self.txList) == 0:
            # initial transmissions are random
            next_time = random.expovariate(packet_rate)
        else:
            if self.trafficType == TrafficType.Poisson:
                next_interval = self.__generatePoissonInterval(packet_rate)
            elif self.trafficType == TrafficType.Periodic:
                next_interval = self.__generatePeriodicInterval(packet_rate)
            next_time = self.txList[-1].time + self.txList[-1].duration + next_interval

        if next_time > simulation_duration:
            return None

        new_packet = Packet(time=next_time, sf=sf, source=self.id, size=packet_size)
        self.txList.append(new_packet)

        return new_packet

    def __generatePoissonInterval(self, packet_rate):
        return random.expovariate(packet_rate)

    def __generatePeriodicInterval(self, packet_rate):
        return 1 / packet_rate


class Gateway(Node):
    def __init__(self, location):
        Node.__init__(self, location)
