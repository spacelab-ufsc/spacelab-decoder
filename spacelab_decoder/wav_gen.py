#
#  wav_gen.py
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


import wave, struct, math

class WavGen:

    def __init__(self, pkt, sample_rate_hz, baudrate, amp, out_file):
        self.amplitude = int(amp*32767)
        bit_samples = int(sample_rate_hz/baudrate)

        wav_file = wave.open(out_file, 'w')
        wav_file.setnchannels(1) # mono
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate_hz)

        self._write_zeros(wav_file, int(sample_rate_hz/20))

        for byte in pkt:
            self._write_byte(wav_file, bit_samples, byte)

        self._write_zeros(wav_file, int(sample_rate_hz/20))

        wav_file.close()

    def _write_bit(self, wav_file, bit_samples, bit):
        for i in range(bit_samples):
            value = int()
            if bit == '1':
                value = self.amplitude
            else:
                value = -self.amplitude
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

    def _write_zeros(self, wav_file, samples):
        for i in range(samples):
            value = 0
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

    def _int2bin(self, byte):
        return bin(byte)[2:].zfill(8)

    def _write_byte(self, wav_file, bit_samples, byte):
        i = 0
        for i in range(8):
            self._write_bit(wav_file, bit_samples, self._int2bin(byte)[i])
