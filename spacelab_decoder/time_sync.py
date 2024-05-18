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

_DEFAULT_SAMPLE_RATE_HZ     = 48000
_DEFAULT_BAUDRATE_BPS       = 1200

class TimeSync:

    def __init__(self):
        pass

    def get_bitstream(self, data, samp_rate=_DEFAULT_SAMPLE_RATE_HZ, baudrate=_DEFAULT_BAUDRATE_BPS):
        sps = samp_rate/baudrate

        samples = np.array(data, dtype=np.float64)

        mu = 0.001  # Initial estimate of phase of sample
        out = np.zeros(len(samples) + 10, dtype=np.complex64)

        out_rail = np.zeros(len(samples) + 10, dtype=np.complex64) # Stores values, each iteration we need the previous 2 values plus current value

        i_in = 0    # Input samples index
        i_out = 2   # Output index (let first two outputs be 0)

        while i_out < len(samples) and i_in+1 < len(samples):
            out[i_out] = samples[i_in + int(mu)] # grab what we think is the "best" sample
            out_rail[i_out] = int(np.real(out[i_out]) > 0) + 1j*int(np.imag(out[i_out]) > 0)

            x = (out_rail[i_out] - out_rail[i_out-2]) * np.conj(out[i_out-1])
            y = (out[i_out] - out[i_out-2]) * np.conj(out_rail[i_out-1])

            mm_val = np.real(y - x)
            mu += sps + 0.001*mm_val

            i_in += int(np.floor(mu))   # Round down to nearest int since we are using it as an index
            mu = mu - np.floor(mu)      # Remove the integer part of mu
            i_out += 1                  # Increment output index

        out = out[2:i_out]              # Remove the first two, and anything after i_out (that was never filled out)

        bits = list()
        for i in range(len(out)):
            if out[i].real > 0:
                bits.append(1)
            else:
                bits.append(0)

        return bits
