#
#  bit_decoder.py
#
#  Copyright The SpaceLab-Decoder Contributors.
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

from spacelab_decoder.bit_buffer import BitBuffer, _BIT_BUFFER_LSB
from spacelab_decoder.sync_word import SyncWord, _SYNC_WORD_LSB
from spacelab_decoder.byte_buffer import ByteBuffer, _BYTE_BUFFER_LSB

_BIT_DECODER_MAX_BYTES_TO_DECODE = 300

class BitDecoder:
    """
    Bitstream decoder.
    """
    def __init__(self, sync_word, max_err):
        """
        Class constructor.
        """
        self._sync_word_buf = BitBuffer(8*len(sync_word), _BIT_BUFFER_LSB)
        self._sync_word = SyncWord(sync_word, _SYNC_WORD_LSB)
        self._byte_buf = ByteBuffer(_BYTE_BUFFER_LSB)
        self._pkt_detected = False
        self._decoded_bytes = 0
        self._max_bit_err = 0
        self.set_max_bit_errors(max_err)

    def decode_bit(self, bit):
        """
        Decodes a single bit from a bitstream.

        :param bit: Is an incoming bit to decode.
        :type: int

        :return: The decoded byte if a packet is detected, None otherwise
        :rtype: int or None
        """
        self._sync_word_buf.push(bool(bit))

        if self._pkt_detected:
            self._byte_buf.push(bool(bit))
            if self._byte_buf.is_full():
                self._decoded_bytes += 1
                if self._decoded_bytes < _BIT_DECODER_MAX_BYTES_TO_DECODE:
                    pkt_byte = self._byte_buf.to_byte()

                    self._byte_buf.clear()

                    return pkt_byte
                else:
                    self.reset()

        if (self._sync_word == self._sync_word_buf) >= (len(self._sync_word) - self.get_max_bit_errors()):
            self._decoded_bytes = 0
            self._pkt_detected = True
            self._byte_buf.clear()

        return None

    def reset(self):
        """
        Resets the decoder.

        :return: None
        """
        self._pkt_detected = False
        self._byte_buf.clear()

    def set_max_bit_errors(self, err):
        """
        Sets the maximum allowed bit errors to detect the sync word.

        :param err: Is the maximum allowed bit errors in the sync word.
        :type: int

        :return: None
        """
        if err > len(self._sync_word)/2:
            raise ValueError("The maximum allowed bit errors in the sync word must not exceed 50 % of the sync word!")
        else:
            self._max_bit_err = err

    def get_max_bit_errors(self):
        """
        Gets the maximum allowed bit errors to detect the sync word.

        :return: The maximum allowed bit errors.
        :rtype: int
        """
        return self._max_bit_err
