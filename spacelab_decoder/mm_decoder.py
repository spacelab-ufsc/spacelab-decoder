# -*- coding: utf-8 -*-

#
#  mm_decoder.py
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


from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq

_DEFAULT_INPUT_FILE         = "/tmp/audio.wav"
_DEFAULT_SAMPLE_RATE_HZ     = 48000
_DEFAULT_BAUDRATE_BPS       = 1200
_DEFAULT_ZMQ_ADDRESS        = "tcp://127.0.0.1:2112"

class mm_decoder(gr.top_block):

    def __init__(self, input_file=_DEFAULT_INPUT_FILE, samp_rate=_DEFAULT_SAMPLE_RATE_HZ, baudrate=_DEFAULT_BAUDRATE_BPS, zmq_adr=_DEFAULT_ZMQ_ADDRESS, play_audio=False):
        gr.top_block.__init__(self, "M&M Audio Decoder")

        # Parameters
        self.baudrate = baudrate
        self.input_file = input_file
        self.samp_rate = samp_rate

        # Blocks
        self.zeromq_push_sink_0 = zeromq.push_sink(gr.sizeof_char, 1, zmq_adr, 100, False, -1)
        self.digital_clock_recovery_mm_xx_0 = digital.clock_recovery_mm_ff(samp_rate/baudrate, 0.001, 0, 0.25, 0.001)
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_wavfile_source_0 = blocks.wavfile_source(input_file, False)
        self.audio_sink_0 = audio.sink(samp_rate, '', play_audio)

        # Connections
        if play_audio:
            self.connect((self.blocks_wavfile_source_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.digital_clock_recovery_mm_xx_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.zeromq_push_sink_0, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))


    def get_baudrate(self):
        return self.baudrate

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate
        self.digital_clock_recovery_mm_xx_0.set_omega(self.samp_rate/self.baudrate)

    def get_input_file(self):
        return self.input_file

    def set_input_file(self, input_file):
        self.input_file = input_file

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.digital_clock_recovery_mm_xx_0.set_omega(self.samp_rate/self.baudrate)
