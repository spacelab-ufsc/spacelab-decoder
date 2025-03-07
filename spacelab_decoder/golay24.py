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
    """

    def __init__(self):
        """
        Class initialization.

        This method initialized the Golay matrices.

        :return: None
        :rtype: None
        """
        # Generator matrix for Golay(24, 12) code
        self.G = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1]
        ], dtype=np.uint8)

        # Parity-check matrix for Golay(24, 12) code
        self.H = np.array([
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        ], dtype=np.uint8)

        # Precomputed syndrome table for error patterns
        self.syndrome_table = {
            tuple(np.dot(self.H, np.roll([1] + [0] * 23, i)) % 2): i for i in range(24)
        }

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

        # Convert the integer to a 12-bit binary array
        data_bits = np.array([int(bit) for bit in f"{data:012b}"], dtype=int)

        # Perform matrix multiplication (data_bits * G) modulo 2
        encoded_bits = np.dot(data_bits, self.G) % 2

        # Convert the 24-bit array to 3 bytes
        encoded_bytes = [
            int("".join(map(str, encoded_bits[i:i+8])), 2) for i in range(0, 24, 8)
        ]

        return encoded_bytes

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

        # Convert the 3 bytes to a 24-bit binary array
        encoded_bits = np.array([int(bit) for byte in encoded_bytes for bit in f"{byte:08b}"], dtype=int)

        # Compute the syndrome
        syndrome = np.dot(self.H, encoded_bits) % 2

        # Check if the syndrome is zero (no errors)
        if np.all(syndrome == 0):
            return int("".join(map(str, encoded_bits[:12])), 2)

        # Check if the syndrome corresponds to a single-bit error
        syndrome_tuple = tuple(syndrome)
        if syndrome_tuple in self.syndrome_table:
            error_position = self.syndrome_table[syndrome_tuple]
            encoded_bits[error_position] ^= 1  # Correct the error
            return int("".join(map(str, encoded_bits[:12])), 2)

        # If no single-bit error, check for 2 or 3 errors
        for i in range(24):
            for j in range(i + 1, 24):
                # Flip two bits and compute the syndrome
                test_data = encoded_bits.copy()
                test_data[i] ^= 1
                test_data[j] ^= 1
                test_syndrome = np.dot(self.H, test_data) % 2
                if np.all(test_syndrome == 0):
                    return int("".join(map(str, test_data[:12])), 2)

        for i in range(24):
            for j in range(i + 1, 24):
                for k in range(j + 1, 24):
                    # Flip three bits and compute the syndrome
                    test_data = encoded_bits.copy()
                    test_data[i] ^= 1
                    test_data[j] ^= 1
                    test_data[k] ^= 1
                    test_syndrome = np.dot(self.H, test_data) % 2
                    if np.all(test_syndrome == 0):
                        return int("".join(map(str, test_data[:12])), 2)

        # If no errors are corrected, return the first 12 bits (may contain errors)
        return int("".join(map(str, encoded_bits[:12])), 2)
