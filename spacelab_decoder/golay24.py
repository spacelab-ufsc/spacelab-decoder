#
#  golay24.py
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


class Golay24:
    """
    Golay24 class.

    This class implements the Golay(24,12,8) code.
    """

    def __init__(self):
        """
        Class initialization.

        This method initialized the Golay matrices.

        :return: None
        :rtype: None
        """
        self._H = [0x8008ED, 0x4001DB, 0x2003B5, 0x100769, 0x80ED1, 0x40DA3, 0x20B47, 0x1068F, 0x8D1D, 0x4A3B, 0x2477, 0x1FFE]
        self._B = list()
        for i in range(len(self._H)):
            self._B.append(self._H[i] & 0xFFF)

    def encode(self, data):
        """
        Computes the parity bits of a given 12-bit integer.

        :param data: Is the integer to compute the parity data.
        :type: int

        :return: A list with the given integer and the parity data.
        :rtype: list[int]
        """
        pass

    def decode(self, data):
        """
        Decodes a Golay packet.

        :param data: Is the list of bytes to decode.
        :type: list[int]

        :return: The decoded data as a list with two bytes.
        :rtype: list[int]
        """
        r = data
        if type(data) is list:
            if len(data) == 2:
                r = (data[0] << 12) | data[1]
            else:
                r = (data[0] << 16) | (data[1] << 8) | data[2]

        s = 0
        q = 0
        e = 0

        # Step 1
        for i in range(12):
            s <<= 1
            s |= self._parity(self._H[i] & r)

        # Step 2
        if self._ones(s) <= 3:
            e = s
            e <<= 12
            res = r ^ e
            if type(data) is list:
                if len(data) == 3:
                    return [(res >> 8) & 0x0F, res & 0xFF]
            return res & 0xFFF

        # Step 3
        for i in range(12):
            if self._ones(s ^ self._B[i]) <= 2:
                e = s ^ self._B[i]
                e <<= 12
                e |= 1 << (12 - i - 1)
                res = r ^ e
                if type(data) is list:
                    if len(data) == 3:
                        return [(res >> 8) & 0x0F, res & 0xFF]
                return res & 0xFFF

        # Step 4
        q = 0
        for i in range(12):
            q <<= 1
            q |= self._parity(self._B[i] & s)

        # Step 5
        if self._ones(q) <= 3:
            e = q
            res = r ^ e
            if type(data) is list:
                if len(data) == 3:
                    return [(res >> 8) & 0x0F, res & 0xFF]
            return res & 0xFFF

        # Step 6
        for i in range(12):
            if self._ones(q ^ self._B[i]) <= 2:
                e = 1 << (2*12 - i - 1)
                e |= q ^ self._B[i]
                res = r ^ e
                if type(data) is list:
                    if len(data) == 3:
                        return [(res >> 8) & 0x0F, res & 0xFF]
                return res & 0xFFF

        # Step 7 - r is uncorrectable
        return -1

    def _ones(self, integer):
        """
        Computes the number of ones in binary format of a given integer.

        :param integer: The number to compute the number of ones (bin format).
        :type integer: int

        :return: The number of ones in given integer.
        :rtype: int
        """
        binary = bin(integer)[2:]

        return binary.count('1')

    def _parity(self, x):
        """
        Computes the parity of a given number.

        The parity of a number is True or False if the number of ones in the binary form is even or odd.

        :param x: The number to check the parity.
        :type x: int

        :return: 1 if the parity is even, or 0 if the parity is odd.
        :rtype: int
        """
        res = 0
        while x:
            res ^= x & 1
            x >>= 1

        return res
