#
#  test_bit_decoder.py
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

import pytest

from bit_decoder import BitDecoder, _BIT_DECODER_MAX_BYTES_TO_DECODE

def test_bit_decoder_initialization():
    """
    Test the initialization of the BitDecoder class.
    """
    sync_word = [0xAA, 0x55]  # Example sync word
    decoder = BitDecoder(sync_word, 0)

    assert decoder._sync_word_buf is not None
    assert decoder._sync_word is not None
    assert decoder._byte_buf is not None
    assert decoder._pkt_detected is False
    assert decoder._decoded_bytes == 0

def test_decode_bit_with_sync_word():
    """
    Test decoding bits with a sync word.
    """
    sync_word = [0xAA, 0x55]  # Example sync word
    decoder = BitDecoder(sync_word, 0)

    # Push the sync word bits
    sync_bits = [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1]  # 0xAA, 0x55 in binary (LSB)
    for bit in sync_bits:
        assert decoder.decode_bit(bit) is None

    # After sync word, the next bits should be decoded as bytes
    data_bits = [1, 0, 1, 0, 1, 0, 1, 0]  # 0xAA in binary (LSB)
    for bit in data_bits:
        byte = decoder.decode_bit(bit)
        if byte is not None:
            assert byte == 0xAA

def test_decode_bit_without_sync_word():
    """
    Test decoding bits without a sync word.
    """
    sync_word = [0xAA, 0x55]  # Example sync word
    decoder = BitDecoder(sync_word, 0)

    # Push random bits that do not match the sync word
    random_bits = [1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0]
    for bit in random_bits:
        assert decoder.decode_bit(bit) is None

def test_decode_bit_max_bytes():
    """
    Test decoding bits up to the maximum number of bytes.
    """
    sync_word = [0xAA, 0x55]  # Example sync word
    decoder = BitDecoder(sync_word, 0)

    # Push the sync word bits
    sync_bits = [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1]  # 0xAA, 0x55 in binary (LSB)
    for bit in sync_bits:
        decoder.decode_bit(bit)

    # Push data bits until the maximum number of bytes is reached
    data_bits = [1, 0, 1, 0, 1, 0, 1, 0]  # 0xAA in binary (LSB)
    for _ in range(_BIT_DECODER_MAX_BYTES_TO_DECODE):
        for bit in data_bits:
            byte = decoder.decode_bit(bit)
            if byte is not None:
                assert byte == 0xAA

    # After reaching the maximum number of bytes, the decoder should reset
    for bit in data_bits:
        assert decoder.decode_bit(bit) is None

def test_reset():
    """
    Test the reset functionality of the decoder.
    """
    sync_word = [0xAA, 0x55]  # Example sync word
    decoder = BitDecoder(sync_word, 0)

    # Push the sync word bits
    sync_bits = [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1]  # 0xAA, 0x55 in binary (LSB)
    for bit in sync_bits:
        decoder.decode_bit(bit)

    # Push some data bits
    data_bits = [1, 0, 1, 0, 1, 0, 1, 0]  # 0xAA in binary (LSB)
    for bit in data_bits:
        byte = decoder.decode_bit(bit)
        if byte is not None:
            assert byte == 0xAA

    # Reset the decoder
    decoder.reset()

    # After reset, the decoder should not detect a packet
    for bit in data_bits:
        assert decoder.decode_bit(bit) is None
