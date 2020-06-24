#
#  byte_buffer.py
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


class ByteBuffer:

    def __init__(self):
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
        byte = 0
        for bit in self.buffer: 
            byte = (byte << 1) | int(bit)

        return byte

    def __repr__(self):
        return str(self.buffer)

    def __str__(self):
        return str(self.buffer)
