#
#  reed_solomon.py
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

class ReedSolomon:
    """
    CCSDS Reed-Solomon (without dual basis representation) class.
    """

    def __init__(self):
        """
        Constructor of the class with the Reed-Solomon paramenters initialization.

        This class uses the Reed-Solomon scheme from CCSDS (without dual basis representation).
        """
        # Constants
        self._MM        = 8
        self._NN        = 255
        self._NROOTS    = 32
        self._FCR       = 112
        self._PRIM      = 11
        self._IPRIM     = 116
        self._A0        = self._NN  # Special reserved value encoding zero in index form

        # Precomputed tables
        self._ccsds_alpha_to = [
            0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x87, 0x89, 0x95, 0xad, 0xdd, 0x3d, 0x7a, 0xf4,
            0x6f, 0xde, 0x3b, 0x76, 0xec, 0x5f, 0xbe, 0xfb, 0x71, 0xe2, 0x43, 0x86, 0x8b, 0x91, 0xa5, 0xcd,
            0x1d, 0x3a, 0x74, 0xe8, 0x57, 0xae, 0xdb, 0x31, 0x62, 0xc4, 0x0f, 0x1e, 0x3c, 0x78, 0xf0, 0x67,
            0xce, 0x1b, 0x36, 0x6c, 0xd8, 0x37, 0x6e, 0xdc, 0x3f, 0x7e, 0xfc, 0x7f, 0xfe, 0x7b, 0xf6, 0x6b,
            0xd6, 0x2b, 0x56, 0xac, 0xdf, 0x39, 0x72, 0xe4, 0x4f, 0x9e, 0xbb, 0xf1, 0x65, 0xca, 0x13, 0x26,
            0x4c, 0x98, 0xb7, 0xe9, 0x55, 0xaa, 0xd3, 0x21, 0x42, 0x84, 0x8f, 0x99, 0xb5, 0xed, 0x5d, 0xba,
            0xf3, 0x61, 0xc2, 0x03, 0x06, 0x0c, 0x18, 0x30, 0x60, 0xc0, 0x07, 0x0e, 0x1c, 0x38, 0x70, 0xe0,
            0x47, 0x8e, 0x9b, 0xb1, 0xe5, 0x4d, 0x9a, 0xb3, 0xe1, 0x45, 0x8a, 0x93, 0xa1, 0xc5, 0x0d, 0x1a,
            0x34, 0x68, 0xd0, 0x27, 0x4e, 0x9c, 0xbf, 0xf9, 0x75, 0xea, 0x53, 0xa6, 0xcb, 0x11, 0x22, 0x44,
            0x88, 0x97, 0xa9, 0xd5, 0x2d, 0x5a, 0xb4, 0xef, 0x59, 0xb2, 0xe3, 0x41, 0x82, 0x83, 0x81, 0x85,
            0x8d, 0x9d, 0xbd, 0xfd, 0x7d, 0xfa, 0x73, 0xe6, 0x4b, 0x96, 0xab, 0xd1, 0x25, 0x4a, 0x94, 0xaf,
            0xd9, 0x35, 0x6a, 0xd4, 0x2f, 0x5e, 0xbc, 0xff, 0x79, 0xf2, 0x63, 0xc6, 0x0b, 0x16, 0x2c, 0x58,
            0xb0, 0xe7, 0x49, 0x92, 0xa3, 0xc1, 0x05, 0x0a, 0x14, 0x28, 0x50, 0xa0, 0xc7, 0x09, 0x12, 0x24,
            0x48, 0x90, 0xa7, 0xc9, 0x15, 0x2a, 0x54, 0xa8, 0xd7, 0x29, 0x52, 0xa4, 0xcf, 0x19, 0x32, 0x64,
            0xc8, 0x17, 0x2e, 0x5c, 0xb8, 0xf7, 0x69, 0xd2, 0x23, 0x46, 0x8c, 0x9f, 0xb9, 0xf5, 0x6d, 0xda,
            0x33, 0x66, 0xcc, 0x1f, 0x3e, 0x7c, 0xf8, 0x77, 0xee, 0x5b, 0xb6, 0xeb, 0x51, 0xa2, 0xc3, 0x00
        ]

        self._ccsds_index_of = [
            0xFF, 0x00, 0x01, 0x63, 0x02, 0xC6, 0x64, 0x6A, 0x03, 0xCD, 0xC7, 0xBC, 0x65, 0x7E, 0x6B, 0x2A,
            0x04, 0x8D, 0xCE, 0x4E, 0xC8, 0xD4, 0xBD, 0xE1, 0x66, 0xDD, 0x7F, 0x31, 0x6C, 0x20, 0x2B, 0xF3,
            0x05, 0x57, 0x8E, 0xE8, 0xCF, 0xAC, 0x4F, 0x83, 0xC9, 0xD9, 0xD5, 0x41, 0xBE, 0x94, 0xE2, 0xB4,
            0x67, 0x27, 0xDE, 0xF0, 0x80, 0xB1, 0x32, 0x35, 0x6D, 0x45, 0x21, 0x12, 0x2C, 0x0D, 0xF4, 0x38,
            0x06, 0x9B, 0x58, 0x1A, 0x8F, 0x79, 0xE9, 0x70, 0xD0, 0xC2, 0xAD, 0xA8, 0x50, 0x75, 0x84, 0x48,
            0xCA, 0xFC, 0xDA, 0x8A, 0xD6, 0x54, 0x42, 0x24, 0xBF, 0x98, 0x95, 0xF9, 0xE3, 0x5E, 0xB5, 0x15,
            0x68, 0x61, 0x28, 0xBA, 0xDF, 0x4C, 0xF1, 0x2F, 0x81, 0xE6, 0xB2, 0x3F, 0x33, 0xEE, 0x36, 0x10,
            0x6E, 0x18, 0x46, 0xA6, 0x22, 0x88, 0x13, 0xF7, 0x2D, 0xB8, 0x0E, 0x3D, 0xF5, 0xA4, 0x39, 0x3B,
            0x07, 0x9E, 0x9C, 0x9D, 0x59, 0x9F, 0x1B, 0x08, 0x90, 0x09, 0x7A, 0x1C, 0xEA, 0xA0, 0x71, 0x5A,
            0xD1, 0x1D, 0xC3, 0x7B, 0xAE, 0x0A, 0xA9, 0x91, 0x51, 0x5B, 0x76, 0x72, 0x85, 0xA1, 0x49, 0xEB,
            0xCB, 0x7C, 0xFD, 0xC4, 0xDB, 0x1E, 0x8B, 0xD2, 0xD7, 0x92, 0x55, 0xAA, 0x43, 0x0B, 0x25, 0xAF,
            0xC0, 0x73, 0x99, 0x77, 0x96, 0x5C, 0xFA, 0x52, 0xE4, 0xEC, 0x5F, 0x4A, 0xB6, 0xA2, 0x16, 0x86,
            0x69, 0xC5, 0x62, 0xFE, 0x29, 0x7D, 0xBB, 0xCC, 0xE0, 0xD3, 0x4D, 0x8C, 0xF2, 0x1F, 0x30, 0xDC,
            0x82, 0xAB, 0xE7, 0x56, 0xB3, 0x93, 0x40, 0xD8, 0x34, 0xB0, 0xEF, 0x26, 0x37, 0x0C, 0x11, 0x44,
            0x6F, 0x78, 0x19, 0x9A, 0x47, 0x74, 0xA7, 0xC1, 0x23, 0x53, 0x89, 0xFB, 0x14, 0x5D, 0xF8, 0x97,
            0x2E, 0x4B, 0xB9, 0x60, 0x0F, 0xED, 0x3E, 0xE5, 0xF6, 0x87, 0xA5, 0x17, 0x3A, 0xA3, 0x3C, 0xB7
        ]

        self._ccsds_genpoly = [
            0x00, 0xF9, 0x3B, 0x42, 0x04, 0x2B, 0x7E, 0xFB, 0x61, 0x1E, 0x03, 0xD5, 0x32, 0x42, 0xAA, 0x05,
            0x18, 0x05, 0xAA, 0x42, 0x32, 0xD5, 0x03, 0x1E, 0x61, 0xFB, 0x7E, 0x2B, 0x04, 0x42, 0x3B, 0xF9,
            0x00
        ]

    def encode(self, data, pad):
        """
        Compute parity for Reed-Solomon encoding.
        
        :param data: Input data list of size up to 223 bytes.
        :type: list
        
        :return: Parity data list with 32 bytes.
        :rtype: list
        """
        parity = np.zeros(self._NROOTS, dtype=np.uint8)
    
        for i in range(self._NN - self._NROOTS - pad):
            feedback = self._ccsds_index_of[data[i] ^ parity[0]]  # Compute feedback term
            if feedback != self._A0:  # If feedback term is non-zero
                # Optional: Uncomment if UNNORMALIZED is defined
                # feedback = mod255(NN - GENPOLY[NROOTS] + feedback)
    
                x = list()
                for j in range(1, self._NROOTS):
                    parity[j] ^= self._ccsds_alpha_to[self._mod255(feedback + self._ccsds_genpoly[self._NROOTS - j])]
    
            # Shift parity array
            parity[:-1] = parity[1:].copy() # Shift left by one
            if feedback != self._A0:
                parity[-1] = self._ccsds_alpha_to[self._mod255(feedback + self._ccsds_genpoly[0])]
            else:
                parity[-1] = np.int8(0)
    
        return list(parity)

    def decode(self, data, pad, eras_pos=None, no_eras=0):
        """
        Decodes a Reed-Solomon codeword (data + parity).

        :param data: Is the codeword as a list of integers.
        :type: list

        :param pad: The number of pad symbols in a block.
        :type: int

        :return: The decoded data.
        :rtype: list

        :return: A list with the position of the detected errors.
        :rtype: list

        :return: The number of detected errors.
        :rtype: int
        """
        deg_lambda  = np.int16()
        el          = np.int16()
        deg_omega   = np.int16()
        i           = np.int16()
        j           = np.int16()
        r           = np.int16()
        k           = np.int16()
        u           = np.uint8()
        q           = np.uint8()
        tmp         = np.uint8()
        num1        = np.uint8()
        num2        = np.uint8()
        den         = np.uint8()
        discr_r     = np.uint8()
        lambda_poly = np.zeros(self._NROOTS + 1, dtype=np.uint8)
        s           = np.zeros(self._NROOTS, dtype=np.uint8)
        b           = np.zeros(self._NROOTS + 1, dtype=np.uint8)
        t           = np.zeros(self._NROOTS + 1, dtype=np.uint8)
        omega       = np.zeros(self._NROOTS + 1, dtype=np.uint8)
        root        = np.zeros(self._NROOTS, dtype=np.uint8)
        reg         = np.zeros(self._NROOTS + 1, dtype=np.uint8)
        loc         = np.zeros(self._NROOTS, dtype=np.uint8)
        syn_error   = np.int16()
        count       = np.int16()

        # Form the syndromes; i.e., evaluate data(x) at roots of g(x)
        for i in range(self._NROOTS):
            s[i] = data[0]
    
        for j in range(1, self._NN - pad):
            for i in range(self._NROOTS):
                if s[i] == 0:
                    s[i] = data[j]
                else:
                    s[i] = data[j] ^ self._ccsds_alpha_to[self._mod255(self._ccsds_index_of[s[i]] + (self._FCR + i) * self._PRIM)]

        # Convert syndromes to index form, checking for nonzero condition
        syn_error = 0
        for i in range(self._NROOTS):
            syn_error |= s[i]
            s[i] = self._ccsds_index_of[s[i]]

        if not syn_error:
            # If syndrome is zero, data[] is a codeword and there are no errors to correct
            return data[:-32], list(), 0

        lambda_poly[0] = np.uint8(1)

        if no_eras > 0 and eras_pos is not None:
            # Init lambda to be the erasure locator polynomial
            lambda_poly[1] = self._ccsds_alpha_to[self._mod255(self._PRIM * (self._NN - 1 - eras_pos[0]))]
            for i in range(1, no_eras):
                u = self._mod255(self._PRIM * (self._NN - 1 - eras_pos[i]))
                for j in range(i + 1, 0, -1):
                    tmp = self._ccsds_index_of[lambda_poly[j - 1]]
                    if tmp != self._A0:
                        lambda_poly[j] ^= self._ccsds_alpha_to[self._mod255(u + tmp)]

        for i in range(self._NROOTS + 1):
            b[i] = self._ccsds_index_of[lambda_poly[i]]

        # Begin Berlekamp-Massey algorithm to determine error+erasure locator polynomial
        r = no_eras
        el = no_eras
        r += 1
        while r <= self._NROOTS:
            # Compute discrepancy at the r-th step in poly-form
            discr_r = np.uint8(0)
            for i in range(r):
                if lambda_poly[i] != 0 and s[r - i - 1] != self._A0:
                    discr_r ^= self._ccsds_alpha_to[self._mod255(self._ccsds_index_of[lambda_poly[i]] + s[r - i - 1])]
            discr_r = self._ccsds_index_of[discr_r] # Index form
            if discr_r == self._A0:
                # B(x) <-- x*B(x)
                b[1:] = b[:-1].copy()
                b[0] = self._A0
            else:
                # T(x) <-- lambda(x) - discr_r*x*b(x)
                t[0] = lambda_poly[0]
                for i in range(self._NROOTS):
                    if b[i] != self._A0:
                        t[i + 1] = lambda_poly[i + 1] ^ self._ccsds_alpha_to[self._mod255(discr_r + b[i])]
                    else:
                        t[i + 1] = lambda_poly[i + 1]
                if 2 * el <= r + no_eras - 1:
                    el = r + no_eras - el
                    # B(x) <-- inv(discr_r) * lambda(x)
                    for i in range(self._NROOTS + 1):
                        b[i] = self._A0 if lambda_poly[i] == 0 else self._mod255(self._ccsds_index_of[lambda_poly[i]] - discr_r + self._NN)
                else:
                    # B(x) <-- x*B(x)
                    b[1:] = b[:-1].copy()
                    b[0] = self._A0
                lambda_poly = t.copy()
            r += 1

        # Convert lambda to index form and compute deg(lambda(x))
        deg_lambda = 0
        for i in range(self._NROOTS + 1):
            lambda_poly[i] = self._ccsds_index_of[lambda_poly[i]]
            if lambda_poly[i] != self._A0:
                deg_lambda = i

        # Find roots of the error+erasure locator polynomial by Chien search
        reg[1:] = lambda_poly[1:].copy()
        count = 0  # Number of roots of lambda(x)
        i = 1
        k = self._IPRIM - 1
        while i <= self._NN:
            q = 1  # lambda[0] is always 0
            for j in range(deg_lambda, 0, -1):
                if reg[j] != self._A0:
                    reg[j] = self._mod255(reg[j] + j)
                    q ^= self._ccsds_alpha_to[reg[j]]

            if q != 0:
                # Not a root, continue to the next iteration
                i += 1
                k = self._mod255(k + self._IPRIM)
                continue

            # Store root (index-form) and error location number
            root[count] = i
            loc[count] = k

            # If we've already found max possible roots, abort the search to save time
            count += 1
            if count == deg_lambda:
                break

            # Update i and k for the next iteration
            i += 1
            k = self._mod255(k + self._IPRIM)

        if deg_lambda != count:
            # deg(lambda) unequal to number of roots => uncorrectable error detected
            raise RuntimeError("Uncorrectable errors detected in Reed-Solomon codeword!")

        # Compute err+eras evaluator poly omega(x) = s(x)*lambda(x) (modulo x**NROOTS)
        deg_omega = deg_lambda - 1
        for i in range(deg_omega + 1):
            tmp = np.uint8(0)
            for j in range(i, -1, -1):
                if s[i - j] != self._A0 and lambda_poly[j] != self._A0:
                    tmp ^= self._ccsds_alpha_to[self._mod255(np.uint16(s[i - j]) + np.uint16(lambda_poly[j]))]
            omega[i] = self._ccsds_index_of[tmp]

        # Compute error values in poly-form
        for j in range(count - 1, -1, -1):
            num1 = 0
            for i in range(deg_omega, -1, -1):
                if omega[i] != self._A0:
                    num1 ^= self._ccsds_alpha_to[self._mod255(omega[i] + i * root[j])]
            num2 = self._ccsds_alpha_to[self._mod255(root[j] * (self._FCR - 1) + self._NN)]
            den = 0

            # lambda[i+1] for i even is the formal derivative lambda_pr of lambda[i]
            for i in range(min(deg_lambda, self._NROOTS - 1) & ~1, -1, -2):
                if lambda_poly[i + 1] != self._A0:
                    den ^= self._ccsds_alpha_to[self._mod255(lambda_poly[i + 1] + i * root[j])]

            # Apply error to data
            if num1 != 0 and loc[j] >= pad:
                data[loc[j] - pad] ^= self._ccsds_alpha_to[self._mod255(self._ccsds_index_of[num1] + self._ccsds_index_of[num2] + self._NN - self._ccsds_index_of[den])]

        eras_pos = list()
        for i in range(count):
            eras_pos.append(loc[i] - pad)

        return data[:-32], eras_pos, count

    def _mod255(self, x):
        """
        Computes the module of a given number.

        :param x: Is the integer to compute the modulo.
        :type: int

        :return: The modulo result.
        :rtype: int
        """
        return x % 255
