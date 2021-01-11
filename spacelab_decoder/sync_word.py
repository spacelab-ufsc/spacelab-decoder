#
#  sync_word.py
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


_SYNC_WORD_MSB = "msb"
_SYNC_WORD_LSB = "lsb"

class SyncWord(list):

    def __init__(self, val, endi=_SYNC_WORD_MSB):
        self.endianess = endi
        if type(val) is list:
            for sync_byte in val:
                buf = self.byte_to_bitfield(sync_byte)
                for i in range(len(buf)):
                    self.append(buf[i])
        else:
            raise RuntimeError("SyncWord: the given sync word isn't a list!")

    def byte_to_bitfield(self, val):
        buf = [True if digit == '1' else False for digit in bin(val)[2:].zfill(8)]  # [2:] to chop off the "0b" part

        if self.endianess == _SYNC_WORD_LSB:
            buf.reverse()

        return buf
