#
#  bit_buffer.py
#  
#  Copyright (C) 2021, Universidade Federal de Santa Catarina
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


_BIT_BUFFER_MSB = "msb"
_BIT_BUFFER_LSB = "lsb"

class BitBuffer(list):

    def __init__(self, size=8, endi=_BIT_BUFFER_MSB):
        self.set_max_size(size)
        self.set_endianess(endi)

    def set_max_size(self, size):
        if type(size) is int:
            self.max_size = size
        else:
            raise RuntimeError("BifBuffer: the maximum size of the buffer must be an integer!")

    def set_endianess(self, endi):
        if endi.lower() == _BIT_BUFFER_MSB:
            self.endianess = _BIT_BUFFER_MSB
        elif endi.lower() == _BIT_BUFFER_LSB:
            self.endianess = _BIT_BUFFER_LSB
        else:
            raise RuntimeError("BifBuffer: %s is an unknown endianess type!", endi)

    def get_max_size(self):
        return self.max_size

    def push(self, bit):
        if (type(bit) is bool) or (type(bit) is int):
            if self.endianess == _BIT_BUFFER_MSB:
                if len(self) == self.get_max_size():
                    self.pop(0)

                self.append(bool(bit))
            else:
                if len(self) == self.get_max_size():
                    self.pop()

                self.insert(0, bool(bit))
        else:
            raise RuntimeError("BifBuffer: the bit buffer must receive only bits!")

    def to_int(self):
        result = 0
        pos = len(self)-1
        for i in self:
            result = result | (int(i) << pos)
            pos = pos-1

        return result
