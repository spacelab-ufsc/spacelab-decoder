#
#  test_golay24.py
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

from golay24 import Golay24

@pytest.fixture
def golay():
    return Golay24()

def test_encode(golay):
    # Test encoding with a known 12-bit input
    data = 0b101010101010  # Example 12-bit data
    encoded_bytes = golay.encode(data)
    # Check that the output is 3 bytes (24 bits)
    assert len(encoded_bytes) == 3
    assert all(0 <= byte <= 255 for byte in encoded_bytes)

def test_decode_no_errors(golay):
    # Test decoding with no errors
    data = 0b110011001100  # Example 12-bit data
    encoded_bytes = golay.encode(data)
    decoded_data = golay.decode(encoded_bytes)
    assert decoded_data == data

def test_decode_single_error(golay):
    # Test decoding with a single-bit error
    data = 0b101010101010  # Example 12-bit data
    encoded_bytes = golay.encode(data)
    # Introduce a single-bit error in the first byte
    encoded_bytes[0] ^= 0b00000001  # Flip the least significant bit
    decoded_data = golay.decode(encoded_bytes)
    assert decoded_data == data

def test_decode_double_error(golay):
    # Test decoding with two-bit errors
    data = 0b111100001111  # Example 12-bit data
    encoded_bytes = golay.encode(data)
    # Introduce two-bit errors in the encoded bytes
    encoded_bytes[1] ^= 0b00000011  # Flip two bits in the second byte
    decoded_data = golay.decode(encoded_bytes)
    assert decoded_data == data

def test_decode_triple_error(golay):
    # Test decoding with three-bit errors
    data = 0b000011110000  # Example 12-bit data
    encoded_bytes = golay.encode(data)
    # Introduce three-bit errors in the encoded bytes
    encoded_bytes[0] ^= 0b00000001  # Flip one bit in the first byte
    encoded_bytes[1] ^= 0b00000010  # Flip one bit in the second byte
    encoded_bytes[2] ^= 0b00000100  # Flip one bit in the third byte
    decoded_data = golay.decode(encoded_bytes)
    assert decoded_data == data

def test_decode_uncorrectable_error(golay):
    # Test decoding with more than three errors (uncorrectable)
    data = 0b101010101010  # Example 12-bit data
    encoded_bytes = golay.encode(data)
    # Introduce four-bit errors in the encoded bytes
    encoded_bytes[0] ^= 0b00001111  # Flip four bits in the first byte
    decoded_data = golay.decode(encoded_bytes)
    # The decoder should return the original data (may contain errors)
    assert decoded_data != data  # The result may not match due to uncorrectable errors

def test_encode_invalid_input(golay):
    # Test encoding with invalid input (not a 12-bit integer)
    with pytest.raises(ValueError):
        golay.encode(5000)  # Input is larger than 12 bits

def test_decode_invalid_input(golay):
    # Test decoding with invalid input (not 3 bytes)
    with pytest.raises(ValueError):
        golay.decode([255, 255])  # Only 2 bytes provided
    with pytest.raises(ValueError):
        golay.decode([256, 255, 255])  # Invalid byte value
