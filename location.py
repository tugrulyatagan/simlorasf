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


class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return '({:>6.0f},{:>6.0f})'.format(self.x, self.y)

    @staticmethod
    def get_distance(a, b):
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)