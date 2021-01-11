#
#  byte_buffer.py
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


_BYTE_BUFFER_MSB = "msb"
_BYTE_BUFFER_LSB = "lsb"

class ByteBuffer:

    def __init__(self, endi=_BYTE_BUFFER_MSB):
        self.endianess = endi
        self.clear()

    def is_full(self):
        if self.pos > 7:
            return True
        else:
            return False

    def push(self, bit):
        if type(bit) is bool:
            if self.pos < 8:
                self.buffer[self.pos] = bit
                self.pos = self.pos - 1
                if self.pos < 0:
                    self.pos = 8
        else:
            raise RuntimeError("ByteBuffer: the byte buffer must only receive bits!")

    def clear(self):
        self.buffer = [False,False,False,False,False,False,False,False]
        self.pos = 7

    def to_byte(self):
        if self.endianess == _BYTE_BUFFER_LSB:
            self.buffer.reverse()
        byte = 0
        for bit in self.buffer: 
            byte = (byte << 1) | int(bit)

        return byte

    def __repr__(self):
        return str(self.buffer)

    def __str__(self):
        return str(self.buffer)
