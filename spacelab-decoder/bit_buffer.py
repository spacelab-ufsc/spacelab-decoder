#
#  bit_buffer.py
#  
#  Copyright (C) 2020, Universidade Federal de Santa Catarina
#  
#  This file is part of SpaceLab-Decoder.
#
#  SpaceLab-Decoder is free software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  SpaceLab-Decoder is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public
#  License along with SpaceLab-Decoder; if not, see <http://www.gnu.org/licenses/>.
#  
#

__author__      = "Gabriel Mariano Marcelino - PU5GMA"
__copyright__   = "Copyright (C) 2020, Universidade Federal de Santa Catarina"
__credits__     = ["Gabriel Mariano Marcelino - PU5GMA"]
__license__     = "GPL3"
__version__     = "0.2.0"
__maintainer__  = "Gabriel Mariano Marcelino - PU5GMA"
__email__       = "gabriel.mm8@gmail.com"
__status__      = "Development"


class BitBuffer(list):

    def __init__(self, size=0):
        self.set_max_size(size)

    def set_max_size(self, size):
        if type(size) is int:
            self.max_size = size
        else:
            raise RuntimeError("BifBuffer: the maximum size of the buffer must be an integer!")

    def get_max_size(self):
        return self.max_size

    def push(self, bit):
        if type(bit) is bool:
            if len(self) == self.get_max_size():
                self.pop(0)

            self.append(bit)
        else:
            raise RuntimeError("BifBuffer: the bit buffer must receive only bits!")
