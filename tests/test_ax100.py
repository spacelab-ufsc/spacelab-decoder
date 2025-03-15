#
#  test_ax100.py
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

import random

import pytest

from ax100 import AX100Mode5

@pytest.fixture
def ax100_mode5():
    return AX100Mode5()

def test_encode_decode(ax100_mode5):
    # Test data
    data = list()
    for i in range(random.randint(1, 223)):
        data.append(random.randint(0, 255))

    # Encode the data
    encoded_packet = ax100_mode5.encode(data)

    preamb_sw_len = len(ax100_mode5.get_preamble()) + len(ax100_mode5.get_sync_word())

    # Decode the encoded packet
    decoded_data = ax100_mode5.decode(encoded_packet[preamb_sw_len:])   # Skip preamble and sync word

    # Assert that the decoded data matches the original data
    assert decoded_data == data

def test_decode_byte(ax100_mode5):
    # Test data
    data = list()
    for i in range(random.randint(1, 223)):
        data.append(random.randint(0, 255))

    # Encode the data
    encoded_packet = ax100_mode5.encode(data)

    # Decode the packet byte by byte
    decoded_data = []
    for byte in encoded_packet[8:]:  # Skip preamble and sync word
        result = ax100_mode5.decode_byte(byte)
        if result is not None:
            decoded_data = result

    # Assert that the decoded data matches the original data
    assert decoded_data == data

def test_padding(ax100_mode5):
    # Test data
    data = [0x01, 0x02, 0x03]

    target_len = 10

    # Apply padding
    padded_data = ax100_mode5._padding(data, target_len)

    # Assert that the length of padded data matches the target length
    assert len(padded_data) == target_len

    # Assert that the padded data contains the original data
    assert padded_data[:len(data)] == data

    # Assert that the padding is done with zeros
    assert all(byte == 0 for byte in padded_data[len(data):])

def test_scrambling(ax100_mode5):
    # Test data
    data = list()
    for i in range(random.randint(1, 255)):
        data.append(random.randint(0, 255))

    # Apply scrambling
    scrambled_data = ax100_mode5._scrambling(data)

    # Apply scrambling again to descramble
    descrambled_data = ax100_mode5._scrambling(scrambled_data)

    # Assert that the descrambled data matches the original data
    assert descrambled_data == data

def test_sync_word(ax100_mode5):
    # Test sync word
    new_sync_word = [0x12, 0x34, 0x56, 0x78]
    ax100_mode5.set_sync_word(new_sync_word)

    # Assert that the sync word is set correctly
    assert ax100_mode5.get_sync_word() == new_sync_word

def test_preamble(ax100_mode5):
    # Test preamble
    new_preamble = [0xAA, 0xBB, 0xCC, 0xDD]
    ax100_mode5.set_preamble(new_preamble)

    # Assert that the preamble is set correctly
    assert ax100_mode5.get_preamble() == new_preamble

if __name__ == "__main__":
    pytest.main()
