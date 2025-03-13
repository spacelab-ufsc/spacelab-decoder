# -*- coding: utf-8 -*-

#
#  time_sync.py
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

_TIME_SYNC_DEFAULT_SAMPLE_RATE_HZ = 48000
_TIME_SYNC_DEFAULT_BAUDRATE_BPS = 1200
_TIME_SYNC_INITIAL_MU = 0.5
_TIME_SYNC_GAIN = 0.001

class TimeSync:
    """
    Time Synchronization.
    """

    def __init__(self, samp_rate=_TIME_SYNC_DEFAULT_SAMPLE_RATE_HZ, baud=_TIME_SYNC_DEFAULT_BAUDRATE_BPS):
        """
        Class constructor with the internal variables initialization.
        """
        self._sps       = samp_rate/baud
        self._mu        = _TIME_SYNC_INITIAL_MU             # Initial estimate of phase of sample
        self._out_rail  = np.zeros(2, dtype=np.complex128)  # Stores the last two output rail values
        self._out       = np.zeros(2, dtype=np.complex128)  # Stores the last two output values
        self._gain      = _TIME_SYNC_GAIN

    def decode_stream(self, data):
        """
        Decodes a stream of samples.

        :param data: Is a list with the signal samples to extract the bits.
        :type: list

        :return: A list with the extracted bits.
        :rtype: list
        """
        samples     = np.array(data, dtype=np.float128)
        out         = np.zeros(len(samples) + int(2*self._sps), dtype=np.complex128)
        out_rail    = np.zeros(len(samples) + int(2*self._sps), dtype=np.complex128)

        # Initialize with the previous state
        out[:2]         = self._out
        out_rail[:2]    = self._out_rail

        i_in    = 0 # Input samples index
        i_out   = 2 # Output index (let first two outputs be from previous state)

        while i_out < len(samples) and i_in + 1 < len(samples):
            out[i_out] = samples[i_in + int(self._mu)]  # Grab what we think is the "best" sample
            out_rail[i_out] = int(np.real(out[i_out]) > 0) + 1j * int(np.imag(out[i_out]) > 0)

            x = (out_rail[i_out] - out_rail[i_out - 2]) * np.conj(out[i_out - 1])
            y = (out[i_out] - out[i_out - 2]) * np.conj(out_rail[i_out - 1])

            mm_val = np.real(y - x)
            self._mu += self._sps + self._gain * mm_val

            i_in += int(np.floor(self._mu))             # Round down to nearest int since we are using it as an index
            self._mu = self._mu - np.floor(self._mu)    # Remove the integer part of mu
            i_out += 1                                  # Increment output index

        # Update the state for the next iteration
        self._out       = out[i_out - 2:i_out]      # Store the last two output values
        self._out_rail  = out_rail[i_out - 2:i_out] # Store the last two output rail values

        # Extract bits from the current chunk
        out = out[2:i_out]  # Remove the first two, and anything after i_out (that was never filled out)

        return [1 if symbol.real > 0 else 0 for symbol in out]  # Binary slicer

    def get_bitstream(self, data):
        """
        Decodes a bitstream from a sequence of samples.

        :param data: Is a list with the signal samples to extract the bits.
        :type: list

        :return: A list with the extracted bits.
        :rtype: list
        """
        samples = np.array(data, dtype=np.float128)

        mu = self._mu   # Initial estimate of phase of sample
        gain = self._gain
        out = np.zeros(len(samples) + 10, dtype=np.complex128)

        out_rail = np.zeros(len(samples) + 10, dtype=np.complex128) # Stores values, each iteration we need the previous 2 values plus current value

        i_in = 0    # Input samples index
        i_out = 2   # Output index (let first two outputs be 0)

        while i_out < len(samples) and i_in + 1 < len(samples):
            out[i_out] = samples[i_in + int(mu)]  # grab what we think is the "best" sample
            out_rail[i_out] = int(np.real(out[i_out]) > 0) + 1j * int(np.imag(out[i_out]) > 0)

            x = (out_rail[i_out] - out_rail[i_out - 2]) * np.conj(out[i_out - 1])
            y = (out[i_out] - out[i_out - 2]) * np.conj(out_rail[i_out - 1])

            mm_val = np.real(y - x)
            mu += self._sps + gain * mm_val

            i_in += int(np.floor(mu))   # Round down to nearest int since we are using it as an index
            mu = mu - np.floor(mu)      # Remove the integer part of mu
            i_out += 1                  # Increment output index

        out = out[2:i_out]  # Remove the first two, and anything after i_out (that was never filled out)

        return [1 if symbol.real > 0 else 0 for symbol in out]  # Binary slicer

    def reset(self):
        """
        Resets the decoder.

        :return: None
        """
        self._mu        = _TIME_SYNC_INITIAL_MU
        self._out       = np.zeros(2, dtype=np.complex128)
        self._out_rail  = np.zeros(2, dtype=np.complex128)
