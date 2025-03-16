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

import numpy as np

class Golay24:
    """
    Golay24 class.

    This class implements the Golay(24,12,8) code.

    Based on the implementation of:
    https://github.com/daniestevez/gr-satellites/blob/master/lib/golay24.c
    """

    def __init__(self):
        """
        Class initialization.

        This method initializes the Golay parity matrix.

        :return: None
        :rtype: None
        """
        # Parity-check matrix for Golay(24, 12) code
        self.H = [0x8008ED,
                  0x4001DB,
                  0x2003B5,
                  0x100769,
                  0x080ED1,
                  0x040DA3,
                  0x020B47,
                  0x01068F,
                  0x008D1D,
                  0x004A3B,
                  0x002477,
                  0x001FFE]

    def encode(self, data):
        """
        Encodes 12-bit data (as an integer) into a 24-bit Golay code.

        :param data: An integer representing 12 bits of data (0 to 4095).
        :type: int

        :return: A list of 3 integers representing the encoded Golay24 packet in byte form.
        :rtype: list[int]
        """
        if data < 0 or data > 4095:
            raise ValueError("Input data must be a 12-bit integer (0 to 4095)!")

        # Extract the lower 12 bits of the input data
        r = data & 0xFFF
        s = 0

        # Compute the parity bits
        for i in range(len(self.H)):    # Number of rows in H
            s <<= 1
            # Calculate parity of (H[i] & r) using the built-in bin().count('1')
            parity = bin(self.H[i] & r).count('1') % 2
            s |= parity

        # Combine the parity bits (s) and the original data (r) into the final codeword
        encoded_data = ((s & 0xFFF) << len(self.H)) | r

        # Translate the result to a list with three bytes
        res = list()
        res.append((encoded_data >> 16) & 0xFF)
        res.append((encoded_data >> 8) & 0xFF)
        res.append(encoded_data & 0xFF)

        return res

    def decode(self, encoded_bytes):
        """
        Decodes a 24-bit Golay code (as 3 bytes) into 12-bit data.

        :param encoded_bytes: A list of 3 integers representing the encoded Golay24 packet
        :type: list[int]

        :return: An integer representing the decoded 12-bit data.
        :rtype: int
        """
        if len(encoded_bytes) != 3 or any(byte < 0 or byte > 255 for byte in encoded_bytes):
            raise ValueError("Input must be a list of 3 bytes (integers between 0 and 255)!")

        r = (encoded_bytes[0] << 16) | (encoded_bytes[1] << 8) | (encoded_bytes[2])
        s = 0     # Syndrome
        q = 0     # Modified syndrome
        e = 0     # Estimated error vector

        # Step 1. Compute syndrome s = H * r
        for i in range(len(self.H)):
            s <<= 1
            parity = bin(self.H[i] & r).count('1') % 2
            s |= parity

        # Step 2. If w(s) <= 3, then e = (s, 0) and go to step 8
        if self._hamming_weight(s) <= 3:
            e = s << len(self.H)
            goto_step8 = True
        else:
            # Step 3. If w(s + B[i]) <= 2, then e = (s + B[i], e_{i+1}) and go to step 8
            goto_step8 = False
            for i in range(len(self.H)):
                s_xor_B = s ^ self._B(i)
                if self._hamming_weight(s_xor_B) <= 2:
                    e = (s_xor_B << len(self.H)) | (1 << (len(self.H) - i - 1))
                    goto_step8 = True
                    break

            if not goto_step8:
                # Step 4. Compute q = B * s
                q = 0
                for i in range(len(self.H)):
                    q <<= 1
                    parity = bin(self._B(i) & s).count('1') % 2
                    q |= parity

                # Step 5. If w(q) <= 3, then e = (0, q) and go to step 8
                if self._hamming_weight(q) <= 3:
                    e = q
                    goto_step8 = True
                else:
                    # Step 6. If w(q + B[i]) <= 2, then e = (e_{i+1}, q + B[i]) and go to step 8
                    for i in range(len(self.H)):
                        q_xor_B = q ^ self._B(i)
                        if self._hamming_weight(q_xor_B) <= 2:
                            e = (1 << (2 * len(self.H) - i - 1)) | q_xor_B
                            goto_step8 = True
                            break

                    # Step 7. If no condition is met, r is uncorrectable
                    if not goto_step8:
                        return -1, None

        # Step 8. Correct the codeword: c = r + e
        corrected_data = r ^ e

        # Return the number of errors corrected (Hamming weight of e)
        return corrected_data & 0xFFF, self._hamming_weight(e)

    def _B(self, i):
        """
        Define B(i) as the i-th row of the identity matrix (12x12).

        :param i: The row number.
        :type: int

        :return: The i-th row of the identity matrix.
        :rtype: list
        """
        return 1 << (len(self.H) - i - 1)

    def _hamming_weight(self, x):
        """
        Function to compute the Hamming weight (number of 1s) of a number.

        :param x: The integer to compute the Hamming weight.
        :type: int

        :return: The number of 1s of the given number.
        :rtype: int
        """
        return bin(x).count('1')
